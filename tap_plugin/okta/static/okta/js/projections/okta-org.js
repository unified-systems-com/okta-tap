/**
 * okta org — one Okta org as a placed picture (req-okta-page-org; the /okta page's graph panel).
 *
 * The org sits at the centre. Around it, one labelled box per family of what the org holds,
 * on a fixed 3x3 cell grid so every org reads the same way:
 *
 *        Federation      Authenticators      Network
 *        Groups          [ Okta org ]        Applications
 *        Administration  Policies            (other)
 *
 * Groups sit left of the org and Applications right of it, so the assignment edges
 * (group → application) cross the centre as the one flow an operator reads first. Policies
 * sit under the org with each policy's rules drawn inside it (EVALUATES_RULE__okta nests them);
 * Authenticators sit above, so a rule's REQUIRES_AUTHENTICATOR__okta edge runs up the page.
 *
 * Reusable: the module names no entity id and no org. Families are keyed by entity type,
 * each org in the scene gets its own boxes (a family box is `okta-family:<org>:<key>`), and a
 * node whose type no family names is still drawn, in an "Other" box, and reported as a warning.
 * Membership comes from the scene's own BELONGS_TO_ORG__okta edges; those are hidden, because
 * the family boxes already say which org a node belongs to.
 *
 * Containment is positional (spec-viz-nested-projection.md): the family boxes are synthetic
 * nodes this module adds, joined to their members by synthetic `_OKTA_FAMILY_HOLDS` edges that
 * the nesting pass consumes. Both are removed and re-added on every entry.
 *
 * Standard tap layout module: `export async function execute(context)`
 * (spec-viz-layouts.md, req-viz-layout-module-contract).
 */

import {projectNested} from "/static/tap_viz/js/runtime/nested-projection.js";
import {applyStandardChrome, placeParentLabels, parentLabelInset} from "/static/tap_viz/js/runtime/chrome.js";

const P = "okta__okta_";
const T = {
    org: `${P}org`,
    family: "okta_layout__family",
    policy: `${P}policy`,
    rule: `${P}policy_rule`,
};

const E = {
    belongsToOrg: "BELONGS_TO_ORG__okta",
    evaluatesRule: "EVALUATES_RULE__okta",
};
const SYN = {holds: "_OKTA_FAMILY_HOLDS"};
const SYN_CLASS = "okta-synthetic";

//: The families, their cell on the 3x3 grid ([column, row]; the org is [1, 1]) and colours.
//: Exported so a page composing its own picture can reuse the same grouping.
export const FAMILIES = [
    {key: "federation", label: "Federation", cell: [0, 0], types: [`${P}identity_provider`, `${P}authorization_server`], border: "#3F51B5", fill: "#F5F7FF"},
    {key: "authenticators", label: "Authenticators", cell: [1, 0], types: [`${P}authenticator`], border: "#00796B", fill: "#F0FAF8"},
    {key: "network", label: "Network", cell: [2, 0], types: [`${P}network_zone`, `${P}trusted_origin`, `${P}log_stream`], border: "#475569", fill: "#F8FAFC"},
    {key: "groups", label: "Groups", cell: [0, 1], types: [`${P}group`, `${P}group_rule`], border: "#007DC1", fill: "#F2F9FD"},
    {key: "applications", label: "Applications", cell: [2, 1], types: [`${P}application`], border: "#3F51B5", fill: "#F5F7FF"},
    {key: "administration", label: "Administration", cell: [0, 2], types: [`${P}admin_role`, `${P}role_assignment`, `${P}resource_set`, `${P}api_token`], border: "#B3261E", fill: "#FEF6F5"},
    {key: "policies", label: "Policies", cell: [1, 2], types: [T.policy], border: "#B26A00", fill: "#FFFBF0"},
    {key: "other", label: "Other", cell: [2, 2], types: [], border: "#94A3B8", fill: "#FFFFFF"},
];
const FAMILY_BY_TYPE = Object.fromEntries(FAMILIES.flatMap((f) => f.types.map((t) => [t, f])));
const OTHER = FAMILIES.find((f) => f.key === "other");

