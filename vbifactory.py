import os
import sys
import re
import time
import datetime
import importlib
import win32api, win32con
from selenium import webdriver
from pykeyboard import PyKeyboard
from utils.report_help import TestResult
from utils.vbi_exceptions import LoginError, NetworkError, ImageLoadError, ImageNotExist, Failure
from utils.driver_help import DriverHelp
from utils.config import TEST_PATH, BASE_URL, INTERNET_RETRY, DATA_PATH
from test.first import UserLogin
from utils.ding_talk_news import notification
from selenium.common.exceptions import TimeoutException
from threading import Thread
from utils.vbi_logger import VBILogger


class VBIFACTORY(object):

    def __init__(self, argv):
        self.argv = argv
        self.serverVersion = None
        self.case_id_list = []
        self.error_id_list = []
        self.case_obj_pool = []
        self.browser_link_pool = []
        self.exec_thread_pool = []
        self.result = TestResult("数智云图WEB测试报告")
        self.result.init_db_connection()
        self.logger = VBILogger('vbi_factory').get_logger()
        self.startTime = str(datetime.datetime.now())[:19]

    def init_base_info(self):
        self.result.startTime = self.startTime
        self.get_server_version()
        self.result.insert_base_info(self.serverVersion)

    def vbi_process(self):
        """
        开启执行线程
        :return:
        """
        # 开启执行线程
        self.control_threads()
        self.init_base_info()
        for driver in self.browser_link_pool:
            if not driver:
                print("待增加异常处理")
                # TODO
            else:
                self.exec_thread_pool.append(Thread(target=self.exec_case, args=[driver]))
        if len(self.exec_thread_pool) == 0:
            print("待增加异常处理")
            # TODO
        for exec_thread in self.exec_thread_pool:
            exec_thread.start()
        for exec_thread in self.exec_thread_pool:
            exec_thread.join()
        self.result.update_end_time()
        self.result.close()

    def exec_case(self, driver):
        """
        执行用例
        :param driver:
        :return:
        """
        while True:
            if len(self.case_obj_pool) == 0:
                break
            case = self.case_obj_pool.pop()
            start = datetime.datetime.now()
            for i in range(INTERNET_RETRY):
                try:
                    r = case.runVBITest(driver)
                    if r == 0:
                        self.result.insert_case_result(case.__class__.__name__, case.name, "通过", "", start,
                                                       datetime.datetime.now())
                    else:
                        self.result.insert_case_result(case.__class__.__name__, case.name, "失败", r, start,
                                                       datetime.datetime.now())
                        self.error_id_list.append(case.__class__.__name__)
                    break
                except Failure as e:
                    self.logger.error(case.name + "测试不通过！" + e.message)
                    self.result.insert_case_result(case.__class__.__name__, case.name, "失败", str(e), start,
                                                   datetime.datetime.now())
                    self.error_id_list.append(case.__class__.__name__)
                    break
                except TimeoutException:
                    self.logger.warn('页面加载超时，重新连接')
                    driver = self.reconnection(driver)
                    continue
                except ImageLoadError as e:
                    self.logger.error(case.name + "测试不通过！" + e.message)
                    self.result.insert_case_result(case.__class__.__name__, case.name, "错误", str(e), start,
                                                   datetime.datetime.now())
                    self.error_id_list.append(case.__class__.__name__)
                    break
                except ImageNotExist as e:
                    self.logger.error(case.name + "测试不通过！" + e.message)
                    self.result.insert_case_result(case.__class__.__name__, case.name, "错误", str(e), start,
                                                   datetime.datetime.now())
                    self.error_id_list.append(case.__class__.__name__)
                    break
                except SystemError:
                    self.logger.warn('系统出错')
                    driver = self.reconnection(driver)
                    continue
                except BaseException as e:
                    self.result.insert_case_result(case.__class__.__name__, case.name, "错误", str(e), start,
                                                   datetime.datetime.now())
                    self.error_id_list.append(case.__class__.__name__)
                    break
            del case

    def login_browser(self, browser):
        """
        登录浏览器
        :param browser:
        :return:
        """
        driver = DriverHelp(browser).driver
        width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        if driver.get_window_size()['width'] != width:
            self.logger.info('开启全屏')
            k = PyKeyboard()
            k.tap_key(k.function_keys[11])
        try:
            self.logger.info('登录浏览器页面')
            UserLogin().runVBITest(driver)
        except LoginError as e:
            self.logger.error(e.message)
            driver.close()
        except NetworkError as e:
            self.logger.error(e.message)
            driver.close()
        else:
            self.logger.info('登录成功，执行用例')
            return driver

    def reconnection(self, driver):
        """
        重连浏览器
        :return:
        """
        name = driver.name
        driver.close()
        if name == 'chrome':
            browser = "CHROME"
        elif name == 'firefox':
            browser = "FIREFOX"
        else:
            browser = "IE"
        return self.login_browser(browser)

    def generate_case_id_list(self, case_id_list):
        self.case_id_list.extend(case_id_list)

    def generate_case_object(self):
        """
        执行用例
        :param driver:
        :return:
        """
        for root, dirs, files in os.walk(TEST_PATH):
            if re.search('__(.*?)__', root.split('\\')[-1]):
                continue
            for fileName in files:
                fileName = os.path.splitext(fileName)[0]
                if fileName in self.case_id_list or self.case_id_list == []:
                    if fileName[0:2] != "__" and fileName != "first":
                        module = importlib.import_module('.',
                                                         root.split('\\', 1)[1].replace('\\', '.') + '.' + fileName)
                        for cls_obj in dir(module):
                            test_cls = getattr(module, cls_obj)
                            if hasattr(test_cls, "runVBITest"):
                                obj = test_cls()
                                self.case_obj_pool.append(obj)
                        del module

    # 控制线程数
    def control_threads(self):
        """
        根据系统资源控制我们的线程数
        :return:
        """
        for i in range(1):
            self.browser_link_pool.append(self.login_browser(self.argv))
        if self.browser_link_pool[0]:
            self.result.driver = self.browser_link_pool[0]

    def get_server_version(self):
        url = BASE_URL + '/license/info'
        version = None
        driver = webdriver.Chrome()
        driver.get(url)
        bgs = driver.find_elements_by_class_name('bg1')
        for bg in bgs:
            if '版本' in bg.text:
                version = re.search(r'.*版本.*\((.*?)\).*', bg.text).group(1)
                break
        driver.close()
        self.serverVersion = version

    # def generate_report(self):
    #     """
    #     发送报告
    #     :return:
    #     """
    #     endTime = datetime.datetime.now()
    # self.result.addTimeInfo(self.startTime, endTime)

    # report = REPORT_PATH + '\\report.html'
    # report_bak = REPORT_PATH + '\\report_%s.html' % time.strftime('%Y%m%d')
    # with open(report, 'wb') as f:
    #     htmlReport = HTMLReport(f, self.result)
    #     htmlReport.generateReport(self.serverVersion)
    # with open(report_bak, 'wb') as f:
    #     with open(report, 'rb') as f1:
    #         f.write(f1.read())

    def send_message(self):
        """
        发送钉钉群消息
        :return:
        """
        notification(self.argv, self.result, self.serverVersion)

    def write_error_case_id(self):
        fail_file = DATA_PATH + '\\fail_case\\fail_file_' + self.argv.lower()
        with open(fail_file, 'wb') as f:
            f.write(str(self.error_id_list).encode('utf-8'))

    def read_error_case_id(self):
        fail_file = DATA_PATH + '/fail_case/fail_file_' + self.argv.lower()
        with open(fail_file, 'rb') as f:
            fail_case_list = eval(f.read())
            return fail_case_list

    def close(self):
        """
        关闭线程
        :return:
        """
        for driver in self.browser_link_pool:
            driver.quit()
