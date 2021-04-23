import scrapy
import logging
from scrapy.http import Request
from datetime import datetime
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose
from core.items.portal.ads import Ad
from core.infraestructure.conf import getConf
from core.infraestructure.psql import Database

DAYS_DELTA = 7
REVISION_DELTA = 3
LIMIT = 400


def get_urls(conf):
    db = Database(conf)
    urls = db.select_to_dict("""
        SELECT * FROM ods.pi_inmo_daily 
        where status='active'
        and insert_date <= now() - INTERVAL '{} DAY'
        and (last_revision <= now() - interval '{} DAY' 
            or last_revision is NULL)
        order by last_revision limit {};""".format(DAYS_DELTA, REVISION_DELTA, LIMIT))
    db.execute_command("""Update ods.pi_inmo_daily set last_revision=now()
        where id in ({})""".format(",".join("'{0}'".format(w) for w in urls['id'].tolist())))
    return urls


class PISpider(scrapy.Spider):
    name = "pi_cleanage"
    allowed_domains = ['www.portalinmobiliario.com']
    url_base = 'https://www.portalinmobiliario.com'
    custom_settings = {
        'METAREFRESH_IGNORE_TAGS': ['noscript'], # PI utiliza un tag de meta refresh dentro de un tag noscript para bloquear scrappers que debemos ignorar.
    }
    conf = getConf().db
    start_urls = [
        "{}/".format(url_base),
    ]
    no_scrap = False #No scrapping, only crawling

    def parse(self, response):

        for index, ad in get_urls(self.conf).iterrows():
            yield response.follow(
                url=ad['url'],
                callback=self.parseAd,
                errback=self.errback,
                cb_kwargs=dict(code=ad['id'],url=ad['url']),
                dont_filter=True,
            )
        
    def parseAd(self, response, code, url):
        if response.css('.item-title::text') or response.css('.ui-pdp-header__title-container h1::text'):
            logging.info("Ad is still active: " + response.request.url + " (" + response.url + ")") 
        else:
            logging.warning("Ad closed: " + response.request.url + " (" + response.url + ")")
            logging.info("Changing status to disabled")
            l = Ad()
            l['id'] = code
            l['url'] = url
            yield l

    def errback(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError %s on %s', response.status, response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
