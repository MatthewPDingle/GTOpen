"""Prospective low-SPR references. Offline only; preserves all earlier studies."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import numpy as np
import holdem_raise_audit as old

prior = old.prior
pilot = prior.pilot
ROOT = old.ROOT
OUT = prior.BASE/'shallow-continuation-20260917'
read, write, now = prior.read, prior.write, prior.now


def panel(seed, per_stratum, exclude=()):
    groups = collections.defaultdict(list)
    for board, iso in read(pilot.AUDIT/'fixtures.json')['canonical_flops']:
        if board in exclude: continue
        cards = [board[i:i+2] for i in range(0, 6, 2)]
        key = ('paired' if len({c[0] for c in cards}) < 3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))+'suits'
        groups[key].append((board, iso))
    result = []
    for key, items in sorted(groups.items()):
        items.sort(key=lambda x: hashlib.sha256((seed+x[0]).encode()).digest())
        for board, iso in items[:per_stratum]:
            result.append(dict(board=board, iso_weight=iso, stratum=key,
                               inclusion_probability=per_stratum/len(items)))
    return result


def prepare():
    assert not (OUT/'manifest.json').exists()
    old_manifest = old.checked()
    old_boards = {b['board'] for b in old_manifest['boards']}
    panels = dict(confirmation=panel('shallow-confirm-v1', 20, old_boards),
                  train=panel('shallow-train-v1', 4), heldout=panel('shallow-heldout-v1', 6))
    cases = []
    target = dict(old_manifest['cases'][2])
    target.update(id='confirmation', partition='confirmation', family='saved-hu40')
    cases.append(target)
    designed = read(pilot.OUT/'manifest.json')['cases']
    for family in ['linear_capped', 'polar_broad', 'linear_broad']:
        template = next(c for c in designed if c['family'] == family and 'forward' in c['id'])
        for spr in [.2, .75]:
            c = dict(template)
            c.update(id=f'train-{family}-{spr}', partition='train', pot=45., stack=45*spr)
            cases.append(c)
    # New mixtures and a premium-dominated pair, never used to fit coefficients.
    templates = {c['family']:c for c in designed if 'forward' in c['id']}
    lc = np.array(templates['linear_capped']['weights'])
    pb = np.array(templates['polar_broad']['weights'])
    premium = np.array(pilot.weights('AA,KK,QQ,JJ:0.5,TT:0.2,AKs,AKo,AQs:0.5,A5s:0.2'))
    for ident, w in [('mixed', .6*lc+.4*pb), ('premium', np.array([.7*lc[1]+.3*pb[1], premium]))]:
        cases.append(dict(id='heldout-'+ident, family=ident, partition='heldout',
                          pot=45., stack=17.5, weights=w.tolist()))
    jobs = []
    for c in cases:
        if c['partition'] != 'confirmation':
            # Tiny nonzero support allows inspection, but quality gates still apply.
            w = np.maximum(np.array(c['weights']), .0001)
            texts = [','.join(f'{pilot.LABELS[k]}:{v:.9g}' for k,v in enumerate(row)) for row in w]
            c.update(weights=[pilot.weights(t) for t in texts], range_oop=texts[0], range_ip=texts[1])
        cfg_tree = dict(old_manifest['jobs'][0]['config']['tree'])
        cfg_tree.update(starting_pot=c['pot'], effective_stack=c['stack'])
        for b in panels[c['partition']]:
            jobs.append(dict(**b, case=c['id'], id=c['id']+'-'+b['board'],
                config=dict(board=b['board'], range_oop=c['range_oop'], range_ip=c['range_ip'], tree=cfg_tree)))
    sources = [Path(__file__), OUT/'PROTOCOL.md', ROOT/'tools/research/shallow_continuation_fit.py',
               old.OUT/'manifest.json', pilot.OUT/'manifest.json', prior.REFERENCE]
    inputs = dict(old_manifest['inputs'])
    inputs.update({p.relative_to(ROOT).as_posix():pilot.sha(p) for p in sources})
    m = dict(registered_at=now(), cases=cases, panels=panels, jobs=jobs, inputs=inputs,
             old_manifest_id=old_manifest['id'], target_gap_pct=.1, max_iterations=2000,
             production_enabled=False, bootstrap_seed=2026091703, bootstrap_replicates=5000)
    m['id'] = hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest()
    write(OUT/'preflight.json', dict(live=prior.idle(), references=len(jobs), production_enabled=False))
    write(OUT/'manifest.json', m)
    print('Registered', len(jobs), 'references', m['id'], flush=True)


def checked():
    m = read(OUT/'manifest.json')
    assert hashlib.sha256(json.dumps({k:v for k,v in m.items() if k != 'id'}, sort_keys=True).encode()).hexdigest() == m['id']
    for p,h in m['inputs'].items(): assert pilot.sha(ROOT/p) == h, p
    return m


def run():
    m = checked(); start = time.perf_counter()
    env = dict(os.environ)
    env['PATH'] = str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH', '')
    for i,j in enumerate(m['jobs']):
        path = OUT/'jobs'/(j['id']+'.json')
        if not path.exists():
            prior.idle()
            write(OUT/'status.json', dict(stage='references', completed=i, total=len(m['jobs']), active=j['id'], updated=now()))
            with (OUT/(j['id']+'.log')).open('w', encoding='utf-8', newline='\n') as log:
                subprocess.run([str(prior.REFERENCE), str(OUT/'manifest.json'), '1'], cwd=ROOT, env=env,
                               stdout=log, stderr=subprocess.STDOUT, check=True)
        old.validate(read(path), j, m)
        print('reference', i+1, '/', len(m['jobs']), j['id'], 'elapsed', round(time.perf_counter()-start), flush=True)
    checked()
    write(OUT/'status.json', dict(stage='references_complete', completed=len(m['jobs']), total=len(m['jobs']), updated=now()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['prepare', 'run'])
    {'prepare':prepare, 'run':run}[parser.parse_args().command]()
