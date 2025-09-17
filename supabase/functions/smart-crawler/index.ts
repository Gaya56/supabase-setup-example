// smart-crawler/index.ts
//
// This edge function orchestrates crawling by calling the external Python
// service. Crawl4AI logic runs in Python (FastAPI), since it cannot run
// inside Deno Edge Functions. This function only validates input, calls
// the Python service, stores results in Supabase, and updates metrics.

import 'jsr:@supabase/functions-js/edge-runtime.d.ts';
import { createClient } from 'jsr:@supabase/supabase-js@2';
import OpenAI from 'jsr:@openai/openai';

// --- Schema conversion helper (kept for compatibility) ---
export function convertToCrawl4aiFormat(patterns: any) {
function processField(name: string, def: any): any {
if (def && typeof def === 'object' && !('selector' in def) && !('attribute' in def)) {
const nestedFields: any[] = [];
for (const subKey of Object.keys(def)) {
nestedFields.push(processField(subKey, def[subKey]));
}
return { name, type: 'nested', fields: nestedFields };
}
const selector: string = def?.selector ?? '';
let attr: string | undefined = def?.attribute;
let type: string;
if (attr && attr.includes('|')) attr = attr.split('|')[0];
if (attr === 'textContent' || attr === 'text') type = 'text';
else if (selector && /a\[|img\[|li|ul/.test(selector)) type = 'list';
else type = 'attribute';
const field: any = { name, selector, type };
if (attr && type !== 'text') field.attribute = attr;
if (def?.required) field.required = true;
return field;
}
const fields: any[] = [];
if (patterns && typeof patterns === 'object') {
for (const key of Object.keys(patterns)) fields.push(processField(key, patterns[key]));
}
return { name: 'extraction_schema', baseSelector: 'body', fields, transform: 'flatten' };
}

// --- Confidence score helper ---
export function calculateConfidenceScore(extractedContent: any) {
if (!extractedContent || typeof extractedContent !== 'object') return 0;
const items = Array.isArray(extractedContent) ? extractedContent : [extractedContent];
let totalFields = 0, populated = 0;
for (const item of items) {
for (const key of Object.keys(item)) {
totalFields++;
const value = item[key];
if (value !== null && value !== undefined && value !== '') populated++;
}
}
return totalFields === 0 ? 0 : populated / totalFields;
}

// --- Metrics update helper ---
export async function updateSchemaMetrics(
schemaId: string,
success: boolean,
processingTime: number,
supabase: any
) {
try {
const { data: existing } = await supabase
.from('extraction_schemas')
.select('usage_count')
.eq('id', schemaId)
.maybeSingle();
let newCount = 1;
if (existing && typeof existing.usage_count === 'number')
newCount = existing.usage_count + (success ? 1 : 0);
const updates: any = { last_used_at: new Date().toISOString() };
if (success) updates.usage_count = newCount;
console.log(`Schema ${schemaId} processed in ${processingTime}ms`);
await supabase.from('extraction_schemas').update(updates).eq('id', schemaId);
} catch (err) {
console.error('Failed to update schema metrics', err);
}
}

// --- Orchestrator: call Python crawler service ---
export async function performSchemaBasedCrawl(
url: string,
schemaId: string,
supabase: any
): Promise<{
success: boolean;
extractedContent?: any;
extractionMethod: 'schema' | 'llm' | 'hybrid';
processingTimeMs: number;
confidenceScore?: number;
costSavings?: string;
error?: string;
}> {
const start = Date.now();
try {
const { data: schemaRow, error: fetchError } = await supabase
.from('extraction_schemas')
.select('id')
.eq('id', schemaId)
.maybeSingle();
if (fetchError || !schemaRow) {
const processing = Date.now() - start;
await updateSchemaMetrics(schemaId, false, processing, supabase);
return { success: false, extractionMethod: 'llm', processingTimeMs: processing, error: 'Extraction schema not found' };
}

const serviceUrl = Deno.env.get('PYTHON_CRAWLER_SERVICE_URL');
const apiKey = Deno.env.get('PYTHON_CRAWLER_API_KEY');
if (!serviceUrl || !apiKey) {
  const processing = Date.now() - start;
  await updateSchemaMetrics(schemaId, false, processing, supabase);
  return { success: false, extractionMethod: 'llm', processingTimeMs: processing, error: 'Python crawler service env vars missing' };
}

const serviceResponse = await fetch(`${serviceUrl}/crawl`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiKey}` },
  body: JSON.stringify({ url, schema_id: schemaId })
});

if (!serviceResponse.ok) {
  const processing = Date.now() - start;
  await updateSchemaMetrics(schemaId, false, processing, supabase);
  return { success: false, extractionMethod: 'llm', processingTimeMs: processing, error: `Python service error: ${serviceResponse.status}` };
}

const pythonResult = await serviceResponse.json();
if (pythonResult && pythonResult.success && pythonResult.extracted_content) {
  const confidenceScore = calculateConfidenceScore(pythonResult.extracted_content);
  const processing = Date.now() - start;
  try {
    await supabase.from('crawl_results').insert({
      url,
      title: pythonResult.extracted_content.title ?? null,
      content: pythonResult.extracted_content.content ?? null,
      extraction_data: pythonResult.extracted_content,
      extraction_schema_id: schemaId,
      extraction_quality: 1,
      schema_match_score: confidenceScore,
      content_embedding: null
    });
  } catch (insertErr) {
    console.error('Failed to insert crawl result', insertErr);
  }
  await updateSchemaMetrics(schemaId, true, processing, supabase);
  return { success: true, extractedContent: pythonResult.extracted_content, extractionMethod: 'schema', processingTimeMs: processing, confidenceScore, costSavings: '90% (no LLM calls)' };
}

const processing = Date.now() - start;
await updateSchemaMetrics(schemaId, false, processing, supabase);
return { success: false, extractionMethod: 'llm', processingTimeMs: processing, error: pythonResult?.error || 'Schema extraction failed' };

} catch (err: any) {
console.error('Schema based crawl orchestrator error', err);
const processing = Date.now() - start;
await updateSchemaMetrics(schemaId, false, processing, supabase);
return { success: false, extractionMethod: 'llm', processingTimeMs: processing, error: err?.message || 'Unknown error' };
}
}

// --- Supabase Edge Function entrypoint ---
Deno.serve(async (req) => {
const corsHeaders = {
'Access-Control-Allow-Origin': '*',
'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
};
if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders });
try {
const { url, schema_id } = await req.json();
if (!url || !schema_id) {
return new Response(JSON.stringify({ success: false, extraction_method: 'schema', error: 'Missing url or schema_id' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } });
}
const supabaseUrl = Deno.env.get('SUPABASE_URL');
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
if (!supabaseUrl || !supabaseKey) {
return new Response(JSON.stringify({ success: false, extraction_method: 'schema', error: 'Supabase env vars not configured' }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } });
}
const supabase = createClient(supabaseUrl, supabaseKey);
const result = await performSchemaBasedCrawl(url, schema_id, supabase);
return new Response(JSON.stringify({
success: result.success,
extracted_content: result.extractedContent,
extraction_method: result.extractionMethod,
processing_time_ms: result.processingTimeMs,
confidence_score: result.confidenceScore,
cost_savings: result.costSavings,
error: result.error
}), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } });
} catch (err) {
console.error('Unexpected error in handler', err);
return new Response(JSON.stringify({ success: false, extraction_method: 'schema', error: 'Invalid request body' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } });
}});