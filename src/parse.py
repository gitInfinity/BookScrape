"""Parse module for extracting book data from HTML."""

from bs4 import BeautifulSoup
from config import WEBSITE_URL
from fetch import fetch_page
from urllib.parse import urljoin

def extract_book_links(html: str, page_url: str) -> tuple[list[str],str | None]:
    """Extract book links from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    book_urls = [
        urljoin(page_url, link["href"]) for link in soup.select("article.product_pod h3 a[href]")
    ]
    next_link = soup.select_one("li.next a[href]")
    next_url = urljoin(page_url, next_link["href"]) if next_link else None
    return book_urls, next_url

def parse_book_cards(html: str) -> list[dict]:
    """Extract book information from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    books = []
    for card in soup.select("article.product_pod"):
        title = card.h3.a["title"]
        price_tag = card.select_one("p.price_color")
        price = price_tag.get_text(strip=True) if price_tag else None
        rating_class = card.p["class"][1]  # e.g. "Three"
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        rating = rating_map.get(rating_class, 0)
        books.append(
            {
                "title": title,
                "price": price,
                "rating": rating,
            }
        )
    return books

def main():
    
    url = WEBSITE_URL + "catalogue/page-1.html"
    catalogue_pages = 0
    discovered_urls = []
    
    while url and catalogue_pages < 3:
        catalogue_pages += 1
        cache_name = f"catalogue-page-{catalogue_pages}.html"
        print(f"\n=== Fetching: {url} ===")
        html = fetch_page(url, cache_name)
        if not html:
            print(f"Failed to fetch {url}")
            return
        book_urls, next_url = extract_book_links(html, url)
        discovered_urls.extend(book_urls)
        
        books = parse_book_cards(html)
        print(f"Found {len(books)} books on page {catalogue_pages}")
        
        for book in books[:3]:  # Show first 3 books per page
            print(f"  - {book['title']}: {book['price']} (Rating: {book['rating']}/5)")
        
        url = next_url
        
    unique_book_urls = set(discovered_urls)
    print(f"\nTotal unique book URLs discovered: {len(unique_book_urls)}")
    
        
if __name__ == "__main__":
    main()