from django.test import TestCase
from django.test import Client

# TODO: Expand test coverage


class TestDataIntegration(TestCase):
    """
        These tests will ensure that the widget (and by extension, the iCommons API) is running as expected.
        Changes in the iCommons api structure will be caught.
    """
    def test_course_number(self):
        # Make sure that the widget is displaying a correct course number for a given course ID
        canvas_course_id = TESTDATA["example_course1"]["canvas_course_id"]
        c = Client(
            HTTP_REFERER="https://canvas.icommons.harvard.edu/courses/%s" % canvas_course_id
        )
        response = c.get('/course_info/widget.html?f=course.registrar_code_display')
        self.assertContains(response, TESTDATA["example_course1"]["number_display"])

    def test_school_name(self):
        canvas_course_id = TESTDATA["example_course1"]["canvas_course_id"]
        c = Client(
            HTTP_REFERER="https://canvas.icommons.harvard.edu/courses/%s" % canvas_course_id
        )
        response = c.get('/course_info/widget.html?f=course.registrar_code_display')
        self.assertContains(response, TESTDATA["example_course1"]["school_display"])


class TestEditor(TestCase):
    """
        TODO
    """

    def test_insert_text_button_existence(self):
        # make sure that the editor is responding to the "offer_text" setting
        pass


TESTDATA = {
    "example_course1": {
        "id": "312976",
        "canvas_course_id": "10000",
        "number_display": "2901",
        "school_display": "Harvard Divinity School"
    }
}
