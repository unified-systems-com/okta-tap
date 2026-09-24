# Okta Network Zone

## Blurb

A network zone in an Okta org: a named set of IP ranges, or a dynamic zone of locations, ASNs and anonymizer categories, used in policy conditions or as a blocklist.

## Purpose

A network zone. Rules reach it by MATCHES_NETWORK_ZONE__okta.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Show which networks the sign-on rules trust or exclude, and what is blocklisted.

## Identity

Natural key: `org_name`, `name`. Zone names are unique within an org; revisited to (org_name, okta_id).

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- No free-form `configuration` field: the records Okta keeps for this object can carry secret material or personal data (a client secret, a signing key, a user's profile), so only promoted columns are stored.
- IP ranges stay strings; they are not linked to computing_core IP address nodes in v1.

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/zones` (okta.networkZones.read).

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- Okta Terraform provider (okta/okta) resource list, from the author's knowledge; not re-read in this pass — okta_network_zone.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `name` — The zone's name (LegacyIpZone, BlockedIpZone and DefaultEnhancedDynamicZone are Okta's).
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `zone_type` — IP zones list addresses; dynamic zones list locations, ASNs and proxy types.
- `usage` — POLICY zones are referenced by rules; BLOCKLIST zones are refused before any policy runs.
- `status` — Okta's zone status.
- `system` — True for the zones Okta ships. Null means not observed.
- `gateways` — IP zone gateway ranges (CIDR or range strings).
- `proxies` — IP zone trusted proxy ranges.
