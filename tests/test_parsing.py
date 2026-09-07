from pathlib import Path

from parse import extract_book_details, extract_book_links, parse_book_cards


HTML_WITH_BOOKS = """
<html>
  <body>
    <ul class="row">
      <li>
        <article class="product_pod">
          <h3><a href="/catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the Attic</a></h3>
          <p class="price_color">£51.77</p>
          <p class="star-rating Three">Three</p>
        </article>
      </li>
      <li>
        <article class="product_pod">
          <h3><a href="/catalogue/its-only-the-himalayas_981/index.html" title="It's Only the Himalayas">It's Only the Himalayas</a></h3>
          <p class="price_color">£45.17</p>
          <p class="star-rating Two">Two</p>
        </article>
      </li>
    </ul>
    <li class="next"><a href="/catalogue/page-2.html">next</a></li>
  </body>
</html>
"""


HTML_DETAIL = """
<article class="product_page">
  <div class="product_main">
    <h1>A Light in the Attic</h1>
    <p class="price_color">£51.77</p>
    <p class="instock availability">In stock (22 available)</p>
    <p class="star-rating Three">
      <i class="icon-star"></i>
    </p>
  </div>
  <div id="product_description"></div>
  <p>It's a book with some description.</p>
</article>
"""


def test_extract_book_links_returns_absolute_urls_and_next_page():
    urls, next_url = extract_book_links(HTML_WITH_BOOKS, "https://books.toscrape.com/catalogue/page-1.html")

    assert urls == [
        "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html",
    ]
    assert next_url == "https://books.toscrape.com/catalogue/page-2.html"


def test_parse_book_cards_extracts_title_price_and_rating():
    books = parse_book_cards(HTML_WITH_BOOKS)

    assert len(books) == 2
    assert books[0]["title"] == "A Light in the Attic"
    assert books[0]["price"] == "£51.77"
    assert books[0]["rating"] == 3


def test_extract_book_details_extracts_product_record():
    record = extract_book_details(
        HTML_DETAIL,
        source_page="https://books.toscrape.com/catalogue/page-1.html",
        product_url="https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    )

    assert record is not None
    assert record["title"] == "A Light in the Attic"
    assert record["price_text"] == "£51.77"
    assert record["product_url"].startswith("https://")
    assert record["source_page"].startswith("https://")
    assert record["description"] == "It's a book with some description."
