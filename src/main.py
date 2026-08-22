from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
FIRST_CATALOGUE_URL = urljoin(BASE_URL, "catalogue/page-1.html")

CACHE_DIR = Path("cache")
DETAIL_CACHE_DIR = CACHE_DIR / "books"

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/NayefNagib)"
TIMEOUT = 10
REQUEST_DELAY = 0.5


def fetch_page(url: str, cache_file: Path) -> tuple[str, bool]:
    """
    Fetch a page or read it from cache.

    Returns:
        (html, cache_hit)
    """
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    if cache_file.exists():
        content = cache_file.read_text(encoding="utf-8")

        print(f"CACHE HIT: {cache_file}")
        print(f"response_size={len(content)} bytes")

        return content, True

    print(f"FETCH: {url}")

    response = requests.get(
        url,
        headers={
            "User-Agent": USER_AGENT
        },
        timeout=TIMEOUT,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch {url}: HTTP {response.status_code}"
        )

    content = response.text

    cache_file.write_text(
        content,
        encoding="utf-8"
    )

    print(f"status={response.status_code}")
    print(f"response_size={len(content)} bytes")
    print(f"cached={cache_file}")

    return content, False


def get_catalogue_page_url(soup: BeautifulSoup) -> str | None:
    next_link = soup.select_one("li.next a")

    if next_link is None:
        return None

    href = next_link.get("href")

    if not href:
        return None

    return href


def discover_books() -> list[dict]:
    """
    Discover all unique book URLs from the first three catalogue pages.
    """
    all_books = []
    catalogue_pages = 0

    current_url = FIRST_CATALOGUE_URL

    while current_url and catalogue_pages < 3:
        catalogue_pages += 1

        cache_file = CACHE_DIR / f"catalogue-page-{catalogue_pages}.html"

        html, cache_hit = fetch_page(
            current_url,
            cache_file
        )

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        books = soup.select("article.product_pod h3 a")

        for book in books:
            href = book.get("href")

            if href:
                product_url = urljoin(
                    current_url,
                    href
                )

                all_books.append(
                    {
                        "product_url": product_url,
                        "source_page": current_url
                    }
                )

        next_href = get_catalogue_page_url(soup)

        if next_href:
            current_url = urljoin(
                current_url,
                next_href
            )

            if catalogue_pages < 3 and not cache_hit:
                sleep(REQUEST_DELAY)
        else:
            current_url = None

    unique_books = {}

    for book in all_books:
        unique_books[book["product_url"]] = book

    unique_books_list = list(unique_books.values())

    print()
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(all_books)}")
    print(f"unique_urls={len(unique_books_list)}")

    return unique_books_list


def extract_book_record(
    product_url: str,
    source_page: str,
    html: str
) -> dict:
    """
    Extract the eight required raw fields from a book page.
    """
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    product = soup.select_one("article.product_page")

    if product is None:
        raise ValueError("Product area not found")

    title_element = product.select_one("div.product_main h1")

    price_element = product.select_one(
        "div.product_main p.price_color"
    )

    availability_element = product.select_one(
        "div.product_main p.instock"
    )

    rating_element = product.select_one(
        "div.product_main p.star-rating"
    )

    description_element = soup.select_one(
        "#product_description + p"
    )

    if title_element is None:
        raise ValueError("Title not found")

    if price_element is None:
        raise ValueError("Price not found")

    if availability_element is None:
        raise ValueError("Availability not found")

    if rating_element is None:
        raise ValueError("Rating not found")

    rating_classes = rating_element.get("class", [])

    rating_text = next(
        (
            item
            for item in rating_classes
            if item != "star-rating"
        ),
        None
    )

    description = None

    if description_element is not None:
        description = description_element.get_text(
            strip=True
        )

    fetched_at = datetime.now(
        timezone.utc
    ).isoformat()

    return {
        "title": title_element.get_text(strip=True),
        "product_url": product_url,
        "price_text": price_element.get_text(strip=True),
        "availability_text": availability_element.get_text(strip=True),
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }


def scrape_books(book_links: list[dict]) -> list[dict]:
    """
    Fetch and extract all 60 book pages.
    """
    DETAIL_CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    records = []

    for index, book in enumerate(book_links, start=1):
        product_url = book["product_url"]
        source_page = book["source_page"]

        cache_file = DETAIL_CACHE_DIR / f"book-{index}.html"

        html, cache_hit = fetch_page(
            product_url,
            cache_file
        )

        try:
            record = extract_book_record(
                product_url,
                source_page,
                html
            )

            records.append(record)

        except Exception as error:
            print(
                f"EXTRACTION ERROR: {product_url} - {error}"
            )

        if not cache_hit and index < len(book_links):
            sleep(REQUEST_DELAY)

    return records


if __name__ == "__main__":
    book_links = discover_books()

    records = scrape_books(
        book_links
    )

    print()
    print(f"detail_pages={len(records)}")

    if records:
        print()
        print("SAMPLE RAW RECORD:")
        print(records[0])