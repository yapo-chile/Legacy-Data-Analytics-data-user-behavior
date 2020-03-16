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
                    subcategories: json = None) -> pd.DataFrame:
    if subcategories is None:
        return
    else:
        df_subcategory = pd.DataFrame()
        for subcat in subcategories:
            json_subcategory = api.get_search_subcategory(subcat['id'])
            pages = math.trunc(json_subcategory['paging']['total'] / 50) + 1
            # If : testing code. For production environment erase.
            if pages > 20:
                pages = 20
            # If : testing code. For production environment erase.
            for page in range(0, pages):
                offset: int = page*50
                subcategory = api.get_search_subcategory(subcat['id'], offset)
                if 'results' in subcategory:
                    ads = subcategory['results']
                    for ad in ads:
                        address = ad['address']
                        region_name = None
                        if address is not None:
                            region_name = address['state_name']
                        row = {'scraping_date': params.get_date_from(),
                            'category_main_name': category_main_name,
                            'category_name': subcat['name'],
                            'category_url': '',
                            'region_name': region_name,
                            'region_ads': 1
                            }
                        df_subcategory = df_subcategory.append([row])
            if df_subcategory.shape[0] > 0:
                df_subcategory = df_subcategory. \
                                    groupby(['scraping_date',
                                            'category_main_name',
                                            'category_name',
                                            'category_url',
                                            'region_name'],
                                            as_index=False)['region_ads'].sum()
            return df_subcategory

def source_data_subcategories(params: ReadParams,
                              api: ApiRequest,
                              data_categories: pd.DataFrame) -> pd.DataFrame():
    df_category = pd.DataFrame()
    for index, row in data_categories.iterrows():
        detail_category = api.get_category(row['id'])
        children_categories = detail_category['children_categories']
        df_subcategory = get_subcategory(params,
                                         api,
                                         row['name'],
                                         children_categories)
        df_category = df_category.append(df_subcategory, ignore_index=True)
    return df_category
        

def source_data_mercadolibre(params: ReadParams,
                             config: getConf) -> pd.DataFrame():
    api = ApiRequest(config, params)
    data_categories = api.get_categories('categories')
    data_categories_region = source_data_subcategories(params,
                                                       api,
                                                       data_categories)
    return data_categories_region

# Write data to data warehouse
def write_data_dwh(params: ReadParams,
                   config: getConf,
                   data_ml_region: pd.DataFrame) -> None:
    query = Query(config, params)
    DB_WRITE = Database(conf=config.db)
    DB_WRITE.execute_command(query.delete_ml_categories_region())
    DB_WRITE.insert_data(data_ml_region)
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
    DATA_ML_REGION = source_data_mercadolibre(PARAMS, CONFIG)
    write_data_dwh(PARAMS, CONFIG, DATA_ML_REGION)
    TIME.get_time()
    LOGGER.info('Process ended successfully.')
