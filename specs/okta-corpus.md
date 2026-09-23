# Okta Vocabulary Corpus (v1, 2026-09-22)

The decision record behind the okta plugin's node and edge types (`build-domain-vocabulary`). It is a
dated artefact with a maintenance obligation: when a source below revises, this file names which types
it touches. The requirements live in [`spec-okta-v0.md`](spec-okta-v0.md); each type's own case is its
domain article under `tap_plugin/okta/domain/`.

## Step 0: Domain and boundary

- **In scope.** An Okta workforce-identity org as its operator answers for it in a FedRAMP 20x
  environment: who can sign in to what, with which factors, from where; who administers the org; which
  standing credentials exist; where its audit log goes. The org may be commercial or Okta for Government
  (Moderate, High, DoD IL4); the vocabulary is the same, `okta__okta_org.service_offering` says which.
- **Out of scope.** Okta Customer Identity (Auth0), Okta Identity Governance (access requests,
  certifications), Okta Privileged Access, Okta Workflows. Also the relying services themselves (Teleport,
  GitLab, AWS), which their own plugins model, and Duo, which the duo plugin models.
- **First real use case.** highbar's design seed: an Okta for Government High org that signs engineers
  in to Teleport and GitLab, requires Duo through an authentication policy, and holds a small set of
  administrators. The /okta page is the second: a live org's front page.

## Step 1: What already exists (queried on the running highbar stack, 2026-09-22)

- `okta__okta_org` (this plugin, v0). Kept, extended with `okta_id` and `service_offering`.
- `identity_core__oidc_issuer` holds the OIDC issuer URL. **Reused:** the Okta authorization server
  does not carry its issuer; it points at the issuer node (`SERVES_ISSUER__okta`), and an OIDC identity
  provider reaches its issuer by identity_core's own `TRUSTS_ISSUER__identity_core`, whose source side is
  deliberately open.
- `identity_core__organization` is a customer or company, not a tenant; not used.
- `computing_core__user` ("a human who interacts with computing systems") is the only person-like type on
  the grid. It is keyed on a display name alone, which is too weak to converge accounts on; the Okta user
  therefore points at a person through the open-ended `IDENTIFIES_PERSON__okta` and the neutral
  person/principal type is reported as a substrate gap.
- `duo__duo_account`, `teleport__teleport_cluster`, `gitlab__gitlab_instance` exist. Named nowhere in
  this plugin: the edges that reach them (`DELEGATES_VERIFICATION__okta`, `SENDS_ASSERTION__okta`) leave
  their target open.
