import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.core.urlresolvers import reverse
from django.conf import settings
from dce_lti_py.tool_config import ToolConfig
from icommons import ICommonsApi
import json
import urlparse

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


@login_required
@require_POST
@csrf_exempt
def lti_launch(request):
    return editor(request)


def __course_context(request, course_instance_id, keys):
    key2class = {
        'title': 'course_info_textHeader1',
        'course.registrar_code_display': 'course_info_textHeader2',
        'term.display_name': 'course_info_textHeader2',
        'instructors_display': 'course_info_textHeader2',
        'location': 'course_info_textHeader2',
        'meeting_time': 'course_info_textHeader2'
    }
    course_info = ICommonsApi.from_request(request).get_course_info(course_instance_id)
    context = {'fields': [], 'course_instance_id': course_instance_id}
    for key in keys:
        if '.' in key:
            keyparts = key.split('.')
            field = {'key': key, 'value': course_info[keyparts[0]][keyparts[1]]}
        else:
            field = {'key': key, 'value': course_info[key]}
        field['class'] = ''
        if key in key2class:
            field['class'] = key2class[key]
        context['fields'].append(field)

    school_info = ICommonsApi.from_request(request).get_school_info("hds")
    context['fields'] = __mungeFields(context['fields'], school_info['title_long'])
    return context

def __mungeFields(fields, school_name):
    # Could possibly sneak in some more inline styles here
    def stern(value, default):
        # special ternary to simplify the logic below
        # deals with blank fields
        if value == u' ' or value == u'' or value == '' or value == ' ':
            return default
        else:
            return value

    for field in fields:
        if field['key'] == 'title':
            field['value'] = '<h1>' + field['value'] + "</h1>"
        elif field['key'] == 'course.registrar_code_display':
            #TODO: make sure this works alright with all courses and schools
            course_number = stern(field['value'], "Unknown").split()[-1]
            field['value'] = school_name + ": " + course_number
        elif field['key'] == 'term.display_name':
            field['value'] = field['value'] #include this? '<b>Term:</b> '
        elif field['key'] == 'instructors_display':
            field['value'] = field['value'] #include this? '<b>Course Instructor(s):</b> '
        elif field['key'] == 'location':
            field['value'] = '<b>Location:</b> ' + stern(field['value'], 'Unknown')
        elif field['key'] == 'meeting_time':
            field['value'] = '<b>Meeting Time:</b> ' + stern(field['value'], 'Unknown')
        elif field['key'] == 'exam_group':
            field['value'] = '<b>Exam Group: </b> ' + stern(field['value'], 'Unknown')
        elif field['key'] == 'description':
            field['value'] = '<b>Course Description:</b> ' + stern(field['value'], 'None')
        elif field['key'] == 'notes':
            field['value'] = '<b>Note:</b> ' + field['value']
        field['value'] = field['value'].replace('<br /> <br />', '<br />')

    return fields


@require_GET
def widget(request):
    course_instance_id = request.GET.get('course_instance_id')
    context = __course_context(request, course_instance_id, request.GET.getlist('f'))

    # Why doesn't this work? I want to take __mungeFields out from the context creator so
    # it doesn't mess up the editor but it somehow doesn't work like this
    #context['fields'] = __mungeFields(context['fields'])
    return render(request, 'course_info/widget.html', context)


def editor(request):
    if settings.COURSE_INSTANCE_ID:
        # course_instance_id = "312976"
        course_instance_id = settings.COURSE_INSTANCE_ID
    else:
        course_instance_id = request.POST.get('lis_course_offering_sourcedid')
    keys = ['title', 'course.registrar_code_display', 'term.display_name', 'instructors_display', 'location',
            'meeting_time', 'exam_group', 'description', 'notes']
    course_context = __course_context(request, course_instance_id, keys)
    # course_context['line_guestimate'] =keys*2
    course_context['launch_presentation_return_url'] = request.POST.get('launch_presentation_return_url')

    # An ugly, temporary fix to the munge issue - for some reason I can't only munge in the widget view.
    def clean(t):
        return t.replace("<b>", "").replace("</b>","").replace("<h1>","").replace("</h1>","")

    for field in course_context['fields']:
        field['value'] = clean(field['value'])

    return render(request, 'course_info/editor.html', course_context)


def oembed_handler(request):  # TODO
    # This view handles the huge url Canvas throws at us, reconciles it with iCommons,
    # and returns oEmbed JSON for the Canvas Rich Text Editor
    # www.oembed.com

    url = request.GET.get('url')
    parsed_url = urlparse.urlparse(url)
    parsed_qs = urlparse.parse_qs(parsed_url.query)
    requested_info = parsed_qs['f'] #get all the selected checkboxes from the editor view
    course_instance_id = parsed_qs['course_instance_id'][0]
    course_info_context = __course_context(request, course_instance_id, requested_info)

    # unfortunately the content-type is going to display because of the way the render function works
    # hacky workaround is to remove the first 13 characters from the html_string. Sorry
    html_string = str(render(request, 'course_info/widget.html', course_info_context, content_type= " "))
    html_string = html_string[13:]

    #Returning just enough oEmbed to satisfy Canvas
    response = json.JSONEncoder().encode({
        "html": html_string,
        "type": "rich"
    })
    return HttpResponse(response, content_type="application/json")