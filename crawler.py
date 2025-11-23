"""Web crawler module for recursively discovering and crawling website pages."""
import time
import requests
import urllib3
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from typing import List, Dict, Set, Optional
from collections import deque
import logging
import re

logger = logging.getLogger(__name__)


class WebCrawler:
    """Intelligent web crawler that recursively discovers and fetches pages from a website."""

    def __init__(
        self,
        start_url: str,
        max_pages: int = 100,
        max_depth: int = 3,
        crawl_delay: float = 1.0,
        same_domain_only: bool = True,
        exclude_patterns: List[str] = None,
        verify_ssl: bool = True
    ):
        """Initialize the web crawler.

        Args:
            start_url: Starting URL to begin crawling
            max_pages: Maximum number of pages to crawl
            max_depth: Maximum depth of links to follow
            crawl_delay: Delay in seconds between requests (politeness)
            same_domain_only: Only crawl links within the same domain
            exclude_patterns: List of patterns to exclude (e.g., ['.pdf', '/admin'])
            verify_ssl: Whether to verify SSL certificates
        """
        self.start_url = start_url
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.crawl_delay = crawl_delay
        self.same_domain_only = same_domain_only
        self.exclude_patterns = exclude_patterns or []
        self.verify_ssl = verify_ssl

        # Extract domain from start URL
        parsed = urlparse(start_url)
        self.domain = f"{parsed.scheme}://{parsed.netloc}"
        self.base_domain = parsed.netloc

        # Tracking
        self.visited_urls: Set[str] = set()
        self.crawled_pages: List[Dict[str, str]] = []

        # Disable SSL warnings if needed
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        logger.info(f"WebCrawler initialized for {start_url}")
        logger.info(f"Settings: max_pages={max_pages}, max_depth={max_depth}, same_domain={same_domain_only}")

    def crawl(self) -> List[Dict[str, str]]:
        """Start crawling from the start URL.

        Returns:
            List of dictionaries with 'url' and 'html' for each crawled page
        """
        # Queue: (url, depth)
        queue = deque([(self.start_url, 0)])
        self.visited_urls.add(self._normalize_url(self.start_url))

        logger.info(f"Starting crawl from {self.start_url}")

        while queue and len(self.crawled_pages) < self.max_pages:
            url, depth = queue.popleft()

            # Check depth limit
            if depth > self.max_depth:
                logger.debug(f"Skipping {url} - max depth reached")
                continue

            # Fetch page
            html = self._fetch_page(url)
            if html:
                # Store successfully crawled page
                self.crawled_pages.append({
                    'url': url,
                    'html': html,
                    'depth': depth
                })
                logger.info(f"Crawled [{len(self.crawled_pages)}/{self.max_pages}]: {url} (depth {depth})")

                # Extract and queue new links if not at max depth
                if depth < self.max_depth:
                    new_links = self._extract_links(html, url)
                    for link in new_links:
                        normalized = self._normalize_url(link)
                        if normalized and normalized not in self.visited_urls:
                            if self._is_valid_url(link):
                                queue.append((link, depth + 1))
                                self.visited_urls.add(normalized)
                                logger.debug(f"Queued: {link} (depth {depth + 1})")

                # Politeness delay
                if self.crawl_delay > 0 and queue:
                    time.sleep(self.crawl_delay)

        logger.info(f"Crawl complete. Total pages: {len(self.crawled_pages)}")
        return self.crawled_pages

    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch a single page.

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if fetch failed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AIWebReader/1.0; +https://github.com/yourrepo)'
            }
            response = requests.get(
                url,
                headers=headers,
                timeout=30,
                verify=self.verify_ssl,
                allow_redirects=True
            )
            response.raise_for_status()

            # Only process HTML content
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                logger.debug(f"Skipping {url} - not HTML (Content-Type: {content_type})")
                return None

            return response.text

        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None

    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from HTML.

        Args:
            html: HTML content
            base_url: Base URL for resolving relative links

        Returns:
            List of absolute URLs
        """
        links = []
        try:
            soup = BeautifulSoup(html, 'lxml')

            for anchor in soup.find_all('a', href=True):
                href = anchor['href']

                # Skip anchors and javascript
                if href.startswith('#') or href.startswith('javascript:'):
                    continue

                # Convert to absolute URL
                absolute_url = urljoin(base_url, href)

                # Remove fragment
                parsed = urlparse(absolute_url)
                clean_url = urlunparse(parsed._replace(fragment=''))

                links.append(clean_url)

        except Exception as e:
            logger.warning(f"Error extracting links from {base_url}: {e}")

        return links

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL should be crawled.

        Args:
            url: URL to check

        Returns:
            True if URL should be crawled
        """
        try:
            parsed = urlparse(url)

            # Must have http/https scheme
            if parsed.scheme not in ['http', 'https']:
                return False

            # Same domain check
            if self.same_domain_only and parsed.netloc != self.base_domain:
                logger.debug(f"Skipping {url} - different domain")
                return False

            # Check exclude patterns
            for pattern in self.exclude_patterns:
                if pattern in url.lower():
                    logger.debug(f"Skipping {url} - matches exclude pattern: {pattern}")
                    return False

            # Exclude common binary/media files
            excluded_extensions = [
                '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
                '.zip', '.tar', '.gz', '.mp4', '.mp3', '.wav', '.avi',
                '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
            ]
            path_lower = parsed.path.lower()
            if any(path_lower.endswith(ext) for ext in excluded_extensions):
                logger.debug(f"Skipping {url} - binary/media file")
                return False

            # Exclude common admin/system paths
            excluded_paths = ['/admin', '/login', '/logout', '/wp-admin', '/wp-login']
            if any(excluded in path_lower for excluded in excluded_paths):
                logger.debug(f"Skipping {url} - admin/system path")
                return False

            return True

        except Exception as e:
            logger.warning(f"Error validating URL {url}: {e}")
            return False

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication.

        Args:
            url: URL to normalize

        Returns:
            Normalized URL
        """
        try:
            parsed = urlparse(url)

            # Remove fragment and trailing slash
            path = parsed.path.rstrip('/')
            if not path:
                path = '/'

            normalized = urlunparse((
                parsed.scheme,
                parsed.netloc.lower(),
                path,
                parsed.params,
                parsed.query,
                ''  # Remove fragment
            ))

            return normalized

        except Exception as e:
            logger.warning(f"Error normalizing URL {url}: {e}")
            return url

    def get_stats(self) -> Dict[str, int]:
        """Get crawling statistics.

        Returns:
            Dictionary with crawl statistics
        """
        return {
            'pages_crawled': len(self.crawled_pages),
            'urls_visited': len(self.visited_urls),
            'max_pages': self.max_pages,
            'max_depth': self.max_depth
        }
