import scrapy


class Corredoras(scrapy.Item):
    corredora_url_view = scrapy.Field()
    comuna_url = scrapy.Field()
    comuna_total_ads = scrapy.Field()
    comuna_nombre = scrapy.Field()
    corredora_url = scrapy.Field()
    corredora_nombre = scrapy.Field()
