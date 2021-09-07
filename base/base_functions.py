import calendar
import datetime
import logging
import random
import string
import time
import json
from functools import wraps
from random import randint

from selenium.common.exceptions import *
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait


class Base(object):
    """
    Page class that all page models can inherit from.
    Please, try to save its structure&style and not to change its code without code review/discussion
    with other project users.

    """

    def __init__(self, driver, explicit_wait=45):
        """
        Inits Selenium Driver class with driver
        :param driver: WebDriver instance
        :param int explicit_wait: Time you want use as wait time
        :return A SeleniumDriver object

        """
        self.driver = driver
        self.wait = WebDriverWait(self.driver, explicit_wait)

    def driver(self):
        return self.driver

    def get_driver(self):
        """
        Get the web driver instance
        :rtype: WebDriver
        :return: WebDriver instance

        """
        driver = self.driver
        return driver

    def refresher(self, total_time, refresh_time):
        """
        Refresh the page according to total time and refresh per seconds
        :param int total_time: Total waiting time for all refreshes
        :param int refresh_time: Time for refresh per seconds

        """
        refresh_count = int(total_time / refresh_time)
        for current_refresh in range(0, refresh_count):
            self.driver.refresh()
            time.sleep(refresh_time)

    def refresh(self):
        """
        Refresh current pages on the web application

        """
        self.driver.refresh()
        time.sleep(3)
        logging.info("The current browser location was refreshed")

    def get_browser_title(self):
        """
        Get title of current pages on the web application
        :return: Title of the current pages

        """
        title = self.driver.title
        logging.info("Title of the current pages is :: " + title)
        return title

    def get_browser_url(self):
        """
        Get URL of current pages on the web application
        :return: Current pages URL

        """
        browser_url = self.driver.current_url
        logging.info("Current browser url is :: " + browser_url)
        return browser_url

    @staticmethod
    def process_browser_request_entry(entry):
        """
        Logs every request in network
        :param entry: Request logs in network

        """
        response = json.loads(entry['message'])['message']
        return response

    def filter_network_request(self):
        """
        Filters request in network

        """
        browser_log = self.driver.get_log('performance')
        events = [self.process_browser_request_entry(entry) for entry in browser_log]
        events = [event for event in events if 'Network.requestWillBeSent' in event['method']]
        return events

    def navigate_url(self, url):
        """
        Browse current window to requested url.
        :param str url: Requested URL of the site to be redirected

        """
        self.driver.get(url)

    def navigate_browser_back(self, additional_wait=0):

        """
        Go one pages back
        :param additional_wait: Additional wait time before getting back (in seconds)

        """
        time.sleep(additional_wait)
        self.driver.back()

    def navigate_browser_forward(self):
        """
        Go one pages forward

        """
        self.driver.forward()

    def quit_driver(self):
        """
        Quit driver

        """
        if self.driver is not None and self.is_browser_reachable():
            self.driver.quit()

    def is_browser_reachable(self):
        try:
            return bool(self.driver.window_handles)
        except:
            return False

    def clear_browser_data(self):
        """
        Clears browsing history, cookies and other site data, cached images and files

        """
        self.navigate_url('chrome://settings/clearBrowserData')
        time.sleep(2)
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.TAB * 7).send_keys(Keys.ENTER).perform()
        time.sleep(2)

    def is_element_present(self, locator):
        """
        Return True if element present and False if element absent
        :param locator: locator of the element to find

        """
        try:
            self.driver.find_element(*locator)
        except (NoSuchElementException, StaleElementReferenceException):
            return False
        return True

    def is_element_clickable(self, locator):
        """
        Return True if element clickable and False if element not clickable
        :param locator: locator of the element to find

        """
        try:
            self.wait_for_element_clickable(locator)
        except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException,
                ElementClickInterceptedException):
            return False
        return True

    def is_element_visible(self, locator):
        """
        Return True if element clickable and False if element not clickable
        :param locator: locator of the element to find

        """
        try:
            self.wait_for_element_visible(locator, timeout=30)
        except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException,
                ElementClickInterceptedException):
            return False
        return True

    def get_element(self, locator):
        """
        Get element for a provided locator
        :param locator: locator of the element to find
        :return: Element Object
        :rtype: WrapWebElement

        """
        try:
            element = self.driver.find_element(*locator)
        except (NoSuchElementException, StaleElementReferenceException):
            raise Exception("There is no such element or its" + str(locator) + " has changed ")
        return WrapWebElement(self.driver, element, locator)

    def get_element_list(self, locator, list_length=1):
        """
        Get elements list for a provided locator
        :param locator: locator of the element list to find
        :param int list_length: Expected count of list
        :return: List of web elements or empty list
        :rtype: list

        """
        elements = Base.wait_until(self.driver.find_elements, params=locator, equals=list_length, timeout=10,
                                   interval=0.5, list_check=True)
        if elements is False:
            return []
        return list(map(lambda el: WrapWebElement(self.driver, el, locator=locator), elements))

    def wait_for_element(self, locator, wait_type=ec.presence_of_element_located, timeout=20):
        """
        Wait for element to present
        :param wait_type: which condition of the element you are waiting for
        :param locator: locator of the element to find
        :param int timeout: Maximum time you want to wait for the element
        :rtype: WrapWebElement

        """
        start_time = int(round(time.time() * 1000))
        element = None
        try:
            logging.info("Waiting for maximum :: " + str(timeout) +
                         " :: seconds for element to be visible and clickable")
            wait = WebDriverWait(self.driver, timeout,
                                 ignored_exceptions=[NoSuchElementException, ElementNotVisibleException,
                                                     ElementNotSelectableException])
            element = wait.until(wait_type(locator))
            end_time = int(round(time.time() * 1000))
            duration = (end_time - start_time) / 1000.00
            logging.info("Element '"
                         "' appeared on the web pages after :: " + "{0:.2f}".format(duration) + " :: seconds")
        except ElementNotVisibleException:
            logging.error("Element '"
                          "' not appeared on the web pages after :: " + str(timeout) + " :: seconds")
        if isinstance(element, WebElement):
            return WrapWebElement(self.driver, element, locator)
        else:
            return element

    def wait_for_element_clickable(self, locator, timeout=20):
        """
        Wait for element to be clickable
        :param locator: locator of the element to find
        :param int timeout: Maximum time you want to wait for the element
        :rtype: WrapWebElement

        """
        return self.wait_for_element(locator, ec.element_to_be_clickable, timeout)

    def wait_for_element_visible(self, locator, timeout=20):
        """
        Wait for element to be visible
        :param locator: locator of the element to find
        :param int timeout: Maximum time you want to wait for the element
        :rtype: WrapWebElement

        """
        return self.wait_for_element(locator, ec.visibility_of_element_located, timeout)

    def wait_for_element_invisible(self, locator, timeout=20):
        """
        Wait for element to be invisible
        :param locator: locator of the element to find
        :param int timeout: Maximum time you want to wait for the element
        :rtype: WrapWebElement

        """
        return self.wait_for_element(locator, ec.invisibility_of_element_located, timeout)

    def create_random_string(self, size=1):
        """
        Create random string to use it in name generator
        :param int size: Size of desired random string
        :return: Random string
        :rtype: string

        """
        chars = string.ascii_uppercase
        return ''.join(random.choice(chars) for _ in range(size))

    def create_random_integer(self, start=0, finish=10):
        """
        Create random integer to use it in name generator
        :param int start: Starting point for interval
        :param int finish: Endpoint for interval
        :return: Random integer between given interval
        :rtype: int

        """
        return randint(start, finish)

    def erase_text(self, locator, click=None, clear=None, backspace=None):
        """
        Various ways to erase text from web element.
        :param tuple locator: locator tuple or WebElement instance
        :param bool click: clicks the input field
        :param bool clear: clears the input field
        :param int backspace: how many times to hit backspace

        """
        element = locator
        if not isinstance(element, WebElement):
            element = self.get_element(locator)

        if click:
            element.click()

        if clear:
            element.clear()

        if backspace:
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.END)
            for _ in range(backspace):
                actions.send_keys(Keys.BACKSPACE)
            actions.perform()

    @staticmethod
    def wait_until(function, params=None, equals=None, not_equals=None, timeout=None, interval=None, list_check=None):
        """
        Checked to wait until the specified timeout time of the specified function.
        :param function: Function name to wait
        :param params: Function name to parameters
        :param equals: Wait until match value with equals parameter
        :param not_equals: Wait until match value with not equals parameter
        :param timeout: Time to wait
        :param interval: Interval seconds to retry
        :param list_check: Use true if you are waiting list
        :return: Function value, if is timeout finish returns False
        """
        end = time.time() + timeout

        while time.time() < end:
            if isinstance(params, tuple):
                val = function(*params)
            elif isinstance(params, list):
                val = function(*tuple(params))
            elif isinstance(params, dict):
                val = function(**params)
            else:
                val = function()

            if list_check is not None and len(val) >= equals:
                return val
            elif equals is not None and val == equals:
                return val
            elif not_equals is not None and val != not_equals:
                return val
            else:
                time.sleep(interval)
        return False

    class SwitchFrame:
        def __init__(self, driver, element):
            self.driver = driver
            self.element = element

        def __enter__(self):
            self.driver.switch_to.frame(self.element)

        def __exit__(self, type, value, traceback):
            self.driver.switch_to.parent_frame()

    def switch_frame(self, locator):
        """
        Switch to iframe togater 'with' keyword.
        Switches back automatically when operations finished 'with' block.
        :param tuple locator:
        :rtype: SwitchFrame

        """
        return self.SwitchFrame(self.driver, self.wait_for_element(locator))

    class DropDownElement:
        def __init__(self, driver, element):
            self.driver = driver
            self.element = element

        def select_by_value(self, item_value):
            """
            Select all options that have a value matching the argument
            :param str item_value: The value to match against

            """
            Select(self.element).select_by_value(item_value)

        def select_by_index(self, item_index):
            """
            Select the option at the given index.
            :param int item_index: The option at this index will be selected

            """
            Select(self.element).select_by_index(item_index)

        def select_by_text(self, item_text):
            """
            Select all options that display text matching the argument
            :param str item_text: The visible text to match against

            """
            Select(self.element).select_by_visible_text(item_text)

    def get_dropdown_element(self, locator, index=0):
        """
        Get and return drop down element for a provided locator
        Switches back automatically when operations finished 'with' block.
        :param tuple locator: locator of the drop down element to find
        :param int index: Element index
        :rtype: DropDownElement

        """
        return self.DropDownElement(self.driver, self.get_element_list(locator)[index])

    def switch_window(self, index):
        """
        Switch to  window or tabs
        :param index: tab index or allowed values are "main", "first", "last"

        """
        if index == "main":
            self.driver.switch_to.window("main")
        elif index == "first":
            self.driver.switch_to.window(self.get_driver().window_handles[0])
        elif index == "last":
            self.driver.switch_to.window(self.get_driver().window_handles[-1])
        elif type(index) == int:
            self.driver.switch_to.window(self.get_driver().window_handles[index])
        else:
            raise Exception("switch_window: Invalid index: {}".format(index))

    def open_new_tab(self):
        """
        Opens new tab and switches the current tab to it

        """
        self.get_driver().execute_script("window.open();")
        self.switch_window("last")

    @staticmethod
    def add_months(current_date, months):
        """
        Adds months to current date to get future datetime
        :param current_date: Current date
        :param int months: Count of months you want to add to get future datetime
        :return: Future datetime

        """
        month = current_date.month - 1 + months
        year = int(current_date.year + month / 12)
        month = month % 12 + 1
        day = min(current_date.day, calendar.monthrange(year, month)[1])
        return datetime.date(year, month, day)


