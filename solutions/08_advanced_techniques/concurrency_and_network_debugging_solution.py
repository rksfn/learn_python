"""
Solution: Debugging Concurrency and Network Issues

This solution demonstrates how to debug and fix concurrency and network-related issues
in a web scraper application, including race conditions, deadlocks, and HTTP interaction problems.
"""

import os
import time
import json
import random
import queue
import threading
import logging
import requests
import traceback
from typing import List, Dict, Any, Optional, Tuple, Set
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from contextlib import contextmanager
from functools import wraps
from bs4 import BeautifulSoup


# FIX #1: Implemented proper logging configuration
# Configure logging with thread information and appropriate levels
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s',
    handlers=[
        logging.FileHandler('web_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('web_scraper')


# Context manager for temporary debug logging
@contextmanager
def debug_logging(logger_name=None):
    """
    Temporarily increase logging level to DEBUG for the specified logger.
    
    Args:
        logger_name: Name of the logger to modify (uses root logger if None)
    """
    selected_logger = logging.getLogger(logger_name) if logger_name else logger
    original_level = selected_logger.level
    selected_logger.setLevel(logging.DEBUG)
    logger.debug(f"Temporarily increased logging level to DEBUG for {logger_name or 'root'}")
    
    try:
        yield selected_logger
    finally:
        selected_logger.setLevel(original_level)
        logger.debug(f"Restored logging level for {logger_name or 'root'} to {logging.getLevelName(original_level)}")


# Decorator to log HTTP requests
def log_http_request(func):
    """
    Decorator to log HTTP requests and responses.
    
    Args:
        func: The function to wrap (should be a method that makes HTTP requests)
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        url = args[0] if args else kwargs.get('url')
        logger.debug(f"HTTP Request: {func.__name__} {url}")
        
        start_time = time.time()
        try:
            response = func(self, *args, **kwargs)
            elapsed = time.time() - start_time
            
            # Log the response details
            logger.debug(
                f"HTTP Response: {response.status_code} from {url} "
                f"({len(response.content)} bytes in {elapsed:.2f}s)"
            )
            return response
        except Exception as e:
            elapsed = time.time() - start_time
            logger.exception(f"HTTP Error after {elapsed:.2f}s: {str(e)}")
            raise
    
    return wrapper


# Thread monitoring class
class ThreadMonitor:
    """
    A class to monitor thread activity and detect potential deadlocks.
    """
    
    def __init__(self, check_interval=5):
        """
        Initialize the thread monitor.
        
        Args:
            check_interval: How often to check thread status (in seconds)
        """
        self.check_interval = check_interval
        self.running = False
        self.monitor_thread = None
        logger.info(f"ThreadMonitor initialized with check_interval={check_interval}s")
    
    def start(self):
        """Start the thread monitor."""
        if self.running:
            logger.warning("ThreadMonitor already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="ThreadMonitor",
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("ThreadMonitor started")
    
    def stop(self):
        """Stop the thread monitor."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=self.check_interval + 1)
            logger.info("ThreadMonitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop that checks thread status periodically."""
        while self.running:
            self._check_threads()
            time.sleep(self.check_interval)
    
    def _check_threads(self):
        """Check the status of all threads and log information."""
        threads = threading.enumerate()
        active_count = len(threads)
        
        logger.debug(f"Thread status: {active_count} active threads")
        
        for thread in threads:
            # Skip the monitor thread itself
            if thread is self.monitor_thread:
                continue
            
            # Log thread information
            logger.debug(f"Thread: {thread.name}, alive: {thread.is_alive()}, daemon: {thread.daemon}")
            
            # Try to get a stack trace for the thread (if supported by the system)
            try:
                frame = sys._current_frames().get(thread.ident)
                if frame:
                    stack = traceback.format_stack(frame)
                    logger.debug(f"Thread {thread.name} stack trace:\n{''.join(stack)}")
            except:
                pass


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
    A multithreaded web scraper with concurrency and networking bugs fixed.
    """
    
    def __init__(self, base_url: str, max_threads: int = 5, timeout: int = 10, max_retries: int = 3):
        """Initialize the web scraper."""
        self.base_url = base_url
        self.max_threads = max_threads
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Storage for page data
        self.pages = {}  # url -> WebPage
        self.visited_urls = set()  # Track visited URLs
        self.queued_urls = queue.Queue()  # Queue of URLs to visit
        self.queue_set = set()  # Track URLs in the queue for quick membership tests
        
        # Locks for thread-safe access to shared resources
        self.page_lock = threading.Lock()
        self.visited_lock = threading.Lock()
        self.queue_lock = threading.Lock()
        self.stats_lock = threading.Lock()
        
        # Threading control
        self.active_threads = 0
        self.thread_count_lock = threading.Lock()  # Protect thread counter
        self.stop_event = threading.Event()
        self.all_done_event = threading.Event()
        
        # Network session
        self.session = requests.Session()
        # Set up connection pooling for better performance
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=max_threads,
            pool_maxsize=max_threads,
            max_retries=max_retries
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Stats
        self.stats = {
            "pages_visited": 0,
            "success_count": 0,
            "error_count": 0,
            "start_time": 0,
            "end_time": 0
        }
        
        # Thread monitor
        self.thread_monitor = ThreadMonitor()
        
        logger.info(f"WebScraper initialized with base URL: {base_url}")
    
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
        self.queue_set = set()
        self.stop_event.clear()
        self.all_done_event.clear()
        
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
        self._add_to_queue(entry_url)
        
        # Start the thread monitor
        self.thread_monitor.start()
        
        # FIX #2: Fixed concurrency issue with ThreadPoolExecutor
        # Use a better approach for worker threads and task coordination
        logger.info(f"Starting scraping from {entry_url} with {self.max_threads} threads")
        
        # Create and start worker threads
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            
            # Submit work to the executor
            for i in range(self.max_threads):
                futures.append(executor.submit(self._worker, max_pages))
            
            # FIX #3: Improved wait mechanism
            # Wait for all work to complete by using the all_done_event
            # This ensures we don't exit prematurely and that all tasks get processed
            logger.debug("Waiting for scraping to complete")
            self.all_done_event.wait()
            
            # Set stop event to signal all threads to exit
            self.stop_event.set()
            
            # Wait for all futures to complete
            for future in futures:
                future.result()  # This will re-raise any exceptions from the workers
        
        # FIX #4: Proper cleanup
        # Complete cleanup of resources
        self.thread_monitor.stop()
        
        with self.stats_lock:
            self.stats["end_time"] = time.time()
            duration = self.stats["end_time"] - self.stats["start_time"]
            logger.info(f"Scraping completed: {self.stats['pages_visited']} pages in {duration:.2f} seconds")
            logger.info(f"Success: {self.stats['success_count']}, Errors: {self.stats['error_count']}")
    
    def _worker(self, max_pages: int) -> None:
        """
        Worker function that processes URLs from the queue.
        
        Args:
            max_pages: Maximum number of pages to scrape
        """
        # FIX #5: Fixed race condition on thread count
        # Thread-safe increment
        with self.thread_count_lock:
            self.active_threads += 1
            current_active = self.active_threads
        
        thread_name = threading.current_thread().name
        logger.debug(f"Worker {thread_name} started (active threads: {current_active})")
        
        try:
            while not self.stop_event.is_set():
                url = None
                try:
                    # FIX #6: Fixed potential deadlock in queue handling
                    # Using a clean approach with appropriate exception handling
                    try:
                        # Use a timeout to periodically check the stop event
                        url = self.queued_urls.get(timeout=1)
                    except queue.Empty:
                        # If queue is empty, check if we're done
                        self._check_if_done(max_pages)
                        continue
                    
                    # Check if we've reached the max pages
                    with self.stats_lock:
                        if self.stats["pages_visited"] >= max_pages:
                            # Mark the URL as processed but don't process it
                            self.queued_urls.task_done()
                            
                            # Signal that we're done
                            self.stop_event.set()
                            self.all_done_event.set()
                            
                            logger.debug(f"Worker {thread_name} stopping - reached max pages")
                            break
                    
                    # FIX #7: Fixed race condition on visited URLs
                    # Using proper synchronization for visited_urls access
                    should_process = False
                    with self.visited_lock:
                        if url not in self.visited_urls:
                            # Mark as visited
                            self.visited_urls.add(url)
                            should_process = True
                    
                    if not should_process:
                        logger.debug(f"URL already visited, skipping: {url}")
                        self.queued_urls.task_done()
                        continue
                    
                    # Fetch the page
                    page = self._fetch_page(url)
                    
                    # Process the page
                    if page.status_code == 200:
                        links = self._extract_links(page)
                        
                        # FIX #8: Fixed duplicate work
                        # Now checking if URLs are already in the queue
                        for link in links:
                            self._add_to_queue(link)
                        
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
                        pages_visited = self.stats["pages_visited"]
                    
                    logger.debug(f"Processed page {pages_visited}: {url} (status: {page.status_code})")
                    
                    # Signal that we're done with this URL
                    self.queued_urls.task_done()
                    
                    # Rate limiting to avoid overloading servers
                    time.sleep(random.uniform(0.1, 0.3))
                    
                    # Check if we're done with all the pages
                    self._check_if_done(max_pages)
                
                except Exception as e:
                    logger.exception(f"Error processing URL {url}: {str(e)}")
                    
                    # Make sure we mark the task as done even if an error occurs
                    if url:
                        try:
                            self.queued_urls.task_done()
                        except:
                            pass
        
        finally:
            # FIX #9: Fixed race condition on thread count
            # Thread-safe decrement
            with self.thread_count_lock:
                self.active_threads -= 1
                current_active = self.active_threads
            
            logger.debug(f"Worker {thread_name} stopped (active threads: {current_active})")
            
            # If this is the last worker and the queue is empty, signal all_done_event
            if current_active == 0:
                self.all_done_event.set()
    
    def _check_if_done(self, max_pages: int) -> None:
        """
        Check if the scraping process is complete.
        
        Args:
            max_pages: Maximum number of pages to scrape
        """
        # Check if we've reached the max pages
        with self.stats_lock:
            if self.stats["pages_visited"] >= max_pages:
                self.stop_event.set()
                self.all_done_event.set()
                return
        
        # Check if the queue is empty and all threads are idle
        if self.queued_urls.empty():
            with self.thread_count_lock:
                if self.active_threads == 1:  # Only this thread is running
                    logger.debug("All URLs processed and no active workers - scraping complete")
                    self.all_done_event.set()
    
    def _add_to_queue(self, url: str) -> None:
        """
        Add a URL to the queue if it hasn't been visited or queued already.
        
        Args:
            url: URL to add to the queue
        """
        # Check if the URL has already been visited or queued
        should_queue = False
        
        with self.queue_lock:
            if url not in self.queue_set and url not in self.visited_urls:
                self.queue_set.add(url)
                should_queue = True
        
        if should_queue:
            self.queued_urls.put(url)
            logger.debug(f"Added to queue: {url}")
    
    @log_http_request
    def _fetch_page(self, url: str) -> WebPage:
        """
        Fetch a web page and return its content.
        
        Args:
            url: URL to fetch
            
        Returns:
            WebPage object with the page content
        """
        page = WebPage(url=url)
        
        # FIX #10: Improved network error handling
        # Added proper retry logic and comprehensive error handling
        retries = 0
        while retries <= self.max_retries:
            try:
                # Use the session for connection pooling and automatic retries
                response = self.session.get(url, timeout=self.timeout)
                page.status_code = response.status_code
                
                if response.status_code == 200:
                    page.content = response.text
                    
                    # Use BeautifulSoup to parse HTML and extract title
                    soup = BeautifulSoup(page.content, 'html.parser')
                    title_tag = soup.find('title')
                    if title_tag:
                        page.title = title_tag.string.strip()
                    else:
                        page.title = url
                    
                    return page
                elif response.status_code == 429:  # Too Many Requests
                    # Back off and retry
                    retry_after = int(response.headers.get('Retry-After', 5))
                    logger.warning(f"Rate limited ({url}). Waiting {retry_after}s before retry.")
                    time.sleep(retry_after)
                    retries += 1
                    continue
                elif 500 <= response.status_code < 600:  # Server error
                    # Retry server errors
                    logger.warning(f"Server error {response.status_code} for {url}. Retrying...")
                    retries += 1
                    time.sleep(1 * (2 ** retries))  # Exponential backoff
                    continue
                else:
                    page.error = f"HTTP Error: {response.status_code}"
                    return page
                    
            except requests.Timeout:
                logger.warning(f"Timeout for {url}. Retry {retries + 1}/{self.max_retries}")
                page.error = "Timeout"
                page.status_code = 0
                retries += 1
                if retries <= self.max_retries:
                    # Exponential backoff
                    time.sleep(1 * (2 ** retries))
                    continue
                else:
                    return page
                
            except requests.RequestException as e:
                logger.warning(f"Request error for {url}: {str(e)}. Retry {retries + 1}/{self.max_retries}")
                page.error = f"Request Error: {str(e)}"
                page.status_code = 0
                retries += 1
                if retries <= self.max_retries:
                    # Exponential backoff
                    time.sleep(1 * (2 ** retries))
                    continue
                else:
                    return page
                
            except Exception as e:
                page.error = f"Error: {str(e)}"
                page.status_code = 0
                return page
        
        return page
    
    def _extract_links(self, page: WebPage) -> List[str]:
        """
        Extract links from a web page using BeautifulSoup.
        
        Args:
            page: WebPage object
            
        Returns:
            List of absolute URLs
        """
        links = []
        
        # FIX #11: Better link extraction using BeautifulSoup
        try:
            soup = BeautifulSoup(page.content, 'html.parser')
            
            # Find all <a> tags with href attributes
            for a_tag in soup.find_all('a', href=True):
                link = a_tag['href']
                
                # Make it an absolute URL if it's relative
                if not link.startswith(('http://', 'https://')):
                    link = urljoin(page.url, link)
                
                # Only add links that are under our base URL
                if link.startswith(self.base_url):
                    links.append(link)
            
            # Store links in the page object
            page.links = links
            
            logger.debug(f"Extracted {len(links)} links from {page.url}")
            return links
            
        except Exception as e:
            logger.exception(f"Error extracting links from {page.url}: {str(e)}")
            return []
    
    def save_results(self, filename: str) -> None:
        """
        Save the scraping results to a file.
        
        Args:
            filename: Name of the file to save to
        """
        # FIX #12: Thread-safe file saving
        # Using lock to safely access self.pages
        
        # Get a thread-safe copy of the pages
        pages_copy = {}
        with self.page_lock:
            for url, page in self.pages.items():
                pages_copy[url] = page
        
        # Convert page objects to dictionaries
        results = []
        for url, page in pages_copy.items():
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
        
        logger.info(f"Saved {len(results)} page results to {filename}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current scraping statistics."""
        # FIX #13: Thread-safe stats access
        # Using lock to safely access and copy stats
        with self.stats_lock:
            stats_copy = dict(self.stats)
            
            # Calculate duration
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
        
        logger.info(f"MockWebServer initialized with base URL: {base_url}")
    
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
        
        logger.debug(f"Added mock page: {url} with {len(links or [])} links")
    
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
        
        logger.debug(f"Added error page: {url} with status code {status_code}")
    
    def start(self) -> None:
        """Start the mock server by monkey patching requests.Session.get."""
        
        def mock_get(session_self, url, **kwargs):
            logger.debug(f"Mock server received request for: {url}")
            
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
                
                logger.debug(f"Mock server returning {response.status_code} for {url}")
                return response
            else:
                # Return a 404 for unknown URLs
                response = requests.Response()
                response.status_code = 404
                response._content = "<html><head><title>Not Found</title></head><body>\nPage not found\n</body></html>".encode('utf-8')
                response.url = url
                
                logger.debug(f"Mock server returning 404 for unknown URL: {url}")
                return response
        
        # Replace the real get method with our mock
        requests.Session.get = mock_get
        logger.info("Mock server started")
    
    def stop(self) -> None:
        """Stop the mock server by restoring the original requests.Session.get."""
        requests.Session.get = self.original_get
        logger.info("Mock server stopped")


def setup_mock_website():
    """Set up a mock website for testing the scraper."""
    logger.info("Setting up mock website")
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
    logger.info("Starting WebScraper demonstration")
    
    # Set up the mock website
    server = setup_mock_website()
    
    try:
        # Use debug logging for the demonstration
        with debug_logging():
            # Create and start the scraper
            scraper = WebScraper(base_url="http://example.com")
            scraper.start(max_pages=20)
            
            # Save the results
            scraper.save_results("data/scraping_results.json")
            
            # Print some stats
            stats = scraper.get_stats()
            logger.info(f"Scraping stats: {stats}")
    
    finally:
        # Stop the mock server
        server.stop()
    
    logger.info("WebScraper demonstration completed")


if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Run the demonstration
    try:
        demo_web_scraper()
    except Exception as e:
        logger.exception("Error in web scraper demo")


"""
Solution Explanation:

This solution addresses all the concurrency and network issues in the web scraper,
while adding robust logging and monitoring capabilities:

1. Implemented Comprehensive Logging:
   - Configured logging with proper levels, formatting, and thread information
   - Created a debug_logging context manager for temporary debugging
   - Added an HTTP request logging decorator to track network interactions
   - Replaced all print statements with appropriate logging calls

2. Fixed Concurrency Issues:
   - Protected shared resources with appropriate locks
   - Ensured thread-safe access to counters, collections, and stats
   - Fixed race conditions in thread counting and URL tracking
   - Implemented proper termination and cleanup with events
   - Added deadlock prevention with timeout-based queue operations

3. Improved Network Handling:
   - Added proper connection pooling for better performance
   - Implemented comprehensive error handling with retries and backoff
   - Used BeautifulSoup for robust HTML parsing instead of string manipulation
   - Added rate limiting to avoid overloading servers

4. Added Debugging Tools:
   - Created a ThreadMonitor class to track thread activity and detect issues
   - Added detailed logging for network requests and responses
   - Implemented proper state tracking throughout the application
   - Used events for clean coordination between threads

Specific Bug Fixes:

1. Bug #1: Implemented proper logging configuration with thread information
2. Bug #2: Fixed concurrency issues with ThreadPoolExecutor
3. Bug #3: Improved wait mechanism with synchronization events
4. Bug #4: Added proper resource cleanup
5. Bug #5: Fixed race condition on thread count with thread_count_lock
6. Bug #6: Fixed potential deadlock in queue handling with timeouts and better error handling
7. Bug #7: Fixed race condition on visited URLs with proper synchronization
8. Bug #8: Prevented duplicate work by tracking queued URLs
9. Bug #9: Fixed race condition on thread count with proper locking
10. Bug #10: Improved network error handling with retries and comprehensive error handling
11. Bug #11: Implemented proper HTML parsing with BeautifulSoup
12. Bug #12: Made file saving thread-safe with proper locking
13. Bug #13: Protected stats access with appropriate locking

Additional Improvements:

1. Added a ThreadMonitor class to observe thread behavior
2. Implemented proper HTTP request/response logging
3. Added connection pooling for better performance
4. Used events for clean thread coordination
5. Added exponential backoff for retries
6. Improved error handling throughout the code
7. Added rate limiting to avoid overloading servers
8. Used BeautifulSoup for reliable HTML parsing
"""
