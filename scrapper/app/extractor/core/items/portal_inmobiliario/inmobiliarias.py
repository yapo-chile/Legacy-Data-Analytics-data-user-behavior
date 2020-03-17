import scrapy


class Inmobiliarias(scrapy.Item):
    comuna_nombre = scrapy.Field()
    comuna_total_ads = scrapy.Field()
    inmobiliaria_nombre = scrapy.Field()
    inmobiliaria_url_view = scrapy.Field()
    inmobiliaria_url = scrapy.Field()
    pass