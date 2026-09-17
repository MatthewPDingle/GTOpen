"""Post-evaluation branch attribution; descriptive only, no fitting or new gate."""
import numpy as np
import shallow_native_feedback as study


def diagnose():
    m = study.checked()
    e = study.read(study.OUT / 'evaluation.json')
    tree = study.read(study.OUT / 'shallow/tree.json')
    values, info, reaches = study.native.tree_values(tree)
    terms, parent, den = study.action.terminal_coefficients(tree, info)
    counts, _ = study.pilot.matrices()
    r = reaches[parent['id']]
    joint = counts * (r[1] / study.pilot.COMBOS)[:, None] * (r[0] / study.pilot.COMBOS)[None, :]
    mass = joint.sum(axis=1) / joint.sum()
    records = e['actions']['records']
    qualified = np.array([min(h['call_frequency'], h['raise_frequency']) >= .0001
                          and max(h['call_br_gain_bb'], h['raise_br_gain_bb']) <= .025 for h in records])
    w = mass * qualified
    w /= w.sum()
    summaries = {}
    for estimator in ['direct', 'corrected']:
        total = np.array([h['shallow_delta_bb'] - h[estimator + '_delta_bb'] for h in records])
        parts = {}
        for case in m['cases']:
            t = terms[case['node']]
            hands = e['leaf_reports'][case['id']]['hand_records']
            reference = np.array([h[estimator + '_gross_bb'] for h in hands if h['side'] == 0])
            sign = -1 if t['action'] == 1 else 1
            parts[case['id']] = sign * t['coefficient'] * (info[case['node']]['gross'] - reference)
        reconstruction = float(abs(sum(parts.values()) - total).max())
        assert reconstruction < 2e-5, reconstruction
        mae = float(w @ abs(total))
        assert abs(mae - e['actions']['call_vs_raise']['pair_weighted_mae_bb']['shallow'][estimator]) < 1e-10
        summaries[estimator] = dict(total_mae_bb=mae, reconstruction_error_bb=reconstruction,
            branches={name: dict(weighted_absolute_contribution_bb=float(w @ abs(p)),
                                 weighted_signed_contribution_bb=float(w @ p),
                                 hypothetical_mae_if_only_this_branch_were_exact_bb=float(w @ abs(total-p)))
                      for name, p in parts.items()},
            hands=[dict(hand=h['hand'], qualified=bool(qualified[k]), total_error_bb=float(total[k]),
                        contributions_bb={name: float(p[k]) for name, p in parts.items()})
                   for k, h in enumerate(records)])
    out = dict(manifest_id=m['id'], evaluated_at=study.now(), qualified_classes=int(qualified.sum()),
               qualified_decision_mass=float(mass @ qualified), estimators=summaries,
               interpretation='Descriptive decomposition on the existing evaluation sample. Absolute branch errors can cancel; they are not additive shares of total error. Hypothetical exact replacements are diagnostics, not validated models or measured policy improvements.',
               production_enabled=False)
    study.write(study.OUT / 'branch-diagnostic.json', out)
    for key, row in summaries.items():
        print(key, {k: v for k, v in row.items() if k != 'hands'})


if __name__ == '__main__':
    diagnose()
