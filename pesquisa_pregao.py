from typing import Union
import os
from datetime import datetime
import json
import requests
import io

from zipfile import ZipFile

from loguru import logger


class PesquisaPregao():
    """
        Downloads clearing files from B3(São Paulo's stock exchange)
        Params:
            * report_date_dict: Dictionary containing:
                * (str) report name as key
                * (datetime or str) date in the format "dd/mm/yyyy" as value
    """
    def __init__(self, report_date_dict:'dict[str, Union[str, datetime]]'):
        clearing_files_path = os.path.join(os.path.dirname(__file__), './data/clearing_file.json')
        with open(clearing_files_path) as file:
            self.__CLEARING_FILENAMES__:'dict[str, str]' = json.load(file)
            
        
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
            del report_date_dict[inconsistent_report] # Deleting inconsistent parameters

        self.selected_reports = report_date_dict

    def download(self, directory_path:str):
        """
            Downloads and saves directories(named as report_id+date(yymmdd)) containing the reports files.
            Params:
                * (str) directory_path: The directory to which the reports will be download.
        """
        url_args = ''
        for report_name in self.selected_reports:
            url_args += self.__CLEARING_FILENAMES__[report_name.lower()].format(
                YYMMDD= self.selected_reports[report_name].strftime('%y%m%d')
            )
            url_args += ','

        # The request returns a compressed file as bytes
        response = requests.get('http://www.b3.com.br/pesquisapregao/download?filelist=' + url_args)

        with ZipFile(io.BytesIO(response.content), 'r') as zip_1:
            for file_name in zip_1.namelist(): # Getting a zip for each requested report
                t = zip_1.read(file_name)
                with ZipFile(io.BytesIO(t)) as report_zip:
                    report_zip.extractall(os.path.join(directory_path, file_name[:-4]))


if __name__ == '__main__':
    # test
    # a = PesquisaPregao({"mercado de derivativos - operacoes estruturadas de volatilidade" : '12/01/2022', 'Mapeamento de Grupos de Instrumentos Padronizados' : '12/01/2022', 'aab' : 'baa'})
    # a.download() #Add file path
    pass