#!/usr/bin/env python3
"""Reproduce the figures and headline numbers of the cryoanalgesia scoping-review
evidence map.

Inputs (under data/):
    reclassification.csv  per-item evidence charting (48 items, 19 columns)
    prisma_counts.json    verified PRISMA-ScR flow counts

Outputs (under output/):
    fig1_prisma_flow.png      PRISMA-ScR flow diagram
    fig2_evidence_map.png     domain x modality evidence-tier map
    domain_tier_table.csv     Table: evidence-tier counts per domain
    summary.json              headline numbers derived from the input data
"""

import csv
import json
import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "output")
os.makedirs(OUT, exist_ok=True)

DOMAINS = ["dental", "vascular access", "thoracic", "orthopedic", "dermatology/office"]
DOMAIN_LABELS = {
    "dental": "Dental / oral",
    "vascular access": "Vascular access",
    "thoracic": "Thoracic / chest wall",
    "orthopedic": "Orthopedic",
    "dermatology/office": "Derm / office",
}
MODALITY_GROUPS = {
    "surface": [
        "ice", "ice application", "ice packs", "cryogel/ice", "precooling",
        "cryotherapy", "cryotherapy adjunct", "vapocoolant spray", "vapocoolants",
        "vapocoolant spray before LA infiltration", "ethyl chloride spray",
        "ethyl chloride spray via cotton pellet",
        "ethyl chloride spray (technique comparison)",
        "distant cold stimulation", "intrapulpal cryoanesthesia (cooled LA solution)",
    ],
    "percutaneous": [
        "cryoanalgesia", "cryoneurolysis", "intercostal cryoneurolysis",
        "intercostal cryoanalgesia", "intercostal nerve cryoablation",
        "intercostal nerve cryoablation (timing)", "intrathoracic cryoablation",
        "intraoperative intercostal cryoanalgesia", "preoperative cryoneurolysis",
        "percutaneous intercostal cryoanalgesia (timing)",
        "bedside percutaneous cryoneurolysis",
        "US-guided percutaneous cryoneurolysis",
        "US-guided percutaneous intercostal cryoneurolysis",
        "cryoneurolysis of genicular nerves",
    ],
    "adjunct": [
        "cryoanalgesia + opioids", "intercostal nerve block + cryoneurolysis",
    ],
}
MODALITY_LABELS = {
    "surface": "Superficial cooling",
    "percutaneous": "Percutaneous cryoneurolysis",
    "adjunct": "Adjunct / combined",
}


def tier_letter(t):
    """Normalize an evidence-tier cell to A / B / C / protocol."""
    t = t.strip()
    if "planned" in t.lower():
        return "protocol"
    return t[0]


def modality_group(m):
    m = m.strip()
    for g, keys in MODALITY_GROUPS.items():
        if m in keys:
            return g
    raise ValueError(f"unmapped modality: {m!r}")


def load():
    with open(os.path.join(DATA, "reclassification.csv"), newline="") as f:
        rows = list(csv.DictReader(f))
    with open(os.path.join(DATA, "prisma_counts.json")) as f:
        prisma = json.load(f)
    return rows, prisma


def summarize(rows):
    per = {d: Counter() for d in DOMAINS}
    for r in rows:
        d = r["domain"].replace("orthopedic/hand", "orthopedic")
        per[d][tier_letter(r["evidence tier"])] += 1
    total = sum(sum(c.values()) for c in per.values())
    return {
        "total_items": total,
        "per_domain": {d: dict(per[d]) for d in DOMAINS},
        "tier_totals": dict(
            Counter(
                t for d in DOMAINS for t, n in per[d].items() for _ in range(n)
            )
        ),
    }


