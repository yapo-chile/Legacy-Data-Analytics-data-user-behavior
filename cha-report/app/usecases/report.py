import os
import base64
import pandas as pd
from utils.query import DataWarehouseQuery
from utils.read_params import ReadParams
from infraestructure.psql import Database
from infraestructure.email import Email

FILENAME = "output.xlsx"


class Report():
    def __init__(self, config, params: ReadParams) -> None:
        self.config = config
        self.params = params

    @property
    def cars_data(self):
        return self.__cars_data

    @cars_data.setter
    def cars_data(self, config):
        query = DataWarehouseQuery(self.params).get_cars()
        db = Database(config)
        data = db.select_to_dict(query)
        column_names = list()
        self.__cars_data.reset_index(inplace=True)
        for i in self.__cars_data.columns:
            column_names.append(i[0] + '_' + i[1])
        self.__cars_data.columns = column_names
        db.close_connection()

        @property
        def dealers_data(self):
            return self.__dealers_data

        @dealers_data.setter
        def dealers_data(self, config):
            query = DataWarehouseQuery(self.params).get_dealers()
            db = Database(config)
            data = db.select_to_dict(query)
            column_names = list()
            self.__dealers_data.reset_index(inplace=True)
            for i in self.__dealers_data.columns:
                column_names.append(i[0] + '_' + i[1])
            self.__dealers_data.columns = column_names
            db.close_connection()

    def generate(self):
        # pylint: disable-all
        self.cars_data = self.config.db
        self.dealers_data = self.config.db

        # Generating excel file
        with pd.ExcelWriter(FILENAME) as writer: # type: ignore
            self.cars_data.to_excel(
                writer, sheet_name='cars', index=False)
            self.dealers_data.to_excel(writer,
                                  sheet_name='dealers',
                                  index=False)
        # Sending email
        data = open(FILENAME, 'rb').read()
        encoded = base64.b64encode(data).decode('UTF-8')
        email = Email(to=self.params.deliver_to,
                      subject="Chileauto weekly info",
                      message="""<h3>Buen dia, se adjunta lo solicitado.</h3>
                        <h6><i>Este mensaje fue generado de forma automatica,
                        por favor no responder</i></h6>""",
                      )
        email.attach(
            "reporte.xlsx",
            encoded,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        email.send()
        # Removing file
        os.remove("output.xlsx")
        return True
