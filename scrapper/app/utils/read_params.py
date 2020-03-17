import datetime
from datetime import datetime as date_str
from datetime import timedelta
import logging


class ReadParams:
    """
    Class that allow read params by sys.
    """
    def __init__(self, str_parse_params) -> None:
        self.str_parse_params = str_parse_params
        self.date_from = None
        self.date_to = None
        self.chileautos_new_ads = None
        self.pi_new_ads_venta = None
        self.pi_new_ads_arriendo = None
        self.logger = logging.getLogger('readParams')
        date_format = """%(asctime)s,%(msecs)d %(levelname)-2s """
        info_format = """[%(filename)s:%(lineno)d] %(message)s"""
        log_format = date_format + info_format
        logging.basicConfig(format=log_format, level=logging.INFO)
        self.load_params()
        self.validate_params()

    def get_date_from(self) -> str:
        """
        Method that get date_from attribute
        """
        return self.date_from.strftime('%Y-%m-%d')

    def get_date_to(self) -> str:
        """
        Method that get date_to attribute
        """
        return self.date_to.strftime('%Y-%m-%d')

    def get_current_year(self) -> str:
        """
        Method that get current_year attribute
        """
        return str(self.date_from.year)

    def get_current_month(self) -> str:
        """
        Method that get current_month attribute
        """
        if self.date_from.month < 10:
            return '0' + str(self.date_from.month)
        return str(self.date_from.month)

    def get_current_day(self) -> str:
        """
        Method that get current_day attribute
        """
        if self.date_from.day < 10:
            return '0' + str(self.date_from.day)
        return str(self.date_from.day)

    def get_last_year(self) -> str:
        """
        Method that get last_year attribute
        """
        return str(int(self.date_from.year) - 1)

    def get_filename_scrapper(self, filename: str) -> str:
        """
        Method that get filename variable
        """
        if filename == 'CL_AUTO_NEW_ADS':
            return self.chileautos_new_ads
        if filename == 'PI_NEW_ADS_VENTA':
            return self.pi_new_ads_venta
        if filename == 'PI_NEW_ADS_ARRIENDO':
            return self.pi_new_ads_arriendo
        return None

    def get_last_year_week(self, delta: int) -> str:
        """
        Method that get last_year_week attribute
        """
        return str((self.\
                    date_from + timedelta(days=delta)).strftime('%Y-%m-%d'))

    def get_inital_day(self, delta) -> datetime:
        tmp_date = datetime.datetime(self.date_from.year - 1, 1, 1)
        return str((tmp_date + timedelta(days=delta)).strftime('%Y-%m-%d'))

    def set_date_from(self, date_from: datetime):
        """
        Method that set date_from attribute
        """
        self.date_from = date_from

    def set_date_to(self, date_to: datetime):
        """
        Method that set date_to attribute
        """
        self.date_to = date_to

    def load_params(self) -> None:
        """
        Method [ load_params ] is method that load params into each attribute.
        """
        self.logger.info('Python name : %s ', self.str_parse_params[0])
        for i in range(1, len(self.str_parse_params)):
            self.logger.info('[%s] : %s ', i, self.str_parse_params[i])
            param = self.str_parse_params[i].split("=")
            self.mapping_params(param[0], param[1])

    def mapping_params(self, key: str, value: str) -> None:
        """
        Method [ mapping_params ] is method that join attribute with key.
        Param  [ key ] is the key that be compare with
            params define for assign to attribute.
        Param  [ value ] is value that will be assign to attribute.
        """
        if key == '-date_from':
            self.date_from = date_str.strptime(value, '%Y-%m-%d').date()
        elif key == '-date_to':
            self.date_to = date_str.strptime(value, '%Y-%m-%d').date()
        elif key == '-chileautos_new_ads':
            self.chileautos_new_ads = value
        elif key == '-pi_new_ads_venta':
            self.pi_new_ads_venta = value
        elif key == '-pi_new_ads_arriendo':
            self.pi_new_ads_arriendo = value

    def validate_params(self) -> None:
        """
        Method [ validate_params ] is method validate
        that each attribute have assign a value.
        """
        self.logger.info('Validate params.')
        path_base = '/app/extractor/core/'
        current_date = datetime.datetime.now()
        if self.date_from is None:
            temp_date = current_date
            self.date_from = temp_date
        if self.date_to is None:
            temp_date = current_date
            self.date_to = temp_date
        if self.chileautos_new_ads is None:
            filename = 'chileautos_new_ads.csv'
            self.chileautos_new_ads = path_base + filename
        if self.pi_new_ads_venta is None:
            filename = 'portal_inmobiliario_new_ads_venta.csv'
            self.pi_new_ads_venta = path_base + filename
        if self.pi_new_ads_arriendo is None:
            filename = 'portal_inmobiliario_new_ads_arriendo.csv'
            self.pi_new_ads_arriendo = path_base + filename

        self.logger.info('Date from : %s', self.date_from)
        self.logger.info('Date to   : %s', self.date_to)
        self.logger.info('Current year : %s', self.get_current_year())
        self.logger.info('Last year : %s', self.get_last_year())
