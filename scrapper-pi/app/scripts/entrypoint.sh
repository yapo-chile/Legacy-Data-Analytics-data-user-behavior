#!/bin/sh
DATE=$(date +%Y-%m-%d);
cd /app/extractor/core/
scrapy crawl pi -a date_start=${DATE}
scrapy crawl monitor_total -a date_start=${DATE}