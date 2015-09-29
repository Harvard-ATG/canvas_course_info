# To test locally, run ./manage.py test
# The test cases for this app may be a little different than usual, because it's so network-heavy,
# and everything we need to test routes through Canvas in Production so is somewhat hard to reach.
# What we'll do for now is run tests on each individual view
# by sending in an appropriate request, then checking the response.

from django.test import TestCase
from icommons import ICommonsApi
from django.test import Client

# TODO: Expand test coverage

class testData(TestCase):
    '''
        These tests will ensure that the widget (and by extension, the iCommons API) is running as expected.
        Changes in the iCommons api structure will be caught.
    '''
    # Tip: first word in a test method must be "test" for Django to recognize it & run it.
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


class testEditor(TestCase):
    '''
        TODO
    '''

    def test_insert_text_button_existence(self):
        # make sure that the editor is responding to the "offer_text" setting
        pass


TESTDATA = {
    "example_course1" : {
        "id" : "312976",
        "canvas_course_id": "10000",
        "number_display" : "2901",
        "school_display" : "Harvard Divinity School"
    }
}

SCHOOLS = {
    "hsph":     "Harvard School of Public Health",
    "hds":      "Harvard Divinity School",
    "rad":      "Radcliffe Institute for Advanced Studies",
    "hu":       "Harvard University",
    "gsd":      "Harvard Design School",
    "gse":      "Harvard Graduate School of Education",
    "fas":      "Faculty of Arts and Sciences",
    "dce":      "Harvard University Division of Continuing Education",
    "hls":      "Harvard Law School",
    "arb":      "Arnold Arboretum",
    "bcis":     "Berkman Center for Internet and Society",
    "colgsas":  "Harvard College/Graduate School of Arts and Sciences",
    "ext":      "Division of Continuing Education - Extension",
    "sum":      "Division of Continuing Education - Summer",
    "ksg":      "Harvard Kennedy School Executive Education Program",
    "hilr":     "Harvard Institute for Learning in Retirement",
    "hks":      "Harvard Kennedy School (HKS)",
    "hcl":      "Harvard College Library",
    "hms":      "Harvard Medical School",
    "hsdm":     "Harvard School of Dental Medicine",
    "hbsmba":   "Harvard Business School MBA Program",
    "hbsdoc":   "Harvard Business School Doctoral Program",
    "hx":       "HarvardX",
    "mit":      "MIT"
}