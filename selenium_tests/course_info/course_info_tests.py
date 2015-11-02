from selenium_tests.course_info.course_info_base_test_case import CourseInfoBaseTestCase
from selenium_tests.pin.page_objects.pin_login_page_object import PinLoginPageObject as LoginPage


class CourseInfoTestFlow(CourseInfoBaseTestCase):

    def test_course_info_flow(self):
        """
        test that the lecture video tool loads properly and checks that
        a the detail page is loaded when a user clicks on one of the videos.
        """
        pin_page = LoginPage(self.driver)
        pin_page.get(self.BASE_URL)
        self.assertTrue(pin_page.is_loaded(), 'pin page not loaded')
        edit_page = pin_page.login(self.USERNAME, self.PASSWORD)
        self.assertTrue(edit_page.is_loaded(), 'edit page not loaded')
