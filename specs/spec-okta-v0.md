# TAP Okta Plugin Specification

**Okta workforce identity as grid vocabulary: one Okta org and the objects its operator answers for in a FedRAMP 20x environment (who can sign in to what, with which factors, from where; who administers the org; which standing credentials exist; where the audit log goes), plus an `/okta` page that reads one org as its front page.**

## Plugin Identity

| Field | Value |
| --- | --- |
| Slug | `okta` |
| Display name | TAP Okta |
| Description | Okta workforce identity as grid vocabulary: the org and the objects a FedRAMP operator answers for in it (users, groups, applications, authorization servers, identity providers, authenticators, policies, network zones, admin roles, API tokens, devices, log streams), with an org page. |
| Kind | Leaf plugin: Okta vocabulary. Consumes identity_core's neutral OIDC issuer (vocabulary dependency); consumed by instance plugins that place an Okta org in a design (highbar first). |

**Default dimensions**

| Dimension | Value | Why |
| --- | --- | --- |
| (none) | | No okta node or edge type declares a default dimension. The one candidate is `dcom`, and its value belongs to the observation, not the type: a seeded design node is `design`, the same type observed by a future collector is `configuration`. Whatever writes the node stamps it. Environment membership (`deployment.environment.*`) is likewise the instance's. |

## Philosophy

An Okta org is where a FedRAMP boundary decides who gets in. The assessor's first questions about it are
always the same: which applications does it sign people in to, who is assigned each, which policy guards
each, does that policy demand MFA (and phishing-resistant MFA), who can administer the org, what standing
API credentials exist, which external identity providers can sign in as a user, and where the System Log
goes. This plugin models exactly the objects those questions traverse, and ships one page that asks them
of one org.

**What the prior-art survey changed** (the full register is [`okta-corpus.md`](okta-corpus.md)):

- *Cartography's Okta module* (2026-08-30) models org, user, group, group rule, application, authenticator,
  user factor, trusted origin, roles and reply URIs. Borrowed the core set; rejected `ReplyUri`,
  `OktaUserType` and `OktaUserFactor` as nodes (nothing but their parent points at the first two, and a
  factor enrollment is a fact about a (user, authenticator) pair, so it is the `ENROLLED_AUTHENTICATOR`
  edge).
- *BloodHound's OpenGraph Okta extension* (read 2026-09-22; OktaHound 2.8.2) adds authorization servers,
  identity providers, policies, resource sets, role assignments as nodes, API tokens and devices.
  Borrowed all of those and the role-assignment/resource-set/scope shape. Rejected its capability edges
  (`Okta_ResetFactors`, `Okta_HelpDeskAdmin` and kin): they are derived from an assignment and its scope,
  and storing them would derive one fact twice.
- *Neither graph models policy rules, network zones or log streams*, yet the factor requirement, the
  network condition and IdP routing all live on the rule, and FedRAMP audit logging lives on the stream.
  Those are where this corpus is ahead of both.
- *The Okta Management API's own OpenAPI description* (dist/2026.08.4) is the authority for names and
  enums: every enum on a model was checked against it.
- *The incident corpus* (help-desk social engineering of super administrators followed by a second
  identity provider for cross-tenant impersonation, 2023; the support-system breach, 2023) is why admin
  role assignments, account-linking identity providers and routing rules are in the first tier.

**Deliberately not done.** No collector (Backlog). No derived capability edges. No sessions or System Log
events as nodes: they are an event stream a collector reads, and grid history keeps what it lands. No
person type of its own: the person is identity_core's `human`, and an Okta user points at it with
identity_core's `HELD_BY_HUMAN__identity_core` (`req-okta-person`). No dependency on the plugins of the services Okta signs in to (Teleport, GitLab) or on Duo:
the edges that reach them leave their target open.

**Three states.** Every observed field is blank (or null) when not observed, never a default that reads
as a finding: a blank `factor_mode` is not "no MFA", a null `last_login_at` is "never signed in or not
observed", a blank `status` is listed among "users who are not active" on purpose. The page's panel
descriptions say which.

