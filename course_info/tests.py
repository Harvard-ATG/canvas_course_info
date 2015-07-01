# To test locally, run ./manage.py test
# TODO: The test cases for this app are a little different than a typical app
# because it's so network-heavy. It may be a good idea to do tests on each individual view
# by sending in an appropriate request, then checking the response.

from django.test import TestCase
from icommons import ICommonsApi
from django.test import Client

# TODO: Expand test coverage


class testData(TestCase):
    '''
        These tests will ensure that the widget (and by extension, the iCommons API) is running
        as expected
    '''
    # Tip: first word in a test method must be "test" for Django to recognize it & run it.
    def test_course_number(self):
        # Make sure that the widget is displaying a correct course number for a given course ID
        id = str(312976)
        c = Client()
        response = c.get('/course_info/widget.html?course_instance_id=' + id + '&f=course.registrar_code_display')
        self.assertContains(response, "2901")
        self.assertEqual("a", "a", "a == a")

    def test_school_name(self):
        id = str(312976)
        c = Client()
        response = c.get('/course_info/widget.html?course_instance_id=' + id + '&f=course.registrar_code_display')
        self.assertContains(response, "Harvard Divinity School")


class testEditor(TestCase):
    '''
        TODO
    '''

    def test_insert_text_button_existence(self):
        # make sure that the editor is responding to the "offer_text" setting
        pass

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