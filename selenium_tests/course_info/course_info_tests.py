from selenium.webdriver.support.ui import WebDriverWait

from selenium_tests.course_info.course_info_base_test_case import CourseInfoBaseTestCase
from selenium_tests.course_info.page_objects.editor_page import EditorPage
from selenium_tests.pin.page_objects.pin_login_page_object import PinLoginPageObject

class CourseInfoTestFlow(CourseInfoBaseTestCase):
    def test_course_info_tool_loads(self):
        """
        test that the course info tool loads properly.
        """
        # try to load the base url, but expect to be interrupted by the pin
        # login page
        pin_page = PinLoginPageObject(self.driver)
        pin_page.login(self.BASE_URL, self.USERNAME, self.PASSWORD)
        edit_page = EditorPage(self.driver)
        self.assertTrue(edit_page.is_loaded(), 'edit page not loaded')

        # click on our tool's button in the editor, verify the tool's field
        # selection page comes up in the "modal" iframe
        edit_page.tool_button.click()
        edit_page.focus_on_tool_frame()
        WebDriverWait(self.driver, 30).until(
            lambda d: edit_page.registrar_code_checkbox.is_displayed(),
            'Timed out waiting for registrar code checkbox to be displayed')

        # just for completeness sake, let's verify that *all* checkboxes are there
        checkbox_properties = [p for p in edit_page.located_properties
                                   if p.endswith('_checkbox')]
        for checkbox in checkbox_properties:
            self.assertTrue(getattr(edit_page, checkbox).is_displayed(),
                            '{} is not displayed'.format(checkbox))
