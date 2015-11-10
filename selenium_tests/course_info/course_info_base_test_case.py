from django.conf import settings

from selenium_tests.base_selenium_test_case import BaseSeleniumTestCase


class CourseInfoBaseTestCase(BaseSeleniumTestCase):
    """
    Canvas course info widget base test case, all other tests will subclass this class.
    """

    @classmethod
    def setUpClass(cls):
        """
        setup values for the tests
        """
        super(CourseInfoBaseTestCase, cls).setUpClass()
        cls.USERNAME = settings.SELENIUM_CONFIG.get('selenium_username')
        cls.PASSWORD = settings.SELENIUM_CONFIG.get('selenium_password')
        cls.BASE_URL = '%s%s' % (settings.SELENIUM_CONFIG.get('canvas_base_url'),
                                 settings.SELENIUM_CONFIG.get('edit_page_url_path'))
