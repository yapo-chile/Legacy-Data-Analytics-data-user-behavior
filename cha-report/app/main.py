# pylint: disable=no-member
# utf-8
import sys
import logging
from infraestructure.conf import getConf
from utils.read_params import ReadParams
from utils.time_execution import TimeExecution
from usecases.report import Report


if __name__ == '__main__':
    # Basic init config
    CONFIG = getConf()
    TIME = TimeExecution()
    LOGGER = logging.getLogger('yapesos-report')
    DATE_FORMAT = """%(asctime)s,%(msecs)d %(levelname)-2s """
    INFO_FORMAT = """[%(filename)s:%(lineno)d] %(message)s"""
    LOG_FORMAT = DATE_FORMAT + INFO_FORMAT
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    TIME.get_time()
    PARAMS = ReadParams(sys.argv)
    # Calling generate report usecase
    Report(CONFIG, PARAMS).generate()
    # End process
    LOGGER.info('Process ended successfully.')