const GEOM = {
    leaf: {width: 150, height: 54},
    rule: {width: 150, height: 44},
    org: {width: 190, height: 70},
    familyFloor: {width: 200, height: 110},
    cellGapX: 90,
    cellGapY: 70,
    orgGap: 160,
    labelInset: 14,
};

const _familyPadding = (inset) => ({top: 14 + inset, right: 24, bottom: 22, left: 24});
const _policyPadding = (inset) => ({top: 10 + inset, right: 14, bottom: 14, left: 14});

export async function execute(context) {
    const {cy} = context;
    const warnings = [];
    const warn = (category, message) => {
        warnings.push({category, message});
        console.warn(`[okta org] ${category}: ${message}`);
    };

    _clear(cy);
    const orgs = cy.nodes(`[entity_type = "${T.org}"]`);
    if (orgs.empty()) {
        warn("okta_no_org", "no okta__okta_org is in the scene; the picture is left as the runtime placed it");
        return {warnings};
    }
    const familiesByOrg = _addFamilies(cy, orgs, warn);

    const chrome = applyStandardChrome(cy);
    const labelInset = parentLabelInset({...chrome, inset: GEOM.labelInset});
    const baseSizes = {[T.family]: GEOM.familyFloor, [T.org]: GEOM.org, [T.rule]: GEOM.rule};
    // Every other type drawn is a leaf card, including a type no family names (drawn in "Other").
    cy.nodes().forEach((n) => {
        const t = n.data("entity_type");
        if (t && !baseSizes[t]) baseSizes[t] = GEOM.leaf;
    });

    const result = await projectNested(cy, {
        relationships: [
            {name: "family-holds", gryphon: `(parent:${T.family})-[:${SYN.holds}]->(child)`},
            {name: "policy-rules", gryphon: `(parent:${T.policy})-[:${E.evaluatesRule}]->(child:${T.rule})`},
        ],
        baseSizes,
        padding: 20,
        paddings: {[T.family]: _familyPadding(labelInset), [T.policy]: _policyPadding(labelInset)},
        innerLayout: {name: "flow", gap: 26, aspect: 1.4},
        innerLayouts: {[T.policy]: {name: "flow", gap: 12, aspect: 0.6, sort: "input"}},
    });
    warnings.push(...(result.warnings || []));

    // One picture per org, side by side (normally there is one).
    let x = 0;
    orgs.forEach((org) => {
        const width = _placeAround(cy, org, familiesByOrg.get(org.id()) || new Map(), x);
        x += width + GEOM.orgGap * 2;
    });

    placeParentLabels(cy, {
        anchor: "upper-left", inset: GEOM.labelInset,
        parentFontSize: chrome.parentFontSize, parentFontWeight: chrome.parentFontWeight,
    });
    _style(cy);
    return {warnings};
}

// ---------------------------------------------------------------------------
// Synthetic families (removed and re-added on every entry)
// ---------------------------------------------------------------------------

function _clear(cy) {
    cy.remove(cy.elements("." + SYN_CLASS));
}

function _orgOf(cy, node) {
    const out = node.outgoers(`edge[edge_type = "${E.belongsToOrg}"]`).targets(`[entity_type = "${T.org}"]`);
    return out.nonempty() ? out.first() : null;
}

