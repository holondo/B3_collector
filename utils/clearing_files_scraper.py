from bs4 import BeautifulSoup
import requests
import json
from unicodedata import normalize

import os
from datetime import datetime
import re


remove_diacritics = lambda string : normalize("NFKD", string).encode('ASCII','ignore').decode('ASCII')


def update_clearing_file_names():
    clearing_files = {}
    html_page = get_html()
    table_body = html_page.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        data = row.find_all("td", {'class' : ['text-center', 'text-left']})
        if not data:
            continue
        clearing_files[remove_diacritics(data[1].find_all('span')[0].text).lower()] = data[0].input.get('value')

    location = os.path.join(os.path.dirname(__file__), '../data', 'clearing_file.json')

    with open(location, 'w') as file:
        json.dump(clearing_files, file, indent=4)


def get_html() -> BeautifulSoup:
    response = requests.get('https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/boletins-diarios/pesquisa-por-pregao/')
    if response.status_code == 200:
        print("======================================================")
        html_page = BeautifulSoup(response.text, 'lxml')
        return html_page
    else:
        print("Deu ruim", response.status_code)
    
    return None


def get_latest_report_updates() -> 'dict[str, datetime]':
    id_to_report = {}
    reports_latest_updates = {}
    html_page = get_html()
    table_body = html_page.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        data = row.find_all("td")
        if not data:
            continue
        id_to_report[data[2].input.get('id')] = remove_diacritics(data[1].find_all('span')[0].text).lower()

    patterns = (re.compile("(\w+\.date)"), re.compile("(\d+/\d+/\d+)"))
    script = html_page.find_all('script', text=patterns[0])
    script = str(script.pop())

    for report_id, latest_update in zip(patterns[0].findall(script), patterns[1].findall(script)):
        if report_id in id_to_report:
            reports_latest_updates[id_to_report[report_id]] = datetime.strptime(latest_update, '%d/%m/%Y')

    print(reports_latest_updates)
    return reports_latest_updates


if __name__ == '__main__':
    # update_clearing_file_names()
    get_latest_report_updates()