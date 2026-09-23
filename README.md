# okta-tap

Okta workforce identity as grid vocabulary: the org and the objects a FedRAMP operator answers for in it (users, groups, applications, authorization servers, identity providers, authenticators, policies, network zones, admin roles, API tokens, devices, log streams), with an org page.

## What this plugin owns

- Eighteen node types (`okta__okta_org` and the seventeen things inside an org) and twenty-four edges. Each has a domain article under `tap_plugin/okta/domain/`.
- The `/okta` page: the org as a picture (applications, groups, policies with their rules, authenticators, federation, administration), then fifteen tables. `?org=<org name>` picks the org (exact match); absent, every org on the grid is shown.
- The reusable layout module `static/okta/js/projections/okta-org.js`.

It depends on identity_core for one type: an Okta authorization server `SERVES_ISSUER__okta` the neutral `identity_core__oidc_issuer`. The services Okta signs users in to (Teleport, GitLab) and Duo are reached by edges whose target is left open; this plugin does not depend on their plugins.

## Read first

`specs/spec-okta-v0.md` (the requirements) and `specs/okta-corpus.md` (why these types and not others: sources, rejected candidates, gaps).

## Stand it up

From a TAP core checkout:

```bash
scripts/spawn-session.sh <label> cli --from 'git+https://github.com/unified-systems-com/okta-tap@<rev>#ci' --dev-plugins okta
```
