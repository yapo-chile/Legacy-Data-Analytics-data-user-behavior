# utf-8
import logging
import pandas as pd
import requests
from unidecode import unidecode


def get_nps(api: str = None, token: str = None) -> pd.DataFrame:
    """
    Method that get data from zendesk.
    Also transform request into dict.
    """
    LOGGER = logging.getLogger('content-evasion-moderation')
    DATE_FORMAT = """%(asctime)s,%(msecs)d %(levelname)-2s """
    INFO_FORMAT = """[%(filename)s:%(lineno)d] %(message)s"""
    LOG_FORMAT = DATE_FORMAT + INFO_FORMAT
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

    if api is None or token is None:
        LOGGER.info('API or TOKEN are empty.')
        return pd.DataFrame()
    headers = {"X-Auth-Token": token,
               "Accept": "application/json",
               "Cache-Control": "no-cache",
               "Pragma": "no-cache"}
    LOGGER.info('Apply GET to %s', api)
    response = requests.get(api, headers=headers)
    LOGGER.info('Send response GET from %s', api)
    nps = response.json()
    if len(nps[0]['answers']) <= 0:
        LOGGER.info('No data found.')
        return pd.DataFrame()
    answers = []
    for j in range(len(nps[0]['answers'])):
        dict_fields = {}
        for i in nps[0]['answers'][j]['elements']:
            dict_fields[i['name']] = i['values'][0]['value']
        dict_fields['channel'] = nps[0]['answers'][j]['channel']
        dict_fields['email'] = nps[0]['answers'][j]['email']
        dict_fields['state'] = nps[0]['answers'][j]['state']
        dict_fields['startDate'] = nps[0]['answers'][j]['startDate']
        dict_fields['endDate'] = nps[0]['answers'][j]['endDate']
        dict_fields['duration'] = nps[0]['answers'][j]['duration']
        dict_fields['answerId'] = nps[0]['answers'][j]['answerId']
        answers.append(dict_fields)

    ans_df = pd.DataFrame.from_dict(answers)
    field_comments = 'Por favor, déjanos tus comentarios o sugerencias aquí'
    ans_df[field_comments] = ans_df[field_comments] \
                                .map(lambda x: (unidecode(x.lower())).strip())
    ans_df.columns = ['facil',
                      'recomendarias',
                      'rapidez',
                      'comentarios',
                      'answerid',
                      'channel',
                      'duration',
                      'email',
                      'endDate',
                      'startDate',
                      'state']
    ans_dict = ans_df.to_dict()
    return ans_dict
