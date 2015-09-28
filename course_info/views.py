import logging
import json
import urlparse
import re
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.shortcuts               import render, redirect
from django.views.decorators.csrf   import csrf_exempt
from django.views.decorators.http   import require_GET, require_POST
from django.core.urlresolvers       import reverse
from django.conf                    import settings
from dce_lti_py.tool_config         import ToolConfig
from icommons                       import ICommonsApi
from django.template.defaultfilters import striptags

log = logging.getLogger(__name__)


@require_GET
def tool_config(request):
    app_config = settings.LTI_APPS['course_info']

    launch_url = request.build_absolute_uri(reverse('lti_launch'))

    editor_settings = {
        'enabled': 'true',
        'text': app_config['menu_title'],
        'width': app_config['selection_width'],
        'height': app_config['selection_height'],
        'icon_url': request.build_absolute_uri(app_config['icon_url']),
        'url': launch_url
    }

    extensions = {
        app_config['extensions_provider']: {
            'editor_button': editor_settings,
            'tool_id': app_config['id'],
            'privacy_level': app_config['privacy_level']
        }
    }

    lti_tool_config = ToolConfig(
        title=app_config['name'],
        launch_url=launch_url,
        secure_launch_url=launch_url,
        extensions=extensions,
        description=app_config['description']
    )

    return HttpResponse(lti_tool_config.to_xml(), content_type='text/xml')


#@login_required
@require_POST
@csrf_exempt
def lti_launch(request):
    return editor(request)


def __course_context(request, keys, show_empty_field=False, **kwargs):
    key2class = {
        'title': 'list-group-item-info'
    }
    course_instance_id = kwargs.get('course_instance_id')
    canvas_course_id = kwargs.get('canvas_course_id')
    course_info = {}
    if course_instance_id:
        course_info = ICommonsApi.from_request(request).get_course_info(course_instance_id)
    elif canvas_course_id:
        course_info = ICommonsApi.from_request(request).get_course_info_by_canvas_course_id(canvas_course_id)
    context = {
        'fields': [],
        'course_instance_id': course_info.get('course_instance_id'),
        'canvas_course_id': course_info.get('canvas_course_id')
    }
    for key in keys:
        try:
            if '.' in key:
                keyparts = key.split('.')
                value = course_info[keyparts[0]][keyparts[1]]
            else:
                value = course_info[key]
        except KeyError:
            value = ''
        field = {'key': key, 'value': value, 'class': ''}
        if key in key2class:
            field['class'] = key2class[key]
        context['fields'].append(field)

    try:
        school_info = ICommonsApi.from_request(request).get_school_info(course_info['course']['school_id'])
        school_title = school_info['title_long']
    except KeyError:
        school_title = ''

    context['fields'] = __mungeFields(context['fields'], school_title, show_empty_field)
    return context


def __mungeFields(fields, school_name, show_empty_field=False, **kwargs):
    # This method takes in all the iCommons fields, and formats those that we'd like to display
    # Could possibly sneak in some more inline styles here

    def field_value_display(value, label, show_empty_field=False, show_label_if_not_empty=True):
        """
        Takes a course info field value, optional label and other options and returns a formatted
        version of the value for display in the UI

        :param value: The value to be displayed
        :param label: A field label for the value
        :param show_empty_field: If True, display the field label and a generic message, otherwise return ''
        :param show_label_if_not_empty: If True, always show the given label, otherwise only show the label
               if the value is empty
        :return: The formatted field value
        """
        if value:
            if label and show_label_if_not_empty:
                value = label + value
        elif show_empty_field:
            value = 'Field not populated by registrar'
            if label:
                value = label + value

        return value

    for field in fields:
        if field['key'] == 'title':
            field['value'] = "<h4>%s</h4>" % field_value_display(field['value'], "Course Title: ", True, False)
        elif field['key'] == 'term.display_name':
            field['value'] = field_value_display(field['value'], "<b>Term:</b> ", show_empty_field, False)
        elif field['key'] == 'instructors_display':
            field['value'] = field_value_display(field['value'], "<b>Instructors:</b> ", show_empty_field, False)
        elif field['key'] == 'location':
            field['value'] = field_value_display(field['value'], "<b>Location:</b> ", show_empty_field)
        elif field['key'] == 'meeting_time':
            field['value'] = field_value_display(field['value'], "<b>Meeting Time:</b> ", show_empty_field)
        elif field['key'] == 'exam_group':
            field['value'] = field_value_display(field['value'], "<b>Exam Group:</b> ", show_empty_field)
        elif field['key'] == 'description':
            field['value'] = field_value_display(field['value'], "<b>Course Description:</b> ", show_empty_field)
        elif field['key'] == 'notes':
            field['value'] = field_value_display(field['value'], "<b>Notes:</b> ", show_empty_field)
        elif field['key'] == 'course.registrar_code_display':
            try:
                # Extracts the course number (the last substring) from typical display codes
                field['value'] = field_value_display(field['value'].split()[-1], school_name + ": ", show_empty_field)
            except IndexError:
                # If the display code is atypical, show the whole thing
                field['value'] = field_value_display(field['value'], school_name + ": ", show_empty_field)
        field['value'] = field['value'].replace('<br /> <br />', '<br />')

    return fields


