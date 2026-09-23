# Serves Issuer

## Blurb

An Okta authorization server is the running service behind an OIDC issuer: it publishes the issuer's discovery document and keys and mints its tokens. The issuer is identity_core's neutral node, so a relying service's TRUSTS_ISSUER edge and this one meet on it. The issuer URL lives on that node, not on the authorization server.

## Purpose

Meet relying services' TRUSTS_ISSUER edges on the neutral issuer node.

## Goals

- Meet relying services' TRUSTS_ISSUER edges on the neutral issuer node.

## Identity

Edges carry no natural key and their ids are assigned (`req-grid-entity-natural-key`); at most one edge of this type is expected between one pair.

## Boundaries

- Only the relationship named in the Blurb; anything the far node is, it is by its own type.
- Edge endpoint lists are declarations: core's permission union lets an unconstrained node emit any edge, so the list is what readers and validators rely on.

## Neutrality

Vendor-specific source; the far end is a substrate or another plugin's node, which is why it is not named here.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- The github_core `HOSTS_REPOSITORY` pattern: a vendor record linked to the neutral thing it runs. Sources: Cartography Okta intel module, `cartography/models/okta/` at commit 030848289203969e19a17bf25e45ff94a527bcef (2026-08-30); BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21).

## Endpoints

- sources: `okta__okta_authorization_server`
- targets: `identity_core__oidc_issuer`
- dimensions stamped: none (the edge's dcom value belongs to whatever writes it)
- no properties
