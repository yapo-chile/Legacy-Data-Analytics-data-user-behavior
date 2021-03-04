# -*- coding: utf-8 -*-
import os
import psycopg2
from .infraestructure.psql import Database

TABLE = "ods.pi_inmo_daily"


class BasePipeline(object):
    def process_item(self, item, spider):
        return item


class PsqlPipeline(object):
    def open_spider(self, spider):
        self.cur = Database(spider.conf)

    def close_spider(self, spider):
        self.cur.close_connection()

    def pi_query(self, item):
        return """UPDATE {}
            set status='disabled',
            last_revision=now() where id='{}' and url='{}';""".format(TABLE,
                                                                 item.get('id'),
                                                                 item.get('url'))

    def process_item(self, item, spider):
        try:
            self.cur.execute_command(self.pi_query(item))
        except:
            print("ERROR ON ITEM: {}".format(item))
        return item
