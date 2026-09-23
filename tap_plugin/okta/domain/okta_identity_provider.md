# Okta Identity Provider

## Blurb

An inbound identity provider in an Okta org: an external SAML or OIDC IdP (another Okta org, Entra ID, Google) whose assertions Okta accepts to sign users in.

## Purpose

Inbound federation. The most consequential object in an Okta org after the super admin: an IdP that can JIT-provision and account-link users can sign in as them. An OIDC IdP's issuer is reached by identity_core's TRUSTS_ISSUER__identity_core edge.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Make inbound federation visible: which external IdPs can sign users in, and whether they can link to existing accounts.

## Identity

Natural key: `org_name`, `name`. IdP names are unique within an org; revisited to (org_name, okta_id).

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- IdP signing certificates and client secrets are never stored.
- Social and identity-verification providers are the same type, distinguished by `idp_type`.

## Neutrality

Vendor-specific record. An OIDC IdP's issuer is identity_core's neutral `oidc_issuer`, reached by identity_core's own TRUSTS_ISSUER edge.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/idps` (okta.idps.read).

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21) — `Okta_IdentityProvider`, `Okta_InboundSSO`, `Okta_IdpGroupAssignment`.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `name` — The IdP's name.
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `idp_type` — Okta's IdP type: SAML2, OIDC, X509 (smart card), MICROSOFT, GOOGLE, LOGINGOV, GITHUB, GITLAB, an identity-verification vendor (IDV_*) and others. Free text: Okta adds types.
- `protocol_type` — protocol.type.
- `status` — Okta's IdP status.
- `provisioning_action` — policy.provisioning.action: AUTO means Just-In-Time provisioning creates users from assertions.
- `account_link_action` — policy.accountLink.action: AUTO links an assertion to an EXISTING user. With AUTO an IdP can sign in as that user.
- `subject_match_type` — policy.subject.matchType: how the assertion's subject is matched to a user (USERNAME, EMAIL, USERNAME_OR_EMAIL, CUSTOM_ATTRIBUTE).
- `configuration` — The remainder of the object as Okta returns it; nothing identity-bearing lives here.
- `tags` — TAP's tag map.
