import scrapy


class NewAds(scrapy.Item):
    fecha = scrapy.Field()
    new_ads = scrapy.Field()
    used_ads = scrapy.Field()
    marca = scrapy.Field()
    pass
