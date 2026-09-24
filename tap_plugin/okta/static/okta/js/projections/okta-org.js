/**
 * okta org — one Okta org as a placed picture (req-okta-page-org; the /okta page's graph panel).
 *
 * The org is the outer box. Inside it, one labelled box per family of what the org holds, on a
 * fixed 3x3 cell grid so every org reads the same way:
 *
 *   ┌─ Okta org ───────────────────────────────────────────────┐
 *   │  Federation      Authenticators      Network             │
 *   │  Groups                              Applications        │ ── requests second factor ──▶ ┌ Duo ┐
 *   │  Administration  Policies            (other)             │                               └─────┘
 *   └──────────────────────────────────────────────────────────┘
 *
 * Groups sit left and Applications right, so the assignment edges (group → application) cross the
 * middle as the one flow an operator reads first. Policies sit at the bottom with each policy's rules
 * drawn inside it (EVALUATES_RULE__okta nests them); Authenticators sit at the top, so a rule's
 * REQUIRES_AUTHENTICATOR__okta edge runs up the page.
 *
 * Outside the org: another system's node that an edge from the scene reaches (a node whose type is
 * not okta's). The one the page draws today is the Duo application Okta sends its users to for a
 * second factor (REQUESTS_SECOND_FACTOR__duo, the same relationship /duo draws from its side),
 * inside the Duo account that holds it. Foreign nodes are placed in a column right of the org
 * container they connect to; they never join a family. Naming duo's type strings here is display
 * only: okta declares no dependency on duo, and a scene without them draws no column.
 *
 * Every drawn edge carries its type as a label, humanized ("EVALUATES_RULE__okta" → "evaluates
 * rule"), so the picture says what each line means.
 *
 * Reusable: the module names no entity id and no org. Families are keyed by entity type, each org
 * in the scene gets its own container and boxes (a family box is `okta-family:<org>:<key>`), and an
 * okta node whose type no family names is still drawn, in an "Other" box, and reported as a warning.
 * Membership comes from the scene's own BELONGS_TO_ORG__okta edges; those are hidden, because the
 * org container and family boxes already say which org a node belongs to.
 *
 * Containment is positional (spec-viz-nested-projection.md): the family boxes are synthetic nodes
 * this module adds, joined to their members by synthetic `_OKTA_FAMILY_HOLDS` edges and to their
 * org by synthetic `_OKTA_ORG_HOLDS` edges, which the nesting pass consumes. All are removed and
 * re-added on every entry. The nesting pass sizes every box; the 3x3 placement inside the org is
 * this module's, so after placing the families it re-fits the org container around them.
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
const SYN = {holds: "_OKTA_FAMILY_HOLDS", orgHolds: "_OKTA_ORG_HOLDS"};
const SYN_CLASS = "okta-synthetic";
const FOREIGN_CLASS = "okta-foreign";
const MEMBERSHIP_CLASS = "okta-membership";

//: Containment among foreign nodes, so another system's container reads as a box outside the org
//: (the Duo account holding the application Okta calls). Matched against the scene only: types
//: absent from the scene nest nothing.
const FOREIGN_NESTS = [
    {name: "duo-account-holds", gryphon: "(parent:duo__duo_account)-[:HOLDS_ACCOUNT_OBJECT__duo]->(child:duo__duo_application)"},
];

//: The families, their cell on the 3x3 grid ([column, row]; the centre cell is left open so the
//: group → application assignments cross it) and colours. Exported so a page composing its own
//: picture can reuse the same grouping.
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
    foreignFloor: {width: 200, height: 90},
    centreFloor: {width: 160, height: 90},   // the open centre cell, room for the assignment edges to cross
    cellGapX: 110,
    cellGapY: 80,
    foreignGap: 260,   // org container → foreign column: room for a readable edge label
    foreignRowGap: 40,
    orgGap: 160,
    labelInset: 14,
};

const _familyPadding = (inset) => ({top: 14 + inset, right: 24, bottom: 22, left: 24});
const _policyPadding = (inset) => ({top: 10 + inset, right: 14, bottom: 14, left: 14});
const _orgPadding = (inset) => ({top: 22 + inset, right: 36, bottom: 32, left: 36});

//: "EVALUATES_RULE__okta" → "evaluates rule": drop the owning plugin's suffix, lower-case, spaces.
export function humanizeEdgeType(edgeType) {
    if (!edgeType) return "";
    return String(edgeType).replace(/__[a-z0-9_]+$/, "").replace(/_+/g, " ").trim().toLowerCase();
}

const _isOkta = (type) => typeof type === "string" && type.startsWith("okta__");

//: A drawn edge's type. The graph panel puts it in `label`; synthetic and runtime edges carry
//: `edge_type`. Same fallback as the nesting pass.
const _edgeType = (e) => e.data("edge_type") || e.data("label") || "";

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
    _labelEdges(cy);

    const chrome = applyStandardChrome(cy, {edgeLabels: true});
    const labelInset = parentLabelInset({...chrome, inset: GEOM.labelInset});
    const baseSizes = {[T.family]: GEOM.familyFloor, [T.org]: GEOM.org, [T.rule]: GEOM.rule};
    // Every other type drawn is a leaf card, including a type no family names (drawn in "Other")
    // and another system's node (drawn outside the org).
    cy.nodes().forEach((n) => {
        const t = n.data("entity_type");
        if (t && !baseSizes[t]) baseSizes[t] = GEOM.leaf;
    });
    const foreignContainerTypes = FOREIGN_NESTS.map((r) => /\(parent:([^)]+)\)/.exec(r.gryphon)[1]);
    const paddings = {[T.family]: _familyPadding(labelInset), [T.policy]: _policyPadding(labelInset), [T.org]: _orgPadding(labelInset)};
    foreignContainerTypes.forEach((t) => {
        paddings[t] = _familyPadding(labelInset);
        baseSizes[t] = GEOM.foreignFloor;
    });

    const result = await projectNested(cy, {
        relationships: [
            {name: "org-holds", gryphon: `(parent:${T.org})-[:${SYN.orgHolds}]->(child:${T.family})`},
            {name: "family-holds", gryphon: `(parent:${T.family})-[:${SYN.holds}]->(child)`},
            {name: "policy-rules", gryphon: `(parent:${T.policy})-[:${E.evaluatesRule}]->(child:${T.rule})`},
            ...FOREIGN_NESTS,
        ],
        baseSizes,
        padding: 20,
        paddings,
        innerLayout: {name: "flow", gap: 26, aspect: 1.4},
        innerLayouts: {[T.policy]: {name: "flow", gap: 12, aspect: 0.6, sort: "input"}},
    });
    warnings.push(...(result.warnings || []));

    // One picture per org, side by side (normally there is one), each followed by the foreign
    // nodes it connects to.
    const foreignRoots = _foreignRoots(cy);
    const placedForeign = new Set();
    let x = 0;
    orgs.forEach((org, i) => {
        const families = familiesByOrg.get(org.id()) || new Map();
        const box = families.size > 0 ? _placeInside(cy, org, families, x, labelInset) : _placeLeaf(org, x);
        let right = box.x2;
        const isLast = i === orgs.length - 1;
        const mine = foreignRoots.filter((r) => !placedForeign.has(r.id()) && (isLast || _connects(cy, org, r)));
        if (mine.length > 0) {
            right = _placeForeign(cy, mine, box);
            mine.forEach((r) => placedForeign.add(r.id()));
        }
        x = right + GEOM.orgGap;
    });

    placeParentLabels(cy, {
        anchor: "upper-left", inset: GEOM.labelInset,
        parentFontSize: chrome.parentFontSize, parentFontWeight: chrome.parentFontWeight,
    });
    _style(cy, foreignContainerTypes);
    return {warnings};
}

// ---------------------------------------------------------------------------
// Synthetic families and org containment (removed and re-added on every entry)
// ---------------------------------------------------------------------------

function _clear(cy) {
    cy.remove(cy.elements("." + SYN_CLASS));
    cy.nodes("." + FOREIGN_CLASS).removeClass(FOREIGN_CLASS);
    cy.edges("." + MEMBERSHIP_CLASS).removeClass(MEMBERSHIP_CLASS);
}

function _orgOf(cy, node) {
    const out = node.outgoers("edge").filter((e) => _edgeType(e) === E.belongsToOrg).targets(`[entity_type = "${T.org}"]`);
    return out.nonempty() ? out.first() : null;
}

function _addFamilies(cy, orgs, warn) {
    const byOrg = new Map();
    orgs.forEach((org) => byOrg.set(org.id(), new Map()));
    const singleOrg = orgs.length === 1 ? orgs.first() : null;

    cy.nodes().forEach((n) => {
        const type = n.data("entity_type");
        if (!type || type === T.org || n.hasClass(SYN_CLASS)) return;
        // Runtime helpers (badges, shadows, stack cards) are not entities of any system.
        if (n.data("_is_badge") || n.data("_is_status_badge") || n.data("_is_shadow") || n.data("_is_stack_card") || n.data("_is_stack_chip")) return;
        // Another system's node is drawn outside the org, never in a family.
        if (!_isOkta(type)) {
            n.addClass(FOREIGN_CLASS);
            return;
        }
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
                    icon_url: "",
                },
                classes: `${SYN_CLASS} okta-family okta-family-${family.key}`,
            });
            cy.add({
                group: "edges",
                data: {id: `${SYN.orgHolds}:${id}`, source: org.id(), target: id, edge_type: SYN.orgHolds, label: ""},
                classes: SYN_CLASS,
            });
            families.set(family.key, id);
        }
        cy.add({
            group: "edges",
            data: {id: `${SYN.holds}:${n.id()}`, source: families.get(family.key), target: n.id(), edge_type: SYN.holds, label: ""},
            classes: SYN_CLASS,
        });
    });
    return byOrg;
}

//: Every real edge carries its humanized type as a label (synthetic containment edges are hidden).
function _labelEdges(cy) {
    cy.edges().forEach((e) => {
        if (e.hasClass(SYN_CLASS)) return;
        if (_edgeType(e) === E.belongsToOrg) {
            e.addClass(MEMBERSHIP_CLASS);
            return;
        }
        e.data("_okta_edge_label", humanizeEdgeType(_edgeType(e)));
    });
}

// ---------------------------------------------------------------------------
// Placement: the 3x3 grid inside one org, then the org fitted around it
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

//: An org with nothing in it is a plain card; returns its box.
function _placeLeaf(org, left) {
    const w = org.width();
    const h = org.height();
    org.position({x: left + w / 2, y: 0});
    return {x1: left, x2: left + w, y1: -h / 2, y2: h / 2};
}

//: Place the org's family boxes on the grid, then size and centre the org container around them.
//: Returns the container's box.
function _placeInside(cy, org, families, left, labelInset) {
    const cells = [];
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
    // The open centre keeps a floor so the assignment edges have room to cross it.
    colW[1] = Math.max(colW[1], GEOM.centreFloor.width);
    rowH[1] = Math.max(rowH[1], GEOM.centreFloor.height);
    const pad = _orgPadding(labelInset);
    const innerLeft = left + pad.left;
    const colX = [];
    let x = innerLeft;
    colW.forEach((w, i) => { colX[i] = x; x += w + (w > 0 && i < 2 ? GEOM.cellGapX : 0); });
    const rowY = [];
    let y = 0;
    rowH.forEach((h, i) => { rowY[i] = y; y += h + (h > 0 && i < 2 ? GEOM.cellGapY : 0); });
    cells.forEach(({node, col, row}) => {
        _moveTreeTo(cy, node, colX[col] + colW[col] / 2, rowY[row] + rowH[row] / 2);
    });
    // Fit the container to what it now holds (the nesting pass sized it for its own inner layout).
    const innerW = x - innerLeft;
    const innerH = y;
    const w = innerW + pad.left + pad.right;
    const h = innerH + pad.top + pad.bottom;
    org.style({width: w, height: h});
    const cx = left + w / 2;
    const cy0 = -pad.top + h / 2;
    org.position({x: cx, y: cy0});
    return {x1: left, x2: left + w, y1: -pad.top, y2: -pad.top + h};
}

//: Top-level foreign nodes: another system's node with no container of its own in the scene.
function _foreignRoots(cy) {
    return cy.nodes("." + FOREIGN_CLASS).filter((n) => !n.data("_viewport_parent")).toArray();
}

//: Whether the org (or anything it contains) has an edge to the foreign root or anything inside it.
function _connects(cy, org, root) {
    const inside = new Set([root.id(), ..._childrenOf(cy, root.id()).map((c) => c.id())]);
    return org.connectedEdges().some((e) => inside.has(e.source().id()) || inside.has(e.target().id()))
        || cy.edges().some((e) => {
            const s = e.source();
            const t = e.target();
            return (inside.has(t.id()) && _isOkta(s.data("entity_type")) && _withinOrg(cy, s, org))
                || (inside.has(s.id()) && _isOkta(t.data("entity_type")) && _withinOrg(cy, t, org));
        });
}

function _withinOrg(cy, node, org) {
    let cur = node;
    for (let depth = 0; cur && cur.nonempty() && depth < 8; depth++) {
        if (cur.id() === org.id()) return true;
        const parentId = cur.data("_viewport_parent");
        cur = parentId ? cy.getElementById(parentId) : null;
    }
    return false;
}

//: Stack the foreign roots in a column right of the org container, centred on it. Returns the
//: column's right edge.
function _placeForeign(cy, roots, box) {
    const colW = Math.max(...roots.map((r) => r.width()));
    const totalH = roots.reduce((s, r) => s + r.height(), 0) + GEOM.foreignRowGap * (roots.length - 1);
    const cx = box.x2 + GEOM.foreignGap + colW / 2;
    let y = (box.y1 + box.y2) / 2 - totalH / 2;
    roots.forEach((r) => {
        _moveTreeTo(cy, r, cx, y + r.height() / 2);
        y += r.height() + GEOM.foreignRowGap;
    });
    return box.x2 + GEOM.foreignGap + colW;
}

// ---------------------------------------------------------------------------
// Style
// ---------------------------------------------------------------------------

function _style(cy, foreignContainerTypes) {
    let style = cy.style()
        // Org membership is drawn as the containers, so the spokes are not drawn as lines too.
        .selector("." + MEMBERSHIP_CLASS)
        .style({display: "none"})
        .selector("edge[_okta_edge_label]")
        .style({
            "label": "data(_okta_edge_label)",
            "font-size": "14px",
            "color": "#334155",
            "text-background-color": "#FFFFFF",
            "text-background-opacity": 0.9,
            "text-background-padding": "2px",
            "text-background-shape": "round-rectangle",
            "text-rotation": "none",
        })
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
        .style({"font-weight": "600"})
        .selector(`node[entity_type = "${T.org}"].tap-viewport-parent`)
        .style({
            "shape": "round-rectangle",
            "background-color": "#F7FBFE",
            "background-opacity": 1,
            "border-width": 2.5,
            "border-color": "#007DC1",
            "border-opacity": 1,
            "color": "#0B3A57",
        });
    foreignContainerTypes.forEach((t) => {
        // Another system's container: a dashed box, so it reads as outside this org.
        style = style.selector(`node[entity_type = "${t}"].tap-viewport-parent`).style({
            "shape": "round-rectangle",
            "background-color": "#FFFFFF",
            "background-opacity": 1,
            "border-width": 2,
            "border-style": "dashed",
            "border-color": "#64748B",
            "border-opacity": 1,
            "color": "#1E293B",
        });
    });
    // Leaf cards carry their label inside, like the family members (a container's label is placed
    // by placeParentLabels, which overrides this).
    const leafSelectors = [...FAMILIES.flatMap((f) => f.types), T.rule].map((t) => `node[entity_type = "${t}"]`);
    leafSelectors.push("." + FOREIGN_CLASS);
    style = style.selector(leafSelectors.join(", ")).style({
        "text-valign": "center", "text-halign": "center", "text-margin-y": 0,
        "text-wrap": "ellipsis", "text-max-width": "130px",
    });
    style.update();
}
