import logging
import re
from typing import Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET

from lti_tool.views import LtiLaunchBaseView
from lti_tool.types import LtiLaunch
from lti_tool.models import LtiRegistration

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


class ApplicationLaunchView(LtiLaunchBaseView):
    """
    Handles LTI 1.3 launches for Canvas Course Info tool.
    """

    def handle_resource_launch(self, request, lti_launch):
        logger.info("Handling resource launch")
        logger.info(f"LTI 1.3 Launch for Course Info: {lti_launch}")
        return editor(request)

    def launch_setup(self, request: HttpRequest, lti_launch: LtiLaunch) -> None:
        if not lti_launch.deployment.is_active:
            lti_launch.deployment.is_active = True
            lti_launch.deployment.save()


def config(request: HttpRequest, registration_uuid: str) -> JsonResponse:
    """
    Generates dynamic LTI 1.3 JSON configuration for Canvas registration.
    """
    tool_domain = request.get_host()
    tool_name = "canvas_course_info"
    tool_friendly_name = "Course Info"

    # Helper to label environments
    def get_env_suffix(host: str) -> Optional[str]:
        # Production
        if host == f"{tool_name}.tlt.harvard.edu":
            return ""
        elif host == f"{tool_name}.dev.tlt.harvard.edu":
            return " - DEV"
        elif host == f"{tool_name}.qa.tlt.harvard.edu":
            return " - QA"
        elif (
            host.startswith("localhost")
            or host.startswith("127.0.0.1")
            or host.startswith("local.tlt.harvard.edu")
        ):
            return " - LOCAL"
        else:
            return None

    # Check for existing LtiRegistration by UUID for this issuer
    existing_registration: Optional[LtiRegistration] = LtiRegistration.objects.filter(
        uuid=registration_uuid
    ).first()
    if existing_registration:
        platform_registration = existing_registration
    else:
        logger.error(f"Provided registration_uuid {registration_uuid} not found.")
        return JsonResponse(
            {
                "error": f"Registration UUID {registration_uuid} not found.",
                "message": "Please make sure you are using a valid registration UUID or create a new registration in the Django admin interface.",
            },
            status=400,
        )

    # Construct the tool registration configuration
    jwks_uri = request.build_absolute_uri(reverse("jwks"))
    oidc_initiation_url = request.build_absolute_uri(
        reverse("init", args=[platform_registration.uuid])
    )
    target_link_uri = request.build_absolute_uri(reverse("launch"))

    description = "Displays and edits course information inside Canvas."
    env = get_env_suffix(tool_domain)

    # LTI Advantage scopes needed by this tool
    scopes = []

    # Custom parameters needed by this tool
    custom_parameters = {
        "canvas_course_id": "$Canvas.course.id",
        "canvas_course_sis_source_id": "$Canvas.course.sisSourceId",
        "canvas_account_id": "$Canvas.account.id",
        "canvas_account_name": "$Canvas.account.name",
        "canvas_user_id": "$Canvas.user.id",
        "canvas_user_loginid": "$Canvas.user.loginId",
        "canvas_user_sisintegrationid": "$Canvas.user.sisIntegrationId",
        "canvas_term_name": "$Canvas.term.name",
        "context_title": "$Context.title",
        "context_label": "$com.instructure.contextLabel",
    }

    tool_registration_config = {
        "title": f"{tool_friendly_name}{env}",
        "description": description,
        "oidc_initiation_url": oidc_initiation_url,
        "target_link_uri": target_link_uri,
        "scopes": scopes,
        "extensions": [
            {
                "domain": tool_domain,
                "tool_id": f"{tool_name}-{platform_registration.uuid}",
                "platform": "canvas.instructure.com",
                "privacy_level": "public",
                "settings": {
                    "text": f"{tool_friendly_name}{env}",
                    "placements": [
                        {
                            "placement": "course_navigation",
                            "message_type": "LtiResourceLinkRequest",
                            "target_link_uri": target_link_uri,
                            "canvas_icon_class": "icon-lti",
                            "display_type": "full_width_in_context",
                            "default": "disabled",
                        }
                    ],
                },
            }
        ],
        "public_jwk_url": jwks_uri,
        "custom_fields": custom_parameters,
    }

    return JsonResponse(tool_registration_config)


def not_authorized(request):
    """
    Returns a simple page that says the user is not authorized to view the requested page.
    """
    return HttpResponse("You are not authorized to view this page.", status=403)


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
                logger.debug(
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

            logger.debug(
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
def widget(request: HttpRequest) -> HttpResponse:
    """
    Returns course information (the results of an iCommons API query), called
    from an embedded iframe in Canvas. Note that this is NOT a secure endpoint,
    and spoofing HTTP_REFERER makes this information available for any course,
    so if anything is added of a sensitive nature then this may need a different
    implementation.
    """
    referer = request.META.get("HTTP_REFERER", "")
    logger.debug(f"referer: {request.META.get('HTTP_REFERER')}")
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


def editor(request: HttpRequest) -> HttpResponse:
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
