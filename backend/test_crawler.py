"""
Simple test script to verify the crawler functionality.
"""
import asyncio
import sys
from crawler.crawler import DocumentCrawler, CrawlRequest
import os
import json

async def test_crawler():
    """Test the DocumentCrawler with the Google Cloud Vertex AI documentation."""
    print("Initializing DocumentCrawler...")
    crawler = DocumentCrawler()
    
    # Create a crawl request for the Vertex AI documentation with menu detection enabled
    request = CrawlRequest(
        url="https://cloud.google.com/vertex-ai/docs",
        max_depth=2,  # Increased depth to capture more structure
        max_pages=10,  # Increased to capture more pages but not too many
        detect_nav_menu=True  # Enable navigation menu detection
    )
    
    print(f"Starting crawl of {request.url}...")
    try:
        # First, check if the crawler object is properly initialized
        print(f"Crawler initialized: {crawler.crawler is not None}")
        
        # Check if we need to start the crawler
        if hasattr(crawler.crawler, 'start') and not getattr(crawler.crawler, 'ready', False):
            print("Starting crawler...")
            await crawler.crawler.start()
        
        print("Attempting to crawl the Vertex AI documentation site...")
        result = await crawler.crawl_site(request)
        print(f"Crawl completed successfully!")
        
        # Display summary information
        print("\n" + "="*80)
        print(f"CRAWL SUMMARY FOR: {result.root_url}")
        print("="*80)
        print(f"Total pages crawled: {result.crawl_stats['total_pages']}")
        print(f"Success rate: {result.crawl_stats['success_rate']:.2%}")
        
        # Calculate some statistics
        total_content_size = sum(len(page.content) for page in result.pages)
        total_links = sum(len(page.links) for page in result.pages)
        total_internal_links = sum(len(page.raw_links.get('internal', [])) for page in result.pages if page.raw_links)
        total_external_links = sum(len(page.raw_links.get('external', [])) for page in result.pages if page.raw_links)
        
        print(f"Total content size: {total_content_size:,} characters")
        print(f"Total links found: {total_links:,}")
        print(f"Total internal links: {total_internal_links:,}")
        print(f"Total external links: {total_external_links:,}")
        
        # Display navigation menu information if available
        if result.nav_menu:
            print("\n" + "-"*80)
            print("NAVIGATION MENU STRUCTURE")
            print("-"*80)
            print(f"Total sections: {len(result.nav_menu)}")
            
            # Count total menu items
            total_menu_items = len(result.nav_menu)
            for section in result.nav_menu:
                total_menu_items += len(section.children)
            
            print(f"Total menu items: {total_menu_items}")
            
            # Print all sections
            print("\nDetected Sections:")
            for section in result.nav_menu:
                children_count = len(section.children)
                print(f"- {section.title} ({children_count} items)")
                
                # Print a sample of children for each section
                if section.children:
                    for i, child in enumerate(section.children[:3]):
                        print(f"  - {child.title} -> {child.url}")
                    
                    if len(section.children) > 3:
                        print(f"  - ... and {len(section.children) - 3} more items")
            
            # Save the menu structure to a JSON file
            menu_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "menu_structure.json")
            with open(menu_file, 'w') as f:
                # Convert the menu to a serializable format
                json_menu = []
                for section in result.nav_menu:
                    section_data = {
                        "title": section.title,
                        "url": section.url,
                        "level": section.level,
                        "children": []
                    }
                    
                    for child in section.children:
                        child_data = {
                            "title": child.title,
                            "url": child.url,
                            "level": child.level
                        }
                        section_data["children"].append(child_data)
                    
                    json_menu.append(section_data)
                
                json.dump(json_menu, f, indent=2)
            
            print(f"\nNavigation menu structure saved to: {menu_file}")
        
        # Display information about each page
        print("\n" + "-"*80)
        print("PAGES CRAWLED")
        print("-"*80)
        for i, page in enumerate(result.pages):
            print(f"\n{i+1}. {page.url}")
            
            # Extract path segments if any
            path = "/".join(page.path_segments) if page.path_segments else "/"
            print(f"   Path: {path}")
            
            # Display menu section if available
            if page.menu_section:
                print(f"   Section: {page.menu_section}")
            
            print(f"   Title: {page.title}")
            print(f"   Content size: {len(page.content):,} characters")
            print(f"   Links: {len(page.links):,} total")
            
            if page.raw_links:
                internal = len(page.raw_links.get('internal', []))
                external = len(page.raw_links.get('external', []))
                print(f"   Internal links: {internal:,}")
                print(f"   External links: {external:,}")
        
        # Save results to a file
        results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
        os.makedirs(results_dir, exist_ok=True)
        
        summary_file = os.path.join(results_dir, "crawl_summary.txt")
        with open(summary_file, 'w') as f:
            f.write(f"CRAWL SUMMARY FOR: {result.root_url}\n")
            f.write("="*80 + "\n")
            f.write(f"Total pages crawled: {result.crawl_stats['total_pages']}\n")
            f.write(f"Success rate: {result.crawl_stats['success_rate']:.2%}\n")
            f.write(f"Total content size: {total_content_size:,} characters\n")
            f.write(f"Total links found: {total_links:,}\n")
            f.write(f"Total internal links: {total_internal_links:,}\n")
            f.write(f"Total external links: {total_external_links:,}\n")
            
            if result.nav_menu:
                f.write("\n" + "-"*80 + "\n")
                f.write("NAVIGATION MENU STRUCTURE\n")
                f.write("-"*80 + "\n")
                f.write(f"Total sections: {len(result.nav_menu)}\n")
                
                # Count total menu items
                total_menu_items = len(result.nav_menu)
                for section in result.nav_menu:
                    total_menu_items += len(section.children)
                
                f.write(f"Total menu items: {total_menu_items}\n\n")
                
                # Write all sections
                f.write("Detected Sections:\n")
                for section in result.nav_menu:
                    children_count = len(section.children)
                    f.write(f"- {section.title} ({children_count} items)\n")
            
            f.write("\n" + "-"*80 + "\n")
            f.write("PAGES CRAWLED\n")
            f.write("-"*80 + "\n")
            
            for i, page in enumerate(result.pages):
                f.write(f"\n{i+1}. {page.url}\n")
                path = "/".join(page.path_segments) if page.path_segments else "/"
                f.write(f"   Path: {path}\n")
                
                if page.menu_section:
                    f.write(f"   Section: {page.menu_section}\n")
                
                f.write(f"   Title: {page.title}\n")
                f.write(f"   Content size: {len(page.content):,} characters\n")
                f.write(f"   Links: {len(page.links):,} total\n")
                
                if page.raw_links:
                    internal = len(page.raw_links.get('internal', []))
                    external = len(page.raw_links.get('external', []))
                    f.write(f"   Internal links: {internal:,}\n")
                    f.write(f"   External links: {external:,}\n")
        
        print(f"\nCrawl summary saved to: {summary_file}")
        return True
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_specific_sections():
    """Test crawling specific sections from the navigation menu."""
    print("Initializing DocumentCrawler...")
    crawler = DocumentCrawler()
    
    # First, extract the menu structure
    print("First, extracting the navigation menu...")
    menu_request = CrawlRequest(
        url="https://cloud.google.com/vertex-ai/docs",
        detect_nav_menu=True
    )
    
    menu_result = await crawler.crawl_site(menu_request)
    
    # Now that we have the menu, let the user pick sections to crawl
    if menu_result.nav_menu:
        print("\nAvailable sections to crawl:")
        for i, section in enumerate(menu_result.nav_menu):
            print(f"{i+1}. {section.title} ({len(section.children)} items)")
        
        # For this test, we'll just pick a few specific sections
        # In a real application, you'd get this from user input
        sections_to_crawl = ["Discover", "Get started"]
        
        print(f"\nCrawling sections: {', '.join(sections_to_crawl)}")
        
        # Create a new request to crawl specific sections
        sections_request = CrawlRequest(
            url="https://cloud.google.com/vertex-ai/docs",
            max_pages=20,
            detect_nav_menu=True,
            sections_to_crawl=sections_to_crawl
        )
        
        # Crawl the selected sections
        result = await crawler.crawl_site(sections_request)
        
        # Print summary of results
        print("\n" + "="*80)
        print(f"CRAWL SUMMARY FOR SELECTED SECTIONS")
        print("="*80)
        print(f"Total pages crawled: {result.crawl_stats['total_pages']}")
        
        for i, page in enumerate(result.pages):
            print(f"\n{i+1}. {page.url}")
            if page.menu_section:
                print(f"   Section: {page.menu_section}")
            print(f"   Title: {page.title}")
            print(f"   Content size: {len(page.content):,} characters")
        
        return True
    else:
        print("No navigation menu found")
        return False

