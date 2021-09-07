from selenium import webdriver
import unittest


class TestBaseMobile(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        mobile_emulation = {"deviceName": "Nexus 5"}
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        self.driver = webdriver.Chrome(chrome_options=chrome_options)


class TestBaseWeb(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        chrome_options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.maximize_window()
