"""CPU qualification of one public opponent reach vector against native histories."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import argparse,hashlib,itertools,json,math,subprocess,sys,threading,time,traceback,uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import psutil
from river_range_reference_v2 import RiverRangeReference
from river_full_action_math_v1 import canonical
from river_posterior64_v1 import posterior
from river_policy_batch_v1 import CPUCurrentPolicy
from board_training_checkpoint_v1 import model_document
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import create,measure
from global_research_inventory_v3 import measure as inventory
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK,OTHER
from owned_windows_job_v1 import OwnedJob

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-range-policy-binding-v1';STORE=Path('S:/GTOpen-research')/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
CONTEXT=OUT/'bb-context-candidate.json';PLAN=OUT/'RIVER-RANGE-POLICY-BINDING-PLAN.md'
FULL=ROOT/'target/release/examples/hu_river_action_queries_batch_v1.exe'
RANKS=ROOT/'target/release/examples/hu_board_hand_ranks_v1.exe'
PRIOR=OUT/'river-posterior64-native-control-v1';LIMIT=192_000_000;RESERVE=64_000_000

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(inputs):
    for p,h in inputs.items():assert sha(p)==h,p

def mapped(cards,perm):
    c=[x//4*4+perm[x%4] for x in cards];c[:2]=sorted(c[:2]);c[2:5]=sorted(c[2:5]);return c

def request_for(hi,actor,hand,board):
    cards=list(hand)+list(board)
    variants=[(mapped(cards,p),p) for p in itertools.permutations(range(4))]
    chosen,perm=min(variants,key=lambda t:sum(c<<(6*i) for i,c in enumerate(t[0])))
    assert tuple(chosen)==canonical(tuple(cards))
    lo=(actor<<42)+sum(c<<(6*i) for i,c in enumerate(chosen))
    return dict(format=1,hi=hi,lo=str(lo)),list(perm),chosen

def accumulate(assembled,signatures,pair,weight,signature):
    if pair in assembled:
        if signatures[pair]!=signature:raise ValueError('Opponent observations depend on hero holding')
        if abs(assembled[pair]-weight)>1e-10:raise ValueError('Inconsistent opponent mass')
    else:assembled[pair]=weight;signatures[pair]=signature

def vector(assembled,hands):
    if set(assembled)!=set(map(tuple,hands)):raise ValueError('Incomplete opponent holding coverage')
    return np.asarray([assembled[tuple(h)] for h in hands])

def specification():
    nr=OUT/'river-posterior64-native-control-v1-registration.json'
    proof=OUT/'river-posterior64-native-control-v1-result.json'
    done=read(proof);assert done['passed'] and done['complete'] and done['registration_sha256']==sha(nr)
    assert sha(FULL)==read(nr)['inputs'][str(FULL)]
    rreg=OUT/'stack-price-reference-control-v1-registration.json'
    assert sha(RANKS)==read(rreg)['inputs'][str(RANKS)]
    vr=OUT/'river-range-reference-control-v2-result.json';vreg=OUT/'river-range-reference-control-v2-registration.json'
    assert read(vr)['passed'] and read(vr)['registration_sha256']==sha(vreg)
    for path in (ROOT/'tools/research/river_range_reference_v1.py',ROOT/'tools/research/river_range_reference_v2.py'):
        assert sha(path)==read(vreg)['inputs'][str(path)]
    pr=OUT/'river-learned-batch-cost-v1-registration.json';policies=read(pr)['policies']
    cp=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    paths=[Path(__file__),PLAN,CONTEXT,FULL,RANKS,nr,proof,rreg,vr,vreg,pr,cp,mp]
    for b in policies:
        path=Path(b['folder'])/b['reference']['file'];assert sha(path)==b['reference']['sha256'];paths.append(path)
    cases=read(OUT/'river-learned-batch-cost-v1-result.json')['cases'];tasks=[]
    artifacts={c['case']:c['artifacts'] for c in done['cases']}
    for case in cases:
        path=PRIOR/case['case']/'full/full-export.json'
        assert sha(path)==artifacts[case['case']]['full\\full-export.json'];paths.append(path)
        full=read(path);seen=set()
        for di,doc in enumerate(full['targets']):
            pair=doc['pairs'][0]
            for ni in range(pair['node_start'],pair['root']+1):
                node=doc['nodes'][ni]
                if node['kind']!='decision' or node['actor'] in seen:continue
                if [a['kind'] for a in node['actions']]!=['fold','call']:continue
                if [doc['nodes'][i]['kind'] for i in node['children']]!=['fold','showdown']:continue
                q=full['queries']['observations'][node['query_index']];seen.add(node['actor'])
                cards=[(int(q['lo'])>>(6*i))&63 for i in range(7)];board=cards[2:]
                available=list(itertools.combinations([c for c in range(52) if c not in board],2))
                selected=[tuple(cards[:2])];used=set(selected[0])
                for seq in (available,available,list(reversed(available))):
                    hand=next(h for h in seq if not used.intersection(h));selected.append(hand);used.update(hand)
                requests=[];permutations=[];canonical_cards=[]
                for hand in selected:
                    request,perm,cc=request_for(q['hi'],q['actor'],hand,board)
                    requests.append(request);permutations.append(perm);canonical_cards.append(cc)
                assert len({r['lo'] for r in requests})==4
                tasks.append(dict(index=len(tasks),case=case['case'],policy_id=case['policy_id'],actor=q['actor'],
                    source_export=str(path),source_doc=di,source_node=ni,source_query=node['query_index'],
                    hi=q['hi'],board=board,hands=[list(h) for h in selected],requests=requests,
                    permutations=permutations,canonical_cards=canonical_cards,root_put=node['put']))
        assert seen=={0,1}
    assert len(tasks)==16
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    return dict(format=1,inputs={str(p):sha(p) for p in paths},tasks=tasks,policies=policies,
        workers=4,maximum_seconds=900,maximum_new_bytes=LIMIT,reserve_bytes=RESERVE,
        mass_tolerance=1e-10,probability_tolerance=1e-12,payoff_tolerance_bb=1e-9,
        gpu_used=False,training_started=False,final_test_evaluated=False,production_modified=False,
        scope='Binding one current played policy at a time; terminal Fold/Call; not an average bank or model quality test.')

def main(run):
    spec=specification()
    if not run:print(json.dumps(dict(preflight_passed=True,states=len(spec['tasks']),actors=[0,1],gpu_used=False)));return
    assert not any(p.exists() for p in (REG,RESULT,STORE,LOCK,OTHER))
    assert production_available() and psutil.cpu_percent(interval=1)<50
    assert psutil.virtual_memory().available>28_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
    began=time.monotonic();mutex=threading.Lock();last=0.
    def guard():
        nonlocal last
        with mutex:
            now=time.monotonic();assert now-began<900
            if now-last<2:return
            assert production_available() and not OTHER.exists()
            assert psutil.virtual_memory().available>24_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
            assert psutil.cpu_percent(interval=None)<75
            last=now
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        accounting=inventory();assert sum(v['allocated_file_bytes'] for v in accounting)+LIMIT+RESERVE<=800_000_000_000
        atomic_json(REG,spec);create(STORE);atomic_json(STORE/'admission.json',dict(inventory=accounting))
        source=CONTEXT.read_text();cp=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
        mp=OUT/'preflop-allin-matrix-control-v1-matrix.json';mass=AllinMatrix(read(mp),source).btn_mass
        weights=PhysicalDeals(source,mode='full_deck',seed=0).weights
        entry=[{tuple(map(int,p)):float(w) for p,w in zip(PAIRS,row)} for row in weights]
        # This binding uses the source class ranges, not arbitrary suit-asymmetric inputs.
        for e in entry:
            for perm in itertools.permutations(range(4)):
                for pair,w in e.items():assert e[tuple(sorted(c//4*4+perm[c%4] for c in pair))]==w
        engines={}
        for b in spec['policies']:
            args=dict(catalog_source=cp.read_text(),matrix_sha256=sha(mp),entry_mass=mass,root_config=b['root_config'])
            engines[b['policy_id']]=CPUCurrentPolicy(model_document(b['folder'],b['reference'],context_source=source,**args),source,**args)
        atomic_json(STORE/'entry.json',[{','.join(map(str,k)):v for k,v in e.items()} for e in entry])
        with OwnedJob() as job:
            def native(exe,args):
                guard()
                bootstrap="import sys,subprocess; assert sys.stdin.readline().strip()=='OWNED_START'; p=subprocess.run(sys.argv[1:],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW); sys.stdout.buffer.write(p.stdout); sys.stderr.buffer.write(p.stderr); sys.exit(p.returncode)"
                proc=subprocess.Popen([sys.executable,'-B','-c',bootstrap,str(exe),*map(str,args)],
                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
                job.assign(proc)
                stdout,stderr=proc.communicate(b'OWNED_START\n',timeout=120)
                assert proc.returncode==0,stderr.decode(errors='replace')[-2000:]
                return stdout,dict(code=proc.returncode,stderr=stderr.decode(errors='replace'))
            def one(task):
                guard();started=time.monotonic();folder=STORE/f"state-{task['index']}";folder.mkdir()
                request=folder/'request.json';dest=folder/'native-export.json'
                atomic_json(request,dict(format=1,targets=task['requests']))
                _,process=native(FULL,[CONTEXT,request,dest]);batch=read(dest)
                atomic_json(folder/'native-process.json',process)
                assert batch['context_source']==source and len(batch['targets'])==4
                p=engines[task['policy_id']].infer(engines[task['policy_id']].prepare(batch['queries']))
                raw,rankprocess=native(RANKS,task['board']);ranks=json.loads(raw)
                atomic_json(folder/'native-ranks.json',ranks);atomic_json(folder/'rank-process.json',rankprocess)
                assert ranks['board']==task['board'] and ranks['larger_rank_is_stronger']
                hands=np.asarray([r['hand'] for r in ranks['rows']]);strength=np.asarray([r['rank'] for r in ranks['rows']])
                oracle=RiverRangeReference(task['board'],hands,strength);ids={tuple(h):i for i,h in enumerate(hands)}
                assembled={};signatures={};records=[];docs=[];overlaps=0;posterror=0.;ownzero=0
                for j,doc in enumerate(batch['targets']):
                    target=doc['target'];assert target['cards']==task['canonical_cards'][j]
                    assert target['hi']==task['hi'] and target['actor']==task['actor'] and target['n']==2
                    inverse={v:k for k,v in enumerate(task['permutations'][j])}
                    common=lambda cards:tuple(sorted(c//4*4+inverse[c%4] for c in cards))
                    assert common(target['cards'][:2])==tuple(task['hands'][j])
                    assert set(common(target['cards'][2:]))==set(task['board'])
                    paircards=[];rawmass=[];own=[];outcomes=[];payout=[];oppsign=[]
                    for pair in doc['pairs']:
                        cards=common(pair['cards']);w=entry[1-task['actor']][tuple(pair['cards'])];my=1.;sig=[]
                        assert w==entry[1-task['actor']][cards]
                        for qi,a,n in pair['path']:
                            row=batch['queries']['observations'][qi];assert row['n']==n and 0<=a<n
                            prob=float(p[qi,a]);assert math.isfinite(prob) and 0<=prob<=1
                            if row['actor']==task['actor']:my*=prob
                            else:w*=prob;sig.append((row['hi'],row['lo'],a,n,prob))
                        if j<3:
                            overlaps+=int(cards in assembled);accumulate(assembled,signatures,cards,w,sig)
                        else:
                            assert cards in assembled
                            accumulate(assembled,signatures,cards,w,sig)
                        node=doc['nodes'][pair['root']];assert node['put']==task['root_put']
                        assert [a['kind'] for a in node['actions']]==['fold','call']
                        fold,call=[doc['nodes'][i] for i in node['children']]
                        assert fold['kind']=='fold' and call['kind']=='showdown'
                        outcomes.append(pair['outcome_loss_tie_win']);payout.append(call['payoff']-fold['payoff'])
                        paircards.append(ids[cards]);rawmass.append(w);own.append(my);oppsign.append(sig)
                    assert len(paircards)==990 and len(set(paircards))==990 and max(own)-min(own)<1e-12
                    ownzero+=int(own[0]==0);rawmass=np.asarray(rawmass);total=math.fsum(map(float,rawmass))
                    if total>0:
                        reference,m,o=posterior(doc,batch['queries']['observations'],p,entry)
                        assert abs(m-total)<1e-10 and abs(o-own[0])<1e-12
                        posterror=max(posterror,float(np.max(abs(reference-rawmass/total))))
                    if j==2:assert len(assembled)==1081
                    docs.append(dict(ids=np.asarray(paircards),mass=rawmass,total=total,own=own[0],
                        outcomes=np.asarray(outcomes),payout=np.asarray(payout)))
                reach=vector(assembled,hands);hero=task['actor'];put=task['root_put'];cost=put[1-hero]-put[hero]
                row=dict(phase=3,pot=sum(put),call_cost=cost,rake_fraction=json.loads(source)['rake_fraction'],
                    rake_cap=json.loads(source)['rake_cap'],actions=[dict(kind='fold',increment=0),dict(kind='call',increment=cost)])
                got=oracle.values(reach,row);maxmass=maxeq=maxcash=0.;arrays=dict(policy=p,weights=reach,hands=hands,ranks=strength)
                for j,data in enumerate(docs):
                    hi=ids[tuple(task['hands'][j])];other=data['ids'];outcome=data['outcomes']
                    expected=np.where(strength[hi]>strength[other],2,np.where(strength[hi]==strength[other],1,0))
                    assert np.array_equal(outcome,expected)
                    assert not np.any(np.isin(hands[other],task['hands'][j]))
                    maxmass=max(maxmass,float(np.max(abs(reach[other]-data['mass']))),abs(float(got['opponent_mass'][hi])-data['total']))
                    supported=data['total']>0;assert bool(got['supported'][hi])==supported
                    eq=cash=None
                    if supported:
                        prob=data['mass']/data['total']
                        eq=math.fsum(float(q*o*.5) for q,o in zip(prob,outcome))
                        cash=math.fsum(float(q*v) for q,v in zip(prob,data['payout']))
                        maxeq=max(maxeq,abs(float(got['equity'][hi])-eq))
                        maxcash=max(maxcash,abs(float(got['call_minus_fold_bb'][hi])-cash))
                        posterror=max(posterror,float(np.max(abs(reach[other]/got['opponent_mass'][hi]-prob))))
                    else:assert np.isnan(got['equity'][hi]) and np.isnan(got['call_minus_fold_bb'][hi])
                    records.append(dict(hand=task['hands'][j],supported=supported,opponent_mass=data['total'],
                        own_history_likelihood=data['own'],equity=eq,call_minus_fold_bb=cash))
                    for k in ('ids','mass','outcomes','payout'):arrays[f'{k}_{j}']=data[k]
                assert maxmass<spec['mass_tolerance'] and maxeq<spec['probability_tolerance']
                assert posterror<spec['probability_tolerance'] and maxcash<spec['payoff_tolerance_bb']
                with (folder/'retained.npz').open('xb') as stream:np.savez_compressed(stream,**arrays)
                result=dict(index=task['index'],case=task['case'],actor=hero,policy_id=task['policy_id'],
                    covered_opponent_holdings=len(assembled),overlap_comparisons=overlaps,fourth_holding_verified=True,
                    records=records,own_zero_rows=ownzero,maximum_mass_error=maxmass,maximum_equity_error=maxeq,
                    maximum_posterior_error=posterror,maximum_payoff_error_bb=maxcash,price=row,
                    seconds=time.monotonic()-started,queries=len(p))
                atomic_json(folder/'result.json',result);guard()
                print(json.dumps(dict(state=task['index'],complete=True,maximum_payoff_error_bb=maxcash)),flush=True)
                return result
            with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(one,spec['tasks']))
            terminal=job.accounting();assert terminal['active_processes']==0
        negative=[]
        def reject(name,fn):
            try:fn()
            except ValueError:negative.append(name)
            else:raise AssertionError('Accepted '+name)
        reject('missing_holding',lambda:vector({},[(0,1)]))
        reject('overlap_mass',lambda:accumulate({(0,1):1.},{(0,1):[]},(0,1),.5,[]))
        reject('overlap_history',lambda:accumulate({(0,1):1.},{(0,1):[]},(0,1),1.,[('different',)]))
        verify(spec['inputs']);guard();size=measure(STORE);assert size['logical_bytes']<LIMIT
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),records=records,negative_controls=negative,
            current_policy_reach_binding_passed=True,source_entry_suit_invariance_passed=True,
            states=16,hero_rows=64,opponent_pair_rows=64*990,job=terminal,storage=size,seconds=time.monotonic()-began,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
            gpu_used=False,training_started=False,production_modified=False,scope=spec['scope'])
        atomic_json(RESULT,result);print(json.dumps(dict(passed=True,seconds=result['seconds'],storage=size)),flush=True)
    except BaseException as error:
        atomic_json(OUT/(NAME+'-failure-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),traceback=traceback.format_exc()))
        raise
    finally:
        assert LOCK.read_text()==str(os.getpid());LOCK.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');main(parser.parse_args().run)
