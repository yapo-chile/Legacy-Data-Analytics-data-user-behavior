# -*- coding: utf-8 -*-
import scrapy
import re
from core.items.portal_inmobiliario.new_ads import NewAds
import datetime

class PortalNewAdsVentaSpider(scrapy.Spider):
    name = "pi_new_ads_venta"
    allowed_domains = ["portalinmobiliario.com"]
    start_urls = (
        'http://www.portalinmobiliario.com/venta/',
    )

    def parse(self, response):
        def get_value(obj):
            value = re.findall("\d+", obj)
            return int("".join(value))

        total_arriendos = response.css(".quantity-results::text").extract()[0]
        total = get_value(total_arriendos)
        projects = response.css('a[title="Proyectos"]') \
                    .css('.filter-results-qty::text').extract()
        total_projects = get_value(projects[0])

        item = NewAds()
        item['fecha'] = str(datetime.date.today())
        item['new_ads'] = str(total_projects)
        item['used_ads'] = str(total - total_projects)
        item['marca'] = 'venta'
        return item

