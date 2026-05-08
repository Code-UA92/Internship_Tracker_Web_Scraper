#imports libraries
import os
import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv 
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