# Okta Admin Role

## Blurb

An administrator role in an Okta org: a standard role such as Super Administrator or Help Desk Administrator, or a custom role with its own permissions.

## Purpose

A role: a bundle of admin permissions. Who holds it, and over what, is an okta__okta_role_assignment.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Name the roles that make someone an Okta administrator, standard and custom.

## Identity

Natural key: `org_name`, `name`. Standard roles are named by Okta and custom role labels are unique within an org; revisited to (org_name, okta_id) for custom roles.

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- Individual permissions are a list on the role, not nodes.

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: Custom roles by `GET /api/v1/iam/roles` (okta.roles.read); standard roles are Okta's fixed set.

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- Cartography Okta intel module, `cartography/models/okta/` at commit 030848289203969e19a17bf25e45ff94a527bcef (2026-08-30) — `OktaUserRole`, `OktaGroupRole`.
- BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21) — `Okta_Role`, `Okta_CustomRole`.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `name` — The role's label (Super Administrator, or a custom role's label).
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `role_type` — Okta's standard role type, or CUSTOM.
- `permissions` — A custom role's permissions (okta.users.manage, ...). Blank for standard roles: Okta defines those.
- `description` — The role's description.
- `configuration` — The remainder of the object as Okta returns it; nothing identity-bearing lives here.
- `tags` — TAP's tag map.
