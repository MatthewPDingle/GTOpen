"""Read-only current-versus-average policy inspection of completed N19 saves."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'research/preflop-evolution/continuation'
OUT = BASE/'current-policy-20260916'
BIN = ROOT/'target/learned-interface-filtered/release/examples/convergence_diagnostics.exe'


def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, v): p.write_text(json.dumps(v, indent=2)+'\n', encoding='utf-8', newline='\n')


def run():
    assert dt.datetime.now(dt.timezone.utc) < dt.datetime(2026, 9, 16, 20, 49, 2, tzinfo=dt.timezone.utc)
    assert not OUT.exists(), 'Completed or partial audit exists; inspect before rerunning'
    OUT.mkdir()
    snapshot = read(BASE/'policy-stability-20260916/original/1500/iteration-1500.json')
    paths = [r['path'] for r in snapshot['views']]; assert len(paths) == 17
    write(OUT/'paths.json', dict(rows=[dict(candidate=dict(path=p)) for p in paths]))
    inputs = [Path(__file__), BIN, OUT/'paths.json', ROOT/'crates/solver/examples/convergence_diagnostics.rs',
              ROOT/'crates/solver/src/preflop/convergence_quality.rs', ROOT/'cache/preflop_eq169.bin',
              ROOT/'cache/realization_fit.json']
    inputs += [BASE/f'policy-stability-20260916/{arm}/1500/policy.gtop' for arm in ['original', 'candidate']]
    hashes = {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in inputs}
    write(OUT/'input-freeze.json', dict(registered_at=dt.datetime.now(dt.timezone.utc).isoformat(), inputs=hashes,
                                     production_enabled=False, scope='Read-only arena and reach inspection; no payoff evaluation or learning.'))
    rows = []
    for arm in ['original', 'candidate']:
        source = BASE/f'policy-stability-20260916/{arm}/1500/policy.gtop'
        target = OUT/f'{arm}.json'
        subprocess.run([str(BIN), str(source), str(OUT/'paths.json'), str(target)], cwd=ROOT, check=True)
        data = read(target); assert len(data['nodes']) == 17
        assert [n['path'] for n in data['nodes']] == paths
        for n in data['nodes']:
            assert n['iteration'] == 1500 and not n['forced'] and not n['frozen']
            mass = sum(h['average_conditional_hand_mass'] for h in n['hands'])
            tv = 0.; fallback = 0.; current = [0.]*len(n['actions']); average = current.copy()
            for h in n['hands']:
                a, c = h['average_probabilities'], h['current_probabilities']
                assert abs(sum(a)-1) < 1e-5 and abs(sum(c)-1) < 1e-5
                w = h['average_conditional_hand_mass']
                tv += w*sum(abs(x-y) for x,y in zip(a,c))/2
                fallback += w*h['current_uniform_fallback']
                for k in range(len(a)): current[k] += w*c[k]; average[k] += w*a[k]
            rows.append(dict(arm=arm, path=n['path'], actor=n['position'], average_range_mass=mass,
                             weighted_current_average_tv=tv if mass > 0 else None,
                             max_action_difference=max(abs(x-y) for x,y in zip(current,average)) if mass > 0 else None,
                             current_uniform_fallback_mass=fallback))
    for p, expected in hashes.items(): assert sha(ROOT/p) == expected, p
    write(OUT/'result.json', dict(rows=rows, inputs_unchanged=True,
          output_hashes={p.name:sha(p) for p in OUT.glob('*.json') if p.name not in ['result.json']},
          caveat='Selected nodes at one checkpoint, weighted by average own hand reach. No current-policy gap evaluation, temporal cycling proof, full-game convergence or accuracy claim.', production_enabled=False))
    lines = ['# Current versus averaged policy at 1500 iterations', '',
             'Read-only inspection of the same17 selected N19 nodes. No payoff evaluation or policy modification.', '',
             '| Path | Position | Ordinary current/average TV | Learned current/average TV |', '|---|---|---:|---:|']
    for p in paths:
        a, c = [next(r for r in rows if r['arm']==arm and r['path']==p) for arm in ['original','candidate']]
        lines.append(f"| {p} | {a['actor']} | {a['weighted_current_average_tv']} | {c['weighted_current_average_tv']} |")
    lines += ['', 'TV is weighted by the averaged policy own-range distribution. A missing range is recorded as null, not stable. '
              'Current/average differences at one instant do not prove oscillation over time or explain the remaining gap by themselves. '
              'The current policy has not been substituted into any reported convergence metric.', '']
    (OUT/'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')
    print('\n'.join(lines), flush=True)


if __name__ == '__main__': run()
