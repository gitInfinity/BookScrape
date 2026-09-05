"""Parse module for extracting book data from HTML."""

from bs4 import BeautifulSoup
from config import WEBSITE_URL
from fetch import fetch_page


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
    
    urls = [WEBSITE_URL + "catalogue/category/books_1", 
            WEBSITE_URL + "catalogue/category/books_1/page-2.html", 
            WEBSITE_URL + "catalogue/category/books_1/page-3.html"
            ]
    for index, url in enumerate(urls, start=1):
        print(f"\n=== Fetching: {url} ===")
        html = fetch_page(url)
        if html:
            books = parse_book_cards(html)
            print(f"Found {len(books)} books on page {index} ")
            for book in books[:3]:  # Show first 3 books
                print(f"  - {book['title']}: {book['price']} (Rating: {book['rating']}/5)")
        else:
            print(f"Failed to fetch {url}")
        
if __name__ == "__main__":
    main()