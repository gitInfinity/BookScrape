# Books to Scrape

A small, cache-aware scraper for the public Books to Scrape practice site.

## Target Classification

- **Site:** [Books to Scrape](https://books.toscrape.com/)
- **Lane:** Web scraping and structured data extraction
- **Classification:** A public sandbox catalogue intended for practising web scraping
- **Scope:** The first three catalogue pages and their product detail pages
- **Collected data:** Book title, price, availability, rating, description, and source URLs

The site is a dedicated practice sandbox. This project should not be reused against another
site without checking that site's terms, robots guidance, and access rules first.

## Install and Run

Install [uv](https://docs.astral.sh/uv/) first, then run this command from the repository root:

```powershell
uv run --with requests --with beautifulsoup4 python src/main.py
```

The command creates:

- `output/books.json` - valid book records
- `output/errors.json` - pages or records that could not be processed
- `output/run-report.json` - counts and timing for the run

Run the tests with:

```powershell
uv run pytest -q
```

## Record Schema

Each item in `output/books.json` is validated with Pydantic and has this shape:

| Field | Type | Meaning |
| --- | --- | --- |
| `title` | string | Book title |
| `product_url` | URL | Absolute product detail URL |
| `price_text` | string | Original displayed price |
| `price_gbp` | non-negative number | Normalized price in GBP |
| `availability_text` | string or null | Availability shown on the detail page |
| `rating_text` | string or null | Rating word such as `Three` |
| `description` | string or null | Product description, when present |
| `source_page` | URL | Catalogue page where the book was found |
| `fetched_at` | string | UTC timestamp for record extraction |

## Politeness Rules

- Requests identify themselves with a descriptive project user-agent.
- Each request has a 10-second timeout.
- A timeout or 5xx server response is retried once after a one-second delay.
- 403 and 404 responses are not retried.
- Successful pages are cached on disk and reused on later runs.
- The scraper limits itself to three catalogue pages and processes each page independently so one failure does not discard good records.

## Real Run Report

This is a real report produced by the scraper:

```json
{
	"start_time": "2026-09-08T20:50:00Z",
	"duration_seconds": 0.938,
	"pages_fetched": 0,
	"cache_hits": 63,
	"valid_records": 60,
	"invalid_records": 1,
	"failed_pages": 1
}
```

The failed page in this run was an intentionally made-up URL used to verify that a broken
page is logged and skipped while the 60 valid records survive.

No browser was needed: the required data is already in the HTML sent by the server, so a
browser would only add cost.

## Limitation

The scraper only follows the first three catalogue pages; it is not a complete export of the
site's catalogue.

## Ethics

Use an official API when one exists. Never bypass logins, paywalls, or access blocks. Collect
only the data needed for the stated purpose, and keep requests slow, limited, and identifiable.