import os
from configparser import ConfigParser

BASE_PATH = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
BASE_PATH = BASE_PATH.replace('\\', '/')
CONFIG_FILE = os.path.join(BASE_PATH, 'config', 'config.ini')
DATA_PATH = os.path.join(BASE_PATH, 'data')
DRIVER_PATH = os.path.join(BASE_PATH, 'drivers')
LOG_PATH = os.path.join(BASE_PATH, 'logs')
REPORT_PATH = os.path.join(BASE_PATH, 'report')
TEST_PATH = os.path.join(BASE_PATH, 'test')

cfg = ConfigParser()
cfg.read(CONFIG_FILE)

BROWSERS = cfg.get("System", "BROWSERS")
DRIVER_NAME = os.path.join(DRIVER_PATH, cfg.get("System", "DRIVER_NAME"))
BASE_URL = cfg.get("Test", "BASE_URL")
USER = cfg.get("Test", "USER")
PASSWORD = cfg.get("Test", "PASSWORD")
INTERNET_RETRY = int(cfg.get('Retry', 'INTERNET_RETRY'))

# DB
DB_HOST = cfg.get('DB_INFO', 'DB_HOST')
DB_PORT = int(cfg.get('DB_INFO', 'DB_PORT'))
DB_NAME = cfg.get('DB_INFO', 'DB_NAME')
DB_USERNAME = cfg.get('DB_INFO', 'DB_USERNAME')
DB_PASSWORD = cfg.get('DB_INFO', 'DB_PASSWORD')
DB_CHARSET = cfg.get('DB_INFO', 'DB_CHARSET')

DB_DICT = {'DB_HOST': DB_HOST, 'DB_PORT': DB_PORT, 'DB_NAME': DB_NAME, 'DB_USERNAME': DB_USERNAME,
           'DB_PASSWORD': DB_PASSWORD, 'DB_CHARSET': DB_CHARSET}

# 钉钉
DINGTALK_WEBHOOK = cfg.get("DingTalk", "webhook")
