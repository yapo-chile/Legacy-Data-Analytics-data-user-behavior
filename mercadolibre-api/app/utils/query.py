from infraestructure.conf import getConf
from utils.read_params import ReadParams


class Query:
    """
    Class that store all querys
    """
    def __init__(self,
                 conf: getConf,
                 params: ReadParams) -> None:
        self.params = params
        self.conf = conf

    def delete_ml_categories_region(self) -> str:
        """
        Method that returns events of the day
        """
        command = """
                    delete from """ + self.conf.db.table_r + """ where 
                    scraping_date::date = 
                    '""" + self.params.get_date_from() + """'::date """

        return command
