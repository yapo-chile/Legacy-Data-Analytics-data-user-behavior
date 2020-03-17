# pylint: disable=no-member
# utf-8
import sys
import logging
import pandas as pd
from infraestructure.conf import getConf
from infraestructure.psql import Database
from utils.query import Query
from utils.read_params import ReadParams
from utils.time_execution import TimeExecution

# Read csv file and load in pandas Dataframe
def data_from_csv(filename: str) -> pd.DataFrame:
    data_csv = pd.read_csv(filename)
    return  data_csv

# Query data from data warehouse
def source_data_dwh(params: ReadParams,
                    config: getConf):
    query = Query(config, params)
    db_source = Database(conf=config.db)
    data_pi = db_source.select_to_dict(query \
                                        .query_pi_new_ads())
    data_cla = db_source.select_to_dict(query \
                                        .query_chileautos_new_ads())
    db_source.close_connection()
    return data_pi, data_cla

#Tranformation that allow get difference between data analysis
def tranform_chileautos(data_chile_autos: pd.DataFrame,
                        data_cla: pd.DataFrame):
    ads = data_chile_autos['ads'].reset_index(drop=True)
    ads_latest = data_cla['ads'].reset_index(drop=True)
    new_column = ads[0] - ads_latest[0]
    data_chile_autos['new'] = new_column
    return data_chile_autos

#Tranformation that allow get difference between data analysis
def transform_pi(data_pi: pd.DataFrame,
                 data_pi_venta: pd.DataFrame,
                 data_pi_arriendo: pd.DataFrame):
    #venta
    df_latest_venta = data_pi.loc[data_pi['marca'] == 'venta']
    ads_venta = data_pi_venta['ads'].reset_index(drop=True)
    ads_venta_latest = df_latest_venta['ads'].reset_index(drop=True)
    new_column = ads_venta[0] - ads_venta_latest[0]
    data_pi_venta['new'] = new_column
    #arriendo
    df_latest_arriendo = data_pi.loc[data_pi['marca'] == 'arriendo']
    ads_arriendo = data_pi_arriendo['ads'].reset_index(drop=True)
    ads_arriendo_latest = df_latest_arriendo['ads'].reset_index(drop=True)
    new_column = ads_arriendo[0] - ads_arriendo_latest[0]
    data_pi_arriendo['new'] = new_column

    return data_pi_venta, data_pi_arriendo

# Write data to data warehouse
def write_data_dwh(params: ReadParams,
                   config: getConf,
                   data_pi_venta: pd.DataFrame,
                   data_pi_arriendo: pd.DataFrame,
                   data_cl_autos: pd.DataFrame) -> None:
    query = Query(config, params)
    DB_WRITE = Database(conf=config.db)
    #Load Portal inmo
    DB_WRITE.execute_command(query.delete_pi())
    DB_WRITE.insert_data_pi(data_pi_venta)
    DB_WRITE.insert_data_pi(data_pi_arriendo)
    #Load ChileAutos
    DB_WRITE.execute_command(query.delete_cl_autos())
    DB_WRITE.insert_data_cl_autos(data_cl_autos)
    DB_WRITE.close_connection()

if __name__ == '__main__':
    CONFIG = getConf()
    TIME = TimeExecution()
    LOGGER = logging.getLogger('scrapper')
    DATE_FORMAT = """%(asctime)s,%(msecs)d %(levelname)-2s """
    INFO_FORMAT = """[%(filename)s:%(lineno)d] %(message)s"""
    LOG_FORMAT = DATE_FORMAT + INFO_FORMAT
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    PARAMS = ReadParams(sys.argv)
    #Extractors
    DATA_CL_AUTOS = data_from_csv(PARAMS. \
        get_filename_scrapper('CL_AUTO_NEW_ADS'))
    DATA_PI_VENTA = data_from_csv(PARAMS. \
        get_filename_scrapper('PI_NEW_ADS_VENTA'))
    DATA_PI_ARRIENDO = data_from_csv(PARAMS. \
        get_filename_scrapper('PI_NEW_ADS_ARRIENDO'))
    DATA_PI, DATA_CLA = source_data_dwh(PARAMS, CONFIG)
    #Transformations
    DATA_PI_VENTA, DATA_PI_ARRIENDO = transform_pi(DATA_PI,
                                                   DATA_PI_VENTA,
                                                   DATA_PI_ARRIENDO)
    DATA_CL_AUTOS = tranform_chileautos(DATA_CL_AUTOS, DATA_CLA)
    #Loads
    write_data_dwh(PARAMS,
                   CONFIG,
                   DATA_PI_VENTA,
                   DATA_PI_ARRIENDO,
                   DATA_CL_AUTOS)
    TIME.get_time()
    LOGGER.info('Process ended successfully.')
