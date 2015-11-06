import urlparse
from selenium.common.exceptions import TimeoutException
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
        edit_page.focus_on_default_content()

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


    def test_insert_widget_all_fields(self):
        """
        Tests inserting the widget into a page, leaving all fields selected.
        """
        # deal with the login
        pin_page = PinLoginPageObject(self.driver)
        pin_page.login(self.BASE_URL, self.USERNAME, self.PASSWORD)
        edit_page = EditorPage(self.driver)
        edit_page.focus_on_default_content()

        # check to make sure our widget isn't already in the page
        # TODO: just nuke them?
        edit_page.focus_on_editor_frame()
        self.assertEqual(edit_page.get_inserted_widgets(), [],
                         'Found unexpected instances of widget already in the page')
        edit_page.focus_on_default_content()

        # launch the tool, click save
        edit_page.tool_button.click()
        edit_page.focus_on_tool_frame()
        edit_page.tool_submit_button.click()
        edit_page.focus_on_default_content()

        # verify the iframe is gone
        with self.assertRaises(TimeoutException):
            WebDriverWait(self.driver, 10).until(
                lambda d: d.find_element(*edit_page.locator_class.REGISTRAR_CODE_CHECKBOX).is_visible())

        # now make sure the widget is in our editor frame
        edit_page.focus_on_editor_frame()
        widgets = edit_page.get_inserted_widgets()
        self.assertEqual(len(widgets), 1)

        # figure out which f values we should be expecting
        expected_f_values = {
            getattr(edit_page.locator_class, c)[1]
                for c in dir(edit_page.locator_class)
                if c.endswith('_CHECKBOX')
        }
        expected_f_values.add('title') # title is always included

        # verify they're all in the widget url
        widget_url = widgets[0].get_attribute('data-mce-p-src')
        parts = urlparse.urlparse(widget_url)
        params = urlparse.parse_qs(parts.query)
        self.assertEqual(set(params['f']), expected_f_values,
                         'Not all expected fields in the widget url')
