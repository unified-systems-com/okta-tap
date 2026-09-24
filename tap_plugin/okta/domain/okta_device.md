# Okta Device

## Blurb

A device registered in an Okta org through Okta Verify: its platform, status and whether it is managed.

## Purpose

A device Okta knows through Okta Verify registration. Devices are only ever observed, never designed, so the key is Okta's id.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Tie Okta Verify registrations to users, for device-bound (FastPass) authentication.

## Identity

Natural key: `org_name`, `okta_id`. Only a collector creates devices, and it always has the id.

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- No free-form `configuration` field: the records Okta keeps for this object can carry secret material or personal data (a client secret, a signing key, a user's profile), so only promoted columns are stored.
- Device assurance policies and posture signals are Backlog (`req-okta-backlog-device-assurance`); the neutral device (computing_core) is not linked in v1.

## Neutrality

Vendor-specific record of what is really a neutral endpoint; the link to a neutral device type is a later edge.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/devices` (okta.devices.read).

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- BloodHound OpenGraph Okta extension schema (bloodhound.specterops.io/opengraph/extensions/okta/schema, read 2026-09-22); collector SpecterOps/OktaHound release 2.8.2 (2026-04-21) — `Okta_Device`, `Okta_DeviceOf`.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `okta_id` — Okta's device id. Required: a device is only ever observed.
- `display_name` — profile.displayName.
- `platform` — profile.platform.
- `os_version` — profile.osVersion.
- `status` — Okta's device status.
- `managed` — Whether a device-management integration reports the device managed. Null means not observed.
- `secure_hardware_present` — profile.secureHardwarePresent (TPM / Secure Enclave). Null means not observed.
