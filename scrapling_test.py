import json
import re
from urllib.parse import urljoin, urlparse

from scrapling import Fetcher


LISTINGS_URL = "https://www.gradcracker.com/search/all-disciplines/engineering-graduate-jobs"

COUNTRY_HINTS = {
    "Netherlands": "Netherlands",
    "Switzerland": "Switzerland",
    "Ireland": "Ireland",
    "Germany": "Germany",
    "France": "France",
    "Belgium": "Belgium",
    "Spain": "Spain",
    "Italy": "Italy",
    "Portugal": "Portugal",
    "Norway": "Norway",
    "Sweden": "Sweden",
    "Denmark": "Denmark",
    "Finland": "Finland",
    "Austria": "Austria",
    "Poland": "Poland",
    "Canada": "Canada",
    "Australia": "Australia",
    "New Zealand": "New Zealand",
    "United States": "United States",
    "USA": "United States",
    "Singapore": "Singapore",
    "India": "India",
}


def extract_company_from_label(label):
    if not label:
        return None

    match = re.search(r"with (.+)$", label)
    if match:
        return match.group(1).strip()

    return None


def extract_location_from_card(article):
    return extract_card_field(article, "Location")


def extract_salary_from_card(article):
    return extract_card_field(article, "Salary")


def extract_card_field(article, field_name):
    labels = [node.get_all_text().strip() for node in article.css("dt")]
    values = [node.get_all_text().strip() for node in article.css("dd")]

    for label, value in zip(labels, values):
        if label == field_name:
            return value

    return None


def extract_deadline_from_card(article):
    match = re.search(r"Deadline:\s*(.+)", article.get_all_text(), re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return None


def extract_subject_tags_from_card(article):
    subject_headings = article.css("h3")

    if not subject_headings:
        return []

    raw_text = subject_headings[0].get_all_text().strip()
    if not raw_text:
        return []

    tags = []
    seen_tags = set()

    for part in raw_text.split(","):
        tag = part.strip().rstrip(".")
        if not tag or tag in seen_tags:
            continue

        seen_tags.add(tag)
        tags.append(tag)

    return tags


def normalize_location(location):
    if not location:
        return None, None

    if "Remote" in location:
        return "Remote", location

    if "Hybrid" in location:
        cleaned_location = re.sub(r"\s*\(Hybrid\)\s*", "", location).strip()
        cleaned_location = re.sub(r"\bHybrid\b", "", cleaned_location).strip()
        cleaned_location = re.sub(r"\s{2,}", " ", cleaned_location)

        return "Hybrid", cleaned_location or location

    return "Onsite", location


def extract_country_from_location(location):
    if not location:
        return None

    if "Remote" in location:
        return "Remote"

    if "Rijswijk" in location:
        return "Netherlands"

    if "Geneva" in location:
        return "Switzerland"

    if "Cork" in location or "Dublin" in location:
        if "Belfast" in location:
            return "Ireland / United Kingdom"
        return "Ireland"

    cleaned_location = re.sub(r"\s*\(Hybrid\)\s*", "", location).strip()
    cleaned_location = re.sub(r"\bHybrid\b", "", cleaned_location).strip()

    country_match = re.search(r"\(([^()]+)\)\s*$", cleaned_location)
    if country_match:
        candidate = country_match.group(1).strip()
        if candidate in COUNTRY_HINTS:
            return COUNTRY_HINTS[candidate]

    if re.search(r"\b(UK|England|Scotland|Wales|Northern Ireland|London|Birmingham|Bristol|Manchester|Leeds|Glasgow|Edinburgh|Sheffield|Exeter|Reading|Swindon|Oxford|Cambridge|Plymouth|Newcastle|Dartmouth|Warton|Samlesbury|Brough|Northampton|Peterborough|Teddington|Rochester|Chatham|Falmer|Alfreton|Uxbridge|Stratford-upon-Avon|Sherborne|Cramlington|Thames Valley|Belfast|Cardiff)\b", cleaned_location):
        return "United Kingdom"

    if "Multiple Worldwide Locations" in cleaned_location:
        return "International"

    return None


def fetch_page(url):
    try:
        return Fetcher.get(url)
    except Exception as error:
        raise SystemExit(f"Failed to fetch page: {error}")


def extract_listing_cards(soup, base_url):
    listings = []
    seen_urls = set()

    for article in soup.css('article[wire\\:key]'):
        title_link = article.css('a[data-mk-label="Job Title"]')

        if not title_link:
            continue

        link = title_link[0]
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

        company = extract_company_from_label(link.attrib.get("aria-label"))
        deadline = extract_deadline_from_card(article)
        raw_location = extract_location_from_card(article)
        salary = extract_salary_from_card(article)
        work_mode, location = normalize_location(raw_location)
        country = extract_country_from_location(raw_location)
        subject_tags = extract_subject_tags_from_card(article)

        seen_urls.add(listing_url)
        listings.append(
            {
                "title": title,
                "company": company,
                "deadline": deadline,
                "salary_listed": bool(salary),
                "salary": salary,
                "country": country,
                "work_mode": work_mode,
                "location": location,
                "subject_tags": subject_tags,
                "url": listing_url,
            }
        )

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