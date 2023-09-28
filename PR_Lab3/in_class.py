import requests
from bs4 import BeautifulSoup
import json

def parseLinks(url, maxPages=None):
    linkList = []
    baseUrl = "https://999.md"
    page = 1
    try:
        while True:
            if maxPages is not None and page > maxPages:
                break
            response = requests.get(url + f"&page={page}")
            page += 1
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                pageLinks = soup.find_all("a", class_="js-item-ad")
                maxPageLink = soup.find("a", class_="is-last-page")
                for pageLink in pageLinks:
                    if pageLink == maxPageLink:
                        break
                    if baseUrl + pageLink.get('href') not in linkList:
                        if "/booster" in pageLink.get('href'):
                            continue
                        else:
                            linkList.append(baseUrl + pageLink.get('href'))
            else:
                print(f"Failed to retrieve the web page for page {page}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
    return linkList

if __name__ == "__main__":
    starting_url = "https://999.md/ru/list/real-estate/apartments-and-rooms?o_30_241=894&applied=1&eo=12900&eo=12912&eo=12885&eo=13859&ef=32&ef=33&o_33_1=7762912&eo=12885&eo=13859&ef=32&ef=33&o_33_1=776"
    parsed_urls = parseLinks(starting_url, maxPages=1)

    with open("parsed_urls.json", "w") as json_file:
        json.dump(parsed_urls, json_file, indent=4)

    for url in parsed_urls:
        print(url)
