from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from selenium_tests.course_info.course_info_base_test_case import CourseInfoBaseTestCase
from selenium_tests.course_info.page_objects.editor_page import EditorPage, EditorPageLocators
from selenium_tests.pin.page_objects.pin_login_page_object import PinLoginPageObject

class CourseInfoTestFlow(CourseInfoBaseTestCase):
    def test_course_info_tool_loads(self):
        """
        test that the course info tool loads properly.
        """
        pin_page = PinLoginPageObject(self.driver)
        pin_page.login(self.BASE_URL, self.USERNAME, self.PASSWORD)
        edit_page = EditorPage(self.driver)
        self.assertTrue(edit_page.is_loaded(), 'edit page not loaded')

        edit_page.open_tool()
        try:
            WebDriverWait(self.driver, 50).until(lambda s: s.find_element(
                *EditorPageLocators.REGISTRAR_CODE_CHECKBOX).is_displayed())
        except TimeoutException:
            return False
        self.assertTrue(edit_page.registrar_code_checkbox.is_displayed(),
                        'tool failed to load')

