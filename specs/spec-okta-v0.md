# TAP Okta Plugin Specification

**Okta workforce identity as grid vocabulary: v0 carries one outer node, the Okta org (the okta.com tenant), so a design can place it before anything is collected.**

## Plugin Identity

| Field | Value |
| --- | --- |
| Slug | `okta` |
| Display name | TAP Okta |
| Description | Okta workforce identity as grid vocabulary: v0 carries one outer node, the Okta org (the okta.com tenant), so a design can place it before anything is collected. |
| Kind | Leaf plugin: Okta vocabulary. Consumes nothing in v0; consumed by instance plugins that place it in a design (highbar first). |

**Default dimensions**

| Dimension | Value | Why |
| --- | --- | --- |
| (none) | | `okta__okta_org` declares no default dimension in v0. The only candidate is the `dcom` axis, and its value is a property of the observation, not the type: a seeded design node is `design`, the same type observed by a future collector is `configuration`. The seeding bundle stamps it per node. |

## Philosophy

This is a thin v0 (ruled 2026-09-22 for the highbar starter set): it exists to put the piece on the board so a design can reference it, not to model the domain. The full `create-plugin-spec` interview, prior-art search and requirement buy-in run when this plugin grows past v0; nothing here pre-empts them.

The one type, `okta__okta_org`, is the outermost thing a reader of a diagram recognises for Okta. Everything inside it (users, groups, policies, projects, sessions) is later vocabulary, added when something observes or designs it.

Three states hold for every observed field: blank means *not observed*, never *empty*. A design-phase node carries only its name; its identifiers stay blank until a collector reads them.

**Provenance markers:** every node of this type seeded in v0 is *designed* (stamped `dcom: design` by the bundle that seeds it). No field is *observed* until the collector (`req-okta-collector`, Backlog) exists.

## Goals

| # | Name | Description |
| --- | --- | --- |
| 1 | On The Board | Exist as an installable plugin so the highbar stack can boot with it. |
| 2 | Designable | Let a design place the Okta outer node before any access exists. |

## Requirements

| RID | Name | Status | Notes |
| --- | --- | --- | --- |
| req-okta-model | [Okta Org Model](#okta-org-model) | Implemented | The one outer node: its fields, natural key, icon and display |
| req-okta-record | [CI Record and Tests](#ci-record-and-tests) | Implemented | The in-package `ci` boot record and the manifest/behaviour tests |
| req-okta-collector | [Collector](#collector) | Backlog | Observe real Okta state onto the grid; deferred until access exists |

---

### Okta Org Model
----
RID: `req-okta-model`

Status: `Implemented`

An Okta org: one okta.com tenant (for example acme.okta.com) that holds users, groups, applications and policies.

#### Implementation

`tap_plugin/okta/models/okta_org.py` defines `OktaOrg(BaseModel)` with `ENTITY_TYPE = "okta__okta_org"`, `ENTITY_ICON = "okta-org"` (SVG at `static/okta/icons/okta-org.svg`), no default dimensions, and fields `name` (required), `org_domain` (The org's okta.com (or custom) domain, for example acme.okta.com. Blank until observed.), `configuration` (object) and `tags` (object). `NATURAL_KEY = ("name",)`: a design-phase node has no observed identifier, so its name is the only fact it carries; the key is revisited when `req-okta-collector` makes `org_domain` observable.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-okta-model-1 | Created Through The Service Layer | Implemented | A `create_node` write with only `name` succeeds and the row carries it. | |
| req-okta-model-2 | Name Required | Implemented | A `create_node` write without `name` is refused. | |
| req-okta-model-3 | Keyed By Name | Implemented | `NATURAL_KEY` is `("name",)` and every key field is a model field. | |

---

### CI Record and Tests
----
RID: `req-okta-record`

Status: `Implemented`

The in-package `ci` boot record (`req-boot-bootstrap-ci-record`) and the tests that run in it.

#### Implementation

`tap_plugin/okta/boot/ci.boot.json` installs this plugin alone (it declares no dependencies), offline and credential-free; the consumer flips self to editable. `tap_plugin/okta/tests/test_okta_manifest.py` runs `validate_plugin` at structure and strict levels; `tests/test_okta_org.py` covers `req-okta-model`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-okta-record-1 | Record Declared | Implemented | The manifest declares the `ci` record with its sha256. | |
| req-okta-record-2 | Validates Strict | Implemented | `validate_plugin --strict` passes on the package. | |

---

### Collector
----
RID: `req-okta-collector`

Status: `Backlog`

Observe real Okta state onto the grid; deferred until access exists.

## Model catalog

| Model | Entity type | Category | Rationale |
| --- | --- | --- | --- |
| `OktaOrg` | `okta__okta_org` | Outer node | The one node a reader recognises as Okta; everything else nests inside it later. |

## Icons

`okta-org` is Okta's own mark, used nominatively to identify the vendor on diagrams. The mark remains its owner's trademark; it is not covered by this repository's licence.
