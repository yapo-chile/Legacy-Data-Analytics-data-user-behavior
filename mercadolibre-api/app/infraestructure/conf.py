import environ


INI_PULSE = environ.secrets.INISecrets.from_path_in_env("API_URL")
INI_DB = environ.secrets.INISecrets.from_path_in_env("APP_DB_SECRET")


@environ.config(prefix="APP")
class AppConfig:
    """
    AppConfig Class representing the configuration of the application
    """

    @environ.config(prefix="API_URL")
    class ApiConfig:
        """
        ApiConfig class represeting the configuration to access
        pulse service
        """
        url: str = INI_PULSE.secret(
            name="url", default=environ.var())
        site: str = INI_PULSE.secret(
            name="site", default=environ.var())

    @environ.config(prefix="DB")
    class DBConfig:
        """
        DBConfig Class representing the configuration to access the database
        """
        host: str = INI_DB.secret(name="host", default=environ.var())
        port: int = INI_DB.secret(name="port", default=environ.var())
        name: str = INI_DB.secret(name="dbname", default=environ.var())
        user: str = INI_DB.secret(name="user", default=environ.var())
        password: str = INI_DB.secret(name="password", default=environ.var())
        table_r: str = "dm_scraping.fact_day_mercadolibre_ads_category_region"
    api = environ.group(ApiConfig)
    db = environ.group(DBConfig)


def getConf():
    return environ.to_config(AppConfig)
