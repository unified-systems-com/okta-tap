"""Okta Group Rule — A group rule in an Okta org: an Okta Expression Language condition that places matching users into groups automatically."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaGroupRule(BaseModel):
    """A group rule in an Okta org: an Okta Expression Language condition that places matching users into groups automatically.

    A group rule: membership by expression. The groups it assigns are ASSIGNS_GROUP_MEMBERSHIP__okta
    edges.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_group_rule"
    ENTITY_NAME: ClassVar[str] = "Okta Group Rule"
    ENTITY_DESCRIPTION: ClassVar[str] = "A group rule in an Okta org: an Okta Expression Language condition that places matching users into groups automatically."
    ENTITY_ICON: ClassVar[str] = "okta-group-rule"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # Rule names are unique within an org; revisited to (org_name, okta_id).
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
        "status": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE", "INVALID"]},
        "expression": {"type": "string"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "status": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE", "INVALID"]}},
        "expression": {"validation": "jsonschema", "schema": {"type": "string"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "name"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The rule's name.
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's rule status. INVALID means the rule references something that no longer exists.
    status = models.CharField(max_length=255, blank=True, default="")
    #: conditions.expression.value: the Okta Expression Language condition.
    expression = models.TextField(blank=True, default="")

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_group_rule"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
