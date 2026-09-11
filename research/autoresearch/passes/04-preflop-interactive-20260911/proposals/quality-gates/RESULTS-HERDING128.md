# Frozen128 terminal audit

Sources: `raw/ensemble128-training-a.log`, `raw/independent128-physical-a.log`, `raw/regression128-physical-a.log`; candidate `frozen-herding128-a.json`. Selection used only the unchanged synthetic training contexts, preserved the frozen64 prefix, and wrote the128 manifest before evaluation. This is follow-up evidence; original inspected contexts remain reused regression, separate from the newly reserved confirmation corpus.

**Verdict: the physical gates tested here pass, with uncertainty accounted for.**128 is worth bounded native policy/timing validation. This does not qualify default deployment, full postflop accuracy, local decisions or10x faster usable solving.

| New reserved case | Candidate MAE / worst (pp) | Full1024 MAE / worst (pp) |
|---|---:|---:|
|Asymmetric3|1.0676 /1.8644|0.7723 /1.9092|
|Overlap4, stress|1.2241 /1.9880|0.9975 /1.5863|
|Sparse6|1.1888 /2.5682|1.3459 /2.5503|
|Asymmetric8|0.7576 /2.7977|0.8198 /1.7710|

All24 new references completed100,000 accepted compatible deals. The nonstress pooled mean is1.0046pp; per-case means and all worst-hand errors are comfortably inside3/4/7pp gates even after adding twice each recorded half-width. The largest new half-width is0.3078pp.

The new overlap additional mean is0.2266064pp. Registered common-reference interval propagation gives[0.1042053,0.3338525]pp, below+1pp. Its nominal worsening in worst error is0.4016893pp; even the conservative upper bound formed from the maximum candidate upper error minus maximum reference lower error is1.2460619pp, below+2pp. No million-deal extension is needed for these margins.

Reused primary core cases have MAE1.2157/1.1012/1.0178pp and worst2.1770/2.3708/2.3565pp for3/4/6 players. Reused overlap additional mean is0.4943841pp with propagated interval[-0.1203180,0.7621050]pp. Its worst worsening is1.7266064pp. KJo remains the largest absolute error for both models throughout the reference intervals and both lie above the same physical mean, so this difference is constant; treating the two errors as independent would incorrectly inflate its uncertainty. Both reused overlap gates pass.

Historical nonpremium core: pooled mean1.7446pp, largest case mean2.6127pp, worst5.0764pp (uniform three-way22). These margins exceed the respective sampling uncertainty. Historical premium-only stress improves mean error by0.6720pp and worst error by1.4479pp versus full1024; this passes the relative guard while retaining a large absolute worst error14.3978pp. Matching the full model's limitations does not turn that stress into physically accurate poker.

Original BB mean error1.7080pp/worst3.1687pp and rebuilt BB mean1.4165pp/worst1.9275pp pass3/5pp limits. KQo retains a profitable closing call: original candidate equity22.4220% gives+0.7041bb showdown call surplus; rebuilt24.0037% gives+0.8243bb, compared with rebuilt physical+0.7713bb. No KQo exception was added.

Next gate is a distinct native128 candidate with exact index identity and pot/tie/save/CPU-GPU checks, then frozen-policy global and selected-local comparisons.128 reduces particle work by8x at most before fixed overhead; its terminal success alone cannot meet or establish the10x end-to-end goal. The smaller frozen models' failed overlap results remain unchanged.
