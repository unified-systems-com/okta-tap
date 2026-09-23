# Includes Resource

## Blurb

A resource set includes an Okta object. Okta also admits 'all users' or 'all groups' style members; those are not an edge to every object, and v0 does not store them.

## Purpose

List a resource set's members.

## Goals

- List a resource set's members.

## Identity

Edges carry no natural key and their ids are assigned (`req-grid-entity-natural-key`); at most one edge of this type is expected between one pair.

## Boundaries

- Only the relationship named in the Blurb; anything the far node is, it is by its own type.
- Edge endpoint lists are declarations: core's permission union lets an unconstrained node emit any edge, so the list is what readers and validators rely on.

## Neutrality

Vendor-specific: both ends are Okta objects.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- BloodHound `Okta_ResourceSetContains`. Sources: Cartography Okta intel module, `cartography/models/okta/` at commit 030848289203969e19a17bf25e45ff94a527bcef (2026-08-30); BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21).

## Endpoints

- sources: `okta__okta_resource_set`
- targets: `okta__okta_user`, `okta__okta_group`, `okta__okta_application`, `okta__okta_authorization_server`, `okta__okta_identity_provider`, `okta__okta_policy`, `okta__okta_admin_role`, `okta__okta_device`
- dimensions stamped: none (the edge's dcom value belongs to whatever writes it)
- no properties
