import os
import environ


INI_ZENDESK = environ.secrets.INISecrets.from_path_in_env("APP_ZENDESK_SECRET")
INI_DB = environ.secrets.INISecrets.from_path_in_env("APP_DB_SECRET")


@environ.config(prefix="APP")
class AppConfig:
    """
    AppConfig Class representing the configuration of the application
    """

    @environ.config(prefix="ZENDESK")
    class ZendeskConfig:
        """
        ZendeskConfig class represeting the configuration to access
        Zendesk service
        """
        authorization: str = INI_ZENDESK.secret(
            name="authorization", default=environ.var())
        survey_id: str = INI_ZENDESK.secret(
            name="survey_id", default=environ.var())
        survey_link_prefix: str = environ.var(
            "https://my.surveypal.com/api/rest/survey/")
        survey_link_sufix : str = environ.var("/answers")


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
        table: str = environ.var("dm_content_sac.nps_answers")
    zendesk = environ.group(ZendeskConfig)
    db = environ.group(DBConfig)
