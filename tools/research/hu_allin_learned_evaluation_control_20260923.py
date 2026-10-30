"""CPU-only trained-bank variance diagnostic on previously registered fixtures.

No training, new held-out deals, responder fitting or policy selection.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['OMP_NUM_THREADS'] = '2'
import copy
import json
from pathlib import Path
import subprocess
import time

import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_cuda_v1 import ROOT, sha, save, batch_values
from sampled_physical_hybrid_checkpoint_v1 import read_object, model_document, verify_bank
from sampled_physical_hybrid_cpu64_v1 import HybridCpuBank64
from sampled_allin_protocol_v3 import AllinCache
from hu_allin_evaluation_control_20260923 import correction

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-allin-learned-evaluation-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
FIXTURE = 'sampled-physical-allin-evaluation-control-v1'


def main():
    started = time.monotonic()
    def guard():
        assert idle() and time.monotonic()-started < 900
        assert psutil.virtual_memory().available > 20_000_000_000
        assert psutil.disk_usage(str(STORE.parent)).free > 40_000_000_000
    guard()
    fixture_review = OUT/f'{FIXTURE}-independent-review.json'
    fixture_result = OUT/f'{FIXTURE}-result.json'
    reviewed = json.loads(fixture_review.read_text())
    assert reviewed['passed'] and reviewed['source_result_sha256'] == sha(fixture_result)
    fixtures = json.loads(fixture_result.read_text())
    for p, h in fixtures['artifacts'].items(): assert sha(p) == h, p
    precision_reg = OUT/'sampled-physical-hybrid-precision-control-v1-registration.json'
    precision_result = OUT/'sampled-physical-hybrid-precision-control-v1-result.json'
    precision = json.loads(precision_result.read_text())
    assert precision['passed'] and precision['registration_sha256'] == sha(precision_reg)
    oldreg_path = OUT/'sampled-physical-hybrid-evaluation-v1-registration.json'
    oldreg = json.loads(oldreg_path.read_text())
    for p, h in oldreg['inputs'].items(): assert sha(p) == h, p
    objects = Path(oldreg['objects']); context_path = Path(oldreg['context'])
    context_source = context_path.read_text(); context = json.loads(context_source)
    checkpoint = json.loads(read_object(objects, oldreg['checkpoint']))
    verify_bank(objects, 78, checkpoint['played_bank'], checkpoint['next_model'], context_source=context_source)
    models = [model_document(objects, r, context_source=context_source) for r in checkpoint['played_bank']]
    cache_review = OUT/'sampled-physical-allin-training-cache-v1-independent-review.json'
    cache = AllinCache.from_review(cache_review)
    exe = ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    sources = [Path(__file__), fixture_review, fixture_result, precision_reg, precision_result,
               oldreg_path, context_path, cache_review, exe,
               ROOT/'target/release/examples/hu_sampled_bank_bridge.exe',
               ROOT/'target/release/examples/hu_sampled_profile_evaluation.exe']
    sources.extend(ROOT/'tools/research'/n for n in (
        'sampled_physical_hybrid_checkpoint_v1.py','sampled_physical_hybrid_cpu64_v1.py',
        'sampled_physical_root_evaluation_cuda_v1.py','sampled_allin_protocol_v3.py',
        'hu_allin_evaluation_control_20260923.py','hu_sampled_physical_dense_btn_jam_diagnosis_20260923.py'))
    reg = dict(inputs={str(p):sha(p) for p in sources}, checkpoint=oldreg['checkpoint'],
               generations=list(range(78)), fixture_result_sha256=sha(fixture_result),
               replicates=16, private_pairs=16, device='cpu', precision='float64',
               scope='Fixed complete hybrid played bank on 16 old training private pairs, each with 16 already registered diagnostic runouts. Compare paired root-deviation variance with sampled versus exact preflop-all-in outcomes. Diagnostic only: no fresh population accuracy, new training, fitted responder, promotion or active-protocol change.',
               production_modified=False)
    regpath = OUT/f'{PREFIX}-registration.json'
    assert not STORE.exists(); save(regpath, reg); STORE.mkdir()
    bank = HybridCpuBank64(models, context_source=context_source)
    error = None; records = []; artifacts = {}; maximum_error = 0.
    try:
        for rep in range(16):
            guard(); folder = STORE/f'runout-{rep:02d}'
            source = Path('S:/GTOpen-research')/FIXTURE/f'runout-{rep:02d}/batch-2.json'
            batch = json.loads(source.read_text())
            summary = batch_values(context_path, batch, objects, checkpoint, folder, guard, bank)
            profile = json.loads((folder/'profiles.json').read_text())
            labelled = cache.batch(batch); labelled_path = folder/'conditional-batch.json'; save(labelled_path, labelled)
            conditional_profile = copy.deepcopy(profile)
            conditional_profile['batch_source'] = labelled_path.read_text()
            profile_path = folder/'conditional-profiles.json'; save(profile_path, conditional_profile)
            native_path = folder/'conditional-native.json'
            guard()
            run = subprocess.run([str(exe),str(context_path),str(labelled_path),str(profile_path),str(native_path)],
                                 cwd=ROOT,capture_output=True,text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
            assert run.returncode == 0, run.stderr[-2000:]
            original = json.loads((folder/'native.json').read_text())
            conditional = json.loads(native_path.read_text())
            assert len(original['profiles']) == len(conditional['profiles']) == 5
            values = []
            for policy, old, new in zip(profile['profiles'], original['profiles'], conditional['profiles']):
                assert policy['name'] == old['name'] == new['name']
                assert len(old['deals']) == len(new['deals']) == 16
                values.append([d['values'][0] for d in new['deals']])
                for i, deal in enumerate(batch['deals']):
                    label = labelled['allin_counts'][i]
                    equity = (label['wins']+.5*label['ties'])/label['boards']
                    delta, mass = correction(context, deal, policy['policies'], equity)
                    a, b = old['deals'][i], new['deals'][i]
                    discrepancy = float(np.max(np.abs(np.array(a['values'])+delta-b['values'])))
                    maximum_error = max(maximum_error, discrepancy)
                    assert discrepancy < 1e-9
                    assert a['expected_rake'] == b['expected_rake'] and a['terminal_mass'] == b['terminal_mass']
                    records.append(dict(replicate=rep,pair=i,profile=policy['name'],
                                        original=a['values'],conditional=b['values'],allin_mass=mass))
            values = np.array(values)
            assert np.max(np.abs(np.sum(np.array(summary['root_probabilities'])*values[1:].T,axis=1)-values[0])) < 1e-9
            artifacts.update({str(p):sha(p) for p in folder.iterdir() if p.is_file()})
            print(json.dumps(dict(replicate=rep,seconds=time.monotonic()-started)),flush=True)
        # Compare uncertainty of the actual paired root differences, not just
        # standalone payoff variance. No choosing whichever action looks best.
        bykey = {(r['replicate'],r['pair'],r['profile']):r for r in records}
        variance = []
        for name in ('baseline','action-0','action-1','action-2','action-3'):
            before = after = 0.
            means_before = []; means_after = []
            for pair in range(16):
                v = []
                for rep in range(16):
                    row = bykey[rep,pair,name]; base = bykey[rep,pair,'baseline']
                    v.append([row[k][0]-(base[k][0] if name != 'baseline' else 0.) for k in ('original','conditional')])
                a = np.array(v); before += float(a[:,0].var(ddof=1)); after += float(a[:,1].var(ddof=1))
                means_before.append(float(a[:,0].mean())); means_after.append(float(a[:,1].mean()))
            variance.append(dict(profile=name,quantity='payoff' if name=='baseline' else 'paired gain versus baseline',
                summed_within_pair_variance_original=before,summed_within_pair_variance_conditional=after,
                ratio=after/before if before else None,diagnostic_mean_original=float(np.mean(means_before)),
                diagnostic_mean_conditional=float(np.mean(means_after))))
        for p,h in reg['inputs'].items(): assert sha(p)==h,p
        rows_path = STORE/'rows.json'; save(rows_path,records); artifacts[str(rows_path)] = sha(rows_path)
        result = dict(passed=True,registration_sha256=sha(regpath),profile_deals=len(records),
                      maximum_correction_error_bb=maximum_error,variance=variance,artifacts=artifacts,
                      seconds=time.monotonic()-started,scope=reg['scope'],production_modified=False)
        save(OUT/f'{PREFIX}-result.json',result)
        print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}),flush=True)
    except Exception as exc:
        error=str(exc);raise
    finally:
        save(OUT/f'{PREFIX}-status.json',dict(state='complete' if error is None else 'stopped',error=error,
             seconds=time.monotonic()-started,production_modified=False))


if __name__ == '__main__':
    main()
