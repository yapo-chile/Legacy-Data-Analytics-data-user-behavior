# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Compose, MapCompose, Join, TakeFirst
clean_text = Compose(MapCompose(lambda v: v.strip()), Join(), (lambda x: x.strip()))
uppercase_text = (lambda x: x.upper())
removepoint_text = (lambda x: x.replace(".", ""))


def clean_km(value):
    if isinstance(value, list):
        if value:
            if value[0] != 'NULL':
                value = int(str(value[0]).replace(".", ''))
                return value
    return 'NULL'

class DealerItem(scrapy.Item):
    id = scrapy.Field(output_processor=clean_text)
    nombre = scrapy.Field(output_processor=clean_text)
    telefono = scrapy.Field(output_processor=clean_text)
    direccion = scrapy.Field(output_processor=clean_text)
    num_avisos = scrapy.Field(output_processor=clean_text)
    url = scrapy.Field(output_processor=clean_text)


class CarItem(scrapy.Item):
    id = scrapy.Field(output_processor=clean_text)
    id_seller = scrapy.Field(output_processor=clean_text)
    patente = scrapy.Field(output_processor=Compose(clean_text, uppercase_text))
    url = scrapy.Field(output_processor=clean_text)
    titulo = scrapy.Field(output_processor=clean_text)
    precio = scrapy.Field(output_processor=Compose(clean_text, removepoint_text))
    kilometros = scrapy.Field(output_processor=clean_km)
