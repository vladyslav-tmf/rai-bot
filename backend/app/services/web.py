from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


class WebService:
    """Service for handling web-related operations."""

    def __init__(self) -> None:
        self.http_client = httpx.AsyncClient(follow_redirects=True, timeout=10.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()

    @staticmethod
    def extract_urls(text: str) -> list[str]:
        """Extract URLs from text."""
        words = text.split()
        urls = []

        for word in words:
            if WebService.is_valid_url(word):
                urls.append(word)

        return urls

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            is_valid = all([result.scheme in ["http", "https"], result.netloc])
            return is_valid

        except ValueError:
            return False

    async def get_webpage_content(self, url: str) -> str | None:
        """Get webpage content."""
        if not self.is_valid_url(url):
            return None

        try:
            response = await self.http_client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for element in soup(["script", "style", "meta", "link"]):
                element.decompose()

            text = soup.get_text(separator="\n", strip=True)

            text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

            return text

        except httpx.HTTPError:
            return None
