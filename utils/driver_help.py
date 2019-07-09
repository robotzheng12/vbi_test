from selenium import webdriver

optons = webdriver.ChromeOptions()
optons.add_argument('disable-infobars')


class DriverHelp:
    def __init__(self, browser):
        if browser == "CHROME":
            self.driver = webdriver.Chrome(chrome_options=optons)
        elif browser == "FIREFOX":
            self.driver = webdriver.Firefox()
        else:
            self.driver = webdriver.Ie()
