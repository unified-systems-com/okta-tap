"""Behaviour tests for the okta corpus v1: every model and every edge (req-okta-corpus, req-okta-edges)."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

import pytest
from django.apps import apps

from tap_grid.caller_context import CallerContext
from tap_grid.constraints import get_edge_type_constraints
from tap_grid.models import BaseModel, Edge, Entity
from tap_grid.services import WriteOperation, delete_node, write_batch

PKG = Path(__file__).resolve().parents[1]
MANIFEST = tomllib.loads((PKG / "tap-plugin.toml").read_text())
MODEL_TYPES = sorted(MANIFEST["models"])
EDGE_SLUGS = sorted(MANIFEST["edges"])


def _model(type_slug: str) -> type[BaseModel]:
    for m in apps.get_app_config("okta").get_models():
        if getattr(m, "ENTITY_TYPE", None) == type_slug:
            return m
    raise AssertionError(f"{type_slug} is not a registered okta model")


def _sample(type_slug: str, **over: Any) -> dict[str, Any]:
    """A minimal valid payload: every CREATE_REQUIRED field, enum-constrained ones from the enum."""
    model = _model(type_slug)
    payload: dict[str, Any] = {}
    for field in model.CREATE_REQUIRED:
        enum = model.FIELD_CRUD_SCHEMA[field].get("enum")
        payload[field] = next(v for v in enum if v) if enum else f"{field}-{type_slug}"
    payload.update(over)
    return payload


def _create(type_slug: str, **over: Any) -> str:
    result = write_batch(
        [WriteOperation(verb="create_node", type_slug=type_slug, payload=_sample(type_slug, **over))],
        caller_context=CallerContext(),
    )
    assert result.results[0].success, result.results[0]
    return str(result.results[0].entity_id)


def _edge(src: str, dst: str, edge_type: str, properties: dict[str, Any] | None = None) -> bool:
    payload = {"properties": properties} if properties is not None else {}
    result = write_batch(
        [WriteOperation(verb="create_edge", from_target=src, to_target=dst, edge_type=edge_type, payload=payload)],
        caller_context=CallerContext(),
    )
    return bool(result.results[0].success)


# ---------------------------------------------------------------------------
# Models (req-okta-corpus)
# ---------------------------------------------------------------------------


def test_manifest_registers_the_corpus() -> None:
    """req-okta-corpus-1: eighteen node types, each manifest key equal to its model's ENTITY_TYPE."""
    assert len(MODEL_TYPES) == 18
    for type_slug in MODEL_TYPES:
        assert _model(type_slug).ENTITY_TYPE == type_slug


@pytest.mark.parametrize("type_slug", MODEL_TYPES)
def test_natural_key_rests_on_columns(type_slug: str) -> None:
    """req-okta-corpus-2: every key field is a model field and a required create field."""
    model = _model(type_slug)
    names = {f.name for f in model._meta.get_fields()}
    assert model.NATURAL_KEY, type_slug
    for key in model.NATURAL_KEY:
        assert key in names
        assert key in model.CREATE_REQUIRED


@pytest.mark.parametrize("type_slug", MODEL_TYPES)
def test_no_default_dimensions(type_slug: str) -> None:
    """req-okta-corpus-3: the dcom value belongs to the observation, never the type."""
    assert _model(type_slug).DEFAULT_DIMENSIONS == {}


@pytest.mark.django_db
@pytest.mark.parametrize("type_slug", MODEL_TYPES)
def test_create_with_required_fields_only(type_slug: str) -> None:
    """req-okta-corpus-4: a design node needs only its key; observed fields stay blank."""
    eid = _create(type_slug)
    row = _model(type_slug).all_objects.get(entity_id=eid)
    assert Entity.objects.get(pk=eid).name == row.get_name()
    if "okta_id" in row.CREATE_REQUIRED:
        return
    if hasattr(row, "okta_id"):
        assert row.okta_id == ""


@pytest.mark.django_db
@pytest.mark.parametrize("type_slug", MODEL_TYPES)
def test_each_required_field_is_enforced(type_slug: str) -> None:
    """req-okta-corpus-4: dropping any required field refuses the write."""
    model = _model(type_slug)
    for field in model.CREATE_REQUIRED:
        payload = _sample(type_slug)
        payload.pop(field)
        result = write_batch(
            [WriteOperation(verb="create_node", type_slug=type_slug, payload=payload)],
            caller_context=CallerContext(),
        )
        assert not result.results[0].success, (type_slug, field)


