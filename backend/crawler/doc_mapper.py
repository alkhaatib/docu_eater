"""
Documentation mapper for Docu Eater.

This module provides functionality for mapping crawled documentation into
a structured representation.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel

from .crawler import CrawlResult, NavMenuItem, DocPage

class DocSection(BaseModel):
    """Represents a section in the documentation map."""
    title: str
    url: Optional[str] = None
    pages: List[str] = []  # List of page URLs in this section
    subsections: List["DocSection"] = []
    
    model_config = {"extra": "ignore"}

class DocMap(BaseModel):
    """Represents a documentation map."""
    url: str
    pages: List[DocPage] = []
    nav_menu: List[NavMenuItem] = []
    sections: List[DocSection] = []
    
    model_config = {"extra": "ignore"}

class DocumentMapper:
    """
    Maps crawled documentation into a structured representation.
    """
    
    def generate_map(self, crawl_result: CrawlResult) -> DocMap:
        """
        Generate a documentation map from a crawl result.
        
        Args:
            crawl_result: The result of a documentation crawl.
            
        Returns:
            A structured documentation map.
        """
        # Start with basic document map
        doc_map = DocMap(
            url=crawl_result.root_url,
            pages=crawl_result.pages,
            nav_menu=crawl_result.nav_menu or []
        )
        
        # Generate sections from nav_menu if available
        if crawl_result.nav_menu:
            doc_map.sections = self._generate_sections_from_nav_menu(
                crawl_result.nav_menu,
                crawl_result.pages
            )
        
        return doc_map
    
    def _generate_sections_from_nav_menu(
        self, 
        nav_menu: List[NavMenuItem],
        pages: List[DocPage]
    ) -> List[DocSection]:
        """
        Generate document sections from navigation menu items.
        
        Args:
            nav_menu: List of navigation menu items.
            pages: List of documentation pages.
            
        Returns:
            List of document sections.
        """
        sections = []
        
        # Create a mapping of page URLs to their section
        page_to_section = {}
        for page in pages:
            if page.menu_section:
                page_to_section[page.url] = page.menu_section
        
        # Generate sections from nav menu
        for menu_item in nav_menu:
            section = DocSection(
                title=menu_item.title,
                url=menu_item.url
            )
            
            # Add pages that belong to this section
            for page in pages:
                if page.menu_section == menu_item.title:
                    section.pages.append(page.url)
            
            # Add subsections from children
            if menu_item.children:
                for child in menu_item.children:
                    subsection = DocSection(
                        title=child.title,
                        url=child.url
                    )
                    # Add pages that might belong to the subsection
                    # This is a simplified approach; in a real app, you'd need more sophisticated matching
                    for page in pages:
                        if child.url and page.url.startswith(child.url):
                            subsection.pages.append(page.url)
                    
                    section.subsections.append(subsection)
            
            sections.append(section)
        
        return sections 