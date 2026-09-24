"""Person link (req-okta-person): an Okta user resolves to identity_core's human."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
from tap_plugin.okta.models.okta_user import OktaUser

from tap_grid.caller_context import CallerContext
from tap_grid.models import Edge
from tap_grid.services import WriteOperation, write_batch

HELD = "HELD_BY_HUMAN__identity_core"
HUMAN = "identity_core__human"
PKG = Path(__file__).resolve().parents[1]


def _node(type_slug: str, payload: dict) -> str:
    result = write_batch(
        [WriteOperation(verb="create_node", type_slug=type_slug, payload=payload)], caller_context=CallerContext()
    ).results[0]
    assert result.success, result
    return str(result.entity_id)


def _held(src: str, dst: str, properties: dict | None = None):
    payload = {"properties": properties} if properties is not None else {}
    return write_batch(
        [WriteOperation(verb="create_edge", from_target=src, to_target=dst, edge_type=HELD, payload=payload)],
        caller_context=CallerContext(),
    ).results[0]


def test_person_link_is_declared() -> None:
    """req-okta-person-1: the user names the edge and the human; the edge's owner is a declared dependency,
    floored at the release that ships the human; the retired open-ended person edge is no longer shipped."""
    declared = {
        (e["type"], n["type"]) for entry in OktaUser.OUTBOUND_EDGES for e in entry["edges"] for n in entry.get("nodes", [])
    }
    assert declared == {(HELD, HUMAN)}
    manifest = tomllib.loads((PKG / "tap-plugin.toml").read_text())
    deps = {d["slug"]: d for d in manifest.get("depends_on", [])}
    # The floor is the first identity_core release that ships identity_core__human.
    assert deps["identity_core"].get("min_version") == "0.1.3"
    assert "IDENTIFIES_PERSON__okta" not in manifest["edges"]
    assert not (PKG / "edges" / "IDENTIFIES_PERSON.edge.json").exists()


@pytest.mark.django_db
def test_user_is_held_by_a_human() -> None:
    """req-okta-person-2."""
    human = _node(HUMAN, {"handle": "t-0001", "name": "Test Person"})
    user = _node("okta__okta_user", {"org_name": "acme", "login": "tperson@example.test"})
    result = _held(user, human, {"matched_on": "operator seed"})
    assert result.success, result
    assert Edge.objects.get(entity_id=result.entity_id).properties == {"matched_on": "operator seed"}


@pytest.mark.django_db
def test_unknown_property_is_refused() -> None:
    """req-okta-person-2: on a fresh pair, so the refusal is the closed property schema and nothing else."""
    human = _node(HUMAN, {"handle": "t-0003"})
    user = _node("okta__okta_user", {"org_name": "acme", "login": "fresh@example.test"})
    refused = _held(user, human, {"matched_by": "email"})
    assert not refused.success
    assert "matched_by" in " ".join(str(e) for e in refused.errors)
    assert not Edge.objects.filter(from_entity_id=user, edge_type=HELD).exists()


@pytest.mark.django_db
def test_user_keeps_its_own_edges() -> None:
    """req-okta-person-1: declaring OUTBOUND_EDGES adds a permission and removes none (permission union)."""
    org = _node("okta__okta_org", {"name": "acme"})
    group = _node("okta__okta_group", {"org_name": "acme", "name": "Everyone"})
    user = _node("okta__okta_user", {"org_name": "acme", "login": "tperson@example.test"})
    for dst, edge_type in ((org, "BELONGS_TO_ORG__okta"), (group, "MEMBER_OF_GROUP__okta")):
        result = write_batch(
            [WriteOperation(verb="create_edge", from_target=user, to_target=dst, edge_type=edge_type, payload={})],
            caller_context=CallerContext(),
        ).results[0]
        assert result.success, (edge_type, result)


@pytest.mark.django_db
def test_shared_account_is_recorded() -> None:
    """req-okta-person-3: a shared login held by two people keeps both edges."""
    first = _node(HUMAN, {"handle": "t-0001"})
    second = _node(HUMAN, {"handle": "t-0002"})
    shared = _node("okta__okta_user", {"org_name": "acme", "login": "break-glass@example.test"})
    assert _held(shared, first, {"matched_on": "operator seed"}).success
    assert _held(shared, second, {"matched_on": "operator seed"}).success
    targets = set(Edge.objects.filter(from_entity_id=shared, edge_type=HELD).values_list("to_entity_id", flat=True))
    assert {str(t) for t in targets} == {first, second}
