import unittest

from django.conf import settings
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


# Enabling stdout logging only for high `-v`
class BaseSeleniumTestCase(unittest.TestCase):
    driver = None  # make selenium driver available to any part of the test case
    display = None  # a reference to the virtual display (for running tests locally)

    def setUp(self):
        """
        Sets up the test case, including the selenium browser driver to use
        """

        local = settings.SELENIUM_CONFIG.get('run_locally', False)

        if local:
            # Run selenium tests from a headless browser within the VM
            print "\nSetting up selenium testing locally..."
            # set up virtual display
            self.display = Display(visible=0, size=(1480, 1024)).start()
            # create a new local browser session
            self.driver = webdriver.Firefox()

        else:
            # Run selenium tests from the Selenium Grid server
            selenium_grid_url = settings.SELENIUM_CONFIG.get('selenium_grid_url', None)
            if selenium_grid_url:
                self.driver = webdriver.Remote(
                    command_executor=selenium_grid_url,
                    desired_capabilities=DesiredCapabilities.FIREFOX
                )

        # shared defaults
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()
        if self.display:
            self.display.stop()
