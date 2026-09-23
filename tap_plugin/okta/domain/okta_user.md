# Okta User

## Blurb

A user account in an Okta org: one login, its lifecycle status and when it last signed in.

## Purpose

A person's (or a service identity's) account in one Okta org. The account, not the person: the same human holds one account per org, and the link to a neutral person node is the open-ended IDENTIFIES_PERSON__okta edge.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Answer 'who can sign in to what' by joining users to their groups and application assignments.
- Show stale and non-active accounts (status, last sign-in) on the org page.

## Identity

Natural key: `org_name`, `login`. login is unique within an org and is what a design names; the key is revisited to (org_name, okta_id) when the collector makes okta_id observable, since a login can be renamed.

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- The person behind the account is not modelled here: IDENTIFIES_PERSON points at a neutral person node when one exists.
- Profile attributes beyond login, email and display name stay in `configuration`.
- The user type is a field (`user_type`); Cartography models it as a node, but nothing but the user points at it.

## Neutrality

Vendor-specific: an Okta user account. The neutral person or principal it identifies belongs in a substrate (identity_core has no person type yet; computing_core__user exists but is keyed on a display name alone).

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/users` (okta.users.read). The API's `lastLogin` is null for a user who never signed in, which is indistinguishable from an unread field unless the collector records which.

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- Cartography Okta intel module, `cartography/models/okta/` at commit 030848289203969e19a17bf25e45ff94a527bcef (2026-08-30) — `OktaUser`, `MEMBER_OF` to `OktaGroup`, `FACTOR` to `OktaUserFactor`.
- BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21) — `Okta_User`, `Okta_MemberOf`, `Okta_ManagerOf`.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `login` — The Okta login (profile.login), usually an email address. Unique within an org.
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `email` — profile.email. Often equal to login, not always.
- `display_name` — profile.displayName, or first and last name as Okta reports them.
- `status` — Okta's lifecycle status. Blank means not observed, never 'active'.
- `user_type` — The Okta user type's name (default 'user'). A field, not a node: nothing but the user points at it.
- `created_at` — When Okta created the account.
- `activated_at` — When the account was activated.
- `last_login_at` — Okta's lastLogin. Null means not observed OR never signed in; the collector records which in configuration.
- `password_changed_at` — Okta's passwordChanged.
- `status_changed_at` — Okta's statusChanged: when the account entered its current status.
- `configuration` — The remainder of the object as Okta returns it; nothing identity-bearing lives here.
- `tags` — TAP's tag map.
