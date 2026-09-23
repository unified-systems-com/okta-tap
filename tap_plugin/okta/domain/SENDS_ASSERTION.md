# Sends Assertion

## Blurb

An Okta application sends a SAML assertion or an OIDC ID token to a relying service, which signs the user in on the strength of it. The target is OPEN (omitted): the relying service's own node belongs to its own plugin (a Teleport cluster, a GitLab instance, an AWS account's IAM Identity Center), and naming those types here would make every new relying service an edit to this plugin. The relying service's trust in the Okta issuer is its own plugin's edge (TRUSTS_ISSUER__identity_core).

## Purpose

Link an Okta application to the relying service it signs users in to, without depending on that service's plugin.

## Goals

- Link an Okta application to the relying service it signs users in to, without depending on that service's plugin.

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

- BloodHound `Okta_OutboundSSO` / `Okta_OutboundOrgSSO`, which name Okta's own kinds at the far end; here the far end is open. Sources: Cartography Okta intel module, `cartography/models/okta/` at commit 030848289203969e19a17bf25e45ff94a527bcef (2026-08-30); BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21).

## Endpoints

- sources: `okta__okta_application`
- targets: open (omitted): see the description
- dimensions stamped: none (the edge's dcom value belongs to whatever writes it)
- property `protocol` — How the application signs the user in to the relying service.
- property `endpoint` — Where the assertion is sent: the SAML ACS URL or the OIDC redirect URI.
