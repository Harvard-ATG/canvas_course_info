from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from selenium_tests.base_page import BasePage


class MainPageLocators(object):
    EDIT_BUTTON = (By.CSS_SELECTOR, 'a.edit-wiki')
    TITLE = (By.CSS_SELECTOR, 'h1.page-title')


class MainPage(BasePage):
    locator_class = MainPageLocators
    located_properties = ['edit_button', 'title', 'tool_submit_button']

    def is_loaded(self):
        return self.title.text == 'Canvas course info selenium test page'
