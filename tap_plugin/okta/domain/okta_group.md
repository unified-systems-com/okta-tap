# Okta Group

## Blurb

A group in an Okta org: an Okta-mastered group, a group imported from an application, or a built-in group such as Everyone.

## Purpose

A group of users in one Okta org. group_type separates Okta-mastered groups from groups an application (AD, LDAP, an HR system) masters and Okta only imports; the importing application is the IMPORTS_GROUP__okta edge.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Carry assignments and policy conditions that name groups, which is how Okta grants almost everything.

## Identity

Natural key: `org_name`, `name`. Group names are unique within an org; revisited to (org_name, okta_id) with the collector.

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- No free-form `configuration` field: the records Okta keeps for this object can carry secret material or personal data (a client secret, a signing key, a user's profile), so only promoted columns are stored.
- Group push to downstream applications (a group's membership pushed to an app) is Backlog (`req-okta-backlog-provisioning`).

## Neutrality

Vendor-specific. 'Group of accounts' is general, but its membership semantics (rules, app-mastered groups) are Okta's.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/groups` (okta.groups.read); members by `GET /api/v1/groups/{id}/users`.

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- Cartography Okta intel module, `cartography/models/okta/` at commit 030848289203969e19a17bf25e45ff94a527bcef (2026-08-30) — `OktaGroup`, `OktaGroupRule` (`ASSIGNED_BY_GROUP_RULE`).
- BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21) — `Okta_Group`, `Okta_GroupPull`, `Okta_GroupPush`.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `name` — profile.name.
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `group_type` — Okta's group type: mastered in Okta, imported from an application, or built in (Everyone).
- `description` — profile.description.
- `tags` — TAP's tag map.
