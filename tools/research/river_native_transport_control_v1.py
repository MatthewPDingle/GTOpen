"""CPU-only native substitution/visit controls; no training or policy-quality gate."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy,hashlib,json,math,subprocess,sys,time,traceback
from pathlib import Path
import numpy as np
from river_full_action_math_v1 import digest,evaluate
from river_full_action_control_v1 import bundle
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-native-transport-control-v1';STORE=OUT/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');FAILURE=OUT/(NAME+'-failure.json')
PLAN=OUT/'RIVER-NATIVE-TRANSPORT-PLAN.md';CONTEXT=OUT/'bb-context-candidate.json'
EXE=ROOT/'target/release/examples/hu_river_transport_control_v1.exe'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,x):
    raw=(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    assert sum(f.stat().st_size for f in STORE.rglob('*') if f.is_file())+len(raw)<100_000_000
    with Path(p).open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
def verify(inputs):
    for p,h in inputs.items():assert sha(p)==h,p

def weights_control(doc,p,entry,exact):
    hero=doc['target']['actor'];raw=np.array([entry[1-hero][tuple(x['cards'])] for x in doc['pairs']]);prior=raw/raw.sum()
    likelihood=np.array([math.prod(p[i][a] for i,a,n in x['path'] if doc['queries']['observations'][i]['actor']!=hero) for x in doc['pairs']])
    pair=np.asarray(exact['pair_action_values']);sigma=np.asarray(p[doc['target']['query_index']][:doc['target']['n']]);q=np.asarray(exact['action_values'])
    wanted=(prior*likelihood)@pair;expected=(prior*likelihood).sum()*q;error=float(np.max(abs(wanted-expected)));assert error<1e-8
    reports=[]
    for name,proposal in [('entry',prior),('unequal',.4*prior+.6/990)]:
        assert np.all(proposal[prior>0]>0);ratio=np.divide(prior,proposal,out=np.zeros_like(prior),where=proposal>0)
        actual=(proposal*ratio*likelihood).sum()*q
        regret=(proposal*ratio*likelihood).sum()*(q-sigma@q)
        target=(prior*likelihood)@(pair-(pair@sigma)[:,None])
        e=max(float(np.max(abs(actual-wanted))),float(np.max(abs(regret-target))));assert e<1e-8
        wrong=(proposal*ratio*ratio*likelihood).sum()*q
        reports.append(dict(proposal=name,maximum_error=e,twice_applied_weight_error=float(np.max(abs(wrong-wanted))),maximum_weight=float(ratio.max())))
    return dict(maximum_error=error,proposals=reports,opponent_visit_mass=float((prior*likelihood).sum()),own_reach=exact['own_history_likelihood'])

def run(name,doc,request):
    path=STORE/(name+'-input.json');dest=STORE/(name+'-native.json');write(path,request)
    start=time.perf_counter();proc=subprocess.run([str(EXE),str(CONTEXT),str(path),str(dest)],capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    write(STORE/(name+'-process.json'),dict(returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,seconds=time.perf_counter()-start))
    assert proc.returncode==0,(name,proc.stderr);value=read(dest);assert value['passed'] and value['complete'] and value['policy_id']==request['policy_id']
    assert value['direct_replacements']==12
    for r in value['reports']:
        if r['mode']=='target-root':
            p=np.asarray(next(row['p'] for row in request['rows'] if row['hi']==request['target']['hi'] and row['lo']==request['target']['lo']))
            q=np.asarray(request['target']['values']);n=request['target']['n'];regret=q[:n]-p@q
            assert np.max(abs(np.asarray(r['regrets'])[:n]-regret))<1e-9
    return dict(native_sha256=sha(dest),input_sha256=sha(path),**{k:value[k] for k in ('original_visits','full_root_replacements','direct_replacements','maximum_error')})

def main():
    assert not any(p.exists() for p in (STORE,REG,RESULT,FAILURE));start=time.monotonic();STORE.mkdir()
    pilot_path=OUT/'river-current-policy-pilot-v1-result.json';pilot=read(pilot_path);assert pilot['passed'] and pilot['complete']
    paths=[Path(__file__),PLAN,CONTEXT,EXE,pilot_path,ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml',ROOT/'crates/solver/examples/hu_river_transport_control_v1.rs']
    paths.extend((ROOT/'crates/solver/examples/research_sampled').glob('*.rs'));paths.extend((ROOT/'crates/solver/src').rglob('*.rs'))
    for c in pilot['cases']:assert sha(c['export_path'])==c['export_sha256'];paths.append(Path(c['export_path']))
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f and Path(f).is_relative_to(ROOT) and Path(f).suffix=='.py':paths.append(Path(f))
    inputs={str(p):sha(p) for p in paths};verify(inputs)
    write(REG,dict(format=1,created_unix=time.time(),inputs=inputs,cases=[c['case'] for c in pilot['cases']],pair_indices=[0,495,989],seeds=list(range(9282801,9282805)),
        maximum_seconds=600,maximum_added_bytes=100_000_000,gpu_used=False,training=False,production_modified=False,
        storage_basis='Fresh prior pilot admitted at 717.79 GB; subsequent evidence <100 MB against 800 GB cap.',
        scope='One exact target per fixture, preserved native visits/RNG/ancestor propagation and finite source-weight expectations; not nested targets or full training.'))
    try:
        source=CONTEXT.read_text();prior=PhysicalDeals(source,mode='full_deck',seed=0).weights
        entry=[{tuple(map(int,p)):float(w) for p,w in zip(PAIRS,row)} for row in prior]
        reports=[];negative_request=None;weight_rejections=0
        for case in pilot['cases']:
            doc=read(case['export_path']);obs=doc['queries']['observations'];ti=doc['target']['query_index']
            base=[]
            for o in obs:
                # Stable, positive, visibly conditioned test policy; never a learned-policy claim.
                raw=[1+int.from_bytes(hashlib.sha256(f"{o['hi']}|{o['lo']}|{a}".encode()).digest()[:2],'little')%7 for a in range(o['n'])]
                z=sum(raw);base.append([x/z for x in raw]+[0.]*(4-o['n']))
            for variant in ('positive','zero-own'):
                p=copy.deepcopy(base);history=obs[ti]['own_history'];changed=False
                if variant=='zero-own' and history:
                    i,a,n=history[0];p[i]=[0. if j==a or j>=n else 1/(n-1) for j in range(4)];changed=True
                name=case['case']+'-'+variant;policy_id='fixture|'+name+'|'+digest(p)
                exact=evaluate(doc,bundle(doc,p,policy_id),entry,expected_policy_id=policy_id,expected_context_source=source);assert exact['supported']
                if changed:assert exact['own_history_likelihood']==0
                w=weights_control(doc,p,entry,exact);weight_rejections+=int(w['proposals'][1]['twice_applied_weight_error']>1e-8)
                target={k:doc['target'][k] for k in ('hi','lo','n')};target.update(values=exact['action_values']+[0.]*(4-doc['target']['n']),policy_id=policy_id)
                request=dict(format=1,context_source=source,policy_id=policy_id,target=target,
                    rows=[dict(hi=o['hi'],lo=o['lo'],n=o['n'],p=row) for o,row in zip(obs,p)],
                    pairs=[doc['pairs'][i]['cards'] for i in (0,495,989)],seeds=list(range(9282801,9282805)))
                result=run(name,doc,request);reports.append(dict(case=name,zero_own_changed=changed,weight_control=w,**result))
                if negative_request is None:negative_request=request
                assert time.monotonic()-start<600
                print(json.dumps(dict(case=name,passed=True,full_hits=result['full_root_replacements'])),flush=True)
        assert weight_rejections>0 and sum(r['full_root_replacements'] for r in reports)>0
        negatives=[]
        edits=[('arity',lambda x:x['target'].__setitem__('n',4)),('padding',lambda x:x['target']['values'].__setitem__(3,1.)),
               ('context',lambda x:x.__setitem__('context_source',x['context_source']+' ')),('identity',lambda x:x['target'].__setitem__('policy_id','wrong')),
               ('duplicate',lambda x:x['rows'].append(x['rows'][0])),('probability',lambda x:x['rows'][0]['p'].__setitem__(0,-1.))]
        for name,edit in edits:
            req=copy.deepcopy(negative_request);edit(req);path=STORE/('bad-'+name+'.json');dest=STORE/('bad-'+name+'-native.json');write(path,req)
            proc=subprocess.run([str(EXE),str(CONTEXT),str(path),str(dest)],capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
            record=dict(case=name,rejected=proc.returncode!=0,returncode=proc.returncode,stderr=proc.stderr);write(STORE/('bad-'+name+'-process.json'),record)
            assert record['rejected'] and not dest.exists();negatives.append(dict(case=name,rejected=True))
        req=copy.deepcopy(negative_request);req['target']['values'][0]='NONFINITE_CONTROL'
        path=STORE/'bad-nonfinite.json';dest=STORE/'bad-nonfinite-native.json'
        with path.open('xb') as f:f.write((json.dumps(req,separators=(',',':')).replace('"NONFINITE_CONTROL"','1e999')+'\n').encode())
        proc=subprocess.run([str(EXE),str(CONTEXT),str(path),str(dest)],capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
        write(STORE/'bad-nonfinite-process.json',dict(returncode=proc.returncode,stderr=proc.stderr))
        assert proc.returncode!=0 and not dest.exists();negatives.append(dict(case='nonfinite',rejected=True))
        verify(inputs)
        write(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),cases=reports,negative_controls=negatives,
            double_weight_controls_rejected=weight_rejections,seconds=time.monotonic()-start,gpu_used=False,training=False,production_modified=False,
            evidence_bytes_before_result=sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())))
        print(json.dumps(dict(passed=True,cases=len(reports),seconds=time.monotonic()-start)),flush=True)
    except Exception as e:write(FAILURE,dict(error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
