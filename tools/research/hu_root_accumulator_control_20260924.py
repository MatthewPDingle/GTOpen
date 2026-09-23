"""CPU replay/control for the separate all-samples BB root accumulator."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import copy
import hashlib
import json
import math
from pathlib import Path
import time
import numpy as np
import psutil
from reboot_research_idle_v1 import idle
from sampled_root_regret_accumulator_v1 import SampledRootRegrets
from sampled_root_policy_table_v1 import SampledRootTable, document
from sampled_physical_preflop_table_v1 import Table

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
STORE = Path('T:/GTOpen-research/exact-initial-fresh-pilot-v1')
PREFIX = 'sampled-root-accumulator-control-v1'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_bytes())


def save(p, value):
    with Path(p).open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, separators=(',', ':'), allow_nan=False)+'\n')


def main():
    start = time.monotonic()
    def guard():
        assert time.monotonic()-start < 600 and idle()
        assert psutil.virtual_memory().available >= 20_000_000_000
    guard()
    rp = OUT/(PREFIX+'-registration.json'); resultp = OUT/(PREFIX+'-result.json')
    assert not rp.exists() and not resultp.exists()
    source = read(OUT/'exact-initial-root-retention-diagnostic-v1-registration.json')
    assert all(sha(p) == h for p,h in source['inputs'].items())
    inputs = dict(source['inputs'])
    diagnosticp = OUT/'exact-initial-root-retention-diagnostic-v1-result.json'
    diagnostic = read(diagnosticp)
    assert diagnostic['passed'] and diagnostic['registration_sha256'] == sha(OUT/'exact-initial-root-retention-diagnostic-v1-registration.json')
    contextp = OUT/'bb-context-candidate.json'
    catalogp = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    assert sha(contextp) == '8e79a4666487873e1f3e9626a6c0fc952879b24b2bdcd54cd125860787e8432d'
    assert sha(catalogp) == '57834fc6b59173f22b5027bcec1f32e649060463fd275bc80fb7a58a4cfc6629'
    for p in [Path(__file__), diagnosticp, contextp, catalogp,
              OUT/'exact-initial-root-retention-diagnostic-v1-registration.json',
              *[ROOT/'tools/research'/s for s in ['sampled_root_regret_accumulator_v1.py',
                'sampled_root_policy_table_v1.py', 'sampled_physical_preflop_table_v1.py']]]:
        inputs[str(p)] = sha(p)
    queryp = STORE/'iteration-0078/batch-00/queries.json'
    m = read(STORE/'iteration-0078/metrics.json')
    assert sha(queryp) == m['subbatches'][0]['artifacts']['queries']
    inputs[str(queryp)] = sha(queryp)
    save(rp, dict(inputs=inputs, gpu_used=False, maximum_seconds=600,
        scope='Replay 78 recorded generations; independent fsum reference, serialized resume each boundary, policy override isolation, and malformed-state rejection. No new model training or poker strength claim.'))
    context = contextp.read_text(); catalog = catalogp.read_text()
    matrixhash = 'ff61c30a7948470bbdeee289601d0cb894b29b5ac246194d2e06e44fc801e885'
    state = SampledRootRegrets(sha(contextp), matrixhash)
    args = dict(context_sha256=sha(contextp), matrix_sha256=matrixhash)
    fallback = np.tile([.1, .2, .3, .4], (169,1))
    assert np.array_equal(state.probabilities(fallback), fallback)
    observed = [x['observation'] for x in json.loads(catalog)['native_observations']]
    initial = SampledRootTable(document(state, context_source=context, catalog_source=catalog),
        context, catalog, matrix_sha256=matrixhash)
    given = np.zeros((len(observed),4))
    for i,o in enumerate(observed):
        given[i,:o['n']] = 1./o['n']
    got,matched = initial.apply(observed,given)
    assert matched == [] and np.array_equal(got,given)
    samples = [[] for _ in range(169)]
    maximum_sum_error = 0.; maximum_policy_error = 0.; rejected = []
    def rejects(name, fn):
        try:
            fn()
        except (ValueError, KeyError, TypeError):
            rejected.append(name)
        else:
            raise AssertionError('Did not reject '+name)
    for iteration in range(1,79):
        guard()
        audits = [read(STORE/f'iteration-{iteration:04d}'/f'batch-{b:02d}'/'derived-targets.json') for b in range(8)]
        if iteration == 1:
            original = state.document()
            rejects('incomplete-generation', lambda: state.step(1,audits[:-1],expected_deals=512,expected_batches=8))
            bad = copy.deepcopy(audits);bad[1]=copy.deepcopy(bad[0])
            rejects('duplicate-subbatch', lambda: state.step(1,bad,expected_deals=512,expected_batches=8))
            bad = copy.deepcopy(audits);bad[-1]['identity']['current_initial_policy_sha256']='0'*64
            rejects('mixed-played-policy', lambda: state.step(1,bad,expected_deals=512,expected_batches=8))
            bad = copy.deepcopy(audits);bad[-1]['bb_root_corrections'][-1]['advantages'][0]=float('nan')
            rejects('nonfinite-final-target', lambda: state.step(1,bad,expected_deals=512,expected_batches=8))
            assert state.document() == original, 'Rejected updates must be atomic'
        state.step(iteration, audits, expected_deals=512, expected_batches=8)
        for a in audits:
            for r in a['bb_root_corrections']:
                samples[r['hand_class']].append(r['advantages'])
        sums = np.array([[math.fsum(r[a] for r in samples[c]) for a in range(4)] for c in range(169)])
        assert np.array_equal(state.counts, [len(s) for s in samples])
        error = float(np.max(abs(sums-state.regrets)))
        maximum_sum_error = max(maximum_sum_error,error)
        assert error < 1e-9
        expected = fallback.copy()
        for c,rows in enumerate(samples):
            if not rows:
                continue
            positive = [max(float(v),0.) for v in sums[c]]; total = math.fsum(positive)
            expected[c] = [v/total for v in positive] if total > 0 else [float(i==max(range(4),key=lambda k:sums[c,k])) for i in range(4)]
        error = float(np.max(abs(expected-state.probabilities(fallback))))
        maximum_policy_error = max(maximum_policy_error,error)
        assert error < 1e-10
        # JSON roundtrip at every boundary is the state needed by checkpoint resume.
        value = json.loads(json.dumps(state.document(),allow_nan=False))
        restored = SampledRootRegrets.restore(value, **args)
        assert restored.document() == state.document()
        state = restored
    assert int(state.counts.sum()) == 39936 and state.steps == 78
    rejects('repeat-completed-generation',lambda:state.step(78,audits,expected_deals=512,expected_batches=8))
    rejects('changed-context',lambda:SampledRootRegrets.restore(state.document(),context_sha256='0'*64,matrix_sha256=matrixhash))
    bad = copy.deepcopy(state.document());bad['sample_counts'][0]=-1
    rejects('negative-count',lambda:SampledRootRegrets.restore(bad,**args))
    bad = copy.deepcopy(state.document());bad['sample_counts'][0]=0;bad['regret_sums'][0]=[1.,0.,0.,0.]
    rejects('regret-without-sample',lambda:SampledRootRegrets.restore(bad,**args))
    value = document(state,context_source=context,catalog_source=catalog)
    table = SampledRootTable(value,context,catalog,matrix_sha256=matrixhash)
    got, matched = table.apply(observed,given)
    assert len(matched) == 169
    for i,item in enumerate(json.loads(catalog)['native_observations']):
        if item['player'] == 0:
            assert np.max(abs(got[i]-expected[item['hand_class']])) < 1e-10
        else:
            assert np.array_equal(got[i],given[i])
    bad = copy.deepcopy(observed);bad[0]['own_history']=[[0,1]]
    rejects('root-own-history',lambda:table.apply(bad,given))
    bad = copy.deepcopy(observed);bad[0]['active_features'][0]=13
    rejects('root-feature-mismatch',lambda:table.apply(bad,given))
    rejects('legacy-retained-table-reader',lambda:Table(value,context))
    model = read(STORE/'objects'/m['next_model']['file'])
    base = Table(model['base_model']['preflop_tables'][0],context)
    combined = table.compose(base)
    raw = read(queryp)['observations']
    for o in raw:
        if int(o['hi']) == 1:
            o['own_history'] = []
    given = np.zeros((len(raw),4))
    for i,o in enumerate(raw):
        given[i,:o['n']] = 1./o['n']
    before,_ = base.apply(raw,given);after,_ = combined.apply(raw,given)
    nonroot = [i for i,o in enumerate(raw) if int(o['hi']) != 1]
    assert np.array_equal(before[nonroot],after[nonroot])
    finalreference = np.array([x['full_policy'] for x in diagnostic['final_unplayed_classes']])
    assert np.max(abs(finalreference-state.probabilities(fallback))) < 1e-10
    for p,h in inputs.items():
        assert sha(p)==h,p
    out = dict(passed=True,registration_sha256=sha(rp),generations=78,root_samples=39936,
        serialized_resume_boundaries=78,maximum_scalar_sum_error=maximum_sum_error,
        maximum_scalar_policy_error=maximum_policy_error,nonroot_rows_unchanged=len(nonroot),
        rejected_cases=rejected,state_payload_bytes=state.counts.nbytes+state.regrets.nbytes,
        gpu_used=False,production_modified=False,accuracy_qualified=False,
        seconds=time.monotonic()-start,scope='Accumulator and override controls only. No joint trainer integration or fresh quality evaluation yet.')
    save(resultp,out);print(json.dumps(out))


if __name__ == '__main__':
    main()
