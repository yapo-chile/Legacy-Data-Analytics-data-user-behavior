# -*- coding: utf-8 -*-
import scrapy
import math
from scrapy.http import Request
from core.items.portal_inmobiliario.inmobiliarias import Inmobiliarias


class InmobiliariasSpider(scrapy.Spider):
    name = "pi_inmobiliarias"
    allowed_domains = ["portalinmobiliario.com"]
    start_urls = (
        'http://www.portalinmobiliario.com/empresas/mostrar_inmobiliarias.asp',
    )

    def parse(self, response):
        num_items = response.css("td.LP-TituloResultados span::text").extract()
        total_pages = float(num_items[0]) / 30.0
        total_pages = int(math.ceil(total_pages)) + 1
        urls = ['http://www.portalinmobiliario.com/empresas/mostrar_inmobiliarias.asp?&Orden=0&Pagina=%d' %(n) for n in range(1, total_pages)]
        
        for url in urls:
            yield Request(url, callback=self.parseListing)

    def parseListing(self, response):
        for inmobiliaria in response.css("table.LP-Tabla"):
            inmobiliaria_view = inmobiliaria.css('td.LP-Nombre a::attr(href)').extract()[0]
            inmobiliaria_nombre = inmobiliaria.css("td.LP-Nombre a::text").extract()[0]
            inmobiliaria_url_view = "http://www.portalinmobiliario.com" + inmobiliaria_view
            inmobiliaria_url = "http://www.portalinmobiliario.com/empresas/broker_fic.asp?" + inmobiliaria_view.split("?")[1]
            data = {
                'inmobiliaria_nombre': inmobiliaria_nombre,
                'inmobiliaria_view': inmobiliaria_view,
                'inmobiliaria_url_view': inmobiliaria_url_view,
                'inmobiliaria_url': inmobiliaria_url
            }
            yield Request(inmobiliaria_url, meta=data, callback=self.parseView)
            
    def parseView(self, response):
        dict_comunas = {}
        inmobiliaria_eid = int(response.meta['inmobiliaria_view'].split('/Empresas/ficha.asp?MenuID=pry_emp&Eid=')[1])
        inmobiliaria = {
            inmobiliaria_eid : {
                'inmobiliaria_nombre': response.meta['inmobiliaria_nombre'],
                'inmobiliaria_view': response.meta['inmobiliaria_view'],
                'inmobiliaria_url_view': response.meta['inmobiliaria_url_view'],
                'inmobiliaria_url': response.meta['inmobiliaria_url']
            }
        }
        texto_comunas = response.css('table')[3]
        for texto_comuna in texto_comunas.css("tr"):
            lista_comuna = texto_comuna.css('font::text').extract()
            if (len(lista_comuna) > 1):
                if inmobiliaria_eid not in dict_comunas:
                    dict_comunas[inmobiliaria_eid] = {}
        for texto_comuna in texto_comunas.css("tr"):
            lista_comuna = texto_comuna.css('font::text').extract()
            if (len(lista_comuna) > 1):
                comuna = lista_comuna[0].split(',')
                comuna_nombre = comuna[len(comuna)-1]
                if comuna_nombre not in dict_comunas[inmobiliaria_eid]:
                    dict_comunas[inmobiliaria_eid][comuna_nombre] = 1
                else:
                    dict_comunas[inmobiliaria_eid][comuna_nombre] += 1

        for com in dict_comunas[inmobiliaria_eid]:
            item = Inmobiliarias()
            item["comuna_nombre"] = com.encode('utf8').strip()
            item["comuna_total_ads"] = dict_comunas[inmobiliaria_eid][com]
            item["inmobiliaria_nombre"] = inmobiliaria[inmobiliaria_eid]['inmobiliaria_nombre'].encode('utf8').strip()
            item["inmobiliaria_url_view"] = inmobiliaria[inmobiliaria_eid]['inmobiliaria_url_view'].strip()
            item["inmobiliaria_url"] = inmobiliaria[inmobiliaria_eid]['inmobiliaria_url'].strip()
            return item
