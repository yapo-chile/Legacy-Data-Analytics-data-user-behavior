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
