# utf-8
import json
import logging
import pandas as pd
import requests
from unidecode import unidecode
from infraestructure.conf import getConf
from utils.read_params import ReadParams


class ApiRequest:
    """
    Class that store all querys
    """
    def __init__(self,
                 conf: getConf,
                 params: ReadParams) -> None:
        self.params = params
        self.conf = conf
        self.logger = logging.getLogger('api-request')
        date_format = """%(asctime)s,%(msecs)d %(levelname)-2s """
        info_format = """[%(filename)s:%(lineno)d] %(message)s"""
        log_format = date_format + info_format
        logging.basicConfig(format=log_format, level=logging.INFO)

    def get_categories(self, extra_path: str=None) -> pd.DataFrame:
        """
        Method that get data from api.mercadolibre.
        Also transform request into dict.
        """
        if extra_path is None:
            self.logger.error('extra_path variable is None.')
            return pd.DataFrame()
        url_request: str = self.conf.api.url + \
                           '/sites/' + \
                           self.conf.api.site + \
                           '/' + \
                           extra_path
        headers = {"Accept": "application/json",
                   "Cache-Control": "no-cache",
                   "Pragma": "no-cache"}
        self.logger.info('Apply GET to %s', url_request)
        response = requests.get(url_request, headers=headers)
        self.logger.info('Send response GET from %s', url_request)
        if response.status_code == 200:
            return pd.DataFrame(response.json())            
        else:
            self.logger.error('Send responde GET Status code : %s', \
                             response.status_code)
            return pd.DataFrame()

    def get_category(self, category_id: str=None) -> json:
        """
        Method that get data from api.mercadolibre.
        Also transform request into dict.
        """
        if category_id is None:
            self.logger.error('category_id variable is None.')
            return json.dumps({})
        url_request: str = self.conf.api.url + \
                           '/categories/' + \
                           category_id
        headers = {"Accept": "application/json",
                   "Cache-Control": "no-cache",
                   "Pragma": "no-cache"}
        self.logger.info('Apply GET to %s', url_request)
        response = requests.get(url_request, headers=headers)
        self.logger.info('Send response GET from %s', url_request)
        if response.status_code == 200:
            return response.json()
        else:
            self.logger.error('Send responde GET Status code : %s', \
                             response.status_code)
            return json.dumps({})

    def get_search_subcategory(self,
                               subcategory_id: str = None,
                               offset: int = 0) -> json:
        """
        Method that get data from api.mercadolibre.
        Also transform request into dict.
        """
        if subcategory_id is None:
            self.logger.error('subcategory_id variable is None.')
            return json.dumps({})
        url_request: str = self.conf.api.url + \
                           '/sites/' + \
                           self.conf.api.site + \
                           '/search?category=' + \
                           subcategory_id + \
                           '&limit=50&offset=' + str(offset)
        headers = {"Accept": "application/json",
                   "Cache-Control": "no-cache",
                   "Pragma": "no-cache"}
        self.logger.info('Apply GET to %s', url_request)
        response = requests.get(url_request, headers=headers)
        self.logger.info('Send response GET from %s', url_request)
        if response.status_code == 200:
            return response.json()
        else:
            self.logger.error('Send responde GET Status code : %s', \
                             response.status_code)
            return json.dumps({})