- The spine gives history and provenance: who created a trusted origin (Cartography's `CREATED_BY`) and
  when a policy changed are grid history, not nodes or edges.

## Step 2: Sources (source register)

| Source | Version / date | Artifact | Verdict |
| --- | --- | --- | --- |
| Okta Management API OpenAPI description | `okta/okta-management-openapi-spec` dist/2026.08.4, commit `74fcd17f` (2026-09-09) | `dist/2026.08.4/management-*.yaml` | **Adopt** for names and enums: every enum on a model was checked against this file. Cadence: monthly dist folders; "what changed" is a new dist folder. |
| Cartography Okta intel module | `cartography-cncf/cartography` `cartography/models/okta/`, commit `03084828` (2026-08-30) | Python node/rel schemas | **Align.** Borrowed: org, user, group, group rule, application, authenticator, trusted origin, the user-account ontology label. Rejected: `ReplyUri` and `OktaUserType` as nodes, `OktaUserFactor` as a node, `CREATED_BY` / `LAST_UPDATED_BY`. |
| BloodHound OpenGraph Okta extension | schema page read 2026-09-22; collector `SpecterOps/OktaHound` 2.8.2 (2026-04-21) | Node and edge kind list | **Align.** Borrowed: authorization server, identity provider, policy, resource set, role assignment as a node, API token, device, and the role-assignment / resource-set / scope shape. Rejected: capability-derived edges (`Okta_ResetFactors`, `Okta_HelpDeskAdmin` and kin), `Okta_Agent` / `AgentPool`, `Okta_JWK`, `Okta_ClientSecret`, `Okta_Realm`, `Okta_*Sync` edges. |
| Okta Terraform provider (`okta/okta`) | author's knowledge; not re-read in this pass | Resource list | **Reference** for the policy family (`okta_policy_signon`, `okta_app_signon_policy(_rule)`, `okta_policy_mfa`, `okta_policy_rule_idp_discovery`), `okta_network_zone`, `okta_log_stream`, `okta_resource_set`. |
| Incident corpus | Okta support-system breach (Oct 2023); help-desk social engineering of super administrators followed by a second IdP for cross-tenant impersonation (Aug–Sep 2023, Okta's own advisory); Lapsus$ via a support contractor (2022) | Public advisories | **Demand.** Each incident's story needs: admin role assignments and their holders, help-desk capability over factors, inbound identity providers with account linking, IdP routing rules, sessions from unexpected networks, standing API tokens, and a log stream an investigator can read. Every one is representable in v1 except sessions and the capability derivation (see Rejected). |

The people pass (Step 2's fourth direction) was not run for this vocabulary; SpecterOps' OpenGraph team
and Cartography's maintainers are the obvious follows.

## Step 3–6: Node inventory

Tier 1 = built in v1 (the design seed and the /okta page need it). Neutral = could a structurally
different identity provider populate it unchanged.

| Type | Neutral? | Tier | Status | Justification (sources, incidents) |
| --- | --- | --- | --- | --- |
| `okta__okta_org` | no (tenant) | 1 | exists, extended | Cartography, BloodHound; every scope. |
| `okta__okta_user` | no (account) | 1 | new | Cartography, BloodHound, API; stale and suspended accounts on the page. |
| `okta__okta_group` | no | 1 | new | Cartography, BloodHound, API; the unit of every assignment. |
| `okta__okta_group_rule` | no | 1 | new | Cartography, API; explains automatic membership of privileged groups. |
| `okta__okta_application` | no | 1 | new | Cartography, BloodHound, API; relying parties (Teleport, GitLab). |
| `okta__okta_authorization_server` | vendor record of a neutral issuer | 1 | new | BloodHound, API; the issuer relying services trust. |
| `okta__okta_identity_provider` | no | 1 | new | BloodHound, API; the 2023 impersonation technique. **Ahead of Cartography.** |
| `okta__okta_authenticator` | no | 1 | new | Cartography, API; "requires Duo". |
| `okta__okta_policy` | no | 1 | new | BloodHound, Terraform, API; MFA enforcement is decided here. |
| `okta__okta_policy_rule` | no | 1 | new | Terraform, API. **Ahead of both graph sources:** neither models rules, yet factor mode, zones and routing all live on the rule. |
| `okta__okta_network_zone` | no | 1 | new | Terraform, API. |
| `okta__okta_trusted_origin` | no | 1 | new | Cartography, API. |
| `okta__okta_admin_role` | no | 1 | new | Cartography, BloodHound, API; incident demand. |
| `okta__okta_resource_set` | no | 1 | new | BloodHound, API. |
| `okta__okta_role_assignment` | no | 1 | new | BloodHound, API. A node because it is a three-way fact (principal, role, scope). |
| `okta__okta_api_token` | no | 1 | new | BloodHound, API; standing credentials. |
| `okta__okta_device` | no (neutral device is computing_core's concern) | 1 | new | BloodHound, API; Okta Verify / FastPass. |
| `okta__okta_log_stream` | no | 1 | new | Terraform, API; FedRAMP audit-log delivery. **No graph source models it.** |

## Edge inventory

Every edge is `__okta`. Properties are closed (`additionalProperties: false`); each property settles a
question named in its schema description.

| Edge | Source → target | Properties (question settled) | Justification |
| --- | --- | --- | --- |
| `BELONGS_TO_ORG` | every okta type → org | none | Page and query scoping. BloodHound `Okta_Contains`, Cartography `RESOURCE`, reversed to a membership. |
| `MEMBER_OF_GROUP` | user → group | `managed_by` (will a manual removal stick?) | All three sources. |
| `ASSIGNS_GROUP_MEMBERSHIP` | group rule, IdP → group | `action` (RULE / ASSIGN / APPEND / SYNC: does it remove as well as add?) | Cartography, BloodHound, API. |
| `ASSIGNED_APPLICATION` | user, group → application | `scope`, `priority`, `status` (direct or inherited; which profile wins) | All three sources. |
| `IMPORTS_GROUP` | application → group | none | BloodHound `Okta_GroupPull`. |
| `SENDS_ASSERTION` | application → open | `protocol`, `endpoint` (federated or vaulted; where the assertion lands) | BloodHound outbound SSO; the relying service is another plugin's node. |
| `SERVES_ISSUER` | authorization server → `identity_core__oidc_issuer` | none | Substrate reuse (the only foreign type named). |
| `BOUND_TO_POLICY` | application → policy | none | BloodHound `Okta_PolicyMapping`. |
| `EVALUATES_RULE` | policy → policy rule | `priority` (evaluation order) | API; the one containment edge. |
| `APPLIES_TO_GROUP` | policy, policy rule → group | `mode` required (include or exclude: who is NOT covered) | API. **Ahead of the graph sources.** |
| `MATCHES_NETWORK_ZONE` | policy rule → network zone | `mode` required | API. |
| `REQUIRES_AUTHENTICATOR` | policy rule → authenticator | `constraint`, `phishing_resistant`, `hardware_protected` (MFA versus phishing-resistant MFA) | API. **Ahead of the graph sources.** |
| `ENROLLS_AUTHENTICATOR` | policy → authenticator | `enroll` required (REQUIRED / OPTIONAL / NOT_ALLOWED) | API. |
| `ROUTES_AUTHENTICATION` | policy rule → identity provider | none | API; incident demand. |
| `ENROLLED_AUTHENTICATOR` | user → authenticator | `status`, `factor_type`, `created_at`, `last_verified_at` | Cartography's `OktaUserFactor`, as an edge. |
| `DELEGATES_VERIFICATION` | authenticator → open | `protocol`, `api_hostname` (which verifier, over what) | "Duo as an authenticator": the Duo side is the duo plugin's. |
| `HOLDS_ROLE_ASSIGNMENT` | user, group, application → role assignment | none | BloodHound. |
| `GRANTS_ADMIN_ROLE` | role assignment → admin role | none | BloodHound. |
| `SCOPED_TO_RESOURCE` | role assignment → resource set, group, application | none (absence of the edge = whole org) | BloodHound `Okta_ScopedTo`. |
| `INCLUDES_RESOURCE` | resource set → user, group, application, authorization server, IdP, policy, admin role, device | none | BloodHound `Okta_ResourceSetContains`. |
| `ACTS_AS_USER` | API token → user | none | BloodHound `Okta_ApiTokenFor`, reversed to the direction of action. |
| `REGISTERED_DEVICE` | user → device | none | BloodHound `Okta_DeviceOf`, reversed. |
| `WRITES_LOGS` | log stream → open | none | aws_core's `WRITES_LOGS` mechanism; destination is another plugin's node. |
| `IDENTIFIES_PERSON` | user → open | none | Account/person split (Cartography's `USER_ACCOUNT` ontology label). |

## Rejected candidates

| Candidate | Source | Why not (and which test decided) |
| --- | --- | --- |
| `ReplyUri` node | Cartography | Nothing but the application points at it (strongest test): `redirect_uris` field. |
| `OktaUserType` node | Cartography | Same test: `user_type` field. |
| `OktaUserFactor` node | Cartography | The facts are about the (user, authenticator) pair: edge properties on `ENROLLED_AUTHENTICATOR`. |
| Capability edges (`Okta_ResetFactors`, `Okta_ResetPassword`, `Okta_HelpDeskAdmin`, `Okta_ManageApp`, `Okta_ReadClientSecret`, ...) | BloodHound | Derived facts: a role assignment plus its scope already imply them. Deriving them into stored edges is the derive-a-fact-twice anti-pattern; a view or path can compute them. Revisit if a page needs them as first-class. |
| `Okta_Agent`, `Okta_AgentPool`, `Okta_KerberosSSO`, `Okta_PasswordSync` | BloodHound | Active Directory agent integration: not part of a FedRAMP cloud-only org's first use case. Tier 3. |
| `Okta_JWK`, `Okta_ClientSecret` | BloodHound | Key and secret material: never stored; their existence is a field on the application when needed. |
| `Okta_Realm` | BloodHound, API | Realms partition users for delegated administration; no demand yet. Tier 2 (`req-okta-backlog-device-assurance` lists it with the other partitioning features). |
| OAuth scopes, claims, grants and authorization-server policies as nodes | API | No edge needs to point at a scope in v1; kept as fields. Tier 2 (`req-okta-backlog-oauth-grants`). |
| Group push, user provisioning (SCIM), profile mappings | BloodHound, API | Provisioning to downstream apps. Tier 2 (`req-okta-backlog-provisioning`). |
| Sessions | API | Ephemeral; the System Log records them. A collector question, not vocabulary. |
| System Log events as nodes | API | An event stream: what a collector reads, and grid history keeps the result. |
| Brands, custom domains, email templates | API, Terraform | Configuration of the org; no security question depends on them as nodes. |
| Event hooks, inline hooks | API | Real outbound data paths; Tier 2 (`req-okta-backlog-provisioning` names them with the other integrations). |
| Device assurance policies | API | Tier 2 (`req-okta-backlog-device-assurance`). |

## Step 9: The update seam (recorded, not built)

- **Okta OpenAPI description:** a new `dist/<yyyy.mm.n>` folder monthly in
  `okta/okta-management-openapi-spec`. A ledger job diffs the enums named in the models against the new
  folder and opens a proposal. This pass checked them against `dist/2026.08.4`.
- **Cartography:** `cartography/models/okta/` git history.
- **BloodHound OpenGraph Okta:** the extension's schema page and `SpecterOps/OktaHound` releases.

## Gaps reported to the substrate owners (not edited here)

- **A neutral person / principal type.** identity_core has none; `computing_core__user` is keyed on a
  display name. `IDENTIFIES_PERSON__okta` waits for it.
- **Core permission union.** An edge type's `sources` / `targets` are not enforced for a node type that
  declares no `OUTBOUND_EDGES` / `INBOUND_EDGES` (`tap_grid/constraints.py`, `validate_edge`); the okta
  tests assert the declaration rather than a refusal.
- **Gryphon optional filter** (tap#360): the page matches the org by exact name, with the org type's
  slug as an every-org sentinel default, because an entity id is a UUID foreign key (a blank default
  fails validation, and it cannot be prefix-matched) and a parameter cannot be tested for absence.
- **Gryphon variable reuse inside one pattern** does not unify: `(p)-[...]->(o)<-[...]-(p)` returned
  rows whose second `p` was a different node (probed 2026-09-22). The page runs its paths org to org
  instead; a wrong-answer candidate for `gryphon-fix-bug`.
- **Gryphon OPTIONAL MATCH v0** needs a single-node mandatory MATCH, so the API-token and admin tables
  cannot join an optional owner or scope.
