# -*- coding: utf-8 -*-
import psycopg2
from datetime import datetime
from .conf import getConf
from core.items.chileauto.dealers import CarItem, DealerItem

CARS_TABLE = "ods.cha_cars"
DEALERS_TABLE = "ods.cha_dealers"
DATE = datetime.now().date()


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
        self.cur.execute("Delete from {} where \"date\"='{}'".format(CARS_TABLE, DATE))
        self.cur.execute("Delete from {} where \"date\"='{}'".format(DEALERS_TABLE, DATE))
        self.connection.commit()

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def dealer_query(self, item):
        return """INSERT INTO {}
            (id, dealer_name, phone, adress, ads, url, "date")
            VALUES('{}', '{}', '{}', '{}', {}, '{}', '{}');
        """.format(DEALERS_TABLE,
                   item['id'],
                   item['nombre'],
                   item['telefono'],
                   item['direccion'],
                   item['num_avisos'],
                   item['url'],
                   DATE)
    
    def cars_query(self, item):
        return """INSERT INTO {}
            (id, id_seller, plate, url, title, price, kilometers, "date")
            VALUES('{}', '{}', '{}', '{}', '{}', {}, {}, '{}');
        """.format(CARS_TABLE,
                   item['id'],
                   item['id_seller'],
                   '',
                   item['url'],
                   item['titulo'],
                   item['precio'],
                   item['kilometros'],
                   DATE)

    def process_item(self, item, spider):
        if isinstance(item, DealerItem):
            try:
                self.cur.execute(self.dealer_query(item))
                self.connection.commit()
            except:
                self.connection.rollback()

        if isinstance(item, CarItem):
            try:
                self.cur.execute(self.cars_query(item))
                self.connection.commit()
            except:
                self.connection.rollback()
            
        return item
