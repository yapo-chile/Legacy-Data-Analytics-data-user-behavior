# pylint: disable=no-member
# utf-8


class CommoditiesQuery:

    def clean_commodities(self, date) -> str:
        return """delete from stg.currency
                    where date_time::date = '{}'::date""".format(date)

    def clean_dollar(self, date) -> str:
        return """delete from stg.dolar_values
                    where "date"::date = '{}'::date""".format(date)

    def insert_dollar(self, date, value) -> str:
        return """ INSERT INTO stg.dolar_values
                    ("date", value)
                    VALUES('{}', {});
                """.format(date, value)
    
    def insert_commodities(self, date, value, currency) -> str:
        return """INSERT INTO stg.currency
                    (date_time, "money", value)
                    VALUES('{}', '{}', {});
                """.format(date, currency, value)