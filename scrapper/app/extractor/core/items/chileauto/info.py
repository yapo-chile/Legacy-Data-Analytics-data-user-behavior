import scrapy


class Info(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    total_ads = scrapy.Field()
    phone = scrapy.Field()
    contact = scrapy.Field()
    address = scrapy.Field()
    pass