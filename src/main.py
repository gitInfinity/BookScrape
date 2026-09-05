"""
Web scraper for Books to Scrape sandbox site.
Collects data from the first 3 catalogue pages.
"""

from .fetch import fetch_page
from .parse import parse_book_cards

BASE_URL = "https://books.toscrape.com/"


def main():
    # Check robots.txt first
    robots_url = BASE_URL + "robots.txt"
    robots_html = fetch_page(robots_url)
    if robots_html:
        print("robots.txt found:")
        print(robots_html[:500])
    else:
        print("no robots file found")

    # Fetch and parse the first 3 catalogue pages
    for page_num in range(1, 4):
        page_url = f"{BASE_URL}catalogue/page-{page_num}.html"
        print(f"\n=== Page {page_num}: {page_url} ===")
        html = fetch_page(page_url)
        if not html:
            print(f"Failed to fetch {page_url}")
            continue
        books = parse_book_cards(html)
        print(f"Found {len(books)} books on page {page_num}")
        for book in books[:3]:  # Show first 3 books per page
            print(f"  - {book['title']}: {book['price']} (Rating: {book['rating']}/5)")


if __name__ == "__main__":
    main()
