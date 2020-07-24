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
        self.master = None
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

    def get_inital_day(self, delta) -> datetime:
        tmp_date = datetime.datetime(self.date_from.year - 1, 1, 1)
        return str((tmp_date + timedelta(days=delta)).strftime('%Y-%m-%d'))

    def get_master(self) -> str:
        """
        Method that get master attribute
        """
        return self.master

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
        # pylint: disable-all
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
        elif key == '-master':
            self.master = value
        elif key == '-deliver_to':
            self.deliver_to = value.split(',')

    def validate_params(self) -> None:
        """
        Method [ validate_params ] is method validate
        that each attribute have assign a value.
        """
        self.logger.info('Validate params.')
        current_date = datetime.datetime.now()
        if self.date_from is None:
            self.date_from = "{}-01-01".format(current_date.year)
        if self.date_to is None:
            self.date_to = current_date.strftime('%Y-%m-%d')
        if self.master is None:
            self.master = 'local'

        self.logger.info('Date from : %s', self.date_from)
        self.logger.info('Date to   : %s', self.date_to)
        self.logger.info('Current year : %s', current_date.year)
        self.logger.info('Node : %s', self.master)
