# Requires Authenticator

## Blurb

A policy rule requires, or accepts, an authenticator to satisfy its verification. The properties carry the constraint that makes the difference between 'MFA' and 'phishing-resistant MFA'.

## Purpose

Say which authenticators satisfy a rule, and whether phishing resistance is demanded.

## Goals

- Say which authenticators satisfy a rule, and whether phishing resistance is demanded.

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

- No surveyed graph carries it; it is where 'requires Duo' is written. Sources: Cartography Okta intel module, `cartography/models/okta/` at commit 030848289203969e19a17bf25e45ff94a527bcef (2026-08-30); BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21).

## Endpoints

- sources: `okta__okta_policy_rule`
- targets: `okta__okta_authenticator`
- dimensions stamped: none (the edge's dcom value belongs to whatever writes it)
- property `constraint` — Which factor class the authenticator satisfies in this rule.
- property `phishing_resistant` — The rule demands a phishing-resistant method of this class.
- property `hardware_protected` — The rule demands a hardware-protected key (device-bound).
