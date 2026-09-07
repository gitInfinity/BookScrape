"""Parse module for extracting book data from HTML."""

from datetime import datetime, timezone
import logging

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from normalise import normalise_price

log = logging.getLogger(__name__)

def parse_book_cards(html: str) -> list[dict]:
    """Extract book information from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    books = []
    for card in soup.select("article.product_pod"):
        title = card.h3.a["title"]
        price_tag = card.select_one("p.price_color")
        price = price_tag.get_text(strip=True) if price_tag else None
        rating_tag = card.select_one("p.star-rating")
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


def extract_book_details(
    html: str, source_page: str, product_url: str
) -> dict | None:
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
        price_text = price_tag.get_text(strip=True) if price_tag else None
        try:
            price_gbp = normalise_price(price_text) if price_text else None
        except ValueError as e:
            log.warning("Failed to normalise price on page %s: %s", product_url, e)
            price_text = None
        availability_tag = product_main.select_one("p.instock.availability")
        description_tag = product.select_one("#product_description + p")
        rating_tag = product_main.select_one("p.star-rating")

        if not title_tag or not price_text:
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
            "price_text": price_text,
            "price_gbp": price_gbp,
            "rating_text": rating_class,
            "availability_text": (
                availability_tag.get_text(" ", strip=True)
                if availability_tag
                else None
            ),
            "description": (
                description_tag.get_text(strip=True)
                if description_tag
                else None
            ),
            "product_url": product_url,
            "source_page": source_page,
            "fetched_at": datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
        }
    except Exception:
        log.exception("Unexpected error parsing product page: %s", product_url)
        return None