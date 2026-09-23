"""Okta Group — A group in an Okta org: an Okta-mastered group, a group imported from an application, or a built-in group such as Everyone."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaGroup(BaseModel):
    """A group in an Okta org: an Okta-mastered group, a group imported from an application, or a built-in group such as Everyone.

    A group of users in one Okta org. group_type separates Okta-mastered groups from groups an
    application (AD, LDAP, an HR system) masters and Okta only imports; the importing application is
    the IMPORTS_GROUP__okta edge.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_group"
    ENTITY_NAME: ClassVar[str] = "Okta Group"
    ENTITY_DESCRIPTION: ClassVar[str] = "A group in an Okta org: an Okta-mastered group, a group imported from an application, or a built-in group such as Everyone."
    ENTITY_ICON: ClassVar[str] = "okta-group"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # Group names are unique within an org; revisited to (org_name, okta_id) with the collector.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ('org_name', 'name')
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFFFFF", "border": "#007DC1", "label": "#00297A"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
        "okta_id": {"type": "string"},
        "group_type": {"type": "string", "enum": ["", "OKTA_GROUP", "APP_GROUP", "BUILT_IN"]},
        "description": {"type": "string"},
        "tags": {"type": "object"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "group_type": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "OKTA_GROUP", "APP_GROUP", "BUILT_IN"]}},
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
    #: profile.name.
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's group type: mastered in Okta, imported from an application, or built in (Everyone).
    group_type = models.CharField(max_length=255, blank=True, default="")
    #: profile.description.
    description = models.TextField(blank=True, default="")
    #: TAP's tag map.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_group"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
