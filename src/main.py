"""Application entry point for the Books to Scrape pipeline."""

import json
import logging
from pathlib import Path

from config import WEBSITE_URL
from fetch import fetch_page
from parse import extract_book_details, extract_book_links, parse_book_cards
from pydantic import ValidationError
from models import BookRecord, BookError

log = logging.getLogger(__name__)


def main():
    catalogue_url = WEBSITE_URL + "catalogue/page-1.html"
    catalogue_pages = 0
    discovered_books = {}

    while catalogue_url and catalogue_pages < 3:
        catalogue_pages += 1
        cache_name = f"catalogue-page-{catalogue_pages}.html"
        print(f"\n=== Fetching: {catalogue_url} ===")

        try:
            html = fetch_page(catalogue_url, cache_name)
            if not html:
                log.error("Failed to fetch catalogue page: %s", catalogue_url)
                break

            book_urls, next_url = extract_book_links(html, catalogue_url)
            for product_url in book_urls:
                discovered_books.setdefault(product_url, catalogue_url)

            books = parse_book_cards(html)
            print(f"Found {len(books)} books on page {catalogue_pages}")
        except Exception:
            log.exception("Failed to process catalogue page: %s", catalogue_url)
            break

        catalogue_url = next_url

    records: list[dict] = []
    errors: list[dict] = []
    for product_url, source_page in sorted(discovered_books.items()):
        print(f"\nFetching book details from: {product_url}")
        book_id = product_url.rstrip("/").split("/")[-2].split("_")[-1]
        cache_name = f"book-detail-{book_id}.html"

        try:
            detail_html = fetch_page(product_url, cache_name)
            if not detail_html:
                continue

            record = extract_book_details(
                detail_html,
                source_page=source_page,
                product_url=product_url,
            )
            
            if record is None:
                errors.append(
                    BookError(
                            product_url=product_url,
                            source_page=source_page,
                            reason="Could not extract book details",
                    ).model_dump(mode="json")
                )
                continue

            try:
                validated_record = BookRecord.model_validate(record)
            except ValidationError as error:
                log.warning("Record validation failed for %s: %s", product_url, error)

                errors.append(
                    BookError(
                        product_url=product_url,
                        source_page=source_page,
                        reason=str(error),
                    ).model_dump(mode="json")
                )
                continue

            records.append(validated_record.model_dump(mode="json"))
            
            print("\nBook details:")
            for field, value in record.items():
                print(f"{field}: {value}")
        except Exception:
            log.exception("Failed to process product page: %s", product_url)

    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)

    books_path = output_dir / "books.json"
    errors_path = output_dir / "errors.json"

    books_path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    errors_path.write_text(
        json.dumps(errors, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nTotal unique book URLs discovered: {len(discovered_books)}")
    print(f"detail_pages={len(records)}")
    print(f"valid output: {books_path}")
    print(f"error output: {errors_path}")


if __name__ == "__main__":
    main()
