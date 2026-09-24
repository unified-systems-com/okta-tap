"""Okta Identity Provider — An inbound identity provider in an Okta org: an external SAML or OIDC IdP (another Okta org, Entra ID, Google) whose assertions Okta accepts to sign users in."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaIdentityProvider(BaseModel):
    """An inbound identity provider in an Okta org: an external SAML or OIDC IdP (another Okta org, Entra ID, Google) whose assertions Okta accepts to sign users in.

    Inbound federation. The most consequential object in an Okta org after the super admin: an IdP
    that can JIT-provision and account-link users can sign in as them. An OIDC IdP's issuer is
    reached by identity_core's TRUSTS_ISSUER__identity_core edge.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_identity_provider"
    ENTITY_NAME: ClassVar[str] = "Okta Identity Provider"
    ENTITY_DESCRIPTION: ClassVar[str] = "An inbound identity provider in an Okta org: an external SAML or OIDC IdP (another Okta org, Entra ID, Google) whose assertions Okta accepts to sign users in."
    ENTITY_ICON: ClassVar[str] = "okta-identity-provider"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # IdP names are unique within an org; revisited to (org_name, okta_id).
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
        "idp_type": {"type": "string"},
        "protocol_type": {"type": "string", "enum": ["", "SAML2", "OIDC", "OAUTH2", "MTLS", "ID_PROOFING"]},
        "status": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]},
        "provisioning_action": {"type": "string", "enum": ["", "AUTO", "DISABLED"]},
        "account_link_action": {"type": "string", "enum": ["", "AUTO", "DISABLED"]},
        "subject_match_type": {"type": "string"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "idp_type": {"validation": "jsonschema", "schema": {"type": "string"}},
        "protocol_type": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "SAML2", "OIDC", "OAUTH2", "MTLS", "ID_PROOFING"]}},
        "status": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]}},
        "provisioning_action": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "AUTO", "DISABLED"]}},
        "account_link_action": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "AUTO", "DISABLED"]}},
        "subject_match_type": {"validation": "jsonschema", "schema": {"type": "string"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "name"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The IdP's name.
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's IdP type: SAML2, OIDC, X509 (smart card), MICROSOFT, GOOGLE, LOGINGOV, GITHUB, GITLAB,
    #: an identity-verification vendor (IDV_*) and others. Free text: Okta adds types.
    idp_type = models.CharField(max_length=255, blank=True, default="")
    #: protocol.type.
    protocol_type = models.CharField(max_length=255, blank=True, default="")
    #: Okta's IdP status.
    status = models.CharField(max_length=255, blank=True, default="")
    #: policy.provisioning.action: AUTO means Just-In-Time provisioning creates users from
    #: assertions.
    provisioning_action = models.CharField(max_length=255, blank=True, default="")
    #: policy.accountLink.action: AUTO links an assertion to an EXISTING user. With AUTO an IdP can
    #: sign in as that user.
    account_link_action = models.CharField(max_length=255, blank=True, default="")
    #: policy.subject.matchType: how the assertion's subject is matched to a user (USERNAME, EMAIL,
    #: USERNAME_OR_EMAIL, CUSTOM_ATTRIBUTE).
    subject_match_type = models.CharField(max_length=255, blank=True, default="")

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_identity_provider"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
