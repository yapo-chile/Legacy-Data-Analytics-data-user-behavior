# pylint: disable=no-member
# utf-8
import sys
import logging
import environ
from infraestructure.conf import AppConfig
from infraestructure.psql import Database
from interfaces.api_request import get_nps
from interfaces.read_params import ReadParams
from interfaces.time_execution import TimeExecution


if __name__ == '__main__':
    CONFIG = environ.to_config(AppConfig)
    TIME = TimeExecution()
    LOGGER = logging.getLogger('content-evasion-moderation')
    DATE_FORMAT = """%(asctime)s,%(msecs)d %(levelname)-2s """
    INFO_FORMAT = """[%(filename)s:%(lineno)d] %(message)s"""
    LOG_FORMAT = DATE_FORMAT + INFO_FORMAT
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    PARAMS = ReadParams(sys.argv)
    URL_GET = CONFIG.zendesk.survey_link_prefix \
              + CONFIG.zendesk.survey_id \
              + CONFIG.zendesk.survey_link_sufix
    DATA_NPS = get_nps(URL_GET, CONFIG.zendesk.authorization)
    DB_WRITE = Database(CONFIG.db.host,
                        CONFIG.db.port,
                        CONFIG.db.name,
                        CONFIG.db.user,
                        CONFIG.db.password)
    TRUNCATE_TABLE = """ truncate table """ + CONFIG.db.table
    DB_WRITE.execute_command(TRUNCATE_TABLE)
    DB_WRITE.insert_nps_dw(CONFIG.db.table,
                           DATA_NPS)
    DB_WRITE.close_connection()
    TIME.get_time()
    LOGGER.info('Process ended successed.')
