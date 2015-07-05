from sqlalchemy import create_engine

# Common settings
DEBUG = True

# MySql Settings
MYSQL_DATA = {
    'type': "mysql",
    'user': "root",
    'password': "",
    'host': "127.0.0.1",
    'port': 3306,
    'db': "comingbot"
}

#Telegram bot api_key
TG_API_KEY='xxx'

# local settings must be placed in a file named 'local_settings.py' next to settings.py
try:
   from local_settings import *
except ImportError:
   pass

MYSQL_CONN_STR = "{0}://{1}:{2}@{3}:{4}/{5}?charset=utf8".format(
                                        MYSQL_DATA['type'],
                                        MYSQL_DATA['user'],
                                        MYSQL_DATA['password'],
                                        MYSQL_DATA['host'],
                                        MYSQL_DATA['port'],
                                        MYSQL_DATA['db'])

MYSQL_ENGINE = create_engine(MYSQL_CONN_STR)
