# Okta Log Stream

## Blurb

A log stream in an Okta org: the System Log delivered continuously to AWS EventBridge or Splunk Cloud.

## Purpose

Where the System Log goes. The destination node, when one exists, is reached by the open-ended WRITES_LOGS__okta edge.

It exists so the /okta page and any query over an Okta org can reach it by type, scoped to one org by `BELONGS_TO_ORG`.

## Goals

- Answer 'does the System Log leave Okta, and to where' for audit-logging requirements.

## Identity

Natural key: `org_name`, `name`. Names are unique within an org; revisited to (org_name, okta_id).

`org_name` is in every child key because names are unique only within an org: two orgs each hold an Everyone group.

## Boundaries

- System Log events themselves are not nodes; they are what a collector reads.

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No call has been executed against an Okta org for this plugin; there is no collector yet (`req-okta-collector`, Backlog). What follows is what the Okta documentation and OpenAPI description say a caller needs, and it must be rewritten from an executed call, naming the credential that made it, when the collector lands.

Documented path: `GET /api/v1/logStreams` (okta.logStreams.read).

## Authoritative Source

- **Source:** Okta Management API, OpenAPI description published in okta/okta-management-openapi-spec
- **Version:** dist/2026.08.4 at commit 74fcd17fad54332caee96ebbb11fd7f203b03e4f (spec `info.version` 2026.08.4)
- **Retrieved:** 2026-09-22 (enums checked against the downloaded spec; no call executed against an Okta org)

## Prior Art

- Okta Terraform provider (okta/okta) resource list, from the author's knowledge; not re-read in this pass — okta_log_stream.
- `specs/okta-corpus.md` (2026-09-22) — the corpus decision this type comes from.

## Fields

- `org_name` — The name of the Okta org this object lives in: the okta__okta_org's natural key. A scoping column, not a copy of the org: the org's own facts live on the org, and the BELONGS_TO_ORG__okta edge is what a traversal follows. It is here because two orgs each hold an 'Everyone' group, and the key must tell them apart (the fact the key rests on is a column).
- `name` — The log stream's name.
- `okta_id` — Okta's own object id (for example 00u1a2b3c4). Blank until observed: a design node has none.
- `stream_type` — Okta's log stream type.
- `status` — Okta's status.
- `destination` — Where the stream lands, in the destination's own words: an EventBridge event source (account, region, source name) or a Splunk host.
- `configuration` — The remainder of the object as Okta returns it; nothing identity-bearing lives here.
- `tags` — TAP's tag map.
