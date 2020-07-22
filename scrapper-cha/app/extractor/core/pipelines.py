# -*- coding: utf-8 -*-
import psycopg2
from datetime import datetime
from .conf import getConf
from core.items.chileauto.dealers import CarItem, DealerItem

CARS_TABLE = "ods.cha_cars"
DEALERS_TABLE = "ods.cha_dealers"

class PsqlPipeline(object):
    def open_spider(self, spider):
        db = getConf().db
        db_config = {"host": db.host,
                     "port": db.port,
                     "user": db.user,
                     "password": db.password,
                     "database": db.name}
        self.connection = psycopg2.connect(**db_config)
        self.cur = self.connection.cursor()
        self.cur.execute("TRUNCATE {}".format(CARS_TABLE))
        self.cur.execute("TRUNCATE {}".format(DEALERS_TABLE))

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def dealer_query(self, item):
        return """INSERT INTO {}
            (id, dealer_name, phone, adress, ads, url)
            VALUES('{}', '{}', '{}', '{}', {}, '{}');
        """.format(DEALERS_TABLE,
                   item['id'],
                   item['nombre'],
                   item['telefono'],
                   item['direccion'],
                   item['num_avisos'],
                   item['url'])
    
    def cars_query(self, item):
        return """INSERT INTO {}
            (id, id_seller, plate, url, title, price, kilometers)
            VALUES('{}', '{}', '{}', '{}', '{}', {}, {});
            ;
        """.format(CARS_TABLE,
                   item['id'],
                   item['id_seller'],
                   '',
                   item['url'],
                   item['titulo'],
                   item['precio'],
                   item['kilometros'])

    def process_item(self, item, spider):
        if isinstance(item, DealerItem):
            self.cur.execute(self.dealer_query(item))
            self.connection.commit()

        if isinstance(item, CarItem):
            self.cur.execute(self.cars_query(item))
            self.connection.commit()
        return item
