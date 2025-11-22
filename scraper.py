"""Web scraping module for extracting content from websites."""
import hashlib
import requests
import urllib3
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    """Scrapes and extracts content from web pages."""

    def __init__(self, url: str, verify_ssl: bool = True):
        """Initialize the scraper with a target URL.

        Args:
            url: The URL of the website to scrape
            verify_ssl: Whether to verify SSL certificates (default: True)
                       Set to False for sites with self-signed or problematic certificates
        """
        self.url = url
        self.verify_ssl = verify_ssl
        self.last_content_hash: Optional[str] = None

        # Disable SSL warnings if verification is disabled
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            logger.warning(
                f"SSL certificate verification is DISABLED for {url}. "
                "This is insecure and should only be used for trusted sources."
            )

    def fetch_content(self) -> Optional[str]:
        """Fetch the HTML content from the target URL.

        Returns:
            HTML content as string, or None if fetch failed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(
                self.url,
                headers=headers,
                timeout=30,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch content from {self.url}: {e}")
            if self.verify_ssl:
                logger.info(
                    "If this is an SSL certificate error, you can disable SSL verification "
                    "by setting VERIFY_SSL=false in your .env file (not recommended for production)"
                )
            return None

    def extract_text_chunks(self, html: str, chunk_size: int = 1000) -> List[Dict[str, str]]:
        """Extract text content from HTML and split into chunks.

        Args:
            html: HTML content as string
            chunk_size: Maximum size of each text chunk in characters

        Returns:
            List of dictionaries containing text chunks and metadata
        """
        soup = BeautifulSoup(html, 'lxml')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Extract title
        title = soup.title.string if soup.title else "No title"

        # Extract main text content
        text_elements = []

        # Get all paragraph, heading, and list item texts
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'article', 'section']):
            text = element.get_text(strip=True)
            if text and len(text) > 20:  # Filter out very short snippets
                text_elements.append({
                    'text': text,
                    'tag': element.name
                })

        # Create chunks with metadata
        chunks = []
        current_chunk = ""
        chunk_id = 0

        for element in text_elements:
            text = element['text']

            # If adding this text exceeds chunk size, save current chunk and start new one
            if len(current_chunk) + len(text) > chunk_size and current_chunk:
                chunks.append({
                    'id': f"chunk_{chunk_id}",
                    'text': current_chunk.strip(),
                    'source': self.url,
                    'title': title
                })
                chunk_id += 1
                current_chunk = ""

            current_chunk += text + " "

        # Add the last chunk
        if current_chunk.strip():
            chunks.append({
                'id': f"chunk_{chunk_id}",
                'text': current_chunk.strip(),
                'source': self.url,
                'title': title
            })

        logger.info(f"Extracted {len(chunks)} text chunks from {self.url}")
        return chunks

    def compute_content_hash(self, html: str) -> str:
        """Compute a hash of the content to detect changes.

        Args:
            html: HTML content as string

        Returns:
            SHA256 hash of the content
        """
        return hashlib.sha256(html.encode('utf-8')).hexdigest()

    def has_content_changed(self, html: str) -> bool:
        """Check if the content has changed since last scrape.

        Args:
            html: HTML content as string

        Returns:
            True if content has changed, False otherwise
        """
        current_hash = self.compute_content_hash(html)

        if self.last_content_hash is None:
            self.last_content_hash = current_hash
            return True

        if current_hash != self.last_content_hash:
            self.last_content_hash = current_hash
            return True

        return False

    def scrape(self) -> Optional[List[Dict[str, str]]]:
        """Perform a full scrape: fetch, extract, and chunk content.

        Returns:
            List of text chunks with metadata, or None if scraping failed
        """
        html = self.fetch_content()
        if not html:
            return None

        # Check if content has changed
        if not self.has_content_changed(html):
            logger.info("Content has not changed, skipping extraction")
            return []

        chunks = self.extract_text_chunks(html)
        return chunks
