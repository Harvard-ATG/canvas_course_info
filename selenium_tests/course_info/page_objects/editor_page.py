from selenium.webdriver.common.by import By
from selenium_tests.base_page import BasePage
from selenium.common.exceptions import NoSuchElementException


class EditorPageLocators(object):
    # locators for main editor page
    NEW_PAGE_SUBMIT = (By.ID, 'new_page_submit')
    TOOL_BUTTON = (By.CSS_SELECTOR,
                   'div[aria-label="Import Course Info - dev (root account)"] button')

    #locators for course info tool iframe
    DESCRIPTION_CHECKBOX = (By.ID, 'description')
    EXAM_GROUP_CHECKBOX = (By.ID, 'exam_group')
    INSTRUCTORS_CHECKBOX = (By.ID, 'instructors_display')
    LOCATION_CHECKBOX = (By.ID, 'location')
    MEETING_TIME_CHECKBOX = (By.ID, 'meeting_time')
    NOTES_CHECKBOX = (By.ID, 'notes')
    REGISTRAR_CODE_CHECKBOX = (By.ID, 'course.registrar_code_display')
    TERM_CHECKBOX = (By.ID, 'term.display_name')
    TITLE_CHECKBOX = (By.ID, 'title')
    TOOL_SUBMIT_BUTTON = (By.ID, 'iframe_submit')
    EXTERNAL_TOOL_BUTTON_DIALOG = (By.ID, 'external_tool_button_dialog')
    EDIT_PAGE_SUBMIT = (By.XPATH, "//div[@id='content']/form/div[2]/div/button")


class EditorPage(BasePage):
    locator_class = EditorPageLocators
    located_properties = [
        'description_checkbox',
        'exam_group_checkbox',
        'new_page_submit',
        'instructors_checkbox',
        'location_checkbox',
        'meeting_time_checkbox',
        'notes_checkbox',
        'registrar_code_checkbox',
        'term_checkbox',
        'title_checkbox',
        'tool_button',
        'tool_submit_button',
    ]
    tool_frame_name = 'external_tool_button_frame'

    def open_tool(self):
        self.tool_button.click()
        self.focus_on_tool_frame()

    def is_loaded(self):
        """ determine if the page loaded by looking for a specific element on the page """
        try:
            self.find_element(*EditorPageLocators.TOOL_BUTTON)
        except NoSuchElementException:
            return False
        return True

    def click_tool_button(self):
        tool_button = self.find_element(*EditorPageLocators.TOOL_BUTTON)
        tool_button.click()

    def is_tool_dialog_displayed(self):
        tool_dialog = self.find_element(*EditorPageLocators.EXTERNAL_TOOL_BUTTON_DIALOG)
        return tool_dialog.is_displayed()

    def click_course_reg_code(self):
        course_reg_code_checkbox = self.find_element(*EditorPageLocators.REGISTRAR_CODE_CHECKBOX)
        course_reg_code_checkbox.click()

    def is_course_reg_code_selected(self):
        course_reg_code_checkbox = self.find_element(*EditorPageLocators.REGISTRAR_CODE_CHECKBOX)
        return course_reg_code_checkbox.is_selected()

    def click_iframe_submit(self):
        tool_submit_button = self.find_element(*EditorPageLocators.TOOL_SUBMIT_BUTTON)
        tool_submit_button.click()

    def save_edit_page(self):
        edit_page_submit = self.find_element(*EditorPageLocators.EDIT_PAGE_SUBMIT)
        edit_page_submit.click()
