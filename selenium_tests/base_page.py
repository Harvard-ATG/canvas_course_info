import logging
from functools import partial

from selenium.common.exceptions import (
    NoSuchElementException,
    InvalidSwitchToTargetException
)


logger = logging.getLogger(__name__)


class BasePageMeta(type):
    """
    This metaclass allows us to avoid writing boilerplate that just finds
    an element in a page by a locator tuple.

    Expected usage:

        class SomePageLocators(object):
            TITLE = (By.CSS_SELECTOR, '#title')
            BUTTON = (By.CSS_SELECTOR, '#the_only_button')

        class SomePage(BasePage):
            locator_class = SomePageLocators
            located_properties = ['title', 'button']

    This metaclass adds properties for each name in located_properties,
    using the corresponding (upper-cased) attribute on the locator_class.
    In the example above, it would add SomePage.title, which would look
    up the element found by SomePageLocators.TITLE, and SomePage.button,
    returning the element found by SomePageLocators.BUTTON.
    """
    def __new__(class_, name, bases, dict_):
        type_ = super(BasePageMeta, class_).__new__(class_, name, bases, dict_)
        if hasattr(type_, 'locator_class'):
            for attribute in getattr(type_, 'located_properties', []):
                def fn(self, attr):
                    locator = getattr(type_.locator_class, attr.upper())
                    if not locator:
                        raise RuntimeError(
                                  '{} locator class {} is missing {}'.format(
                                      name, type_.locator_class.__name__,
                                      attr.upper()))
                    try:
                        return self.find_element(*locator)
                    except NoSuchElementException:
                        raise RuntimeError('Unable to find {} on {}'.format(
                                               attr, name))
                setattr(type_, attribute, property(partial(fn, attr=attribute)))
        return type_


class BasePage(object):
    """
    This is the base class that all page models can inherit from
    """
    __metaclass__ = BasePageMeta
    tool_frame_name = 'external_tool_button_frame'

    def __init__(self, driver):
        self._driver = driver

    # These methods locate a specific element or elements.
    def find_element(self, *loc):
        """
        find the web element specified by *loc
        :param loc:
        :return:
        """
        return self._driver.find_element(*loc)

    def find_elements(self, *loc):
        """
        find the web elements specified by *loc
        :param loc:
        :return:
        """
        return self._driver.find_elements(*loc)

    def find_element_by_xpath(self, *loc):
        """
        find the web element specified by *loc using an xpath expression
        :param loc:
        :return:
        """
        return self._driver.find_element_by_xpath(*loc)

    def get_title(self):
        """
        get the page title
        :return:
        """
        return self._driver.title

    def get_url(self):
        """
        get the page url
        :return:
        """
        return self._driver.current_url

    def get(self, url):
        """
        open the provided url
        :param url:
        :return:
        """
        self._driver.get(url)

    def focus_on_tool_frame(self):
        """
        The pages we are testing are in an iframe, make sure we have the
        correct focus
        :return:
        """
        try:
            self._driver.switch_to.frame(self.tool_frame_name)
        except InvalidSwitchToTargetException:
            logger.warning('Unable to switch to tool frame %s',
                           self.tool_frame_name)
