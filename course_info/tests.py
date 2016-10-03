from django.test import Client, TestCase, RequestFactory
from mock import patch, MagicMock
from views import editor, sort_and_format_instructor_display

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

mock_course_info_without_instructor_display = {
    u'course': {
        u'registrar_code_display': u'ABC 1234',
        u'school_id': u'abc'
    },
    u"course_instance_id": 338318,
    u'description': u'a fake course',
    u'term': {
        u'display_name': u'Fall 2012'
    },
    u'title': u'Mock Course',
}

mock_course_info_without_cid = {
    u'course': {
        u'registrar_code_display': u'ABC 1234',
        u'school_id': u'abc'
    },
    u'description': u'a fake course',
    u'term': {
        u'display_name': u'Fall 2012'
    },
    u'title': u'Mock Course',
}

mock_staff_data_from_api = [
    {
        u'profile': {u'name_first': u'user1_first', u'name_last': u'user1_last', u'role_type_cd': u'EMPLOYEE'},
        u'source': u'xmlfeed',
        u'role': {u'role_name': u'Course Head', u'canvas_role': u'Course Head', u'role_id': 1},
        u'seniority_sort': 1,
        u'user_id': u'12121212'
    },
    {
        u'profile': {u'name_first': u'user2_first', u'name_last': u'user2_last', u'role_type_cd': u'EMPLOYEE'},
        u'source': u'xmlfeed',
        u'role': {u'role_name': u'Faculty', u'canvas_role': u'Faculty', u'role_id': 2},
        u'seniority_sort': 3,
        u'user_id': u'34343434'
    },
    {
        u'profile': {u'name_first': u'user3_first', u'name_last': u'user3_last', u'role_type_cd': u'EMPLOYEE'},
        u'source': u'xmlfeed',
        u'role': {u'role_name': u'Faculty', u'canvas_role': u'Faculty', u'role_id': 2},
        u'seniority_sort': 2,
        u'user_id': u'34343434'
    },
    {
        u'profile': {u'name_first': u'user4_first', u'name_last': u'a_lname', u'role_type_cd': u'EMPLOYEE'},
        u'source': u'',
        u'role': {u'role_name': u'Teacher', u'canvas_role': u'teacher', u'role_id': 2},
        u'seniority_sort': None,
        u'user_id': u'56565656'
    },
    {
        u'profile': {u'name_first': u'user5_first', u'name_last': u'z_lname', u'role_type_cd': u'EMPLOYEE'},
        u'source': u'',
        u'role': {u'role_name': u'Teacher', u'canvas_role': u'teacher', u'role_id': 2},
        u'user_id': u'56565656'
    }
]

mock_school_info = {
    u'title_long': u'Harvard School of ABCs'
}

integration_test_course_info = {
    u'canvas_course_id': u'42',
    u'number_display': u'156208',
    u'school_display': u'Harvard College/Graduate School of Arts and Sciences'
}


