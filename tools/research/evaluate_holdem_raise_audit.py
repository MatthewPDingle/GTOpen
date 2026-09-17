"""Paired reference estimates and branch-aware uncertainty for call versus raise."""
import collections
import json
import numpy as np
import holdem_raise_audit as run


def terminal_coefficients(tree, info):
    nodes = tree['nodes']; parent = next(n for n in nodes if n['path'] == [2])
    denominator = info[parent['children'][0]]['factor']
    terms = {}
    def visit(i, own, action):
        node = nodes[i]
        if node['kind'] != 0:
            terms[i] = dict(action=action, coefficient=own*info[i]['factor']/denominator)
            return
        sigma = np.array(node['sigma']).reshape(-1, 169)
        for a, child in enumerate(node['children']):
            visit(child, own*sigma[a] if node['actor'] == 1 else own, action)
    for a in [1, 2]: visit(parent['children'][a], np.ones(169), a)
    for a in [1, 2]:
        assert np.max(np.abs(sum(t['coefficient'] for t in terms.values() if t['action'] == a)-1)) < 2e-6
    return terms, parent, denominator


def board_arrays(rows, pot):
    n = len(rows)
    mass = np.zeros((n, 169)); ev = mass.copy(); residual = mass.copy(); gain = mass.copy()
    for b, row in enumerate(rows):
        factor = row['job']['iso_weight']/row['job']['inclusion_probability']
        for h in row['hands'][0]:
            k = run.prior.pilot.INDEX[h['hand']]; w = factor*h['pair_mass']
            mass[b, k] = w; ev[b, k] = w*h['ev_bb']
            residual[b, k] = w*(h['ev_bb']-pot*h['equity'])
            gain[b, k] = w*max(0., h['br_ev_bb']-h['ev_bb'])
    assert (mass.sum(axis=0) > 0).all()
    return mass, ev, residual, gain


def classify(model, direct_ci, corrected_ci, call_frequency, raise_frequency, call_gain, raise_gain):
    if min(call_frequency, raise_frequency) < .0001: return 'sparse_action_support'
    if max(call_gain, raise_gain) > .025: return 'postflop_hand_unsettled'
    if model > .05 and max(direct_ci[1], corrected_ci[1]) < -.05:
        return 'clear_model_raise_reference_call'
    if model < -.05 and min(direct_ci[0], corrected_ci[0]) > .05:
        return 'clear_model_call_reference_raise'
    return 'uncertain_or_no_clear_sign_disagreement'


