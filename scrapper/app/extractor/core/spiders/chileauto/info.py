# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from core.items.chileauto.info import Info 
import re


class InfoSpider(scrapy.Spider):
    name = "chileautos_info"
    allowed_domains = ["chileautos.cl"]
    start_urls = (
        'https://www.chileautos.cl/automotoras/buscar',
    )

    def parse(self, response):
        total_automotoras = response.css("h1 span::text").extract()[0]
        total_automotoras = int(total_automotoras)
        urls = ['https://www.chileautos.cl/automotoras/buscar?s=%d' % (n) for n in range(0, total_automotoras, 20)]
        for url in urls:
            meta = {
                'url': url,
                'download_timeout': 300
            }
            yield Request(url, meta=meta, callback=self.parseListing, dont_filter=True)
#            yield Request(url, callback=self.parseListing)

    def parseListing(self, response):
        for automotora in response.css(".dealer-search-item.listing-item"):
#            auto_url = 'https://www.chileautos.cl/'+automotora.css('.listing-item__header a::attr(href)').extract()[0].split('/')[3]
            auto_url = automotora.css('.listing-item__header a::attr(href)').extract()[0]
            auto_name = automotora.css('.listing-item__header a h2::text').extract()[0]
            meta = {
                'url': auto_url,
                'name': auto_name,
                'download_timeout': 300
            }
            yield Request(auto_url, meta=meta, callback=self.parseView, dont_filter=True)

    def parseView(self, response):
        elem_ads = response.css(".page-header span::text").extract()[0]
        if 'venta' not in elem_ads:
            elem_ads = '0'
        item = Info()
        item["name"] = response.meta['name']
        item["url"] = response.meta['url']
        item["total_ads"] = int(re.search(r'\d+', elem_ads).group())
        item["phone"] = response.css('.clearfix.phoneDealer span::text').extract()
        item["contact"] = response.css('.dealer-info-details__list')[0].css('.clearfix')[1].css('div::text')[2].extract().strip()
        leng = len(response.css('.dealer-info-details__list')[1].css('.clearfix'))
        item["address"] = response.css('.dealer-info-details__list')[1].css('.clearfix')[leng-2].css('div::text')[2].extract().strip()
        return item