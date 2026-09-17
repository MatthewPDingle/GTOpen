"""Fixed-policy call/3-bet audit; offline references, no live-server mutations."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import numpy as np
import holdem_call_audit as prior

ROOT = prior.ROOT
OUT = prior.BASE/'holdem-raise-audit-20260917'
PATHS = [[2, 1], [2, 2, 1], [2, 2, 2, 1]]
CASE_IDS = ['call', 'threebet-call', 'fourbet-call']
read, write, now = prior.read, prior.write, prior.now


def tree_values(tree, arm='candidate', replacement=None):
    """Independent legal-pair CF backup; replacement values are BB gross bb."""
    counts, eq = prior.pilot.matrices()
    combos = prior.pilot.COMBOS; prob = combos/1326
    kernel = counts/combos[:, None]/combos[None, :]
    z0 = prob@kernel@prob
    nodes = tree['nodes']; n = len(nodes)
    reaches = np.broadcast_to(prob, (n, 2, 169)).copy()
    for i, nd in enumerate(nodes):
        if nd['kind'] != 0: continue
        sigma = np.array(nd['sigma']).reshape(-1, 169)
        for a, child in enumerate(nd['children']):
            reaches[child] = reaches[i]
            reaches[child, nd['actor']] *= sigma[a]
    base = np.array(read(ROOT/'cache/realization_fit.json')['class_base'])
    model = read(prior.MODEL)
    relative = []
    for pos in [.92, 1.08]:
        a = eq*base[:, None]*pos; b = (1-eq)*base[None, :]*(2-pos)
        relative.append(a/(a+b))
    values = np.zeros((n, 169)); info = {}
    for i in range(n-1, -1, -1):
        nd = nodes[i]
        if nd['path'][:1] != [2]: continue
        if nd['kind'] == 0:
            child = values[nd['children']]
            values[i] = (child*np.array(nd['sigma']).reshape(-1, 169)).sum(axis=0) if nd['actor'] == 1 else child.sum(axis=0)
            continue
        # Heads-up root is the chance anchor. SB is IP, BB is OOP.
        r = reaches[i, [1, 0]]; total = r.sum(axis=1)
        assert (total > 0).all()
        d = r/total[:, None]; den = np.array([kernel@d[1], kernel@d[0]])
        raw = np.array([(kernel*eq)@d[1]/den[0], (kernel*eq)@d[0]/den[1]])
        pot = nd['pot']; left = min(tree['config']['stack']-v for v in nd['invested']); spr = left/pot
        factor = total[1]*den[0]/z0
        if nd['kind'] == 1:
            gross = np.full(169, pot if nd['winner'] == 1 else 0.)
            origin = 'fold'
        else:
            pred = raw.copy()
            for side, seat in enumerate([1, 0]):
                blend = min(1., abs(nd['r'][seat]-1)/.08)
                pred[side] += blend*((kernel*relative[side])@d[1-side]/den[side]-raw[side])
            origin = 'cached_allin_equity' if left == 0 else 'balanced_fallback'
            if arm == 'candidate' and 1 <= spr <= 20:
                case = dict(weights=(d/combos).tolist(), pot=pot, stack=left)
                context = prior.pilot.context(case, counts, eq)
                context.update(case=case, base_x=context['x'].copy(), base_names=list(context['names']))
                pred = prior.network.predict(context, model); origin = 'learned'
            gross = pot*pred[0]
        info[i] = dict(factor=factor, gross=gross.copy(), origin=origin, raw_equity=raw[0])
        if replacement is not None and i in replacement: gross = replacement[i]
        values[i] = factor*(gross-nd['invested'][1])
    return values, info, reaches


def native_comparison(tree, arm):
    values, info, reaches = tree_values(tree, arm)
    node = next(n for n in tree['nodes'] if n['path'] == [2])
    native = read(prior.OUT/(arm+'-values.json'))
    bb = next(r for r in native['rows'] if r['path'] == [2])
    observed = np.array([h['action_values_counterfactual_bb'] for h in bb['hands']])
    expected = values[node['children']].T
    error = float(np.max(np.abs(expected-observed)))
    assert error < 2e-5, (arm, error)
    return dict(max_cf_error_bb=error, values_checked=int(expected.size),
                action_labels=[a['label'] for a in node['actions']])


def prepare():
    assert not (OUT/'manifest.json').exists(), 'Do not overwrite registered protocol'
    old = prior.checked(); tree = read(OUT/'tree.json')
    assert tree['config'] == read(prior.SNAPSHOT)['config'] and tree['read_only']
    preflight = {arm: native_comparison(tree, arm) for arm in ['candidate', 'balanced']}
    cases = []; jobs = []
    for path, ident in zip(PATHS, CASE_IDS):
        nd = next(n for n in tree['nodes'] if n['path'] == path)
        # Reproduce the native UI/export f32 division, preserving exact old ranges.
        p = (prior.pilot.COMBOS/1326).astype(np.float32)
        weights = np.minimum(np.array(nd['reaches'], dtype=np.float32)/p, 1.)[[1, 0]].astype(float)
        case = dict(id=ident, node=nd['id'], path=path, pot=nd['pot'],
                    stack=min(tree['config']['stack']-v for v in nd['invested']),
                    weights=weights.tolist(), positions=['BB', 'SB'])
        texts = [','.join(f'{prior.pilot.LABELS[h]}:{v:.9g}' for h, v in enumerate(row) if v > 0) for row in weights]
        case.update(range_oop=texts[0], range_ip=texts[1]); cases.append(case)
        if ident == 'call':
            assert np.array_equal(weights, np.array(old['case']['weights']))
            assert texts == [old['case']['range_oop'], old['case']['range_ip']]
            continue
        config_tree = dict(old['jobs'][0]['config']['tree'])
        config_tree.update(starting_pot=case['pot'], effective_stack=case['stack'])
        for b in old['boards']:
            jobs.append(dict(**b, id=ident+'-'+b['board'], case=ident,
                config=dict(board=b['board'], range_oop=texts[0], range_ip=texts[1], tree=config_tree)))
    paths = [Path(__file__), OUT/'PROTOCOL.md', OUT/'tree.json',
             ROOT/'crates/solver/examples/holdem_action_export.rs',
             ROOT/'target/learned-interface-filtered/release/examples/holdem_action_export.exe',
             prior.OUT/'manifest.json', prior.OUT/'evaluation.json']
    paths += [prior.OUT/'jobs'/(j['id']+'.json') for j in old['jobs']]
    inputs = dict(old['inputs'])
    inputs.update({p.relative_to(ROOT).as_posix(): prior.pilot.sha(p) for p in paths})
    m = dict(registered_at=now(), cases=cases, jobs=jobs, boards=old['boards'],
             reused_call_manifest=old['id'], target_gap_pct=.1, max_iterations=2000,
             bootstrap_seed=20260918, bootstrap_replicates=5000, probes=prior.PROBES,
             inputs=inputs, production_enabled=False)
    m['id'] = hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest()
    preflight.update(live_app=prior.idle(), new_references=len(jobs), reused_references=50,
                     source_save_sha256=prior.pilot.sha(prior.SAVE))
    write(OUT/'preflight.json', preflight); write(OUT/'manifest.json', m)
    print(json.dumps(preflight, indent=2))


def checked():
    m = read(OUT/'manifest.json')
    assert hashlib.sha256(json.dumps({k:v for k,v in m.items() if k != 'id'}, sort_keys=True).encode()).hexdigest() == m['id']
    for p, digest in m['inputs'].items(): assert prior.pilot.sha(ROOT/p) == digest, p
    return m


def validate(row, job, m):
    assert row['manifest_id'] == m['id'] and row['job'] == job and row['target_met']
    assert 0 <= row['gap_pct'] <= .1 and 0 <= row['gpu_gap_pct'] <= .1
    assert row['query_mode'] == 'materialized_full_enumeration'
    assert abs(sum(row['means_bb'])-job['config']['tree']['starting_pot']) < .002
    for hands in row['hands']:
        assert len({h['hand'] for h in hands}) == len(hands)
        assert all(np.isfinite([h['pair_mass'], h['ev_bb'], h['equity'], h['br_ev_bb']]).all() for h in hands)
        assert abs(sum(h['pair_mass'] for h in hands)/row['pair_mass']-1) < 1e-5


def run():
    m = checked(); start = time.perf_counter()
    env = dict(os.environ); env['PATH'] = str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH', '')
    for i, job in enumerate(m['jobs']):
        path = OUT/'jobs'/(job['id']+'.json')
        if not path.exists():
            prior.idle()
            write(OUT/'status.json', dict(stage='references', completed=i, total=len(m['jobs']), active=job['id'], updated=now()))
            with (OUT/(job['id']+'.log')).open('w', encoding='utf-8', newline='\n') as log:
                subprocess.run([str(prior.REFERENCE), str(OUT/'manifest.json'), '1'], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        validate(read(path), job, m)
        print('reference', i+1, '/', len(m['jobs']), job['id'], 'elapsed', round(time.perf_counter()-start), flush=True)
    checked(); write(OUT/'status.json', dict(stage='references_complete', completed=len(m['jobs']), total=len(m['jobs']), updated=now()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['prepare', 'run'])
    {'prepare':prepare, 'run':run}[parser.parse_args().command]()
