"""Exploratory read-only coverage/drift diagnostic of all four completed banks.

No new deals, refits, selected checkpoints, promotion or stationary-error claims.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
import time
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['OMP_NUM_THREADS'] = '2'

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'later-action-root-trajectory-v1'
TRIALS = ['action-integrated-fresh-pilot-v1', 'later-action-first-audit-recovery-v1',
          'action-integrated-replication-v1', 'later-action-replication-volume-continuation-v1']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def object_read(folder, ref, inputs):
    path = folder / ref['file']
    assert path.resolve().parent == folder.resolve()
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ref['sha256']
    inputs[str(path)] = ref['sha256']
    return json.loads(raw)


def policy(state, fallback):
    rows = []
    for n, regret in zip(state['sample_counts'], state['regret_sums'], strict=True):
        assert len(regret) == 4 and all(math.isfinite(x) for x in regret)
        if not n:
            assert regret == [0., 0., 0., 0.]
            rows.append(fallback[len(rows)])
        else:
            positive = [max(x, 0) for x in regret]; total = math.fsum(positive)
            if total:
                rows.append([x / total for x in positive])
            else:
                best = max(range(4), key=regret.__getitem__)
                rows.append([float(a == best) for a in range(4)])
    return rows


def tv(a, b, mass):
    return math.fsum(w * math.fsum(abs(x-y) for x,y in zip(p,q)) * .5 for w,p,q in zip(mass,a,b))


def average(policies, generations):
    denominator = sum(g+1 for g in generations)
    return [[math.fsum((g+1)*policies[g][c][a] for g in generations)/denominator
             for a in range(4)] for c in range(169)]


def main():
    started = time.monotonic(); inputs = {str(Path(__file__)): sha(Path(__file__))}
    source_path = OUT / 'later-action-final-root-stability.json'
    source = load(source_path); inputs[str(source_path)] = sha(source_path)
    source_result = load(OUT / 'later-action-compact-evaluation-study-v1-result.json')
    source_review = load(OUT / 'later-action-compact-evaluation-study-v1-independent-review.json')
    assert source_result['root_stability_sha256'] == sha(source_path)
    assert source_review['passed'] and source_review['source_result_sha256'] == sha(OUT / 'later-action-compact-evaluation-study-v1-result.json')
    mass = source['entry_masses']; findings = []; class_rows = []; count_arrays = []
    context_path = OUT/'bb-context-candidate.json'
    catalog_path = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    matrix_path = OUT/'preflop-allin-matrix-control-v1-matrix.json'
    context = context_path.read_text(); catalog = catalog_path.read_text()
    from preflop_allin_matrix_v1 import AllinMatrix
    from exact_initial_single_policy64_v1 import predict
    entry_mass = AllinMatrix(load(matrix_path), context).btn_mass
    root_obs = {r['hand_class']:r['observation'] for r in json.loads(catalog)['native_observations'] if r['player']==0}
    for path in [context_path,catalog_path,matrix_path,*Path(__file__).parent.glob('*.py')]: inputs[str(path)] = sha(path)
    for index, prefix in enumerate(TRIALS):
        metadata = {}
        for suffix in ['registration', 'result', 'independent-review']:
            path = OUT / f'{prefix}-{suffix}.json'
            metadata[suffix] = load(path); inputs[str(path)] = sha(path)
        result, review = metadata['result'], metadata['independent-review']
        assert result['passed'] and result['terminal'] and review['passed']
        assert review['source_result_sha256'] == sha(OUT / f'{prefix}-result.json')
        assert result['registration_sha256'] == sha(OUT / f'{prefix}-registration.json')
        folder = Path(result['store']) / 'objects'
        checkpoint = object_read(folder, result['final_checkpoint'], inputs)
        assert checkpoint['completed_iterations'] == 78 and len(checkpoint['played_bank']) == 78
        states = []; policies = []
        for generation, ref in enumerate([*checkpoint['played_bank'], checkpoint['next_model']]):
            doc = object_read(folder, ref, inputs)
            assert doc['generation'] == ref['generation'] == generation
            state = doc['integrated_root']['state']
            assert state['completed_updates'] == generation
            assert len(state['sample_counts']) == len(state['regret_sums']) == 169
            assert sum(state['sample_counts']) == generation * 512
            missing = [c for c,n in enumerate(state['sample_counts']) if not n]
            fallback = {}
            if missing:
                query = dict(context_source=context,observations=[root_obs[c] for c in missing])
                _, probabilities, _ = predict(query,doc['exact_model'],catalog_source=catalog,
                    matrix_sha256=sha(matrix_path),entry_mass=entry_mass,device='cpu')
                fallback = {c:p.tolist() for c,p in zip(missing,probabilities)}
            states.append(state); policies.append(policy(state, fallback))
        counts = [s['sample_counts'] for s in states]; count_arrays.append(counts)
        complete = average(policies, list(range(78)))
        max_error = max(abs(a-b) for x,y in zip(complete, source['root_probabilities'][index]) for a,b in zip(x,y))
        assert max_error < 1e-12, (prefix, max_error)
        updates = []
        for g in range(1,79):
            increment = [b-a for a,b in zip(counts[g-1],counts[g])]
            assert min(increment) >= 0 and sum(increment) == 512
            switches = [max(range(4),key=policies[g-1][c].__getitem__) != max(range(4),key=policies[g][c].__getitem__) for c in range(169)]
            updates.append(dict(generation=g, zero_sample_classes=sum(n==0 for n in increment),
                zero_sample_entry_mass=math.fsum(w for w,n in zip(mass,increment) if not n),
                weighted_policy_step_tv=tv(policies[g-1],policies[g],mass),
                modal_switch_entry_mass=math.fsum(w for w,x in zip(mass,switches) if x),
                cumulative_average_tv_to_complete=tv(average(policies,list(range(g))),complete,mass)))
        windows=[average(policies,list(range(lo,hi))) for lo,hi in [(0,26),(26,52),(52,78)]]
        final_counts = counts[-1]
        per_class=[]
        for c in range(169):
            n=[counts[g][c]-counts[g-1][c] for g in range(1,79)]
            switches=sum(max(range(4),key=policies[g-1][c].__getitem__)!=max(range(4),key=policies[g][c].__getitem__) for g in range(1,79))
            row=dict(bank=source['policy_order'][index], hand_class=c, entry_mass=mass[c],
                deals=final_counts[c], average_deals_per_update=final_counts[c]/78,
                zero_sample_updates=sum(x==0 for x in n), modal_switches=switches,
                final_current_vs_played_average_tv=tv([policies[-1][c]],[complete[c]],[1.]))
            class_rows.append(row); per_class.append(row)
        findings.append(dict(prefix=prefix, bank=source['policy_order'][index],
            counts_min=min(final_counts),counts_median=sorted(final_counts)[84],counts_max=max(final_counts),
            count_total=sum(final_counts), played_average_max_error=max_error,
            mean_zero_sample_classes_per_update=math.fsum(x['zero_sample_classes'] for x in updates)/78,
            mean_zero_sample_entry_mass_per_update=math.fsum(x['zero_sample_entry_mass'] for x in updates)/78,
            first_middle_window_tv=tv(windows[0],windows[1],mass),
            middle_last_window_tv=tv(windows[1],windows[2],mass),
            final_current_vs_played_average_tv=tv(policies[-1],complete,mass),
            mean_step_tv_last_26=math.fsum(x['weighted_policy_step_tv'] for x in updates[52:])/26,
            updates=updates,classes=per_class))
        print(json.dumps({k:v for k,v in findings[-1].items() if k not in ('updates','classes')}),flush=True)
    # Same sampler seeds and budgets must give identical class coverage within each pair.
    assert count_arrays[0] == count_arrays[1] and count_arrays[2] == count_arrays[3]
    for path,digest in inputs.items(): assert sha(Path(path)) == digest, path
    document=dict(passed=True,exploratory=True,inputs=inputs,findings=findings,
        matched_class_counts_identical=True,new_deals=0,gpu_used=False,production_modified=False,
        final_unplayed_generation_used_only_for_diagnostic=True,
        scope='Coverage and changing root policies only; no variance attribution, stationary confidence intervals, best-response claim or selected alternative policy.',
        seconds=time.monotonic()-started)
    with (OUT/f'{PREFIX}-result.json').open('x') as stream: json.dump(document,stream,separators=(',',':'))
    with (OUT/f'{PREFIX}-classes.csv').open('x',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(class_rows[0]));writer.writeheader();writer.writerows(class_rows)


if __name__ == '__main__': main()
