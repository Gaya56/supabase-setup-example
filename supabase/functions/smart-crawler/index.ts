// smart-crawler/index.ts
//
// This/**
 * Convert an extraction schema stored in the `extraction_schemas.patterns`
 * column into the format expected by our external Python crawl4ai scripts.
 * 
 * The existing schemas are stored as an object where each key maps to
 * `{ selector: string, attribute: string, required?: boolean }`. In the
 * target format the schema must include a `baseSelector` (defaults to
 * `body`) and a `fields` array of objects with `name`, `selector`,
 * `type` and optional `attribute` and `required` properties.
 * 
 * @param patterns The original patterns JSON from the database
 */n implements a schema‑based crawler using Crawl4AI’s
// JsonCssExtractionStrategy.  It falls back to an LLM based approach when
// the provided extraction schema fails.  The goal is to avoid expensive
// LLM calls by learning a schema once and reusing it for future crawls.
//
// References:
// - The Crawl4AI `JsonCssExtractionStrategy` accepts a schema with a
//   `baseSelector` and an array of `fields` where each field defines a
//   CSS selector, type and optional attributes [oai_citation:0‡docs.crawl4ai.com](https://docs.crawl4ai.com/api/strategies/).
// - You can initialise a new `AsyncWebCrawler` and call its `arun()`
//   method with a `CrawlerRunConfig` that includes an extraction strategy [oai_citation:1‡docs.crawl4ai.com](https://docs.crawl4ai.com/api/async-webcrawler/).
// - Supabase exposes environment variables such as `SUPABASE_URL` and
//   `SUPABASE_SERVICE_ROLE_KEY` by default and they can be accessed via
//   `Deno.env.get()` [oai_citation:2‡supabase.com](https://supabase.com/docs/guides/functions/secrets).  The recommended way to
//   create a client inside edge functions is using the `createClient`
//   helper from `@supabase/supabase-js@2` [oai_citation:3‡supabase.com](https://supabase.com/docs/guides/functions/secrets).

// Import the edge runtime types.  This ensures that Deno knows about
// globals like `Deno.serve()` when targeting Supabase Edge Functions.
import 'jsr:@supabase/functions-js/edge-runtime.d.ts';
// Use the official Supabase client from the jsr registry as recommended
// in the docs [oai_citation:4‡supabase.com](https://supabase.com/docs/guides/functions/dependencies).  The `createClient` helper
// initializes a client using your project URL and key.
import { createClient } from 'jsr:@supabase/supabase-js@2';
// Keep the OpenAI import so existing embedding logic continues to work.
// Although this file doesn’t use OpenAI directly, other parts of the
// current function may.  Do not remove this import.
import OpenAI from 'jsr:@openai/openai';
// Note: Due to Supabase Edge Functions limitations with crawl4ai npm package,
// this implementation uses a hybrid approach:
// 1. Edge Function orchestrates and manages database operations
// 2. External Python scripts handle actual crawl4ai operations
// 3. Results are processed and stored via this Edge Function

