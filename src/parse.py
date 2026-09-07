"""Parse module for extracting book data from HTML."""

from datetime import datetime, timezone
import logging

from bs4 import BeautifulSoup
from config import WEBSITE_URL
from fetch import fetch_page
from urllib.parse import urljoin

log = logging.getLogger(__name__)

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


def extract_book_links(html: str, page_url: str) -> tuple[list[str],str | None]:
    """Extract book links from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    book_urls = [
        urljoin(page_url, link["href"]) for link in soup.select("article.product_pod h3 a[href]")
    ]
    next_link = soup.select_one("li.next a[href]")
    next_url = urljoin(page_url, next_link["href"]) if next_link else None
    return book_urls, next_url


def extract_book_details(html: str, page_url: str, product_url: str) -> dict | None:
    """Extract detailed book information from HTML."""
    try:
        soup = BeautifulSoup(html, "html.parser")
        product = soup.select_one("article.product_page")
        if not product:
            log.error("Product page structure not found: %s", product_url)
            return None

        product_main = product.select_one("div.product_main")
        if not product_main:
            log.error("Product main section not found: %s", product_url)
            return None

        title_tag = product_main.select_one("h1")
        price_tag = product_main.select_one("p.price_color")
        availability_tag = product_main.select_one("p.instock.availability")
        description_tag = product.select_one("#product_description + p")
        rating_tag = product_main.select_one("p.star-rating")

        if not title_tag or not price_tag:
            log.warning("Missing title or price on page: %s", product_url)
            return None

        rating_class = None
        if rating_tag:
            rating_class = next(
                (
                    class_name
                    for class_name in rating_tag.get("class", [])
                    if class_name != "star-rating"
                ),
                None,
            )

        return {
            "title": title_tag.get_text(strip=True),
            "price": price_tag.get_text(strip=True),
            "rating": rating_class,
            "availability": (
                availability_tag.get_text(" ", strip=True)
                if availability_tag
                else None
            ),
            "description": (
                description_tag.get_text(strip=True)
                if description_tag
                else None
            ),
            "url": product_url,
            "source_page": page_url,
            "fetched_at": datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
        }
    except Exception:
        log.exception("Unexpected error parsing product page: %s", product_url)
        return None

def main():
    
    url = WEBSITE_URL + "catalogue/page-1.html"
    catalogue_pages = 0
    discovered_urls = []
    
    while url and catalogue_pages < 3:
        catalogue_pages += 1
        cache_name = f"catalogue-page-{catalogue_pages}.html"
        print(f"\n=== Fetching: {url} ===")
        try:
            html = fetch_page(url, cache_name)
        except Exception:
            log.exception("Unexpected error fetching catalogue page: %s", url)
            return
        if not html:
            print(f"Failed to fetch {url}")
            return
        try:
            book_urls, next_url = extract_book_links(html, url)
        except Exception:
            log.exception("Failed to parse catalogue page: %s", url)
            return
        discovered_urls.extend(book_urls)
        
        try:
            books = parse_book_cards(html)
        except Exception:
            log.exception("Failed to parse book cards from: %s", url)
            books = []
        print(f"Found {len(books)} books on page {catalogue_pages}")
        
        records = []

        for book_url in sorted(set(discovered_urls)):
            print(f"\nFetching book details from: {book_url}")
            book_id = book_url.rstrip("/").split("/")[-2].split("_")[-1]
            cache_name = f"book-detail-{book_id}.html"

            try:
                detail_html = fetch_page(book_url, cache_name)
            except Exception:
                log.exception("Unexpected error fetching book page: %s", book_url)
                continue
            if not detail_html:
                print(f"Failed to fetch {book_url}")
                continue

            record = extract_book_details(
                detail_html,
                page_url=url,
                product_url=book_url,
            )

            if record:
                records.append(record)
                print("\nBook details:")
                for field, value in record.items():
                    print(f"{field}: {value}")

        print(f"\ndetail_pages={len(records)}")
        
        url = next_url
        
    unique_book_urls = set(discovered_urls)
    print(f"\nTotal unique book URLs discovered: {len(unique_book_urls)}")
    
        
if __name__ == "__main__":
    main()