# Official Resources by Implementation Step

This document organizes all official documentation URLs needed for the 4-step crawl4ai integration with Supabase implementation.

## Step 1: LLM Structure Learning

### crawl4ai Resources
- **Main Documentation**: https://docs.crawl4ai.com/
- **API Reference**: https://docs.crawl4ai.com/md/api/
- **Quickstart Guide**: https://docs.crawl4ai.com/md/quickstart/
- **LLM Extraction Strategies**: https://docs.crawl4ai.com/md/api/llm_extraction_strategy/
- **GitHub Repository**: https://github.com/unclecode/crawl4ai

### Supabase Edge Functions Resources
- **Edge Functions Documentation**: https://supabase.com/docs/guides/functions
- **Edge Functions API Reference**: https://supabase.com/docs/reference/javascript/functions-invoke
- **Edge Functions Deployment**: https://supabase.com/docs/guides/functions/deploy
- **Edge Functions Quickstart**: https://supabase.com/docs/guides/functions/quickstart
- **CLI Functions Reference**: https://supabase.com/docs/reference/cli/supabase-functions-deploy

### OpenAI Integration (for LLM extraction)
- **OpenAI API Documentation**: https://platform.openai.com/docs/api-reference
- **OpenAI Models Documentation**: https://platform.openai.com/docs/models
- **Function Calling Guide**: https://platform.openai.com/docs/guides/function-calling

## Step 2: Schema Storage

### Supabase Database Resources
- **Database Migrations**: https://supabase.com/docs/guides/deployment/database-migrations
- **PostgreSQL Functions**: https://supabase.com/docs/guides/database/functions
- **Database Schema Design**: https://supabase.com/docs/guides/database/overview
- **SQL Editor**: https://supabase.com/docs/guides/database/sql-editor

### Supabase CLI Resources
- **CLI Introduction**: https://supabase.com/docs/reference/cli/introduction
- **Database Commands**: https://supabase.com/docs/reference/cli/supabase-db-push
- **Migration Commands**: https://supabase.com/docs/guides/local-development/cli/getting-started
- **Local Development**: https://supabase.com/docs/guides/local-development/overview

### MCP (Model Context Protocol) Resources
- **Official MCP Documentation**: https://modelcontextprotocol.io/
- **TypeScript SDK**: https://github.com/modelcontextprotocol/typescript-sdk
- **Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **MCP Servers Repository**: https://github.com/modelcontextprotocol/servers
- **Example Servers**: https://modelcontextprotocol.io/examples
- **Supabase MCP Server**: https://github.com/modelcontextprotocol/servers/tree/main/src/supabase

## Step 3: Non-LLM Scraping

### crawl4ai Non-LLM Strategies
- **JsonCssExtractionStrategy**: https://docs.crawl4ai.com/md/api/css_extraction_strategy/
- **JsonXPathExtractionStrategy**: https://docs.crawl4ai.com/md/api/xpath_extraction_strategy/
- **RegexExtractionStrategy**: https://docs.crawl4ai.com/md/api/regex_extraction_strategy/
- **LLM-Free Strategies Guide**: https://docs.crawl4ai.com/md/tutorial/llm_free_strategies/

### Supabase Edge Functions (for crawling orchestration)
- **Edge Functions Runtime**: https://supabase.com/docs/guides/functions/runtime
- **Deno Runtime Documentation**: https://deno.land/manual
- **HTTP Client in Deno**: https://deno.land/manual/runtime/http_server_apis
- **Environment Variables**: https://supabase.com/docs/guides/functions/secrets

## Step 4: Data Storage with Vector Embeddings

### pgvector & Vector Search Resources
- **pgvector Extension**: https://supabase.com/docs/guides/database/extensions/pgvector
- **Vector Similarity Search**: https://supabase.com/docs/guides/ai/vector-columns
- **Semantic Search**: https://supabase.com/docs/guides/ai/semantic-search
- **AI & Vectors Guide**: https://supabase.com/docs/guides/ai
- **OpenAI Embeddings with Postgres**: https://supabase.com/blog/openai-embeddings-postgres-vector
- **Supabase Vector Module**: https://supabase.com/modules/vector

### OpenAI Embeddings Resources
- **Embeddings API**: https://platform.openai.com/docs/guides/embeddings
- **Embeddings API Reference**: https://platform.openai.com/docs/api-reference/embeddings
- **Best Practices**: https://platform.openai.com/docs/guides/embeddings/best-practices

### Supabase JavaScript Client
- **JavaScript Client Documentation**: https://supabase.com/docs/reference/javascript/introduction
- **Insert Data**: https://supabase.com/docs/reference/javascript/insert
- **Query Data**: https://supabase.com/docs/reference/javascript/select
- **RPC Functions**: https://supabase.com/docs/reference/javascript/rpc

## Cross-Step Resources

### Performance & Monitoring
- **Supabase Dashboard**: https://supabase.com/dashboard/
- **Performance Tuning**: https://supabase.com/docs/guides/platform/performance
- **Database Observability**: https://supabase.com/docs/guides/platform/logs
- **Edge Functions Logs**: https://supabase.com/docs/guides/functions/logs

### Security & Authentication
- **Row Level Security**: https://supabase.com/docs/guides/auth/row-level-security
- **API Keys Management**: https://supabase.com/docs/guides/api/api-keys
- **Environment Variables**: https://supabase.com/docs/guides/functions/secrets

### Deployment & CI/CD
- **GitHub Actions Integration**: https://supabase.com/docs/guides/cli/github-action
- **Production Deployment**: https://supabase.com/docs/guides/platform/going-live
- **CLI Deployment Commands**: https://supabase.com/docs/reference/cli/supabase-functions-deploy

## Tutorial Videos & Additional Learning

### Supabase Video Resources
- **Supabase Vector DB Crash Course**: https://www.youtube.com/watch?v=cyPZsbO5i5U
- **pgvector + RAG in Production**: https://www.youtube.com/watch?v=ibzlEQmgPPY
- **Database Migrations with CLI**: https://www.youtube.com/watch?v=Kx5nHBmIxyQ
- **Local Development Workflow**: https://www.youtube.com/watch?v=nyX_EygplXQ

### MCP Video Resources
- **MCP TypeScript Server Tutorial**: https://www.youtube.com/watch?v=kXuRJXEzrE0
- **AI Agent with TypeScript and MCP**: https://www.youtube.com/watch?v=gKkTpVeqdcY
- **MCP Python SDK Tutorial**: https://www.youtube.com/watch?v=oq3dkNm51qc
- **Model Context Protocol Overview**: https://www.youtube.com/watch?v=CQywdSdi5iA

## Implementation Priority Order

1. **Start with Step 2 (Schema Storage)**: Set up database tables using migrations
2. **Move to Step 4 (Data Storage)**: Test vector embeddings with sample data
3. **Implement Step 3 (Non-LLM Scraping)**: Build extraction pipeline with crawl4ai
4. **Add Step 1 (LLM Structure Learning)**: Enhance with intelligent schema generation

This order ensures a stable foundation before adding AI complexity.