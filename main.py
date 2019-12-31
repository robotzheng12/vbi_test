import os
import sys
import shutil
from vbifactory import VBIFACTORY
from utils.config import BASE_PATH

if __name__ == '__main__':
    argv = sys.argv
    # 清理历史error_images
    try:
        shutil.rmtree(BASE_PATH + r'/data/images/error_images/{browser}/'.format(browser='firefox'))
    finally:
        os.mkdir(BASE_PATH + r'/data/images/error_images/{browser}/'.format(browser='firefox'))
    # 登录页面
    factory = VBIFACTORY("FIREFOX")
    factory.generate_case_object()
    factory.vbi_process()
    factory.get_server_version()
    # 生成测试报告
    # factory.generate_report()
    # 发送钉钉群消息
    factory.send_message()
    factory.write_error_case_id()
    factory.close()
