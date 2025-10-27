import logging
import re
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET

from .icommons import ICommonsApi, ICommonsApiValidationError

logger = logging.getLogger(__name__)

_api = ICommonsApi()
_INSTRUCTORS_DISPLAY_FIELD = "instructors_display"
_FIELD_DETAILS = {
    "title": {"label": "Course Title", "order": 1},
    "course.registrar_code_display": {"label": "Course Code", "order": 2},
    "term.display_name": {"label": "Term", "order": 3},
    _INSTRUCTORS_DISPLAY_FIELD: {"label": "Course Instructor(s)", "order": 4},
    "location": {"label": "Location", "order": 5},
    "meeting_time": {"label": "Meeting Time", "order": 6},
    "exam_group": {"label": "Exam Group", "order": 7},
    "description": {"label": "Course Description", "order": 8, "contains_html": True},
    "notes": {"label": "Notes", "order": 9, "contains_html": True},
}
_ORDERED_FIELD_NAMES = [
    f[0] for f in sorted(iter(_FIELD_DETAILS.items()), key=lambda f: f[1]["order"])
]
_REFERER_COURSE_ID_RE = re.compile(r"^.+/courses/(?P<canvas_course_id>\d+)(?:$|.+$)")


def lti_launch(request: HttpRequest) -> HttpResponse:
    # """
    # Called from the LTI 1.3 launch handler after Canvas initiates the tool launch.
    # Renders the Course Info editor view inside the Canvas iframe.
    # """
    # logger.info("Handling Course Info LTI launch")

    # course_instance_id = request.POST.get("lis_course_offering_sourcedid")
    # course_context = _course_context(
    #     request, _ORDERED_FIELD_NAMES, True, course_instance_id=course_instance_id
    # )

    # course_context["launch_presentation_return_url"] = request.POST.get(
    #     "launch_presentation_return_url"
    # )
    # course_context["canvas_course_id"] = request.POST.get("custom_canvas_course_id")
    # return render(request, "course_info/editor.html", course_context)
    return editor(request)


def editor(request):
    logger.debug("EDITOR: {}".format(request.POST))
    course_instance_id = request.POST.get("lis_course_offering_sourcedid")

    course_context = _course_context(
        request, _ORDERED_FIELD_NAMES, True, course_instance_id=course_instance_id
    )
    course_context["launch_presentation_return_url"] = request.POST.get(
        "launch_presentation_return_url"
    )
    course_context["canvas_course_id"] = request.POST.get("custom_canvas_course_id")
    return render(request, "course_info/editor.html", course_context)


def _get_course_code(value):
    try:
        return value.split()[-1]
    except IndexError:
        return value


def _get_field_value_for_key(key, course_info):
    try:
        if "." in key:
            a, b = key.split(".")
            value = course_info[a][b]
        else:
            value = course_info[key]
        if key == "course.registrar_code_display":
            value = _get_course_code(value)
    except KeyError:
        value = ""
    return value


def _course_context(
    request,
    requested_keys,
    show_empty_fields=False,
    course_instance_id=None,
    canvas_course_id=None,
):
    if course_instance_id and isinstance(course_instance_id, str):
        try:
            course_instance_id = int(float(course_instance_id))
        except ValueError:
            logger.debug(f"non-numeric course_instance_id: {course_instance_id}")
            course_instance_id = None

    course_info = {}
    try:
        if course_instance_id:
            course_info = _api.get_course_info(course_instance_id)
        elif canvas_course_id:
            course_info = _api.get_course_info_by_canvas_course_id(canvas_course_id)
            if course_info.get("course_instance_id"):
                course_instance_id = int(float(course_info["course_instance_id"]))
            logger.debug(f"course instance id from course info is {course_instance_id}")
    except ICommonsApiValidationError:
        pass

    context = {
        "fields": [],
        "course_instance_id": course_info.get("course_instance_id"),
        "canvas_course_id": course_info.get("canvas_course_id"),
    }

    if (_INSTRUCTORS_DISPLAY_FIELD in requested_keys) and not course_info.get(
        _INSTRUCTORS_DISPLAY_FIELD
    ):
        try:
            if not course_instance_id:
                course_instance_id = course_info.get("course_instance_id")
            if course_instance_id:
                instructors = _api.get_course_info_instructor_list(course_instance_id)
                if instructors:
                    display = sort_and_format_instructor_display(instructors)
                    course_info[_INSTRUCTORS_DISPLAY_FIELD] = display
        except (ICommonsApiValidationError, KeyError):
            pass

    for key in [k for k in _ORDERED_FIELD_NAMES if k in requested_keys]:
        value = _get_field_value_for_key(key, course_info)
        if value or show_empty_fields:
            field = {"key": key, "label": _FIELD_DETAILS[key]["label"], "value": value}
            if _FIELD_DETAILS[key].get("contains_html"):
                field["value"] = mark_safe(field["value"])
            context["fields"].append(field)

    try:
        school_info = _api.get_school_info(course_info["course"]["school_id"])
        context["school_title"] = school_info["title_long"]
    except (ICommonsApiValidationError, KeyError):
        context["school_title"] = ""

    return context


@require_GET
def widget(request: HttpRequest) -> HttpResponse:
    referer = request.META.get("HTTP_REFERER", "")
    logger.debug(f"referer: {referer}")
    try:
        canvas_course_id = _REFERER_COURSE_ID_RE.match(referer).group(
            "canvas_course_id"
        )
    except AttributeError:
        canvas_course_id = request.GET.get("backup_canvas_course_id")

    course_instance_id = request.GET.get("backup_course_instance_id")
    field_names = [f for f in request.GET.getlist("f") if f in _FIELD_DETAILS.keys()]

    course_context = _course_context(
        request, field_names, canvas_course_id=canvas_course_id
    )
    if not course_context.get("course_instance_id"):
        course_context = _course_context(
            request, field_names, course_instance_id=course_instance_id
        )

    populated_fields = [f for f in course_context["fields"] if f["value"]]
    course_context["show_registrar_fields_message"] = len(populated_fields) < len(
        field_names
    )
    course_context["referer"] = referer
    course_context["build_info"] = settings.BUILD_INFO
    return render(request, "course_info/widget.html", course_context)


def sort_and_format_instructor_display(instructors):
    instructors = [x for x in instructors if x.get("profile")]
    instructors.sort(
        key=lambda x: (
            x.get("role", {}).get("role_id") != 19,
            x.get("role", {}).get("role_id"),
            100 if x.get("seniority_sort") is None else x.get("seniority_sort", {}),
            x.get("profile", {}).get("name_last"),
        )
    )
    names = [get_display_name(p) for p in instructors]
    if len(names) == 1:
        return names[0]
    elif len(names) == 2:
        return " and ".join(names)
    elif len(names) > 2:
        return ", ".join(names[:-1]) + " and " + names[-1]
    return ""


def get_display_name(person):
    if person:
        return f"{person.get('profile', {}).get('name_first', '')} {person.get('profile', {}).get('name_last', '')}"
    return ""
