import os
import requests, json
from utils.config import DINGTALK_WEBHOOK, BROWSERS

projectName = os.getenv("JOB_NAME")
sonarqubeAddress = os.getenv("SonarqubeAddress")
# Dingtalk_access_token = DINGTALK_WEBHOOK
Dingtalk_access_token = 'https://oapi.dingtalk.com/robot/send?access_token=1ffe5cabce5dbb4c56b227566028b55d2068086e156927a78def5c66e25ec451'
JenkinsAddress = os.getenv("JenkinsAddress")
JenkinsUserName = os.getenv("JenkinsUserName")
JenkinsPassWord = os.getenv("JenkinsPassWord")
TestDataBaseType = os.getenv("VBI_ENV_TYPE")


def Log(mes):
    print(mes + '\n')
    return


def sendding(content, title, messageUrl):
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


def ReadVersion():
    version = "5.0"
    try:
        versionFile = 'finalversion.txt'
        versionfileName = os.path.abspath(versionFile)
        result = []
        with open(versionfileName, 'r') as f:
            for line in f:
                result.append(str(line.strip('\n')))
        if len(result) == 4:
            version = '.'.join(result)
    except Exception as p:
        Log(p.message)
        pass
    Log(version)
    return version


def ReadServerVersion():
    version = "5.0"
    try:
        versionFile = 'serverVersion.txt'
        versionfileName = os.path.abspath(versionFile)
        result = []
        with open(versionfileName, 'r') as f:
            for line in f:
                result.append(str(line.strip('\n')))
        if len(result) > 0:
            version = result[0]
    except Exception as p:
        Log(p.message)
        pass;
    Log(version)
    return version


def notification(result):
    # messageUrl = 'http://' + JenkinsAddress + '/job/' + projectName + '/' + str(projectBuildNumber) + '/HTML_20Report/'
    messageUrl = 'http://172.16.206.22/job/VBI5_WEBUI_TEST/HTML_20Report/'
    code_reslut = []
    for browser in eval(BROWSERS):
        if browser == 'IE':
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
                               " \n - 用例数量:<font color=#555555>" + str(test_count) + "</font>个" + \
                               " \n - 成功数量:<font color=#11cd11>" + str(pass_count) + "</font>个" + \
                               " \n - 失败数量:<font color=#bb1111>" + str(fail_count) + "</font>个" + \
                               " \n - 错误数量:<font color=#bb1111>" + str(error_count) + "</font>个 \n")
        if browser == 'CHROME':
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
                               " \n - 用例数量:<font color=#555555>" + str(test_count) + "</font>个" + \
                               " \n - 成功数量:<font color=#11cd11>" + str(pass_count) + "</font>个" + \
                               " \n - 失败数量:<font color=#bb1111>" + str(fail_count) + "</font>个" + \
                               " \n - 错误数量:<font color=#bb1111>" + str(error_count) + "</font>个 \n")
        if browser == 'FIREFOX':
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
                               " \n - 用例数量:<font color=#555555>" + str(test_count) + "</font>个" + \
                               " \n - 成功数量:<font color=#11cd11>" + str(pass_count) + "</font>个" + \
                               " \n - 失败数量:<font color=#bb1111>" + str(fail_count) + "</font>个" + \
                               " \n - 错误数量:<font color=#bb1111>" + str(error_count) + "</font>个 \n")
    code_reslut.append(" - [查看详情](" + messageUrl + ")")
    code_reslut = ''.join(code_reslut)
    sendding(content=code_reslut, title='WEBUI测试', messageUrl=messageUrl)
    return


class result(object):
    def __init__(self):
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0


if __name__ == '__main__':
    result = result()
    notification(result)
