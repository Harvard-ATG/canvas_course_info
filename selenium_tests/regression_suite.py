"""
To run these tests from the command line in a local VM, you'll need to set up the environment:
> export PYTHONPATH=~/tlt/canvas_course_info
> export DJANGO_SETTINGS_MODULE=canvas_course_info.settings.local
> sudo apt-get install xvfb
> python selenium_tests/regression_tests.py
"""

import time

from django.conf import settings
from selenium_tests.course_info.course_info_tests import CourseInfoTestFlow


if settings.SELENIUM_CONFIG.get('use_htmlrunner', True):
    import HTMLTestRunner
    dateTimeStamp = time.strftime('%Y%m%d_%H_%M_%S')
    buf = file("TestReport" + "_" + dateTimeStamp + ".html", 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
        stream=buf,
        title='Test the Report',
        description='Result of tests'
    )
else:
    import logging; logging.basicConfig(level=logging.DEBUG)
    import unittest
    runner = unittest.TextTestRunner()

course_info_flow_test = unittest.TestLoader().loadTestsFromTestCase(CourseInfoTestFlow)
smoke_tests = unittest.TestSuite([course_info_flow_test])

# run the suite
runner.run(smoke_tests)
