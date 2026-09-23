# Okta Org

## Blurb

An Okta org: one okta.com (or okta-gov.com) tenant that holds users, groups, applications and policies.

## Purpose

The tenant every other okta type belongs to (BELONGS_TO_ORG__okta).

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Give every Okta object one tenant to belong to, so a page or a query can be scoped to one org.
- Let a design place an org (for example an Okta for Government High org) before anything is collected.

## Identity

Natural key: `name`. A design-phase org has no observed identifier, so its name is the only fact it carries; revisited to okta_id when the collector makes it observable.

## Boundaries

- The org's brands, custom domains, email templates and org-wide settings are configuration on the org, not nodes.
- Okta's own infrastructure (cells, the okta-gov.com cell a FedRAMP High org lives in) is outside the model; `service_offering` records which offering hosts the org.

## Neutrality

Vendor-specific. The neutral neighbour is `identity_core__organization` (a customer or company), which is a different thing: an Okta org is a tenant of a SaaS product, and one organization may run several.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/org` (org settings) needs a token that can read org settings; the org's id and subdomain come from it.

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- Cartography Okta intel module, `cartography/models/okta/` at commit 030848289203969e19a17bf25e45ff94a527bcef (2026-08-30) — `OktaOrganization` (the tenant, keyed by org id).
- BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21) — `Okta_Organization` and its `Okta_Contains` edge.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `name` — The org's name as the design or the operator knows it. The natural key, and the value every child's `org_name` carries.
- `org_domain` — The org's okta.com, okta-gov.com or custom domain, for example acme.okta-gov.com. Blank until observed.
- `okta_id` — Okta's org id. Blank until observed.
- `service_offering` — Which Okta offering hosts the org: commercial, Okta for Government Moderate, Okta for Government High (FedRAMP High) or Okta for DoD IL4. A design can know it; blank means not stated, never commercial.
- `configuration` — The remainder of the org settings.
- `tags` — TAP's tag map.
