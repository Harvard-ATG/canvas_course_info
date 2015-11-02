"""
To run these tests from the command line in a local VM, you'll need to set up the environment:
> export PYTHONPATH=~/tlt/canvas_course_info
> export DJANGO_SETTINGS_MODULE=canvas_course_info.settings.local
> sudo apt-get install xvfb
> python selenium_tests/regression_tests.py
"""

import unittest
import time
from selenium_tests.course_info.course_info_tests import CourseInfoTestFlow

import HTMLTestRunner

dateTimeStamp = time.strftime('%Y%m%d_%H_%M_%S')
buf = file("TestReport" + "_" + dateTimeStamp + ".html", 'wb')
runner = HTMLTestRunner.HTMLTestRunner(
    stream=buf,
    title='Test the Report',
    description='Result of tests'
)

course_info_flow_test = unittest.TestLoader().loadTestsFromTestCase(CourseInfoTestFlow)
smoke_tests = unittest.TestSuite([course_info_flow_test])

# run the suite
runner.run(smoke_tests)

