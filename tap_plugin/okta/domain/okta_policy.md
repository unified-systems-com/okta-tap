# Okta Policy

## Blurb

A policy in an Okta org: a global session, authentication (app sign-on), password, authenticator enrollment, IdP routing or other policy, evaluated through its ordered rules.

## Purpose

One policy of one type. Which groups it applies to is APPLIES_TO_GROUP__okta, its rules are EVALUATES_RULE__okta, an authentication policy's applications are BOUND_TO_POLICY__okta, and an enrollment policy's authenticators are ENROLLS_AUTHENTICATOR__okta.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Hold the global session, authentication, password, enrollment and routing policies an assessor reads first.

## Identity

Natural key: `org_name`, `policy_type`, `name`. Policy names are unique per type within an org; revisited to (org_name, okta_id).

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- No free-form `configuration` field: the records Okta keeps for this object can carry secret material or personal data (a client secret, a signing key, a user's profile), so only promoted columns are stored.
- Authorization-server access policies are Backlog (`req-okta-backlog-oauth-grants`).
- Device assurance policies are Backlog (`req-okta-backlog-device-assurance`).

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/policies?type=<TYPE>` (okta.policies.read), one call per policy type.

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21) — `Okta_Policy`, `Okta_PolicyMapping`.
- Okta Terraform provider (okta/okta) resource list, from the author's knowledge; not re-read in this pass — okta_policy_signon, okta_app_signon_policy, okta_policy_mfa, okta_policy_password.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `policy_type` — Okta's policy type: OKTA_SIGN_ON is the global session policy, ACCESS_POLICY an authentication (app sign-on) policy, MFA_ENROLL authenticator enrollment, IDP_DISCOVERY IdP routing.
- `name` — The policy's name.
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `status` — Okta's policy status.
- `priority` — Evaluation order among policies of the same type (1 first). Null for types Okta does not order (ACCESS_POLICY).
- `system` — True for the policy Okta ships and will not let you delete (the Default Policy). Null means not observed.
- `description` — The policy's description.
