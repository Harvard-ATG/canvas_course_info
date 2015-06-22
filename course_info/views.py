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
import cgi
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
    print("course_info (icommons): " + course_info)
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
    context['fields'] = __mungeFields(context['fields'])
    return context


def __mungeFields(fields):
    for field in fields:
        if field['key'] == 'notes':
            field['value'] = '<b>Note:</b> ' + field['value']
        elif field['key'] == 'location':
            field['value'] = '<b>Location:</b> ' + field['value']
        elif field['key'] == 'meeting_time':
            field['value'] = '<b>Meeting Time:</b> ' + field['value']
        field['value'] = field['value'].replace('<br /> <br />', '<br />')
    return fields


@require_GET
def widget(request):
    course_instance_id = request.GET.get('course_instance_id')
    return render(request, 'course_info/widget.html',
                  __course_context(request, course_instance_id,
                                   request.GET.getlist('f')))


def editor(request):
    if settings.COURSE_INSTANCE_ID:
        # course_instance_id = "312976"
        course_instance_id = settings.COURSE_INSTANCE_ID
    else:
        course_instance_id = request.POST.get('lis_course_offering_sourcedid')
    #print("course_instance_id: " + course_instance_id)
    keys = ['title', 'course.registrar_code_display', 'term.display_name', 'instructors_display', 'location',
            'meeting_time', 'description', 'notes']
    course_context = __course_context(request, course_instance_id, keys)
    # course_context['line_guestimate'] =keys*2
    course_context['launch_presentation_return_url'] = request.POST.get('launch_presentation_return_url')
    return render(request, 'course_info/editor.html', course_context)


def oembed_handler(request):  # TODO
    # this is the view that is going to handle the huge url Canvas throws at us,
    # returning oembed JSON or XML for the Canvas Rich Text Editor


    #print("OEMBED CALL")

    dynamic_var = 2 + 3

    # http://stackoverflow.com/a/2077410
    #TODO: see if we actually need this. Python's already pretty good with strings
    def escape(t):
        # if we need more: .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (t.replace('"', "'")).replace("&", "&amp;")

    #request

    #course_instance_id = request.GET.get('course_instance_id')
    url = request.GET.get('url')

    parsed_url = urlparse.urlparse(url)
    print()
    print(parsed_url)

    parsed_qs = urlparse.parse_qs(escape(parsed_url.query))
    requested_info = parsed_qs['f']
    course_instance_id = parsed_qs['course_instance_id']
    print(course_instance_id)
    print(requested_info)
    print()

    #this is where we need to be specific.
    # we want the scripts but not the head tags...
    #could use request.body
    dynamic_string = render(request, 'course_info/widget.html', __course_context(request, course_instance_id, requested_info))#request.GET.getlist('f')))

    #print(escape(str(dynamic_string)))
    #print(dynamic_string)

    # why the hell does this work:
    # http://localhost:8000/course_info/oembed&url=http://localhost:8000/course_info/widget.html?course_instance_id=312976&amp;f=title&amp;f=course.registrar_code_display&amp;f=term.display_name&amp;f=instructors_display&amp;f=location&amp;f=meeting_time&amp;f=description&amp;f=notes&page_view_id=414bbdab-b559-41e8-a712-1370d47c5a24
    # but you get nothing in the table when it comes from Canvas?
    # I think it has something to do with Canvas passing widget.html a more complicated request from its own servers

    html_string = str(dynamic_string)
    #print(html_string)

    demonstration_data = "<h3> h3:" +  str(11 << 20) + "</h3>"

    demonstration_string = \
        "<div>Hey What's up Hello" \
            "<h1>Course Info</h1>" \
            "<br/>" \
            "<div id='course_info_embed'>" + str(demonstration_data) + "</div>" \
        "</div>" \

    response = json.JSONEncoder().encode({
        "html": demonstration_string + html_string,
        "url": "http://www.TODO.com",
        "height": "null",
        "provider_url": "http://www.TODO.com",
        "provider_name": "TODO",
        "author_name": "TODO",
        "version": "1.0",
        "author_url": "http://www.TODO.com",
        "type": "rich",
        "width": 550
    })
    return HttpResponse(response, content_type="application/json")