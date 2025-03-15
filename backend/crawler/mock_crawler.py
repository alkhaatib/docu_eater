"""
Mock crawler module to use if crawl4ai is causing issues.
This provides a complete replacement for the crawler functionality
to allow testing without external dependencies.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, field_validator
import asyncio
import random
import time
from datetime import datetime

class CrawlRequest(BaseModel):
    """Request model for initiating a crawl operation."""
    url: str
    max_depth: int = 5
    max_pages: int = 100
    respect_robots_txt: bool = True
    user_agent: str = "Docu-Eater/1.0"
    detect_nav_menu: bool = False
    sections_to_crawl: List[str] = []
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v
    
    model_config = {"extra": "ignore"}

class MockPage(BaseModel):
    """Mock page class for testing."""
    url: str
    title: str
    content: str = "This is mock content for testing purposes."
    links: List[str] = []
    menu_section: Optional[str] = None
    raw_links: Optional[Dict[str, Any]] = None
    parent_url: Optional[str] = None
    path_segments: List[str] = []

class CrawlResult(BaseModel):
    """Mock CrawlResult for testing."""
    url: str
    pages: List[MockPage] = []
    crawl_stats: Dict[str, Any] = {"total_pages": 0, "success_rate": 0.0}

class DocMap(BaseModel):
    """Mock DocMap for testing."""
    url: str
    pages: List[MockPage] = []
    nav_menu: List[Any] = []

class NavMenuItem(BaseModel):
    """Represents an item in the navigation menu."""
    title: str
    url: str
    level: int
    children: List["NavMenuItem"] = []
    parent: Optional[str] = None
    
    model_config = {"extra": "ignore"}

class DocumentMapper:
    """Mock document mapper for testing."""
    
    def generate_map(self, crawl_result: CrawlResult) -> DocMap:
        """Generate a document map from crawl results."""
        # Create mock navigation menu
        nav_menu = []
        sections = ["Getting Started", "API Reference", "Examples", "FAQ"]
        
        for i, section in enumerate(sections):
            menu_item = NavMenuItem(
                title=section,
                url=f"{crawl_result.url}/{section.lower().replace(' ', '-')}",
                level=1,
                children=[]
            )
            
            # Add sub-items
            for j in range(3):
                child = NavMenuItem(
                    title=f"{section} {j+1}",
                    url=f"{menu_item.url}/{j+1}",
                    level=2,
                    parent=section
                )
                menu_item.children.append(child)
                
            nav_menu.append(menu_item)
        
        # Assign menu sections to pages
        pages = list(crawl_result.pages)
        for i, page in enumerate(pages):
            if i < len(pages) * 0.8:  # 80% have a section
                section_idx = i % len(sections)
                page.menu_section = sections[section_idx]
        
        return DocMap(
            url=crawl_result.url,
            pages=pages,
            nav_menu=nav_menu
        )

class DocumentCrawler:
    """Mock crawler for testing."""
    
    async def crawl_site(self, request: CrawlRequest) -> CrawlResult:
        """Mock crawl site method."""
        # Simulate crawling delay
        await asyncio.sleep(2)
        
        # Generate mock pages
        page_count = min(request.max_pages, 20)  # Generate up to 20 pages for testing
        pages = []
        
        # Generate main sections
        sections = ["Getting Started", "API Reference", "Examples", "FAQ"]
        
        for i in range(page_count):
            # Create path segments
            path_segments = []
            if i > 0:
                section = sections[i % len(sections)]
                path_segments = [section.lower().replace(' ', '-')]
                
                if i > len(sections):
                    sub_section = f"topic-{(i // len(sections))}"
                    path_segments.append(sub_section)
            
            # Make URL from path segments
            url = request.url
            if path_segments:
                url = f"{url}/{'/'.join(path_segments)}"
            
            # Create title from URL
            title_parts = path_segments if path_segments else ["Home"]
            title = f"{title_parts[-1].replace('-', ' ').title()} - Documentation"
            
            # Generate links (some internal, some external)
            links = []
            for j in range(random.randint(3, 8)):
                if random.random() > 0.2:  # 80% internal links
                    link_section = sections[random.randint(0, len(sections)-1)]
                    links.append(f"{request.url}/{link_section.lower().replace(' ', '-')}")
                else:
                    links.append(f"https://external-site-{j}.com")
            
            # Create page
            page = MockPage(
                url=url,
                title=title,
                content=f"This is mock content for {title}. " * 20,  # Make content longer
                links=links,
                path_segments=path_segments,
                menu_section=sections[i % len(sections)] if i > 0 else None
            )
            pages.append(page)
        
        # Create crawl stats
        crawl_stats = {
            "total_pages": len(pages),
            "success_rate": 1.0,
            "crawl_time": 2.0,
            "url": request.url,
            "start_time": datetime.now().isoformat()
        }
        
        result = CrawlResult(
            url=request.url,
            pages=pages,
            crawl_stats=crawl_stats
        )
        
        return result 