"""Okta Resource Set — A resource set in an Okta org: the named collection of users, groups, applications and other objects a custom admin role assignment is scoped to."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaResourceSet(BaseModel):
    """A resource set in an Okta org: the named collection of users, groups, applications and other objects a custom admin role assignment is scoped to.

    A resource set. Its members are INCLUDES_RESOURCE__okta edges; an assignment scoped to it is
    SCOPED_TO_RESOURCE__okta.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_resource_set"
    ENTITY_NAME: ClassVar[str] = "Okta Resource Set"
    ENTITY_DESCRIPTION: ClassVar[str] = "A resource set in an Okta org: the named collection of users, groups, applications and other objects a custom admin role assignment is scoped to."
    ENTITY_ICON: ClassVar[str] = "okta-resource-set"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # Labels are unique within an org; revisited to (org_name, okta_id).
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
        "description": {"type": "string"},
        "tags": {"type": "object"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
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
    #: The resource set's label.
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The resource set's description.
    description = models.TextField(blank=True, default="")
    #: TAP's tag map.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_resource_set"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
