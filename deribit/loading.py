from base_classes import Settings, Credentials, MysqlDB


def get_robot_settings():
    with open('/var/deribit/settings.json', 'r') as stream:
        doc: str = stream.read()
        settings = Settings.parse_raw(doc)
        robot_settings = settings.robot
        return [robot_settings['gap'], robot_settings['gap_ignore']]


class LoadSettigs:
    def __init__(self) -> None:
        with open('./settings.json', 'r') as stream:
            doc: str = stream.read()
            settings = Settings.parse_raw(doc)
            exchange = settings.credentials
            mysql_db = settings.db
            self.db_settings = MysqlDB(mysql_db['db_user'],
                                       mysql_db['db_password'],
                                       mysql_db['db_name'],
                                       mysql_db['db_table'],
                                       mysql_db['db_host'],
                                       mysql_db['db_port'])
            self.credentials = Credentials(exchange['client_id'],
                                           exchange['client_secret'],
                                           exchange['client_url'])

    def get_credentials(self):
        return self.credentials

    def get_db_settings(self):
        return self.db_settings
