"""Okta Network Zone — A network zone in an Okta org: a named set of IP ranges, or a dynamic zone of locations, ASNs and anonymizer categories, used in policy conditions or as a blocklist."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaNetworkZone(BaseModel):
    """A network zone in an Okta org: a named set of IP ranges, or a dynamic zone of locations, ASNs and anonymizer categories, used in policy conditions or as a blocklist.

    A network zone. Rules reach it by MATCHES_NETWORK_ZONE__okta.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_network_zone"
    ENTITY_NAME: ClassVar[str] = "Okta Network Zone"
    ENTITY_DESCRIPTION: ClassVar[str] = "A network zone in an Okta org: a named set of IP ranges, or a dynamic zone of locations, ASNs and anonymizer categories, used in policy conditions or as a blocklist."
    ENTITY_ICON: ClassVar[str] = "okta-network-zone"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # Zone names are unique within an org; revisited to (org_name, okta_id).
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ('org_name', 'name')
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#F1F5F9", "border": "#475569", "label": "#1E293B"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
        "okta_id": {"type": "string"},
        "zone_type": {"type": "string", "enum": ["", "IP", "DYNAMIC", "DYNAMIC_V2"]},
        "usage": {"type": "string", "enum": ["", "POLICY", "BLOCKLIST"]},
        "status": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]},
        "system": {"type": ["boolean", "null"]},
        "gateways": {"type": "array", "items": {"type": "string"}},
        "proxies": {"type": "array", "items": {"type": "string"}},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "zone_type": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "IP", "DYNAMIC", "DYNAMIC_V2"]}},
        "usage": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "POLICY", "BLOCKLIST"]}},
        "status": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]}},
        "system": {"validation": "jsonschema", "schema": {"type": ["boolean", "null"]}},
        "gateways": {"validation": "jsonschema", "schema": {"type": "array", "items": {"type": "string"}}},
        "proxies": {"validation": "jsonschema", "schema": {"type": "array", "items": {"type": "string"}}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "name"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The zone's name (LegacyIpZone, BlockedIpZone and DefaultEnhancedDynamicZone are Okta's).
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: IP zones list addresses; dynamic zones list locations, ASNs and proxy types.
    zone_type = models.CharField(max_length=255, blank=True, default="")
    #: POLICY zones are referenced by rules; BLOCKLIST zones are refused before any policy runs.
    usage = models.CharField(max_length=255, blank=True, default="")
    #: Okta's zone status.
    status = models.CharField(max_length=255, blank=True, default="")
    #: True for the zones Okta ships. Null means not observed.
    system = models.BooleanField(null=True, blank=True)
    #: IP zone gateway ranges (CIDR or range strings).
    gateways = models.JSONField(default=list, blank=True)
    #: IP zone trusted proxy ranges.
    proxies = models.JSONField(default=list, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_network_zone"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
