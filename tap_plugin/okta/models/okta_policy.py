"""Okta Policy — A policy in an Okta org: a global session, authentication (app sign-on), password, authenticator enrollment, IdP routing or other policy, evaluated through its ordered rules."""

from typing import Any, ClassVar

from django.db import models

from tap_grid.models import BaseModel


class OktaPolicy(BaseModel):
    """A policy in an Okta org: a global session, authentication (app sign-on), password, authenticator enrollment, IdP routing or other policy, evaluated through its ordered rules.

    One policy of one type. Which groups it applies to is APPLIES_TO_GROUP__okta, its rules are
    EVALUATES_RULE__okta, an authentication policy's applications are BOUND_TO_POLICY__okta, and an
    enrollment policy's authenticators are ENROLLS_AUTHENTICATOR__okta.

    Spec: specs/spec-okta-v0.md (req-okta-corpus).
    """

    ENTITY_TYPE: ClassVar[str] = "okta__okta_policy"
    ENTITY_NAME: ClassVar[str] = "Okta Policy"
    ENTITY_DESCRIPTION: ClassVar[str] = "A policy in an Okta org: a global session, authentication (app sign-on), password, authenticator enrollment, IdP routing or other policy, evaluated through its ordered rules."
    ENTITY_ICON: ClassVar[str] = "okta-policy"
    # No default dimension: the dcom value belongs to the observation (a seeded design node is
    # `design`, a collected one `configuration`), so whatever writes the node stamps it.
    DEFAULT_DIMENSIONS: ClassVar[dict[str, str]] = {}
    # Policy names are unique per type within an org; revisited to (org_name, okta_id).
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ('org_name', 'policy_type', 'name')
    OUTBOUND_EDGES: ClassVar[list[dict[str, Any]]] = [
        {"nodes": [{"type": "okta__okta_org"}], "edges": [{"type": "BELONGS_TO_ORG__okta"}]},
        {"nodes": [{"type": "okta__okta_policy_rule"}], "edges": [{"type": "EVALUATES_RULE__okta"}]},
        {"nodes": [{"type": "okta__okta_group"}], "edges": [{"type": "APPLIES_TO_GROUP__okta"}]},
        {"nodes": [{"type": "okta__okta_authenticator"}], "edges": [{"type": "ENROLLS_AUTHENTICATOR__okta"}]},
    ]
    # A policy's rules exist only as part of it: retiring the policy retires them.
    CONTAINMENT_EDGES: ClassVar[tuple[str, ...]] = ('EVALUATES_RULE__okta',)
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
        "name": {"type": "string", "minLength": 1},
        "okta_id": {"type": "string"},
        "status": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]},
        "priority": {"type": ["integer", "null"]},
        "system": {"type": ["boolean", "null"]},
        "description": {"type": "string"},
    }
    FIELD_VALIDATION_SCHEMA: ClassVar[dict[str, Any]] = {
        "org_name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "policy_type": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["OKTA_SIGN_ON", "ACCESS_POLICY", "PASSWORD", "MFA_ENROLL", "PROFILE_ENROLLMENT", "IDP_DISCOVERY", "POST_AUTH_SESSION", "ENTITY_RISK", "DEVICE_SIGNAL_COLLECTION", "SESSION_VIOLATION_DETECTION", "CLIENT_UPDATE", "IDENTITY_CLAIM_SOURCING"], "minLength": 1}},
        "name": {"validation": "jsonschema", "schema": {"type": "string", "minLength": 1}},
        "okta_id": {"validation": "jsonschema", "schema": {"type": "string"}},
        "status": {"validation": "jsonschema", "schema": {"type": "string", "enum": ["", "ACTIVE", "INACTIVE"]}},
        "priority": {"validation": "jsonschema", "schema": {"type": ["integer", "null"]}},
        "system": {"validation": "jsonschema", "schema": {"type": ["boolean", "null"]}},
        "description": {"validation": "jsonschema", "schema": {"type": "string"}},
    }
    CREATE_REQUIRED: ClassVar[list[str]] = ["org_name", "policy_type", "name"]

    #: The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping
    #: column, not a copy of the org: the org's own facts live on the org, and the
    #: BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold
    #: an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a
    #: column).
    org_name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's policy type: OKTA_SIGN_ON is the global session policy, ACCESS_POLICY an
    #: authentication (app sign-on) policy, MFA_ENROLL authenticator enrollment, IDP_DISCOVERY IdP
    #: routing.
    policy_type = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: The policy's name.
    name = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
    okta_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    #: Okta's policy status.
    status = models.CharField(max_length=255, blank=True, default="")
    #: Evaluation order among policies of the same type (1 first). Null for types Okta does not
    #: order (ACCESS_POLICY).
    priority = models.IntegerField(null=True, blank=True)
    #: True for the policy Okta ships and will not let you delete (the Default Policy). Null means
    #: not observed.
    system = models.BooleanField(null=True, blank=True)
    #: The policy's description.
    description = models.TextField(blank=True, default="")

    class Meta(BaseModel.Meta):
        db_table = "okta__okta_policy"

    def get_name(self) -> str:
        return self.name or ""

    def __str__(self) -> str:
        return self.get_name()
