import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

class WebCrawler:
    """
    A web crawler that systematically browses and indexes web pages within a specified domain.
    Implements breadth-first search traversal with depth limiting.
    """
    
    def __init__(self, start_url: str, max_depth: int = 3):
        """
        Initialize the web crawler with a starting URL and maximum crawl depth.
        
        Args:
            start_url (str): The initial URL to begin crawling from
            max_depth (int): Maximum depth of pages to crawl (default: 3)
        """
        self.start_url = start_url
        self.base_domain = urlparse(start_url).netloc  # Extract domain (e.g., 'example.com')
        self.visited = set()  # Track visited URLs to avoid cycles
        self.queue = deque([(start_url, 0)])  # Queue of (URL, depth) pairs for BFS
        self.max_depth = max_depth

    def fetch_page(self, url: str) -> str | None:
        """
        Fetch the HTML content of a given URL using requests.
        
        Args:
            url (str): The URL to fetch
            
        Returns:
            str | None: HTML content of the page if successful, None otherwise
        """
        try:
            # Add User-Agent header to avoid being blocked by some servers
            response = requests.get(
                url, 
                timeout=5,  # Timeout after 5 seconds
                headers={"User-Agent": "Mozilla/5.0"}
            )
            if response.status_code == 200:
                return response.text
        except requests.RequestException:
            # Handle any requests-related exceptions (timeout, connection error, etc.)
            pass
        return None

    def extract_links(self, html: str, current_url: str) -> set:
        """
        Extract all valid links from a page's HTML content.
        
        Args:
            html (str): HTML content to parse
            current_url (str): URL of the current page (for resolving relative URLs)
            
        Returns:
            set: Set of absolute URLs found on the page that belong to the same domain
        """
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        
        # Find all <a> tags with href attributes
        for a_tag in soup.find_all("a", href=True):
            # Convert relative URLs (like '/about') to absolute URLs
            link = urljoin(current_url, a_tag["href"])
            parsed_link = urlparse(link)
            
            # Only include links from the same domain
            if parsed_link.netloc == self.base_domain:
                links.add(link)
                
        return links

    def crawl(self):
        """
        Main crawling method that implements breadth-first traversal of web pages.
        Prints progress information as it crawls.
        """
        while self.queue:
            url, depth = self.queue.popleft()
            
            # Skip if we've seen this URL or exceeded max depth
            if url in self.visited or depth > self.max_depth:
                continue

            print(f"Visiting: {url} (Depth: {depth})")
            self.visited.add(url)
            
            # Fetch and process the page
            html = self.fetch_page(url)
            if html:
                links = self.extract_links(html, url)
                print(f"Found {len(links)} links on {url}")
                
                # Add new links to the queue
                for link in links:
                    if link not in self.visited:
                        self.queue.append((link, depth + 1))

if __name__ == "__main__":
    # Example usage
    start_url = "https://example.com"  # Replace with the actual start URL
    crawler = WebCrawler(start_url)
    crawler.crawl()
