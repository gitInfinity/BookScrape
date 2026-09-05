# Web Scraper - Books to Scrape

## Target Classification
- **Site**: https://books.toscrape.com/
- **Why**: Sandbox site built for practising web scraping
- **Scope**: First 3 catalogue pages only
- **Data collected**: Book title, price, and rating (1-5 stars) from each catalogue page
- **Appropriateness**: This is a dedicated practise sandbox; the code will not be reused on another site without checking its rules and terms first

## Robots.txt Check
- Fetched: https://books.toscrape.com/robots.txt
- Result: no robots file found

## Implementation
- Scraper entry point: `src/main.py`
- Uses: `requests` for HTTP, `beautifulsoup4` for HTML parsing
- Collects data from the first 3 catalogue pages only