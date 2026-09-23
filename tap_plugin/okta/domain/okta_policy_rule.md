# Okta Policy Rule

## Blurb

A rule in an Okta policy: its conditions (people, network zones) and its action (allow or deny, the factors it requires, re-authentication frequency).

## Purpose

One rule of one policy, reached from the policy by EVALUATES_RULE__okta and retired with it. The authenticators a rule requires are REQUIRES_AUTHENTICATOR__okta edges; its zones are MATCHES_NETWORK_ZONE__okta; an IdP routing rule's target is ROUTES_AUTHENTICATION__okta.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Make the evaluation order and the catch-all rule visible, and carry the factor requirement where it is actually decided.

## Identity

Natural key: `org_name`, `policy_type`, `policy_name`, `name`. Rule names are unique within a policy, so the key carries the policy's own key alongside; revisited to (org_name, okta_id).

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- No free-form `configuration` field: the records Okta keeps for this object can carry secret material or personal data (a client secret, a signing key, a user's profile), so only promoted columns are stored.
- Rule conditions other than people and network zones (risk, device, platform) are not stored in v0.

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/policies/{id}/rules` (okta.policies.read).

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- Okta Terraform provider (okta/okta) resource list, from the author's knowledge; not re-read in this pass — okta_policy_rule_signon, okta_app_signon_policy_rule, okta_policy_rule_idp_discovery.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `policy_type` — The owning policy's type: part of the key, because the policy's own key is (org_name, policy_type, name).
- `policy_name` — The owning policy's name: part of the key.
- `name` — The rule's name.
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `status` — Okta's rule status.
- `priority` — Evaluation order within the policy (1 first). The catch-all rule is last.
- `access` — The rule's access decision.
- `factor_mode` — How many factor types the rule demands: ACCESS_POLICY verificationMethod.factorMode; for a global session rule, 2FA when requireFactor is true. Blank means not observed, never 'no MFA'.
- `reauthenticate_in` — ISO-8601 duration before the user must re-verify (PT12H); blank when not observed.
- `tags` — TAP's tag map.
