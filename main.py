#imports libraries
import os
import requests
from bs4 import BeautifulSoup
import json
import google.generativeai as genai
from dotenv import load_dotenv 
#loads api from environment
load_dotenv()

genai.configure(api_key=os.getenv("gemini_api_key"))

demo_url= "https://www.google.com/about/careers/applications/jobs/results/116505799294886598-software-engineering-intern-summer-2026?category=DATA_CENTER_OPERATIONS&category=DEVELOPER_RELATIONS&category=HARDWARE_ENGINEERING&category=INFORMATION_TECHNOLOGY&category=MANUFACTURING_SUPPLY_CHAIN&category=NETWORK_ENGINEERING&category=PRODUCT_MANAGEMENT&category=PROGRAM_MANAGEMENT&category=SOFTWARE_ENGINEERING&category=TECHNICAL_INFRASTRUCTURE_ENGINEERING&category=TECHNICAL_SOLUTIONS&category=TECHNICAL_WRITING&category=USER_EXPERIENCE&jex=ENTRY_LEVEL&target_level=INTERN_AND_APPRENTICE"



brave_search_api_key = os.getenv("brave_search_api_key")
# Load your JSON file, read only.
with open("data/search_terms.json", "r") as file:
    #loads JSON file to Python OOP object
    data = json.load(file)

#creates 2 lists, they take their data from the JSON headers
fields = data["fields"]
opportunity_types = data["opportunity_types"]
#creates new list for query results
queries = []

#nested for loop
#for loop declares field and oppurtunity_type
#each field in the list of fields is looped through
for field in fields:
    #for each field each oppurtunity type is looped through
    for opportunity_type in opportunity_types:
        #combines a field to oppurtunity_type together to combine a phrase
        query = f"{field} {opportunity_type}"
        #adds to list of queries for future use
        queries.append(query)
        #outputs current query to terminal
        print(query)
        print(brave_search_api_key)