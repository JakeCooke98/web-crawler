import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import json
from typing import Set, List

class AsyncWebCrawler:
    """
    Asynchronous web crawler that crawls pages within a single domain.
    """
    def __init__(self, start_url: str, max_depth: int = 3, rate_limit: float = 1.0):
        """
        Initialize the crawler.

        :param start_url: Starting URL for crawling.
        :param max_depth: Maximum depth for recursive crawling.
        :param rate_limit: Delay (in seconds) between consecutive requests.
        """
        self.start_url = start_url
        self.max_depth = max_depth
        self.rate_limit = rate_limit
        self.base_domain = urlparse(start_url).netloc
        self.visited: Set[str] = set()
        self.results = {}  # Mapping of URL -> list of found URLs

        # Configure logging for detailed output and debugging.
        self.logger = logging.getLogger("AsyncWebCrawler")
        self.logger.setLevel(logging.DEBUG)
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
        async with aiohttp.ClientSession() as session:
            await self.crawl_url(session, self.start_url, 0)

    def save_results(self, filename: str):
        """
        Save crawling results to a JSON file.

        :param filename: Path of the JSON file.
        """
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=4)

# Below is an example of how to run the crawler.
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Async Web Crawler")
    parser.add_argument("start_url", help="Starting URL for crawling")
    parser.add_argument("--depth", type=int, default=3, help="Maximum depth for crawling")
    parser.add_argument("--rate", type=float, default=1.0, help="Delay between requests (seconds)")
    parser.add_argument("--output", type=str, default="results.json", help="File to save crawl results")
    args = parser.parse_args()

    crawler = AsyncWebCrawler(args.start_url, max_depth=args.depth, rate_limit=args.rate)
    asyncio.run(crawler.crawl())
    crawler.save_results(args.output)
    print(f"Crawling completed. Results saved to {args.output}")