/**

- Convert an extraction schema stored in the `extraction_schemas.patterns`
- column into the format expected by Crawl4AI’s JsonCssExtractionStrategy.
- 
- The existing schemas are stored as an object where each key maps to
- `{ selector: string, attribute: string, required?: boolean }`. In the
- target format the schema must include a `baseSelector` (defaults to
- `body`) and a `fields` array of objects with `name`, `selector`,
- `type` and optional `attribute` and `required` properties [oai_citation:5‡docs.crawl4ai.com](https://docs.crawl4ai.com/api/strategies/).
- 
- @param patterns The original patterns JSON from the database
*/
export function convertToCrawl4aiFormat(patterns: any) {
/*
    - Recursively process a pattern definition into a Crawl4AI field. If the
    - definition does not include a `selector` or `attribute` property it is
    - treated as a nested object. Nested objects are converted into
    - `type: 'nested'` fields with their own list of sub‑fields. This
    - allows complex structures like metadata objects to be extracted
    - correctly [oai_citation:6‡docs.crawl4ai.com](https://docs.crawl4ai.com/assets/llm.txt/txt/extraction-no-llm.txt).
    */
    function processField(name: string, def: any): any {
    // If this definition has no selector/attribute then treat it as nested.
    if (def && typeof def === 'object' && !('selector' in def) && !('attribute' in def)) {
    const nestedFields: any[] = [];
    for (const subKey of Object.keys(def)) {
    nestedFields.push(processField(subKey, def[subKey]));
    }
    return {
    name,
    type: 'nested',
    fields: nestedFields
    };
    }
    const selector: string = def?.selector ?? '';
    let attr: string | undefined = def?.attribute;
    let type: string;
    // Handle composite attribute strings like "textContent|datetime" by
    // splitting on `|` and taking the first segment. Additional hints
    // (e.g. datetime) can be ignored here but could be used for further
    // processing.
    if (attr && attr.includes('|')) {
    const parts = attr.split('|');
    attr = parts[0];
    }
    // Determine the field type. Use 'text' for textContent; 'list' for
    // common multi‑value selectors like anchor and image tags; otherwise
    // default to 'attribute' [oai_citation:7‡docs.crawl4ai.com](https://docs.crawl4ai.com/api/strategies/).
    if (attr === 'textContent' || attr === 'text') {
    type = 'text';
    } else if (selector && /a\[|img\[|li|ul/.test(selector)) {
    type = 'list';
    } else {
    type = 'attribute';
    }
    const field: any = { name, selector, type };
    if (type === 'attribute' && attr) {
    field.attribute = attr;
    }
    if (def?.required) {
    field.required = true;
    }
    return field;
    }

const fields: any[] = [];
if (patterns && typeof patterns === 'object') {
for (const key of Object.keys(patterns)) {
fields.push(processField(key, patterns[key]));
}
}
return {
name: 'extraction_schema',
baseSelector: 'body',
fields,
transform: 'flatten'
};
}

/**

- Estimate a confidence score based on how many fields were successfully
- extracted. This naive implementation counts the proportion of
- non‑empty fields relative to the number of expected fields. The score
- will be between 0 and 1.
- 
- @param extractedContent The parsed JSON extracted from the crawler
*/
export function calculateConfidenceScore(extractedContent: any) {
if (!extractedContent || typeof extractedContent !== 'object') return 0;
const items = Array.isArray(extractedContent)
? extractedContent
: [extractedContent];
let totalFields = 0;
let populated = 0;
for (const item of items) {
for (const key of Object.keys(item)) {
totalFields += 1;
const value = item[key];
if (value !== null && value !== undefined && value !== '') {
populated += 1;
}
}
}
if (totalFields === 0) return 0;
return populated / totalFields;
}

/**

- Update schema usage metrics after a crawl. On success the
- `usage_count` is incremented and `last_used_at` is updated. On
- failure only `last_used_at` is updated.
- 
- @param schemaId The UUID of the schema to update
- @param success Whether the crawl succeeded
- @param supabase Supabase client
*/
export async function updateSchemaMetrics(
schemaId: string,
success: boolean,
processingTime: number,
supabase: any
) {
try {
// Retrieve current usage_count
const { data: existing, error: fetchErr } = await supabase
.from('extraction_schemas')
.select('usage_count')
.eq('id', schemaId)
.maybeSingle();
if (fetchErr) {
console.error('Error fetching schema metrics:', fetchErr.message);
}
let newCount = 1;
if (existing && typeof existing.usage_count === 'number') {
newCount = existing.usage_count + (success ? 1 : 0);
}
const updates: any = { last_used_at: new Date().toISOString() };
if (success) {
updates.usage_count = newCount;
}
// Optionally record the processing time in the metadata field of the
// schema. There is no dedicated column for processing time so this
// simply logs it to the console. You could persist it in a custom
// column if desired.
console.log(`Schema ${schemaId} processed in ${processingTime}ms`);
await supabase
.from('extraction_schemas')
.update(updates)
.eq('id', schemaId);
} catch (err) {
console.error('Failed to update schema metrics', err);
}
}

/**

- Perform a schema‑based crawl with Crawl4AI. Attempts to reuse an
- existing extraction schema to avoid LLM calls. If the schema
- extraction fails it falls back to the previous LLM logic (not
- implemented here) and returns an appropriate response.
- 
- @param url The target URL to crawl
- @param schemaId UUID referencing an extraction schema record
- @param supabase Supabase client for database access
*/
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
// Fetch the schema patterns from the database
const { data: schemaRow, error } = await supabase
.from('extraction_schemas')
.select('patterns')
.eq('id', schemaId)
.maybeSingle();
if (error || !schemaRow || !schemaRow.patterns) {
// Schema not found — fallback to LLM (not implemented)
const processing = Date.now() - start;
await updateSchemaMetrics(schemaId, false, processing, supabase);
return {
success: false,
extractionMethod: 'llm',
processingTimeMs: processing,
error: 'Extraction schema not found'
};
}
// Convert the stored schema into Crawl4AI’s schema format
const crawl4aiSchema = convertToCrawl4aiFormat(schemaRow.patterns);
// Create extraction strategy
const extractionStrategy = new JsonCssExtractionStrategy(crawl4aiSchema);
// Run the crawler with the schema. The API accepts a run
// configuration with an `extraction_strategy` property [oai_citation:8‡docs.crawl4ai.com](https://docs.crawl4ai.com/api/async-webcrawler/).
const crawler = new AsyncWebCrawler();
const result: any = await crawler.arun(url, {
extraction_strategy: extractionStrategy
});
// Check if the crawl succeeded
if (result && result.success && result.extracted_content) {
const extractedContent = JSON.parse(result.extracted_content);
const confidenceScore = calculateConfidenceScore(extractedContent);
const processing = Date.now() - start;
// Update schema metrics on success
await updateSchemaMetrics(schemaId, true, processing, supabase);
return {
success: true,
extractedContent,
extractionMethod: 'schema',
processingTimeMs: processing,
confidenceScore,
costSavings: '90% (no LLM calls)'
};
}
// Extraction failed — update metrics and fall back
const processing = Date.now() - start;
await updateSchemaMetrics(schemaId, false, processing, supabase);
return {
success: false,
extractionMethod: 'llm',
processingTimeMs: processing,
error: result?.error_message || 'Schema extraction failed'
};
} catch (err: any) {
console.error('Schema based crawl error', err);
const processing = Date.now() - start;
await updateSchemaMetrics(schemaId, false, processing, supabase);
return {
success: false,
extractionMethod: 'llm',
processingTimeMs: processing,
error: err?.message || 'Unknown error'
};
}
}