def evaluate(m, rows_by_case, tree):
    values, info, reaches = run.tree_values(tree)
    base_values, _, _ = run.tree_values(tree, 'balanced')
    terms, parent, denominator = terminal_coefficients(tree, info)
    candidate = values[parent['children']]/denominator
    balanced = base_values[parent['children']]/denominator
    assert np.max(np.abs(candidate[0]+1)) < 1e-10
    # Common paired board samples for all three postflop contexts.
    rng = np.random.default_rng(m['bootstrap_seed']); groups = collections.defaultdict(list)
    for i, board in enumerate(m['boards']): groups[board['stratum']].append(i)
    draws = np.zeros((m['bootstrap_replicates'], len(m['boards'])))
    for b in range(len(draws)):
        for ids in groups.values(): draws[b] += np.bincount(rng.choice(ids, len(ids)), minlength=len(m['boards']))
    leaves = {}; leaf_records = {}
    counts, eq = run.prior.pilot.matrices()
    for case in m['cases']:
        rows = rows_by_case[case['id']]
        assert [r['job']['board'] for r in rows] == [b['board'] for b in m['boards']]
        mass, ev, residual, gain = board_arrays(rows, case['pot'])
        total = mass.sum(axis=0); sampled_mass = draws@mass
        assert (sampled_mass > 0).all()
        context = run.prior.pilot.context(case, counts, eq)
        raw = ev.sum(axis=0)/total
        corrected = case['pot']*context['raw'][0]+residual.sum(axis=0)/total
        leaves[case['node']] = dict(direct=raw, corrected=corrected,
            direct_boot=(draws@ev)/sampled_mass,
            corrected_boot=case['pot']*context['raw'][0]+(draws@residual)/sampled_mass,
            gain=gain.sum(axis=0)/total)
        leaf_records[case['id']] = dict(node=case['node'], pot=case['pot'], stack=case['stack'],
            model_source=info[case['node']]['origin'],
            records=[dict(hand=run.prior.pilot.LABELS[k], model_gross_bb=float(info[case['node']]['gross'][k]),
                          direct_gross_bb=float(raw[k]), corrected_gross_bb=float(corrected[k]),
                          br_gain_bb=float(leaves[case['node']]['gain'][k])) for k in range(169)])
    raw = candidate[[1, 2]].copy(); corrected = raw.copy()
    raw_boot = np.broadcast_to(raw, (len(draws), 2, 169)).copy(); cv_boot = raw_boot.copy()
    gain = np.zeros((2, 169)); contributions = []
    for node_id, term in terms.items():
        a = term['action']-1; coefficient = term['coefficient']; node = tree['nodes'][node_id]
        learned_gross = info[node_id]['gross']; gross_raw = gross_cv = learned_gross
        if node_id in leaves:
            leaf = leaves[node_id]; gross_raw, gross_cv = leaf['direct'], leaf['corrected']
            raw[a] += coefficient*(gross_raw-learned_gross)
            corrected[a] += coefficient*(gross_cv-learned_gross)
            raw_boot[:, a] += coefficient*(leaf['direct_boot']-learned_gross)
            cv_boot[:, a] += coefficient*(leaf['corrected_boot']-learned_gross)
            gain[a] += coefficient*leaf['gain']
        contributions.append(dict(path=node['path'], action=term['action'],
            probability=coefficient.tolist(), model_source=info[node_id]['origin'],
            model_advantage_contribution_bb=(coefficient*(learned_gross-node['invested'][1]+1)).tolist(),
            direct_advantage_contribution_bb=(coefficient*(gross_raw-node['invested'][1]+1)).tolist(),
            corrected_advantage_contribution_bb=(coefficient*(gross_cv-node['invested'][1]+1)).tolist()))
    for a in [1, 2]:
        for key, expected in [('model', candidate[a]+1), ('direct', raw[a-1]+1), ('corrected', corrected[a-1]+1)]:
            summed = sum(np.array(t[key+'_advantage_contribution_bb']) for t in contributions if t['action']==a)
            assert np.max(np.abs(summed-expected)) < 2e-5
    sigma = np.array(parent['sigma']).reshape(-1, 169)
    delta_raw = raw[1]-raw[0]; delta_cv = corrected[1]-corrected[0]
    ci_raw = np.quantile(raw_boot[:, 1]-raw_boot[:, 0], [.025, .975], axis=0)
    ci_cv = np.quantile(cv_boot[:, 1]-cv_boot[:, 0], [.025, .975], axis=0)
    # Compare with exact same native values used by the first audit; independent
    # tree reconstruction was qualified before labels and is checked again here.
    native = next(r for r in run.read(run.prior.OUT/'candidate-values.json')['rows'] if r['path']==[2])
    native_base = next(r for r in run.read(run.prior.OUT/'balanced-values.json')['rows'] if r['path']==[2])
    records = []
    for k, hand in enumerate(native['hands']):
        v = hand['action_values_counterfactual_bb']; vb = native_base['hands'][k]['action_values_counterfactual_bb']
        model_delta = (v[2]-v[1])/-v[0]; baseline_delta = (vb[2]-vb[1])/-vb[0]
        assert abs(model_delta-(candidate[2, k]-candidate[1, k])) < 2e-5
        assert abs(baseline_delta-(balanced[2, k]-balanced[1, k])) < 2e-5
        decision = classify(model_delta, ci_raw[:, k], ci_cv[:, k], sigma[1, k], sigma[2, k], gain[0, k], gain[1, k])
        records.append(dict(hand=run.prior.pilot.LABELS[k], class_index=k,
            call_frequency=float(sigma[1, k]), raise_frequency=float(sigma[2, k]),
            candidate_delta_bb=model_delta, balanced_delta_bb=baseline_delta,
            direct_delta_bb=float(delta_raw[k]), corrected_delta_bb=float(delta_cv[k]),
            direct_95_interval=ci_raw[:, k].tolist(), corrected_95_interval=ci_cv[:, k].tolist(),
            candidate_call_advantage_bb=float(candidate[1, k]+1), candidate_raise_advantage_bb=float(candidate[2, k]+1),
            direct_call_advantage_bb=float(raw[0, k]+1), direct_raise_advantage_bb=float(raw[1, k]+1),
            corrected_call_advantage_bb=float(corrected[0, k]+1), corrected_raise_advantage_bb=float(corrected[1, k]+1),
            call_br_gain_bb=float(gain[0, k]), raise_br_gain_bb=float(gain[1, k]), decision=decision))
    # Weight descriptive errors by legal hand mass at the decision, restricted
    # to hands with support for BOTH first actions and settled references.
    joint = counts*(reaches[parent['id'], 1]/run.prior.pilot.COMBOS)[:, None]*(reaches[parent['id'], 0]/run.prior.pilot.COMBOS)[None, :]
    mass = joint.sum(axis=1)/joint.sum()
    qualified = np.array([not r['decision'] in ['sparse_action_support', 'postflop_hand_unsettled'] for r in records])
    qualified_mass = float(mass@qualified); weighted = mass*qualified/max(qualified_mass, 1e-100)
    errors = {}
    for model in ['candidate', 'balanced']:
        for label in ['direct', 'corrected']:
            errors[model+'_'+label] = float(weighted@np.array([abs(r[model+'_delta_bb']-r[label+'_delta_bb']) for r in records])) if qualified_mass else None
    return dict(records=records, counts=dict(collections.Counter(r['decision'] for r in records)),
        qualified_decision_pair_mass_fraction=qualified_mass, qualified_pair_weighted_mae_bb=errors,
        leaf_values=leaf_records, branch_contributions=contributions,
        positive_delta_means='3-bet preferred over call', production_enabled=False)


def main():
    m = run.checked(); tree = run.read(run.OUT/'tree.json'); old = run.prior.checked()
    call_rows = []
    for job in old['jobs']:
        row = run.read(run.prior.OUT/'jobs'/(job['id']+'.json')); run.prior.validate(row, job, old); call_rows.append(row)
    rows = {'call':call_rows}; hashes = {}
    for job in m['jobs']:
        path = run.OUT/'jobs'/(job['id']+'.json'); row = run.read(path); run.validate(row, job, m)
        rows.setdefault(job['case'], []).append(row); hashes[job['id']] = run.prior.pilot.sha(path)
    result = evaluate(m, rows, tree)
    result.update(manifest_id=m['id'], evaluated_at=run.now(), new_job_sha256=hashes,
        new_reference_seconds=sum(r['seconds'] for case in rows if case!='call' for r in rows[case]),
        max_cpu_gap_pct=max(r['gap_pct'] for case in rows for r in rows[case]),
        max_gpu_gap_pct=max(r['gpu_gap_pct'] for case in rows for r in rows[case]),
        new_reference_count=len(m['jobs']), reused_reference_count=len(call_rows))
    run.write(run.OUT/'evaluation.json', result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['records', 'branch_contributions', 'leaf_values', 'new_job_sha256']}, indent=2))


if __name__ == '__main__': main()
