"""Read back immutable multi-depth control evidence; no fitting or GPU use."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  PYTHONDONTWRITEBYTECODE='1')
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from stack_context_inputs_v1 import Registry
from board_prefix_publication_v1 import atomic_json

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
STORE = Path('S:/GTOpen-research/stack-context-model-control-v1')
GEOMETRY = Path('S:/GTOpen-research/stack-geometry-control-v1')
RESULT = OUT/'stack-context-model-control-v1-readback-v1.json'

def read(p): return json.loads(Path(p).read_bytes())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(d): return (json.dumps(d, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()

def public_reference(row):
    """Independent scalar ledger-to-input calculation, then float32 rounding."""
    a = row['actor']; b = 1-a
    s, i, r = (row[k] for k in ('starting_stacks', 'invested', 'remaining'))
    p, c = row['pot'], row['call_cost']
    log = lambda x: math.log1p(x)/math.log(1001)
    values = [float(row['phase'] == t) for t in range(4)]
    money = [s[a], s[b], r[a], r[b], i[a], i[b], p, c, row['dead_money'],
             min(s), min(r), min(r)/p, min(r[a]-c, r[b])/(p+c)]
    values += list(map(log, money)) + [c/(p+c), row['rake_fraction'], log(row['rake_cap'])]
    for j in range(4):
        if j >= len(row['actions']):
            values += [0.]*10
            continue
        action = row['actions'][j]; k = action['kind']; amount = action['increment']
        if k == 'jam': k = 'raise'
        values += [1.] + [float(k == t) for t in ('fold','check','call','bet','raise')]
        values += [float(action['all_in']), log(amount), amount/(p+amount), amount/r[a] if r[a] else 0.]
    return np.asarray(values, dtype=np.float32)

def main():
    assert not RESULT.exists(), 'Preserve completed evidence'
    rp = OUT/'stack-context-model-control-v1-registration.json'
    result_path = OUT/'stack-context-model-control-v1-result.json'
    reg, result = read(rp), read(result_path)
    assert result['passed'] and result['complete'] and result['registration_sha256'] == sha(rp)
    checked = {}
    def check(p, h):
        assert sha(p) == h, p
        checked[str(p)] = h
    check(rp, sha(rp)); check(result_path, sha(result_path))
    for p,h in reg['inputs'].items(): check(p,h)
    for p,h in result['artifacts'].items(): check(p,h)
    assert hashlib.sha256(canonical(reg['registry'])).hexdigest() == result['registry_sha256']
    entries = []
    for r in result['contexts']:
        depth = r['stack']; source = (GEOMETRY/'fixtures'/f'stack-{depth}-context.json').read_text()
        assert hashlib.sha256(source.encode()).hexdigest() == r['context_sha256']
        ledger = read(GEOMETRY/f'stack-{depth}-public.json')
        entries.append(dict(name=f'{depth}bb', split=r['split'], context_source=source, public_document=ledger))
    registry = Registry(entries)
    assert registry.manifest == reg['registry'] and registry.sha256 == result['registry_sha256']
    keys = []; old = []; links = 0; feature_error = 0.; root_error = 0.; count = 0
    documents = []
    for ref in result['model_objects']:
        p = STORE/'objects'/ref['file']; check(p, ref['sha256']); d = read(p)
        assert d['generation'] == ref['generation'] and d['registry'] == reg['registry']
        assert set(d['preflop_tables']) == set(registry.fit_contexts)
        documents.append(d)
    for entry, record in zip(entries, result['contexts']):
        q = read(STORE/f"stack-{record['stack']}-queries.json")
        assert q['batch_source'] == (STORE/'retained-deals.json').read_text()
        prepared = registry.prepare(q, context_sha256=record['context_sha256'])
        rows = {r['hi']:r for r in entry['public_document']['public_states']}
        assert set(rows) == {o['hi'] for o in q['observations']}
        assert len(q['observations']) == record['observations'] and len(rows) == record['public_states']
        local_links = sum(len(o['own_history']) for o in q['observations'])
        assert local_links == record['own_history_links']; links += local_links
        for o, x in zip(q['observations'], prepared['features']):
            feature_error = max(feature_error, float(np.max(abs(x[302:]-public_reference(rows[o['hi']])))))
            count += 1; old.append((o['hi'],o['lo']))
        keys.extend(prepared['keys'])
        idx = next(j for j,o in enumerate(q['observations']) if o['hi']=='1')
        o = q['observations'][idx]; x = prepared['features'][idx].astype(np.float64)
        net = documents[1]['networks'][o['actor']]
        for layer, (width, prev) in enumerate(((64,362),(64,64),(4,64))):
            w = np.asarray(net[f'w{layer}'], dtype=np.float32).astype(np.float64).reshape(width,prev)
            b = np.asarray(net[f'b{layer}'], dtype=np.float32).astype(np.float64)
            x = w@x+b
            if layer<2: x=np.maximum(x,0)
        table = documents[1]['preflop_tables'].get(record['context_sha256'], [None,None])[o['actor']]
        if table:
            match = [r for r in table['rows'] if (r['hi'],r['lo'])==(o['hi'],o['lo'])]
            if match: x=np.asarray(match[0]['mean_regret'])
        p = np.maximum(x,0); p[o['n']:] = 0
        if p.sum(): p /= p.sum()
        else: p[np.argmax(x[:o['n']])] = 1
        root_error = max(root_error, float(np.max(abs(p-result['synthetic_root_policies'][str(record['stack'])]))))
    assert len(keys)==len(set(keys)) and len(old)-len(set(old))==result['original_key_collisions_across_contexts']
    assert feature_error<1e-7 and root_error<1e-12
    assert count==5028 and links==17724
    assert not result['accuracy_claim'] and not result['training_checkpoint_implemented']
    atomic_json(RESULT, dict(passed=True, source_sha256=sha(__file__), inputs=checked,
        verified_files=len(checked), contexts=7, observations=count, own_history_links=links,
        public_features_scalar_recompute_max_error=feature_error,
        synthetic_root_policy_recompute_max_error=root_error,
        original_key_collisions=3996, namespaced_keys_unique=True,
        native_deals_reused=2, new_training_deals=0, new_evaluation_deals=0,
        gpu_used=False, fitted_poker_models=0, accuracy_claim=False, production_modified=False))
    print(json.dumps({k:v for k,v in read(RESULT).items() if k!='inputs'}), flush=True)

if __name__=='__main__': main()
