# Okta Group Rule

## Blurb

A group rule in an Okta org: an Okta Expression Language condition that places matching users into groups automatically.

## Purpose

A group rule: membership by expression. The groups it assigns are ASSIGNS_GROUP_MEMBERSHIP__okta edges.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Explain a membership nobody added by hand: the rule that put a user in a privileged group.

## Identity

Natural key: `org_name`, `name`. Rule names are unique within an org; revisited to (org_name, okta_id).

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- The expression is kept verbatim; TAP does not evaluate Okta Expression Language.

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/groups/rules` (okta.groups.read).

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- Cartography Okta intel module, `cartography/models/okta/` at commit 030848289203969e19a17bf25e45ff94a527bcef (2026-08-30) — `OktaGroupRule`.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `name` — The rule's name.
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `status` — Okta's rule status. INVALID means the rule references something that no longer exists.
- `expression` — conditions.expression.value: the Okta Expression Language condition.
- `configuration` — The remainder of the object as Okta returns it; nothing identity-bearing lives here.
- `tags` — TAP's tag map.