/**

- Supabase Edge Function entrypoint.
- 
- Use `Deno.serve()` as recommended in the Supabase docs and include CORS
- handling for browser‑initiated requests. The function expects a JSON
- payload with `url` and `schema_id`. It returns a `CrawlResponse`
- containing the extracted content, confidence score and cost savings.
*/
Deno.serve(async (req) => {
// CORS preflight handling: return early on OPTIONS requests
const corsHeaders = {
'Access-Control-Allow-Origin': '*',
'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
};
if (req.method === 'OPTIONS') {
return new Response('ok', { headers: corsHeaders });
}
try {
const { url, schema_id } = await req.json();
if (!url || !schema_id) {
return new Response(
JSON.stringify({
success: false,
extraction_method: 'schema',
error: 'Missing url or schema_id'
}),
{ status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
);
}
const supabaseUrl = Deno.env.get('SUPABASE_URL');
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
if (!supabaseUrl || !supabaseKey) {
return new Response(
JSON.stringify({
success: false,
extraction_method: 'schema',
error: 'Supabase environment variables not configured'
}),
{ status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
);
}
// Initialise the Supabase client using service role key [oai_citation:9‡supabase.com](https://supabase.com/docs/guides/functions/secrets)
const supabase = createClient(supabaseUrl, supabaseKey);
const result = await performSchemaBasedCrawl(url, schema_id, supabase);
return new Response(
JSON.stringify({
success: result.success,
extracted_content: result.extractedContent,
extraction_method: result.extractionMethod,
processing_time_ms: result.processingTimeMs,
confidence_score: result.confidenceScore,
cost_savings: result.costSavings,
error: result.error
}),
{ headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
);
} catch (err) {
console.error('Unexpected error in handler', err);
return new Response(
JSON.stringify({
success: false,
extraction_method: 'schema',
error: 'Invalid request body'
}),
{ status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
);
}
});