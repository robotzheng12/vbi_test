import os
import re
import requests, json
from utils.config import DINGTALK_WEBHOOK, BROWSERS, BASE_URL
from selenium import webdriver

url = BASE_URL + '/license/info'
projectName = os.getenv("JOB_NAME")
sonarqubeAddress = os.getenv("SonarqubeAddress")
Dingtalk_access_token = DINGTALK_WEBHOOK
JenkinsAddress = os.getenv("JenkinsAddress")
JenkinsUserName = os.getenv("JenkinsUserName")
JenkinsPassWord = os.getenv("JenkinsPassWord")
TestDataBaseType = os.getenv("VBI_ENV_TYPE")


def Log(mes):
    print(mes + '\n')
    return


def sendding(content, title):
    url = Dingtalk_access_token
    pagrem = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": content,
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    # 发送消息
    requests.post(url, data=json.dumps(pagrem), headers=headers)


def notification(agrv, result, serverVersion):
    # messageUrl = 'http://' + JenkinsAddress + '/job/' + projectName + '/' + str(projectBuildNumber) + '/HTML_20Report/'
    code_reslut = []
    messageUrl = None
    if agrv == 'IE':
        messageUrl = 'http://172.16.206.22/job/VBI5_WEBUI_TEST_IE/HTML_20Report/'
        result_info = '通过'
        textcolor = "11cd11"
        test_count = result.ie_success_count + result.ie_failure_count + result.ie_error_count
        pass_count = result.ie_success_count
        fail_count = result.ie_failure_count
        error_count = result.ie_error_count
        if int(fail_count) + int(error_count) > 0:
            result_info = "未通过"
            textcolor = "bb1111"
        title = "WEBUI测试[<font color=#555555>ie</font>]  <font color=#" + textcolor + " size=10>" + str(
            result_info) + "</font>"
        code_reslut.append("### " + title + \
                           " \n - 服务版本:<font color=#555555>" + serverVersion + \
                           " \n - 用例数量:<font color=#555555>" + str(test_count) + "</font>个" + \
                           " \n - 成功数量:<font color=#11cd11>" + str(pass_count) + "</font>个" + \
                           " \n - 失败数量:<font color=#bb1111>" + str(fail_count) + "</font>个" + \
                           " \n - 错误数量:<font color=#bb1111>" + str(error_count) + "</font>个 \n")
    if agrv == 'CHROME':
        messageUrl = 'http://172.16.206.22/job/VBI5_WEBUI_TEST_CHROME/HTML_20Report/'
        result_info = '通过'
        textcolor = "11cd11"
        test_count = result.chrome_success_count + result.chrome_failure_count + result.chrome_error_count
        pass_count = result.chrome_success_count
        fail_count = result.chrome_failure_count
        error_count = result.chrome_error_count
        if int(fail_count) + int(error_count) > 0:
            result_info = "未通过"
            textcolor = "bb1111"
        title = "WEBUI测试[<font color=#555555>chrome</font>]  <font color=#" + textcolor + " size=10>" + str(
            result_info) + "</font>"
        code_reslut.append("### " + title + \
                           " \n - 服务版本:<font color=#555555>" + serverVersion + \
                           " \n - 用例数量:<font color=#555555>" + str(test_count) + "</font>个" + \
                           " \n - 成功数量:<font color=#11cd11>" + str(pass_count) + "</font>个" + \
                           " \n - 失败数量:<font color=#bb1111>" + str(fail_count) + "</font>个" + \
                           " \n - 错误数量:<font color=#bb1111>" + str(error_count) + "</font>个 \n")
    if agrv == 'FIREFOX':
        messageUrl = 'http://172.16.206.22/job/VBI5_WEBUI_TEST_FIREFOX/HTML_20Report/'
        result_info = '通过'
        textcolor = "11cd11"
        test_count = result.firefox_success_count + result.firefox_failure_count + result.firefox_error_count
        pass_count = result.firefox_success_count
        fail_count = result.firefox_failure_count
        error_count = result.firefox_error_count
        if int(fail_count) + int(error_count) > 0:
            result_info = "未通过"
            textcolor = "bb1111"
        title = "WEBUI测试[<font color=#555555>firefox</font>]  <font color=#" + textcolor + " size=10>" + str(
            result_info) + "</font>"
        code_reslut.append("### " + title + \
                           " \n - 服务版本:<font color=#555555>" + serverVersion + \
                           " \n - 用例数量:<font color=#555555>" + str(test_count) + "</font>个" + \
                           " \n - 成功数量:<font color=#11cd11>" + str(pass_count) + "</font>个" + \
                           " \n - 失败数量:<font color=#bb1111>" + str(fail_count) + "</font>个" + \
                           " \n - 错误数量:<font color=#bb1111>" + str(error_count) + "</font>个 \n")
    code_reslut.append(" - [查看详情](" + messageUrl + ")")
    code_reslut = ''.join(code_reslut)
    sendding(content=code_reslut, title='WEBUI测试')
    return


class result(object):
    def __init__(self):
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0


if __name__ == '__main__':
    result = result()
    # notification(argv, result)
