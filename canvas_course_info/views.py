import json
import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView

from lti_tool.models import LtiRegistration

logger = logging.getLogger(__name__)

_TOOL_HOST = "canvas-course-info.tlt.harvard.edu"
_TOOL_FRIENDLY_NAME = "Course Info"
_TOOL_DESCRIPTION = "A button to insert course info into Canvas pages."


def _get_env_suffix(host: str) -> str:
    """Return a display suffix based on the request host, or empty string for production."""
    bare = host.split(":")[0]  # strip port for local dev comparisons
    if bare == _TOOL_HOST:
        return ""
    elif bare == "canvas-course-info.dev.tlt.harvard.edu":
        return " - DEV"
    elif bare == "canvas-course-info.qa.tlt.harvard.edu":
        return " - QA"
    elif bare in ("localhost", "127.0.0.1") or bare.endswith(".ngrok-free.app"):
        return " - LOCAL"
    else:
        return " - LOCAL"

# Custom parameters requested from Canvas during LTI launch
_CUSTOM_PARAMETERS = [
    "Canvas.api.baseUrl",
    "Canvas.api.domain",
    "Canvas.course.id",
    "Canvas.course.sisSourceId",
]


def _to_custom_field_key(canvas_param: str) -> str:
    """Convert a Canvas substitution variable name to a snake_case dict key."""
    key = canvas_param.replace("com.instructure.", "").replace("vnd.", "vnd_")
    key = key.replace(".", "_")
    key = key.replace("<>", "")
    return key.lower()


class ConfigView(PermissionRequiredMixin, TemplateView):
    permission_required = "lti_tool.view_ltiregistration"
    login_url = "/admin/login/"
    template_name = "canvas_course_info/config.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uuid = self.request.GET.get("uuid")
        if uuid is None:
            context["registrations"] = LtiRegistration.objects.all()
        else:
            registration = LtiRegistration.objects.get(uuid=uuid)
            context["registration"] = registration

            tool_domain = self.request.get_host()
            env_suffix = _get_env_suffix(tool_domain)
            tool_title = f"{_TOOL_FRIENDLY_NAME}{env_suffix}"

            jwks_uri = self.request.build_absolute_uri(reverse("jwks"))
            oidc_initiation_url = self.request.build_absolute_uri(
                reverse("init", args=[uuid])
            )
            target_link_uri = self.request.build_absolute_uri(
                reverse("course_info:lti_launch")
            )

            custom_fields = {_to_custom_field_key(p): f"${p}" for p in _CUSTOM_PARAMETERS}

            tool_config = {
                "title": tool_title,
                "description": _TOOL_DESCRIPTION,
                "oidc_initiation_url": oidc_initiation_url,
                "target_link_uri": target_link_uri,
                "scopes": [],
                "extensions": [
                    {
                        "domain": tool_domain,
                        "tool_id": f"canvas_course_info-{uuid}",
                        "platform": "canvas.instructure.com",
                        "privacy_level": "public",
                        "settings": {
                            "text": tool_title,
                            "placements": [
                                {
                                    "text": tool_title,
                                    "placement": "editor_button",
                                    "message_type": "LtiDeepLinkingRequest",
                                    "target_link_uri": target_link_uri,
                                    "canvas_icon_class": "icon-lti",
                                },
                            ],
                        },
                    }
                ],
                "public_jwk_url": jwks_uri,
                "custom_fields": custom_fields,
            }

            context["tool_config"] = json.dumps(tool_config, indent=4)

        return context
