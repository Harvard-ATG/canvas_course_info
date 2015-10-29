import logging
import re
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.shortcuts               import render
from django.views.decorators.csrf   import csrf_exempt
from django.views.decorators.http   import require_GET, require_POST
from django.core.urlresolvers       import reverse
from django.conf                    import settings
from dce_lti_py.tool_config         import ToolConfig
from icommons                       import ICommonsApi

log = logging.getLogger(__name__)

_FIELD_LABEL_MAP = {
    'title': 'Course Title',
    'term.display_name': 'Term',
    'instructors_display': 'Course Instructors',
    'location': 'Location',
    'meeting_time': 'Meeting Time',
    'exam_group': 'Exam Group',
    'description': 'Course Description',
    'notes': 'Notes',
    'course.registrar_code_display': 'Course Code'
}


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

    custom_fields = {
        'include_text_option': 'false'
    }

    lti_tool_config = ToolConfig(
        title=app_config['name'],
        launch_url=launch_url,
        secure_launch_url=launch_url,
        extensions=extensions,
        description=app_config['description']
    )
    lti_tool_config.set_ext_param('canvas.instructure.com', 'custom_fields', custom_fields)

    return HttpResponse(lti_tool_config.to_xml(), content_type='text/xml')


@login_required
@require_POST
@csrf_exempt
def lti_launch(request):
    return editor(request)


def _get_course_code(value):
    try:
        # Extracts the course number (the last substring) from typical display codes
        course_code = value.split()[-1]
    except IndexError:
        # If the display code is atypical, show the whole thing
        course_code = value
    return course_code


def _get_field_value_for_key(key, course_info):
    try:
        if '.' in key:
            keyparts = key.split('.')
            value = course_info[keyparts[0]][keyparts[1]]
        else:
            value = course_info[key]
        if key == 'course.registrar_code_display':
            value = _get_course_code(value)
    except KeyError:
        value = ''
    return value


def __course_context(request, keys, show_empty_fields=False, **kwargs):
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
        value = _get_field_value_for_key(key, course_info)
        if value or show_empty_fields:
            field = {'key': key, 'label': _FIELD_LABEL_MAP[key], 'value': value}
            context['fields'].append(field)

    try:
        school_info = ICommonsApi.from_request(request).get_school_info(course_info['course']['school_id'])
        school_title = school_info['title_long']
    except KeyError:
        school_title = ''

    context['school_title'] = school_title

    return context


@require_GET
def widget(request):
    """
    Returns course information (the results of an iCommons API query), called
    from an embedded iframe in Canvas. Note that this is NOT a secure endpoint,
    and spoofing HTTP_REFERER makes this information available for any course,
    so if anything is added of a sensitive nature then this may need a different
    implementation.
    """
    referer = request.META.get('HTTP_REFERER', '')
    try:
        canvas_course_id = re.match('^.+/courses/(?P<canvas_course_id>\d+)(?:$|.+$)', referer).group('canvas_course_id')
    except AttributeError:
        canvas_course_id = None

    # field names are sent as URL params f=field_name when widget is 'launched'
    field_names = request.GET.getlist('f')
    course_context = __course_context(request, field_names, canvas_course_id=canvas_course_id)

    populated_fields = [f for f in course_context['fields'] if f['value']]
    course_context['show_registrar_fields_message'] = len(populated_fields) < len(field_names)

    return render(request, 'course_info/widget.html', course_context)


def editor(request):
    # Use an example course for development if one is configured in settings
    course_instance_id = getattr(settings, 'COURSE_INSTANCE_ID', None)
    if not course_instance_id:
        # "lis" appears to be a deliberate misspelling
        course_instance_id = request.POST.get('lis_course_offering_sourcedid')

    # The values we will want to display, in the order we wish them to appear
    field_names = [
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

    course_context = __course_context(request, field_names, True, course_instance_id=course_instance_id)

    course_context['launch_presentation_return_url'] = request.POST.get('launch_presentation_return_url')
    course_context['textarea_fields'] = ['description', 'notes']

    return render(request, 'course_info/editor.html', course_context)
