#!/bin/sh

scrapy crawl pi_new_ads_venta -o ${PORTAL_INMO_NEWS_ADS_VENTA} -t csv
scrapy crawl pi_new_ads_arriendo -o ${PORTAL_INMO_NEWS_ADS_ARRIENDO} -t csv
