import scrapy


class NewAds(scrapy.Item):
    fecha = scrapy.Field()
    ads = scrapy.Field()
    automotora = scrapy.Field()
    particular = scrapy.Field()
    remate = scrapy.Field()
    pass