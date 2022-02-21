from typing import Union
import os
from datetime import datetime
import json
import requests

from loguru import logger


class PesquisaPregao():
    def __init__(self, report_date_dict:'dict[str, Union[str, datetime]]'):
        clearing_files_path = os.path.join(os.path.dirname(__file__), './data/clearing_file.json')
        with open(clearing_files_path) as file:
            self.__CLEARING_FILENAMES__:'dict[str, str]' = json.load(file)
            
        self.__downloaded__ = False
        
        inconsistent = []
        for report_name in report_date_dict:
            if report_name.lower() not in self.__CLEARING_FILENAMES__.keys():
                logger.warning(f'Report {report_name} does not exists, ignoring.')
                inconsistent.append(report_name)

            elif type(report_date_dict[report_name]) != datetime:
                try:
                    report_date_dict[report_name] = datetime.strptime(report_date_dict[report_name], '%d/%m/%Y')
                except ValueError as e:
                    logger.warning(f'Date format exception for report {report_name}, ignoring it.')
                    logger.warning(str(e))
                    inconsistent.append(report_name)

        for inconsistent_report in inconsistent:
            del report_date_dict[inconsistent_report]

        self.selected_reports = report_date_dict

    def download(self):
        url_args = ''
        for report_name in self.selected_reports:
            url_args += self.__CLEARING_FILENAMES__[report_name.lower()].format(
                YYMMDD= self.selected_reports[report_name].strftime('%y%m%d')
            )
            url_args += ','

        response = requests.get('http://www.b3.com.br/pesquisapregao/download?filelist=' + url_args)

        with open('teste.zip', 'wb') as file:
            file.write(response.content)
        

if __name__ == '__main__':
    # test
    a = PesquisaPregao({'Mapeamento de Grupos de Instrumentos Padronizados' : '12/01/2021', 'pao' : 'aa', 'aab' : 'baa'})
    a.download()
    pass