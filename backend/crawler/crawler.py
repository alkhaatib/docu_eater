"""
Main crawler implementation using Crawl4AI with DFS strategy.

This module provides the DocumentCrawler class which handles crawling
documentation websites and processing the results.
"""
from typing import Dict, List, Optional, Union, Any, Tuple
from pydantic import BaseModel
import asyncio
from crawl4ai import (
    AsyncWebCrawler,
    CrawlResult as Crawl4AICrawlResult,
    CacheMode
)
import re
from bs4 import BeautifulSoup

class CrawlRequest(BaseModel):
    """Request model for initiating a crawl operation."""
    url: str
    max_depth: int = 5
    max_pages: int = 100
    respect_robots_txt: bool = True
    user_agent: str = "Docu-Eater/1.0"
    detect_nav_menu: bool = False
    sections_to_crawl: List[str] = []
    
    model_config = {"extra": "ignore"}

class NavMenuItem(BaseModel):
    """Represents an item in the navigation menu."""
    title: str
    url: str
    level: int
    children: List["NavMenuItem"] = []
    parent: Optional[str] = None
    
    model_config = {"extra": "ignore"}

class DocPage(BaseModel):
    """Represents a page in the documentation."""
    url: str
    title: str
    content: str
    links: List[str]
    raw_links: Optional[Dict[str, Any]] = None
    parent_url: Optional[str] = None
    path_segments: List[str] = []
    menu_section: Optional[str] = None
    
    model_config = {"extra": "ignore"}

class CrawlResult(BaseModel):
    """Results of a crawl operation."""
    root_url: str
    pages: List[DocPage]
    nav_menu: Optional[List[NavMenuItem]] = None
    crawl_stats: Dict[str, Any]
    
    model_config = {"extra": "ignore"}

