import asyncio
import json
import requests
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def eligibility_extractor():
    url = "https://grants.gov/search-grants"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="load")
        await asyncio.sleep(2)
        html_content = await page.content()
        await browser.close()

    soup = BeautifulSoup(html_content, "html.parser")
    labels = soup.select("#m-a2 label.usa-checkbox__label.margin-top-1")
    eligibilities = [label.text for label in labels]
    return [eleg.split("(")[0].strip() for eleg in eligibilities]


def grant_list():
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": "https://grants.gov",
        "Referer": "https://grants.gov/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    json_data = {
        "keyword": None,
        "oppNum": None,
        "cfda": None,
        "agencies": None,
        "sortBy": "openDate|desc",
        "rows": 5000,
        "eligibilities": None,
        "fundingCategories": None,
        "fundingInstruments": None,
        "dateRange": "3",
        "oppStatuses": "forecasted|posted",
    }

    response = requests.post(
        "https://apply07.grants.gov/grantsws/rest/opportunities/search",
        headers=headers,
        json=json_data,
    )
    return response.json()["oppHits"]


def grant_detail(id="350938"):
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Origin": "https://grants.gov",
        "Referer": "https://grants.gov/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    
    data = {
        "oppId": id,
    }

    response = requests.post(
        "https://apply07.grants.gov/grantsws/rest/opportunity/details",
        headers=headers,
        data=data,
    )
    return response.json()


if __name__ == "__main__":
    # print(asyncio.run(eligibility_extractor()))
    with open("grants.json", "w") as file:
        file.write(json.dumps(grant_list(), indent=4))

    with open("grants.json", "r") as file:
        data = json.load(file)

    with open("details.json", "a") as file:
        for grant in data:
            file.write(json.dumps(grant_detail(grant["id"]), indent=4))