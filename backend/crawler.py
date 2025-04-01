import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from typing import Dict, Set, List

class AsyncWebCrawler:
    """
    Asynchronous web crawler that crawls pages within a single domain.
    """
    def __init__(self, start_url: str, max_depth: int = 3, rate_limit: float = 1.0, update_callback=None):
        """
        Initialize the crawler.

        :param start_url: Starting URL for crawling.
        :param max_depth: Maximum depth for recursive crawling.
        :param rate_limit: Delay (in seconds) between consecutive requests.
        :param update_callback: Callback function to send live updates.
        """
        self.start_url = start_url
        self.max_depth = max_depth
        self.rate_limit = rate_limit
        self.base_domain = urlparse(start_url).netloc
        self.visited: Set[str] = set()
        self.results: Dict[str, List[str]] = {}  # Mapping of URL -> list of found URLs
        self.update_callback = update_callback

        # Configure logging
        self.logger = logging.getLogger("AsyncWebCrawler")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> str:
        """
        Asynchronously fetch page content.

        :param session: aiohttp ClientSession for making requests.
        :param url: URL to fetch.
        :return: HTML content as a string or an empty string if an error occurs.
        """
        try:
            async with session.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.warning(f"Non-200 status code for {url}: {response.status}")
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
        return ""

    def extract_links(self, html: str, current_url: str) -> List[str]:
        """
        Extract all links from HTML content, filtering to stay within the same domain.

        :param html: HTML content as a string.
        :param current_url: URL of the current page (used to resolve relative URLs).
        :return: List of absolute URLs on the same domain.
        """
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        for a_tag in soup.find_all("a", href=True):
            link = urljoin(current_url, a_tag["href"])
            parsed_link = urlparse(link)
            if parsed_link.netloc == self.base_domain:  # Keep only links within the same domain
                links.add(link)
        return list(links)

    async def crawl_url(self, session: aiohttp.ClientSession, url: str, depth: int):
        """
        Crawl a single URL and schedule further crawling for links found on the page.

        :param session: aiohttp ClientSession for making requests.
        :param url: URL to crawl.
        :param depth: Current depth of recursion.
        """
        if url in self.visited or depth > self.max_depth:
            return

        self.visited.add(url)
        self.logger.info(f"Crawling: {url} (Depth: {depth})")

        html = await self.fetch_page(session, url)
        if not html:
            return

        # Extract links and store results for this page.
        links = self.extract_links(html, url)
        self.results[url] = links

        # Send live update if callback is provided
        if self.update_callback:
            await self.update_callback(url, links)

        # Rate limiting to avoid overwhelming the server.
        await asyncio.sleep(self.rate_limit)

        # Schedule crawling for each new link concurrently.
        tasks = []
        for link in links:
            if link not in self.visited:
                tasks.append(self.crawl_url(session, link, depth + 1))
        if tasks:
            await asyncio.gather(*tasks)

    async def crawl(self):
        """
        Start crawling from the initial URL.
        """
        connector = aiohttp.TCPConnector(limit=10)  # Adjust the limit as needed
        async with aiohttp.ClientSession(connector=connector) as session:
            await self.crawl_url(session, self.start_url, 0)

    def get_results(self) -> Dict[str, List[str]]:
        """
        Get the crawling results.

        :return: Dictionary containing URLs and their extracted links.
        """
        return self.results


async def crawl_website(url: str, max_depth: int = 3) -> Dict[str, List[str]]:
    """
    FastAPI-compatible function to crawl a website asynchronously.

    :param url: The starting URL to crawl.
    :param max_depth: The depth limit for crawling.
    :return: Dictionary containing crawled URLs and their extracted links.
    """
    crawler = AsyncWebCrawler(url, max_depth)
    await crawler.crawl()
    return crawler.get_results()
