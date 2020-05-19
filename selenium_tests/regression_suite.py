"""
To run these tests from the command line in a local VM, you'll need to:
> python selenium_tests/regression_suite.py
"""

import os
import sys
import time
import unittest

from django.conf import settings


# set up PYTHONPATH and DJANGO_SETTINGS_MODULE.  icky, but necessary
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.setenv('DJANGO_SETTINGS_MODULE', 'canvas_course_info.settings.local')

# developing test cases is easier with text test runner, lets us drop into pdb
if settings.SELENIUM_CONFIG.get('use_htmlrunner', True):
    from . import HTMLTestRunner
    dateTimeStamp = time.strftime('%Y%m%d_%H_%M_%S')
    buf = file("TestReport" + "_" + dateTimeStamp + ".html", 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
        stream=buf,
        title='Test the Report',
        description='Result of tests'
    )
else:
    import logging; logging.basicConfig(level=logging.DEBUG)
    runner = unittest.TextTestRunner()

# load in all unittest.TestCase objects from *_tests.py files.  start in PWD,
# with top_level_dir set to PWD/..
suite = unittest.defaultTestLoader.discover(
            os.path.abspath(os.path.dirname(__file__)),
            pattern='*_tests.py',
            top_level_dir=os.path.abspath(
                             os.path.join(os.path.dirname(__file__), '..'))
)

# run the suite
result = runner.run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
