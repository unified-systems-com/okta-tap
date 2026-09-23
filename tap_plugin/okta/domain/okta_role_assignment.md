# Okta Role Assignment

## Blurb

An administrator role assignment in an Okta org: one principal (user, group or service app) holding one admin role, over the whole org or a scoped set of resources.

## Purpose

A three-way fact (principal, role, scope), so a node rather than an edge: HOLDS_ROLE_ASSIGNMENT__okta from the principal, GRANTS_ADMIN_ROLE__okta to the role, SCOPED_TO_RESOURCE__okta to what it covers. No scope edge means the role covers the whole org.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Answer 'who is a super administrator, directly or through a group' and 'what is each admin scoped to'.

## Identity

Natural key: `org_name`, `name`. Okta's assignment id is not knowable at design time, so a design names the assignment (for example 'Okta Admins: Super Administrator'); revisited to (org_name, okta_id) when the collector lands.

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- The capabilities a role implies (reset factors, manage apps) are not derived into edges as BloodHound does; that is a traversal a later view can compute.

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/users/{id}/roles` and `/api/v1/groups/{id}/roles` (okta.roles.read); assignments to service apps by the client role-assignment endpoints.

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21) — `Okta_RoleAssignment`, `Okta_HasRoleAssignment`, `Okta_ScopedTo`.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `name` — The assignment's name: design-authored, or principal and role as the collector composes them.
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `assignment_type` — Okta's assignmentType: to a user directly, to a group, or to a service app (CLIENT).
- `status` — Okta's assignment status.
- `configuration` — The remainder of the object as Okta returns it; nothing identity-bearing lives here.
- `tags` — TAP's tag map.
