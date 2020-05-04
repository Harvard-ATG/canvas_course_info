import urllib.parse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from selenium_tests.course_info.course_info_base_test_case import CourseInfoBaseTestCase
from selenium_tests.course_info.page_objects.editor_page import EditorPage
from selenium_tests.course_info.page_objects.main_page import MainPage
from selenium_tests.pin.page_objects.pin_login_page_object import PinLoginPageObject


class CourseInfoTests(CourseInfoBaseTestCase):
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

        # open the widget editing tool, verify the field selection page comes
        # up in the "modal" iframe
        edit_page.open_widget_editor()
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

        # delete any instances of the widget already in the page
        edit_page.remove_existing_widgets()

        # now squawk if any are left
        self.assertEqual(edit_page.get_inserted_widgets(), [],
                         'Found unexpected instances of widget already in the page')

        # launch the tool, click save in the tool iframe
        edit_page.open_widget_editor()
        edit_page.save_widget()

        # verify the iframe is gone
        edit_page.focus_on_default_content()
        with self.assertRaises(TimeoutException):
            WebDriverWait(self.driver, 10).until(
                lambda d: d.find_element(*edit_page.locator_class.REGISTRAR_CODE_CHECKBOX).is_visible())

        # now make sure the widget is in our editor frame
        widgets = edit_page.get_inserted_widgets()
        self.assertEqual(len(widgets), 1)

        # verify all f values are in the widget url
        widget_url = widgets[0].get_attribute('data-mce-p-src')
        parts = urllib.parse.urlparse(widget_url)
        params = urllib.parse.parse_qs(parts.query)
        self.assertEqual(set(params['f']), edit_page.get_all_f_values(),
                         'Not all expected fields in the widget url')

        # save the page
        edit_page.save_page()

        # sanity check the result
        main_page = MainPage(self.driver)
        self.assertTrue(main_page.is_loaded(),
                        'Unable to confirm main page is loaded')
        self.assertEqual(len(main_page.get_widgets()), 1,
                         'Unexpected number of widgets found on main page')
