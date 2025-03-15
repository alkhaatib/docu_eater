"""
Tests for the crawler module.
"""
import pytest
import asyncio
from crawler.crawler import DocumentCrawler, CrawlRequest
from crawler.doc_mapper import DocumentMapper

@pytest.mark.asyncio
async def test_crawler_basic():
    """Test basic crawler functionality with a simple website."""
    crawler = DocumentCrawler()
    request = CrawlRequest(
        url="https://example.com",
        max_depth=1,
        max_pages=2
    )
    
    # This is a simple test that just verifies the crawler works
    # In a real test, we would mock the crawl4ai.crawler.Crawler
    # but for now we'll just make a simple request to a known site
    result = await crawler.crawl_site(request)
    
    # Basic assertions
    assert result.root_url == "https://example.com"
    assert len(result.pages) > 0
    
@pytest.mark.asyncio
async def test_doc_mapper_basic():
    """Test document mapper with a simple crawl result."""
    from crawler.crawler import DocPage, CrawlResult
    
    # Create a mock crawl result
    crawl_result = CrawlResult(
        root_url="https://example.com",
        pages=[
            DocPage(
                url="https://example.com",
                title="Example Domain",
                content="This domain is for use in examples.",
                links=[],
                path_segments=[]
            ),
            DocPage(
                url="https://example.com/page1",
                title="Page 1",
                content="This is page 1.",
                links=[],
                path_segments=["page1"]
            ),
            DocPage(
                url="https://example.com/docs/page2",
                title="Page 2",
                content="This is page 2.",
                links=[],
                path_segments=["docs", "page2"]
            )
        ],
        crawl_stats={
            "total_pages": 3,
            "elapsed_time": 1.0,
            "success_rate": 1.0
        }
    )
    
    mapper = DocumentMapper()
    doc_map = mapper.generate_map(crawl_result)
    
    # Basic assertions
    assert doc_map.root.url == "https://example.com"
    assert doc_map.pages_count == 3
    assert "page1" in doc_map.root.children
    assert "docs" in doc_map.root.children
    assert "page2" in doc_map.root.children["docs"].children
    
if __name__ == "__main__":
    # Run the tests manually
    asyncio.run(test_crawler_basic())
    asyncio.run(test_doc_mapper_basic())
    print("All tests passed!") 