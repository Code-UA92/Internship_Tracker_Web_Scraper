import json
from urllib.parse import urlparse

from scrapling import Fetcher
from bs4 import BeautifulSoup

demo_url = "https://www.efinancialcareers.co.uk/jobs-UK-London-Software_Developer_Summer_Internship.id24214094"

FIELD_ALIASES = {
    "deadline": [
        "deadline",
        "due date",
        "closing date",
        "applications close",
        "application deadline",
        "valid through"
    ],
    "salary": [
        "salary",
        "compensation",
        "pay",
        "annual salary",
        "hourly rate"
    ],
    "location": [
        "location",
        "based in",
        "office"
    ]
}


def fetch_page(url):
    try:
        return Fetcher.get(url)
    except Exception as error:
        print(f"Failed to fetch page: {error}")
        exit()


def first_text(soup, selector):
    result = soup.select_one(selector)

    if result:
        return result.get_text(" ", strip=True)

    return None


def all_matching_lines(full_text, field_name):
    aliases = FIELD_ALIASES.get(field_name, [])
    matches = []

    for line in full_text.split("\n"):
        lower_line = line.lower()

        for alias in aliases:
            if alias.lower() in lower_line:
                matches.append(line.strip())
                break

    return matches


def detect_job_board_site(url):
    return urlparse(url).netloc.lower()


def infer_job_type(title):
    if not title:
        return None

    lower_title = title.lower()

    if "intern" in lower_title:
        return "Internship"

    if "placement" in lower_title:
        return "Placement Year"

    if "graduate" in lower_title:
        return "Graduate Role"

    return "Unknown"


def clean_company_name(company_data):
    if isinstance(company_data, dict):
        return company_data.get("name")

    if isinstance(company_data, str):
        return company_data

    return None


def detect_company_from_page(soup, full_text):
    selectors = [
        '[data-testid*="company"]',
        '[data-testid*="employer"]',
        '[class*="company"]',
        '[class*="Company"]',
        '[class*="employer"]',
        '[class*="Employer"]',
        'a[href*="/company/"]',
        'a[href*="/companies/"]',
        'a[href*="/employer/"]',
        'a[href*="/recruiter/"]'
    ]

    for selector in selectors:
        result = soup.select_one(selector)

        if result:
            text = result.get_text(" ", strip=True)

            if text:
                return text

    lines = [line.strip() for line in full_text.split("\n") if line.strip()]

    for index, line in enumerate(lines):
        lower_line = line.lower()

        if lower_line in ["company", "employer", "hiring company", "recruiter"]:
            if index + 1 < len(lines):
                return lines[index + 1]

        if lower_line.startswith("company:"):
            return line.split(":", 1)[1].strip()

        if lower_line.startswith("employer:"):
            return line.split(":", 1)[1].strip()

        if lower_line.startswith("recruiter:"):
            return line.split(":", 1)[1].strip()

    return None


def clean_location(location_data):
    if isinstance(location_data, list) and location_data:
        location_data = location_data[0]

    if isinstance(location_data, dict):
        address = location_data.get("address")

        if isinstance(address, dict):
            parts = [
                address.get("addressLocality"),
                address.get("addressRegion"),
                address.get("addressCountry")
            ]

            return ", ".join(part for part in parts if part)

        return location_data.get("name")

    if isinstance(location_data, str):
        return location_data

    return None


def clean_salary(job_posting):
    salary_data = job_posting.get("baseSalary")

    if not salary_data:
        return None

    if isinstance(salary_data, dict):
        value = salary_data.get("value")

        if isinstance(value, dict):
            min_value = value.get("minValue")
            max_value = value.get("maxValue")
            unit_text = value.get("unitText")
            currency = salary_data.get("currency")

            if min_value and max_value:
                return f"{currency or ''} {min_value} - {max_value} {unit_text or ''}".strip()

            if min_value:
                return f"{currency or ''} {min_value} {unit_text or ''}".strip()

        return salary_data.get("currency")

    return str(salary_data)


def find_job_posting_json_ld(soup):
    scripts = soup.select('script[type="application/ld+json"]')

    for script in scripts:
        if not script.string:
            continue

        try:
            data = json.loads(script.string)
        except json.JSONDecodeError:
            continue

        items = data if isinstance(data, list) else [data]

        for item in items:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                return item

            if isinstance(item, dict) and "@graph" in item:
                for graph_item in item["@graph"]:
                    if isinstance(graph_item, dict) and graph_item.get("@type") == "JobPosting":
                        return graph_item

    return None


response = fetch_page(demo_url)
soup = BeautifulSoup(response.text, "html.parser")
full_text = soup.get_text(separator="\n", strip=True)

job_posting = find_job_posting_json_ld(soup)

location_matches = all_matching_lines(full_text, "location")
salary_matches = all_matching_lines(full_text, "salary")
deadline_matches = all_matching_lines(full_text, "deadline")

if job_posting:
    title = job_posting.get("title") or first_text(soup, "h1")

    company = clean_company_name(job_posting.get("hiringOrganization"))

    if not company:
        company = detect_company_from_page(soup, full_text)

    location = clean_location(job_posting.get("jobLocation"))
    salary = clean_salary(job_posting)
    description = job_posting.get("description") or first_text(soup, "main")
    deadline = job_posting.get("validThrough")
    open_date = job_posting.get("datePosted")
else:
    title = first_text(soup, "h1")
    company = detect_company_from_page(soup, full_text)
    location = location_matches[0] if location_matches else None
    salary = salary_matches[0] if salary_matches else None
    description = first_text(soup, "main")
    deadline = deadline_matches[0] if deadline_matches else None
    open_date = None


job_data = {
    "title": title,
    "company": company,
    "job_board_site": detect_job_board_site(demo_url),
    "job_type": infer_job_type(title),
    "location": location,
    "description": description,
    "req_qualifications": [],
    "pref_qualifications": [],
    "open_date": open_date,
    "deadline": deadline,
    "programme_link": demo_url,
    "salary": salary,
    "is_active": True,
    "is_paid": salary is not None
}

print(json.dumps(job_data, indent=2))

with open("job_data.json", "w", encoding="utf-8") as file:
    json.dump(job_data, file, indent=2, ensure_ascii=False)