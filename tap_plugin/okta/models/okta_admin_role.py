"""Okta Admin Role — An administrator role in an Okta org: a standard role such as Super Administrator or Help Desk Administrator, or a custom role with its own permissions."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaAdminRole(BaseModel):
    """An administrator role in an Okta org: a standard role such as Super Administrator or Help Desk Administrator, or a custom role with its own permissions.

    A role: a bundle of admin permissions. Who holds it, and over what, is an
    okta__okta_role_assignment.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_admin_role"
    ENTITY_NAME: ClassVar[str] = "Okta Admin Role"
    ENTITY_DESCRIPTION: ClassVar[str] = "An administrator role in an Okta org: a standard role such as Super Administrator or Help Desk Administrator, or a custom role with its own permissions."
    ENTITY_ICON: ClassVar[str] = "okta-admin-role"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # Standard roles are named by Okta and custom role labels are unique within an org; revisited to
    # (org_name, okta_id) for custom roles.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ('org_name', 'name')
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FDECEA", "border": "#B3261E", "label": "#5F1410"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
        "okta_id": {"type": "string"},
        "role_type": {"type": "string", "enum": ["", "SUPER_ADMIN", "ORG_ADMIN", "APP_ADMIN", "USER_ADMIN", "HELP_DESK_ADMIN", "READ_ONLY_ADMIN", "MOBILE_ADMIN", "API_ACCESS_MANAGEMENT_ADMIN", "REPORT_ADMIN", "GROUP_MEMBERSHIP_ADMIN", "ACCESS_CERTIFICATIONS_ADMIN", "ACCESS_REQUESTS_ADMIN", "WORKFLOWS_ADMIN", "CUSTOM"]},
        "permissions": {"type": "array", "items": {"type": "string"}},
        "description": {"type": "string"},
        "tags": {"type": "object"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "role_type": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "SUPER_ADMIN", "ORG_ADMIN", "APP_ADMIN", "USER_ADMIN", "HELP_DESK_ADMIN", "READ_ONLY_ADMIN", "MOBILE_ADMIN", "API_ACCESS_MANAGEMENT_ADMIN", "REPORT_ADMIN", "GROUP_MEMBERSHIP_ADMIN", "ACCESS_CERTIFICATIONS_ADMIN", "ACCESS_REQUESTS_ADMIN", "WORKFLOWS_ADMIN", "CUSTOM"]}},
        "permissions": {"validation": "jsonschema", "schema": {"type": "array", "items": {"type": "string"}}},
        "description": {"validation": "jsonschema", "schema": {"type": "string"}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "name"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The role's label (Super Administrator, or a custom role's label).
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's standard role type, or CUSTOM.
    role_type = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: A custom role's permissions (okta.users.manage, ...). Blank for standard roles: Okta defines
    #: those.
    permissions = models.JSONField(default=list, blank=True)
    #: The role's description.
    description = models.TextField(blank=True, default="")
    #: TAP's tag map.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_admin_role"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
