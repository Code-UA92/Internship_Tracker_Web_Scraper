import re
from datetime import datetime


def clean_text(value):
    if value is None:
        return None
    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)
    return value or None


def normalize_country(value):
    if value is None:
        return None
    value = clean_text(value)
    return value or None


def normalize_work_mode(value):
    if value is None:
        return "Unknown"
    normalized = str(value).strip()
    if normalized.lower() in {"remote", "hybrid", "onsite"}:
        return normalized.title()
    return normalized or "Unknown"


def normalize_deadline(value):
    if value is None:
        return None
    return clean_text(value)


def normalize_job(raw_job):
    normalized = {
        "source": raw_job.get("source") or "unknown",
        "source_url": raw_job.get("source_url") or raw_job.get("url"),
        "title": clean_text(raw_job.get("title")),
        "company": clean_text(raw_job.get("company")),
        "country": normalize_country(raw_job.get("country")),
        "location": clean_text(raw_job.get("location")),
        "work_mode": normalize_work_mode(raw_job.get("work_mode")),
        "deadline": normalize_deadline(raw_job.get("deadline")),
        "salary": clean_text(raw_job.get("salary")),
        "description": clean_text(raw_job.get("job_description")),
        "requirements": raw_job.get("minimum_requirements") or [],
        "preferred_requirements": raw_job.get("preferred_requirements") or [],
        "duration": clean_text(raw_job.get("duration")),
        "subject_tags": raw_job.get("subject_tags") or [],
        "scraped_at": raw_job.get("scraped_at") or datetime.utcnow().isoformat(),
    }
    return normalized


def normalize_jobs(raw_jobs):
    return [normalize_job(job) for job in raw_jobs]