def fig1(prisma):
    steps = prisma["flow"]
    fig, ax = plt.subplots(figsize=(8, 9))
    ax.axis("off")
    ys = [0.85, 0.50, 0.15]
    labels = [
        f"Records screened after deduplication (n = {steps['deduplicated']})",
        f"Full-text articles assessed (n = {steps['fulltext']})",
        f"Evidence items included (n = {steps['included']})",
    ]
    side = [
        f"Excluded at title/abstract (n = {steps['deduplicated'] - steps['fulltext']})",
        f"Excluded at full text (n = {steps['fulltext'] - steps['included']})",
    ]
    for i, (y, lab) in enumerate(zip(ys, labels)):
        ax.add_patch(FancyBboxPatch((0.12, y - 0.09), 0.52, 0.12,
                                    boxstyle="round,pad=0.01",
                                    facecolor="#dce8f5", edgecolor="#33547a"))
        ax.text(0.38, y - 0.03, lab, ha="center", va="center", fontsize=11)
        if i < 2:
            ax.annotate("", xy=(0.38, ys[i + 1] + 0.035), xytext=(0.38, y - 0.09),
                        arrowprops=dict(arrowstyle="->", lw=1.5))
            ax.add_patch(FancyBboxPatch((0.70, y - 0.155), 0.27, 0.10,
                                        boxstyle="round,pad=0.01",
                                        facecolor="#f7f7f7", edgecolor="#999999"))
            ax.text(0.835, y - 0.105, side[i], ha="center", va="center", fontsize=9)
    ax.text(0.38, 0.03,
            f"Base search {steps['base']} + update search {steps['update']} = {steps['included']} items",
            ha="center", fontsize=9, color="#555555")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("PRISMA-ScR flow diagram", fontsize=13)
    p = os.path.join(OUT, "fig1_prisma_flow.png")
    fig.savefig(p, dpi=600, bbox_inches="tight")
    plt.close(fig)
    return p


def fig2(rows):
    grid = {d: {m: Counter() for m in MODALITY_GROUPS} for d in DOMAINS}
    for r in rows:
        d = r["domain"].replace("orthopedic/hand", "orthopedic")
        t = tier_letter(r["evidence tier"])
        if t == "protocol":
            continue
        grid[d][modality_group(r["cryo modality"])][t] += 1
    fig, ax = plt.subplots(figsize=(9, 4.5))
    groups = list(MODALITY_GROUPS)
    ax.set_xlim(0, len(DOMAINS))
    ax.set_ylim(0, len(groups))
    for i, d in enumerate(DOMAINS):
        for j, m in enumerate(groups):
            c = grid[d][m]
            a, b, cc = c.get("A", 0), c.get("B", 0), c.get("C", 0)
            tot = a + b + cc
            share = a / tot if tot else 0
            face = "#2e7d32" if share > 0.66 else "#a5d6a7" if share > 0.33 else \
                "#e0e0e0" if tot else "#ffffff"
            ax.add_patch(plt.Rectangle((i, j), 1, 1, facecolor=face,
                                       edgecolor="#555555"))
            if tot:
                ax.text(i + 0.5, j + 0.55, f"{a} / {b} / {cc}",
                        ha="center", va="center", fontsize=11)
                ax.text(i + 0.5, j + 0.25, "A / B / C",
                        ha="center", va="center", fontsize=6.5, color="#555555")
    ax.set_xticks([i + 0.5 for i in range(len(DOMAINS))])
    ax.set_xticklabels([DOMAIN_LABELS[d] for d in DOMAINS], fontsize=10)
    ax.set_yticks([j + 0.5 for j in range(len(groups))])
    ax.set_yticklabels([MODALITY_LABELS[g] for g in groups], fontsize=10)
    ax.invert_yaxis()
    ax.set_title("Evidence items per domain x modality cell (Tier A / B / C)",
                 fontsize=11)
    ax.text(0, len(groups) + 0.25,
            "Shading: proportion of direct (Tier A) items in the cell.",
            fontsize=8, color="#555555", transform=ax.transData)
    p = os.path.join(OUT, "fig2_evidence_map.png")
    fig.savefig(p, dpi=600, bbox_inches="tight")
    plt.close(fig)
    return p


def table_csv(summary):
    p = os.path.join(OUT, "domain_tier_table.csv")
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["domain", "tier A (direct)", "tier B (indirect)",
                    "tier C (contextual)", "protocols", "total"])
        for d in DOMAINS:
            c = summary["per_domain"][d]
            w.writerow([
                DOMAIN_LABELS[d], c.get("A", 0), c.get("B", 0), c.get("C", 0),
                c.get("protocol", 0), sum(c.values()),
            ])
        w.writerow([
            "Total",
            sum(summary["per_domain"][d].get("A", 0) for d in DOMAINS),
            sum(summary["per_domain"][d].get("B", 0) for d in DOMAINS),
            sum(summary["per_domain"][d].get("C", 0) for d in DOMAINS),
            sum(summary["per_domain"][d].get("protocol", 0) for d in DOMAINS),
            summary["total_items"],
        ])
    return p


def main():
    rows, prisma = load()
    summary = summarize(rows)
    assert summary["total_items"] == prisma["flow"]["included"], (
        summary["total_items"], prisma["flow"]["included"])
    p1 = fig1(prisma)
    p2 = fig2(rows)
    p3 = table_csv(summary)
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    for p in (p1, p2, p3):
        print("wrote", p)


if __name__ == "__main__":
    main()
