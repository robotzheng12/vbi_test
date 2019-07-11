import time
import cv2
from PIL import Image
from io import BytesIO
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pykeyboard import PyKeyboard
from common.commonaw import compare_image
from utils.config import BASE_PATH
from utils.vbi_logger import VBILogger
from utils.vbi_exceptions import ImageLoadError, ImageNotExist


class VBIImage(object):
    """
    VBI图像类
    """

    def __init__(self, target_image=None, driver=None, module='web_ui'):
        self.target_image = target_image
        self.image_name = None
        self.similaritylimit = 0.99
        self.logger = VBILogger(module, log_file_name='test.log').get_logger()
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 5)

    def get_target_image(self):
        """
        获取目标图片

        :param driver: browser对象
        :return: 目标图片
        """
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'screenBody')))
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'el-input__inner')))
        input = self.driver.find_element_by_css_selector(".screenHead input.el-input__inner")
        input.clear()
        if self.image_name:
            input.send_keys(self.image_name)
        self.driver.find_element_by_css_selector('.el-input-group__append button').click()
        if '连接成功' in self.driver.find_element_by_class_name(
                'headerItem').text and '该目录暂无画面' in self.driver.find_element_by_class_name('screenBody').text:
            raise ImageNotExist('{imageName}画面不存在'.format(imageName=self.image_name))
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'el-card__body'))).click()
        time.sleep(1)
        target_image = self._get_target_image()
        self.driver.back()
        self.logger.info(self.image_name)
        return target_image

    def _get_target_image(self):
        """
        截取目标图片
        :param driver:  webdriver obj
        :return: target image
        """
        k = PyKeyboard()
        k.tap_key(k.function_keys[11])
        # 解决IE浏览器全屏出现滚动条页面显示不全问题
        self.driver.refresh()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'inner')))
        time.sleep(3)
        self.target_image = self.get_image(self.driver)
        # 按浏览器类型保存图片
        target_image = None
        if self.driver.name == 'internet explorer':
            self.target_image.save(BASE_PATH + '/data/images/ie_target_image.png', 'png')
            target_image = cv2.imread(BASE_PATH + '/data/images/ie_target_image.png')
        elif self.driver.name == 'chrome':
            self.target_image.save(BASE_PATH + '/data/images/chrome_target_image.png', 'png')
            target_image = cv2.imread(BASE_PATH + '/data/images/chrome_target_image.png')
        elif self.driver.name == 'firefox':
            self.target_image.save(BASE_PATH + '/data/images/firefox_target_image.png', 'png')
            target_image = cv2.imread(BASE_PATH + '/data/images/firefox_target_image.png')
        k.tap_key(k.function_keys[11])
        return target_image

    def get_template_image(self, template_image_name):
        """
        获取模板图像

        :param path: 模板图片路径+文件名
        :return: Image对象
        """
        base_path = BASE_PATH + '/data/images/'
        if self.driver.name == 'internet explorer':
            TEMP_DIR = base_path + 'ie_template_images/'
        elif self.driver.name == 'chrome':
            TEMP_DIR = base_path + 'chrome_template_images/'
        elif self.driver.name == 'firefox':
            TEMP_DIR = base_path + 'firefox_template_images/'
        else:
            raise Exception
        path = TEMP_DIR + template_image_name + '.png'
        template_image = cv2.imread(path)
        if template_image is None:
            raise ImageLoadError('不存在模板图片')
        return template_image

    def get_position(self, browser):
        """
        获取验证码图片位置
        :return:
        """
        img = None
        self.logger.info('开始找图片')
        try:
            img = WebDriverWait(browser, 5).until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'inner')))
        except TimeoutException:
            self.logger.error('未发现图片')
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)

    def get_image(self, browser):
        """
        获取验证码截图
        :return:
        """
        top, bottom, left, right = self.get_position(browser)
        self.logger.info('图片位置:' + str(top) + ',' + str(bottom) + ',' + str(left) + ',' + str(right))
        screenshot = self.get_screenshot(browser)
        captcha = screenshot.crop((left, top, right, bottom))
        return captcha

    def get_screenshot(self, browser):
        """
        获取网页截图
        :return:
        """
        screenshot = browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def compare_image(self, image1, image2, method='ahash'):
        """
        对比图片

        :param image1:用于对比的图片1
        :param image2:用于对比的图片2
        :return similarity:图片相似度
        """
        similarity = compare_image(image1, image2, method)
        return similarity

    def if_similarity(self, similarity):
        """
        是否相识
        :param similarity: 相似度
        :return:
        """
        if similarity > self.similaritylimit:
            self.logger.info('相似度%s' % similarity)
            return True
        else:
            self.logger.error('图片存在差异，相似度%s，备份图片' % similarity)
            self.backup_image()
            raise Exception('图片存在差异，相似度%s' % similarity)

    def backup_image(self):
        """
        备份失败图片
        :return:
        """
        self.logger.info('备份失败图片')
        self.target_image.save(
            BASE_PATH + '/data/images/error_images/%s.png' % (self.image_name + '_' + self.driver.name), 'png')
