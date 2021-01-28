import requests
from core.infraestructure.conf import getConf
from core.infraestructure.psql import Database
from core.pipelines import TABLE


class MonitorTotal():
    def __init__(self, date_start, total_ads=0):
        self.conf = getConf()
        self.__date = date_start
        self._total_scraped_ads = int(total_ads)

    def get_total_table(self, category) -> str:
        return """
            select count(id) as total from {table} 
            where "date"='{date}'
            and cat_2 = '{category}';
        """.format(table=TABLE, date=self.__date, category=category)
    
    def get_total_table_agg(self) -> str:
        return """
            select count(id) as total from {table} 
            where "date"='{date}';
        """.format(table=TABLE, date=self.__date)

    def totalized_data(self, category):
        conn = Database(conf=self.conf.db)
        totalized_data = conn.select_to_dict(self.get_total_table(category))
        conn.close_connection()
        return totalized_data
    
    def totalized_data_agg(self):
        conn = Database(conf=self.conf.db)
        totalized_data = conn.select_to_dict(self.get_total_table_agg())
        conn.close_connection()
        return totalized_data

    def check(self, value, category=''):
        total_ads = 0
        scraped_text = ""
        data = self.totalized_data(category)
        if self._total_scraped_ads > 0:
            total_ads = self.totalized_data_agg()
            scraped_perc = round((self._total_scraped_ads * 100) / total_ads, 2)
            scraped_text = "\n \n Total disponible {}\n Total scrapeado {}\n Porc: {}%".format(self._total_scraped_ads,
                                                                                       total_ads,
                                                                                       scraped_perc)

        if not data.empty:
            # data['total'] refers to how many are in the db
            # value refers to how many are in website
            perc = round((int(data['total']) * 100) / value, 2)

            slack_body = {	
                'attachments': [
                    {
                        'fallback': "Required plain-text summary of the attachment.",
                        'color': "#50A926",
                        'pretext': "Scraper de Portal Inmo NAA",
                        'author_name': "Rundeck",
                        'title': "Job Terminado",
                        'title_link': "http://3.94.225.3:4440/project/data_jobs/job/show/aa09a545-614a-44cd-a30f-dcf7987b9e5a",
                        'text': "Estadisticas del Scraper de Portal Inmo, tiene {} registros de {}, fecha {} y categoria {}, Perc: {}% {}".format(int(data['total']),
                                                                                                                                                                value,
                                                                                                                                                                self.__date,
                                                                                                                                                                category,
                                                                                                                                                                perc,
                                                                                                                                                                scraped_text),
                        'fields': [
                            {
                                'title': "Priority",
                                'value': "Low",
                                'short': False
                            }
                        ],
                        'footer': "Data Notificator bot"
                    }
                ]
            }
            url = 'https://hooks.slack.com/services/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'
            x = requests.post(url, json=slack_body, headers={'Content-type': 'application/json'})
            print(x.text)
            return True