class WrapWebElement(WebElement):
    """
    This class defines the generic interceptor for the methods of wrapped web element references.It also provides
    implementations for methods that acquire web element references

    """
    element = None
    driver = None
    locator = None

    def __init__(self, driver, element, locator=None):
        super().__init__(element.parent, element._id)
        self.element = element
        self.driver = driver
        self.locator = locator

    def find_element(self, *locator):
        """
        Find an element given a By strategy and locator.
        :param locator: locator of the element to find
        :rtype: WrapWebElement

        """
        if isinstance(locator[0], tuple):
            element = self.element.find_element(*locator[0])
            used_locator = locator[0]
        else:
            element = self.element.find_element(*locator)
            used_locator = locator
        return WrapWebElement(self.driver, element, locator=used_locator)

    def find_elements(self, *locator):
        """
        Find elements given locator.
        :param locator: locator of the elements to find
        :rtype: list of elements

        """
        if isinstance(locator[0], tuple):
            elements = self.element.find_elements(*locator[0])
            used_locator = locator[0]
        else:
            elements = self.element.find_elements(*locator)
            used_locator = locator
        return list(map(lambda el: WrapWebElement(self.driver, el, locator=used_locator), elements))

    def wait_visible(self, timeout=20):
        """
        Wait for element to be visible
        :param int timeout: Desired wait time before visibility of element
        :return: Desired visible element
        :rtype: WrapWebElement

        """
        wait = WebDriverWait(self.driver, timeout)
        wait.until(lambda _: self.element.is_displayed(), "{} element not visible".format(str(self.locator)))
        return self

    def wait_enable(self, timeout=20):
        """
        Wait for element to be enable
        :param int timeout: Desired wait time before visibility of element
        :return: Desired visible element
        :rtype: WrapWebElement

        """
        wait = WebDriverWait(self.driver, timeout)
        wait.until(lambda _: self.element.is_enabled(), "{} element not enable".format(str(self.locator)))
        return self

    def wait_clickable(self, timeout=20):
        """
        Wait for element to be clickable
        :param int timeout: Desired wait time before visibility of element
        :return: Desired visible element
        :rtype: WrapWebElement

        """
        self.wait_visible(timeout=timeout)
        self.wait_enable(timeout=timeout)
        return self

    def click(self, delay=0):
        """
        Clicks the web element.
        :param float delay: Wait seconds before click
        :return: Desired visible element
        :rtype: WrapWebElement

        """
        if delay:
            time.sleep(delay)
        self.element.click()
        return self

    def js_click(self):
        """
        Clicks given element with execute script

        """
        self.driver.execute_script("arguments[0].click();", self.element)
        return self

    def double_click(self):
        """
        Double-clicks an element.
        :rtype: WrapWebElement

        """
        actions = ActionChains(self.driver)
        actions.double_click(self.element).perform()
        return self

    def right_click(self):
        """
        Right clicks an element.
        :rtype: WrapWebElement

        """
        actions = ActionChains(self.driver)
        actions.context_click(self.element).perform()
        return self

    def offset_click(self, x_offset, y_offset):
        """
         Function provides relative offset shifting
        :param x_offset: horizontal offset
        :param y_offset: vertical offset

        """
        action = ActionChains(self.driver)
        action.move_to_element_with_offset(self.element, x_offset, y_offset)
        action.click()
        action.perform()
        return self

    def slide(self, x_offset, y_offset):
        """
        Slides an element by offsets
        :param x_offset: horizontal offset
        :param y_offset: vertical offset

        """
        action = ActionChains(self.driver)
        action.click_and_hold(self.element)
        action.move_by_offset(x_offset, y_offset)
        action.release()
        action.perform()
        return self

    def focus(self):
        """
        Focus on an an element.
        :rtype: WrapWebElement

        """
        actions = ActionChains(self.driver)
        actions.move_to_element(self.element).perform()
        self.click()
        return self

    def hover(self):
        """
        Hover to an element

        """
        actions = ActionChains(self.driver)
        actions.move_to_element(self.element).perform()
        return self

    def scroll(self, center=False):
        """
        Scrolls to an element
        :rtype: WrapWebElement

        """
        if center:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", self.element)
        else:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", self.element)
        return self

    def send_keys(self, value, delay=0):
        """
        Sends keys to current focused element.
        :param str value: A string for typing
        :param float delay: Requested wait time between typing each character
        :rtype: WrapWebElement

        """
        if delay:
            for char in list(value):
                self.element.send_keys(char)
                time.sleep(delay)
        else:
            self.element.send_keys(value)
        return self

    def action_chains_send_keys(self, *keys_to_send):
        """
        Sends keys to current focused element.
        :Args:
         - keys_to_send: The keys to send.  Modifier keys constants can be found in the
           'Keys' class.

        """
        actions = ActionChains(self.driver)
        actions.send_keys(*keys_to_send)
        actions.perform()

    def control_shortcuts(self, char):
        """
        Makes the desired shortcut operations with the control keys
        :param str char:  Give one of the shortcut letters

        """
        actions = ActionChains(self.driver)
        actions.key_down(Keys.CONTROL)
        actions.key_down(char)
        actions.key_up(char)
        actions.key_up(Keys.CONTROL)
        actions.perform()

    def __getattribute__(self, attribute):
        """
        Return getattr(self, name).
        :param str attribute: Attribute of the element
        :return: value of attribute

        """
        if attribute not in list(WrapWebElement.__dict__):
            returning_value = object.__getattribute__(self.element, attribute)
        else:
            returning_value = object.__getattribute__(self, attribute)

        @wraps(WebElement)
        def wrapper(*args, **kwargs):
            value = returning_value(*args, **kwargs)
            if (isinstance(value, WebElement) or attribute in (
                    "submit", "clear")) and attribute != 'find_element':
                return self
            else:
                return value

        if callable(returning_value):
            return wrapper
        else:
            return returning_value
