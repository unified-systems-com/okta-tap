"""Okta Policy Rule — A rule in an Okta policy: its conditions (people, network zones) and its action (allow or deny, the factors it requires, re-authentication frequency)."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaPolicyRule(BaseModel):
    """A rule in an Okta policy: its conditions (people, network zones) and its action (allow or deny, the factors it requires, re-authentication frequency).

    One rule of one policy, reached from the policy by EVALUATES_RULE__okta and retired with it. The
    authenticators a rule requires are REQUIRES_AUTHENTICATOR__okta edges; its zones are
    MATCHES_NETWORK_ZONE__okta; an IdP routing rule's target is ROUTES_AUTHENTICATION__okta.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_policy_rule"
    ENTITY_NAME: ClassVar[str] = "Okta Policy Rule"
    ENTITY_DESCRIPTION: ClassVar[str] = "A rule in an Okta policy: its conditions (people, network zones) and its action (allow or deny, the factors it requires, re-authentication frequency)."
    ENTITY_ICON: ClassVar[str] = "okta-policy-rule"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # Rule names are unique within a policy, so the key carries the policy's own key alongside;
    # revisited to (org_name, okta_id).
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ('org_name', 'policy_type', 'policy_name', 'name')
    DEFAULT_DISPLAY: ClassVar[dict[str, Any]] = {
        "tap_viz": {
            "shape": "round-rectangle",
            "colors": {"fill": "#FFF8E1", "border": "#B26A00", "label": "#4E2E00"},
            "label": {"valign": "bottom", "halign": "center", "position": "outside"},
        }
    }

    FIELD_CRUD_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"type": "string", "minLength": 1},
        "policy_type": {"type": "string", "enum": ["OKTA_SIGN_ON", "ACCESS_POLICY", "PASSWORD", "MFA_ENROLL", "PROFILE_ENROLLMENT", "IDP_DISCOVERY", "POST_AUTH_SESSION", "ENTITY_RISK", "DEVICE_SIGNAL_COLLECTION", "SESSION_VIOLATION_DETECTION", "CLIENT_UPDATE", "IDENTITY_CLAIM_SOURCING"], "minLength": 1},
        "policy_name": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
        "okta_id": {"type": "string"},
        "status": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]},
        "priority": {"type": ["integer", "null"]},
        "access": {"type": "string", "enum": ["", "ALLOW", "DENY"]},
        "factor_mode": {"type": "string", "enum": ["", "1FA", "2FA"]},
        "reauthenticate_in": {"type": "string"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "policy_type": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["OKTA_SIGN_ON", "ACCESS_POLICY", "PASSWORD", "MFA_ENROLL", "PROFILE_ENROLLMENT", "IDP_DISCOVERY", "POST_AUTH_SESSION", "ENTITY_RISK", "DEVICE_SIGNAL_COLLECTION", "SESSION_VIOLATION_DETECTION", "CLIENT_UPDATE", "IDENTITY_CLAIM_SOURCING"], "minLength": 1}},
        "policy_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "status": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]}},
        "priority": {"validation": "jsonschema", "schema": {"type": ["integer", "null"]}},
        "access": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ALLOW", "DENY"]}},
        "factor_mode": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "1FA", "2FA"]}},
        "reauthenticate_in": {"validation": "jsonschema", "schema": {"type": "string"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "policy_type", "policy_name", "name"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The owning policy's type: part of the key, because the policy's own key is (org_name,
    #: policy_type, name).
    policy_type = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The owning policy's name: part of the key.
    policy_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The rule's name.
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's rule status.
    status = models.CharField(max_length=255, blank=True, default="")
    #: Evaluation order within the policy (1 first). The catch-all rule is last.
    priority = models.IntegerField(null=True, blank=True)
    #: The rule's access decision.
    access = models.CharField(max_length=255, blank=True, default="")
    #: How many factor types the rule demands: ACCESS_POLICY verificationMethod.factorMode; for a
    #: global session rule, 2FA when requireFactor is true. Blank means not observed, never 'no
    #: MFA'.
    factor_mode = models.CharField(max_length=255, blank=True, default="")
    #: ISO-8601 duration before the user must re-verify (PT12H); blank when not observed.
    reauthenticate_in = models.CharField(max_length=255, blank=True, default="")

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_policy_rule"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
