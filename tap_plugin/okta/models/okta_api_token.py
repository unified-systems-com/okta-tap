"""Okta API Token — An Okta API token (SSWS): a long-lived secret that acts with the admin permissions of the user who created it."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaApiToken(BaseModel):
    """An Okta API token (SSWS): a long-lived secret that acts with the admin permissions of the user who created it.

    An API token's metadata; the secret is never stored. The user it acts as is ACTS_AS_USER__okta.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_api_token"
    ENTITY_NAME: ClassVar[str] = "Okta API Token"
    ENTITY_DESCRIPTION: ClassVar[str] = "An Okta API token (SSWS): a long-lived secret that acts with the admin permissions of the user who created it."
    ENTITY_ICON: ClassVar[str] = "okta-api-token"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # Token names are what an operator sees; Okta does not require them unique, so the key is
    # revisited to (org_name, okta_id).
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
        "client_name": {"type": "string"},
        "created_at": {"type": ["string", "null"]},
        "expires_at": {"type": ["string", "null"]},
        "network_connection": {"type": "string", "enum": ["", "ANYWHERE", "ZONE"]},
        "tags": {"type": "object"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "client_name": {"validation": "jsonschema", "schema": {"type": "string"}},
        "created_at": {"validation": "jsonschema", "schema": {"type": ["string", "null"]}},
        "expires_at": {"validation": "jsonschema", "schema": {"type": ["string", "null"]}},
        "network_connection": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ANYWHERE", "ZONE"]}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "name"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The token's name.
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The client Okta recorded when the token was created (Okta Admin Console, a CLI).
    client_name = models.CharField(max_length=255, blank=True, default="")
    #: When the token was created.
    created_at = models.DateTimeField(null=True, blank=True)
    #: expiresAt: Okta moves it forward on every use (a token expires after 30 days unused), so it
    #: is also the API's only read on recent use. The API reports no last-used time.
    expires_at = models.DateTimeField(null=True, blank=True)
    #: network.connection: whether the token is usable from anywhere or only from listed zones.
    network_connection = models.CharField(max_length=255, blank=True, default="")
    #: TAP's tag map.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_api_token"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
