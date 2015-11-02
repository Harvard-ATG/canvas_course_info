from django.test import Client, TestCase, RequestFactory
from mock import patch, MagicMock
from views import editor

# todo: docstrings

mock_course_info = {
    u'course': {
        u'registrar_code_display': u'ABC 1234',
        u'school_id': u'abc'
    },
    u'description': u'a fake course',
    u'exam_group': u'',
    u'instructors_display': u'first last',
    u'location': u'some room',
    u'meeting_time': u'mon 3-5',
    u'notes': u'',
    u'term': {
        u'display_name': u'Fall 2012'
    },
    u'title': u'Mock Course',
}

mock_school_info = {
    u'title_long': u'Harvard School of ABCs'
}

integration_test_course_info = {
    u'canvas_course_id': u'10000',
    u'number_display': u'2901',
    u'school_display': u'Harvard Divinity School'
}


@patch('course_info.views.ICommonsApi.from_request')
class DisplayTests(TestCase):
    """
    Widget and editor should display correct values in the returned HTML
    """
    api_course_mock = MagicMock(return_value=mock_course_info)
    api_school_mock = MagicMock(return_value=mock_school_info)
    # as we are mocking return values, only the general format of the
    # referer string is important here
    canvas_course_id = '0000'
    referer_string = 'https://canvas/courses/{}'.format(canvas_course_id)
    factory = RequestFactory()

    def test_course_and_school_lookup(self, api_mock):
        """
        Backend code should fetch info from the course and school
        helpers of the API wrapper
        """
        api_mock.return_value.get_course_info_by_canvas_course_id = self.api_course_mock
        api_mock.return_value.get_school_info = self.api_school_mock
        mock_school_id = mock_course_info['course']['school_id']

        client = Client(HTTP_REFERER=self.referer_string)
        client.get('/course_info/widget.html?f=course.registrar_code_display')

        self.assertTrue(self.api_course_mock.called_once_with(self.canvas_course_id))
        self.assertTrue(self.api_school_mock.called_once_with(mock_school_id))

    def test_course_code(self, api_mock):
        """
        Should show full school name and the course code (without the
        leading school short code, if present in registrar_code_display field)
        """
        api_mock.return_value.get_course_info_by_canvas_course_id = self.api_course_mock
        api_mock.return_value.get_school_info = self.api_school_mock

        client = Client(HTTP_REFERER=self.referer_string)
        response = client.get('/course_info/widget.html?f=course.registrar_code_display')

        # Should not display full registrar code from API response
        # (it should be reformatted by _get_course_code())
        full_code = mock_course_info['course']['registrar_code_display']
        self.assertNotContains(response, full_code)

        # Should show the expanded school name and non-school portion
        # of course code instead
        partial_code = full_code[4:]  # just the portion we want
        self.assertContains(response, partial_code)
        self.assertContains(response, mock_school_info['title_long'])

    def test_widget_multiple_fields(self, api_mock):
        """ Widget should display only the fields requested """
        api_mock.return_value.get_course_info_by_canvas_course_id = self.api_course_mock
        query = 'f=title&f=term.display_name'
        client = Client(HTTP_REFERER=self.referer_string)
        response = client.get('/course_info/widget.html?{}'.format(query))
        self.assertContains(response, mock_course_info['title'])
        self.assertContains(response, mock_course_info['term']['display_name'])
        self.assertNotContains(response, mock_course_info['location'])

    def test_widget_partial_fields(self, api_mock):
        """ Widget should display only the fields with registrar data """
        api_mock.return_value.get_course_info_by_canvas_course_id = self.api_course_mock
        query = 'f=exam_group&f=term.display_name'
        client = Client(HTTP_REFERER=self.referer_string)
        response = client.get('/course_info/widget.html?{}'.format(query))
        self.assertContains(response, mock_course_info['term']['display_name'])
        self.assertNotContains(response, 'Field not populated by registrar')

    def test_editor_partial_field_data(self, api_mock):
        """ Editor should display all fields and note those without data """
        api_mock.return_value.get_course_info = self.api_course_mock
        post_body = {'lis_course_offering_sourcedid': '0000'}
        request = self.factory.post('/', post_body)
        response = editor(request)
        self.assertEqual(response.status_code, 200)
        # should have a checkbox for every configured field (unlike in widget)
        self.assertContains(response, 'course_info_checkbox', count=9)
        # fields with empty API return values should have a friendly message
        self.assertContains(response, 'Field not populated by registrar', count=2)


class TestDataIntegration(TestCase):
    """
    These tests will ensure that the widget (and by extension, the iCommons API)
    is running as expected. Changes in the iCommons api structure will be caught.
    """
    @classmethod
    def setUpClass(cls):
        cls.base_url = 'https://canvas.icommons.harvard.edu/'
        cls.referer_header = '{}/courses/{}'.format(
            cls.base_url,
            integration_test_course_info['canvas_course_id']
        )
        cls.test_url = '/course_info/widget.html?f=course.registrar_code_display'

    def test_course_number(self):
        """ Course info call should return data in the format we expect """
        c = Client(HTTP_REFERER=self.referer_header)
        response = c.get(self.test_url)
        self.assertContains(response, integration_test_course_info['number_display'])

    def test_school_name(self):
        """ School info call should return data in the format we expect """
        c = Client(HTTP_REFERER=self.referer_header)
        response = c.get(self.test_url)
        self.assertContains(response, integration_test_course_info['school_display'])
