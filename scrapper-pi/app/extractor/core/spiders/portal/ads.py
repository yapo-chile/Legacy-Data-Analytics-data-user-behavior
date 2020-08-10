import scrapy
import logging
from datetime import datetime
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose
from core.items.portal.ads import Ad


class PISpider(scrapy.Spider):
    name = "pi"
    allowed_domains = ['www.portalinmobiliario.com']
    url_base = 'https://www.portalinmobiliario.com'
    custom_settings = {
        'METAREFRESH_IGNORE_TAGS': ['noscript'], # PI utiliza un tag de meta refresh dentro de un tag noscript para bloquear scrappers que debemos ignorar.
    }
    operaciones = [
        'venta',
        'arriendo',
    ]
    no_scrap = False #No scrapping, only crawling

    def start_requests(self):
        yield scrapy.Request(
            url=self.url_base,
            callback=self.startProcessing,
        )

    def startProcessing(self, response):
        for operacion in self.operaciones:
            yield response.follow(
                url='/' + operacion,
                callback=self.parseListing, 
                errback=self.errback,
                cb_kwargs=dict(depth=0),
                dont_filter=True,
            )

    def parseListing(self, response, depth):
        if response.css('.quantity-results::text').get() is None:
            logging.warning("Retrying listing: " + response.url)
            yield response.request.replace(dont_filter=True) # Retry
        else:    
            quantity_results = int(response.css('.quantity-results::text').get().strip().split()[0].replace('.',''))
            logging.debug("Visiting: " + response.url + " (Qty: " + str(quantity_results) + ")" + "(Depth: " + str(depth) + ")")

            if quantity_results > 2000: #PI muestra un maximo de 2000 avisos por listado, por lo que debemos seguir aplicando filtros.
                yield from self.divideNConquer(response, depth, quantity_results)
            else:
                yield from self.parseInnerListing(response)

    def divideNConquer(self, response, depth, qty):
        if depth == 0:  # Navigate by inmueble (departamente, casa, terreno, etc.)
            logging.info("Total ads: " + str(qty))

            if response.xpath('//*[@id="id_9991459-AMLC_1459_1"]').get() is None: # Pasamos el siguiente nivel si el filtro no existe
                depth += 1
                yield from self.divideNConquer(response, depth, qty)
            else:
                if response.xpath('//*[@id="id_9991459-AMLC_1459_1"]//label[contains(@class,"see-more-filter")]').get() is None:
                    urls = response.xpath('//*[@id="id_9991459-AMLC_1459_1"]//h3/a/@href')
                else:
                    urls = response.xpath('//*[@id="id_9991459-AMLC_1459_1"]//*[contains(@class,"modal-content")]//h3/a/@href')

                for url in urls:
                    yield scrapy.Request(
                        url=url.get(),
                        callback=self.parseListing,
                        errback=self.errback,
                        cb_kwargs=dict(depth=1),
                        dont_filter=True,
                    )
        elif depth == 1: # Navigate by modalidad (usada o nueva)
            if response.xpath('//*[@id="id_9991459-AMLC_1459_3"]//h3/a/@href').get() is None: # Pasamos el siguiente nivel si el filtro no existe
                depth += 1
                yield from self.divideNConquer(response, depth, qty)
            else:
                for url in response.xpath('//*[@id="id_9991459-AMLC_1459_3"]//h3/a/@href'):
                    yield scrapy.Request(
                        url=url.get(),
                        callback=self.parseListing,
                        errback=self.errback,
                        cb_kwargs=dict(depth=2),
                        dont_filter=True,
                    )
        elif depth == 2: # Navigate by region
            if response.xpath('//*[@id="id_state"]').get() is None: # Pasamos el siguiente nivel si el filtro no existe
                depth += 1
                yield from self.divideNConquer(response, depth, qty)
            else:
                if response.xpath('//*[@id="id_state"]//label[contains(@class,"see-more-filter")]').get() is None:
                    urls = response.xpath('//*[@id="id_state"]//h3/a/@href')
                else:
                    urls = response.xpath('//*[@id="id_state"]//*[contains(@class,"modal-content")]//dd/a/@href')

                for url in urls:
                    yield scrapy.Request(
                        url=url.get(),
                        callback=self.parseListing, 
                        errback=self.errback,
                        cb_kwargs=dict(depth=3),
                        dont_filter=True,
                    )
        elif depth == 3: # Navigate by city
            if response.xpath('//*[@id="id_city"]').get() is None: # Pasamos el siguiente nivel si el filtro no existe
                depth += 1
                yield from self.divideNConquer(response, depth, qty)
            else:
                if response.xpath('//*[@id="id_city"]//label[contains(@class,"see-more-filter")]').get() is None:
                    urls = response.xpath('//*[@id="id_city"]//h3/a/@href')
                else:
                    urls = response.xpath('//*[@id="id_city"]//*[contains(@class,"modal-content")]//div/a/@href')

                for url in urls:
                    yield scrapy.Request(
                        url=url.get(),
                        callback=self.parseListing, 
                        errback=self.errback,
                        cb_kwargs=dict(depth=4),
                        dont_filter=True,
                    )
        elif depth == 4: # Navigate by price
            if response.xpath('//*[@id="id_price"]').get() is None: # Pasamos el siguiente nivel si el filtro no existe
                depth += 1
                yield from self.divideNConquer(response, depth, qty)
            else:
                for url in response.xpath('//*[@id="id_price"]//dd/a/@href'):
                    yield scrapy.Request(
                        url=url.get(),
                        callback=self.parseListing, 
                        errback=self.errback,
                        cb_kwargs=dict(depth=5),
                        dont_filter=True,
                    )
        elif depth == 5: # Navigate by superficie total
            if response.xpath('//*[@id="id_TOTAL_AREA"]').get() is None: # Pasamos el siguiente nivel si el filtro no existe
                depth += 1
                yield from self.divideNConquer(response, depth, qty)
            else:
                for url in response.xpath('//*[@id="id_TOTAL_AREA"]//dd/a/@href'):
                    yield scrapy.Request(
                        url=url.get(),
                        callback=self.parseListing, 
                        errback=self.errback,
                        cb_kwargs=dict(depth=6),
                        dont_filter=True,
                    )
        elif depth == 6: # Navigate by baños
            if response.xpath('//*[@id="id_FULL_BATHROOMS"]').get() is None: # Pasamos el siguiente nivel si el filtro no existe
                depth += 1
                yield from self.divideNConquer(response, depth, qty)
            else:
                for url in response.xpath('//*[@id="id_FULL_BATHROOMS"]//dd/a/@href'):
                    yield scrapy.Request(
                        url=url.get(),
                        callback=self.parseListing, 
                        errback=self.errback,
                        cb_kwargs=dict(depth=7),
                        dont_filter=True,
                    )
        else:
            logging.warning("Still too big: " + response.url + " (" + str(qty) + ")" + "(" + str(depth) + ")")

    def parseInnerListing(self, response):
        if self.no_scrap == False:
            for item in response.xpath('//section[@id="results-section"]/ol/li'):
                adLink = item.css('a.item__info-link::attr(href)').re_first(r'^([^#]+)')
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

        if response.xpath('//header[@class="item-title"]/h1/text()').get() is None:
            logging.warning("Failed to get ad: " + response.request.url + " (" + response.url + ")")
        else:
            categories = response.xpath('//*[contains(@class,"vip-navigation-breadcrumb-list")]//a[not(span)]/text()').getall()
            locations = response.xpath('//*[contains(@class,"vip-navigation-breadcrumb-list")]//a/span/text()').getall()

            def clean_string(string):
                return " ".join(string.split())
            
            def get_price(value):
                if value:
                    value = int(value.replace(".", ""))
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