@require_GET
def widget(request):
    referer = request.META.get('HTTP_REFERER', '')
    try:
        canvas_course_id = re.match('^.+/courses/(?P<canvas_course_id>\d+)(?:$|.+$)', referer).group('canvas_course_id')
    except AttributeError:
        canvas_course_id = None
    context = __course_context(request, request.GET.getlist('f'), canvas_course_id=canvas_course_id)
    return render(request, 'course_info/widget.html', context)


def editor(request):
    # Use an example course for development if one is configured in settings
    course_instance_id = getattr(settings, 'COURSE_INSTANCE_ID', None)
    if not course_instance_id:
        # "lis" appears to be a deliberate misspelling
        course_instance_id = request.POST.get('lis_course_offering_sourcedid')

    # The values we will want to display
    keys = [
        'title',
        'course.registrar_code_display',
        'term.display_name',
        'instructors_display',
        'location',
        'meeting_time',
        'exam_group',
        'description',
        'notes'
    ]

    course_context = __course_context(request, keys, True, course_instance_id=course_instance_id)

    # this is likely a remnant of the iFrame resize struggle
    #course_context['line_guestimate'] =keys*2

    course_context['launch_presentation_return_url'] = request.POST.get('launch_presentation_return_url')
    course_context['should_offer_text'] = settings.OFFER_TEXT

    # scrub HTML tags (just for the editor view)
    # this could also be done in the django template
    for field in course_context['fields']:
        field['value'] = striptags(field['value'])

    return render(request, 'course_info/editor.html', course_context)


def oembed_handler(request):
    '''
        This view handles the huge url Canvas throws at us, reconciles it with iCommons,
        and returns oEmbed JSON for the Canvas Rich Text Editor
        See the README for more information - how oEmbed works, terminology, etc.
        www.oembed.com
    '''

    # the url we need to act on is a parameter in Canvas' oEmbed request
    url = request.GET.get('url')

    # move from string functionality to url functionality
    parsed_url = urlparse.urlparse(url)

    # load the url parameters/queries into a dictionary
    parsed_qs = urlparse.parse_qs(parsed_url.query)

    # get the selected checkboxes and course id
    requested_info = parsed_qs['f']
    referer = request.META.get('HTTP_REFERER', '')
    try:
        canvas_course_id = re.match('^.+/courses/(?P<canvas_course_id>\d+)(?:$|.+$)', referer).group('canvas_course_id')
    except AttributeError:
        canvas_course_id = None

    course_info_context = __course_context(request, requested_info, canvas_course_id=canvas_course_id)

    # put the rendered html in a string, so that it can be returned in the oEmbed JSON
    # the content_type = " " is included so there will be a fixed amount of characters to delete later (13)
    html_string = str(render(request, 'course_info/widget.html', course_info_context, content_type = " "))

    # unfortunately 'Content-Type: ' is going to be included in html_string because of the way
    # the "render" function works. Workaround is to remove it with the regex substitution function
    # Further down the line, this method could also be used to insert styles or other dynamic content
    html_string = re.sub('Content-Type: ', '', html_string)

    # Return just enough oEmbed to satisfy Canvas
    # More can be included if so desired (title, width, height, other metadata, etc)
    oEmbed_response = json.JSONEncoder().encode({
        "html": html_string,
        "type": "rich"
    })
    return HttpResponse(oEmbed_response, content_type="application/json")
