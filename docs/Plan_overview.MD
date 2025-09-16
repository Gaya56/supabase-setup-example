## 🎯 **Project Goal**

Intelligent web crawling system using **4-step approach**: LLM structure learning → Schema storage → Non-LLM scraping → Data storage with embeddings.

### 📋 **Architecture:**

- **Step 1**: LLM analyzes website structure, generates crawl4ai schemas
- **Step 2**: Store schemas with embeddings for intelligent matching  
- **Step 3**: Reuse schemas for fast JsonCssExtractionStrategy scraping
- **Step 4**: Store data in Supabase with automatic embedding generation

### 🔧 **Key Technologies:**

- **Crawl4ai JsonCssExtractionStrategy** → Fast, LLM-free extraction
- **Supabase MCP** → Direct database operations via Claude
- **Vector Embeddings** → Semantic search and schema matching
- **Edge Functions** → Serverless processing pipeline

### 🎯 **Benefits:**

- **90% cost reduction** after initial learning phase
- **10x speed improvement** using schema-based extraction
- **Learning system** that gets smarter over time
- **Seamless MCP integration** for Claude access

**Implementation Status**: Comprehensive plan documented in `4-Step_Crawl4ai_Integration_Plan.md`