@patch('course_info.views._api')
class DisplayTests(TestCase):
    """
    Widget and editor should display correct values in the returned HTML
    """
    api_course_mock = MagicMock(return_value=mock_course_info)
    api_school_mock = MagicMock(return_value=mock_school_info)
    api_course_mock_without_instructor = MagicMock(return_value=mock_course_info_without_instructor_display)
    api_course_mock_without_cid = MagicMock(return_value=mock_course_info_without_cid)

    api_staff_data = MagicMock(return_value=mock_staff_data_from_api)
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
        api_mock.get_course_info_by_canvas_course_id = self.api_course_mock
        api_mock.get_school_info = self.api_school_mock
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
        api_mock.get_course_info_by_canvas_course_id = self.api_course_mock
        api_mock.get_school_info = self.api_school_mock

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
        api_mock.get_course_info_by_canvas_course_id = self.api_course_mock
        query = 'f=title&f=term.display_name'
        client = Client(HTTP_REFERER=self.referer_string)
        response = client.get('/course_info/widget.html?{}'.format(query))
        self.assertContains(response, mock_course_info['title'])
        self.assertContains(response, mock_course_info['term']['display_name'])
        self.assertNotContains(response, mock_course_info['location'])

    def test_widget_partial_fields(self, api_mock):
        """ Widget should display only the fields with registrar data """
        api_mock.get_course_info_by_canvas_course_id = self.api_course_mock
        query = 'f=exam_group&f=term.display_name'
        client = Client(HTTP_REFERER=self.referer_string)
        response = client.get('/course_info/widget.html?{}'.format(query))
        self.assertContains(response, mock_course_info['term']['display_name'])
        self.assertNotContains(response, 'Field not populated by registrar')

    def test_editor_partial_field_data(self, api_mock):
        """ Editor should display all fields and note those without data """
        api_mock.get_course_info = self.api_course_mock
        post_body = {'lis_course_offering_sourcedid': '0000'}
        request = self.factory.post('/', post_body)
        response = editor(request)
        self.assertEqual(response.status_code, 200)
        # should have a checkbox for every configured field except for title,
        # which is automatically included, thus 8/9 fields
        self.assertContains(response, 'course_info_checkbox', count=len(mock_course_info.keys())-1)
        # fields with empty API return values should have a friendly message
        self.assertContains(response, 'Field not populated by registrar', count=2)

    def test_widget_alternate_instructor_display(self, api_mock):
        """ Widget should display instructor display from  teaching staff list
         if it is missing from registrar feed """
        api_mock.get_course_info_by_canvas_course_id = self.api_course_mock_without_instructor
        api_mock.get_course_info_instructor_list = self.api_staff_data
        query = 'f=exam_group&f=term.display_name&f=instructors_display'
        client = Client(HTTP_REFERER=self.referer_string)
        response = client.get('/course_info/widget.html?{}'.format(query))

        # assert that alternate method to fetch instructor is called  when get_course mock has missing instructor data
        api_mock.get_course_info_instructor_list.assert_called_with\
            (mock_course_info_without_instructor_display['course_instance_id'])

        # assert that the response contains 'Course Instructors' label  and mocked instructor name
        self.assertContains(response, 'Course Instructor(s):')
        self.assertContains(response, mock_staff_data_from_api[0]['profile']['name_first'])

    def test_sort_and_format_instructor_display_names(self,api_mock):
        """
        verify that the instructor names are sorted by role_id, seniority sort, last name
        and then formatted such that they are comma delimited String with an 'and' before
        that last user name.
        """

        expected_instructor_name_format = 'user1_first user1_last, user3_first' \
                                          ' user3_last, user2_first user2_last, ' \
                                          'user4_first a_lname and user5_first z_lname'
        result = sort_and_format_instructor_display(mock_staff_data_from_api)
        self.assertEqual(str(result), expected_instructor_name_format)

    def test_when_alternate_instructor_display_is_blank(self, api_mock):
        """ Widget should not display instructor name if it is missing from both sources """
        api_mock.get_course_info_by_canvas_course_id = self.api_course_mock_without_instructor
        api_mock.get_course_info_instructor_list = MagicMock(return_value=None)
        query = 'f=exam_group&f=term.display_name&f=instructors_display'
        client = Client(HTTP_REFERER=self.referer_string)
        response = client.get('/course_info/widget.html?{}'.format(query))
        # assert that alternate method to fetch instructor is called  when get_course mock has missing instructor data
        api_mock.get_course_info_instructor_list.assert_called_with\
            (mock_course_info_without_instructor_display['course_instance_id'])

        # assert that the response does not contain 'Course Instructors' label
        self.assertNotContains(response, 'Course Instructors:')

    def test_instructor_display_format_for_single_instructor(self, api_mock):

        staff_data = []
        # Add one user to list
        staff_data.append(mock_staff_data_from_api[0])
        expected_instructor_name_format = 'user1_first user1_last'
        result = sort_and_format_instructor_display(staff_data)
        self.assertEqual(str(result), expected_instructor_name_format)

    def test_instructor_display_format_for_two_instructors(self, api_mock):

        staff_data = []
        # Add 2 users  to list
        staff_data.append(mock_staff_data_from_api[0])
        staff_data.append(mock_staff_data_from_api[1])
        expected_instructor_name_format = 'user1_first user1_last and ' \
                                          'user2_first user2_last'
        result = sort_and_format_instructor_display(staff_data)
        self.assertEqual(str(result), expected_instructor_name_format)

    def test_people_api_not_invoked_if_cid_is_missing(self, api_mock):
        """ Api call to fetch instructors shouldn't be made even if
         instructor_display is one of the selected keys but  it is missing
        course_instance id  from registrar feed """
        api_mock.get_course_info_by_canvas_course_id = self.api_course_mock_without_cid
        query = 'f=exam_group&f=term.display_name&f=instructors_display'
        client = Client(HTTP_REFERER=self.referer_string)
        response = client.get('/course_info/widget.html?{}'.format(query))

        # assert that method to fetch instructor is not called  when get_course
        # mock has missing instructor data
        self.assertEqual(api_mock.get_course_info_instructor_list.call_count, 0)
        # assert that the response doesn't contains 'Course Instructors'label
        self.assertNotContains(response, 'Course Instructors:')


class IntegrationTests(TestCase):
    """
    These tests will ensure that the widget (and by extension, the iCommon API)
    is running as expected. Changes in the iCommons api structure will be caught.
    Please note that these tests may break if the canvas course id in
    integration_test_course_info is not a valid value present in course manager
    (as the api will not return expected values.
    """
    @classmethod
    def setUpClass(cls):
        super(IntegrationTests, cls).setUpClass()
        cls.base_url = 'https://canvas.dev.harvard.edu/'
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
