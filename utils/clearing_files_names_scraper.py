from bs4 import BeautifulSoup
import requests
import json
from unicodedata import normalize

import os

def main():
    remove_diacritics = lambda string : normalize("NFKD", string).encode('ASCII','ignore').decode('ASCII')
    clearing_files = {}
    response = requests.get('https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/boletins-diarios/pesquisa-por-pregao/')
    html_page = BeautifulSoup(response.text, 'lxml')
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

if __name__ == '__main__':
    main()