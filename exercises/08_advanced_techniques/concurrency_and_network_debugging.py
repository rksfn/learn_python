"""
Exercise 2: Debugging Concurrency and Network Issues

In this exercise, you'll work with a web scraper application that has concurrency 
and network-related issues. You'll learn how to debug and fix problems related to 
multithreading, deadlocks, and API interactions.
"""

import os
import time
import json
import random
import queue
import threading
import logging
import requests
from typing import List, Dict, Any, Optional, Tuple, Set
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field


# BUG #1: Missing proper logging configuration
# No logging configuration is set up, leading to no log output


@dataclass
class WebPage:
    """Class representing a web page with its content and links."""
    url: str
    title: str = ""
    content: str = ""
    status_code: int = 0
    links: List[str] = field(default_factory=list)
    error: Optional[str] = None
    visited: bool = False


class WebScraper:
    """
    A multithreaded web scraper with concurrency and networking bugs to fix.
    """
    
    def __init__(self, base_url: str, max_threads: int = 5, timeout: int = 10):
        """Initialize the web scraper."""
        self.base_url = base_url
        self.max_threads = max_threads
        self.timeout = timeout
        
        # Storage for page data
        self.pages = {}  # url -> WebPage
        self.visited_urls = set()
        self.queued_urls = queue.Queue()
        
        # Locks and conditions
        self.page_lock = threading.Lock()
        self.stats_lock = threading.Lock()
        
        # Threading control
        self.active_threads = 0
        self.stop_event = threading.Event()
        
        # Network session
        self.session = requests.Session()
        
        # Stats
        self.stats = {
            "pages_visited": 0,
            "success_count": 0,
            "error_count": 0,
            "start_time": 0,
            "end_time": 0
        }
        
        print(f"WebScraper initialized with base URL: {base_url}")
    
    def start(self, entry_url: str = None, max_pages: int = 100) -> None:
        """
        Start the web scraper from the given entry URL.
        
        Args:
            entry_url: Starting URL (defaults to base_url if None)
            max_pages: Maximum number of pages to scrape
        """
        # Set up the entry URL
        if entry_url is None:
            entry_url = self.base_url
        
        # Reset state
        self.pages = {}
        self.visited_urls = set()
        self.queued_urls = queue.Queue()
        self.stop_event.clear()
        
        # Reset stats
        with self.stats_lock:
            self.stats = {
                "pages_visited": 0,
                "success_count": 0,
                "error_count": 0,
                "start_time": time.time(),
                "end_time": 0
            }
        
        # Add the entry URL to the queue
        self.queued_urls.put(entry_url)
        
        # Start the scraper threads
        # BUG #2: Concurrency issue with ThreadPoolExecutor
        # The way workers are managed can lead to thread starvation or deadlocks
        print(f"Starting scraping from {entry_url} with {self.max_threads} threads")
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            for _ in range(self.max_threads):
                executor.submit(self._worker, max_pages)
            
            # BUG #3: Improper wait mechanism
            # This doesn't properly wait for all work to complete
            while not self.queued_urls.empty() and len(self.visited_urls) < max_pages:
                time.sleep(0.1)
        
        # BUG #4: Incomplete cleanup
        # Resources might not be properly cleaned up
        with self.stats_lock:
            self.stats["end_time"] = time.time()
            duration = self.stats["end_time"] - self.stats["start_time"]
            print(f"Scraping completed: {self.stats['pages_visited']} pages in {duration:.2f} seconds")
            print(f"Success: {self.stats['success_count']}, Errors: {self.stats['error_count']}")
    
    def _worker(self, max_pages: int) -> None:
        """
        Worker function that processes URLs from the queue.
        
        Args:
            max_pages: Maximum number of pages to scrape
        """
        # BUG #5: Race condition on thread count
        # Not thread-safe increment/decrement
        self.active_threads += 1
        
        try:
            while not self.stop_event.is_set():
                try:
                    # BUG #6: Potential deadlock in queue handling
                    # If an exception occurs after getting a URL but before marking it visited,
                    # the URL might never be processed
                    url = self.queued_urls.get(timeout=1)
                    
                    # Check if we've reached the max pages
                    with self.stats_lock:
                        if self.stats["pages_visited"] >= max_pages:
                            self.queued_urls.task_done()
                            self.stop_event.set()
                            break
                    
                    # BUG #7: Race condition on visited URLs
                    # Not properly synchronized access to visited_urls
                    if url in self.visited_urls:
                        self.queued_urls.task_done()
                        continue
                    
                    # Mark as visited
                    self.visited_urls.add(url)
                    
                    # Fetch the page
                    page = self._fetch_page(url)
                    
                    # Process the page
                    if page.status_code == 200:
                        links = self._extract_links(page)
                        
                        # BUG #8: Duplicate work
                        # Not checking if URLs are already in the queue
                        for link in links:
                            if link not in self.visited_urls:
                                self.queued_urls.put(link)
                        
                        # Update stats
                        with self.stats_lock:
                            self.stats["success_count"] += 1
                    else:
                        # Update stats
                        with self.stats_lock:
                            self.stats["error_count"] += 1
                    
                    # Store the page data
                    with self.page_lock:
                        self.pages[url] = page
                        page.visited = True
                    
                    # Update visit count
                    with self.stats_lock:
                        self.stats["pages_visited"] += 1
                    
                    # Signal that we're done with this URL
                    self.queued_urls.task_done()
                    
                    # Simulate rate limiting
                    time.sleep(random.uniform(0.1, 0.5))
                    
                except queue.Empty:
                    # Queue is empty, check if we should stop
                    if self.queued_urls.empty() and self.active_threads == 1:
                        self.stop_event.set()
                    continue
                
                except Exception as e:
                    print(f"Error in worker: {str(e)}")
                    self.queued_urls.task_done()
        finally:
            # BUG #9: Race condition on thread count
            # Not thread-safe decrement
            self.active_threads -= 1
    
    def _fetch_page(self, url: str) -> WebPage:
        """
        Fetch a web page and return its content.
        
        Args:
            url: URL to fetch
            
        Returns:
            WebPage object with the page content
        """
        page = WebPage(url=url)
        
        try:
            # BUG #10: Network error handling
            # Not properly handling network errors or timeouts
            response = self.session.get(url, timeout=self.timeout)
            page.status_code = response.status_code
            
            if response.status_code == 200:
                page.content = response.text
                # Extract title (very basic implementation)
                title_start = page.content.find("<title>")
                title_end = page.content.find("</title>")
                if title_start != -1 and title_end != -1:
                    page.title = page.content[title_start + 7:title_end].strip()
                else:
                    page.title = url
            else:
                page.error = f"HTTP Error: {response.status_code}"
                
        except requests.Timeout:
            page.error = "Timeout"
            page.status_code = 0
            
        except requests.RequestException as e:
            page.error = f"Request Error: {str(e)}"
            page.status_code = 0
            
        except Exception as e:
            page.error = f"Error: {str(e)}"
            page.status_code = 0
        
        return page
    
    def _extract_links(self, page: WebPage) -> List[str]:
        """
        Extract links from a web page.
        
        Args:
            page: WebPage object
            
        Returns:
            List of absolute URLs
        """
        links = []
        
        # Very basic link extraction for demonstration purposes
        # In a real implementation, you would use a proper HTML parser
        content = page.content.lower()
        position = 0
        
        # BUG #11: Inefficient and brittle link extraction
        # This approach to parsing HTML is error-prone and inefficient
        while True:
            # Find the next href attribute
            href_pos = content.find('href="', position)
            if href_pos == -1:
                break
            
            # Find the closing quote
            start_pos = href_pos + 6  # Length of 'href="'
            end_pos = content.find('"', start_pos)
            if end_pos == -1:
                break
            
            # Extract the link
            link = content[start_pos:end_pos]
            
            # Make it an absolute URL if it's relative
            if not link.startswith(('http://', 'https://')):
                link = urljoin(page.url, link)
            
            # Only add links that are under our base URL
            if link.startswith(self.base_url):
                links.append(link)
            
            # Move position forward
            position = end_pos + 1
        
        return links
    
    def save_results(self, filename: str) -> None:
        """
        Save the scraping results to a file.
        
        Args:
            filename: Name of the file to save to
        """
        # BUG #12: Not thread-safe
        # Should acquire lock before accessing self.pages
        
        # Convert page objects to dictionaries
        results = []
        for url, page in self.pages.items():
            results.append({
                "url": url,
                "title": page.title,
                "status_code": page.status_code,
                "error": page.error,
                "links_count": len(page.links)
            })
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Saved {len(results)} page results to {filename}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current scraping statistics."""
        # BUG #13: Not thread-safe
        # Should acquire lock before accessing self.stats
        stats_copy = dict(self.stats)
        if stats_copy["end_time"] == 0 and stats_copy["start_time"] > 0:
            stats_copy["duration"] = time.time() - stats_copy["start_time"]
        else:
            stats_copy["duration"] = stats_copy["end_time"] - stats_copy["start_time"]
        
        return stats_copy


class MockWebServer:
    """
    A mock web server for testing the scraper without making real HTTP requests.
    This allows for reproducible testing of concurrency issues.
    """
    
    def __init__(self, base_url: str = "http://example.com", latency: float = 0.1):
        """Initialize the mock web server."""
        self.base_url = base_url
        self.latency = latency
        self.pages = {}
        self.original_get = requests.Session.get
        
        print(f"MockWebServer initialized with base URL: {base_url}")
    
    def add_page(self, path: str, title: str, content: str = "", links: List[str] = None) -> None:
        """
        Add a mock page to the server.
        
        Args:
            path: URL path (will be joined with base_url)
            title: Page title
            content: Page content
            links: List of links on the page (paths only, will be made absolute)
        """
        url = urljoin(self.base_url, path)
        
        # Create content with title
        full_content = f"<html><head><title>{title}</title></head><body>\n"
        
        # Add content
        full_content += content + "\n"
        
        # Add links
        if links:
            for link in links:
                abs_link = urljoin(self.base_url, link)
                full_content += f'<a href="{abs_link}">Link to {link}</a>\n'
        
        full_content += "</body></html>"
        
        # Store the page
        self.pages[url] = {
            "title": title,
            "content": full_content,
            "status_code": 200
        }
    
    def add_error_page(self, path: str, status_code: int = 404) -> None:
        """
        Add a mock error page to the server.
        
        Args:
            path: URL path (will be joined with base_url)
            status_code: HTTP status code to return
        """
        url = urljoin(self.base_url, path)
        
        # Store the error page
        self.pages[url] = {
            "title": f"Error {status_code}",
            "content": f"<html><head><title>Error {status_code}</title></head><body>\nError {status_code}\n</body></html>",
            "status_code": status_code
        }
    
    def start(self) -> None:
        """Start the mock server by monkey patching requests.Session.get."""
        
        def mock_get(session_self, url, **kwargs):
            # Simulate network latency
            time.sleep(self.latency)
            
            # Check if we have this URL
            if url in self.pages:
                page = self.pages[url]
                
                # Create a mock response
                response = requests.Response()
                response.status_code = page["status_code"]
                response._content = page["content"].encode('utf-8')
                response.url = url
                
                return response
            else:
                # Return a 404 for unknown URLs
                response = requests.Response()
                response.status_code = 404
                response._content = "<html><head><title>Not Found</title></head><body>\nPage not found\n</body></html>".encode('utf-8')
                response.url = url
                
                return response
        
        # Replace the real get method with our mock
        requests.Session.get = mock_get
    
    def stop(self) -> None:
        """Stop the mock server by restoring the original requests.Session.get."""
        requests.Session.get = self.original_get


def setup_mock_website():
    """Set up a mock website for testing the scraper."""
    server = MockWebServer()
    
    # Add pages with links to each other to simulate a website
    server.add_page("/", "Home Page", "Welcome to the example website.",
                  ["/about", "/products", "/contact"])
    
    server.add_page("/about", "About Us", "This is the about page.",
                  ["/", "/team", "/products"])
    
    server.add_page("/products", "Our Products", "Check out our products.",
                  ["/", "/about", "/product/1", "/product/2", "/product/3"])
    
    server.add_page("/contact", "Contact Us", "Get in touch with us.",
                  ["/", "/about"])
    
    server.add_page("/team", "Our Team", "Meet our team members.",
                  ["/", "/about"])
    
    # Add some product pages
    for i in range(1, 6):
        server.add_page(f"/product/{i}", f"Product {i}", f"Details for product {i}.",
                      ["/", "/products", f"/product/{i}/specs"])
        
        server.add_page(f"/product/{i}/specs", f"Product {i} Specifications",
                      f"Technical specifications for product {i}.",
                      ["/", "/products", f"/product/{i}"])
    
    # Add some error pages
    server.add_error_page("/broken-link", 404)
    server.add_error_page("/server-error", 500)
    
    # Start the mock server
    server.start()
    
    return server


def demo_web_scraper():
    """Run a demonstration of the WebScraper class with the mock server."""
    # Set up the mock website
    server = setup_mock_website()
    
    try:
        # Create and start the scraper
        scraper = WebScraper(base_url="http://example.com")
        scraper.start(max_pages=20)
        
        # Save the results
        scraper.save_results("data/scraping_results.json")
        
        # Print some stats
        stats = scraper.get_stats()
        print(f"Scraping stats: {stats}")
        
    finally:
        # Stop the mock server
        server.stop()


if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Run the demonstration
    demo_web_scraper()


"""
Exercise Instructions:

