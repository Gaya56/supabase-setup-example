---
mode: agent
---

# 🚨 CRITICAL TASK: Implement crawl4ai JsonCssExtractionStrategy in Supabase Edge Function

## 🎯 **TASK DEFINITION**

**Objective**: Update the existing `smart-crawler` Edge Function to integrate crawl4ai JsonCssExtractionStrategy for 90% cost reduction by eliminating LLM calls after initial schema learning.

**Critical Requirement**: The code MUST work perfectly with our existing database schema and be production-ready.

---

## 📊 **CURRENT IMPLEMENTATION STATUS**

### ✅ **COMPLETED INFRASTRUCTURE**
- **Database**: 4 tables with pgvector embeddings operational
- **Edge Functions**: 3 deployed (schema-analyzer, schema-matcher, smart-crawler v2)
- **Project URL**: https://yycmlnxomwxdqsqfccvz.supabase.co
- **Sample Schema ID**: a008ff1b-d992-4d38-a02c-aef011a03897

### ❌ **MISSING CRITICAL COMPONENT**
- **crawl4ai Integration**: Current smart-crawler uses basic HTML parsing + LLM (expensive)
- **Target**: Use JsonCssExtractionStrategy to achieve 90% cost reduction

---

## 🎯 **SPECIFIC USE CASE CONTEXT**

**Industry**: Alberta Energy & Mineral Regulatory Data Extraction
**Target Websites**: Government regulatory sites with complex, structured data
**Data Types**: Energy regulations, mineral ownership records, land tenure information

### **Production Crawling Targets**:
1. **Alberta Energy Regulator**: https://www.aer.ca/
   - Energy regulatory data and compliance information
2. **Mineral Ownership Database**: https://www.alberta.ca/mineral-ownership
   - Ownership records and regulatory information  
3. **Land Tenure Offerings**: https://content2.energy.alberta.ca/petroleum-and-natural-gas-tenure-public-offerings-and-results
   - Current and historical land purchase/lease opportunities

**Critical**: The crawler must handle government website structures efficiently and extract regulatory data accurately.

---

## 💾 **CURRENT DATABASE SCHEMA**

### **extraction_schemas** table:
```sql
CREATE TABLE extraction_schemas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  base_url TEXT NOT NULL,
  patterns JSONB DEFAULT '{}',  -- CURRENT FORMAT NEEDS CONVERSION
  embedding VECTOR(1536),
  usage_count INTEGER DEFAULT 0,
  last_used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### **ACTUAL SCHEMA FORMAT** (from database - needs conversion to crawl4ai):
```json
{
  "links": {"selector": "a[href]", "attribute": "href"},
  "title": {"required": true, "selector": "h1", "attribute": "textContent"},
  "images": {"selector": "img[src]", "attribute": "src"},
  "content": {"required": true, "selector": "body", "attribute": "textContent"},
  "metadata": {
    "author": {"selector": "", "attribute": "textContent"},
    "description": {"selector": "p", "attribute": "textContent"},
    "publishDate": {"selector": "", "attribute": "textContent|datetime"}
  }
}
```

### **crawl_results** table:
```sql
-- Key columns for storage:
url TEXT,
title TEXT,
content TEXT,
extraction_data JSONB,
extraction_schema_id UUID REFERENCES extraction_schemas(id),
extraction_quality NUMERIC CHECK (extraction_quality >= 0 AND extraction_quality <= 1),
schema_match_score NUMERIC CHECK (schema_match_score >= 0 AND schema_match_score <= 1),
content_embedding VECTOR(1536)
```

---

## 📄 **CURRENT SMART-CRAWLER FUNCTION STATUS**

### **Current File Structure**:
```
supabase/functions/smart-crawler/
├── index.ts          (EXISTS - needs crawl4ai integration)
└── deno.json         (EXISTS - needs crawl4ai import)
```

### **Current Import Pattern** (MUST FOLLOW THIS EXACT PATTERN):
```typescript
// ✅ CORRECT - Already working in current function:
import 'jsr:@supabase/functions-js/edge-runtime.d.ts';
import { createClient } from 'jsr:@supabase/supabase-js@2';
import OpenAI from 'jsr:@openai/openai';

