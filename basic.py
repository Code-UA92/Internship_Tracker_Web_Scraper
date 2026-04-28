#imports libraries
import requests
from bs4 import BeautifulSoup

#finds website
url = "http://books.toscrape.com"
#saves response to variable
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

#loops through soup variables to find a links
for link in soup.find_all("a"):
    #prints href destination
    print(link.get("href"))