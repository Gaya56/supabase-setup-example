# llm_discovery.py

# Based on Crawl4AI LLM extraction strategy docs https://docs.crawl4ai.com/extraction/no-llm-strategies/

import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonSchemaExtractionStrategy

async def discover_schema(url: str):
    """
    Use Crawl4AI's LLM-based JsonSchemaExtractionStrategy to discover 
    extraction schemas for Alberta regulatory sites.
    """
    strategy = JsonSchemaExtractionStrategy(
        instruction="Extract meaningful fields (title, content, links, metadata) from this Alberta regulatory page.",
        schema_name="AlbertaRegulatorySchema",
        enforce=True,
        verbose=True
    )

    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=strategy
    )

    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url, config=config)
        
        if result.success:
            print(f"\n=== DISCOVERED SCHEMA FOR {url} ===")
            print("Discovered schema JSON:\n", result.extracted_content)
            print("=" * 60)
            return result.extracted_content
        else:
            print(f"Error discovering schema for {url}:", result.error_message)
            return None

if __name__ == "__main__":
    # Alberta regulatory sites for schema discovery
    urls = [
        "https://www.aer.ca/",
        "https://www.alberta.ca/mineral-ownership",
        "https://content2.energy.alberta.ca/petroleum-and-natural-gas-tenure-public-offerings-and-results"
    ]
    
    print("🔍 Starting schema discovery for Alberta regulatory sites...")
    
    for url in urls:
        print(f"\n📊 Discovering schema for: {url}")
        try:
            asyncio.run(discover_schema(url))
        except Exception as e:
            print(f"❌ Failed to discover schema for {url}: {e}")
    
    print("\n✅ Schema discovery complete!")
    print("💡 Copy the discovered schemas to your extraction_schemas table")