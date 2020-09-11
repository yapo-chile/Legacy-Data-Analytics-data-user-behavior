import requests
from datetime import datetime

ENDPOINT='https://mindicador.cl/api'


class Mindicator():
    """
    Public indicator api: https://mindicador.cl/
    There would be documentation about other items that could be extracted
    and their historical data
    """
    
    def call_webservice(self, attributes, date=''):
        def parse_datetime(string):
            return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.000%z").date() \
                .strftime("%Y-%m-%d")

        def humanize_date(string):
            return datetime.strptime(string, "%Y-%m-%d") \
                .strftime("%d-%m-%Y")

        data = []
        for commodity in attributes:
            url = "{}/{}/{}".format(ENDPOINT, commodity, humanize_date(date))
            resp = requests.get(url)
            if resp.status_code == 200:
                resp = resp.json()['serie'][0]
                if resp['valor'] != []:
                    if commodity == 'dolar':
                        code = 'USD'
                    elif commodity == 'uf':
                        code = commodity.upper()
                    elif commodity == 'euro':
                        code = 'EUR'
                    data.append({"value": resp['valor'],
                                "date": parse_datetime(resp['fecha']),
                                "code": code})
        return data