# Same reserved boards, explicit evaluator metadata

Use `expansion-reserved-95-evaluation-v1.json` when running the common frozen-policy evaluator. It preserves every board, weight, selection seed, offset, population description and reserved flag from the original registered `expansion-reserved-95.json`. The original remains unchanged, and its SHA-256 is recorded in the evaluation copy.

The original sampling helper placed `future_card_policy: projected_explicit` in every generated manifest. That matches the new training executable, but not the common streamed evaluator selected in the strategic comparison plan. The evaluation copy labels the latter `plain_explicit`. This label is descriptive: the retained evaluator reads boards, weights, suit-orbit treatment and the bet menu; it does not use `future_card_policy` to select a numerical method. The executable hash determines the actual method. No solver code or behavior changes here.

The source audit in `STRATEGIC-EVALUATION-COMPATIBILITY.md` still applies. New weighted versus equal-weight training is a controlled comparison. Comparisons with the older 47-board baseline cannot isolate board coverage from the difference in training updates. All three frozen policies will receive the same plain explicit evaluation procedure.

The selection was reproduced from its original seed and eligible population, with exact board/weight equality. Its 95 suit-isomorphic representatives remain disjoint from all three training candidates and all 164 earlier comparison boards. Its eligible population is 15,320 of 22,100 physical flops. This metadata correction neither reads reserved strategy results nor converts that restricted sample into a full-deck accuracy measure.
