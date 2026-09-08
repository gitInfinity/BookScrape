"""Fetch module for web scraping."""

import requests
from config import WEBSITE_URL, USER_AGENT
from pathlib import Path
from dataclasses import dataclass
import logging
import time

CACHE_DIR = Path("cache")
RETRY_DELAY_SECONDS = 1

log = logging.getLogger(__name__)


@dataclass
class FetchStats:
    pages_fetched: int = 0
    cache_hits: int = 0
    failed_pages: int = 0

headers = {
    "User-Agent": USER_AGENT
}

def fetch_page(
    url: str, cache_name: str, stats: FetchStats | None = None
) -> str | None:
    """Fetch a page and return its HTML, or None on failure."""
    cache_path = CACHE_DIR / cache_name
    if cache_path.exists():
        if stats:
            stats.cache_hits += 1
        print(f"Loading from cache: {cache_path}")
        return cache_path.read_text(encoding="utf-8")

    for attempt in range(2):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                html = response.text
                CACHE_DIR.mkdir(exist_ok=True)
                cache_path.write_text(html, encoding="utf-8")
                if stats:
                    stats.pages_fetched += 1
                return html

            if 500 <= response.status_code <= 599 and attempt == 0:
                log.warning("Server error %s for %s; retrying once", response.status_code, url)
                time.sleep(RETRY_DELAY_SECONDS)
                continue

            log.error("Fetch failed with status %s: %s", response.status_code, url)
            break
        except requests.Timeout as error:
            if attempt == 0:
                log.warning("Timeout fetching %s; retrying once: %s", url, error)
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            log.error("Fetch timed out after retry: %s: %s", url, error)
            break
        except requests.RequestException as error:
            log.error("Error fetching %s: %s", url, error)
            break

    if stats:
        stats.failed_pages += 1
    return None
    
def main():
    # Example usage
    url = WEBSITE_URL
    html = fetch_page(url, "example.html")
    if html:
        print(f"Fetched {len(html)} characters from {url}")
    else:
        print(f"Failed to fetch {url}")
        
if __name__ == "__main__":
    main()