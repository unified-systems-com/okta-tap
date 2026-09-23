# Okta Authorization Server

## Blurb

An OAuth 2.0 / OIDC authorization server in an Okta org: the org authorization server, the default custom server, or a custom server, each an OIDC issuer.

## Purpose

An authorization server: the thing that mints tokens. Its issuer is the neutral identity_core__oidc_issuer node reached by SERVES_ISSUER__okta; the issuer URL lives there, not here.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Tie an Okta-minted token to the neutral OIDC issuer a relying service trusts (SERVES_ISSUER).

## Identity

Natural key: `org_name`, `name`. Server names are unique within an org (the org server is named for the org); revisited to (org_name, okta_id).

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- Scopes and claims are fields in v1; access policies, their rules and per-client grants are Backlog (`req-okta-backlog-oauth-grants`).
- The issuer URL lives on `identity_core__oidc_issuer`, not here.

## Neutrality

Vendor-specific record of a neutral thing: the OIDC issuer is identity_core's, the server that runs it is Okta's.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/authorizationServers` (okta.authorizationServers.read) lists custom servers; the org server is not in that list and is inferred from the org.

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21) — `Okta_AuthorizationServer`.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `name` — The server's name ('default' for the default custom server).
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `server_kind` — Which of Okta's three kinds this is. The org server issues tokens for Okta's own APIs and for apps that use the org URL as issuer.
- `status` — Okta's server status.
- `issuer_mode` — Which domain the issuer uses.
- `audiences` — The audiences the server mints tokens for.
- `scopes` — Custom scope names. A field in v1: nothing yet needs to point at a scope (Backlog: req-okta-backlog-oauth-grants).
- `claims` — Custom claim names. A field in v1 for the same reason as scopes.
- `configuration` — The remainder of the object as Okta returns it; nothing identity-bearing lives here.
- `tags` — TAP's tag map.
