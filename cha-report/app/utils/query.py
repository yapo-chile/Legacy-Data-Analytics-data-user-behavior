from utils.read_params import ReadParams


class DataWarehouseQuery:
    """
    Class that store Datawarehouse queries
    """

    def __init__(self,
                 params: ReadParams) -> None:
        self.params = params

    def get_cars(self) -> str:
        """
        Method return str with query
        """
        query = """select
                    * from ods.cha_cars 
                    where "date" = CURRENT_DATE;"""
        return query

    def get_dealers(self):
        query = """select
                    * from ods.cha_dealers 
                    where "date" = CURRENT_DATE;"""
        return query
