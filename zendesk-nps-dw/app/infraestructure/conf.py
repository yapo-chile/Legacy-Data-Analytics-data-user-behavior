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
            name="authorization", default=None)
        survey_id: str = INI_ZENDESK.secret(
            name="survey_id", default=None)
        survey_link_prefix: str = environ.var(
            "https://my.surveypal.com/api/rest/survey/")
        survey_link_sufix = environ.var("/answers")
        if authorization is None:
            authorization = os.environ.get("ZENDESK_AUTHORIZATION")
        if survey_id is None:
            survey_id = os.environ.get("ZENDESK_SURVEY_ID")


    @environ.config(prefix="DB")
    class DBConfig:
        """
        DBConfig Class representing the configuration to access the database
        """
        host: str = INI_DB.secret(name="host", default=None)
        port: int = INI_DB.secret(name="port", default=None)
        name: str = INI_DB.secret(name="dbname", default=None)
        user: str = INI_DB.secret(name="user", default=None)
        password: str = INI_DB.secret(name="password", default=None)
        table: str = environ.var("dm_content_sac.nps_answers")
        if host is None:
            host = os.environ.get("DB_HOST")
        if port is None:
            port = os.environ.get("DB_PORT")
        if name is None:
            name = os.environ.get("DB_NAME")
        if user is None:
            user = os.environ.get("DB_USER")
        if password is None:
            password = os.environ.get("DB_PASSWORD")
    zendesk = environ.group(ZendeskConfig)
    db = environ.group(DBConfig)
