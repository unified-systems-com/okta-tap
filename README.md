# okta-tap

Okta workforce identity as grid vocabulary: v0 carries one outer node, the Okta org (the okta.com tenant), so a design can place it before anything is collected.

## What this plugin owns

One type in v0: `okta__okta_org` — an Okta org: one okta.com tenant (for example acme.okta.com) that holds users, groups, applications and policies. A design can place it before any access exists; everything inside it is later vocabulary.

## Read first

`specs/spec-okta-v0.md` — this is a thin v0 that puts the piece on the board; the full spec interview runs when the plugin grows.

## Stand it up

From a TAP core checkout:

```bash
scripts/spawn-session.sh <label> cli --from 'git+https://github.com/unified-systems-com/okta-tap@<rev>#ci' --dev-plugins okta
```
