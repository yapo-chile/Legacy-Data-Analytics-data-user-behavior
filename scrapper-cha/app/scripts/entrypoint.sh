#!/bin/sh
cd /app/extractor/core/
scrapy crawl pi_new_ads_venta
scrapy crawl pi_new_ads_arriendo
