from selenium.webdriver.common.by import By
from selenium_tests.base_page import BasePage


class EditorPageLocators(object):
    # locators for main editor page
    EDITOR_TABS = (By.ID, 'editor_tabs')
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
    EXTERNAL_TOOL_BUTTON_DIALOG = (By.ID, 'external_tool_button_dialog')
    EDIT_PAGE_SUBMIT = (By.XPATH, "//div[@id='content']/form/div[2]/div/button")


class EditorPage(BasePage):
    locator_class = EditorPageLocators
    located_properties = [
        'description_checkbox',
        'editor_tabs',
        'exam_group_checkbox',
        'instructors_checkbox',
        'location_checkbox',
        'meeting_time_checkbox',
        'notes_checkbox',
        'registrar_code_checkbox',
        'term_checkbox',
        'tool_button',
        'tool_submit_button',
    ]
    tool_frame_name = 'external_tool_button_frame'

    def is_loaded(self):
        return bool(self.editor_tabs)
