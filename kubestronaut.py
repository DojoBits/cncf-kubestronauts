import asyncio
import os
import time

import aiohttp
import gspread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Set up environment variables
# This is the Google service account JSON file. You need to setup that.
GSHEET_CREDS = os.getenv("GSHEET_CREDS")
# This is the Google Sheet ID it looks something like 1ha_2rN4xRCah9KfnEUj2E..
GSHEET_KEY = os.getenv("GSHEET_KEY")


# Asynchronous function to fetch population data from REST Countries API. It's
# just faster with async
async def fetch_population(session, country_name):
    print(f"Fetching population for {country_name}...")
    url = f"https://restcountries.com/v3.1/name/{country_name}"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            """
            Some countries have multiple entries, so we need to handle them.
            I found that "United States" and "Georgia" have multiple entries.
            Let's handle them specifically.
            """
            if country_name.lower() == "united states" and len(data) > 1:
                print(f"Fetching the second population entry for {country_name}.")
                return data[1].get("population", "Population data not available")
            elif country_name.lower() == "georgia" and len(data) > 1:
                print(f"Fetching the second population entry for {country_name}.")
                return data[1].get("population", "Population data not available")
            return data[0].get("population", "Population data not available")
        print(f"Failed to fetch population data for {country_name}.")
        return "Population data not available"


# Asynchronous function to get populations for all countries
async def get_populations(countries):
    print("Starting population fetch for all countries...")
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_population(session, country[0]) for country in countries]
        populations = await asyncio.gather(*tasks)
        print("Completed population fetch for all countries.")
        return populations


"""
Step 1: Web Scraping with Selenium for Kubestronaut data.
At some point I relaliased that I can use much better way getting the data
directly from CNCF github people page:
https://github.com/cncf/people/blob/main/people.json, so if you want to play
better solutin is to parse the json.
"""

print("Starting Selenium to scrape Kubestronaut data...")
driver = webdriver.Chrome()
driver.get("https://www.cncf.io/training/kubestronaut/")
wait = WebDriverWait(driver, 10)
select_element = wait.until(
    EC.presence_of_element_located((By.CLASS_NAME, "sf-input-select"))
)
options = select_element.find_elements(By.TAG_NAME, "option")

# Delay to ensure all data is scraped properly
time.sleep(3)

regions = []
countries = []
total_kubestronauts = 0

# Parse data into regions and countries
for option in options:
    text = option.get_attribute("innerText")
    if "(" in text:
        name, count = text.rsplit("(", 1)
        count = int(count.rstrip(")"))
        name = name.strip()
        # Check for leading spaces for countries. Some of them have two spaces
        if text.startswith("  "):
            countries.append([name, count])
        else:
            regions.append([name, count])
            total_kubestronauts += count

# Close Selenium browser
driver.quit()
print(f"Scraped {len(regions)} regions and {len(countries)} countries.")

# Fetch populations asynchronously
print("Fetching populations asynchronously...")
populations = asyncio.run(get_populations(countries))

"""
Prepare data for Google Sheets as batch this will avoid multiple API calls and
you will avoid hitting the rate limit of the API.
"""
batch_data = [
    [country[0], country[1], population]
    for country, population in zip(countries, populations)
]

"""
Sort batch_data by the number of Kubestronauts in descending order
I preffer to sort the data in the code. It is more reliable and easier.
"""

batch_data = sorted(batch_data, key=lambda x: x[1], reverse=True)

# Step 2: Update Google Sheets
print("Updating Google Sheets...")
glogin = gspread.service_account(filename=GSHEET_CREDS)
gsheet = glogin.open_by_key(GSHEET_KEY)
client = gsheet.worksheet("kubestronauts")

# Some custom headers
client.update(range_name="A1", values=[["Region"]])
client.update(range_name="B1", values=[["Kubestronauts"]])
client.update(range_name="D1", values=[["Country"]])
client.update(range_name="E1", values=[["Kubestronauts"]])
client.update(range_name="F1", values=[["Population"]])
client.update(range_name="A10", values=[["Total Kubestronauts"]])
client.update(range_name="B10", values=[[total_kubestronauts]])

# Sort regions by the number of Kubestronauts (second column) in descending order
regions = sorted(regions, key=lambda x: x[1], reverse=True)
# Update regions individually
print("Updating regions individually...")
for i, region in enumerate(regions, start=2):
    client.update(range_name=f"A{i}:B{i}", values=[region])

# Batch update countries starting from D2
print("Batch updating countries in Google Sheets...")

client.update(range_name="D2", values=batch_data)

print("Data has been successfully updated in the Google Sheet.")