@pytest.mark.django_db
def test_enum_rejects_an_unknown_value() -> None:
    """req-okta-corpus-5: vocabularies are closed; blank is admitted as not observed."""
    ok = write_batch(
        [WriteOperation(verb="create_node", type_slug="okta__okta_user", payload=_sample("okta__okta_user", status=""))],
        caller_context=CallerContext(),
    )
    assert ok.results[0].success
    bad = write_batch(
        [WriteOperation(verb="create_node", type_slug="okta__okta_user", payload=_sample("okta__okta_user", login="b", status="HAPPY"))],
        caller_context=CallerContext(),
    )
    assert not bad.results[0].success


@pytest.mark.parametrize("type_slug", MODEL_TYPES)
def test_no_free_form_record(type_slug: str) -> None:
    """req-okta-corpus-8: no type declares a free-form `configuration` field."""
    model = _model(type_slug)
    assert "configuration" not in model.FIELD_CRUD_SCHEMA
    assert "configuration" not in model.FIELD_VALIDATION_SCHEMA
    assert "configuration" not in {f.name for f in model._meta.get_fields()}


@pytest.mark.django_db
@pytest.mark.parametrize("type_slug", MODEL_TYPES)
def test_configuration_write_is_refused(type_slug: str) -> None:
    """req-okta-corpus-8: a create_node write carrying `configuration` is refused, so a record cannot ride along."""
    result = write_batch(
        [WriteOperation(verb="create_node", type_slug=type_slug, payload=_sample(type_slug, configuration={"client_secret": "sentinel"}))],
        caller_context=CallerContext(),
    )
    assert not result.results[0].success, type_slug


@pytest.mark.django_db
def test_same_name_in_two_orgs_is_two_nodes() -> None:
    """req-okta-corpus-2: org_name is part of every child key, so each org has its own Everyone group."""
    a = _create("okta__okta_group", org_name="staging", name="Everyone")
    b = _create("okta__okta_group", org_name="production", name="Everyone")
    assert a != b


# ---------------------------------------------------------------------------
# Edges (req-okta-edges)
# ---------------------------------------------------------------------------


def test_edge_files_match_manifest() -> None:
    """req-okta-edges-1: slug == manifest key == file; every property schema is closed."""
    assert len(EDGE_SLUGS) == 24
    for slug, rel in MANIFEST["edges"].items():
        data = json.loads((PKG / rel).read_text())
        assert data["slug"] == slug
        assert (PKG / rel).name == f"{slug.removesuffix('__okta')}.edge.json"
        if "property_schema" in data:
            assert data["property_schema"].get("additionalProperties") is False, slug


def test_open_ends_are_explained() -> None:
    """req-okta-edges-2: an omitted side says in its description what may appear there."""
    for rel in MANIFEST["edges"].values():
        data = json.loads((PKG / rel).read_text())
        if "targets" not in data:
            assert "OPEN" in data["description"], data["slug"]


def test_foreign_types_are_substrate_only() -> None:
    """req-okta-edges-2: the only foreign type named is identity_core's (a declared vocabulary dependency)."""
    foreign = set()
    for rel in MANIFEST["edges"].values():
        data = json.loads((PKG / rel).read_text())
        for t in data.get("sources", []) + data.get("targets", []):
            if not t.startswith("okta__"):
                foreign.add(t)
    assert foreign == {"identity_core__oidc_issuer"}
    assert [d["slug"] for d in MANIFEST["depends_on"]] == ["identity_core"]