In this exercise, you'll debug and fix concurrency and network-related issues in a 
web scraper application. The scraper uses multithreading to fetch and process web pages 
in parallel, but it has several bugs that can lead to deadlocks, race conditions, and 
other concurrency problems.

Part 1: Implement Proper Logging
-------------------------------
1. Set up a proper logging configuration with appropriate levels and formatting
2. Replace all print statements with logging calls at the appropriate level
3. Add thread identification to log messages
4. Implement a logging context manager to temporarily change log levels for debugging

Part 2: Fix Concurrency Issues
-----------------------------
1. Fix the race conditions in thread counting and URL tracking
2. Resolve the potential deadlock in the queue handling
3. Implement proper synchronization for shared resources (visited_urls, pages, stats)
4. Fix the thread waiting mechanism to properly wait for all work to complete
5. Ensure proper cleanup of resources

Part 3: Improve Network Error Handling
-------------------------------------
1. Implement proper error handling for network requests
2. Add retry logic for failed requests
3. Implement proper timeouts and connection pooling
4. Use a proper HTML parser for link extraction instead of string manipulation

Part 4: Add Debugging Tools
--------------------------
1. Implement a thread monitor that logs the state of all threads periodically
2. Add a network traffic logger to record all requests and responses
3. Create a performance tracking system to identify slow operations
4. Implement proper status reporting for the scraper

Bonus Challenges:
---------------
1. Add a deadlock detection system
2. Implement a pause/resume mechanism for the scraper
3. Add a rate limiting system to avoid overloading servers
4. Create a visualization of the scraping process (which pages link to which)

Notes:
-----
- The exercise uses a mock web server to simulate network requests
- Each bug is marked with a comment (BUG #1, BUG #2, etc.) in the code
- Focus on thread safety, proper synchronization, and defensive programming
- Consider both correctness (fixing bugs) and performance implications
"""
