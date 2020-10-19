# pylint: disable=no-member
# utf-8
import logging
from infraestructure.psql import Database
from infraestructure.mindicator import Mindicator as CommoditiesRetrival
from utils.query import CommoditiesQuery


class Commodities(CommoditiesRetrival, CommoditiesQuery):

    # Query data from data warehouse
    @property
    def commodities_data(self):
        return self.__commodities_data

    @commodities_data.setter
    def commodities_data(self, attributes):
        self.__commodities_data = self.call_webservice(attributes, self.params.get_date())

    def insert_to_table(self):
        if len(self.__commodities_data[0]) > 0:
            dwh = Database(conf=self.config.db)
            dwh.execute_command(self.clean_commodities(self.params.get_date()))
            dwh.execute_command(self.clean_dollar(self.params.get_date()))
            for data in self.__commodities_data:
                if data.get('code') == 'USD':
                    dwh.execute_command(self.insert_dollar(data['date'], data['value']))
                dwh.execute_command(self.insert_commodities(data['date'], data['value'], data['code']))
            dwh.close_connection()
            self.logger.info("Commodities succesfully saved")
        else:
            self.logger.info("No data retrieved, nothing to save")

    def get_commodities(self):
        self.commodities_data = ['dolar', 'euro', 'uf']
        if bool(self.commodities_data):
            self.insert_to_table()
        return True

            


