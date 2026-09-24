# Okta Authenticator

## Blurb

An authenticator configured in an Okta org: Okta Verify, a security key (WebAuthn/FIDO2), password, email, phone, a smart card, or an external verifier such as Duo.

## Purpose

An authenticator as the org configures it. Which users enrolled it is the ENROLLED_AUTHENTICATOR__okta edge (Cartography's OktaUserFactor is that edge, not a node). An authenticator that hands verification to another service (Duo, an external IdP) reaches it by the open-ended DELEGATES_VERIFICATION__okta edge.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Name the authenticators policies require and users enroll, so 'is MFA enforced, and with what' is a query.

## Identity

Natural key: `org_name`, `name`. Authenticator names are unique within an org; revisited to (org_name, okta_id).

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- No free-form `configuration` field: the records Okta keeps for this object can carry secret material or personal data (a client secret, a signing key, a user's profile), so only promoted columns are stored.
- A user's enrolled factor is the ENROLLED_AUTHENTICATOR edge, not a node.
- Duo's own configuration is the duo plugin's; this node records only that Okta hands verification to it.

## Neutrality

Vendor-specific: Okta's authenticator configuration. 'Second factor method' is general, but the set and its settings are Okta's.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/authenticators` (okta.authenticators.read); a user's enrollments by `GET /api/v1/users/{id}/factors`.

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- Cartography Okta intel module, `cartography/models/okta/` at commit 030848289203969e19a17bf25e45ff94a527bcef (2026-08-30) — `OktaAuthenticator`, `OktaUserFactor`.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `name` — The authenticator's name as the org shows it (for example 'Okta Verify', 'Duo Security').
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `authenticator_key` — Okta's key: okta_verify, webauthn, security_key, okta_password, okta_email, phone_number, duo, google_otp, security_question, smart_card_idp, external_idp, custom_app, onprem_mfa, symantec_vip, yubikey_token, tac. Free text: Okta adds keys.
- `authenticator_type` — Okta's type: app, password, email, phone, security_key, security_question, federated, tac.
- `status` — Okta's authenticator status.
- `phishing_resistant` — Whether the authenticator can satisfy a phishing-resistant constraint (FastPass, WebAuthn, smart card). Null means not observed.
