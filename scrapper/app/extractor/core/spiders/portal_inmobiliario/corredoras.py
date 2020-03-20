# -*- coding: utf-8 -*-
import scrapy
import math
from scrapy.http import Request
from core.items.portal_inmobiliario.corredoras import Corredoras


class CorredorasSpider(scrapy.Spider):
    name = "pi_corredoras"
    allowed_domains = ["portalinmobiliario.com"]
    start_urls = (
        'https://www.portalinmobiliario.com/empresas/corredoraspresentes.aspx',
    )

    def parse(self, response):
        num_items = response.css("#ContentPlaceHolder1_lblNumeroCorredorasPresentes::text").extract()
        print("num_items: %s" % num_items[0])
        total_pages = float(num_items[0]) / 15.0
        total_pages = int(math.ceil(total_pages)) + 1
        print("total pages: {0}".format(total_pages))
        urls = ['https://www.portalinmobiliario.com/empresas/corredoraspresentes.aspx?p=%d' %(n) for n in range(1, total_pages)]
        for url in urls:
            yield Request(url, callback=self.parseListing)

    def parseListing(self, response):
        for corredora in response.css("tr[id*=ContentPlaceHolder1_ListViewCorredorasPresentes_ctr] td"):
            corredora_view = corredora.css('a::attr(href)').extract()[0]
            corredora_nombre = corredora.css("a img::attr(title)").extract()[0]
            corredora_url_view = "https://www.portalinmobiliario.com" + corredora_view
            corredora_url = "https://www.portalinmobiliario.com/propiedades/broker_fic.asp?" + corredora_view.split("?")[1]
            data = {
                'corredora_nombre': corredora_nombre,
                'corredora_url_view': corredora_url_view,
                'corredora_url': corredora_url
            }
            yield Request(corredora_url, meta=data, callback=self.parseView)
            
    def parseView(self, response):
        corredora_nombre = response.meta['corredora_nombre']
        corredora_url_view = response.meta['corredora_url_view']
        corredora_url = response.meta['corredora_url']
        for comuna in response.css("table td [href*='Buscar_resp']"):
            comuna_nombre = comuna.css('a::text').extract()[0]
            comuna_url =  comuna.css('a::attr(href)').extract()[0]
            comuna_url = "https://www.portalinmobiliario.com" + comuna_url.replace("..", "")
            data = {
                'corredora_nombre': corredora_nombre,
                'corredora_url_view': corredora_url_view,
                'corredora_url': corredora_url,
                'comuna_nombre': comuna_nombre,
                'comuna_url': comuna_url
            }
            yield Request(comuna_url, meta=data, callback=self.parseComuna)

    def parseComuna(self, response):
        num_items = response.css("#tableListadoPropiedades .RGBPaginacionFilaGris > td:nth-child(1) > b::text").extract()[0]
        num_items = num_items.replace("\r\n", "")
        num_items = num_items.replace(",", "")
        totals = [int(s) for s in num_items.split() if s.isdigit()]

        item = Corredoras()
        item["corredora_url_view"] = response.meta['corredora_url_view'].strip()
        item["comuna_url"] = response.meta['comuna_url'].strip()
        item["comuna_total_ads"] = totals[0]
        item["comuna_nombre"] = response.meta['comuna_nombre'].encode('utf8').strip()
        item["corredora_url"] = response.meta['corredora_url'].strip()
        item["corredora_nombre"] = response.meta['corredora_nombre'].encode('utf8').strip()
        return item
