import json
from pathlib import Path

from classifier import classify_jobs
from deduper import dedupe_jobs
from normalizer import normalize_jobs
from scraper import fetch_gradcracker_jobs


OUTPUT_PATH = Path(__file__).with_name("final_jobs.json")


def run_pipeline():
    raw_jobs = fetch_gradcracker_jobs()
    normalized_jobs = normalize_jobs(raw_jobs)
    classified_jobs = classify_jobs(normalized_jobs)
    canonical_jobs = dedupe_jobs(classified_jobs)
    if not canonical_jobs:
        raise SystemExit(
            "Pipeline produced 0 jobs. Existing final_jobs.json was not updated."
        )
    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(canonical_jobs, file, indent=2, ensure_ascii=False)
    return canonical_jobs


if __name__ == "__main__":
    jobs = run_pipeline()
    print(f"Processed {len(jobs)} canonical jobs")
    print(f"Saved to {OUTPUT_PATH}")
