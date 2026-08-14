import hashlib
import re


def normalize_for_key(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip().lower())


def canonical_key(job):
    title = normalize_for_key(job.get("title"))
    company = normalize_for_key(job.get("company"))
    location = normalize_for_key(job.get("location"))
    deadline = normalize_for_key(job.get("deadline"))
    source_url = normalize_for_key(job.get("source_url"))
    if source_url:
        raw_key = source_url
    else:
        raw_key = "|".join([title, company, location, deadline])
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def merge_jobs(existing, new_job):
    existing["source_urls"] = sorted(set((existing.get("source_urls") or []) + [new_job.get("source_url")]))
    existing["sources"] = sorted(set((existing.get("sources") or []) + [new_job.get("source")]))
    existing["categories"] = sorted(set((existing.get("categories") or []) + (new_job.get("categories") or [])))
    existing["tags"] = sorted(set((existing.get("tags") or []) + (new_job.get("tags") or [])))
    existing["last_seen_at"] = new_job.get("scraped_at") or existing.get("last_seen_at")
    existing["title"] = existing.get("title") or new_job.get("title")
    existing["company"] = existing.get("company") or new_job.get("company")
    existing["location"] = existing.get("location") or new_job.get("location")
    if not existing.get("description"):
        existing["description"] = new_job.get("description")
    if not existing.get("country"):
        existing["country"] = new_job.get("country")
    if not existing.get("work_mode"):
        existing["work_mode"] = new_job.get("work_mode")
    return existing


def dedupe_jobs(jobs):
    deduped = {}
    for job in jobs:
        key = canonical_key(job)
        if key not in deduped:
            deduped[key] = {
                "id": key,
                "title": job.get("title"),
                "company": job.get("company"),
                "country": job.get("country"),
                "location": job.get("location"),
                "work_mode": job.get("work_mode"),
                "deadline": job.get("deadline"),
                "description": job.get("description"),
                "source": job.get("source"),
                "source_urls": [job.get("source_url")],
                "sources": [job.get("source")],
                "categories": job.get("categories") or [],
                "tags": job.get("tags") or [],
                "first_seen_at": job.get("scraped_at"),
                "last_seen_at": job.get("scraped_at"),
                "salary": job.get("salary"),
                "duration": job.get("duration"),
            }
        else:
            deduped[key] = merge_jobs(deduped[key], job)
    return list(deduped.values())
