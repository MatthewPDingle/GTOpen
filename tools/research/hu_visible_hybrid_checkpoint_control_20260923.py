"""Synthetic round-trip/continuation checks, not new poker training."""
import copy
import json
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_reservoir_v1 import PhysicalReservoir, ingest
from sampled_physical_preflop_table_v1 import build, Table
import sampled_physical_checkpoint_v1 as old
import sampled_physical_hybrid_checkpoint_v1 as prior_hybrid
import sampled_visible_hybrid_checkpoint_v1 as hybrid
from sampled_visible_hybrid_policy_v1 import predict
from sampled_visible_initialization_v1 import features

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-visible-hybrid-checkpoint-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX


def main():
    started = time.monotonic()
    def guard():
        assert time.monotonic()-started < 120 and idle()
        assert psutil.virtual_memory().available >= 20_000_000_000
    guard(); assert not STORE.exists()
    prereg = OUT/'sampled-physical-preflop-table-control-v1-registration.json'
    prereq = OUT/'sampled-physical-preflop-table-control-v1-result.json'
    result = json.loads(prereq.read_text()); reg = json.loads(prereg.read_text())
    assert result['passed'] and result['registration_sha256'] == sha(prereg)
    paths = [*map(Path,reg['inputs']),*map(Path,result['artifacts']),prereg,prereq,Path(__file__),
        *[ROOT/'tools/research'/n for n in ('sampled_visible_hybrid_checkpoint_v1.py','sampled_visible_hybrid_policy_v1.py','sampled_visible_initialization_v1.py','sampled_visible_poker_features_v1.py')]]
    registration = dict(inputs={str(p):sha(p) for p in paths},maximum_seconds=120,
        scope='Synthetic serialization/continuation control using old fixture updates and fixed networks. No new training or poker strength evaluation.',production_modified=False)
    for p,h in {**reg['inputs'],**result['artifacts']}.items(): assert sha(p) == h,p
    save(OUT/f'{PREFIX}-registration.json',registration)
    queries = json.loads(Path(reg['fixture']).read_text()); context = queries['context_source']
    updates = json.loads((OUT/'sampled-physical-preflop-table-control-v1-native.json').read_text())
    fixture_models = json.loads((OUT/'sampled-physical-preflop-table-control-v1-models.json').read_text())
    STORE.mkdir(); directory = STORE/'objects'; directory.mkdir()
    config = dict(control=True,policy_type=hybrid.POLICY_TYPE,reservoir_capacity=64,architecture=[302,64,64,4],representation=hybrid.FEATURE_SPEC)
    sampler = PhysicalDeals(context,mode='full_deck',seed=61231)
    rng = np.random.Generator(np.random.PCG64(61232))
    reservoirs = [PhysicalReservoir(64,p,61233+p,context) for p in (0,1)]
    initial = hybrid.write_model(directory,0,hybrid.uniform_networks(),[1.,1.],[None,None],context_source=context)
    zero = hybrid.save_checkpoint(directory,completed=0,context_source=context,config=config,
        sampler=sampler,action_rng=rng,reservoirs=reservoirs,bank=[],current=initial)
    zero_restored = hybrid.restore_checkpoint(directory,zero,context_source=context,config=config)
    assert zero_restored['completed_iterations'] == 0 and zero_restored['played_bank'] == []
    sampler.sample(16); rng.integers(0,2**63,size=16)
    ingest(queries,updates,reservoirs,1)
    tables = [build(r,context) for r in reservoirs]
    # Explicit control fixture: preserve existing scores by appending zero columns.
    # This is not an automatic old-checkpoint migration or a trained candidate.
    networks = copy.deepcopy(fixture_models[-1]['networks'])
    for net in networks:
        w = np.asarray(net['w0']).reshape(64,269)
        net['w0'] = np.pad(w,((0,0),(0,33))).ravel().tolist()
    current = hybrid.write_model(directory,1,networks,[1.,1.],tables,context_source=context)
    checkpoint = hybrid.save_checkpoint(directory,completed=1,context_source=context,config=config,
        sampler=sampler,action_rng=rng,reservoirs=reservoirs,bank=[initial],current=current)
    restored = hybrid.restore_checkpoint(directory,checkpoint,context_source=context,config=config)
    assert restored['next_model_document']['preflop_tables'] == tables
    assert restored['played_bank'] == [initial] and restored['next_model'] == current
    for original,loaded in zip(reservoirs,restored['reservoirs']):
        assert original.summary() == loaded.summary() and original.rng.bit_generator.state == loaded.rng.bit_generator.state
        for name in ('keys','active','arity','values','iterations'):
            assert np.array_equal(getattr(original,name),getattr(loaded,name)),name
    # Advance both copies through the same old fixture updates. Sampler/action
    # draws test saved RNG state only; they do not generate new outcome labels.
    assert sampler.sample(8) == restored['sampler'].sample(8)
    assert np.array_equal(rng.integers(0,2**63,size=32),restored['action_rng'].integers(0,2**63,size=32))
    ingest(queries,updates,reservoirs,2); ingest(queries,updates,restored['reservoirs'],2)
    next_tables = [build(r,context) for r in reservoirs]
    assert next_tables == [build(r,context) for r in restored['reservoirs']]
    next_model = hybrid.write_model(directory,2,networks,[1.,1.],next_tables,context_source=context)
    def save_next(rs,stream,actions):
        return hybrid.save_checkpoint(directory,completed=2,context_source=context,config=config,
            sampler=stream,action_rng=actions,reservoirs=rs,bank=[initial,current],current=next_model)
    first = save_next(reservoirs,sampler,rng)
    second = save_next(restored['reservoirs'],restored['sampler'],restored['action_rng'])
    assert first == second
    # Verify inference uses only visible observations, and preflop overrides survive.
    import torch
    torch.set_num_threads(2)
    doc = hybrid.model_document(directory,current,context_source=context)
    state = torch.random.get_rng_state().clone()
    scores,probabilities,covered = predict(queries,doc,'cpu')
    assert torch.equal(state,torch.random.get_rng_state()) and sum(covered)>0
    visible = features(queries['observations'])
    for player in (0,1):
        ids = [i for i,o in enumerate(queries['observations']) if o['actor']==player]
        y = visible[ids].astype(np.float64)
        for layer,shape in enumerate(((64,302),(64,64),(4,64))):
            w = np.asarray(networks[player][f'w{layer}'],np.float32).astype(np.float64).reshape(shape)
            b = np.asarray(networks[player][f'b{layer}'],np.float32).astype(np.float64)
            y = y@w.T+b
            if layer<2:y=np.maximum(y,0)
        assert np.max(abs(y-scores[ids]))<1e-5
    for t in tables:
        table = Table(t,context)
        for i,o in enumerate(queries['observations']):
            if o['phase']==0 and o['actor']==t['player']:
                key=(int(o['hi']),int(o['lo']))
                if key in table.rows:assert np.array_equal(probabilities[i],table.rows[key][2])
    changed = dict(queries,batch_source='unread hidden-label sentinel')
    assert np.array_equal(predict(changed,doc,'cpu')[1],probabilities)
    rejections = []
    def reject(name,fn):
        try: fn()
        except ValueError: rejections.append(name)
        else: raise AssertionError(('Invalid state accepted',name))
    reject('269-input-hybrid-reader',lambda:prior_hybrid.model_document(directory,current,context_source=context))
    reject('legacy-reader-hybrid-model',lambda:old.model_document(directory,current))
    reject('legacy-reader-hybrid-checkpoint',lambda:old.restore_checkpoint(directory,checkpoint,context_source=context,config=config))
    legacy = old.write_model(directory,0,old.uniform_networks(),[1.,1.])
    reject('hybrid-reader-legacy-model',lambda:hybrid.model_document(directory,legacy,context_source=context))
    reject('changed-context',lambda:hybrid.model_document(directory,current,context_source=context+' '))
    reject('changed-configuration',lambda:hybrid.restore_checkpoint(directory,checkpoint,context_source=context,config=dict(config,reservoir_capacity=65)))
    reject('unused-model-in-played-bank',lambda:hybrid.verify_bank(directory,1,[current],initial,context_source=context))
    bad = copy.deepcopy(next_tables); bad[0]['rows'][0]['mean_regret'][0] += 1.
    bad_model = hybrid.write_model(directory,2,networks,[1.,1.],bad,context_source=context)
    reject('table-content-reservoir-mismatch',lambda:hybrid.save_checkpoint(directory,completed=2,context_source=context,config=config,
        sampler=sampler,action_rng=rng,reservoirs=reservoirs,bank=[initial,current],current=bad_model))
    bad_meta=copy.deepcopy(doc);bad_meta['representation']['feature_names'].reverse()
    reject('wrong-feature-meaning',lambda:hybrid.validate_model(bad_meta,context))
    bad_width=copy.deepcopy(doc);bad_width['networks'][0]['w0'].pop()
    reject('wrong-input-width',lambda:hybrid.validate_model(bad_width,context))
    reject('old-config-layout',lambda:hybrid.restore_checkpoint(directory,checkpoint,context_source=context,config=dict(config,architecture=[269,64,64,4])))
    reject('changed-object-hash',lambda:hybrid.read_object(directory,dict(checkpoint,sha256='0'*64)))
    guard()
    for p,h in registration['inputs'].items(): assert sha(p) == h,p
    evidence = dict(passed=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        initial_checkpoint=zero,round_trip_checkpoint=checkpoint,continued_checkpoint=first,
        exact_continuation_hash=True,reservoir_arrays_and_rng_exact=True,table_content_exact=True,
        played_bank_excludes_unused_model=True,old_readers_reject_hybrid=True,rejections=rejections,
        artifacts={str(p):sha(p) for p in directory.iterdir() if p.is_file()},seconds=time.monotonic()-started,
        inference_observations=len(queries['observations']),covered_preflop_rows=covered,policy_ignores_hidden_batch_labels=True,
        accuracy_qualified=False,production_modified=False,scope=registration['scope'])
    save(OUT/f'{PREFIX}-result.json',evidence)
    print(json.dumps({k:v for k,v in evidence.items() if k!='artifacts'}))


if __name__ == '__main__': main()
