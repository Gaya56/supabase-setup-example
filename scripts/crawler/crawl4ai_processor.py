"""
Crawl4ai Processor - Official Quickstart Implementation
Reference: https://docs.crawl4ai.com/md/quickstart/
"""
import asyncio
from typing import Dict, Any
from datetime import datetime

try:
    from crawl4ai import AsyncWebCrawler
except ImportError:
    print("❌ crawl4ai not installed. Run: pip install crawl4ai")
    raise


class Crawl4aiProcessor:
    """
    Basic crawl4ai implementation following official quickstart
    https://docs.crawl4ai.com/md/quickstart/
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.crawler = None
    
    async def __aenter__(self):
        """Initialize crawler - from official docs"""
        self.crawler = AsyncWebCrawler(verbose=self.verbose)
        await self.crawler.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up crawler - from official docs"""
        if self.crawler:
            await self.crawler.__aexit__(exc_type, exc_val, exc_tb)
    
    async def crawl_url(self, url: str) -> Dict[str, Any]:
        """
        Basic crawling implementation from official quickstart
        https://docs.crawl4ai.com/md/quickstart/
        """
        if not self.crawler:
            raise RuntimeError("Crawler not initialized. Use async context manager.")
        
        print(f"🔍 Crawling: {url}")
        start_time = datetime.now()
        
        try:
            # Official quickstart pattern
            result = await self.crawler.arun(url=url)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if result.success:
                # Extract basic data following official docs structure
                crawl_data = {
                    'url': url,
                    'title': result.metadata.get('title', '') if result.metadata else '',
                    'content': result.markdown or '',
                    'content_length': len(result.markdown) if result.markdown else 0,
                    'content_hash': hash(result.markdown.strip()) if result.markdown else 0,
                    'metadata': {
                        'status_code': result.status_code,
                        'page_metadata': result.metadata or {},
                        'links_count': len(result.links.get('internal', [])) + len(result.links.get('external', [])) if result.links else 0,
                        'images_count': len(result.media.get('images', [])) if result.media else 0
                    },
                    'extraction_data': {
                        'method': 'basic_crawl',
                        'success': True,
                        'processing_time_ms': int(processing_time),
                        'timestamp': datetime.now().isoformat()
                    },
                    'crawled_at': datetime.now().isoformat()
                }
                
                print(f"✅ Success: {len(result.markdown)} chars extracted")
                return crawl_data
            
            else:
                print(f"❌ Failed: {result.error_message}")
                return self._create_error_result(url, result.error_message, processing_time)
                
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            print(f"❌ Exception: {str(e)}")
            return self._create_error_result(url, str(e), processing_time)
    
    def _create_error_result(self, url: str, error: str, processing_time: float) -> Dict[str, Any]:
        """Create standardized error result"""
        return {
            'url': url,
            'title': '',
            'content': '',
            'content_length': 0,
            'content_hash': 0,
            'metadata': {'error': error},
            'extraction_data': {
                'method': 'basic_crawl',
                'success': False,
                'error': error,
                'processing_time_ms': int(processing_time)
            },
            'crawled_at': datetime.now().isoformat()
        }


async def test_crawler():
    """Test function following official quickstart pattern"""
    test_url = "https://example.com"
    
    async with Crawl4aiProcessor() as processor:
        result = await processor.crawl_url(test_url)
        print(f"\nTest Result:")
        print(f"URL: {result['url']}")
        print(f"Title: {result['title']}")
        print(f"Content Length: {result['content_length']}")
        print(f"Success: {result['extraction_data']['success']}")


if __name__ == "__main__":
    # Official docs pattern for running async code
    asyncio.run(test_crawler())