async def test_specific_section_crawling():
    """Test crawling specific sections from the navigation menu with detailed debugging."""
    print("DEBUG: Initializing DocumentCrawler for section-specific crawling...")
    crawler = DocumentCrawler()
    
    try:
        # First, extract the menu structure
        print("DEBUG: First, extracting the navigation menu...")
        menu_request = CrawlRequest(
            url="https://cloud.google.com/vertex-ai/docs",
            detect_nav_menu=True
        )
        
        menu_result = await crawler.crawl_site(menu_request)
        
        # Now that we have the menu, select specific sections to crawl
        if menu_result.nav_menu:
            print("\nDEBUG: Navigation menu extracted successfully")
            print(f"DEBUG: Found {len(menu_result.nav_menu)} sections in the menu")
            
            # For this test, we'll pick specific sections to crawl that match the actual menu structure
            sections_to_crawl = ["Get predictions from a custom model", "Train a custom model", "Model evaluation in Vertex AI"]
            print(f"\nDEBUG: Will attempt to crawl sections: {', '.join(sections_to_crawl)}")
            
            # Create a new request to crawl specific sections
            sections_request = CrawlRequest(
                url="https://cloud.google.com/vertex-ai/docs",
                max_depth=2,
                max_pages=15,  # Increased to capture more pages
                detect_nav_menu=True,
                sections_to_crawl=sections_to_crawl
            )
            
            # Crawl the selected sections
            print("DEBUG: Starting crawl of specific sections...")
            result = await crawler.crawl_site(sections_request)
            print("DEBUG: Section-specific crawl completed")
            
            # Print summary of results
            print("\n" + "="*80)
            print(f"CRAWL SUMMARY FOR SELECTED SECTIONS: {', '.join(sections_to_crawl)}")
            print("="*80)
            print(f"Total pages crawled: {result.crawl_stats['total_pages']}")
            print(f"Success rate: {result.crawl_stats['success_rate']:.2%}")
            
            # Calculate some statistics
            total_content_size = sum(len(page.content) for page in result.pages)
            total_links = sum(len(page.links) for page in result.pages)
            
            print(f"Total content size: {total_content_size:,} characters")
            print(f"Total links found: {total_links:,}")
            
            # Display information about each page
            print("\n" + "-"*80)
            print("PAGES CRAWLED IN SPECIFIC SECTIONS")
            print("-"*80)
            
            for i, page in enumerate(result.pages):
                print(f"\n{i+1}. {page.url}")
                
                # Extract path segments if any
                path = "/".join(page.path_segments) if page.path_segments else "/"
                print(f"   Path: {path}")
                
                # Display menu section if available
                if page.menu_section:
                    print(f"   Section: {page.menu_section}")
                
                print(f"   Title: {page.title}")
                print(f"   Content size: {len(page.content):,} characters")
            
            # Save the section crawl results to a JSON file
            results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
            os.makedirs(results_dir, exist_ok=True)
            
            section_results_file = os.path.join(results_dir, "section_crawl_results.json")
            with open(section_results_file, 'w') as f:
                # Convert the results to a serializable format
                json_results = {
                    "url": result.root_url,
                    "sections_crawled": sections_to_crawl,
                    "total_pages": result.crawl_stats['total_pages'],
                    "success_rate": result.crawl_stats['success_rate'],
                    "total_content_size": total_content_size,
                    "total_links": total_links,
                    "pages": []
                }
                
                for page in result.pages:
                    page_data = {
                        "url": page.url,
                        "path": "/".join(page.path_segments) if page.path_segments else "/",
                        "section": page.menu_section,
                        "title": page.title,
                        "content_size": len(page.content),
                        "links_count": len(page.links)
                    }
                    json_results["pages"].append(page_data)
                
                json.dump(json_results, f, indent=2)
            
            print(f"\nSection crawl results saved to: {section_results_file}")
            return True
        else:
            print("DEBUG ERROR: No navigation menu found")
            return False
    except Exception as e:
        print(f"DEBUG ERROR during section crawling test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running crawler test on Vertex AI docs...")
    nav_menu_success = asyncio.run(test_crawler())
    
    # Test specific section crawling
    print("\nTesting specific section crawling...")
    section_crawl_success = asyncio.run(test_specific_section_crawling())
    
    print(f"Section crawling test {'succeeded' if section_crawl_success else 'failed'}")
    sys.exit(0 if nav_menu_success and section_crawl_success else 1)
