# -*- coding: utf-8 -*-
import psycopg2
from datetime import datetime
from .conf import getConf
from scrapy.exporters import CsvItemExporter
from core.items.chileauto.dealers import CarItem, DealerItem


class CorePipeline(object):
    def process_item(self, item, spider):
        return item


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

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):
        self.cur.execute(item['query'])
        self.connection.commit()
        del item['query']
        return item


class ChileAutosDealerPipeline(object):
    # Since this is a custom pipeline, would be using a custom name as well
    def open_spider(self, spider):
        dealersFile = open('cha_dealers.csv', 'wb')
        self.dealersExporter = CsvItemExporter(dealersFile)
        self.dealersExporter.fields_to_export = ['id', 'nombre', 'num_avisos', 'direccion', 'telefono', 'url']
        self.dealersExporter.start_exporting()

        carsFile = open('cha_cars.csv', 'wb')
        self.carsExporter = CsvItemExporter(carsFile)
        self.carsExporter.fields_to_export = ['id_seller', 'id', 'patente', 'titulo', 'precio', 'kilometros', 'url']
        self.carsExporter.start_exporting()

    def close_spider(self, spider):
        self.dealersExporter.finish_exporting()
        self.carsExporter.finish_exporting()

    def process_item(self, item, spider):
        if isinstance(item, DealerItem):
            self.dealersExporter.export_item(item)
        
        if isinstance(item, CarItem):
            self.carsExporter.export_item(item)

        return item