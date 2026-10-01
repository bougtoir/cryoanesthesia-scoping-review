# Cryoanalgesia scoping review — figure/number reproduction

Code and input data that reproduce the figures and headline counts of a scoping-review
evidence map comparing cryoanalgesic modalities with local-anesthetic techniques across
clinical settings.

## Contents

- `reproduce.py` — regenerates every figure, table, and headline number from the inputs
- `data/reclassification.csv` — 48-item evidence charting table
  (citation, year, domain, design, population, modality, comparator, LA comparator,
  evidence tier, outcomes, persistent-pain definition, adverse events, interpretation bounds)
- `data/prisma_counts.json` — verified PRISMA-ScR flow counts
- `output/` — generated artifacts (fig1 flow diagram, fig2 evidence map,
  domain × tier table, summary.json)

## Run

```sh
pip install matplotlib
python3 reproduce.py
```

## What is reproduced

- PRISMA-ScR flow: 1,247 deduplicated records → 134 full texts → 38 + 10 = 48 evidence items
- Evidence map: direct (Tier A) / indirect (Tier B) / contextual (Tier C) counts
  per clinical domain × cryoanalgesic-modality group
- Headline counts: 48 evidence items across 5 domains; 16 completed direct
  local-anesthetic comparisons; trial protocols counted separately

"Evidence item" denotes a unique publication or registered report included for mapping
purposes — not an independent patient cohort; some syntheses summarize primary studies
also represented elsewhere in the map.
