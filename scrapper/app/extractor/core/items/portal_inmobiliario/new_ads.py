import scrapy


class NewAds(scrapy.Item):
    fecha = scrapy.Field()
    ads = scrapy.Field()
    new = scrapy.Field()
    marca = scrapy.Field()
    query = scrapy.Field()
    pass
