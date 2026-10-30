"""Native multi-depth input/model checks only; synthetic networks are not poker fits."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import uuid
import numpy as np
import river_matched_training_pilot_v1 as pilot
from stack_context_inputs_v1 import Registry,SPEC,digest
import stack_context_policy_v1 as policy
from sampled_visible_features_bulk_v1 import features as original_features
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from weighted_preflop_table_v1 import build as build_table

ROOT=pilot.ROOT;OUT=pilot.OUT;NAME='stack-context-model-control-v1'
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');STATUS=OUT/(NAME+'-status.json')
STORE=Path('S:/GTOpen-research')/NAME
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
PLAN=OUT/'STACK-CONTEXT-MODEL-CONTRACT.md';EXE=pilot.EXES['query_executable']
DEPTHS=(20,40,60,100,150,200,400);HELDOUT=(60,150)
LIMIT=16_000_000;RESERVE=16_000_000;SECONDS=1200;NETWORK_SEED=9296201


def specification():
    gr=OUT/'stack-geometry-control-v1-registration.json';gp=OUT/'stack-geometry-control-v1-result.json'
    geometry=pilot.read(gp);assert geometry['passed'] and geometry['registration_sha256']==pilot.sha(gr)
    pilot.verify(geometry['artifacts'])
    query_result=OUT/'complete-preflop-query-catalog-control-v3-result.json'
    query_reg=OUT/'complete-preflop-query-catalog-control-v3-registration.json'
    qp=pilot.read(query_result);assert qp['passed'] and qp['registration_sha256']==pilot.sha(query_reg)
    assert pilot.sha(EXE)==pilot.read(query_reg)['inputs'][str(EXE)]
    raw=Path(qp['native_exports'][0]['raw']);assert pilot.sha(raw)==qp['native_exports'][0]['raw_sha256']
    deals=pilot.read(raw)['deals'][:2];assert len(deals)==2
    entries=[];paths=[Path(__file__),PLAN,gr,gp,query_reg,query_result,raw,EXE,
        ROOT/'crates/solver/examples/hu_sampled_bank_bridge.rs',
        ROOT/'crates/solver/examples/research_sampled/observation_v1.rs']
    for depth in DEPTHS:
        context=GEOMETRY/'fixtures'/f'stack-{depth}-context.json';public=GEOMETRY/f'stack-{depth}-public.json'
        assert pilot.sha(context)==geometry['artifacts'][str(context)] and pilot.sha(public)==geometry['artifacts'][str(public)]
        source=context.read_text();assert json.loads(source)['config']['stack']==depth
        entries.append(dict(name=f'{depth}bb',split='heldout' if depth in HELDOUT else 'fit',
                            context_source=source,public_document=pilot.read(public)))
        paths.extend([context,public])
    registry=Registry(entries)
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    inputs={str(p):pilot.sha(p) for p in paths}
    return dict(format=1,inputs=inputs,registry=registry.manifest,registry_sha256=registry.sha256,
        maximum_seconds=SECONDS,maximum_new_bytes=LIMIT,reserve_bytes=RESERVE,
        global_allocated_cap=pilot.GLOBAL_LIMIT,network_seed=NETWORK_SEED,
        heldout_depths=list(HELDOUT),native_retained_deals=2,new_training_deals=0,new_evaluation_deals=0,
        cpu_cuda_absolute_tolerance=1e-10,production_modified=False,
        scope='Native geometry/visible inputs, table isolation, immutable model objects and own-reach averaging. Synthetic network/table values are test sentinels, not fitted poker strategies.'),entries,registry,deals


def main(run=False):
    start=time.monotonic();spec,entries,registry,deals=specification()
    if not run:
        print(json.dumps(dict(preflight_passed=True,contexts=7,input_width=362,heldout_depths=list(HELDOUT),gpu_started=False)),flush=True)
        return
    assert not any(p.exists() for p in (REG,RESULT,STORE)),'Preserve prior attempts'
    ready,probe=pilot.available();assert ready,'Other research or production has priority'
    acquired=False
    try:
        with pilot.LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        inventory=pilot.global_measure();allocated=sum(r['allocated_file_bytes'] for r in inventory)
        assert allocated+LIMIT+RESERVE<=pilot.GLOBAL_LIMIT
        pilot.atomic_json(REG,spec);pilot.create(STORE)
        pilot.atomic_json(STORE/'admission.json',dict(allocated_bytes=allocated,inventory=inventory,
            reserve_bytes=LIMIT+RESERVE,gpu=probe))
        pilot.STORE=STORE;pilot.STATUS=STATUS;pilot.LIMIT=LIMIT
        import torch
        assert torch.cuda.is_available();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.cuda.set_per_process_memory_fraction(pilot.CUDA_BUDGET_BYTES/torch.cuda.get_device_properties(0).total_memory)
        resource=pilot.Guard()
        def guard():
            assert time.monotonic()-start<SECONDS;resource()
        raw=STORE/'retained-deals.json'
        pilot.atomic_json(raw,dict(format=2,batch_id=NAME,seed=0,query_limit=100000,deals=deals))
        queries={};prepared={};records=[];all_keys=[];old_keys=[]
        for entry,depth in zip(entries,DEPTHS):
            guard();pilot.status('checking_native_stack_context',stack=depth)
            context=GEOMETRY/'fixtures'/f'stack-{depth}-context.json';dest=STORE/f'stack-{depth}-queries.json'
            done=subprocess.run([str(EXE),'queries',str(context),str(raw),'-',str(dest)],capture_output=True,
                text=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
            assert done.returncode==0,done.stderr[-2000:]
            q=pilot.read(dest);key=digest(entry['context_source']);assert q['batch_source']==raw.read_text()
            prepared[key]=registry.prepare(q,context_sha256=key);queries[key]=q
            assert np.array_equal(prepared[key]['features'][:,:302],original_features(q['observations']))
            public={o['hi'] for o in q['observations']}
            assert public=={r['hi'] for r in entry['public_document']['public_states']}
            hidden=copy.deepcopy(q);hidden['batch_source']='hidden opponent/runout data deliberately changed';hidden['targets']=[999]
            assert np.array_equal(prepared[key]['features'],registry.prepare(hidden,context_sha256=key)['features'])
            all_keys.extend(prepared[key]['keys']);old_keys.extend((o['hi'],o['lo']) for o in q['observations'])
            records.append(dict(stack=depth,context_sha256=key,split=entry['split'],
                observations=len(q['observations']),public_states=len(public),
                own_history_links=sum(len(o['own_history']) for o in q['observations'])))
        assert len(set(all_keys))==len(all_keys) and len(set(old_keys))<len(old_keys)
        by_depth={r['stack']:r['context_sha256'] for r in records}
        roots=[]
        for depth in DEPTHS:
            key=by_depth[depth];index=next(i for i,o in enumerate(queries[key]['observations']) if o['hi']=='1')
            roots.append(prepared[key]['features'][index])
        assert all(np.array_equal(roots[0][:302],r[:302]) for r in roots)
        assert all(not np.array_equal(a[302:],b[302:]) for i,a in enumerate(roots) for b in roots[i+1:])
        initial=policy.initial(registry);rng=np.random.default_rng(NETWORK_SEED)
        nets=[{name:rng.normal(0.,.03,int(np.prod(shape))).astype(np.float32).tolist()
               for name,shape in policy.SHAPES.items()} for _ in (0,1)]
        # Keep positive mixed action scores, and add a known public-stack signal.
        for net in nets:
            net['b0']=[.2]*64;net['b1']=[.2]*64;net['b2']=[1.]*4
            net['w0'][306]=1.;net['w1'][0]=1.;net['w2'][64]=1.
        tables={k:[None,None] for k in registry.fit_contexts}
        for depth,action in ((20,1),(40,2)):
            key=by_depth[depth];q=queries[key]
            o=next(o for o in q['observations'] if o['hi']=='1')
            reservoir=WeightedPhysicalReservoir(4,0,0,registry.source(key))
            reservoir.add(o,[float(a==action) for a in range(4)],1,deal_weight=1.)
            tables[key][0]=build_table(reservoir,registry.source(key))
        candidate=policy.model(registry,generation=1,networks=nets,preflop_tables=tables)
        references=[]
        for value in (initial,candidate):
            reference=policy.write_model(STORE/'objects',value,registry)
            assert policy.read_model(STORE/'objects',reference,registry)==value
            references.append(reference)
        weights=np.tile([1.,2.],(2,1));errors=[];naive_error=0.;root_policies={}
        for record in records:
            guard();key=record['context_sha256'];q=queries[key]
            p0,_=policy.predict(initial,registry,q,context_sha256=key)
            p1,prep=policy.predict(candidate,registry,q,context_sha256=key)
            gpu,_=policy.predict(candidate,registry,q,context_sha256=key,device='cuda')
            error=float(np.max(abs(p1-gpu)));assert error<1e-10
            cpu,reach=policy.average([initial,candidate],registry,q,context_sha256=key,
                weights_by_player=weights,device='cpu',guard=guard)
            avg,gr=policy.average([initial,candidate],registry,q,context_sha256=key,
                weights_by_player=weights,device='cuda',guard=guard)
            error=max(error,float(np.max(abs(cpu-avg))),float(np.max(abs(reach-gr))));assert error<1e-10
            expected=[];expected_reach=[]
            for i,history in enumerate(prep['own_history']):
                w=np.asarray([np.prod([p0[j,a] for j,a in history]),2*np.prod([p1[j,a] for j,a in history])])
                n=q['observations'][i]['n'];r=float(w.sum());expected_reach.append(r)
                expected.append((w[0]*p0[i]+w[1]*p1[i])/r if r else np.asarray([1./n if a<n else 0. for a in range(4)]))
            assert np.max(abs(cpu-np.asarray(expected)))<1e-12 and np.max(abs(reach-expected_reach))<1e-12
            naive_error=max(naive_error,float(np.max(abs(cpu-(p0+2*p1)/3))))
            index=next(i for i,o in enumerate(q['observations']) if o['hi']=='1')
            root_policies[record['stack']]=p1[index].tolist()
            if record['stack'] in (20,40):assert p1[index][1 if record['stack']==20 else 2]==1.
            errors.append(dict(stack=record['stack'],maximum_cpu_cuda_error=error))
        assert naive_error>1e-4 and not np.allclose(root_policies[60],root_policies[150],rtol=0.,atol=1e-8)
        rejected=[]
        def reject(name,action):
            try:action()
            except (ValueError,KeyError):rejected.append(name)
            else:raise AssertionError('Accepted invalid case: '+name)
        k20=by_depth[20];k40=by_depth[40];q=queries[k20]
        reject('unknown_context',lambda:registry.prepare(q,context_sha256='0'*64))
        reject('wrong_context_batch',lambda:registry.prepare(q,context_sha256=k40))
        for depth in HELDOUT:
            key=by_depth[depth];reject('heldout_fit_'+str(depth),lambda key=key:registry.prepare(queries[key],context_sha256=key,purpose='fit'))
        for field,replacement in (('lo','0'),('n',1),('actor',1),('phase',3)):
            bad=copy.deepcopy(q);bad['observations'][0][field]=replacement
            reject('bad_'+field,lambda bad=bad:registry.prepare(bad,context_sha256=k20))
        bad=copy.deepcopy(q);later=next(o for o in bad['observations'] if o['own_history']);later['own_history'][0][1]=9
        reject('invalid_own_history',lambda:registry.prepare(bad,context_sha256=k20))
        reject('duplicate_registry',lambda:Registry([entries[0],entries[0]]))
        bad=copy.deepcopy(candidate);bad['preflop_tables'][by_depth[60]]=[None,None]
        reject('heldout_table',lambda:policy.validate(bad,registry))
        bad=copy.deepcopy(candidate);bad['preflop_tables'][k20][0]=copy.deepcopy(tables[k40][0])
        reject('cross_context_table',lambda:policy.validate(bad,registry))
        bad=copy.deepcopy(candidate);bad['networks'][0]['w0']=bad['networks'][0]['w0'][:64*302]
        reject('old_width',lambda:policy.validate(bad,registry))
        bad=copy.deepcopy(candidate);bad['policy_type']='board-root-stratified-postflop-poker-v1'
        reject('old_policy_type',lambda:policy.validate(bad,registry))
        other=copy.deepcopy(entries);other[2]['split']='fit';changed=Registry(other)
        reject('changed_registry',lambda:policy.validate(candidate,changed))
        reject('corrupt_object_reference',lambda:policy.read_model(STORE/'objects',dict(references[1],sha256='0'*64),registry))
        reject('unplayed_bank_order',lambda:policy.average([candidate,initial],registry,q,context_sha256=k20,
            weights_by_player=weights,device='cpu',guard=guard))
        pilot.verify(spec['inputs']);guard();measurement=pilot.study_measure(STORE)
        assert measurement['logical_bytes']<LIMIT
        result=dict(passed=True,complete=True,registration_sha256=pilot.sha(REG),registry_sha256=registry.sha256,
            contexts=records,representation=SPEC,model_objects=references,cpu_cuda=errors,
            original_key_collisions_across_contexts=len(old_keys)-len(set(old_keys)),
            namespaced_keys_unique=True,old_visible_inputs_identical=True,hidden_batch_invariance=True,
            public_stack_inputs_distinct=True,own_reach_vs_naive_max_difference=naive_error,
            synthetic_root_policies=root_policies,negative_controls=rejected,heldout_fitting_refused=True,
            artifacts={str(p):pilot.sha(p) for p in STORE.rglob('*') if p.is_file()},storage=measurement,
            seconds=time.monotonic()-start,gpu_used=True,peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),
            peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),resource_wait_seconds=resource.wait_seconds,
            fitted_poker_models=0,new_training_deals=0,new_evaluation_deals=0,
            training_checkpoint_implemented=False,accuracy_claim=False,production_modified=False)
        pilot.atomic_json(RESULT,result);pilot.status('complete',result=str(RESULT))
        print(json.dumps({k:v for k,v in result.items() if k not in ('artifacts','representation','synthetic_root_policies')}),flush=True)
    except BaseException as error:
        pilot.atomic_json(OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(
            registration_sha256=pilot.sha(REG) if REG.exists() else None,error=repr(error),traceback=traceback.format_exc()))
        raise
    finally:
        if acquired:
            assert pilot.LOCK.read_text()==str(os.getpid());pilot.LOCK.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');main(parser.parse_args().run)
