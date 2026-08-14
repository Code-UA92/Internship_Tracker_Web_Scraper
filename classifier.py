import re

CATEGORY_RULES = {
    "software-engineering": [
        "software", "developer", "engineer", "backend", "frontend", "full stack",
        "full-stack", "platform", "systems", "computer science", "web", "embedded"
    ],
    "cyber-security": [
        "security", "cyber", "penetration", "infosec", "threat", "incident",
        "malware", "forensics", "identity", "cloud security"
    ],
    "data-science": [
        "data science", "data scientist", "analytics", "machine learning", "ml",
        "artificial intelligence", "ai", "statistics", "model", "python"
    ],
    "cloud-devops": [
        "cloud", "devops", "infrastructure", "platform engineering", "kubernetes",
        "aws", "azure", "terraform", "sre"
    ],
    "embedded-hardware": [
        "embedded", "hardware", "electronics", "fpga", "iot", "firmware", "electrical"
    ],
    "business-product": [
        "product", "business analyst", "product manager", "strategy", "commercial",
        "sales", "marketing", "business development"
    ],
}


def build_text(job):
    parts = [
        job.get("title") or "",
        job.get("company") or "",
        job.get("description") or "",
        " ".join(job.get("requirements") or []),
        " ".join(job.get("preferred_requirements") or []),
        " ".join(job.get("subject_tags") or []),
    ]
    return " ".join(parts).lower()


def classify_job(job):
    text = build_text(job)
    matched_categories = []
    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in text for keyword in keywords):
            matched_categories.append(category)
    if not matched_categories:
        matched_categories = ["general-technology"]
    job["categories"] = matched_categories
    job["tags"] = matched_categories
    return job


def classify_jobs(jobs):
    return [classify_job(job) for job in jobs]
