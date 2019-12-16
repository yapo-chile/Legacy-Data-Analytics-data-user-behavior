import logging
import psycopg2
import psycopg2.extras
import pandas as pd


class Database:
    """
    Class that allow do operations with postgresql database.
    """
    def __init__(self, host, port, dbname, user, password):
        self.log = logging.getLogger('psql')
        date_format = """%(asctime)s,%(msecs)d %(levelname)-2s """
        info_format = """[%(filename)s:%(lineno)d] %(message)s"""
        log_format = date_format + info_format
        logging.basicConfig(format=log_format, level=logging.INFO)
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.connection = None
        self.get_connection()

    def database_conf(self):
        """
        Method that return dict with database credentials.
        """
        return {"host": self.host,
                "port": self.port,
                "user": self.user,
                "password": self.password,
                "dbname": self.dbname}

    def get_connection(self):
        """
        Method that returns database connection.
        """
        self.log.info('get_connection DB %s/%s', self.host, self.dbname)
        self.connection = psycopg2.connect(**self.database_conf())
        self.connection.set_client_encoding('UTF-8')

    def execute_command(self, command):
        """
        Method that allow execute sql commands such as DML commands.
        """
        self.log.info('execute_command : %s',
                      command.replace('\n', ' ').replace('\t', ' '))
        cursor = self.connection.cursor()
        cursor.execute(command)
        self.connection.commit()
        cursor.close()

    def select_to_dict(self, query):
        """
        Method that from query transform raw data into dict.
        """
        self.log.info('Query : %s', query.replace(
            '\n', ' ').replace('    ', ' '))
        cursor = self.connection.cursor()
        cursor.execute(query)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        cursor.close()
        return result


    def insert_nps_dw(self, table_name, data_dict: pd.DataFrame):
        self.log.info('INSERT INTO %s', table_name)
        page_size: int = 10000
        with self.connection.cursor() as cursor:
            psycopg2.extras \
                .execute_values(cursor,
                                """ INSERT INTO """ + table_name +
                                """ VALUES %s; """, ((
                                    row.facil,
                                    row.recomendarias,
                                    row.rapidez,
                                    row.comentarios,
                                    row.answerid,
                                    row.channel,
                                    row.duration,
                                    row.email,
                                    row.endDate,
                                    row.startDate,
                                    row.state,
                                    ) for row in data_dict.itertuples()),
                                page_size=page_size)
            self.log.info('insert_nps_dw COMMIT.')
            self.connection.commit()
            self.log.info('Close cursor %s', table_name)
            cursor.close()


    def close_connection(self):
        """
        Method that close connection to postgresql database.
        """
        self.log.info('Close connection DB : %s/%s', self.host, self.dbname)
        self.connection.close()
