import re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
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
MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def fetch_page(url):
    try:
        return Fetcher.get(url)
    except Exception as error:
        raise SystemExit(f"Failed to fetch page: {error}")


def extract_company_from_label(label):
    if not label:
        return None
    match = re.search(r"with (.+)$", label)
    if match:
        return match.group(1).strip()
    return None


def extract_card_field(article, field_name):
    labels = [node.get_text(" ", strip=True) for node in article.select("dt")]
    values = [node.get_text(" ", strip=True) for node in article.select("dd")]
    for label, value in zip(labels, values):
        if label == field_name:
            return value
    return None


def extract_location_from_card(article):
    return extract_card_field(article, "Location")


def extract_salary_from_card(article):
    return extract_card_field(article, "Salary")


def extract_deadline_from_card(article):
    match = re.search(r"Deadline:\s*(.+)", article.get_text(" ", strip=False), re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_subject_tags_from_card(article):
    subject_headings = article.select("h3")
    tags = []
    for heading in subject_headings:
        heading_text = heading.get_text(" ", strip=True)
        if heading_text:
            tags.append(heading_text)
    return tags


def parse_detail_page(detail_html):
    soup = BeautifulSoup(detail_html, "html.parser")
    body = soup.select_one("div.body-content")
    if body is None:
        return {
            "job_description": None,
            "minimum_requirements": [],
            "preferred_requirements": [],
            "duration": None,
        }

    description_parts = []
    section_text = {}
    current_section = None
    for child in body.children:
        if getattr(child, "name", None) is None:
            continue
        if child.name == "h3":
            current_section = child.get_text(" ", strip=True).rstrip(":")
            section_text.setdefault(current_section, [])
            continue
        text = child.get_text(" ", strip=True)
        if not text:
            continue
        if current_section is None:
            description_parts.append(text)
        else:
            section_text[current_section].append(text)

    job_description_sections = ["About the Role", "Responsibilities", "Key Responsibilities"]
    job_description_parts = description_parts[:]
    for section_name in job_description_sections:
        job_description_parts.extend(section_text.get(section_name, []))

    requirements_text = " ".join(section_text.get("Requirements", []))
    minimum_requirements = extract_minimum_requirements(requirements_text)
    preferred_requirements = extract_preferred_requirements(requirements_text)
    duration = extract_duration_from_text(" ".join(job_description_parts + [requirements_text]))

    return {
        "job_description": " ".join(job_description_parts).strip() or None,
        "minimum_requirements": minimum_requirements,
        "preferred_requirements": preferred_requirements,
        "duration": duration,
    }


def extract_minimum_requirements(requirements_text):
    if not requirements_text:
        return []
    lines = [line.strip("•; ") for line in requirements_text.splitlines()]
    items = []
    seen = set()
    for line in lines:
        if not line:
            continue
        normalized_line = re.sub(r"\s+", " ", line).strip()
        if normalized_line.lower().startswith("preferred") or normalized_line.lower().startswith("preferable"):
            continue
        if normalized_line not in seen:
            seen.add(normalized_line)
            items.append(normalized_line)
    if not items:
        compact = re.sub(r"\s+", " ", requirements_text).strip()
        if compact:
            items.append(compact)
    return items


def extract_preferred_requirements(requirements_text):
    if not requirements_text:
        return []
    preferred_matches = []
    for match in re.finditer(r"(?:preferred|preferable)\s+([^.;\n]+)", requirements_text, re.IGNORECASE):
        value = match.group(1).strip()
        if value and value not in preferred_matches:
            preferred_matches.append(value)
    return preferred_matches


def extract_duration_from_text(text):
    if not text:
        return None
    month_pattern = r"(?:" + "|".join(MONTH_NAMES) + r")"
    patterns = [
        r"\b\d+\s*(?:months?|weeks?|days?)\b",
        rf"\b{month_pattern}\s*(?:-|to|–|—)\s*{month_pattern}(?:\s+\d{{4}})?\b",
        r"\byear in industry\b",
        r"\bplacement\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return None


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


def extract_listing_cards(soup, base_url):
    listings = []
    seen_urls = set()
    for article in soup.select("article"):
        if article.get("wire:key") is None:
            continue
        if article.get("aria-hidden") == "true":
            continue
        title_link = article.select('a[data-mk-label="Job Title"]')
        if not title_link:
            continue
        link = title_link[0]
        href = link.attrs.get("href")
        if not href:
            continue
        listing_url = urljoin(base_url, href)
        if listing_url in seen_urls:
            continue
        title = link.get_text(" ", strip=True)
        if not title or title.lower() == "view job":
            continue
        if title.lower().endswith(" logo"):
            continue
        company = extract_company_from_label(link.attrs.get("aria-label"))
        deadline = extract_deadline_from_card(article)
        raw_location = extract_location_from_card(article)
        salary = extract_salary_from_card(article)
        work_mode, location = normalize_location(raw_location)
        country = extract_country_from_location(raw_location)
        subject_tags = extract_subject_tags_from_card(article)
        detail_data = parse_detail_page(fetch_page(listing_url).html_content)
        seen_urls.add(listing_url)
        listings.append(
            {
                "source": "gradcracker",
                "source_url": listing_url,
                "source_site": urlparse(base_url).netloc.lower(),
                "title": title,
                "company": company,
                "deadline": deadline,
                "salary_listed": bool(salary),
                "salary": salary,
                "country": country,
                "work_mode": work_mode,
                "location": location,
                "subject_tags": subject_tags,
                "job_description": detail_data["job_description"],
                "minimum_requirements": detail_data["minimum_requirements"],
                "preferred_requirements": detail_data["preferred_requirements"],
                "duration": detail_data["duration"],
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return listings


def fetch_gradcracker_jobs(url=LISTINGS_URL):
    response = fetch_page(url)
    if getattr(response, "status", None) != 200:
        raise SystemExit(
            f"Failed to fetch listings page (status={getattr(response, 'status', 'unknown')}). "
            "Gradcracker may be rate-limiting or blocking requests."
        )
    soup = BeautifulSoup(response.html_content, "html.parser")
    jobs = extract_listing_cards(soup, url)
    return jobs
