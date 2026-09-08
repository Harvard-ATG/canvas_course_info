"""
Utility functions for extracting data from LTI 1.3 launch requests.
"""

from logging import getLogger

from lti_tool.types import LtiLaunch

logger = getLogger(__name__)


def get_custom_data_from_request(request):
    """
    Get the custom claim data from the LTI launch request.
    """
    lti_launch: LtiLaunch = request.lti_launch
    launch_data = lti_launch.get_message_launch().get_launch_data()
    return launch_data.get("https://purl.imsglobal.org/spec/lti/claim/custom", {})


def get_course_instance_id_from_request(request):
    """
    Get the course instance ID (SIS source ID) from the LTI launch custom claim.
    """
    custom_data = get_custom_data_from_request(request)
    return custom_data.get("canvas_course_sissourceid")


def get_canvas_course_id_from_request(request):
    """
    Get the Canvas course ID from the LTI launch custom claim.
    """
    custom_data = get_custom_data_from_request(request)
    return custom_data.get("canvas_courseid")



