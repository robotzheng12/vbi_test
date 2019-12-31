import pymysql


def singleton(cls):
    instances = {}

    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return getinstance


@singleton
class mysql_connection(object):
    def __init__(self, host, port, user_name, pass_word, db_name, charset='utf8'):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user_name = user_name
        self.pass_word = pass_word
        self.chartset = charset
        self.init_connection()

    def init_connection(self):
        self.db_connection = pymysql.connect(self.host, self.user_name, self.pass_word, self.db_name, port=self.port,
                                             charset='utf8')
        self.cursor = self.db_connection.cursor()

    def exec_sql(self, sql):
        self.cursor.execute(sql)
        self.db_connection.commit()

    def close(self):
        self.cursor.close()
        self.db_connection.close()


if __name__ == '__main__':
    obj1 = mysql_connection('172.16.206.157', 3307, 'mycompany', 'zhengyanlin123', 'vbi_ui_test')
    sql = """
        insert into base_info (test_env,server_version,browser,browser_version,start_time,end_time) value
        ('http://172.16.206.65:8089','20190926_1850-5.9.1078.6149'
        ,'firefox','67.0.1','2019-09-27 14:00:11','2019-09-27 14:12:11');
        """
    obj1.cursor.execute(sql)
    obj1.db_connection.commit()
    obj1.cursor.close()
    obj1.db_connection.close()
