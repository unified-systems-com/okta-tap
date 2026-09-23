# Okta API Token

## Blurb

An Okta API token (SSWS): a long-lived secret that acts with the admin permissions of the user who created it.

## Purpose

An API token's metadata; the secret is never stored. The user it acts as is ACTS_AS_USER__okta.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Show standing API credentials and whose permissions they carry.

## Identity

Natural key: `org_name`, `name`. Token names are what an operator sees; Okta does not require them unique, so the key is revisited to (org_name, okta_id).

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- No free-form `configuration` field: the records Okta keeps for this object can carry secret material or personal data (a client secret, a signing key, a user's profile), so only promoted columns are stored.
- The token secret is never stored or seen: the API returns metadata only.

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/api-tokens` (okta.apiTokens.read). The API reports `expiresAt` and `lastUpdated`, no last-used time.

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21) — `Okta_ApiToken`, `Okta_ApiTokenFor`.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `name` — The token's name.
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `client_name` — The client Okta recorded when the token was created (Okta Admin Console, a CLI).
- `created_at` — When the token was created.
- `expires_at` — expiresAt: Okta moves it forward on every use (a token expires after 30 days unused), so it is also the API's only read on recent use. The API reports no last-used time.
- `network_connection` — network.connection: whether the token is usable from anywhere or only from listed zones.
- `tags` — TAP's tag map.
