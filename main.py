#imports libraries
import os
import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv 
#loads api from environment
load_dotenv()
from google import genai
from scrapling import Fetcher

client = genai.Client(api_key=os.getenv("gemini_api_key"))

demo_url= "https://www.efinancialcareers.co.uk/jobs-UK-London-Software_Developer_Summer_Internship.id24214094?utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic"

def extract_job_details(page_text, source_url):

    prompt = f"""
        Extract the following job details from this webpage.

        Return ONLY valid JSON with:
        - job_title
        - job_type
        - salary
        - job_location
        - source_url

        If missing, return null.

        Source URL:
        {source_url}

        Text:
        {page_text}
        """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
        )

    return response.text

 
response = requests.get(demo_url)

soup = BeautifulSoup(response.text, "html.parser")

page_text = soup.get_text(separator="\n", strip=True)

result = extract_job_details(page_text[:10000], demo_url)

print(result)