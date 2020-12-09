# -*- coding: utf-8 -*-
import os
import psycopg2
from datetime import datetime
from .infraestructure.conf import getConf

TABLE = "ods.pi_inmo"
DATE = datetime.now().date()
os.environ['START_DATE'] = DATE.strftime("%Y-%m-%d")


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
        self.cur.execute("Delete from {} where \"date\"='{}'".format(TABLE, DATE))
        self.connection.commit()

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def pi_query(self):
        return """INSERT INTO {}
            (id, code, url, publish_date, cat_1,
            cat_2, cat_3, region, city, neighborhood,
            title, price_1_symbol, price_1_value,
            price_2_symbol, price_2_value, total_surface,
            useful_surface, bedrooms, bathrooms, agency,
            phone, adress, builder, "location", "date")
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                   %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""".format(TABLE)
    
    def pi_items(self, item):
        return (item.get('id'),
                item.get('codigo_propiedad'),
                item.get('url'),
                item.get('fecha_publicacion'),
                item.get('cat_1'),
                item.get('cat_2'),
                item.get('cat_3'),
                item.get('region'),
                item.get('ciudad'),
                item.get('barrio'),
                item.get('titulo'),
                item.get('precio_1_simbolo'),
                item.get('precio_1_valor', 0),
                item.get('precio_2_simbolo'),
                item.get('precio_2_valor', 0),
                item.get('superficie_total', ''),
                item.get('superficie_util', ''),
                item['dormitorios'],
                item['banos'],
                item.get('agencia', ''),
                item.get('telefonos'),
                item.get('direccion'),
                item.get('constructora', ''),
                item.get('locacion'),
                DATE)

    def process_item(self, item, spider):
        try:
            self.cur.execute(self.pi_query(), self.pi_items(item))
            self.connection.commit()
        except:
            print("ERROR ON ITEM: {}".format(item))   
            self.connection.rollback()
        return item
