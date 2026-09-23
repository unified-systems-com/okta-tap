"""Okta User — A user account in an Okta org: one login, its lifecycle status and when it last signed in."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaUser(BaseModel):
    """A user account in an Okta org: one login, its lifecycle status and when it last signed in.

    A person's (or a service identity's) account in one Okta org. The account, not the person: the
    same human holds one account per org, and the link to a neutral person node is the open-ended
    IDENTIFIES_PERSON__okta edge.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_user"
    ENTITY_NAME: ClassVar[str] = "Okta User"
    ENTITY_DESCRIPTION: ClassVar[str] = "A user account in an Okta org: one login, its lifecycle status and when it last signed in."
    ENTITY_ICON: ClassVar[str] = "okta-user"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # login is unique within an org and is what a design names; the key is revisited to (org_name,
    # okta_id) when the collector makes okta_id observable, since a login can be renamed.
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ('org_name', 'login')
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "ellipse",
            "colors": {"fill": "#FFFFFF", "border": "#007DC1", "label": "#00297A"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"type": "string", "minLength": 1},
        "login": {"type": "string", "minLength": 1},
        "okta_id": {"type": "string"},
        "email": {"type": "string"},
        "display_name": {"type": "string"},
        "status": {"type": "string", "enum": ["", "STAGED", "PROVISIONED", "ACTIVE", "RECOVERY", "PASSWORD_EXPIRED", "LOCKED_OUT", "SUSPENDED", "DEPROVISIONED"]},
        "user_type": {"type": "string"},
        "created_at": {"type": ["string", "null"]},
        "activated_at": {"type": ["string", "null"]},
        "last_login_at": {"type": ["string", "null"]},
        "password_changed_at": {"type": ["string", "null"]},
        "status_changed_at": {"type": ["string", "null"]},
        "tags": {"type": "object"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "login": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "email": {"validation": "jsonschema", "schema": {"type": "string"}},
        "display_name": {"validation": "jsonschema", "schema": {"type": "string"}},
        "status": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "STAGED", "PROVISIONED", "ACTIVE", "RECOVERY", "PASSWORD_EXPIRED", "LOCKED_OUT", "SUSPENDED", "DEPROVISIONED"]}},
        "user_type": {"validation": "jsonschema", "schema": {"type": "string"}},
        "created_at": {"validation": "jsonschema", "schema": {"type": ["string", "null"]}},
        "activated_at": {"validation": "jsonschema", "schema": {"type": ["string", "null"]}},
        "last_login_at": {"validation": "jsonschema", "schema": {"type": ["string", "null"]}},
        "password_changed_at": {"validation": "jsonschema", "schema": {"type": ["string", "null"]}},
        "status_changed_at": {"validation": "jsonschema", "schema": {"type": ["string", "null"]}},
        "tags": {"validation": "jsonschema", "schema": {"type": "object"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "login"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The Okta login (profile.login), usually an email address. Unique within an org.
    login = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: profile.email. Often equal to login, not always.
    email = models.CharField(max_length=255, blank=True, default="")
    #: profile.displayName, or first and last name as Okta reports them.
    display_name = models.CharField(max_length=255, blank=True, default="")
    #: Okta's lifecycle status. Blank means not observed, never 'active'.
    status = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The Okta user type's name (default 'user'). A field, not a node: nothing but the user points
    #: at it.
    user_type = models.CharField(max_length=255, blank=True, default="")
    #: When Okta created the account.
    created_at = models.DateTimeField(null=True, blank=True)
    #: When the account was activated.
    activated_at = models.DateTimeField(null=True, blank=True)
    #: Okta's lastLogin. Null means not observed OR never signed in.
    last_login_at = models.DateTimeField(null=True, blank=True)
    #: Okta's passwordChanged.
    password_changed_at = models.DateTimeField(null=True, blank=True)
    #: Okta's statusChanged: when the account entered its current status.
    status_changed_at = models.DateTimeField(null=True, blank=True)
    #: TAP's tag map.
    tags = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_user"

    def get_name(self) -> str:
        return self.login or ""

    def __str__(self) -> str:
        return self.get_name()
