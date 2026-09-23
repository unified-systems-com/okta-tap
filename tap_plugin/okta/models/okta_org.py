"""Okta Org — an Okta org: one okta.com tenant (for example acme.okta.com) that holds users, groups, applications and policies."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaOrg(BaseModel):
    """An Okta org: one okta.com tenant (for example acme.okta.com) that holds users, groups, applications and policies.

    The tenant every other okta type belongs to (BELONGS_TO_ORG__okta). A design can place it
    before any access exists, so its observed identifiers stay blank until a collector reads them.

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
        # The type slug is reserved: it is the /okta page's every-org sentinel (req-okta-page-org).
        "name": {"type": "string", "minLength": 1, "not": {"const": "okta__okta_org"}},
        "org_domain": {"type": "string"},
        "okta_id": {"type": "string"},
        "service_offering": {"type": "string", "enum": ["", "commercial", "okta_for_government_moderate", "okta_for_government_high", "okta_for_dod_il4"]},
        "tags": {"type": "object"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1, "not": {"const": "okta__okta_org"}}},
        "org_domain": {"validation": "jsonschema", "schema": {"type": "string"}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "service_offering": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "commercial", "okta_for_government_moderate", "okta_for_government_high", "okta_for_dod_il4"]}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["name"]

    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    # The org's okta.com (or custom) domain, for example acme.okta.com. Blank until observed.
    org_domain = models.CharField(max_length=255, blank=True, default="")
    #: Okta's org id. Blank until observed.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Which Okta offering hosts the org: commercial, Okta for Government Moderate (FedRAMP
    #: Moderate), Okta for Government High (FedRAMP High, okta-gov.com cells) or Okta for DoD IL4.
    #: A design can know this; blank means not stated, never 'commercial'.
    service_offering = models.CharField(max_length=64, blank=True, default="")
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_org"

    def get_name(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.get_name()
