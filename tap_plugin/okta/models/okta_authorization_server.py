"""Okta Authorization Server — An OAuth 2.0 / OIDC authorization server in an Okta org: the org authorization server, the default custom server, or a custom server, each an OIDC issuer."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaAuthorizationServer(BaseModel):
    """An OAuth 2.0 / OIDC authorization server in an Okta org: the org authorization server, the default custom server, or a custom server, each an OIDC issuer.

    An authorization server: the thing that mints tokens. Its issuer is the neutral
    identity_core__oidc_issuer node reached by SERVES_ISSUER__okta; the issuer URL lives there, not
    here.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_authorization_server"
    ENTITY_NAME: ClassVar[str] = "Okta Authorization Server"
    ENTITY_DESCRIPTION: ClassVar[str] = "An OAuth 2.0 / OIDC authorization server in an Okta org: the org authorization server, the default custom server, or a custom server, each an OIDC issuer."
    ENTITY_ICON: ClassVar[str] = "okta-authorization-server"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # Server names are unique within an org (the org server is named for the org); revisited to
    # (org_name, okta_id).
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ('org_name', 'name')
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#EEF2FF", "border": "#3F51B5", "label": "#1A237E"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
        "okta_id": {"type": "string"},
        "server_kind": {"type": "string", "enum": ["", "org", "default", "custom"]},
        "status": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]},
        "issuer_mode": {"type": "string", "enum": ["", "ORG_URL", "CUSTOM_URL", "DYNAMIC"]},
        "audiences": {"type": "array", "items": {"type": "string"}},
        "scopes": {"type": "array", "items": {"type": "string"}},
        "claims": {"type": "array", "items": {"type": "string"}},
        "tags": {"type": "object"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "server_kind": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "org", "default", "custom"]}},
        "status": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]}},
        "issuer_mode": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ORG_URL", "CUSTOM_URL", "DYNAMIC"]}},
        "audiences": {"validation": "jsonschema", "schema": {"type": "array", "items": {"type": "string"}}},
        "scopes": {"validation": "jsonschema", "schema": {"type": "array", "items": {"type": "string"}}},
        "claims": {"validation": "jsonschema", "schema": {"type": "array", "items": {"type": "string"}}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "name"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The server's name ('default' for the default custom server).
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Which of Okta's three kinds this is. The org server issues tokens for Okta's own APIs and for
    #: apps that use the org URL as issuer.
    server_kind = models.CharField(max_length=255, blank=True, default="")
    #: Okta's server status.
    status = models.CharField(max_length=255, blank=True, default="")
    #: Which domain the issuer uses.
    issuer_mode = models.CharField(max_length=255, blank=True, default="")
    #: The audiences the server mints tokens for.
    audiences = models.JSONField(default=list, blank=True)
    #: Custom scope names. A field in v1: nothing yet needs to point at a scope (Backlog:
    #: req-okta-backlog-oauth-grants).
    scopes = models.JSONField(default=list, blank=True)
    #: Custom claim names. A field in v1 for the same reason as scopes.
    claims = models.JSONField(default=list, blank=True)
    #: TAP's tag map.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_authorization_server"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
