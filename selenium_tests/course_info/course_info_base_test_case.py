from selenium_tests.base_selenium_test_case import BaseSeleniumTestCase
from django.conf import settings


class CourseInfoBaseTestCase(BaseSeleniumTestCase):
    """
    Lecture Video base test case, all other tests will subclass this class
    """

    @classmethod
    def setUpClass(cls):
        """
        setup values for the tests
        """
        super(CourseInfoBaseTestCase, cls).setUpClass()
        cls.USERNAME = settings.SELENIUM_CONFIG.get('selenium_username')
        cls.PASSWORD = settings.SELENIUM_CONFIG.get('selenium_password')
        cls.BASE_URL = '%s/courses/5949/pages/front-page/edit' % settings.SELENIUM_CONFIG.get('canvas_base_url')

    @classmethod
    def tearDownClass(cls):
        super(CourseInfoBaseTestCase, cls).tearDownClass()

