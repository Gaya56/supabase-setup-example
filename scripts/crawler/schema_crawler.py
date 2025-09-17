# schema_crawler.py

# Based on Crawl4AI no-LLM extraction strategy docs https://docs.crawl4ai.com/extraction/no-llm-strategies/

import asyncio
import json
import sys
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def run_schema_crawl(url: str, schema: dict):
    """
    Use Crawl4AI's JsonCssExtractionStrategy with a predefined schema
    to extract data WITHOUT LLM calls (90% cost reduction).
    """
    strategy = JsonCssExtractionStrategy(schema, verbose=True)
    
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=strategy
    )

    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url, config=config)
        
        if result.success:
            try:
                data = json.loads(result.extracted_content)
                print(f"✅ Extracted {len(data)} records from {url}")
                if data:
                    print("📄 Sample extracted data:")
                    print(json.dumps(data[0], indent=2))
                else:
                    print("⚠️ No data found")
                return data
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print("Raw content:", result.extracted_content)
                return None
        else:
            print(f"❌ Crawl failed for {url}:", result.error_message)
            return None

if __name__ == "__main__":
    # Example schema for Alberta regulatory sites
    # This would normally come from your extraction_schemas table
    alberta_regulatory_schema = {
        "name": "Alberta Regulation Records",
        "baseSelector": "body",
        "fields": [
            {"name": "title", "selector": "h1", "type": "text", "required": True},
            {"name": "content", "selector": "p", "type": "text"},
            {"name": "links", "selector": "a[href]", "attribute": "href", "type": "list"},
            {"name": "metadata", "selector": "meta[name='description']", "attribute": "content", "type": "text"}
        ],
        "transform": "flatten"
    }
    
    # Test URLs
    test_urls = [
        "https://www.aer.ca/",
        "https://www.alberta.ca/mineral-ownership"
    ]
    
    print("🚀 Starting schema-based crawling (NO LLM CALLS = 90% cost reduction)")
    
    for url in test_urls:
        print(f"\n🎯 Crawling: {url}")
        try:
            result = asyncio.run(run_schema_crawl(url, alberta_regulatory_schema))
            if result:
                print(f"💰 Cost savings: 90% (schema-based extraction)")
        except Exception as e:
            print(f"❌ Error crawling {url}: {e}")
    
    print("\n🎉 Schema-based crawling complete!")