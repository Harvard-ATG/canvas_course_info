from django.conf import settings
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from selenium_tests.base_page import BasePage


class EditorPageLocators(object):
    # locators for main editor page
    EDITOR_TABS = (By.ID, 'editor_tabs')
    LOGOUT_BUTTON = (By.CSS_SELECTOR, 'a[href="/logout"]')
    TOOL_BUTTON = (By.CSS_SELECTOR,
                   'div[aria-label="Import Course Info - dev (root account)"] button')

    # locators for course info tool iframe
    DESCRIPTION_CHECKBOX = (By.ID, 'description')
    EXAM_GROUP_CHECKBOX = (By.ID, 'exam_group')
    INSTRUCTORS_CHECKBOX = (By.ID, 'instructors_display')
    LOCATION_CHECKBOX = (By.ID, 'location')
    MEETING_TIME_CHECKBOX = (By.ID, 'meeting_time')
    NOTES_CHECKBOX = (By.ID, 'notes')
    REGISTRAR_CODE_CHECKBOX = (By.ID, 'course.registrar_code_display')
    TERM_CHECKBOX = (By.ID, 'term.display_name')
    TOOL_SUBMIT_BUTTON = (By.ID, 'iframe_submit')

    # locator for inserted widget in editor.  since there's potentially many
    # of these, can't use this as a property
    WIDGET = (By.CSS_SELECTOR,
              'img.mce-object-iframe[data-mce-p-src^="%s"]'
                  % settings.SELENIUM_CONFIG.get('widget_url'))


class EditorPage(BasePage):
    locator_class = EditorPageLocators
    located_properties = [
        'description_checkbox',
        'editor_tabs',
        'exam_group_checkbox',
        'instructors_checkbox',
        'location_checkbox',
        'logout_button',
        'meeting_time_checkbox',
        'notes_checkbox',
        'registrar_code_checkbox',
        'term_checkbox',
        'tool_button',
        'tool_submit_button',
    ]
    tool_frame_name = 'external_tool_button_frame'
    editor_frame_name = 'editor_box_unique_id_1_ifr'

    def focus_on_editor_frame(self):
        self._driver.switch_to.frame(self.editor_frame_name)

    def get_inserted_widgets(self):
        """Returns any widget elements already inserted into the page.  If none
        are found, returns []."""
        try:
            return self.find_elements(*self.locator_class.WIDGET)
        except NoSuchElementException:
            return []

    def is_loaded(self):
        return bool(self.editor_tabs)
