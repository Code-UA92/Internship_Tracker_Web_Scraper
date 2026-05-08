import json
from scrapling import Fetcher
from bs4 import BeautifulSoup

demo_url = "https://www.google.com/about/careers/applications/jobs/results/116505799294886598-software-engineering-intern-summer-2026?category=DATA_CENTER_OPERATIONS&category=DEVELOPER_RELATIONS&category=HARDWARE_ENGINEERING&category=INFORMATION_TECHNOLOGY&category=MANUFACTURING_SUPPLY_CHAIN&category=NETWORK_ENGINEERING&category=PRODUCT_MANAGEMENT&category=PROGRAM_MANAGEMENT&category=SOFTWARE_ENGINEERING&category=TECHNICAL_INFRASTRUCTURE_ENGINEERING&category=TECHNICAL_SOLUTIONS&category=TECHNICAL_WRITING&category=USER_EXPERIENCE&jex=ENTRY_LEVEL&target_level=INTERN_AND_APPRENTICE"

response = Fetcher.get(demo_url)

soup = BeautifulSoup(response.text, "html.parser")


def first_text(selector):
    result = soup.select_one(selector)

    if result:
        return result.get_text(strip=True)

    return None


job_data = {
    "job_title": first_text("h1"),
    "job_type": None,
    "salary": None,
    "job_location": first_text("[class*='location'], [aria-label*='location']"),
    "source_url": demo_url
}

print(json.dumps(job_data, indent=2))