import os
import logging
from logging.handlers import TimedRotatingFileHandler

path = os.path.dirname(os.path.abspath(__file__))
path = path.replace('\\', '/')
log_path = os.path.join(path, '../logs')


class VBILogger(object):

    def __init__(self, logger_name='logs', log_file_name='test.log'):
        self.logger = logging.getLogger(logger_name)
        logging.root.setLevel(logging.NOTSET)
        self.log_file_name = log_file_name
        self.backup_count = 5  # 最多存放日志的数量
        # 日志输出级别
        self.console_output_level = 'INFO'
        self.file_output_level = 'DEBUG'
        # 日志输出格式
        self.formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')

    def get_logger(self):
        """
        在logger中添加日志句柄并返回，如果logger已有句柄，则直接返回
        :return:
        """
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.formatter)
            console_handler.setLevel(self.console_output_level)
            self.logger.addHandler(console_handler)

            # 日志文件
            file_handler = TimedRotatingFileHandler(
                filename=os.path.join(log_path, self.log_file_name).replace('\\', '/'), when='D',
                backupCount=self.backup_count, delay=True, encoding='utf-8')
            file_handler.setFormatter(self.formatter)
            file_handler.setLevel(self.file_output_level)
            self.logger.addHandler(file_handler)
        return self.logger
