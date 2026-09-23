"""Okta Application — An application integration in an Okta org: a SAML, OIDC, WS-Fed, SWA or bookmark app that users sign in to through Okta, or an API service app."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaApplication(BaseModel):
    """An application integration in an Okta org: a SAML, OIDC, WS-Fed, SWA or bookmark app that users sign in to through Okta, or an API service app.

    An application integration. For an SSO relying party (Teleport, GitLab) this is Okta's side of
    the trust; the relying service's own node is reached by the open-ended SENDS_ASSERTION__okta
    edge. An OAuth service app (client credentials, application_type=service) is the same type.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_application"
    ENTITY_NAME: ClassVar[str] = "Okta Application"
    ENTITY_DESCRIPTION: ClassVar[str] = "An application integration in an Okta org: a SAML, OIDC, WS-Fed, SWA or bookmark app that users sign in to through Okta, or an API service app."
    ENTITY_ICON: ClassVar[str] = "okta-application"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # label is what an operator and a design name; Okta does not require it unique, so the key is
    # revisited to (org_name, okta_id) when the collector lands.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ('org_name', 'label')
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#EEF2FF", "border": "#3F51B5", "label": "#1A237E"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"type": "string", "minLength": 1},
        "label": {"type": "string", "minLength": 1},
        "okta_id": {"type": "string"},
        "app_name": {"type": "string"},
        "sign_on_mode": {"type": "string", "enum": ["", "SAML_2_0", "SAML_1_1", "OPENID_CONNECT", "WS_FEDERATION", "AUTO_LOGIN", "BROWSER_PLUGIN", "SECURE_PASSWORD_STORE", "BASIC_AUTH", "BOOKMARK"]},
        "status": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE", "DELETED"]},
        "application_type": {"type": "string", "enum": ["", "web", "native", "browser", "service"]},
        "client_id": {"type": "string"},
        "redirect_uris": {"type": "array", "items": {"type": "string"}},
        "grant_types": {"type": "array", "items": {"type": "string"}},
        "tags": {"type": "object"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "label": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "app_name": {"validation": "jsonschema", "schema": {"type": "string"}},
        "sign_on_mode": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "SAML_2_0", "SAML_1_1", "OPENID_CONNECT", "WS_FEDERATION", "AUTO_LOGIN", "BROWSER_PLUGIN", "SECURE_PASSWORD_STORE", "BASIC_AUTH", "BOOKMARK"]}},
        "status": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE", "DELETED"]}},
        "application_type": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "web", "native", "browser", "service"]}},
        "client_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "redirect_uris": {"validation": "jsonschema", "schema": {"type": "array", "items": {"type": "string"}}},
        "grant_types": {"validation": "jsonschema", "schema": {"type": "array", "items": {"type": "string"}}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "label"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The application's display label (what users see on the dashboard).
    label = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's app name: the catalog key (for example 'oidc_client', 'teleport', 'gitlab') or a
    #: generated key for a custom app.
    app_name = models.CharField(max_length=255, blank=True, default="")
    #: Okta's signOnMode. BROWSER_PLUGIN and AUTO_LOGIN are Secure Web Authentication (password
    #: vaulting).
    sign_on_mode = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's app lifecycle status.
    status = models.CharField(max_length=255, blank=True, default="")
    #: For OIDC and service apps: settings.oauthClient.application_type. Blank for SAML and SWA
    #: apps.
    application_type = models.CharField(max_length=255, blank=True, default="")
    #: For OIDC and service apps: the OAuth client_id (Okta uses the app id).
    client_id = models.CharField(max_length=255, blank=True, default="")
    #: OIDC redirect URIs or the SAML ACS URL(s). A field, not a node: nothing but the app points at
    #: a reply URI.
    redirect_uris = models.JSONField(default=list, blank=True)
    #: OIDC/OAuth grant types the client may use.
    grant_types = models.JSONField(default=list, blank=True)
    #: TAP's tag map.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_application"

    def get_name(self) -> str:
        return self.label or ""

    def __str__(self) -> str:
        return self.get_name()
