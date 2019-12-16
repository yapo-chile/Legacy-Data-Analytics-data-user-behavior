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
        authorization = INI_ZENDESK.secret(
            name="authorization", default=environ.var())
        survey_id = environ.var("survey_id")
        survey_link_prefix = environ.var(
            "https://my.surveypal.com/api/rest/survey/")
        survey_link_sufix = environ.var("/answers")


    @environ.config(prefix="DB")
    class DBConfig:
        """
        DBConfig Class representing the configuration to access the database
        """
        host: str = environ.var("postgres")
        port: int = environ.var(5432)
        name = environ.var("database")
        user = environ.var("user")
        password = INI_DB.secret(name="password", default=environ.var())
        table = environ.var("schema.table")

    zendesk = environ.group(ZendeskConfig)
    db = environ.group(DBConfig)
