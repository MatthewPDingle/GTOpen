# Research range preview

Open <http://localhost:56708/research/preflop-evolution/range-preview/> while the
normal local GTOpen server is running. This standalone, read-only page uses the
server's existing static research route. It does not load a game, change either
solver session, run a solve, or replace the production preflop model.

Compare weighted-112, equal-weight-112, the earlier 47-flop policy, and the saved
Balanced baseline. The four available decisions belong to the same fixed
200 bb, straddled, eight-player source situation: the early opener faces a
3-bet after everyone else folds. Study labels UTG/LJ correspond to the original
GTOpen seats UTG1/MP. There is no new blind-defense policy or arbitrary setup
editor in this preview.

Use the Decision selector or a raise action to navigate. Hover/focus a hand for
all action frequencies; click to pin a comparison. Bar height represents relative
arriving weight per physical combo, normalized to the largest class density in
that panel. A low bar is not a low continuation frequency. Class frequencies and
totals include live-player card compatibility and the selected policy's earlier
actions. Unsupported hands are blank. Earlier folded-card effects are omitted.

The builder verifies frozen source hashes and the common entry prior. It
checks all 16 model/node combinations, probability normalization, and
reconstruction of total frequencies from class rows. Original saved f32 columns
are normalized for display (rounding differences below 2e-7); source files are
not changed. `data-review.json` records identities. Rebuild with:

```
python tools/research/build_preflop_research_preview_20260922.py
```

Browser verification covered all 16 model/node combinations, displayed totals,
169 cells per panel, complete tooltips, hand pinning, raise navigation, and
390-pixel mobile layout without horizontal overflow. Desktop and mobile captures
are local under `output/playwright/research-preview/`.

This is an inspection preview of experimental policies, not a general-purpose
test solver or a claim of agreement with GTO Wizard. The independent comparison
and its limitations are documented in
[`STRATEGIC-CONFIRM190-RESULT.md`](../ssd-storage-20260920/STRATEGIC-CONFIRM190-RESULT.md).
