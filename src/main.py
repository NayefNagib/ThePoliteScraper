from pathlib import Path

import requests


BASE_URL = "https://books.toscrape.com/"
CATALOGUE_PAGE_1 = BASE_URL + "catalogue/page-1.html"

CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/NayefNagib)"
TIMEOUT = 10


def fetch_catalogue_page():
    CACHE_DIR.mkdir(exist_ok=True)

    if CACHE_FILE.exists():
        content = CACHE_FILE.read_text(encoding="utf-8")

        print("CACHE HIT")
        print(f"response_size={len(content)} bytes")

        return content

    print("FETCH")

    response = requests.get(
        CATALOGUE_PAGE_1,
        headers={
            "User-Agent": USER_AGENT
        },
        timeout=TIMEOUT,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch page: HTTP {response.status_code}"
        )

    content = response.text

    CACHE_FILE.write_text(
        content,
        encoding="utf-8"
    )

    print(f"status={response.status_code}")
    print(f"response_size={len(content)} bytes")
    print(f"cached={CACHE_FILE}")

    return content


if __name__ == "__main__":
    fetch_catalogue_page()