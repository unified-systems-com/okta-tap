"""Okta Role Assignment — An administrator role assignment in an Okta org: one principal (user, group or service app) holding one admin role, over the whole org or a scoped set of resources."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaRoleAssignment(BaseModel):
    """An administrator role assignment in an Okta org: one principal (user, group or service app) holding one admin role, over the whole org or a scoped set of resources.

    A three-way fact (principal, role, scope), so a node rather than an edge:
    HOLDS_ROLE_ASSIGNMENT__okta from the principal, GRANTS_ADMIN_ROLE__okta to the role,
    SCOPED_TO_RESOURCE__okta to what it covers. No scope edge means the role covers the whole org.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_role_assignment"
    ENTITY_NAME: ClassVar[str] = "Okta Role Assignment"
    ENTITY_DESCRIPTION: ClassVar[str] = "An administrator role assignment in an Okta org: one principal (user, group or service app) holding one admin role, over the whole org or a scoped set of resources."
    ENTITY_ICON: ClassVar[str] = "okta-role-assignment"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # Okta's assignment id is not knowable at design time, so a design names the assignment (for
    # example 'Okta Admins: Super Administrator'); revisited to (org_name, okta_id) when the
    # collector lands.
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
        "assignment_type": {"type": "string", "enum": ["", "USER", "GROUP", "CLIENT"]},
        "status": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]},
        "tags": {"type": "object"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "assignment_type": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "USER", "GROUP", "CLIENT"]}},
        "status": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "name"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The assignment's name: design-authored, or principal and role as the collector composes them.
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's assignmentType: to a user directly, to a group, or to a service app (CLIENT).
    assignment_type = models.CharField(max_length=255, blank=True, default="")
    #: Okta's assignment status.
    status = models.CharField(max_length=255, blank=True, default="")
    #: TAP's tag map.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_role_assignment"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
