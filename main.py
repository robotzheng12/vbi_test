import os
import time
import importlib
import datetime
import logging
from utils.vbi_exceptions import LoginError, NetworkError
from utils.config import TEST_PATH, REPORT_PATH, INTERNET_RETRY
from utils.driver_help import DriverHelp
from test.first import UserLogin
from utils.report_help import TestResult, HTMLReport
from utils.config import BROWSERS
from utils.vbi_logger import VBILogger
from selenium.common.exceptions import TimeoutException

log_dir = r'E:\workspace\python_project\vbitest\logs'
startTime = datetime.datetime.now()
result = TestResult("数智云图WEB测试报告", "针对WEB UI的自动化测试报告")
logger = VBILogger('vbi_main', log_file_name='test.log').get_logger()
for browser in eval(BROWSERS):
    driver = DriverHelp(browser).driver
    try:
        UserLogin().runVBITest(driver)
    except LoginError as e:
        logger.error(e.message)
    except NetworkError as e:
        logger.error(e.message)
    else:
        logger.info('登录成功，执行用例')
        for fileName in os.listdir(TEST_PATH):
            fileName = os.path.splitext(fileName)[0]
            if fileName[0:2] != "__" and fileName != "first":
                module = importlib.import_module('.', "test." + fileName)
                for cls_obj in dir(module):
                    test_cls = getattr(module, cls_obj)
                    if hasattr(test_cls, "runVBITest"):
                        start = datetime.datetime.now()
                        for i in range(INTERNET_RETRY):
                            obj = test_cls(driver)
                            logging.basicConfig(level='INFO',
                                                filename=log_dir + r'\%s_%s.log' % (obj.name, time.strftime('%Y%m%d')))
                            try:
                                r = obj.runVBITest()
                                exectime = datetime.datetime.now() - start
                                if r == 0:
                                    print(obj.name + "测试通过！")
                                    result.addResult(obj.name, "通过", "", exectime, driver.name)
                                else:
                                    print(obj.name + "测试不通过！")
                                    result.addResult(obj.name, "失败", r, exectime, driver.name)
                            except TimeoutException:
                                driver.close()
                                driver = DriverHelp(browser).driver
                                UserLogin().runVBITest(driver)
                                continue
                            except BaseException as e:
                                exectime = datetime.datetime.now() - start
                                print(obj.name + " 发生异常：", e)
                                print(obj.name + "测试不通过！")
                                result.addResult(obj.name, "错误", str(e), exectime, driver.name)
                            del obj
                            break
                del module
    finally:
        driver.quit()
endTime = datetime.datetime.now()
result.addTimeInfo(startTime, endTime)

report = REPORT_PATH + '\\report.html'
report_bak = REPORT_PATH + '\\report_%s.html' % time.strftime('%Y%m%d')
with open(report, 'wb') as f:
    htmlReport = HTMLReport(f, result)
    htmlReport.generateReport()
with open(report_bak, 'a') as f:
    f.write('a')
    htmlReport = HTMLReport(f, result)
    htmlReport.generateReport()

# 推送钉钉
# notification(result)
