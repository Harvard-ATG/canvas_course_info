import logging
import re

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from pylti1p3.deep_link_resource import DeepLinkResource
from lti_tool.constants import SESSION_KEY
from lti_tool.types import LtiLaunch
from lti_tool.utils import get_launch_from_request, sync_data_from_launch
from lti_tool.views import LtiLaunchBaseView

from .icommons import ICommonsApi, ICommonsApiValidationError
from .utils import (
    get_canvas_course_id_from_request,
    get_course_instance_id_from_request,
)

_api = ICommonsApi()
_logger = logging.getLogger(__name__)
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

class ApplicationLaunchView(LtiLaunchBaseView):
    def post(self, request, *args, **kwargs):
        request.session.clear()
        lti_launch = get_launch_from_request(request)
        sync_data_from_launch(lti_launch, lti1p1_secret=None)
        self.launch_setup(request, lti_launch)
        if not lti_launch.deployment.is_active:
            return self.handle_inactive_deployment(request, lti_launch)
        request.session[SESSION_KEY] = lti_launch.get_launch_id()
        request.lti_launch = lti_launch
        if lti_launch.is_resource_launch:
            return self.handle_resource_launch(request, lti_launch)
        if lti_launch.is_deep_link_launch:
            return self.handle_deep_linking_launch(request, lti_launch)

    def handle_resource_launch(
        self, request: HttpRequest, lti_launch: LtiLaunch
    ) -> HttpResponse:
        return redirect(reverse("course_info:editor"))

    def handle_deep_linking_launch(
        self, request: HttpRequest, lti_launch: LtiLaunch
    ) -> HttpResponse:
        return redirect(reverse("course_info:editor"))

    def launch_setup(self, request: HttpRequest, lti_launch: LtiLaunch) -> None:
        if not lti_launch.deployment.is_active:
            lti_launch.deployment.is_active = True
            lti_launch.deployment.save()


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
        if "." in key:
            keyparts = key.split(".")
            value = course_info[keyparts[0]][keyparts[1]]
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
    if course_instance_id:
        if isinstance(course_instance_id, str):
            try:
                course_instance_id = int(float(course_instance_id))
            except ValueError:
                _logger.debug(
                    "non-numeric course_instance_id: {}".format(course_instance_id)
                )
                course_instance_id = None

    course_info = {}
    try:
        if course_instance_id:
            course_info = _api.get_course_info(course_instance_id)
        elif canvas_course_id:
            course_info = _api.get_course_info_by_canvas_course_id(canvas_course_id)
            if course_info.get("course_instance_id"):
                course_instance_id = int(float(course_info.get("course_instance_id")))

            _logger.debug(
                "course instance id from course info is {}".format(course_instance_id)
            )

    except ICommonsApiValidationError:
        # this is logged in the icommons library, and course_info is already
        # set to {}
        pass

    context = {
        "fields": [],
        "course_instance_id": course_info.get("course_instance_id"),
        "canvas_course_id": course_info.get("canvas_course_id"),
    }

    # if instructor_display is one of the selected keys and instructor data is missing
    # from registrar feed, then fetch teaching staff names(from course staff table)
    if (_INSTRUCTORS_DISPLAY_FIELD in requested_keys) and not course_info.get(
        _INSTRUCTORS_DISPLAY_FIELD
    ):
        try:
            if not course_instance_id:
                course_instance_id = course_info.get("course_instance_id")

            # Proceed to fetch course staff from api only if there is a valid course_instance_id
            if course_instance_id:
                course_instructor_list = _api.get_course_info_instructor_list(
                    course_instance_id
                )
                if course_instructor_list:
                    instructor_display = sort_and_format_instructor_display(
                        course_instructor_list
                    )
                    course_info[_INSTRUCTORS_DISPLAY_FIELD] = instructor_display
        except (ICommonsApiValidationError, KeyError):
            # do nothing, instructor_display is set to ''
            pass
    # add field to context in order of its preferred display on the template
    for key in [k for k in _ORDERED_FIELD_NAMES if k in requested_keys]:
        value = _get_field_value_for_key(key, course_info)
        if value or show_empty_fields:
            field = {"key": key, "label": _FIELD_DETAILS[key]["label"], "value": value}
            if _FIELD_DETAILS[key].get("contains_html", False):
                field["value"] = mark_safe(field["value"])
            context["fields"].append(field)

    try:
        school_info = _api.get_school_info(course_info["course"]["school_id"])
        school_title = school_info["title_long"]
    except (ICommonsApiValidationError, KeyError):
        school_title = ""

    context["school_title"] = school_title

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
    referer = request.META.get("HTTP_REFERER", "")
    _logger.debug("referer: {}".format(request.META.get("HTTP_REFERER")))
    try:
        canvas_course_id = _REFERER_COURSE_ID_RE.match(referer).group(
            "canvas_course_id"
        )
    except AttributeError:
        canvas_course_id = request.GET.get("backup_canvas_course_id")

    course_instance_id = request.GET.get("backup_course_instance_id")

    # field names are sent as URL params f=field_name when widget is 'launched'
    field_names = [f for f in request.GET.getlist("f") if f in _FIELD_DETAILS.keys()]

    # get the course_context based on course_instance_id if we can't get one by canvas course ID
    course_context = _course_context(
        request, field_names, canvas_course_id=canvas_course_id
    )
    if not course_context or not course_context.get("course_instance_id"):
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


