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
    print("course_instance_id: " + course_instance_id)
    keys = ['title', 'course.registrar_code_display', 'term.display_name', 'instructors_display', 'location',
            'meeting_time', 'description', 'notes']
    course_context = __course_context(request, course_instance_id, keys)
    # course_context['line_guestimate'] =keys*2
    course_context['launch_presentation_return_url'] = request.POST.get('launch_presentation_return_url')
    return render(request, 'course_info/editor.html', course_context)


def oembed_handler(request):  # TODO
    # this is the view that is going to handle the huge url Canvas throws at us,
    # returning oembed JSON or XML for the Canvas Rich Text Editor

    print("HEY WHAT'S UP HELLO")

    #course_instance_id = request.GET.get('course_instance_id')
    #course_info = ICommonsApi.from_request(request).get_course_info(course_instance_id)
    #print(course_info)
    return HttpResponse("<p>Look under the Hood, brah</p>", content_type="text/xml")
    #return(widget(request))

    # # for now this is identical to widget(request)
    # course_instance_id = request.GET.get('course_instance_id')
    # # return render(request.GET.get('url'), 'course_info/widget.html',
    # #               __course_context(request,course_instance_id,
    # #                 request.GET.getlist('f')))
    # #return render(request, 'course_info/widget.html', course_context)
    #






    # course_instance_id = request.GET.get('course_instance_id')
    # render(request, 'course_info/widget.html', __course_context(request, course_instance_id, request.GET.getlist('f')))
    #
    #return HttpResponse(course_html, content_type="text/html")

    # data = {
    #     "cache_age": "3153600000",
    #     "url": "https:\/\/twitter.com\/jack\/statuses\/20",
    #     "height": "null",
    #     "provider_url": "https:\/\/twitter.com",
    #     "provider_name": "Twitter",
    #     "author_name": "Jack",
    #     "version": "1.0",
    #     "author_url": "https:\/\/twitter.com\/jack",
    #     "type": "rich",
    #     "html": "\u003Cblockquote class=\"twitter-tweet\"\u003E\u003Cp lang=\"en\" dir=\"ltr\"\u003Ejust setting up my twttr\u003C\/p\u003E&mdash; Jack (@jack) \u003Ca href=\"https:\/\/twitter.com\/jack\/status\/20\"\u003EMarch 21, 2006\u003C\/a\u003E\u003C\/blockquote\u003E\n\u003Cscript async src=\"\/\/platform.twitter.com\/widgets.js\" charset=\"utf-8\"\u003E\u003C\/script\u003E",
    #     "width": 550
    # }



    #response = json.JSONEncoder().encode(data)
    # return HttpResponse(response, content_type="application/json")

    #return render(request, 'course_info/widget.html')


