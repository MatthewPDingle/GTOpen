"""Apply proposed arithmetic to fixed old training traces without changing them.

Four evenly spaced generations of the already inspected visible-input trial.
No new deals, current trial access, inference, fitting, native walk or RNG use.
Observed variance is descriptive, not a controlled training improvement.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import json
import time
from pathlib import Path
import numpy as np
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class
from reboot_research_idle_v1 import idle
from preflop_allin_matrix_v1 import AllinMatrix
from initial_allin_targets_v1 import bb_correction, btn_targets

PREFIX = 'initial-allin-trace-diagnostic-v1'
GENERATIONS = (0, 25, 51, 77)


def statistics(old, new):
    old, new = np.asarray(old), np.asarray(new)
    assert old.shape == new.shape and len(old) > 1
    return dict(observations=len(old), old_mean=old.mean(0).tolist(), corrected_mean=new.mean(0).tolist(),
        old_sample_variance=old.var(0, ddof=1).tolist(), corrected_sample_variance=new.var(0, ddof=1).tolist(),
        caveat='Finite old sample; variation includes hand-class signal. Not an unbiased conditional variance comparison or achieved training improvement.')


def main():
    started = time.monotonic()
    def guard():
        assert idle() and psutil.virtual_memory().available > 20_000_000_000 and time.monotonic()-started < 600
    guard()
    rp = OUT/f'{PREFIX}-registration.json'
    assert not rp.exists(), 'Preserve previous attempts'
    inputs = {}
    def admit(path):
        path = Path(path); inputs[str(path)] = sha(path); return read(path)
    arpath = OUT/'allin-generation-attribution-v1-registration.json'
    ar, ap, aa = [admit(OUT/f'allin-generation-attribution-v1-{k}.json') for k in ('registration', 'result', 'independent-review')]
    assert aa['passed'] and aa['result_sha256'] == sha(OUT/'allin-generation-attribution-v1-result.json')
    assert ap['registration_sha256'] == sha(arpath)
    gp = next(Path(p) for p in ap['artifacts'] if Path(p).name == 'visible_302-generation-policies.json')
    assert sha(gp) == ap['artifacts'][str(gp)]
    generations = np.asarray(admit(gp)['policies'])
    catalog = admit(ar['catalog'])['native_observations']
    srpath = OUT/'sampled-visible-hybrid-completion-pilot-v1-registration.json'
    sr = admit(srpath)
    audit = admit(OUT/'sampled-visible-hybrid-completion-pilot-v1-independent-review.json')
    assert audit['passed'] and audit['terminal_complete'] and audit['source_registration_sha256'] == sha(srpath)
    store = Path(sr['store'])
    mr, mp, ma = [admit(OUT/f'preflop-allin-matrix-control-v1-{k}.json') for k in ('registration', 'result', 'independent-review')]
    assert ma['passed'] and ma['result_sha256'] == sha(OUT/'preflop-allin-matrix-control-v1-result.json')
    matrix_path = Path(mp['matrix_artifact']); assert sha(matrix_path) == mp['matrix_sha256']
    source_path = OUT/'bb-context-candidate.json'; source = source_path.read_text(); inputs[str(source_path)] = sha(source_path)
    matrix = AllinMatrix(admit(matrix_path), source)
    control = admit(OUT/'initial-allin-target-control-v1-result.json')
    assert control['passed'] and control['registration_sha256'] == sha(OUT/'initial-allin-target-control-v1-registration.json')
    inputs[str(OUT/'initial-allin-target-control-v1-registration.json')] = control['registration_sha256']
    for path in (Path(__file__), ROOT/'tools/research/initial_allin_targets_v1.py', ROOT/'tools/research/preflop_allin_matrix_v1.py'):
        inputs[str(path)] = sha(path)
    batches = []
    for g in GENERATIONS:
        metrics_path = store/f'iteration-{g+1:04d}'/'metrics.json'
        assert audit['steps'][g]['iteration'] == g+1
        assert sha(metrics_path) == audit['steps'][g]['metrics_sha256']
        metrics = admit(metrics_path)
        assert metrics['iteration'] == g+1 and len(metrics['subbatches']) == 8
        for sub in metrics['subbatches']:
            assert sub['used_model']['generation'] == g
            folder = metrics_path.parent/f"batch-{sub['chunk']:02d}"
            for name, h in sub['artifacts'].items():
                path = folder/name; assert sha(path) == h; inputs[str(path)] = h
            batches.append((g, folder))
    save(rp, dict(inputs=inputs, generations=list(GENERATIONS), batches=len(batches), maximum_seconds=600,
        scope='Post-hoc target-noise diagnostic on old immutable training traces. No current-candidate reads, inference, model choice, native execution or training changes.',
        production_modified=False, gpu_used=False))
    output = {}; maximum = 0.; touched = dict(bb_roots=0, btn_first_responses=0)
    for g in GENERATIONS:
        root = np.zeros((169, 4)); calls = np.zeros(169)
        for row, policy in zip(catalog, generations[g]):
            if row['player'] == 0: root[row['hand_class']] = policy
            else: calls[row['hand_class']] = policy[1]
        exact = matrix.evaluate(root, calls)
        jam_values = exact['bb_jam_entries']/exact['bb_entries']
        old_bb, new_bb, old_btn, new_btn = [], [], [], []
        for _, folder in [x for x in batches if x[0] == g]:
            guard()
            batch, queries, policy_doc, updates = [read(folder/f'{k}.json') for k in ('batch', 'queries', 'policies', 'updates')]
            assert queries['context_source'] == source and policy_doc['context_source'] == source
            assert updates['policies_frozen_across_updater_passes']
            obs = queries['observations']; records = updates['records']
            heads = [i for i, r in enumerate(records) if obs[r[0]]['phase'] == 0 and int(obs[r[0]]['hi']) == 1]
            assert len(heads) == len(updates['roots']) == 2*len(batch['deals']) and heads[0] == 0
            for index, (deal_id, updater, value) in enumerate(updates['roots']):
                assert (deal_id, updater) == divmod(index, 2)
                group = records[heads[index]:(heads[index+1] if index+1 < len(heads) else len(records))]
                assert all(r[1] == updater for r in group)
                deal = batch['deals'][deal_id]; bc, tc = hand_class(deal[:2]), hand_class(deal[2:4])
                qi, _, tag, regret = group[0]
                observed_root = np.asarray(policy_doc['policies'][qi]['probabilities'])
                maximum = max(maximum, float(np.max(abs(observed_root-root[bc]))))
                if updater == 0:
                    assert tag == 4
                    old = np.asarray(regret)
                    maximum = max(maximum, abs(old@observed_root), abs(old[0]+value-matrix.bb_fold))
                    _, delta = bb_correction(observed_root, old[3]+value, jam_values[bc])
                    corrected = old+delta
                    maximum = max(maximum, abs(corrected@observed_root))
                    old_bb.append(old); new_bb.append(corrected); touched['bb_roots'] += 1
                else:
                    assert tag == -4
                    responses = [r for r in group if obs[r[0]]['phase'] == 0 and int(obs[r[0]]['hi']) == 13 and r[2] == 2]
                    assert len(responses) <= 1
                    for qi, actor, _, regret in responses:
                        assert actor == 1 and len(group) == 2
                        p = np.asarray(policy_doc['policies'][qi]['probabilities'])[:2]
                        maximum = max(maximum, abs(p[1]-calls[tc]), abs(np.asarray(regret)[:2]@p), abs(regret[0]+value-matrix.btn_fold))
                        _, corrected = btn_targets(p[1], matrix.btn_fold, exact['btn_call_entries'][tc], exact['btn_jam_mass'][tc])
                        maximum = max(maximum, abs(corrected@p))
                        old_btn.append(regret[:2]); new_btn.append(corrected); touched['btn_first_responses'] += 1
        assert len(old_bb) == 512
        output[str(g)] = dict(bb=statistics(old_bb, new_bb), btn=statistics(old_btn, new_btn) if len(old_btn)>1 else dict(observations=len(old_btn), insufficient=True))
    assert maximum < 1e-9, maximum
    for p, h in inputs.items(): assert sha(p) == h, p
    guard()
    result = dict(passed=True, registration_sha256=sha(rp), generations=output, processed=touched,
        maximum_policy_or_centering_error_bb=maximum, seconds=time.monotonic()-started,
        production_modified=False, gpu_used=False, accuracy_qualified=False,
        limitation='Finite old-trace diagnosis, not new training or population-variance proof. No records were modified; this does not qualify native integration.')
    save(OUT/f'{PREFIX}-result.json', result)
    print(json.dumps(result))


if __name__ == '__main__': main()
