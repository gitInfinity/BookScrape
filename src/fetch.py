"""Fetch module for web scraping."""

import requests
from config import WEBSITE_URL, USER_AGENT
from pathlib import Path

CACHE_DIR = Path("cache")

headers = {
    "User-Agent": USER_AGENT
}

def fetch_page(url: str, cache_name: str) -> str | None:
    """Fetch a page and return its HTML, or None on failure."""
    cache_path = CACHE_DIR / cache_name
    if cache_path.exists():
        print(f"Loading from cache: {cache_path}")
        return cache_path.read_text(encoding="utf-8")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Fetch failed with status {response.status_code}")
            return None
        response.raise_for_status()
        html = response.text
        CACHE_DIR.mkdir(exist_ok=True)
        cache_path.write_text(html, encoding="utf-8")
        return html
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
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