@login_required
def editor(request):
    _logger.debug("EDITOR: lti_launch=%s", getattr(request, "lti_launch", None))

    course_instance_id = None
    canvas_course_id = None

    lti_launch_obj = getattr(request, "lti_launch", None)
    if lti_launch_obj is not None and not lti_launch_obj.is_absent:
        course_instance_id = get_course_instance_id_from_request(request)
        canvas_course_id = get_canvas_course_id_from_request(request)

    course_context = _course_context(
        request, _ORDERED_FIELD_NAMES, True, course_instance_id=course_instance_id
    )
    course_context["canvas_course_id"] = canvas_course_id
    return render(request, "course_info/editor.html", course_context)


@login_required
@csrf_exempt
def deep_link_return(request):
    """
    Handles the editor form submission for LTI 1.3 deep linking.
    Builds a widget URL from the selected fields and returns a deep link response
    that Canvas uses to embed the widget iframe in the rich text editor.
    """
    lti_launch_obj = getattr(request, "lti_launch", None)
    if lti_launch_obj is None or lti_launch_obj.is_absent:
        return HttpResponse("No active LTI session.", status=403)

    canvas_course_id = request.POST.get("canvas_course_id", "")
    course_instance_id = request.POST.get("course_instance_id", "")
    field_keys = request.POST.getlist("f")

    widget_url = request.build_absolute_uri(reverse("course_info:widget"))
    params = "&".join(["f=title"] + [f"f={k}" for k in field_keys])
    if canvas_course_id:
        params += f"&backup_canvas_course_id={canvas_course_id}"
    if course_instance_id:
        params += f"&backup_course_instance_id={course_instance_id}"
    widget_url = f"{widget_url}?{params}"

    resource = (
        DeepLinkResource()
        .set_url(widget_url)
        .set_title("Course Info")
    )
    return lti_launch_obj.deep_link_response([resource])


def sort_and_format_instructor_display(course_instructor_list):
    """
    Returns a sorted  string  sorted by  the instructors by role_id, seniority sort, last name
    and then formatted such that it appears as a comma delimited String with an 'and' before that last user.
    # Eg: User1, User2 and User3.
    """
    # First, filter out any instructor entries that do not have a profile - fixes TLT-2976
    course_instructor_list = [x for x in course_instructor_list if x.get("profile")]

    # Note:  when seniority_sort is None, it was getting precedence over 1(eg: null, 1, 2).  So in such cases,
    # it is being set to a large number (picked 100) so it is lower in the sorting order. [1, 2, ...null(set to 100)]
    # Also, x.get('seniority_sort', {}) handles null condition  but for None, needed to have the explicit check
    course_instructor_list.sort(
        key=lambda x: (
            x.get("role", {}).get("role_id")
            != 19,  # Primary Instructor (19) should come first
            x.get("role", {}).get("role_id"),  # Other role IDs in ascending order
            100
            if x.get("seniority_sort") is None
            else x.get("seniority_sort", {}),  # Handle None values
            x.get("profile", {}).get("name_last"),  # Sort by last name
        )
    )

    num_instructors = len(course_instructor_list)

    course_instructor_names = [get_display_name(p) for p in course_instructor_list]

    if num_instructors == 1:
        return course_instructor_names[0]
    elif num_instructors == 2:
        return " and ".join(course_instructor_names)
    elif num_instructors > 2:
        # add the last instructor name after an 'and'
        return (
            ", ".join(course_instructor_names[:-1])
            + " and "
            + course_instructor_names[-1]
        )
    else:
        # num_instructors == 0
        return ""


def get_display_name(person):
    if person:
        return (
            person.get("profile", {}).get("name_first", "")
            + " "
            + person.get("profile", {}).get("name_last", "")
        )
    return ""
