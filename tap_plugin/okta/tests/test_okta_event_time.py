"""Event time (core's req-grid-entity-event-time, tap 0.4.7): what each okta model declares, and what core
derives from it.

The first class pins the declarations, so a model added later without one, or one that names the wrong
field, fails here. The second applies core's own derivation to plain values: a user or API token holds
from Okta's `created` with no stated end.
"""

from datetime import UTC, datetime

from tap_plugin.okta.models import (
    OktaAdminRole,
    OktaApiToken,
    OktaApplication,
    OktaAuthenticator,
    OktaAuthorizationServer,
    OktaDevice,
    OktaGroup,
    OktaGroupRule,
    OktaIdentityProvider,
    OktaLogStream,
    OktaNetworkZone,
    OktaOrg,
    OktaPolicy,
    OktaPolicyRule,
    OktaResourceSet,
    OktaRoleAssignment,
    OktaTrustedOrigin,
    OktaUser,
)

from tap_grid.event_time import NO_EVENT_TIME, Interval, declaration_problems, derive
from tap_grid.registry import get_model_class, list_entity_types

DECLARED = {
    OktaUser: Interval("created_at", "created"),
    OktaApiToken: Interval("created_at", "created"),
    OktaAdminRole: NO_EVENT_TIME,
    OktaApplication: NO_EVENT_TIME,
    OktaAuthenticator: NO_EVENT_TIME,
    OktaAuthorizationServer: NO_EVENT_TIME,
    OktaDevice: NO_EVENT_TIME,
    OktaGroup: NO_EVENT_TIME,
    OktaGroupRule: NO_EVENT_TIME,
    OktaIdentityProvider: NO_EVENT_TIME,
    OktaLogStream: NO_EVENT_TIME,
    OktaNetworkZone: NO_EVENT_TIME,
    OktaOrg: NO_EVENT_TIME,
    OktaPolicy: NO_EVENT_TIME,
    OktaPolicyRule: NO_EVENT_TIME,
    OktaResourceSet: NO_EVENT_TIME,
    OktaRoleAssignment: NO_EVENT_TIME,
    OktaTrustedOrigin: NO_EVENT_TIME,
}

CREATED = datetime(2026, 11, 2, 9, 30, tzinfo=UTC)


class TestDeclarations:
    def test_every_model_of_the_plugin_decides(self) -> None:
        own = {get_model_class(slug) for slug in list_entity_types() if slug.startswith("okta__")}
        assert own == set(DECLARED)
        assert {model: model.EVENT_TIME for model in own} == DECLARED

    def test_core_accepts_each_declaration(self) -> None:
        for model in DECLARED:
            assert declaration_problems(model) == [], model.__name__


class TestDerivation:
    def test_a_user_and_an_api_token_hold_from_creation_with_no_end(self) -> None:
        for model in (OktaUser, OktaApiToken):
            derived = derive(model.EVENT_TIME, {"created_at": CREATED}.get)
            assert (derived.event_start, derived.event_end, derived.kind) == (CREATED, None, "created"), model.__name__

    def test_a_user_with_no_creation_date_has_none(self) -> None:
        derived = derive(OktaUser.EVENT_TIME, {"created_at": None}.get)
        assert (derived.event_start, derived.event_end, derived.kind) == (None, None, None)
