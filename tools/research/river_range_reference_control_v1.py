"""CPU-only qualification of arbitrary-range terminal river arithmetic."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import argparse,hashlib,json,math,threading,time,traceback,uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import psutil
import torch
from river_range_reference_v1 import RiverRangeReference
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import create,measure
from global_research_inventory_v3 import measure as inventory
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK,OTHER
from stack_price_reference_control_v1 import public_key

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-range-reference-control-v1';STORE=Path('S:/GTOpen-research')/NAME
PREVIOUS=Path('S:/GTOpen-research/stack-price-reference-control-v1')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main(run):
    proof=OUT/'stack-price-reference-control-v1-result.json';old=read(proof)
    prior=OUT/'stack-price-reference-control-v1-registration.json'
    assert old['passed'] and old['complete'] and old['registration_sha256']==sha(prior)
    inv=OUT/'global-research-inventory-v3-control-v2.json';ir=OUT/'global-research-inventory-v3-registration-v2.json'
    assert read(inv)['passed'] and read(inv)['registration_sha256']==sha(ir)
    for p,h in read(ir)['inputs'].items():assert sha(p)==h,p
    paths=[Path(__file__),ROOT/'tools/research/river_range_reference_v1.py',
        ROOT/'tools/research/stack_price_reference_v1.py',proof,prior,inv,ir,OUT/'RIVER-RANGE-REFERENCE-PLAN.md']
    for index in range(12):
        for suffix in ('native-ranks','reference'):
            p=PREVIOUS/f'board-{index}-{suffix}.json';assert sha(p)==old['artifacts'][str(p)];paths.append(p)
    contexts=[]
    for depth in (20,40,100,200,400):
        p=GEOMETRY/f'stack-{depth}-public.json';assert sha(p)==read(prior)['inputs'][str(p)];paths.append(p)
        control=PREVIOUS/f'stack-{depth}-native-control.json';assert sha(control)==old['artifacts'][str(control)];paths.append(control)
        public={r['hi']:r for r in read(p)['public_states'] if r['phase']==3 and [a['kind'] for a in r['actions']]==['fold','call']}
        native=[r for r in read(control)['templates'] if r['legal_actions']==2]
        for r in (native[0],native[-1]):
            assert r['call_ends_showdown'];contexts.append((public[public_key(r)],np.asarray(r['endpoints_loss_tie_win'])[[2,1,0]]))
    spec=dict(inputs={str(p):sha(p) for p in paths},seed=9297001,boards=12,weight_cases=6,
        mass_tolerance=1e-12,equity_tolerance=1e-12,payoff_tolerance_bb=1e-9,
        scalar_hero_indices=[0,1,180,360,540,720,900,1080],workers=4,maximum_seconds=600,
        maximum_new_bytes=16_000_000,reserve_bytes=16_000_000,
        reach_factorization_qualified=False,new_policy_training=False,gpu_used=False,production_modified=False)
    if not run:print(json.dumps(dict(preflight_passed=True,boards=12)));return
    assert not any(p.exists() for p in (REG,RESULT,STORE,LOCK,OTHER))
    assert production_available() and psutil.cpu_percent(interval=1)<50
    assert psutil.virtual_memory().available>28_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
    began=time.monotonic();mutex=threading.Lock();last=0.
    def guard():
        nonlocal last
        with mutex:
            now=time.monotonic();assert now-began<600
            if now-last<2:return
            assert production_available() and not OTHER.exists()
            assert psutil.virtual_memory().available>24_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
            assert psutil.cpu_percent(interval=None)<75
            last=now
    with LOCK.open('x') as stream:stream.write(str(os.getpid()))
    try:
        accounting=inventory();assert sum(v['allocated_file_bytes'] for v in accounting)+32_000_000<=800_000_000_000
        atomic_json(REG,spec);create(STORE);atomic_json(STORE/'admission.json',dict(inventory=accounting))
        def one(index):
            guard();raw=read(PREVIOUS/f'board-{index}-native-ranks.json');retained=read(PREVIOUS/f'board-{index}-reference.json')
            board=raw['board'];hands=np.asarray([r['hand'] for r in raw['rows']]);ranks=np.asarray([r['rank'] for r in raw['rows']])
            assert raw['larger_rank_is_stronger'];oracle=RiverRangeReference(board,hands,ranks)
            rng=np.random.default_rng(spec['seed']+index);lognormal=np.exp(rng.normal(0,2,1081))
            single=np.zeros(1081);single[0]=1
            sparse=np.where(np.arange(1081)%17==0,lognormal,0.)
            tiny=np.full(1081,1e-100);tiny[0]=1.
            cases=[('uniform',np.ones(1081)),('lognormal',lognormal),('zero',np.zeros(1081)),
                   ('single',single),('sparse',sparse),('tiny_surviving_mass',tiny)]
            records=[];maxmass=maxeq=maxcash=maxscalar=0.
            for name,w in cases:
                guard();actual=oracle.masses(w);expected=[]
                for hero,rank in zip(hands,ranks):
                    legal=(hands!=hero[0]).all(1)&(hands!=hero[1]).all(1)
                    expected.append([float(w[legal&(ranks>rank)].sum()),float(w[legal&(ranks==rank)].sum()),float(w[legal&(ranks<rank)].sum())][::-1])
                expected=np.asarray(expected);error=float(np.max(abs(actual-expected))/max(1.,float(w.sum())))
                maxmass=max(maxmass,error);assert error<spec['mass_tolerance']
                supported=expected.sum(1)>0
                if name=='uniform':assert np.array_equal(actual,retained['counts_win_tie_loss'])
                if name=='single':assert np.count_nonzero(supported)==990
                if name=='zero':assert not supported.any()
                if name=='tiny_surviving_mass':assert supported.all()
                for j in spec['scalar_hero_indices']:
                    terms=[[],[],[]]
                    for pair,rank,weight in zip(hands,ranks,w):
                        if set(hands[j]).intersection(pair):continue
                        category=0 if ranks[j]>rank else 1 if ranks[j]==rank else 2
                        terms[category].append(float(weight))
                    independent=np.asarray([math.fsum(v) for v in terms])
                    err=float(np.max(abs(actual[j]-independent))/max(1.,float(w.sum())))
                    maxscalar=max(maxscalar,err);assert err<spec['mass_tolerance']
                expected_eq=np.divide(expected[:,0]+.5*expected[:,1],expected.sum(1),out=np.full(1081,np.nan),where=supported)
                for row,endpoints in contexts:
                    got=oracle.values(w,row)
                    assert np.array_equal(got['supported'],supported)
                    assert np.isnan(got['equity'][~supported]).all() and np.isnan(got['call_minus_fold_bb'][~supported]).all()
                    want=np.divide(expected@endpoints,expected.sum(1),out=np.full(1081,np.nan),where=supported)
                    eqerr=float(np.max(abs(got['equity'][supported]-expected_eq[supported]))) if supported.any() else 0.
                    casherr=float(np.max(abs(got['call_minus_fold_bb'][supported]-want[supported]))) if supported.any() else 0.
                    maxeq=max(maxeq,eqerr);maxcash=max(maxcash,casherr)
                    assert eqerr<spec['equity_tolerance'] and casherr<spec['payoff_tolerance_bb']
                scaled=oracle.values(w*.125,contexts[0][0]);plain=oracle.values(w,contexts[0][0])
                assert np.allclose(scaled['equity'],plain['equity'],rtol=0,atol=1e-12,equal_nan=True)
                records.append(dict(case=name,supported_rows=int(supported.sum()),mass_error_normalized=error))
            # Relabel suits and reverse board order; map private cards and their weights together.
            transform=lambda c:int(c//4*4+(c%4+1)%4)
            mapped=np.asarray([sorted([transform(h[1]),transform(h[0])]) for h in hands])
            order=np.lexsort((mapped[:,1],mapped[:,0]));mapped_board=[transform(c) for c in board[::-1]]
            other=RiverRangeReference(mapped_board,mapped[order],ranks[order])
            left=oracle.masses(lognormal)[order];right=other.masses(lognormal[order])
            assert np.max(abs(left-right))/lognormal.sum()<1e-12
            result=dict(index=index,records=records,maximum_normalized_mass_error=maxmass,
                maximum_scalar_mass_error=maxscalar,maximum_equity_error=maxeq,maximum_payoff_error_bb=maxcash,
                uniform_counts_exact=True,scale_and_card_relabeling_passed=True)
            atomic_json(STORE/f'board-{index}.json',result);return result
        with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(one,range(12)))
        raw=read(PREVIOUS/'board-0-native-ranks.json');board=raw['board']
        h=np.asarray([r['hand'] for r in raw['rows']]);r=np.asarray([r['rank'] for r in raw['rows']]);oracle=RiverRangeReference(board,h,r)
        rejected=[]
        def reject(label,fn):
            try:fn()
            except ValueError:rejected.append(label)
            else:raise AssertionError('Accepted '+label)
        reject('duplicate_board',lambda:RiverRangeReference([0,0,1,2,3],h,r))
        reject('missing_holding',lambda:RiverRangeReference(board,h[:-1],r[:-1]))
        reject('reversed_hole_order',lambda:RiverRangeReference(board,h[:,::-1],r))
        reject('float_ranks',lambda:RiverRangeReference(board,h,r.astype(float)))
        reject('negative_ranks',lambda:RiverRangeReference(board,h,-r))
        for label,w in [('wrong_weight_count',np.ones(1080)),('negative_weight',np.full(1081,-1.)),
                        ('nan_weight',np.full(1081,np.nan)),('infinite_weight',np.full(1081,np.inf)),
                        ('boolean_weight',np.ones(1081,dtype=bool))]:reject(label,lambda w=w:oracle.masses(w))
        reject('wrong_street',lambda:oracle.values(np.ones(1081),dict(contexts[0][0],phase=2)))
        reject('negative_call_price',lambda:oracle.values(np.ones(1081),dict(contexts[0][0],call_cost=-1)))
        for p,hsh in spec['inputs'].items():assert sha(p)==hsh,p
        guard();assert not torch.cuda.is_initialized();size=measure(STORE);assert size['logical_bytes']<16_000_000
        result=dict(passed=True,registration_sha256=sha(REG),records=records,negative_controls=rejected,
            mass_rows=12*6*1081,cashflow_rows=12*6*1081*len(contexts),seconds=time.monotonic()-began,storage=size,
            gpu_used=False,new_policy_training=False,reach_factorization_qualified=False,production_modified=False,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()})
        atomic_json(RESULT,result);print(json.dumps({k:v for k,v in result.items() if k not in ('records','artifacts')}),flush=True)
    except BaseException as error:
        atomic_json(OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),traceback=traceback.format_exc()))
        raise
    finally:
        assert LOCK.read_text()==str(os.getpid());LOCK.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');main(parser.parse_args().run)
