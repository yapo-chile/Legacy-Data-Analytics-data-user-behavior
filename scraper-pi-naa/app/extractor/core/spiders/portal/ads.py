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


class PISpider(scrapy.Spider):
    name = "pi_naa"
    allowed_domains = ['www.portalinmobiliario.com']
    url_base = 'https://www.portalinmobiliario.com'
    custom_settings = {
        'METAREFRESH_IGNORE_TAGS': ['noscript'], # PI utiliza un tag de meta refresh dentro de un tag noscript para bloquear scrappers que debemos ignorar.
    }
    operaciones = [
        'venta',
        'arriendo',
    ]
    venta_urls = [
        "https://www.portalinmobiliario.com/venta/_PublishedToday_YES",
    ]
    arriendo_urls = [
        "https://www.portalinmobiliario.com/arriendo/_PublishedToday_YES",
    ]
    start_urls = [
        "{}/".format(url_base),
    ]
    no_scrap = False #No scrapping, only crawling

    def parse(self, response):

        for city in self.arriendo_urls + self.venta_urls:
            yield response.follow(
                url=city,
                callback=self.parseListing,
                cb_kwargs=dict(depth=0),
                errback=self.errback,
                dont_filter=True,
            )

    def parseListing(self, response, depth):
        if response.css('.ui-search-search-result__quantity-results::text').get() is None:
            logging.warning("Retrying listing: " + response.url)
            yield response.request.replace(dont_filter=True) # Retry
        else:    
            quantity_results = int(response.css('.ui-search-search-result__quantity-results::text').get().strip().split()[0].replace('.',''))
            logging.debug("Visiting: " + response.url + " (Qty: " + str(quantity_results) + ")")

            if quantity_results > 2000: #PI muestra un maximo de 2000 avisos por listado, por lo que debemos seguir aplicando filtros.
                depth += 1
                yield from self.divideNConquer(response, quantity_results, depth)
            else:
                yield from self.parseInnerListing(response)

    def extractMenusFromSeeMore(self, response, depth):
        urls = response.css('.ui-search-search-modal-filter::attr(href)').extract()
        for url in urls:
            yield response.follow(
                url=url,
                callback=self.parseListing,
                cb_kwargs=dict(depth=depth),
                errback=self.errback,
                dont_filter=True
            )

    def getMenuSeeMore(self, response, depth):
        yield Request(
            url=response.css('.ui-search-modal__link::attr(href)').extract_first(),
            callback=self.extractMenusFromSeeMore,
            errback=self.errback,
            cb_kwargs=dict(depth=depth),
            dont_filter=True
        )

    def divideNConquer(self, response, qty, depth):
        nav_menu = response.css('.ui-search-filter-dl')
        nav_titles = response.css('.ui-search-filter-dl .ui-search-filter-dt-title::text').extract()
        print('---- NAV MENU TITLES ----')
        print(nav_titles)
        levels = ['Ciudades', #'Barrios',
                  'Inmueble', 'Modalidad',
                  'Ambientes', 'Baños', 'Superficie total']
        if depth > 4:
            levels = levels[-4:]
        logging.info("Total ads: " + str(qty))
        logging.info("Actual depth: " + str(depth))

        def findMenuAvailable(menu, levels):
            for m in levels:
                if m in menu:
                    return m
            return False

        def getMenuBody(menu_to_find, nav_menu):
            for obj in nav_menu:
                if menu_to_find in obj.extract():
                    return obj
            return False

        menuAvailable = findMenuAvailable(nav_titles, levels)
        menu = getMenuBody(menuAvailable, nav_menu)
        if qty > 2000:
            if menu and depth <= 6:
                if 'Ver todos' in menu.css('.ui-search-link::text').extract():
                    yield from self.getMenuSeeMore(menu, depth)
                else:
                    for obj in menu.css('.ui-search-link::attr(href)').extract():
                            yield scrapy.Request(
                                url=obj,
                                callback=self.parseListing,
                                cb_kwargs=dict(depth=depth),
                                errback=self.errback,
                                dont_filter=True,
                            )
            elif depth == 7:
                logging.warning("Still too big: " + response.url + " (" + str(qty) + ")")
                logging.warning("Actual URL: {}".format(obj))
                yield scrapy.Request(
                    url=obj,
                    callback=self.parseInnerListing,
                    errback=self.errback,
                    dont_filter=True,
                )
        else:
            yield scrapy.Request(
                url=obj,
                callback=self.parseInnerListing,
                errback=self.errback,
                dont_filter=True,
            )

    def parseInnerListing(self, response):
        if self.no_scrap == False:
            for item in response.css('ol.ui-search-layout--pi li'):
                adLink = item.css('a.ui-search-link::attr(href)') \
                    .re_first(r'^([^#]+)')
                if adLink:
                    yield scrapy.Request(
                        url=adLink,
                        callback=self.parseAd,
                        errback=self.errback,
                    )
        
        next_page = response.css('li.andes-pagination__button--next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(
                url=next_page, 
                callback=self.parseInnerListing,
                errback=self.errback,
                dont_filter=True,
            )
        
    def parseAd(self, response):
        if not response.css('header.item-title h1::text'):
            logging.warning("Failed to get ad: " + response.request.url + " (" + response.url + ")")
        else:
            categories = response.xpath('//*[contains(@class,"vip-navigation-breadcrumb-list")]//a[not(span)]/text()').getall()
            locations = response.xpath('//*[contains(@class,"vip-navigation-breadcrumb-list")]//a/span/text()').getall()

            def clean_string(string):
                return " ".join(string.split())
            
            def get_price(value):
                if value is not None:
                    value = float(value.replace(".", "").replace(",", "."))
                    return value
                return 0
            
            def set_default(value, default):
                if value:
                    return value
                return default

            def get_room_format(value):
                try:
                    return str(value[0][0])
                except:
                    return None

            def date_format(date):
                try:
                    datetime.strptime(date, '%Y-%m-%d')
                    return date
                except ValueError:
                    date = datetime.strptime(date, '%d-%m-%Y')
                    return date.strftime('%Y-%m-%d')

            l = Ad()
            l['codigo_propiedad'] = set_default(response.css('div.info-property-code p.info::text').extract_first(), '')
            l['fecha_publicacion'] = date_format(response.css('div.info-property-date p.info::text').extract_first())
            l['cat_1'] = clean_string(categories[0] if len(categories) > 0 else '')
            l['cat_2'] = clean_string(categories[1] if len(categories) > 1 else '')
            l['cat_3'] = clean_string(categories[2] if len(categories) > 2 else '')
            l['region'] = locations[0] if len(locations) > 0 else ''
            l['ciudad'] = locations[1] if len(locations) > 1 else ''
            l['barrio'] = locations[2] if len(locations) > 2 else ''
            l['titulo'] = clean_string(response.xpath('//header[@class="item-title"]/h1/text()').extract_first())
            l['precio_1_simbolo'] = response.xpath('//span[contains(@class,"price-tag-motors")]/span[@class="price-tag-symbol"]/text()').extract_first()
            l['precio_1_valor'] = get_price(response.xpath('//span[contains(@class,"price-tag-motors")]/span[@class="price-tag-fraction"]/text()').extract_first())
            l['precio_2_simbolo'] = response.xpath('//div[contains(@class,"price-site-currency")]/span[@class="price-tag-symbol"]/text()').extract_first()
            l['precio_2_valor'] = get_price(response.xpath('//div[contains(@class,"price-site-currency")]/span[@class="price-tag-fraction"]/text()').extract_first())
            l['superficie_total'] = clean_string(
                set_default(
                    response.xpath('//ul[contains(@class,"specs-list")]/li[strong/text() = "Superficie total"]/span/text()').extract_first(), ''
                )
            )
            l['superficie_util'] = clean_string(
                set_default(
                    response.xpath('//ul[contains(@class,"specs-list")]/li[strong/text() = "Superficie útil"]/span/text()').extract_first(), ''
                )
            )
            bedroom = response.xpath('//ul[contains(@class,"specs-list")]/li[strong/text() = "Dormitorios"]/span/text()').extract_first(),
            l['dormitorios'] = get_room_format(bedroom)
            bathroom = response.xpath('//ul[contains(@class,"specs-list")]/li[strong/text() = "Baños"]/span/text()').extract_first()
            l['banos'] = get_room_format(bathroom),
            # This could be seem as double check but sometimes it generates
            # a tuple inside a tuple
            if type(l['banos']) is tuple:
                try:
                    l['banos'] = l['banos'][0][0]
                except:
                    l['banos'] = None
            l['agencia'] = set_default(response.xpath('//p[@id="real_estate_agency"]/text()').extract_first(), '')
            l['telefonos'] = set_default(response.xpath('//span[@class="profile-info-phone-value"]/text()').extract_first(), 0)
            l['constructora'] = set_default(response.css('div.info-project-constructs p.info::text').extract_first(), '')
            l['direccion'] = response.css('div.seller-location .map-address::text').extract_first()
            l['locacion'] = response.css('div.seller-location .map-location::text').extract_first()
            l['id'] = response.css('.item-info__id-number::text').extract_first()
            l['url'] = response.url
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
