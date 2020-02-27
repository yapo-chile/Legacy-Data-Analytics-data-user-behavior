# pylint: disable=no-member
# utf-8
import json
import sys
import logging
import math
import pandas as pd
from infraestructure.conf import getConf
from infraestructure.psql import Database
from utils.api_request import ApiRequest
from utils.query import Query
from utils.read_params import ReadParams
from utils.time_execution import TimeExecution


def get_subcategory(params: ReadParams,
                    api: ApiRequest,
                    category_main_name: str,
                    subcategories: json = None):
    if subcategories is None:
        return
    else:
        df_subcategory = pd.DataFrame()
        for subcat in subcategories:
            json_subcategory = api.get_search_subcategory(subcat['id'])
            pages = math.trunc(json_subcategory['paging']['total'] / 50) + 1
            for page in range(0, pages):
                offset: int = page*50
                subcategory = api.get_search_subcategory(subcat['id'], offset)
                ads = subcategory['results']
                for ad in ads:
                    row = {'scraping_date': params.get_date_from(),
                           'category_main_name': category_main_name,
                           'category_name': subcat['name'],
                           'category_url': '',
                           'region_name': ad['address']['state_name'],
                           'region_ads': 1
                           }
                    df_subcategory = df_subcategory.append([row])
            print(df_subcategory.head())
            exit()

def source_data_subcategories(params: ReadParams,
                              api: ApiRequest,
                              data_categories: pd.DataFrame) -> pd.DataFrame():
    for index, row in data_categories.iterrows():
        detail_category = api.get_category(row['id'])
        children_categories = detail_category['children_categories']
        get_subcategory(params,
                        api,
                        row['name'],
                        children_categories)

def source_data_mercadolibre(params: ReadParams,
                             config: getConf) -> pd.DataFrame():
    api = ApiRequest(config, params)
    data_categories = api.get_categories('categories')
    source_data_subcategories(params, api, data_categories)
    return pd.DataFrame()

# Write data to data warehouse
def write_data_dwh(params: ReadParams,
                   config: getConf,
                   data_dwh: pd.DataFrame) -> None:
    query = Query(config, params)
    DB_WRITE = Database(conf=config.db)
    DB_WRITE.execute_command(query.delete_base())
    DB_WRITE.insert_data(data_dwh)
    DB_WRITE.close_connection()

if __name__ == '__main__':
    CONFIG = getConf()
    TIME = TimeExecution()
    LOGGER = logging.getLogger('mercadolibre-api')
    DATE_FORMAT = """%(asctime)s,%(msecs)d %(levelname)-2s """
    INFO_FORMAT = """[%(filename)s:%(lineno)d] %(message)s"""
    LOG_FORMAT = DATE_FORMAT + INFO_FORMAT
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    PARAMS = ReadParams(sys.argv)
    data_mercadolibre = source_data_mercadolibre(PARAMS, CONFIG)
    exit()
    DATA_DWH = source_data_dwh(PARAMS, CONFIG)
    write_data_dwh(PARAMS, CONFIG, DATA_DWH)
    TIME.get_time()
    LOGGER.info('Process ended successfully.')
