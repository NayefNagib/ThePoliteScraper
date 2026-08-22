from pathlib import Path
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
FIRST_CATALOGUE_URL = urljoin(BASE_URL, "catalogue/page-1.html")

CACHE_DIR = Path("cache")

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/NayefNagib)"
TIMEOUT = 10
REQUEST_DELAY = 0.5


def fetch_page(url: str, cache_file: Path) -> str:
    CACHE_DIR.mkdir(exist_ok=True)

    if cache_file.exists():
        content = cache_file.read_text(encoding="utf-8")

        print(f"CACHE HIT: {cache_file}")
        print(f"response_size={len(content)} bytes")

        return content

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

    return content


def get_catalogue_page_url(soup: BeautifulSoup) -> str | None:
    next_link = soup.select_one("li.next a")

    if next_link is None:
        return None

    href = next_link.get("href")

    if not href:
        return None

    return href


def discover_books():
    all_book_urls = []
    catalogue_pages = 0

    current_url = FIRST_CATALOGUE_URL

    while current_url and catalogue_pages < 3:
        catalogue_pages += 1

        cache_file = CACHE_DIR / f"catalogue-page-{catalogue_pages}.html"

        html = fetch_page(
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
                absolute_url = urljoin(
                    current_url,
                    href
                )

                all_book_urls.append(absolute_url)

        next_href = get_catalogue_page_url(soup)

        if next_href:
            next_url = urljoin(
                current_url,
                next_href
            )

            current_url = next_url

            if catalogue_pages < 3:
                sleep(REQUEST_DELAY)
        else:
            current_url = None

    unique_urls = list(dict.fromkeys(all_book_urls))

    print()
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(all_book_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return unique_urls


if __name__ == "__main__":
    discover_books()