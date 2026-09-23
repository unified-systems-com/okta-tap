"""Okta Org — an Okta org: one okta.com tenant (for example acme.okta.com) that holds users, groups, applications and policies."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaOrg(BaseModel):
    """An Okta org: one okta.com tenant (for example acme.okta.com) that holds users, groups, applications and policies.

    v0 is the outer node only: a design can place it before any access exists, so its one
    identifying field stays blank (not observed) until a collector reads it.

    Spec: specs/spec-okta-v0.md (req-okta-model).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_org"
    ENTITY_NAME: ClassVar[str] = "Okta Org"
    ENTITY_DESCRIPTION: ClassVar[str] = "An Okta org: one okta.com tenant (for example acme.okta.com) that holds users, groups, applications and policies."
    ENTITY_ICON: ClassVar[str] = "okta-org"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so the bundle that seeds a node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # A design-phase node has no observed identifier; its name is the only fact it carries.
    # Revisit when the collector makes org_domain observable (req-okta-collector).
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("name",)
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFFFFF", "border": "#007DC1", "label": "#00297A"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "name": {"type": "string", "minLength": 1},
        "org_domain": {"type": "string"},
        "configuration": {"type": "object"},
        "tags": {"type": "object"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "org_domain": {"validation": "jsonschema", "schema": {"type": "string"}},
        "configuration": {"validation": "jsonschema", "schema": {"type": "object"}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["name"]

    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    # The org's okta.com (or custom) domain, for example acme.okta.com. Blank until observed.
    org_domain = models.CharField(max_length=255, blank=True, default="")
    configuration = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_org"

    def get_name(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.get_name()
