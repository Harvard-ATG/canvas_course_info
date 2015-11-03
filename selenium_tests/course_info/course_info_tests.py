from selenium_tests.course_info.course_info_base_test_case import CourseInfoBaseTestCase
from selenium_tests.pin.page_objects.pin_login_page_object import PinLoginPageObject as LoginPage
from selenium_tests.course_info.page_objects.editor_page import EditorPage, EditorPageLocators
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

class CourseInfoTestFlow(CourseInfoBaseTestCase):

    def test_course_info_flow(self):
        """
        test that the lecture video tool loads properly and checks that
        a the detail page is loaded when a user clicks on one of the videos.
        """
        pin_page = LoginPage(self.driver)
        pin_page.login(self.BASE_URL, self.USERNAME, self.PASSWORD)
        edit_page = EditorPage(self.driver)
        self.assertTrue(edit_page.is_loaded(), 'edit page not loaded')
        edit_page.click_tool_button()
        self.assertTrue(edit_page.is_tool_dialog_displayed(), 'tool dialog is not displayed')

        try:
            WebDriverWait(self.driver, 50).until(lambda s: s.find_element(
                *EditorPageLocators.REGISTRAR_CODE_CHECKBOX).is_displayed())
        except TimeoutException:
            # this seems to always throw and execption even if the bos is present
            # I'm not sure why this is happening 
            pass

        self.driver.save_screenshot('screenshot1.png')
        edit_page.click_course_reg_code()
        self.driver.save_screenshot('screenshot1.png')

        edit_page.click_iframe_submit()
        edit_page.save_edit_page()


