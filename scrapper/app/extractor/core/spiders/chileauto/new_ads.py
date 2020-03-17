# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
import brotli
from core.items.chileauto.new_ads import NewAds


class ChileAutosNewAdsSpider(scrapy.Spider):
    name = "chileautos_new_ads"
    start_urls = (
        'https://www.chileautos.cl/vehiculos/autos-veh%C3%ADculo/',
    )
    headers =  {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'es-419,es;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://www.google.cl/',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': 1
    }
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': headers
    }

    def parse(self, response):
        total_vehiculos = response.css("h1::text").extract()[0].split()[0].split(',')
        total_vehiculos = int((total_vehiculos[0])+(total_vehiculos[1]))

        item = NewAds()
        item['fecha'] = datetime.date.today()
        item['ads'] = str(total_vehiculos)

        def get_value(obj):
            value = re.findall("\d+", str(obj.css('span::text').extract()))
            return int("".join(value))

        for obj in response.css('div[data-aspect-name="propietario"]').css('li'):
            if obj.css('a::text').extract()[0].lower() == 'automotora':
                item['automotora'] = get_value(obj)
            if obj.css('a::text').extract()[0].lower() == 'particular':
                item['particular'] = get_value(obj)
            if obj.css('a::text').extract()[0].lower() == 'remate':
                item['remate'] = get_value(obj)
        return item
