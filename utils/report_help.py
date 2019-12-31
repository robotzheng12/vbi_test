import datetime
from .config import BASE_URL
from utils.connect_db import mysql_connection
from utils.config import DB_DICT


class TestResult:
    def __init__(self, title):
        self.title = title
        self.result = []
        self.startTime = 'null'
        self.stopTime = 'null'
        self.driver = None
        self.ie_success_count = 0
        self.ie_failure_count = 0
        self.ie_error_count = 0
        self.chrome_success_count = 0
        self.chrome_failure_count = 0
        self.chrome_error_count = 0
        self.firefox_success_count = 0
        self.firefox_failure_count = 0
        self.firefox_error_count = 0

    def init_db_connection(self):
        self.conn = mysql_connection(DB_DICT['DB_HOST'], DB_DICT['DB_PORT'], DB_DICT['DB_USERNAME'],
                                     DB_DICT['DB_PASSWORD'], DB_DICT['DB_NAME'], DB_DICT['DB_CHARSET'])
        sql = """
                CREATE TABLE case_result_info (CASE_ID varchar(255) not null, CASE_NAME varchar(255) not null, 
                START_TIME datetime,END_TIME datetime,RESULT varchar(255),EXCEPT_INFO varchar(255)) default charset='utf8';
                """
        try:
            self.conn.exec_sql(sql)
        except:
            pass
        sql = """
                create table base_info (TASK_ID int not null auto_increment primary key, TEST_ENV varchar(255) not null,
                SERVER_VERSION varchar(255) not null, BROWSER varchar(255) not null, BROWSER_VERSION varchar(255) not null,
                START_TIME datetime,END_TIME datetime) default charset='utf8';
                """
        try:
            self.conn.exec_sql(sql)
        except:
            pass

    def insert_base_info(self, serverVersion):
        if self.driver.name == 'chrome':
            version = self.driver.capabilities['version']
        else:
            version = self.driver.capabilities['browserVersion']

        sql = """
        insert into base_info (test_env,server_version,browser,browser_version,start_time,end_time) value ('%s', '%s', '%s', '%s', '%s', %s);
        """ % (BASE_URL, serverVersion, self.driver.name, version, self.startTime, self.stopTime)
        self.conn.exec_sql(sql)

    def insert_case_result(self, case_id, name, status, detail, start_time, exectime):
        sql = """
        insert into case_result_info (CASE_ID,CASE_NAME,START_TIME,END_TIME,RESULT,EXCEPT_INFO) value ('%s', '%s', '%s', '%s', '%s', '%s');
        """ % (case_id, name, start_time, exectime, status, detail)
        self.conn.exec_sql(sql)
        if status == "通过":
            if self.driver.name == 'internet explorer':
                self.ie_success_count += 1
            if self.driver.name == 'chrome':
                self.chrome_success_count += 1
            if self.driver.name == 'firefox':
                self.firefox_success_count += 1
        elif status == "失败":
            if self.driver.name == 'internet explorer':
                self.ie_failure_count += 1
            if self.driver.name == 'chrome':
                self.chrome_failure_count += 1
            if self.driver.name == 'firefox':
                self.firefox_failure_count += 1
        else:
            if self.driver.name == 'internet explorer':
                self.ie_error_count += 1
            if self.driver.name == 'chrome':
                self.chrome_error_count += 1
            if self.driver.name == 'firefox':
                self.firefox_error_count += 1

    def update_end_time(self):
        sql = """
                update base_info set END_TIME= '%s' where START_TIME= '%s';
            """ % (str(datetime.datetime.now())[:19], self.startTime)
        self.conn.exec_sql(sql)

    def close(self):
        self.conn.close()