**Identity at design time.** A design node has no Okta id. Every child type therefore keys on the fields
a design can know, scoped by `org_name` (names are unique only within an org: two orgs each hold an
"Everyone" group); every key is revisited to `(org_name, okta_id)` when `req-okta-collector` makes the id
observable. `org_name` is a scoping column, not a second copy of the org: traversal follows
`BELONGS_TO_ORG__okta`.

**Provenance markers.** Every claim about Okta's behaviour here is *documented* (the OpenAPI description
and Okta's documentation), not *observed*: no call has been executed against an Okta org. Every node and
edge seeded by an instance's design is *designed* (`dcom: design`).

## Goals

| # | Name | Description |
| --- | --- | --- |
| 1 | Designable | A design can place an Okta org and its applications, groups, policies and authenticators before any access exists. |
| 2 | Answers The Assessor | The questions an assessor asks of an identity provider in a FedRAMP boundary are traversals over this vocabulary. |
| 3 | Converges, Never Depends | The Okta side of a trust meets the other side on a substrate (the OIDC issuer) or an open edge end, never on another vendor plugin's type. |
| 4 | One Org, One Page | `/okta` reads one org as its front page, picked by `?org=`, reusable by any instance. |

## Requirements

| RID | Name | Status | Notes |
| --- | --- | --- | --- |
| req-okta-model | [Okta Org Model](#okta-org-model) | Implemented | The tenant: its fields, natural key, icon and display |
| req-okta-corpus | [Corpus Node Types](#corpus-node-types) | Implemented | The seventeen types inside an org, their keys, icons and domain articles |
| req-okta-edges | [Corpus Edge Types](#corpus-edge-types) | Implemented | Twenty-three edges; open ends and the one substrate target |
| req-okta-person | [Person Link](#person-link) | Implemented | An Okta user is held by `identity_core__human` (`HELD_BY_HUMAN__identity_core`) |
| req-okta-page-org | [Page: Org](#page-org) | Implemented | `/okta?org=<org name>`: the graph (the org as the outer box, labelled edges, the Duo link both ways), then fifteen tables; observed in a browser 2026-09-24 |
| req-okta-record | [CI Record and Tests](#ci-record-and-tests) | Implemented | The in-package `ci` boot record and the suite |
| req-okta-collector | [Collector](#collector) | Backlog | Observe a real Okta org onto the grid |
| req-okta-backlog-oauth-grants | [OAuth Scopes, Claims And Grants](#oauth-scopes-claims-and-grants) | Backlog | Scopes, claims, authorization-server policies and client grants as first-class |
| req-okta-backlog-provisioning | [Provisioning And Integrations](#provisioning-and-integrations) | Backlog | SCIM push and import, group push, profile mappings, event and inline hooks |
| req-okta-backlog-device-assurance | [Device Assurance And Realms](#device-assurance-and-realms) | Backlog | Device assurance policies, posture signals, realms, the neutral device link |
| req-okta-nongoals | [Non-goals](#non-goals) | Implemented | Derived capability edges, sessions, System Log events, brands |

---

### Okta Org Model
----
RID: `req-okta-model`

Status: `Implemented`

An Okta org: one okta.com, okta-gov.com or custom-domain tenant. The node every other okta type belongs to.

#### Implementation

`tap_plugin/okta/models/okta_org.py` defines `OktaOrg(BaseModel)`, `ENTITY_TYPE = "okta__okta_org"`,
`ENTITY_ICON = "okta-org"`, no default dimensions, fields `name` (required; the value `okta__okta_org`
is refused because it is the /okta page's every-org sentinel), `org_domain`, `okta_id`,
`service_offering` (`commercial`, `okta_for_government_moderate`, `okta_for_government_high`,
`okta_for_dod_il4`, or blank = not stated). `NATURAL_KEY = ("name",)`; revisited
to `okta_id` with `req-okta-collector`. Article: `tap_plugin/okta/domain/okta_org.md`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-okta-model-1 | Created Through The Service Layer | Implemented | A `create_node` write with only `name` succeeds and the row carries it. | `tests/test_okta_org.py` |
| req-okta-model-2 | Name Required | Implemented | A `create_node` write without `name` is refused. | |
| req-okta-model-3 | Keyed By Name | Implemented | `NATURAL_KEY` is `("name",)` and every key field is a model field. | |
| req-okta-model-4 | Offering Is Stated, Never Assumed | Implemented | `service_offering` admits only its closed set plus blank; blank means not stated. | `tests/test_okta_corpus.py` |

---

### Corpus Node Types
----
RID: `req-okta-corpus`

Status: `Implemented`

The seventeen node types inside an org, each justified in [`okta-corpus.md`](okta-corpus.md) and
described in its domain article.

#### Implementation

One module per type under `tap_plugin/okta/models/`, registered in `tap-plugin.toml` `[models]`:
`okta_user` (key `org_name, login`), `okta_group`, `okta_group_rule`, `okta_application` (key
`org_name, label`), `okta_authorization_server`, `okta_identity_provider`, `okta_authenticator`,
`okta_policy` (key `org_name, policy_type, name`), `okta_policy_rule` (key `org_name, policy_type,
policy_name, name`), `okta_network_zone`, `okta_trusted_origin`, `okta_admin_role`, `okta_resource_set`,
`okta_role_assignment`, `okta_api_token`, `okta_device` (key `org_name, okta_id`: only ever observed),
`okta_log_stream`; the rest key on `org_name, name`. Every type carries `org_name`, `okta_id` (blank until
observed, except the device); the vendor facts each carries are its article's
Fields section. **No type has a free-form `configuration` or `tags` field**, the org included (`tags` was removed in migration `0004` because nothing read it: a shapeless map is the same unreviewed-blob risk as `configuration`): the records Okta keeps
can carry secret material and personal data (an application's client secret, an identity provider's signing
keys, a user's profile), and nothing here collects them, so only promoted columns are stored and a record
cannot be passed through whole. Closed vocabularies (`status`, `sign_on_mode`, `policy_type`, `role_type`, ...) are JSON
Schema enums checked against the Okta OpenAPI description dist/2026.08.4, each admitting blank as *not
observed* except where the field is part of the key. `OktaPolicy` declares `EVALUATES_RULE__okta` as its
one containment edge. Migration `0002_okta_corpus_v1`; `0003_drop_unused_configuration` removes the
field. Icons: `static/okta/icons/okta-<type>.svg`.
Articles: `tap_plugin/okta/domain/<type>.md`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-okta-corpus-1 | Registered | Implemented | Eighteen node types in the manifest, each key equal to its model's `ENTITY_TYPE`. | `tests/test_okta_corpus.py` |
| req-okta-corpus-2 | Keys Rest On Columns | Implemented | Every `NATURAL_KEY` field is a model field and a required create field; the same name in two orgs is two nodes. | |
| req-okta-corpus-3 | No Default Dimensions | Implemented | Every type's `DEFAULT_DIMENSIONS` is empty. | |
| req-okta-corpus-4 | Design Nodes Need Only Their Key | Implemented | A write with only the required fields succeeds and leaves `okta_id` blank; dropping any required field is refused. | |
| req-okta-corpus-5 | Closed Vocabularies | Implemented | An enum field refuses a value outside its set and admits blank. | |
| req-okta-corpus-6 | Icons | Implemented | Every `ENTITY_ICON` has an SVG with `width="64" height="64"` and a square viewBox. | Checked by `validate_plugin --strict`. |
| req-okta-corpus-7 | Domain Articles | Implemented | Every node and edge type has a conforming article; every `FIELD_CRUD_SCHEMA` key is in its Fields section. | Checked with `tap.domain_articles.findings_for_root` (zero findings). |
| req-okta-corpus-8 | No Free-Form Record | Implemented | No type declares `configuration`, and a `create_node` write carrying it is refused. | `tests/test_okta_corpus.py` |

---

### Corpus Edge Types
----
RID: `req-okta-edges`

Status: `Implemented`

Twenty-three edges, one relationship each, registered in `tap-plugin.toml` `[edges]` from
`tap_plugin/okta/edges/<SLUG>.edge.json`. The table in [Edge types](#edge-types) records why each points
the way it does.

#### Implementation

Every slug is `<ACTION>_<OBJECT>__okta`. Every property schema is closed (`additionalProperties: false`),
and the properties that decide severity are required where the edge is meaningless without them
(`APPLIES_TO_GROUP.mode`, `MATCHES_NETWORK_ZONE.mode`, `ENROLLS_AUTHENTICATOR.enroll`). No edge declares
default dimensions. The one foreign type named is `identity_core__oidc_issuer` (`SERVES_ISSUER__okta`),
declared in `depends_on` as a vocabulary dependency. Three edges leave their target open and say in their
description what appears there: `SENDS_ASSERTION` (the relying service: a Teleport cluster, a GitLab
instance), `DELEGATES_VERIFICATION` (the external verifier: a Duo account) and `WRITES_LOGS` (the log
destination). `IDENTIFIES_PERSON` (user → open person) was retired on 2026-09-24: identity_core's
`HELD_BY_HUMAN__identity_core` is the same relationship with a real target (`req-okta-person`). An OIDC identity provider reaches its issuer by
identity_core's own `TRUSTS_ISSUER__identity_core`, whose source side is open for exactly this.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-okta-edges-1 | Files Match The Manifest | Implemented | Slug, manifest key and file name agree; every property schema is closed. | `tests/test_okta_corpus.py` |
| req-okta-edges-2 | Open Ends Explained, Substrate Only | Implemented | An omitted target is explained in the description; the only foreign type named is identity_core's, and identity_core is the only `depends_on`. | |
| req-okta-edges-3 | Rules Retire With Their Policy | Implemented | `delete_node(policy, cascade="contained")` retires its rules and ends, never follows, their references. | |
| req-okta-edges-4 | Property Vocabularies Enforced | Implemented | An edge write with an unknown property, or a value outside a property's enum, is refused; a required property is required. | |

---

### Person Link
----
RID: `req-okta-person`

Status: `Implemented`

An Okta user is one person's account in one org; the person is `identity_core__human`, a neutral substrate
node keyed on an operator-assigned handle, so the same human's Okta, Duo, Teleport and GitLab accounts
converge on one node. The link is identity_core's `HELD_BY_HUMAN__identity_core`, whose source is
wildcard so the substrate never depends on this plugin.

#### Implementation

`OktaUser.OUTBOUND_EDGES` declares `{"nodes": [{"type": "identity_core__human"}], "edges": [{"type":
"HELD_BY_HUMAN__identity_core"}]}`. Under the permission union (`req-grid-edge-constraints-3`) this adds a
permission and constrains nothing else: the okta edge files still permit the user's own edges.
`identity_core` is already the plugin's one `depends_on` (a vocabulary dependency); the `ci` record pins
it at `53da388b6f47590090ef3bdc8d98731acff4c8e2`, the commit of identity_core's `v0.1.3` tag, the first
release carrying the human, and `depends_on` declares that release as the floor (`min_version = "0.1.3"`). This retired the corpus's own
`IDENTIFIES_PERSON__okta` (user → open target), which recorded the same relationship while no substrate
owned a person type: two edges for one relationship is the one-edge-one-relationship defect. Email is not
identity: the edge is drawn by whoever knows the match and records how in `matched_on`; nothing joins on
`email`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-okta-person-1 | Declared On The User | Implemented | `OktaUser` declares `HELD_BY_HUMAN__identity_core` to `identity_core__human`; `identity_core` is in `depends_on` with `min_version = "0.1.3"`; `IDENTIFIES_PERSON__okta` is no longer shipped. | `test_person_link_is_declared` |
| req-okta-person-2 | Written Through The Service Layer | Implemented | An Okta user writes the edge to a human with `matched_on`; an unknown property is refused (on a fresh pair). | `test_user_is_held_by_a_human`, `test_unknown_property_is_refused` |
| req-okta-person-3 | Shared Account Recorded | Implemented | One Okta user may be held by two humans; both edges stand. | `test_shared_account_is_recorded` |

---

### Page: Org
----
RID: `req-okta-page-org`

Status: `Implemented`

`/okta` — one Okta org as its operator's front page in a live FedRAMP 20x environment. The graph at the
top, then the tables an assessor asks about first. Reached by direct URL or the site navigation
(`nav_weight` 300); an instance links to it with `?org=<org name>`.

#### Implementation

`grift/okta-page.grift.json` (manifest `[grift] okta_page`), one batch `okta: org page v0.3.0`: the page
node, sixteen `USES_PANEL` edges, a graph panel and fifteen standard table panels, each table over one
search. Every id is defined in the bundle; nothing names an org or an entity id outside it.

- **Parameter.** Every search declares one input, `org` (`["string", "null"]`, default `null`), and
  filters each org it reaches through `BELONGS_TO_ORG__okta` with `($org IS NULL OR o.data.name = $org)`:
  the org's name, matched exactly, or every org when `?org` is absent (the one org on a single-org grid).
  The parameter is the name, not the entity id: an entity id is a UUID foreign key. (Before tap v0.2.2
  Gryphon could not test a parameter for absence, tap#360, and the page defaulted to the org type's slug
  as an every-org sentinel; that workaround is gone.)
- **Both ends in the org.** A search that joins two Okta objects scopes each to the SAME org by binding
  one org variable at both ends: `(o)<-[:BELONGS_TO_ORG__okta]-(a)-[:EDGE]->(b)-[:BELONGS_TO_ORG__okta]->(o)`.
  A repeated variable binds one node (tap#780, fixed in tap v0.2.2), so a cross-org edge never pulls a
  foreign group, role or rule onto the page, including when `?org` is absent and every org is shown. A
  node in the middle of a longer path (the role assignment between holder and role, the rule between
  policy and authenticator) cannot be routed through the org by a linear pattern, so it is filtered on
  its own `org_name` column: `($org IS NULL OR <v>.data.org_name = $org)`.
- **Graph** (`org-graph`, row height `66vh`). `tap_viz/panels/graph_panel.html` over the `okta org`
  projection (`node_style: icon-badge`, `lock_nodes`, `min_zoom: fit`), one elevation, one layout,
  `static/okta/js/projections/okta-org.js`. Sixteen scene searches: the org; what it holds (applications,
  groups, policies and rules, authenticators, identity providers, authorization servers, admin roles and
  assignments, resource sets, network zones, trusted origins, log streams, via `n.entity_type IN [...]`);
  and one search per drawn edge type (`ASSIGNED_APPLICATION` from groups, `BOUND_TO_POLICY`,
  `EVALUATES_RULE`, `REQUIRES_AUTHENTICATOR`, `ENROLLS_AUTHENTICATOR`, `APPLIES_TO_GROUP`,
  `ROUTES_AUTHENTICATION`, `ASSIGNS_GROUP_MEMBERSHIP` from IdPs, `HOLDS_ROLE_ASSIGNMENT` from groups and
  service apps, `GRANTS_ADMIN_ROLE`, `SCOPED_TO_RESOURCE`, `IMPORTS_GROUP`, `MATCHES_NETWORK_ZONE`), never
  an unfiltered edge search; and one cross-vendor search, below. Users, devices, API tokens and group
  rules are left to the tables.
- **The Duo relationship.** /duo draws an Okta org sending its users to a Duo application for a second
  factor (`REQUESTS_SECOND_FACTOR__duo`, whose source duo leaves open). /okta draws the same edge from its
  side: `MATCH (o:okta__okta_org)-[:REQUESTS_SECOND_FACTOR__duo]->(d)<-[:HOLDS_ACCOUNT_OBJECT__duo]-(a)`,
  the org scoped like every other search, returning the Duo application and the Duo account that holds
  it. The pattern names duo's edge types and never its node types: an unknown edge type filters to
  nothing, while an unknown node label is an execution error, so on a grid without duo (okta's own `ci`
  record) the search matches nothing and the graph still draws. okta declares no dependency on duo.
- **Click-through.** The graph panel's config carries `nav_rules` (spec-viz-panel.md,
  `req-viz-panel-click-semantics-8`): the Duo account navigates to `/duo?account={data.name}`, the Duo
  application (which carries no account name) to `/duo`. /duo carries the mirror rule, an Okta org to
  `/okta?org={data.name}`. This is the narrow form, a page path named in the other vendor's panel config.
  The generic form, where the plugin that owns a node type declares the page that answers for it and
  every graph panel routes by it, does not exist in tap_viz yet.
- **Layout module** `okta-org.js` (reusable; exports `FAMILIES` and `humanizeEdgeType`): the org is the
  outer box, holding a 3x3 grid of family boxes: Federation, Authenticators, Network at the top; Groups
  left and Applications right with the centre cell left open (so assignment edges cross it);
  Administration and Policies at the bottom, each policy's rules nested inside it by
  `EVALUATES_RULE__okta`. Family boxes are synthetic containers, joined to their members by
  `_OKTA_FAMILY_HOLDS` and to their org by `_OKTA_ORG_HOLDS`, added and removed on every entry; the nesting
  pass (spec-viz-nested-projection.md) sizes every box, then the module places the families on the grid
  and re-fits the org around them. `BELONGS_TO_ORG__okta` edges are hidden because the containers say it.
  A node of another system's type (not `okta__`) joins no family: it is drawn in a column right of the org
  it connects to by an edge, the Duo application inside its Duo account (a dashed box, nested by
  `HOLDS_ACCOUNT_OBJECT__duo`); a foreign node no org connects to is drawn apart, past every org, and
  reported, never placed beside an org it has no edge to. Every drawn edge is labelled with its type, humanized
  (`EVALUATES_RULE__okta` → "evaluates rule"): `applyStandardChrome(cy, {edgeLabels: true})` keeps the
  label and the module sets its text, since tap_viz has no humanized edge-label option. An okta type no
  family names is drawn in an Other box and reported as a warning, never dropped; each org in the scene
  gets its own container.
- **Tables**, in order: Applications; Who is assigned each application; Admin role assignments; Sign-on
  rules and their factor requirement; Authenticators each rule requires; Authenticators; Authenticator
  enrollment policies; Users who are not active; Sign-in recency; API tokens; Inbound federation;
  Authorization servers; Network zones; Trusted origins; System Log streaming. Each is
  `tap_web/panels/table_panel.html` with `header_tooltip` on every column, `toneBadge` where a value's
  severity is closed-set (a 1FA rule, an account-linking IdP and a super-admin role are red), and a panel
  description that names its third state.
- **What the tables cannot yet say.** The admin table does not join each assignment's scope and the
  API-token table does not join who a token acts as: Gryphon's OPTIONAL MATCH v0 needs a single-node
  mandatory MATCH, and a required join would hide the rows with no observed scope or owner. Both panel
  descriptions say so; the graph draws the scope.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-okta-page-org-1 | Bundle Registered, Layout Shipped | Implemented | The manifest declares the bundle and the layout module the projection names ships in the package. | `tests/test_okta_page.py` |
| req-okta-page-org-2 | Slots Match Panels | Implemented | One `USES_PANEL` per layout slot, graph first, slug `/okta`. | |
| req-okta-page-org-3 | Icon-Badge, Named Edges | Implemented | The projection's `node_style` is `icon-badge`; no scene search matches an untyped edge; every search's `org` input is `[string, null]` with default `null`, tested by `$org IS NULL`. | |
| req-okta-page-org-4 | Reusable | Implemented | Every id an edge names is defined in the bundle. | |
| req-okta-page-org-5 | One Org At A Time | Implemented | Imported with a seeded org, a second org and cross-org edges between them (a foreign node at either end of a join, and in the middle of a longer path), every search returns the seeded org's rows and none of the other's; `?org=a` does not match an org named `aba`; `?org` absent returns every org, and an edge search still keeps both ends in one org. | Real search path (`execute_search`), both databases. |
| req-okta-page-org-6 | Layout Places Without Overlap | Implemented | The org container holds every family box, rules nest in their policies, an unmapped type is reported, no family boxes overlap, the Duo account sits outside the org, and every drawn edge carries its humanized type as a label. | v0.1.0 layout exercised under JavaScriptCore with the vendored Cytoscape (2026-09-22); v0.2.0 observed in a browser on the highbar stack (2026-09-24). Not a shipped test (no JS runner in CI). |
| req-okta-page-org-7 | Renders In A Browser | Implemented | `/okta` renders on a booted stack with every slot filled and no console error from the graph's layout. | Observed 2026-09-24 on the highbar stack with `drive-browser`: the graph and all fifteen tables rendered, console clean. |
| req-okta-page-org-8 | The Duo Link, Both Ways | Implemented | The cross-vendor search names duo's edge types and no duo node type, and okta declares no dependency on duo; with duo installed it returns the org's Duo application and account and none of another org's; without duo it runs and matches nothing. The graph panel's `nav_rules` route the Duo account to `/duo?account=<its name>` and the Duo application to `/duo`; the org itself does not navigate. | `test_duo_link_is_open_ended_and_navigable`, `test_every_search_answers_for_one_org`. Clicked through in a browser on the highbar stack (2026-09-24). |

---

### CI Record and Tests
----
RID: `req-okta-record`

Status: `Implemented`

The in-package `ci` boot record (`req-boot-bootstrap-ci-record`) and the tests that run in it.

#### Implementation

`tap_plugin/okta/boot/ci.boot.json` installs identity_core (pinned at
`53da388b6f47590090ef3bdc8d98731acff4c8e2`, the commit of its `v0.1.3` tag, the `depends_on` floor) and self, offline and credential-free, and seeds the plugin's
own GRIFT; the consumer flips self to editable. Tests: `test_okta_manifest.py` (`validate_plugin` at
structure and strict), `test_okta_org.py`, `test_okta_corpus.py`, `test_okta_page.py`, `test_okta_person.py`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-okta-record-1 | Record Declared | Implemented | The manifest declares the `ci` record with its sha256. | |
| req-okta-record-2 | Validates Strict | Implemented | `validate_plugin --strict` passes on the package. | |

---

### Collector
----
RID: `req-okta-collector`

Status: `Backlog`

Observe a real Okta org onto the grid: a read-only OAuth service app (client credentials, private-key
JWT, the `okta.*.read` scopes the domain articles name) lands every type in the corpus, keyed by
`okta_id`, and records per surface whether it could look (three states: none / some / not observable).
Run `manage-secret` before any credential is named. Every domain article's Observability section is then
rewritten from an executed call.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-okta-collector-1 | Observed, Keyed By Id | Backlog | Every collected node carries `okta_id` and the keys move to `(org_name, okta_id)`. | |

---

### OAuth Scopes, Claims And Grants
----
RID: `req-okta-backlog-oauth-grants`

Status: `Backlog`

Authorization-server scopes and claims as nodes, the access policies and rules on each server, and the
scope grants on each client, when a page needs to say which service app can call which API with which
scope.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-okta-backlog-oauth-grants-1 | Grant Queryable | Backlog | For a service app, a query returns the scopes it was granted and the server that issues them. | |

---

### Provisioning And Integrations
----
RID: `req-okta-backlog-provisioning`

Status: `Backlog`

SCIM provisioning (users pushed to and imported from applications), group push, profile mappings, and
event and inline hooks (Okta calling out to a URL with identity data).

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-okta-backlog-provisioning-1 | Outbound Data Paths Visible | Backlog | Every place Okta sends user data outside itself is an edge. | |

---

### Device Assurance And Realms
----
RID: `req-okta-backlog-device-assurance`

Status: `Backlog`

Device assurance policies and the rules that require them, Okta Verify posture signals, realms, and the
link from `okta__okta_device` to a neutral device type.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-okta-backlog-device-assurance-1 | Device Condition Queryable | Backlog | A rule's device requirement is an edge to the assurance policy it names. | |

---

### Non-goals
----
RID: `req-okta-nongoals`

Status: `Implemented`

What this plugin will not model, so the question is not re-opened: capability edges derived from a role
assignment and its scope (BloodHound's `Okta_ResetFactors` and kin: a traversal computes them); sessions
and System Log events as nodes (an event stream a collector reads); brands, custom domains and email
templates as nodes (org configuration); key and secret material (never stored); the Active Directory
agent integration (agents, agent pools, Kerberos SSO, password sync) until a consumer needs it.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-okta-nongoals-1 | None Shipped | Implemented | No type or edge in the manifest models any of the above. | |

## Model catalog

Superseded by the manifest as of v0.1.0: the classes and their articles are the one source. What the code
cannot state:

| Model | Entity type | Category | Rationale |
| --- | --- | --- | --- |
| `OktaRoleAssignment` | `okta__okta_role_assignment` | node for a three-way fact | Principal, role and scope: an edge cannot carry a third endpoint. |
| `OktaPolicyRule` | `okta__okta_policy_rule` | node | Neither graph source models rules, yet factor mode, zones and routing live on the rule. |
| (rejected) `OktaUserFactor` | — | edge instead | An enrollment is a fact about a (user, authenticator) pair: `ENROLLED_AUTHENTICATOR__okta`. |
| (rejected) `ReplyUri`, `OktaUserType` | — | fields instead | Nothing but the parent points at them. |

## Edge types

Superseded by the manifest as of v0.1.0. Decisions the files cannot state:

| Edge | From → To | Properties | Rationale |
| --- | --- | --- | --- |
| `BELONGS_TO_ORG__okta` | every okta type → org | — | Points from the object to its tenant, as a membership (like `BELONGS_TO_ACCOUNT`), not a generic `CONTAINS` from the org. |
| `ACTS_AS_USER__okta` | API token → user | — | BloodHound points user → token; the token is the actor, so the edge starts there. |
| `SENDS_ASSERTION__okta` | application → open | `protocol`, `endpoint` | The relying service is another plugin's node; naming its type would make every relying service an edit here. |
| `DELEGATES_VERIFICATION__okta` | authenticator → open | `protocol`, `api_hostname` | "Duo as an authenticator" without depending on the duo plugin. |
| `SERVES_ISSUER__okta` | authorization server → `identity_core__oidc_issuer` | — | The issuer URL lives once, on the substrate node relying services also trust. |
| `SCOPED_TO_RESOURCE__okta` | role assignment → resource set, group, application | — | The absence of the edge is the finding (whole org). |

## Icons

`okta-org` is Okta's own mark from simple-icons (CC0 SVG), used nominatively to identify the vendor on
diagrams; the mark remains Okta's trademark and is not covered by this repository's licence. Every other
icon is a plain glyph drawn for this plugin (a white glyph on a rounded tile, 64x64, square viewBox), one
colour per family: blue for users, groups and group rules; indigo for applications, authorization servers
and identity providers; teal for authenticators; amber for policies and rules; red for admin roles,
resource sets, role assignments and API tokens; slate for network zones, trusted origins, devices and log
streams.