// 🚨 ADD THIS for crawl4ai (the critical missing piece):
// Option 1 - npm: prefix (recommended for Deno Edge Functions)
import { AsyncWebCrawler, JsonCssExtractionStrategy } from 'npm:crawl4ai@latest';

// Option 2 - If npm: fails, try esm.sh
// import { AsyncWebCrawler, JsonCssExtractionStrategy } from 'https://esm.sh/crawl4ai@latest?target=deno';
```

### **Current deno.json** (MUST UPDATE THIS):
```json
{
  "imports": {
    "@supabase/supabase-js": "jsr:@supabase/supabase-js@2",
    "@openai/openai": "jsr:@openai/openai",
    "crawl4ai": "npm:crawl4ai@latest"
  }
}
```

### **Current Function Entry Point** (MUST USE THIS PATTERN):
```typescript
// ✅ CORRECT - Current pattern that works:
Deno.serve(async (req) => {
  // Your implementation here
});

// ❌ WRONG - Don't use this:
// import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
```

---

## 📚 **OFFICIAL SOURCES (MUST USE THESE EXACTLY)**

### **crawl4ai Documentation**:
- **JsonCssExtractionStrategy**: https://docs.crawl4ai.com/extraction/no-llm-strategies/
- **AsyncWebCrawler**: https://docs.crawl4ai.com/core/quickstart/
- **API Reference**: https://docs.crawl4ai.com/api/async-webcrawler/

### **Supabase Documentation**:
- **Edge Functions Dependencies**: https://supabase.com/docs/guides/functions/dependencies
- **Edge Functions Runtime**: https://supabase.com/docs/guides/functions/runtime
- **JavaScript Client**: https://supabase.com/docs/reference/javascript

### **REQUIRED crawl4ai Format** (Target Conversion):
```typescript
// Official JsonCssExtractionStrategy format from docs:
const crawl4aiSchema = {
  "baseSelector": "body",
  "fields": [
    {
      "name": "title",
      "selector": "h1", 
      "attribute": "textContent",
      "type": "text",
      "required": true
    },
    {
      "name": "content",
      "selector": ".content, p",
      "attribute": "textContent", 
      "type": "text"
    },
    {
      "name": "links",
      "selector": "a[href]",
      "attribute": "href",
      "type": "list"
    }
  ],
  "transform": "flatten"
};
```

---

## 🎯 **SPECIFIC REQUIREMENTS**

### **1. Current Function Logic to PRESERVE**:
```typescript
// ✅ KEEP - Current working patterns:
- CORS headers handling
- Request validation
- Schema detection via schema-matcher function
- Database storage in crawl_results table
- OpenAI embedding generation
- Error handling and responses