class DocumentCrawler:
    """
    Crawler for documentation websites.
    
    Uses Crawl4AI with DFS strategy to crawl documentation websites
    and extract their structure and content.
    """
    def __init__(self):
        """
        Initialize the DocumentCrawler.
        """
        self.crawler = AsyncWebCrawler()
        self._started = False
        
    async def _ensure_started(self):
        """Ensure that the crawler has been started."""
        if not self._started:
            await self.crawler.start()
            self._started = True
    
    def _extract_links(self, links_data):
        """
        Extract links from the links data returned by Crawl4AI.
        
        Args:
            links_data: Links data from Crawl4AI.
            
        Returns:
            List of URLs.
        """
        if not links_data:
            return []
            
        extracted_links = []
        
        # Handle dictionary case
        if isinstance(links_data, dict):
            # Extract internal links
            internal_links = links_data.get('internal', [])
            for link in internal_links:
                if isinstance(link, dict) and 'href' in link:
                    extracted_links.append(link['href'])
                elif isinstance(link, str):
                    extracted_links.append(link)
            
            # Extract external links
            external_links = links_data.get('external', [])
            for link in external_links:
                if isinstance(link, dict) and 'href' in link:
                    extracted_links.append(link['href'])
                elif isinstance(link, str):
                    extracted_links.append(link)
                    
        # Handle list case
        elif isinstance(links_data, list):
            for link in links_data:
                if isinstance(link, dict) and 'href' in link:
                    extracted_links.append(link['href'])
                elif isinstance(link, str):
                    extracted_links.append(link)
        
        return extracted_links
    
    def _is_nav_link(self, link: str, base_url: str) -> bool:
        """
        Check if a link is likely part of the documentation navigation.
        
        Args:
            link: The link URL to check
            base_url: The base documentation URL
            
        Returns:
            True if the link appears to be a documentation navigation link
        """
        # Basic check for documentation links
        if not link.startswith(base_url):
            return False
            
        # Avoid anchors, query params, and non-doc pages
        if '#' in link or '?' in link:
            return False
            
        # Check if it has expected doc path patterns
        doc_patterns = [
            '/docs/', 
            '/reference/', 
            '/guides/', 
            '/tutorials/',
            '/samples/',
            '/support/',
            '/overview/',
            '/start/',
            '/beginner/'
        ]
        
        for pattern in doc_patterns:
            if pattern in link:
                return True
                
        return False
    
    def _extract_nav_menu_from_html(self, html: str, base_url: str) -> List[NavMenuItem]:
        """
        Extract the navigation menu structure from HTML content using BeautifulSoup.
        
        Args:
            html: The HTML content of the page
            base_url: The base URL of the documentation
            
        Returns:
            List of navigation menu items with their hierarchy
        """
        menu_items = []
        
        # Using BeautifulSoup for better HTML parsing
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except ImportError:
            # Fallback to regex approach if BeautifulSoup is not available
            return self._extract_nav_menu_with_regex(html, base_url)
        
        # Common navigation selectors for documentation sites
        nav_selectors = [
            'nav',  # Standard nav elements
            'div.devsite-nav-list',  # Google Cloud specific
            'div.sidebar',  # Common doc sidebar
            'div.toc',  # Table of contents
            'aside',  # Side navigation
            'ul.nav',  # Bootstrap-style nav
            '.navigation',  # Generic navigation class
            '.menu',  # Generic menu class
            '#sidebar',  # Common sidebar ID
            '#navigation'  # Common navigation ID
        ]
        
        # Try each selector until we find something useful
        nav_elements = []
        for selector in nav_selectors:
            try:
                found_elements = soup.select(selector)
                if found_elements:
                    nav_elements.extend(found_elements)
            except Exception:
                # Invalid selector or parsing error, continue to next
                continue
        
        # If no elements found with selectors, use generic approach
        if not nav_elements:
            nav_elements = soup.find_all(class_=lambda c: c and any(term in c.lower() for term in ['nav', 'menu', 'sidebar', 'toc']))
        
        if nav_elements:
            # Process each navigation element
            for nav in nav_elements:
                # Try to extract sections and links
                sections = self._process_nav_element(nav, base_url)
                if sections:
                    menu_items.extend(sections)
        
        # If no navigation elements found or not enough items, look for common patterns
        if len(menu_items) < 5:
            # Try to find structured lists that might be navigation
            list_elements = soup.find_all(['ul', 'ol'])
            
            for list_elem in list_elements:
                # Skip small lists that are unlikely to be navigation
                if len(list_elem.find_all('li')) < 3:
                    continue
                    
                # Check if this list has many links - likely a navigation menu
                links = list_elem.find_all('a', href=True)
                if len(links) >= 3:
                    # Extract links from this list and organize them
                    sections = self._process_list_as_nav(list_elem, base_url)
                    if sections:
                        menu_items.extend(sections)
                    
        # If we still don't have enough items, try a more aggressive approach
        if len(menu_items) < 5:
            # Get all links and try to organize them by URL path structure
            all_links = soup.find_all('a', href=True)
            menu_items.extend(self._organize_links_by_structure(all_links, base_url))
        
        return menu_items
    
    def _process_list_as_nav(self, list_element, base_url: str) -> List[NavMenuItem]:
        """
        Process an HTML list element as a navigation menu.
        
        Args:
            list_element: BeautifulSoup list element
            base_url: Base URL of the documentation site
            
        Returns:
            List of navigation menu items
        """
        sections = []
        current_section = None
        
        # Check for nested lists which indicate hierarchy
        for item in list_element.find_all('li', recursive=False):
            # Get the text and link from this list item
            link = item.find('a', href=True)
            if not link:
                continue
            
            link_text = link.get_text().strip()
            href = link['href']
            
            if not link_text or not href:
                continue
            
            # Make the URL absolute
            if not href.startswith('http'):
                if href.startswith('/'):
                    domain_match = re.match(r'^(https?://[^/]+)', base_url)
                    domain = domain_match.group(1) if domain_match else base_url
                    href = domain + href
                else:
                    href = base_url + '/' + href
            
            # Skip non-documentation links
            if not self._is_nav_link(href, base_url):
                continue
            
            # Check if this item has a nested list - if so, it's a section
            nested_list = item.find(['ul', 'ol'])
            
            if nested_list:
                # This is a section with children
                section_item = NavMenuItem(
                    title=link_text,
                    url=href,
                    level=0,
                    children=[]
                )
                
                # Process all links in the nested list as children
                for child_item in nested_list.find_all('li'):
                    child_link = child_item.find('a', href=True)
                    if not child_link:
                        continue
                    
                    child_text = child_link.get_text().strip()
                    child_href = child_link['href']
                    
                    if not child_text or not child_href:
                        continue
                    
                    # Make child URL absolute
                    if not child_href.startswith('http'):
                        if child_href.startswith('/'):
                            domain_match = re.match(r'^(https?://[^/]+)', base_url)
                            domain = domain_match.group(1) if domain_match else base_url
                            child_href = domain + child_href
                        else:
                            child_href = base_url + '/' + child_href
                    
                    # Add as child
                    child = NavMenuItem(
                        title=child_text,
                        url=child_href,
                        level=1,
                        parent=link_text
                    )
                    section_item.children.append(child)
                
                sections.append(section_item)
            else:
                # This is a standalone item - could be a section or child
                # If it's visually distinct (has a class that suggests heading), treat as section
                is_heading = any(c and any(term in c.lower() for term in ['heading', 'header', 'title']) 
                                for c in item.get('class', []))
                
                if is_heading:
                    # Create new section
                    section_item = NavMenuItem(
                        title=link_text,
                        url=href,
                        level=0,
                        children=[]
                    )
                    sections.append(section_item)
                    current_section = section_item
                elif current_section:
                    # Add as child to current section
                    child = NavMenuItem(
                        title=link_text,
                        url=href,
                        level=1,
                        parent=current_section.title
                    )
                    current_section.children.append(child)
                else:
                    # Standalone item, no clear parent
                    sections.append(NavMenuItem(
                        title=link_text,
                        url=href,
                        level=0,
                        children=[]
                    ))
        
        return sections
    
    def _organize_links_by_structure(self, links, base_url: str) -> List[NavMenuItem]:
        """
        Organize links into a menu structure based on URL patterns.
        
        Args:
            links: List of BeautifulSoup link elements
            base_url: Base URL of the documentation site
            
        Returns:
            List of organized NavMenuItem objects
        """
        # Group links by their first path segment
        path_groups = {}
        
        for link in links:
            href = link['href']
            text = link.get_text().strip()
            
            if not text or not href:
                continue
            
            # Make URL absolute
            if not href.startswith('http'):
                if href.startswith('/'):
                    domain_match = re.match(r'^(https?://[^/]+)', base_url)
                    domain = domain_match.group(1) if domain_match else base_url
                    href = domain + href
                else:
                    href = base_url + '/' + href
            
            # Skip non-documentation links
            if not self._is_nav_link(href, base_url):
                continue
            
            # Extract path for grouping
            path = href.replace(base_url, '').strip('/')
            path_parts = path.split('/')
            
            if path_parts:
                # Use first path segment as section
                section = path_parts[0].replace('-', ' ').replace('_', ' ').title()
                
                if section not in path_groups:
                    path_groups[section] = []
                    
                path_groups[section].append((text, href))
        
        # Convert groups to NavMenuItem objects
        menu_items = []
        
        for section, links in path_groups.items():
            if not section or len(links) < 2:
                # Skip empty sections or those with too few links
                continue
            
            section_item = NavMenuItem(
                title=section,
                url="",  # No specific URL for the section itself
                level=0,
                children=[]
            )
            
            # Add links as children
            for link_text, link_url in links:
                child = NavMenuItem(
                    title=link_text,
                    url=link_url,
                    level=1,
                    parent=section
                )
                section_item.children.append(child)
            
            menu_items.append(section_item)
        
        return menu_items
    
    def _find_menu_section(self, url: str, nav_menu: List[NavMenuItem]) -> Optional[str]:
        """
        Find which menu section a URL belongs to.
        
        Args:
            url: The URL to find the section for
            nav_menu: The navigation menu structure
            
        Returns:
            The name of the section, or None if not found
        """
        # Normalize the URL for comparison
        url = url.split('#')[0].split('?')[0].rstrip('/')
        
        # First, try to find an exact match
        for item in nav_menu:
            # Normalize item URL
            item_url = item.url.split('#')[0].split('?')[0].rstrip('/') if item.url else ""
            
            if item_url and item_url == url:
                return item.title
            
            for child in item.children:
                # Normalize child URL
                child_url = child.url.split('#')[0].split('?')[0].rstrip('/') if child.url else ""
                if child_url and child_url == url:
                    return item.title  # Return the parent section name
        
        # If no exact match, try to find by URL path
        # Extract domain and path parts from the URL
        url_domain = re.match(r'^(https?://[^/]+)', url)
        url_domain = url_domain.group(1) if url_domain else ""
        url_path = url[len(url_domain):].strip('/')
        url_parts = url_path.split('/')
        
        if url_parts:
            # Try to match by first path segment
            first_segment = url_parts[0]
            
            for item in nav_menu:
                # Check if section title contains or is contained in the first path segment
                if first_segment and (first_segment.lower() in item.title.lower() or 
                                      item.title.lower() in first_segment.lower()):
                    return item.title
                    
                # Check if URL starts with section URL
                if item.url and url.startswith(item.url):
                    return item.title
                    
                # Check children
                for child in item.children:
                    if child.url and url.startswith(child.url):
                        return item.title  # Return the parent section name
        
        return None
    
    def _print_menu_structure(self, nav_menu: List[NavMenuItem], level: int = 0):
        """Print the menu structure for debugging."""
        for item in nav_menu:
            indent = "  " * level
            url_suffix = f" -> {item.url}" if item.url else ""
            print(f"{indent}- {item.title}{url_suffix}")
            
            if item.children:
                self._print_menu_structure(item.children, level + 1)
    
    def _extract_content(self, result_obj):
        """Extract content from the result object in the best available format."""
        content = ""
        if hasattr(result_obj, 'markdown'):
            content = result_obj.markdown
        elif hasattr(result_obj, 'html'):
            content = result_obj.html
        elif hasattr(result_obj, 'extracted_content'):
            content = result_obj.extracted_content
        return content or ""
    
    def _extract_path_segments(self, url: str, root_url: str) -> List[str]:
        """
        Extract path segments from URL to establish hierarchy.
        
        Args:
            url: The URL to extract path segments from.
            root_url: The root URL of the documentation site.
            
        Returns:
            List of path segments.
        """
        # Strip the root URL to get relative path
        if url.startswith(root_url):
            relative_path = url[len(root_url):].strip('/')
        else:
            return []
            
        # Remove any anchor or query parameters
        relative_path = relative_path.split('#')[0].split('?')[0]
            
        # Split into segments
        if not relative_path:
            return []
        return relative_path.split('/')

    async def extract_menu_structure(self, url: str) -> List[NavMenuItem]:
        """
        Extract the navigation menu structure from a documentation site.
        
        Args:
            url: The URL of the documentation site
            
        Returns:
            List of navigation menu items with their hierarchy
        """
        # Make sure the crawler is started
        await self._ensure_started()
        
        # Crawl the page
        result = await self.crawler.arun(
            url=url,
            respect_robots_txt=True,
            user_agent="Docu-Eater/1.0"
        )
        
        # Extract the HTML content
        html = ""
        if hasattr(result, 'html'):
            html = result.html
        elif hasattr(result, 'cleaned_html'):
            html = result.cleaned_html
        
        # Extract the navigation menu
        return self._extract_nav_menu_from_html(html, url)

    async def crawl_site(self, request: CrawlRequest) -> CrawlResult:
        """
        Crawl a documentation website.
        
        Args:
            request: Crawl request parameters.
            
        Returns:
            Processed crawl results.
        """
        # Make sure the crawler is started
        await self._ensure_started()
        
        # Extract the navigation menu if requested
        nav_menu = None
        if request.detect_nav_menu:
            print("Extracting navigation menu structure...")
            nav_menu = await self.extract_menu_structure(request.url)
            print(f"Found {len(nav_menu)} top-level menu sections")
            
            # Print the menu structure for debugging
            self._print_menu_structure(nav_menu)
            
            # If specific sections are requested, filter the links to crawl
            if request.sections_to_crawl:
                return await self._crawl_specific_sections(request, nav_menu)
        
        # Try to manually crawl multiple pages
        pages = []
        root_page_result = await self.crawler.arun(
            url=request.url,
            respect_robots_txt=request.respect_robots_txt,
            user_agent=request.user_agent
        )
        
        # Process the root page
        content = self._extract_content(root_page_result)
        links = self._extract_links(getattr(root_page_result, 'links', {}))
        
        # Add the root page to our results
        root_doc_page = DocPage(
            url=request.url,
            title=getattr(root_page_result, 'title', "Untitled") or "Untitled",
            content=content,
            links=links,
            raw_links=getattr(root_page_result, 'links', {}),
            path_segments=self._extract_path_segments(request.url, request.url)
        )
        pages.append(root_doc_page)
        
        # Now try to crawl a few of the internal links
        print(f"Found {len(links)} links on the root page")
        internal_links = []
        for link in links:
            # Only follow links to the same domain
            if request.url in link and link != request.url:
                internal_links.append(link)
        
        # Limit to max_pages - 1 (because we already have the root page)
        internal_links = internal_links[:min(request.max_pages - 1, len(internal_links))]
        print(f"Attempting to crawl {len(internal_links)} internal links")
        
        # Crawl each internal link
        for i, link in enumerate(internal_links):
            try:
                print(f"Crawling link {i+1}/{len(internal_links)}: {link}")
                page_result = await self.crawler.arun(
                    url=link,
                    respect_robots_txt=request.respect_robots_txt,
                    user_agent=request.user_agent
                )
                
                # Process the page
                content = self._extract_content(page_result)
                sub_links = self._extract_links(getattr(page_result, 'links', {}))
                
                # Try to determine the menu section
                menu_section = None
                if nav_menu:
                    menu_section = self._find_menu_section(link, nav_menu)
                
                # Add the page to our results
                doc_page = DocPage(
                    url=link,
                    title=getattr(page_result, 'title', "Untitled") or "Untitled",
                    content=content,
                    links=sub_links,
                    raw_links=getattr(page_result, 'links', {}),
                    parent_url=request.url,
                    path_segments=self._extract_path_segments(link, request.url),
                    menu_section=menu_section
                )
                pages.append(doc_page)
            except Exception as e:
                print(f"Error crawling {link}: {e}")
                continue
        
        return CrawlResult(
            root_url=request.url,
            pages=pages,
            nav_menu=nav_menu,
            crawl_stats={
                "total_pages": len(pages),
                "elapsed_time": 0,  # We don't have a combined elapsed time
                "success_rate": len(pages) / (len(internal_links) + 1) if internal_links else 1.0
            }
        )

    async def _crawl_specific_sections(self, request: CrawlRequest, nav_menu: List[NavMenuItem]) -> CrawlResult:
        """
        Crawl specific sections of the documentation based on the navigation menu.
        
        Args:
            request: The crawl request parameters
            nav_menu: The navigation menu structure
            
        Returns:
            The crawl results for the requested sections
        """
        pages = []
        section_urls = []
        
        # Extract all URLs from the requested sections
        for section_name in request.sections_to_crawl:
            section_urls.extend(self._get_urls_for_section(section_name, nav_menu))
        
        # Limit the number of pages to crawl
        section_urls = section_urls[:request.max_pages]
        
        print(f"Found {len(section_urls)} URLs in the requested sections")
        
        # Crawl each URL
        for i, url in enumerate(section_urls):
            try:
                print(f"Crawling section URL {i+1}/{len(section_urls)}: {url}")
                page_result = await self.crawler.arun(
                    url=url,
                    respect_robots_txt=request.respect_robots_txt,
                    user_agent=request.user_agent
                )
                
                # Process the page
                content = self._extract_content(page_result)
                links = self._extract_links(getattr(page_result, 'links', {}))
                
                # Find the section this URL belongs to
                section = self._find_menu_section(url, nav_menu)
                
                # Add the page to our results
                doc_page = DocPage(
                    url=url,
                    title=getattr(page_result, 'title', "Untitled") or "Untitled",
                    content=content,
                    links=links,
                    raw_links=getattr(page_result, 'links', {}),
                    parent_url=request.url,
                    path_segments=self._extract_path_segments(url, request.url),
                    menu_section=section
                )
                pages.append(doc_page)
            except Exception as e:
                print(f"Error crawling {url}: {e}")
                continue
            
        return CrawlResult(
            root_url=request.url,
            pages=pages,
            nav_menu=nav_menu,
            crawl_stats={
                "total_pages": len(pages),
                "elapsed_time": 0,  # We don't have a combined elapsed time
                "success_rate": len(pages) / len(section_urls) if section_urls else 1.0
            }
        )

    def _get_urls_for_section(self, section_name: str, nav_menu: List[NavMenuItem]) -> List[str]:
        """
        Get all URLs for a specific section in the navigation menu.
        
        Args:
            section_name: The name of the section to get URLs for
            nav_menu: The navigation menu structure
            
        Returns:
            List of URLs in the specified section
        """
        urls = []
        
        # Try using fuzzy matching for better section identification
        for item in nav_menu:
            # Check if this item matches the section name (case-insensitive partial match)
            if section_name.lower() in item.title.lower() or item.title.lower() in section_name.lower():
                # Add this item's URL if it has one
                if item.url:
                    urls.append(item.url)
                
                # Add all child URLs
                for child in item.children:
                    if child.url:
                        urls.append(child.url)
                    
                if urls:  # Only return if we found URLs to avoid false matches
                    return urls
            
            # Check children
            for child in item.children:
                if section_name.lower() in child.title.lower() or child.title.lower() in section_name.lower():
                    # Add this item's URL
                    if child.url:
                        urls.append(child.url)
                    return urls  # Return even with empty list to indicate section was found
                
        return urls 

    def _extract_nav_menu_with_regex(self, html: str, base_url: str) -> List[NavMenuItem]:
        """
        Extract the navigation menu structure from HTML content using regex.
        
        Args:
            html: The HTML content of the page
            base_url: The base URL of the documentation
            
        Returns:
            List of navigation menu items with their hierarchy
        """
        menu_items = []
        
        # Look for common navigation menu patterns
        # This is a simplified approach - in a production environment, you'd want to use
        # a proper HTML parser like BeautifulSoup
        
        # Try to find navigation sections 
        nav_section_pattern = re.compile(r'<nav[^>]*>(.*?)</nav>', re.DOTALL)
        nav_sections = nav_section_pattern.findall(html)
        
        # Find menu headings and links
        heading_pattern = re.compile(r'<h\d[^>]*>(.*?)</h\d>', re.DOTALL)
        link_pattern = re.compile(r'<a[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>', re.DOTALL)
        
        section_level = 0
        current_section = None
        
        for nav_section in nav_sections:
            # Extract headings
            headings = heading_pattern.findall(nav_section)
            
            # Extract links
            links = link_pattern.findall(nav_section)
            
            # Process headings as main sections
            for heading in headings:
                clean_heading = re.sub(r'<[^>]*>', '', heading).strip()
                if clean_heading:
                    section_level = 0
                    current_section = clean_heading
                    menu_items.append(NavMenuItem(
                        title=clean_heading,
                        url="",  # Section headings might not have URLs
                        level=section_level,
                        children=[]
                    ))
            
            # Process links
            for url, text in links:
                clean_text = re.sub(r'<[^>]*>', '', text).strip()
                if clean_text and url:
                    # Make sure URL is absolute
                    if not url.startswith('http'):
                        if url.startswith('/'):
                            # Get domain from base_url
                            domain_match = re.match(r'^(https?://[^/]+)', base_url)
                            domain = domain_match.group(1) if domain_match else base_url
                            url = domain + url
                        else:
                            url = base_url + '/' + url
                        
                    # Remove any anchor or query params
                    url = url.split('#')[0].split('?')[0]
                    
                    # Skip non-documentation links
                    if not self._is_nav_link(url, base_url):
                        continue
                    
                    # Determine level based on indentation or context
                    level = 1  # Default level
                    
                    # Create menu item
                    menu_item = NavMenuItem(
                        title=clean_text,
                        url=url,
                        level=level,
                        parent=current_section
                    )
                    
                    # If we have a current section, add as child, otherwise add to top level
                    if current_section and menu_items:
                        menu_items[-1].children.append(menu_item)
                    else:
                        menu_items.append(menu_item)
        
        # If nav_sections extraction didn't yield enough results, try a more general approach
        if len(menu_items) < 5:
            # Extract all links and try to organize them
            all_links = link_pattern.findall(html)
            section_links = {}
            
            for url, text in all_links:
                clean_text = re.sub(r'<[^>]*>', '', text).strip()
                if clean_text and url:
                    # Make sure URL is absolute
                    if not url.startswith('http'):
                        if url.startswith('/'):
                            # Get domain from base_url
                            domain_match = re.match(r'^(https?://[^/]+)', base_url)
                            domain = domain_match.group(1) if domain_match else base_url
                            url = domain + url
                        else:
                            url = base_url + '/' + url
                    
                    # Only include documentation links
                    if self._is_nav_link(url, base_url):
                        # Try to get the section from the URL structure
                        path_parts = url.replace(base_url, '').strip('/').split('/')
                        if path_parts:
                            section = path_parts[0].capitalize()
                            if section not in section_links:
                                section_links[section] = []
                            section_links[section].append((clean_text, url))
            
            # Create menu items from structured links
            for section, links in section_links.items():
                section_item = NavMenuItem(
                    title=section,
                    url="",
                    level=0,
                    children=[]
                )
                
                for link_text, link_url in links:
                    child_item = NavMenuItem(
                        title=link_text,
                        url=link_url,
                        level=1,
                        parent=section
                    )
                    section_item.children.append(child_item)
                
                menu_items.append(section_item)
        
        return menu_items

    def _process_nav_element(self, nav_element, base_url: str) -> List[NavMenuItem]:
        """
        Process a navigation element to extract sections and links.
        
        Args:
            nav_element: The BeautifulSoup element to process
            base_url: The base URL of the documentation
            
        Returns:
            List of navigation menu items
        """
        sections = []
        current_section = None
        
        # Find all headings in the navigation
        headings = nav_element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) or \
                  nav_element.find_all(class_=lambda c: c and ('heading' in c.lower() or 'header' in c.lower()))
        
        # Find all links in the navigation
        links = nav_element.find_all('a', href=True)
        
        # If there are headings, use them as sections
        if headings:
            for heading in headings:
                heading_text = heading.get_text().strip()
                if heading_text:
                    # Check if heading contains a link
                    heading_link = heading.find('a', href=True)
                    heading_url = ""
                    if heading_link and heading_link['href']:
                        href = heading_link['href']
                        if not href.startswith('http'):
                            if href.startswith('/'):
                                domain_match = re.match(r'^(https?://[^/]+)', base_url)
                                domain = domain_match.group(1) if domain_match else base_url
                                href = domain + href
                            else:
                                href = base_url + '/' + href
                        heading_url = href
                    
                    section_item = NavMenuItem(
                        title=heading_text,
                        url=heading_url,
                        level=0,
                        children=[]
                    )
                    sections.append(section_item)
                    current_section = section_item
        
        # Process links
        for link in links:
            link_text = link.get_text().strip()
            href = link['href']
            
            if not link_text or not href:
                continue
            
            # Make the URL absolute
            if not href.startswith('http'):
                if href.startswith('/'):
                    domain_match = re.match(r'^(https?://[^/]+)', base_url)
                    domain = domain_match.group(1) if domain_match else base_url
                    href = domain + href
                else:
                    href = base_url + '/' + href
            
            # Skip non-documentation links
            if not self._is_nav_link(href, base_url):
                continue
            
            # Determine if it's a section link or child link based on HTML structure
            is_section_link = False
            parent = link.parent
            while parent and parent != nav_element:
                if parent.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] or (parent.get('class') and any('heading' in c.lower() for c in parent.get('class'))):
                    is_section_link = True
                    break
                parent = parent.parent
            
            if is_section_link and not current_section:
                # Create a new section
                section_item = NavMenuItem(
                    title=link_text,
                    url=href,
                    level=0,
                    children=[]
                )
                sections.append(section_item)
                current_section = section_item
            elif is_section_link and current_section:
                # Update current section
                current_section.title = link_text
                current_section.url = href
            elif current_section:
                # Add as child to current section
                child_item = NavMenuItem(
                    title=link_text,
                    url=href,
                    level=1,
                    parent=current_section.title
                )
                current_section.children.append(child_item)
            else:
                # Standalone link, treat as its own section
                sections.append(NavMenuItem(
                    title=link_text,
                    url=href,
                    level=0,
                    children=[]
                ))
        
        return sections 