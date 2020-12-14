import os
import requests
from core.infraestructure.conf import getConf
from core.infraestructure.psql import Database
from core.pipelines import TABLE


class MonitorTotal():
    def __init__(self):
        self.conf = getConf()
        self.__date = os.environ.get('START_DATE')

    def get_total_table(self, category) -> str:
        return """
            select count(id) as total from {table} 
            where "date"='{date}'
            and cat_2 = '{category}';
        """.format(table=TABLE, date=self.__date, category=category)

    def totalized_data(self, category):
        conn = Database(conf=self.conf.db)
        totalized_data = conn.select_to_dict(self.get_total_table(category))
        conn.close_connection()
        return totalized_data

    def check(self, value, category=''):
        data = self.totalized_data(category)
        if not data.empty:
            # data['total'] refers to how many are in the db
            # value refers to how many are in website
            if int(data['total']) < int(value) * 0.85:
                slack_body = {	
                    'attachments': [
                        {
                            'fallback': "Required plain-text summary of the attachment.",
                            'color': "#cc0000",
                            'pretext': "Error en job Scraper de Portal Inmo",
                            'author_name': "Rundeck",
                            'title': "Job Fallido",
                            'title_link': "http://3.94.225.3:4440/project/data_jobs/job/show/aa09a545-614a-44cd-a30f-dcf7987b9e5a",
                            'text': "El job de Scraper de Portal Inmo tiene irregularidades en la data, tiene {} registros de {}, fecha {} y categoria {}".format(int(data['total']),
                                                                                                                                                                  value,
                                                                                                                                                                  self.__date,
                                                                                                                                                                  category),
                            'fields': [
                                {
                                    'title': "Priority",
                                    'value': "High",
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
                return False
        return True
