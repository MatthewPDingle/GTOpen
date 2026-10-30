"""CPU native-query bridge for the relative-input model-object contract."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import argparse,copy,hashlib,json,sys,threading,time,traceback,uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import psutil
from stack_context_inputs_v1 import Registry as BaseRegistry,digest
from stack_context_relative_inputs_v1 import Registry,SPEC
import stack_context_policy_v1 as base_policy
import stack_context_relative_policy_v1 as policy
from stack_price_learning_data_v2 import card_factors,public_factors
from stack_board_relative_features_v1 import relative_features
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import create,measure
from global_research_inventory_v3 import measure as inventory
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK,OTHER

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='stack-context-relative-control-v1';STORE=Path('S:/GTOpen-research')/NAME
OLD=Path('S:/GTOpen-research/stack-context-model-control-v1')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
DEPTHS=(20,40,60,100,150,200,400)
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(paths):
    for p,h in paths.items():assert sha(p)==h,p

def specification():
    pr=OUT/'stack-context-model-control-v1-registration.json';proof=OUT/'stack-context-model-control-v1-result.json'
    old=read(proof);assert old['passed'] and old['complete'] and old['registration_sha256']==sha(pr)
    gr=OUT/'stack-geometry-control-v1-result.json';geometry=read(gr)
    assert geometry['passed'];paths=[Path(__file__),pr,proof,gr,OUT/'STACK-CONTEXT-RELATIVE-CONTRACT.md']
    entries=[]
    for depth in DEPTHS:
        cp=GEOMETRY/'fixtures'/f'stack-{depth}-context.json';pp=GEOMETRY/f'stack-{depth}-public.json';qp=OLD/f'stack-{depth}-queries.json'
        for p in (cp,pp):assert sha(p)==geometry['artifacts'][str(p)]
        assert sha(qp)==old['artifacts'][str(qp)]
        entries.append(dict(name=f'{depth}bb',split='heldout' if depth in (60,150) else 'fit',
            context_source=cp.read_text(),public_document=read(pp)));paths.extend([cp,pp,qp])
    original=BaseRegistry(entries);new=Registry(entries)
    assert original.sha256==old['registry_sha256'] and new.sha256!=original.sha256
    for ref in old['model_objects']:
        p=OLD/'objects'/ref['file'];assert sha(p)==ref['sha256'];paths.append(p)
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    return dict(inputs={str(p):sha(p) for p in paths},registry=new.manifest,registry_sha256=new.sha256,
        representation=SPEC,maximum_seconds=900,maximum_new_bytes=16_000_000,reserve_bytes=16_000_000,workers=4,
        neutral_policy_equality='exact',neutral_average_equality='exact',diagnostic_input_equality='exact',
        gpu_used=False,cuda_parity_qualified=False,model_quality_qualified=False,training_checkpoint_implemented=False,
        new_training_deals=0,new_evaluation_deals=0,production_modified=False),entries,original,new,old

def main(run):
    spec,entries,original,registry,old=specification()
    if not run:print(json.dumps(dict(preflight_passed=True,contexts=7,input_width=387,gpu_used=False)));return
    assert not any(p.exists() for p in (REG,RESULT,STORE,LOCK,OTHER))
    assert production_available() and psutil.cpu_percent(interval=1)<50
    assert psutil.virtual_memory().available>28_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
    start=time.monotonic();mutex=threading.Lock();last=0.
    def guard():
        nonlocal last
        with mutex:
            now=time.monotonic();assert now-start<900
            if now-last<2:return
            assert production_available() and not OTHER.exists() and psutil.cpu_percent(interval=None)<75
            assert psutil.virtual_memory().available>24_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
            last=now
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        accounting=inventory();assert sum(r['allocated_file_bytes'] for r in accounting)+32_000_000<=800_000_000_000
        atomic_json(REG,spec);create(STORE);atomic_json(STORE/'admission.json',dict(inventory=accounting))
        models=[base_policy.read_model(OLD/'objects',r,original) for r in old['model_objects']]
        assert [m['generation'] for m in models]==[0,1]
        lifted=[policy.extend_from_362(m,original,registry) for m in models]
        sentinel=copy.deepcopy(lifted[1])
        for net in sentinel['networks']:
            w=np.asarray(net['w0']).reshape(64,387);w[0,362:371]=.5;net['w0']=w.reshape(-1).tolist()
        policy.validate(sentinel,registry);refs=[]
        for value in [*lifted,sentinel]:
            ref=policy.write_model(STORE/'objects',value,registry)
            assert policy.read_model(STORE/'objects',ref,registry)==value;refs.append(ref)
        def one(item):
            depth,entry=item;guard();q=read(OLD/f'stack-{depth}-queries.json');key=digest(entry['context_source'])
            plain=original.prepare(q,context_sha256=key);extra=registry.prepare(q,context_sha256=key)
            assert np.array_equal(plain['features'],extra['features'][:,:362])
            assert plain['keys']==extra['keys'] and plain['own_history']==extra['own_history']
            phase=np.asarray([r['phase'] for r in q['observations']]);assert set(phase)=={0,1,2,3}
            assert not np.any(extra['features'][phase!=3,362:]) and np.any(extra['features'][phase==3,362:])
            hidden=copy.deepcopy(q);hidden['batch_source']='unread hidden private-card/runout labels';hidden['targets']=[999]
            assert np.array_equal(extra['features'],registry.prepare(hidden,context_sha256=key)['features'])
            for a,b in zip(models,lifted):
                want,_=base_policy.predict(a,original,q,context_sha256=key)
                got,_=policy.predict(b,registry,q,context_sha256=key)
                assert np.array_equal(got,want)
            weights=np.tile([1.,2.],(2,1))
            want,reach=base_policy.average(models,original,q,context_sha256=key,weights_by_player=weights,device='cpu',guard=guard)
            got,nreach=policy.average(lifted,registry,q,context_sha256=key,weights_by_player=weights,device='cpu',guard=guard)
            assert np.array_equal(got,want) and np.array_equal(reach,nreach)
            p0,_=policy.predict(lifted[1],registry,q,context_sha256=key)
            p1,_=policy.predict(sentinel,registry,q,context_sha256=key)
            assert np.array_equal(p0[phase!=3],p1[phase!=3])
            changed=float(np.max(abs(p1[phase==3]-p0[phase==3])));assert changed>1e-10
            public=public_factors(entry['public_document']);states={r['hi']:i for i,r in enumerate(public['rows'])}
            eligible=[(i,o) for i,o in enumerate(q['observations']) if o['hi'] in states]
            # Reconstruct selected existing observations with the diagnostic assembler.
            selected=[eligible[0],eligible[-1]];checks=0
            for i,o in selected:
                cards=[(int(o['lo'])>>(6*j))&63 for j in range(7)];factors=card_factors(cards[2:])
                j=next(j for j,h in enumerate(factors['hands'].tolist()) if h==cards[:2])
                row=np.concatenate((factors['features'][j]+public['features'][states[o['hi']]],relative_features(cards[:2],cards[2:])))
                assert np.array_equal(row,extra['features'][i]);checks+=1
            path=STORE/f'stack-{depth}-readback.npz'
            with path.open('xb') as f:np.savez_compressed(f,neutral_policy=got,base_policy=want,neutral_reach=nreach,base_reach=reach,
                candidate=p0,sentinel=p1,phase=phase,features=extra['features'])
            report=dict(stack=depth,observations=len(phase),phases=sorted(set(map(int,phase))),river_rows=int(sum(phase==3)),
                exact_prefix=True,exact_neutral_policy=True,exact_neutral_average=True,exact_own_reach=True,
                earlier_streets_unchanged=True,maximum_sentinel_river_change=changed,diagnostic_rows=checks)
            print(json.dumps(report),flush=True);return report
        with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(one,zip(DEPTHS,entries)))
        negative=[]
        def reject(label,fn):
            try:fn()
            except (ValueError,KeyError):negative.append(label)
            else:raise AssertionError('Accepted '+label)
        reject('old_model_new_reader',lambda:policy.validate(models[1],registry))
        reject('new_model_old_reader',lambda:base_policy.validate(lifted[1],original))
        reject('new_model_old_registry',lambda:policy.validate(lifted[1],original))
        for depth in (60,150):
            entry=entries[DEPTHS.index(depth)];q=read(OLD/f'stack-{depth}-queries.json')
            reject(f'heldout_fit_{depth}',lambda q=q,entry=entry:registry.prepare(q,context_sha256=digest(entry['context_source']),purpose='fit'))
        for kind in ('width','nonfinite','initial_nonzero'):
            bad=copy.deepcopy(lifted[0] if kind=='initial_nonzero' else lifted[1])
            if kind=='width':bad['networks'][0]['w0']=bad['networks'][0]['w0'][:-25]
            elif kind=='nonfinite':bad['networks'][0]['w0'][-1]=float('nan')
            else:bad['networks'][0]['w0'][-1]=1.
            reject(kind,lambda bad=bad:policy.validate(bad,registry))
        changed=copy.deepcopy(entries);changed[0]['split']='heldout';other=Registry(changed)
        reject('changed_context_role',lambda:policy.extend_from_362(models[1],original,other))
        verify(spec['inputs']);guard();size=measure(STORE);assert size['logical_bytes']<16_000_000
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),registry_sha256=registry.sha256,
            contexts=records,observations=sum(r['observations'] for r in records),model_objects=refs,negative_controls=negative,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},storage=size,seconds=time.monotonic()-start,
            gpu_used=False,cuda_parity_qualified=False,model_quality_qualified=False,training_checkpoint_implemented=False,
            new_training_deals=0,new_evaluation_deals=0,production_modified=False)
        atomic_json(RESULT,result);print(json.dumps(dict(passed=True,seconds=result['seconds'],observations=result['observations'],storage=size)),flush=True)
    except BaseException as error:
        atomic_json(OUT/(NAME+'-failure-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),traceback=traceback.format_exc()));raise
    finally:
        assert LOCK.read_text()==str(os.getpid());LOCK.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');main(parser.parse_args().run)
