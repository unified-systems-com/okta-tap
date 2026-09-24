"""Okta Authenticator — An authenticator configured in an Okta org: Okta Verify, a security key (WebAuthn/FIDO2), password, email, phone, a smart card, or an external verifier such as Duo."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaAuthenticator(BaseModel):
    """An authenticator configured in an Okta org: Okta Verify, a security key (WebAuthn/FIDO2), password, email, phone, a smart card, or an external verifier such as Duo.

    An authenticator as the org configures it. Which users enrolled it is the
    ENROLLED_AUTHENTICATOR__okta edge (Cartography's OktaUserFactor is that edge, not a node). An
    authenticator that hands verification to another service (Duo, an external IdP) reaches it by
    the open-ended DELEGATES_VERIFICATION__okta edge.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_authenticator"
    ENTITY_NAME: ClassVar[str] = "Okta Authenticator"
    ENTITY_DESCRIPTION: ClassVar[str] = "An authenticator configured in an Okta org: Okta Verify, a security key (WebAuthn/FIDO2), password, email, phone, a smart card, or an external verifier such as Duo."
    ENTITY_ICON: ClassVar[str] = "okta-authenticator"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # Authenticator names are unique within an org; revisited to (org_name, okta_id).
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ('org_name', 'name')
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#E0F2F1", "border": "#00796B", "label": "#003D33"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
        "okta_id": {"type": "string"},
        "authenticator_key": {"type": "string"},
        "authenticator_type": {"type": "string"},
        "status": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]},
        "phishing_resistant": {"type": ["boolean", "null"]},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "authenticator_key": {"validation": "jsonschema", "schema": {"type": "string"}},
        "authenticator_type": {"validation": "jsonschema", "schema": {"type": "string"}},
        "status": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]}},
        "phishing_resistant": {"validation": "jsonschema", "schema": {"type": ["boolean", "null"]}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "name"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The authenticator's name as the org shows it (for example 'Okta Verify', 'Duo Security').
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's key: okta_verify, webauthn, security_key, okta_password, okta_email, phone_number,
    #: duo, google_otp, security_question, smart_card_idp, external_idp, custom_app, onprem_mfa,
    #: symantec_vip, yubikey_token, tac. Free text: Okta adds keys.
    authenticator_key = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's type: app, password, email, phone, security_key, security_question, federated, tac.
    authenticator_type = models.CharField(max_length=255, blank=True, default="")
    #: Okta's authenticator status.
    status = models.CharField(max_length=255, blank=True, default="")
    #: Whether the authenticator can satisfy a phishing-resistant constraint (FastPass, WebAuthn,
    #: smart card). Null means not observed.
    phishing_resistant = models.BooleanField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_authenticator"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
