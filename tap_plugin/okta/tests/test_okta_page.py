"""The /okta page bundle (req-okta-page-org): it imports, and every search it ships answers for one org.

Seeds a small org with one of everything the page reads, plus a second org, then runs each of the
bundle's searches through the real search path for the org, for the other org, and with ?org absent.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tap_grid.caller_context import CallerContext
from tap_grid.services import WriteOperation, write_batch

PKG = Path(__file__).resolve().parents[1]
BUNDLE_PATH = PKG / "grift" / "okta-page.grift.json"
READS_THROUGH_GRYPHON = pytest.mark.django_db(transaction=True, databases=["default", "search_readonly"])


def _bundle() -> dict[str, Any]:
    return json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))


def _nodes(entity_type: str) -> list[dict[str, Any]]:
    return [n for b in _bundle()["batches"] for n in b["nodes"] if n["entity"]["entity_type"] == entity_type]


class _Seed:
    def __init__(self) -> None:
        self.ctx = CallerContext()
        self.ids: dict[str, str] = {}

    def node(self, key: str, type_slug: str, org: str | None = None, **payload: Any) -> str:
        r = write_batch([WriteOperation(verb="create_node", type_slug=type_slug, payload=payload)], caller_context=self.ctx).results[0]
        assert r.success, r
        eid = str(r.entity_id)
        self.ids[key] = eid
        if org:
            self.edge(eid, self.ids[org], "BELONGS_TO_ORG__okta")
        return eid

    def edge(self, src: str, dst: str, edge_type: str, props: dict[str, Any] | None = None) -> None:
        payload = {"properties": props} if props else {}
        r = write_batch([WriteOperation(verb="create_edge", from_target=src, to_target=dst, edge_type=edge_type, payload=payload)], caller_context=self.ctx).results[0]
        assert r.success, (edge_type, r)


def _seed_org(s: _Seed) -> None:
    P = "okta__okta_"
    s.node("acme", f"{P}org", name="acme", service_offering="okta_for_government_high")
    s.node("other", f"{P}org", name="other")
    s.node("other-app", f"{P}application", "other", org_name="other", label="Other app")
    s.node("other-group", f"{P}group", "other", org_name="other", name="Other group")
    s.node("other-role", f"{P}admin_role", "other", org_name="other", name="Other role")
    s.node("other-ra", f"{P}role_assignment", "other", org_name="other", name="Other assignment", status="ACTIVE")
    s.node("other-rule", f"{P}policy_rule", "other", org_name="other", policy_type="ACCESS_POLICY", policy_name="x", name="Other rule")
    o = {"org": "acme", "org_name": "acme"}

    def n(key: str, t: str, **kw: Any) -> str:
        return s.node(key, f"{P}{t}", o["org"], org_name=o["org_name"], **kw)

    n("teleport", "application", label="Teleport", sign_on_mode="SAML_2_0", status="ACTIVE")
    n("eng", "group", name="Engineers", group_type="OKTA_GROUP")
    n("admins", "group", name="Okta Admins", group_type="OKTA_GROUP")
    n("alice", "user", login="alice@acme.example", status="ACTIVE")
    n("bob", "user", login="bob@acme.example", status="SUSPENDED")
    n("policy", "policy", policy_type="ACCESS_POLICY", name="Require Duo")
    n("rule", "policy_rule", policy_type="ACCESS_POLICY", policy_name="Require Duo", name="Engineers with Duo", access="ALLOW", factor_mode="2FA", priority=1)
    n("enroll", "policy", policy_type="MFA_ENROLL", name="Enroll Duo", priority=1)
    n("duo", "authenticator", name="Duo Security", authenticator_key="duo", status="ACTIVE")
    n("idp", "identity_provider", name="Partner IdP", idp_type="SAML2", account_link_action="AUTO")
    n("as", "authorization_server", name="acme", server_kind="org")
    n("role", "admin_role", name="Super Administrator", role_type="SUPER_ADMIN")
    n("ra", "role_assignment", name="Okta Admins: Super Administrator", assignment_type="GROUP")
    n("token", "api_token", name="terraform", network_connection="ANYWHERE")
    n("zone", "network_zone", name="Corp egress", zone_type="IP", usage="POLICY")
    n("origin", "trusted_origin", name="GitLab", origin="https://gitlab.example", scopes=["CORS"])
    n("stream", "log_stream", name="To EventBridge", stream_type="aws_eventbridge")
    n("rset", "resource_set", name="Engineering apps")
    n("ad", "application", label="Active Directory", app_name="active_directory")
    n("adgroup", "group", name="AD Staff", group_type="APP_GROUP")
    n("routing", "policy", policy_type="IDP_DISCOVERY", name="Routing")
    n("route", "policy_rule", policy_type="IDP_DISCOVERY", policy_name="Routing", name="Partners to Partner IdP")
    i = s.ids
    s.edge(i["eng"], i["teleport"], "ASSIGNED_APPLICATION__okta", {"priority": 0})
    s.edge(i["alice"], i["teleport"], "ASSIGNED_APPLICATION__okta", {"scope": "GROUP"})
    s.edge(i["teleport"], i["policy"], "BOUND_TO_POLICY__okta")
    s.edge(i["policy"], i["rule"], "EVALUATES_RULE__okta", {"priority": 1})
    s.edge(i["rule"], i["duo"], "REQUIRES_AUTHENTICATOR__okta", {"constraint": "possession"})
    s.edge(i["rule"], i["eng"], "APPLIES_TO_GROUP__okta", {"mode": "include"})
    s.edge(i["rule"], i["zone"], "MATCHES_NETWORK_ZONE__okta", {"mode": "include"})
    s.edge(i["enroll"], i["duo"], "ENROLLS_AUTHENTICATOR__okta", {"enroll": "REQUIRED"})
    s.edge(i["idp"], i["eng"], "ASSIGNS_GROUP_MEMBERSHIP__okta", {"action": "APPEND"})
    s.edge(i["admins"], i["ra"], "HOLDS_ROLE_ASSIGNMENT__okta")
    s.edge(i["ra"], i["role"], "GRANTS_ADMIN_ROLE__okta")
    s.edge(i["token"], i["alice"], "ACTS_AS_USER__okta")
    s.edge(i["ra"], i["rset"], "SCOPED_TO_RESOURCE__okta")
    s.edge(i["ad"], i["adgroup"], "IMPORTS_GROUP__okta")
    s.edge(i["routing"], i["route"], "EVALUATES_RULE__okta", {"priority": 1})
    s.edge(i["route"], i["idp"], "ROUTES_AUTHENTICATION__okta")
    # Cross-org edges nothing should draw on acme's page: a foreign group assigned acme's app,
    # holding acme's assignment, and acme's assignment granting a foreign role.
    s.edge(i["other-group"], i["teleport"], "ASSIGNED_APPLICATION__okta")
    s.edge(i["other-group"], i["ra"], "HOLDS_ROLE_ASSIGNMENT__okta")
    s.edge(i["ra"], i["other-role"], "GRANTS_ADMIN_ROLE__okta")
    # A foreign node in the MIDDLE of a path whose ends are both acme's.
    s.edge(i["eng"], i["other-ra"], "HOLDS_ROLE_ASSIGNMENT__okta")
    s.edge(i["other-ra"], i["role"], "GRANTS_ADMIN_ROLE__okta")
    s.edge(i["policy"], i["other-rule"], "EVALUATES_RULE__okta", {"priority": 2})
    s.edge(i["other-rule"], i["duo"], "REQUIRES_AUTHENTICATOR__okta", {"constraint": "possession"})


def test_bundle_is_registered_and_names_its_layout() -> None:
    """req-okta-page-org-1: the manifest declares the bundle; the layout module ships in the package."""
    import tomllib

    manifest = tomllib.loads((PKG / "tap-plugin.toml").read_text())
    assert manifest["grift"]["okta_page"] == "grift/okta-page.grift.json"
    (layout,) = _nodes("layout")
    js = layout["node"]["definition"]["js_file"]
    assert (PKG / js.removeprefix("tap_plugin/okta/")).is_file()


def test_page_slots_match_uses_panel_edges() -> None:
    """req-okta-page-org-2: one USES_PANEL per layout slot, graph first (the hotlink is exact)."""
    (page,) = _nodes("page")
    rows = page["node"]["layout"]["columns"]["col-1"]["rows"]
    slots = [rows[k]["panel-id"] for k in sorted(rows, key=lambda r: int(r.split("-")[1]))]
    assert slots[0] == "org-graph"
    uses = [e["edge"]["properties"]["hotlink"]["value"] for b in _bundle()["batches"] for e in b["edges"] if e["edge"]["edge_type"] == "USES_PANEL"]
    assert sorted(uses) == sorted(slots)
    assert page["node"]["slug"] == "/okta"


def test_graph_is_icon_badge_and_names_every_edge_type() -> None:
    """req-okta-page-org-3: icon-badge node style; every scene edge search names its edge type."""
    (proj,) = _nodes("projection")
    assert proj["node"]["definition"]["node_style"] == {"mode": "icon-badge"}
    for s in _nodes("search"):
        q = " ".join(s["node"]["definition"]["query"])
        assert "-[]" not in q and "-[e]" not in q, s["entity"]["name"]
        assert s["node"]["input_schema"]["properties"]["org"]["default"] == "okta__okta_org"


def test_no_entity_id_outside_the_bundle() -> None:
    """req-okta-page-org-4: reusable. Every id the bundle names is one it defines."""
    b = _bundle()["batches"][0]
    defined = {n["entity"]["entity_id"] for n in b["nodes"]}
    for e in b["edges"]:
        assert e["edge"]["from_entity_id"] in defined
        assert e["edge"]["to_entity_id"] in defined


@READS_THROUGH_GRYPHON
def test_every_search_answers_for_one_org() -> None:
    """req-okta-page-org-5: each search returns the seeded org's rows, none of the other org's."""
    from tap_grid.grift import grift_import
    from tap_grid.models import Search
    from tap_grid.search import execute_search

    assert grift_import(_bundle()).success
    s = _Seed()
    _seed_org(s)
    other_ids = {s.ids[k] for k in ("other", "other-app", "other-group", "other-role", "other-ra", "other-rule")}
    foreign_names = ("Other group", "Other role", "Other assignment", "Other rule")
    for spec in _nodes("search"):
        search = Search.objects.get(entity_id=spec["entity"]["entity_id"])
        env = execute_search(search, inputs={"org": "acme"})
        env = env.get("results", env)
        got = len(env.get("nodes", [])) + len(env.get("rows", []))
        assert got > 0, f"{search.name}: nothing for the seeded org"
        ids = {str(n["entity_id"]) for n in env.get("nodes", [])}
        assert not ids & other_ids, f"{search.name}: leaked another org's nodes"
        flat = json.dumps(env.get("rows", []))
        assert not [n for n in foreign_names if n in flat], f"{search.name}: leaked another org's rows"


@READS_THROUGH_GRYPHON
def test_absent_org_means_every_org() -> None:
    """req-okta-page-org-5: ?org absent falls back to the schema default, which matches every org."""
    from tap_grid.grift import grift_import
    from tap_grid.models import Search
    from tap_grid.search import execute_search

    assert grift_import(_bundle()).success
    s = _Seed()
    _seed_org(s)
    (apps,) = [n for n in _nodes("search") if n["entity"]["name"] == "okta — applications in the org"]
    search = Search.objects.get(entity_id=apps["entity"]["entity_id"])
    every = execute_search(search, inputs={})  # schema default: the every-org sentinel
    every = every.get("results", every)
    assert {n["name"] for n in every["nodes"]} == {"Teleport", "Active Directory", "Other app"}
    one = execute_search(search, inputs={"org": "other"})
    one = one.get("results", one)
    assert {n["name"] for n in one["nodes"]} == {"Other app"}


@READS_THROUGH_GRYPHON
def test_org_name_is_matched_exactly() -> None:
    """req-okta-page-org-5: ?org=a does not also match an org named aba."""
    from tap_grid.grift import grift_import
    from tap_grid.models import Search
    from tap_grid.search import execute_search

    assert grift_import(_bundle()).success
    s = _Seed()
    s.node("a", "okta__okta_org", name="a")
    s.node("aba", "okta__okta_org", name="aba")
    s.node("a-app", "okta__okta_application", "a", org_name="a", label="A app")
    s.node("aba-app", "okta__okta_application", "aba", org_name="aba", label="ABA app")
    (apps,) = [n for n in _nodes("search") if n["entity"]["name"] == "okta — applications in the org"]
    search = Search.objects.get(entity_id=apps["entity"]["entity_id"])
    one = execute_search(search, inputs={"org": "a"})
    one = one.get("results", one)
    assert {n["name"] for n in one["nodes"]} == {"A app"}


@pytest.mark.django_db
def test_the_sentinel_is_not_an_org_name() -> None:
    """req-okta-page-org-5: the every-org sentinel can never be a real org's name."""
    r = write_batch([WriteOperation(verb="create_node", type_slug="okta__okta_org", payload={"name": "okta__okta_org"})], caller_context=CallerContext())
    assert not r.results[0].success
