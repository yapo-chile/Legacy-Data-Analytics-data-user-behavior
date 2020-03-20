#!/bin/sh
# python script intended to fill database on db creation
# params :
# -chileautos_new_ads
# -pi_new_ads_venta
# -pi_new_ads_arriendo

export PATH_EXTRACTOR=/app/extractor/core/
export CHILEAUTOS_NEW_ADS=${PATH_EXTRACTOR}chileautos_new_ads.csv
export CHILEAUTOS_INFO=${PATH_EXTRACTOR}chileautos_info.csv
export PORTAL_INMO_NEWS_ADS_VENTA=${PATH_EXTRACTOR}portal_inmobiliario_new_ads_venta.csv
export PORTAL_INMO_NEWS_ADS_ARRIENDO=${PATH_EXTRACTOR}portal_inmobiliario_new_ads_arriendo.csv
export PORTAL_INMO_INMOBILIARIAS=${PATH_EXTRACTOR}portal_inmobiliario_inmobiliarias.csv
export PORTAL_INMO_CORREDORAS=${PATH_EXTRACTOR}portal_inmobiliario_corredoras.csv

function FILE_EXISTS(){
    FILE=$1
    if [ -f "${FILE}" ]; then
        echo "DELETE FILE : ${FILE}"
        rm ${FILE}
    fi
}

FILE_EXISTS ${CHILEAUTOS_NEW_ADS}
FILE_EXISTS ${CHILEAUTOS_INFO}
FILE_EXISTS ${PORTAL_INMO_NEWS_ADS_VENTA}
FILE_EXISTS ${PORTAL_INMO_NEWS_ADS_ARRIENDO}
FILE_EXISTS ${PORTAL_INMO_INMOBILIARIAS}
FILE_EXISTS ${PORTAL_INMO_CORREDORAS}

echo "CHANGE DIRECTORY : ${PATH_EXTRACTOR}"
cd ${PATH_EXTRACTOR}

scrapy crawl chileautos_new_ads -o ${CHILEAUTOS_NEW_ADS} -t csv
##scrapy crawl chileautos_info -o ${CHILEAUTOS_INFO} -t csv
scrapy crawl pi_new_ads_venta -o ${PORTAL_INMO_NEWS_ADS_VENTA} -t csv
scrapy crawl pi_new_ads_arriendo -o ${PORTAL_INMO_NEWS_ADS_ARRIENDO} -t csv
##scrapy crawl pi_inmobiliarias -o ${PORTAL_INMO_INMOBILIARIAS} -t csv
##scrapy crawl pi_corredoras -o ${PORTAL_INMO_CORREDORAS} -t csv

python /app/main.py $@ \
    -chileautos_new_ads=${CHILEAUTOS_NEW_ADS} \
    -pi_new_ads_venta=${PORTAL_INMO_NEWS_ADS_VENTA} \
    -pi_new_ads_arriendo=${PORTAL_INMO_NEWS_ADS_ARRIENDO}