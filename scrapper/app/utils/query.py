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

    def query_pi_new_ads(self) -> str:
        """
        Method return str with query
        """
        query = """
                select *
                from 
                (
                    select max(fecha) as fecha
                    from ods.fact_portal_new_ads 
                ) t 
                inner join ods.fact_portal_new_ads pia on t.fecha = pia.fecha
            """
        return query

    def query_chileautos_new_ads(self) -> str:
        """
        Method return str with query
        """
        query = """
                select *
                from
                (
                select max(fecha) as fecha
                from ods.fact_chileautos_new_ads
                ) t
                inner join ods.fact_chileautos_new_ads cla on t.fecha = cla.fecha
            """
        return query

    def delete_pi(self) -> str:
        """
        Method that returns events of the day
        """
        command = """
                    delete from ods.fact_portal_new_ads where 
                    fecha::date = 
                    '""" + self.params.get_date_from() + """'::date """
        return command

    def delete_cl_autos(self) -> str:
        """
        Method that returns events of the day
        """
        command = """
                    delete from ods.fact_chileautos_new_ads where 
                    fecha::date = 
                    '""" + self.params.get_date_from() + """'::date """

        return command