function _addFamilies(cy, orgs, warn) {
    const byOrg = new Map();
    orgs.forEach((org) => byOrg.set(org.id(), new Map()));
    const singleOrg = orgs.length === 1 ? orgs.first() : null;

    cy.nodes().forEach((n) => {
        const type = n.data("entity_type");
        if (!type || type === T.org || n.data("_is_badge") || n.hasClass(SYN_CLASS)) return;
        // A rule is drawn inside its policy; it joins no family of its own.
        if (type === T.rule) return;
        let org = _orgOf(cy, n);
        if (!org && singleOrg) org = singleOrg;
        if (!org) {
            warn("okta_no_membership", `${n.data("label")} (${type}) belongs to no org in the scene; left where the runtime placed it`);
            return;
        }
        let family = FAMILY_BY_TYPE[type];
        if (!family) {
            family = OTHER;
            warn("okta_unmapped_type", `${n.data("label")} (${type}) has no family in the org picture; drawn in "Other"`);
        }
        const families = byOrg.get(org.id());
        if (!families.has(family.key)) {
            const id = `okta-family:${org.id()}:${family.key}`;
            cy.add({
                group: "nodes",
                data: {
                    id, entity_type: T.family, label: family.label, shape: "round-rectangle",
                    fill_color: family.fill, border_color: family.border, label_color: "#1E293B", _okta_family: family.key,
                },
                classes: `${SYN_CLASS} okta-family okta-family-${family.key}`,
            });
            families.set(family.key, id);
        }
        cy.add({
            group: "edges",
            data: {id: `${SYN.holds}:${n.id()}`, source: families.get(family.key), target: n.id(), edge_type: SYN.holds},
            classes: SYN_CLASS,
        });
    });
    return byOrg;
}

// ---------------------------------------------------------------------------
// Placement: the 3x3 grid around one org
// ---------------------------------------------------------------------------

function _childrenOf(cy, parentId) {
    return cy.nodes().filter((n) => n.data("_viewport_parent") === parentId);
}

function _moveTree(cy, node, dx, dy) {
    if (!dx && !dy) return;
    const p = node.position();
    node.position({x: p.x + dx, y: p.y + dy});
    _childrenOf(cy, node.id()).forEach((c) => _moveTree(cy, c, dx, dy));
}

function _moveTreeTo(cy, node, x, y) {
    const p = node.position();
    _moveTree(cy, node, x - p.x, y - p.y);
}

//: Place one org and its family boxes on the grid, the grid's left edge at `left`. Returns the width used.
function _placeAround(cy, org, families, left) {
    const cells = [{node: org, col: 1, row: 1}];
    for (const f of FAMILIES) {
        const id = families.get(f.key);
        if (!id) continue;
        const node = cy.getElementById(id);
        if (node.nonempty()) cells.push({node, col: f.cell[0], row: f.cell[1]});
    }
    const colW = [0, 0, 0];
    const rowH = [0, 0, 0];
    cells.forEach(({node, col, row}) => {
        colW[col] = Math.max(colW[col], node.width());
        rowH[row] = Math.max(rowH[row], node.height());
    });
    // The centre column and row keep a floor so the org never touches its neighbours.
    colW[1] = Math.max(colW[1], GEOM.org.width + GEOM.cellGapX);
    rowH[1] = Math.max(rowH[1], GEOM.org.height + GEOM.cellGapY);
    const colX = [];
    let x = left;
    colW.forEach((w, i) => { colX[i] = x; x += w + (w > 0 ? GEOM.cellGapX : 0); });
    const rowY = [];
    let y = 0;
    rowH.forEach((h, i) => { rowY[i] = y; y += h + (h > 0 ? GEOM.cellGapY : 0); });
    cells.forEach(({node, col, row}) => {
        _moveTreeTo(cy, node, colX[col] + colW[col] / 2, rowY[row] + rowH[row] / 2);
    });
    return x - left;
}

// ---------------------------------------------------------------------------
// Style
// ---------------------------------------------------------------------------

function _style(cy) {
    let style = cy.style()
        // Org membership is drawn as the family boxes, so the spokes are not drawn as lines too.
        .selector(`edge[edge_type = "${E.belongsToOrg}"]`)
        .style({display: "none"})
        .selector(".okta-family")
        .style({
            "shape": "round-rectangle",
            "background-color": "data(fill_color)",
            "background-opacity": 1,
            "border-width": 1.5,
            "border-color": "data(border_color)",
            "color": "#1E293B",
        })
        .selector(`node[entity_type = "${T.org}"]`)
        .style({"font-weight": "600"});
    FAMILIES.forEach((f) => {
        f.types.forEach((t) => {
            style = style.selector(`node[entity_type = "${t}"]`).style({
                "text-valign": "center", "text-halign": "center", "text-margin-y": 0,
                "text-wrap": "ellipsis", "text-max-width": "130px",
            });
        });
    });
    style.update();
}
