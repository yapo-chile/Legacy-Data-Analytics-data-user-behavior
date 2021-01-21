import scrapy
import logging
from scrapy.http import Request
from datetime import datetime
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from core.monitoring.total import MonitorTotal

class PISpider(scrapy.Spider):
    name = "monitor_total"
    allowed_domains = ['www.portalinmobiliario.com']
    url_base = 'https://www.portalinmobiliario.com'
    custom_settings = {
        'METAREFRESH_IGNORE_TAGS': ['noscript'], # PI utiliza un tag de meta refresh dentro de un tag noscript para bloquear scrappers que debemos ignorar.
        'ITEM_PIPELINES': {
            'core.pipelines.BasePipeline': 400
        }
    }
    total_ads = 0

    start_urls = [
        "{}/venta".format(url_base),
        "{}/arriendo".format(url_base),
    ]
    no_scrap = False #No scrapping, only crawling

    def parse(self, response):
        quantity_results = int(response.css('.ui-search-search-result__quantity-results::text').get().strip().split()[0].replace('.',''))
        self.total_ads += quantity_results
        logging.debug("Visiting: " + response.url + " (Qty: " + str(quantity_results) + ")")
        if quantity_results == self.total_ads:
            monitor = MonitorTotal(self.date_start)
        else:
            monitor = MonitorTotal(self.date_start, self.total_ads)
        monitor.check(quantity_results, str(response.url.split('/')[-1]).capitalize())