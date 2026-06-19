import json
from urllib.parse import urljoin, urlparse

from scrapling import Fetcher


LISTINGS_URL = "https://www.gradcracker.com/search/all-disciplines/engineering-graduate-jobs"


def fetch_page(url):
    try:
        return Fetcher.get(url)
    except Exception as error:
        raise SystemExit(f"Failed to fetch page: {error}")


def extract_listing_cards(soup, base_url):
    listings = []
    seen_urls = set()

    for link in soup.css('a[href*="/graduate-job/"]'):
        href = link.attrib.get("href")

        if not href:
            continue

        listing_url = urljoin(base_url, href)

        if listing_url in seen_urls:
            continue

        title = link.get_all_text().strip()

        if not title or title.lower() == "view job":
            continue

        if title.lower().endswith(" logo"):
            continue

        seen_urls.add(listing_url)
        listings.append({"title": title, "url": listing_url})

    return listings


response = fetch_page(LISTINGS_URL)
listings = extract_listing_cards(response, LISTINGS_URL)

result = {
    "source_url": LISTINGS_URL,
    "job_board_site": urlparse(LISTINGS_URL).netloc.lower(),
    "count": len(listings),
    "listings": listings[:10],
}

print(json.dumps(result, indent=2))

with open("job_data.json", "w", encoding="utf-8") as file:
    json.dump(result, file, indent=2, ensure_ascii=False)