// 🚨 REPLACE - Current basic HTML parsing:
// Replace this section with real crawl4ai integration:
const response = await fetch(crawlRequest.url, {...});
const html = await response.text();
// Basic HTML parsing to extract title and content
```

### **2. Key Functions to IMPLEMENT**:
```typescript
// MUST implement these functions:
async function performSchemaBasedCrawl(url: string, schema_id: string, supabase: any): Promise<SchemaBasedResult>
function convertToCrawl4aiFormat(patterns: any): any  // Convert existing format
function calculateConfidenceScore(extractedContent: any): number
async function updateSchemaMetrics(schema_id: string, success: boolean, processing_time: number, supabase: any): Promise<void>
```

### **3. Environment Variables** (ALREADY AVAILABLE):
- `SUPABASE_URL` 
- `SUPABASE_SERVICE_ROLE_KEY`
- `OPENAI_API_KEY`

### **4. Response Format** (MUST MATCH):
```typescript
interface CrawlResponse {
  success: boolean;
  extracted_content?: any;
  extraction_method: 'schema' | 'llm' | 'basic';
  processing_time_ms: number;
  confidence_score?: number;
  cost_savings?: string;  // "90% (no LLM calls)" when schema used
  error?: string;
}
```

---

## 🔧 **CRITICAL CONVERSION LOGIC**

### **Schema Conversion Function** (CRITICAL - Must Handle Nested Objects):
```typescript
function convertToCrawl4aiFormat(patterns: any): any {
  const fields: any[] = [];
  
  function processPattern(name: string, config: any, parentPath: string = '') {
    const fieldName = parentPath ? `${parentPath}.${name}` : name;
    
    if (config.selector) {
      // Direct field
      fields.push({
        name: fieldName,
        selector: config.selector,
        attribute: config.attribute || 'textContent',
        type: Array.isArray(config.selector) ? 'list' : 'text',
        required: config.required || false
      });
    } else if (typeof config === 'object' && !config.selector) {
      // Nested object - recurse
      Object.entries(config).forEach(([key, value]) => {
        processPattern(key, value, fieldName);
      });
    }
  }
  
  Object.entries(patterns).forEach(([name, config]) => {
    processPattern(name, config);
  });
  
  return {
    baseSelector: "body",
    fields,
    transform: "flatten"
  };
}
```

---

## ⚠️ **CRITICAL CONSTRAINTS**

### **MUST Requirements**:
1. **PRESERVE EXISTING LOGIC**: Keep all current working functionality
2. **ADD crawl4ai**: Replace basic HTML parsing with real crawl4ai
3. **EXACT DATABASE COMPATIBILITY**: Use existing table structure exactly
4. **HANDLE NESTED SCHEMAS**: Support current metadata.author format
5. **GRACEFUL FALLBACK**: If crawl4ai fails, fallback to current logic

### **DON'T Requirements**:
1. **NO SCHEMA CHANGES**: Don't modify existing database tables
2. **NO BREAKING CHANGES**: Current API must keep working
3. **NO COMPLEX REFACTORING**: Keep it simple and focused

---

## 🎯 **SUCCESS CRITERIA**

### **Testing Requirements**:
```bash
# Must pass with existing schema:
curl -X POST "https://yycmlnxomwxdqsqfccvz.supabase.co/functions/v1/smart-crawler" \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.aer.ca/",
    "extraction_schema_id": "a008ff1b-d992-4d38-a02c-aef011a03897"
  }'

# Expected response with cost_savings: "90% (no LLM calls)"
```

### **Performance Targets**:
- ⚡ **Processing Time**: 1-2 seconds (vs 10-15s LLM)
- 💰 **Cost Reduction**: 90% (eliminate LLM calls for schema-based extractions)
- 🎯 **Accuracy**: Maintain >80% confidence score

---

## 🚀 **IMPLEMENTATION APPROACH**

### **Phase 1: Add crawl4ai Import**
1. Update `deno.json` with crawl4ai import
2. Add import statement to `index.ts`
3. Test basic import works

### **Phase 2: Implement Schema-Based Extraction**
1. Add `performSchemaBasedCrawl()` function
2. Add `convertToCrawl4aiFormat()` function  
3. Add confidence scoring
4. Test with existing schema

### **Phase 3: Integrate with Main Function**
1. Add schema-based extraction to main logic
2. Keep LLM fallback intact
3. Add performance tracking
4. Test complete flow

---

## 📖 **IMPORTANT NOTES**

1. **INCREMENTAL APPROACH**: Add crawl4ai without breaking existing functionality
2. **USE EXACT PATTERNS**: Follow the current function's patterns exactly
3. **HANDLE REAL SCHEMA**: Support the actual nested metadata structure
4. **PRODUCTION FOCUS**: Code must work perfectly on first deployment
5. **COST OPTIMIZATION**: This unlocks 90% cost savings for production use

**CRITICAL**: The current function already has 70% of the logic working. You only need to replace the basic HTML parsing section with real crawl4ai JsonCssExtractionStrategy integration. Keep everything else exactly the same.

---

## 🔍 **WHAT CHATGPT SHOULD DELIVER**

### **1. Updated index.ts file** with:
- Added crawl4ai import
- New `performSchemaBasedCrawl()` function using real crawl4ai
- Updated main logic to try schema-based extraction first
- All existing functionality preserved

### **2. Updated deno.json file** with:
- crawl4ai dependency added

### **3. Deployment command**:
```bash
supabase functions deploy smart-crawler
```

The goal is to transform the current expensive LLM-based system into a cost-efficient schema-based extraction system while maintaining 100% backward compatibility.