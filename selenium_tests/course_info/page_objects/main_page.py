from django.conf import settings
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from selenium_tests.base_page import BasePage


class MainPageLocators(object):
    EDIT_BUTTON = (By.CSS_SELECTOR, 'a.edit-wiki')
    TITLE = (By.CSS_SELECTOR, 'h1.page-title')

    # since there's potentially many widget instances on a page, can't use
    # this as a property
    WIDGET = (By.CSS_SELECTOR,
              'iframe[src^="%s"]' % settings.SELENIUM_CONFIG.get('widget_url'))


class MainPage(BasePage):
    locator_class = MainPageLocators
    located_properties = ['edit_button', 'title']

    def get_widgets(self):
        """Returns any widget iframes present in the pagel  If none are found,
        returns []."""
        self.focus_on_default_content()
        try:
            return self.find_elements(*self.locator_class.WIDGET)
        except NoSuchElementException:
            return []

    def is_loaded(self):
        self.focus_on_default_content()
        return self.title.text == 'Course Information'
