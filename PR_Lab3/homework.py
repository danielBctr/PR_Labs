import requests
from bs4 import BeautifulSoup
from in_class import parseLinks
import json

def extractAppInfoFromPage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        info = {}

        titles = ['Caracteristici', 'Condiții de utilizare', 'Adăugător', 'Preț', 'Regiunea', 'Contacte']

        for title in titles:
            section = soup.find('h2', string=title)
            if not section and title not in ['Preț', 'Regiunea', 'Contacte']:
                continue

            info[title] = {}
            if title == 'Preț':
                currencies = {'€': 'Euro', 'lei': 'Lei', '$': 'USD'}
                for li in soup.select('.adPage__content__price-feature__prices li:not(.tooltip)'):
                    currency = li.select_one('.adPage__content__price-feature__prices__price__currency').text.strip()
                    value = li.select_one('.adPage__content__price-feature__prices__price__value').text.strip()
                    info[title][currencies.get(currency, currency)] = value
            elif title == 'Regiunea':
                info[title] = ' '.join([v.text.strip() for v in soup.findAll('dd', {'itemprop': 'address'})])
            elif title == 'Contacte':
                value = soup.find('dt', string=title + ': ')
                info[title] = None if not value else value.find_next('dd').select_one('li a')['href']
            else:
                info[title] = {}
                key_selector = '.adPage__content__features__key' if title != 'Condiții de utilizare' else '.adPage__content__features__key.with-rules'
                for li in section.find_next('ul').select('li.m-value, li.m-no_value'):
                    key = li.select_one(key_selector).text.strip()
                    value = li.select_one('.adPage__content__features__value').text.strip() if title == 'Caracteristici' else None
                    info[title][key] = value

        return info

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def extractAndSaveAppDetails(urls, limit=5):
    app_details_list = []

    for url in urls[:limit]:
        try:
            car_info = extractAppInfoFromPage(url)
            if car_info:
                app_details_list.append(car_info)
                print(f"Apartments details extracted for {url}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the request: {e}")

    with open("app_details.json", "w", encoding="utf-8") as json_file:
        json.dump(app_details_list, json_file, ensure_ascii=False, indent=4)
    print(f"Apartments details saved to car_details.json")

if __name__ == "__main__":
    starting_url = "https://999.md/ru/list/real-estate/apartments-and-rooms?o_30_241=894&applied=1&eo=12900&eo=12912&eo=12885&eo=13859&ef=32&ef=33&o_33_1=776"
    parsed_urls = parseLinks(starting_url, maxPages=1)

    extractAndSaveAppDetails(parsed_urls, limit=5)
