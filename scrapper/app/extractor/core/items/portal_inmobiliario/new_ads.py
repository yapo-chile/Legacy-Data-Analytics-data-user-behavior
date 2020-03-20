import scrapy


class NewAds(scrapy.Item):
    fecha = scrapy.Field()
    ads = scrapy.Field()
    marca = scrapy.Field()
    pass
