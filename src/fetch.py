"""Fetch module for web scraping."""

import requests

from config import WEBSITE_URL

def fetch_page(url: str) -> str | None:
    """Fetch a page and return its HTML, or None on failure."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    
def main():
    # Example usage
    url = WEBSITE_URL
    html = fetch_page(url)
    if html:
        print(f"Fetched {len(html)} characters from {url}")  # Print first 500 characters of the HTML
    else:
        print(f"Failed to fetch {url}")
        
if __name__ == "__main__":
    main()