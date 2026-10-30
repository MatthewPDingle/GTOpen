"""Old-fixture correctness control for direct preflop regret representation."""
import copy
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_physical_checkpoint_v1 import read_object, model_document, uniform_networks
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_batch_model_v1 import predict
from sampled_batch_protocol_v2 import policy_document
from sampled_physical_bank_v1 import histories
from sampled_physical_preflop_table_v1 import build, Table, average

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-preflop-table-control-v1'


def main():
    import torch
    torch.set_num_threads(2); started = time.monotonic()
    def guard():
        assert time.monotonic()-started < 180 and idle(), 'Control deadline or production activity'
        assert psutil.virtual_memory().available >= 20_000_000_000
    guard()
    sourcepath = OUT/'sampled-physical-cached-fit-v1-registration.json'; source = json.loads(sourcepath.read_text())
    for p,h in source['inputs'].items(): assert sha(p) == h,p
    objects = Path(source['objects']); context = Path(source['context']).read_text()
    querypath = Path('S:/GTOpen-research/sampled-physical-gpu-bank-v1/queries.json')
    batchpath = OUT/'sampled-batch-bridge-v2-batch.json'
    refs = [json.loads((objects.parent/f'checkpoint-{i:04d}.json').read_text()) for i in (77,78)]
    checkpoints = [json.loads(read_object(objects,r)) for r in refs]
    assert [c['completed_iterations'] for c in checkpoints] == [77,78]
    paths = [*map(Path,source['inputs']),sourcepath,Path(__file__),
        ROOT/'tools/research/sampled_physical_preflop_table_v1.py',querypath,batchpath,
        ROOT/'target/release/examples/hu_sampled_batch_bridge_v2.exe',
        *[objects/r['file'] for r in refs],
        *[objects/r['file'] for c in checkpoints for r in [*c['reservoirs'],c['next_model']]]]
    reg = dict(inputs={str(p):sha(p) for p in paths},checkpoints=refs,
        fixture=str(querypath),maximum_seconds=180,mean_tolerance_bb=1e-10,policy_tolerance=1e-12,
        scope='Old-fixture CPU correctness only. No new deals, training, held-out outcomes or poker-quality conclusion.',production_modified=False)
    save(OUT/f'{PREFIX}-registration.json',reg)
    queries = json.loads(querypath.read_text()); obs = queries['observations']
    assert queries['context_source'] == context and queries['batch_source'] == batchpath.read_text()
    models = [dict(networks=uniform_networks(),tables=[None,None])]; rows_checked = 0; max_mean_error = 0.
    for checkpoint in checkpoints:
        tables = []
        for player,ref in enumerate(checkpoint['reservoirs']):
            guard(); reservoir = PhysicalReservoir.load(objects/ref['file'],context)
            document = build(reservoir,context); Table(document,context)
            for row in document['rows']:
                mask = (reservoir.keys[:reservoir.size,0] == int(row['hi'])) & (reservoir.keys[:reservoir.size,1] == int(row['lo']))
                assert mask.sum() == row['count']
                raw_mean = reservoir.values[:reservoir.size][mask].mean(0)
                error = float(np.max(np.abs(raw_mean-row['mean_regret'])))
                assert error < reg['mean_tolerance_bb']; max_mean_error = max(max_mean_error,error); rows_checked += 1
            tables.append(document)
        models.append(dict(networks=model_document(objects,checkpoint['next_model'])['networks'],tables=tables))
    cpu_rng = torch.get_rng_state().clone()
    policies = []; neural = []; covered = []
    for model in models:
        guard(); _,p = predict(obs,model['networks'],'cpu'); neural.append(p.copy()); changed = []
        for player,document in enumerate(model['tables']):
            if document is not None:
                p,ids = Table(document,context).apply(obs,p); changed += ids
        post = [i for i,o in enumerate(obs) if o['phase'] != 0]
        assert np.array_equal(p[post],neural[-1][post])
        policies.append(p); covered.append(len(changed))
    weights = np.asarray([[1.,2.,3.],[3.,2.,1.]])
    actual,support = average(queries,models,weights,context_source=context,device='cpu',guard=guard)
    history = histories(obs); expected = np.zeros_like(actual); wrong = np.zeros_like(actual); expected_support = []
    for i,o in enumerate(obs):
        factors = []; wrong_factors = []
        for m in range(len(models)):
            reach = weights[o['actor'],m]; old_reach = reach
            for ancestor,action in history[i]:
                reach *= policies[m][ancestor,action]; old_reach *= neural[m][ancestor,action]
            factors.append(reach); wrong_factors.append(old_reach)
        expected_support.append(sum(factors))
        for target,fs in ((expected,factors),(wrong,wrong_factors)):
            if sum(fs)>0: target[i] = sum(f*p[i] for f,p in zip(fs,policies))/sum(fs)
            else: target[i,:o['n']] = 1/o['n']
    assert np.max(np.abs(expected-actual)) < reg['policy_tolerance']
    assert np.max(np.abs(np.asarray(expected_support)-support)) < reg['policy_tolerance']
    wrong_reach_error = float(np.max(np.abs(wrong-actual)))
    assert wrong_reach_error > 1e-6, 'Fixture must distinguish updating policy from updating its reach'
    # Missing rows preserve the original neural policy, including all postflop.
    empty = copy.deepcopy(models[-1]['tables'][0]); empty['rows'] = []
    untouched,matched = Table(empty,context).apply(obs,neural[-1])
    assert matched == [] and np.array_equal(untouched,neural[-1])
    rejections = []
    for kind in ('future-card','duplicate','bad-menu','wrong-context','bad-count'):
        bad = copy.deepcopy(models[-1]['tables'][0])
        if kind == 'future-card': bad['rows'][0]['lo'] = str(int(bad['rows'][0]['lo']) & ~(63<<12))
        elif kind == 'duplicate': bad['rows'].append(copy.deepcopy(bad['rows'][0]))
        elif kind == 'bad-menu': bad['rows'][0]['n'] = 2 if bad['rows'][0]['n'] != 2 else 4
        elif kind == 'wrong-context': bad['context_sha256'] = '0'*64
        elif kind == 'bad-count': bad['rows'][0]['count'] = 0
        try: Table(bad,context)
        except ValueError: rejections.append(kind)
        else: raise AssertionError(('Invalid table was accepted',kind))
    assert torch.equal(cpu_rng,torch.get_rng_state())
    tables_path = OUT/f'{PREFIX}-models.json'; save(tables_path,models)
    policy_path = OUT/f'{PREFIX}-policies.json'; save(policy_path,policy_document(queries,actual))
    native_path = OUT/f'{PREFIX}-native.json'; guard()
    done = subprocess.run([str(ROOT/'target/release/examples/hu_sampled_batch_bridge_v2.exe'),'verify',
        source['context'],str(batchpath),str(policy_path),str(native_path)],cwd=ROOT,capture_output=True,
        text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    assert done.returncode == 0,done.stderr[-2000:]
    native = json.loads(native_path.read_text()); assert native['maximum_reference_error'] == 0
    assert native['verified_traversals'] == 2*len(json.loads(batchpath.read_text())['deals'])
    for p,h in reg['inputs'].items(): assert sha(p) == h,p
    guard()
    result = dict(passed=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        mean_rows_checked=rows_checked,maximum_mean_error_bb=max_mean_error,
        query_observations=len(obs),matched_rows_per_model=covered,postflop_per_model_unchanged=True,
        maximum_average_error=float(np.max(np.abs(expected-actual))),
        maximum_support_error=float(np.max(np.abs(np.asarray(expected_support)-support))),
        incorrect_unmodified_reach_error=wrong_reach_error,missing_rows_preserve_neural=True,
        invalid_documents_rejected=rejections,verified_traversals=native['verified_traversals'],
        native_reference_error=native['maximum_reference_error'],cpu_rng_unchanged=True,
        artifacts={str(p):sha(p) for p in (tables_path,policy_path,native_path)},seconds=time.monotonic()-started,
        scope=reg['scope'],production_modified=False,accuracy_qualified=False)
    save(OUT/f'{PREFIX}-result.json',result); print(json.dumps(result))


if __name__ == '__main__': main()
