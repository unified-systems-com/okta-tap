# Okta Application

## Blurb

An application integration in an Okta org: a SAML, OIDC, WS-Fed, SWA or bookmark app that users sign in to through Okta, or an API service app.

## Purpose

An application integration. For an SSO relying party (Teleport, GitLab) this is Okta's side of the trust; the relying service's own node is reached by the open-ended SENDS_ASSERTION__okta edge. An OAuth service app (client credentials, application_type=service) is the same type.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Name every relying service Okta signs users in to, with its sign-on mode.
- Be the Okta side of an SSO trust whose other side (Teleport, GitLab) is another plugin's node.

## Identity

Natural key: `org_name`, `label`. label is what an operator and a design name; Okta does not require it unique, so the key is revisited to (org_name, okta_id) when the collector lands.

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- No free-form `configuration` field: the records Okta keeps for this object can carry secret material or personal data (a client secret, a signing key, a user's profile), so only promoted columns are stored.
- Reply URIs are a field (`redirect_uris`), not nodes as in Cartography's ReplyUri: nothing but the application points at one.
- Provisioning (SCIM push, import schedules, profile mappings) is Backlog (`req-okta-backlog-provisioning`).
- Client secrets and signing keys are never stored.

## Neutrality

Vendor-specific: an Okta app integration. The relying service is neutral or another vendor's, which is why SENDS_ASSERTION leaves its target open.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/apps` (okta.apps.read); assignments by `GET /api/v1/apps/{id}/users` and `/groups`.

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- Cartography Okta intel module, `cartography/models/okta/` at commit 030848289203969e19a17bf25e45ff94a527bcef (2026-08-30) — `OktaApplication`, `ReplyUri`.
- BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21) — `Okta_Application`, `Okta_AppAssignment`, `Okta_OutboundSSO`, `Okta_SWA`.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `label` — The application's display label (what users see on the dashboard).
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `app_name` — Okta's app name: the catalog key (for example 'oidc_client', 'teleport', 'gitlab') or a generated key for a custom app.
- `sign_on_mode` — Okta's signOnMode. BROWSER_PLUGIN and AUTO_LOGIN are Secure Web Authentication (password vaulting).
- `status` — Okta's app lifecycle status.
- `application_type` — For OIDC and service apps: settings.oauthClient.application_type. Blank for SAML and SWA apps.
- `client_id` — For OIDC and service apps: the OAuth client_id (Okta uses the app id).
- `redirect_uris` — OIDC redirect URIs or the SAML ACS URL(s). A field, not a node: nothing but the app points at a reply URI.
- `grant_types` — OIDC/OAuth grant types the client may use.