@pytest.mark.django_db
class TestEdgeBehaviour:
    def test_belongs_to_org(self) -> None:
        org = _create("okta__okta_org", name="acme")
        user = _create("okta__okta_user", org_name="acme")
        assert _edge(user, org, "BELONGS_TO_ORG__okta")
        # Direction is declared on the edge type. Core's permission union lets an unconstrained
        # node emit any edge, so the declaration is what a validator and a reader rely on.
        declared = get_edge_type_constraints("BELONGS_TO_ORG__okta")
        assert declared is not None
        assert declared.targets == {"okta__okta_org"}
        assert "okta__okta_org" not in declared.sources

    def test_member_of_group_property_vocabulary(self) -> None:
        user = _create("okta__okta_user")
        group = _create("okta__okta_group")
        assert _edge(user, group, "MEMBER_OF_GROUP__okta", {"managed_by": "group_rule"})
        assert not _edge(user, group, "MEMBER_OF_GROUP__okta", {"managed_by": "magic"})
        assert not _edge(user, group, "MEMBER_OF_GROUP__okta", {"extra": 1})

    def test_applies_to_group_requires_mode(self) -> None:
        policy = _create("okta__okta_policy")
        group = _create("okta__okta_group")
        assert not _edge(policy, group, "APPLIES_TO_GROUP__okta", {})
        assert _edge(policy, group, "APPLIES_TO_GROUP__okta", {"mode": "exclude"})

    def test_requires_authenticator_from_rule_only(self) -> None:
        rule = _create("okta__okta_policy_rule")
        policy = _create("okta__okta_policy", name="p2")
        authn = _create("okta__okta_authenticator")
        assert _edge(rule, authn, "REQUIRES_AUTHENTICATOR__okta", {"constraint": "possession", "phishing_resistant": True})
        assert not _edge(policy, authn, "REQUIRES_AUTHENTICATOR__okta", {"constraint": "possession"})

    def test_role_assignment_chain(self) -> None:
        group = _create("okta__okta_group")
        assignment = _create("okta__okta_role_assignment")
        role = _create("okta__okta_admin_role", role_type="SUPER_ADMIN")
        rset = _create("okta__okta_resource_set")
        assert _edge(group, assignment, "HOLDS_ROLE_ASSIGNMENT__okta")
        assert _edge(assignment, role, "GRANTS_ADMIN_ROLE__okta")
        assert _edge(assignment, rset, "SCOPED_TO_RESOURCE__okta")

    def test_serves_issuer_lands_on_the_substrate(self) -> None:
        server = _create("okta__okta_authorization_server", server_kind="org")
        issuer = write_batch(
            [WriteOperation(verb="create_node", type_slug="identity_core__oidc_issuer", payload={"issuer_url": "https://acme.okta-gov.com"})],
            caller_context=CallerContext(),
        ).results[0].entity_id
        assert _edge(server, str(issuer), "SERVES_ISSUER__okta")

    def test_open_ended_edges_accept_a_foreign_node(self) -> None:
        """SENDS_ASSERTION / DELEGATES_VERIFICATION / WRITES_LOGS / IDENTIFIES_PERSON name no target type."""
        foreign = str(
            write_batch(
                [WriteOperation(verb="create_node", type_slug="identity_core__oidc_issuer", payload={"issuer_url": "https://relying.example"})],
                caller_context=CallerContext(),
            ).results[0].entity_id
        )
        app = _create("okta__okta_application")
        authn = _create("okta__okta_authenticator")
        assert _edge(app, foreign, "SENDS_ASSERTION__okta", {"protocol": "oidc", "endpoint": "https://relying.example/callback"})
        assert _edge(authn, foreign, "DELEGATES_VERIFICATION__okta", {"protocol": "duo_universal_prompt"})
        assert not _edge(app, foreign, "SENDS_ASSERTION__okta", {"protocol": "carrier-pigeon"})

    def test_policy_rules_retire_with_their_policy(self) -> None:
        """req-okta-edges-3: EVALUATES_RULE is the one containment edge."""
        policy = _create("okta__okta_policy")
        rule = _create("okta__okta_policy_rule")
        group = _create("okta__okta_group")
        assert _edge(policy, rule, "EVALUATES_RULE__okta", {"priority": 1})
        assert _edge(rule, group, "APPLIES_TO_GROUP__okta", {"mode": "include"})
        result = delete_node(policy, caller_context=CallerContext(), cascade="contained")
        assert result.success
        assert not _model("okta__okta_policy_rule").objects.filter(entity_id=rule).exists()
        # A reference is ended, never followed: the group stays live.
        assert _model("okta__okta_group").objects.filter(entity_id=group).exists()
        assert not Edge.objects.filter(from_entity_id=rule).exists()


@pytest.mark.django_db
def test_org_offering_is_closed() -> None:
    """req-okta-model-4: service_offering admits its closed set plus blank (not stated)."""
    assert _create("okta__okta_org", name="gov", service_offering="okta_for_government_high")
    assert _create("okta__okta_org", name="unstated", service_offering="")
    bad = write_batch(
        [WriteOperation(verb="create_node", type_slug="okta__okta_org", payload={"name": "x", "service_offering": "fedramp"})],
        caller_context=CallerContext(),
    )
    assert not bad.results[0].success


@pytest.mark.parametrize("type_slug", MODEL_TYPES)
def test_icon_is_a_square_64px_svg(type_slug: str) -> None:
    """req-okta-corpus-6: every ENTITY_ICON ships, sized, with a square viewBox."""
    import re

    svg = (PKG / "static" / "okta" / "icons" / f"{_model(type_slug).ENTITY_ICON}.svg").read_text()
    head = svg[: svg.index(">")]
    assert 'width="64"' in head and 'height="64"' in head
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', head)
    assert m and m.group(1) == m.group(2)
