import scrapy
from scrapy.loader.processors import Compose, MapCompose, Join
clean_text = Compose(MapCompose(lambda v: v.strip().replace('\r\n', ' ')), Join())


class Ad(scrapy.Item):
    id = scrapy.Field(output_processor=clean_text)
    url = scrapy.Field(output_processor=clean_text)