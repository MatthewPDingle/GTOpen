"""Registered, bounded native river bridge controls; no training or production writes."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
import zipfile
import numpy as np
import psutil
from river_full_action_math_v1 import digest,validate_document,probabilities,evaluate,observation
from board_river_opponent_reach_math_v1 import posterior
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS

ROOT=Path('T:/Dev/GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-full-action-control-v1'
STORE=OUT/NAME
OLD=Path('S:/GTOpen-research/board-river-target-learning-v1')
CONTEXT=OUT/'bb-context-candidate.json'
EXE=ROOT/'target/release/examples/hu_river_action_queries_v1.exe'
SELECTION=OUT/'board-river-target-learning-v1-selection.json'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
PLAN=OUT/'RIVER-FULL-ACTION-CONTROL-PLAN.md'
REG=OUT/(NAME+'-registration.json')
RESULT=OUT/(NAME+'-result.json')
FAILURE=OUT/(NAME+'-failure.json')
LIMIT=100_000_000
CASES=[
    ('p0-raise','d000-p0-under10-0',None),
    ('p0-no-raise','d000-p0-100to200-0',None),
    ('p1-raise','d000-p1-under10-0',None),
    ('p1-no-raise','d000-p1-100to200-0',None),
    ('p0-check','d000-p0-under10-0','9223372036859602130'),
    ('p1-check','d000-p1-under10-0','9223372036893386386'),
    ('p0-facing-allin','d000-p0-200plus-1',None),
    ('p1-facing-allin','d001-p1-200plus-0',None),
]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def added():return sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())+sum(p.stat().st_size for p in (REG,RESULT,FAILURE) if p.exists())
def write(p,value):
    data=(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    assert added()+len(data)<=LIMIT
    with Path(p).open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())


def archive(case):
    manifest=read(OLD/'cases'/(case+'.manifest.json'));path=OLD/'cases'/(case+'.zip')
    assert sha(path)==manifest['archive_sha256']
    with zipfile.ZipFile(path) as z:
        info=z.infolist();assert len(info)==4 and {i.filename for i in info}=={'request.json','export.json','policies.npz','record.json'}
        assert sum(i.file_size for i in info)<=32_000_000
        raw={i.filename:z.read(i.filename) for i in info}
    for name,data in raw.items():
        m=manifest['members'][name];assert len(data)==m['bytes'] and hashlib.sha256(data).hexdigest()==m['sha256']
    return json.loads(raw['request.json']),json.loads(raw['export.json'])


def policy(rows,mode):
    values=[]
    for o in rows:
        if mode=='uniform':weights=[1.]*o['n']
        else:
            # Only the identified visible information key and legal action index.
            weights=[1+int.from_bytes(hashlib.sha256(f"visible-policy-v1|{o['hi']}|{o['lo']}|{a}".encode()).digest()[:2],'big')%31 for a in range(o['n'])]
        total=sum(weights);values.append([w/total for w in weights]+[0.]*(4-o['n']))
    return values


def bundle(doc,p,identity):
    return dict(policy_id=identity,context_source=doc['context_source'],query_sha256=digest(doc['queries']),
                probabilities_sha256=digest(p),probabilities=p)


def reject(fn):
    try:fn()
    except (AssertionError,ValueError,KeyError,IndexError):return True
    raise AssertionError('Negative control was accepted')


def run_export(name,context_path,request):
    request_path=STORE/(name+'-request.json');dest=STORE/(name+'-export.json')
    write(request_path,request)
    # Native executable has a 64 MB output cap; reserve the entire cap before launch.
    assert added()+64_000_000<=LIMIT
    start=time.perf_counter()
    proc=subprocess.run([str(EXE),str(context_path),str(request_path),str(dest)],capture_output=True,text=True,timeout=60)
    write(STORE/(name+'-native.json'),dict(code=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,seconds=time.perf_counter()-start))
    assert proc.returncode==0 and dest.exists();assert added()<=LIMIT
    return read(dest)


def case_control(name,request,old,context_path,zero_rake=False):
    start=time.perf_counter();context_source=context_path.read_text();doc=run_export(name,context_path,request)
    checks=validate_document(doc,context_source)
    assert doc['target']['cards']==old['target']['cards'] and doc['target']['actor']==old['target']['actor']
    assert [(p['cards'],p['outcome_loss_tie_win']) for p in doc['pairs']]==[(p['cards'],p['outcome_loss_tie_win']) for p in old['pairs']]
    prior=PhysicalDeals(context_source,mode='full_deck',seed=0).weights
    entry=[{tuple(map(int,p)):float(w) for p,w in zip(PAIRS,row)} for row in prior]
    root=doc['nodes'][doc['pairs'][0]['root']];kinds=[a['kind'] for a in root['actions']]
    if 'check' in name:assert kinds[0]=='check'
    else:assert kinds[:2]==['fold','call']
    if name.endswith('-raise') and not name.endswith('no-raise'):assert 'raise' in kinds
    if name.endswith('no-raise'):assert len(kinds)==2
    if 'facing-allin' in name:assert kinds==['fold','call'] and root['actions'][1]['all_in']
    records=[];zero_controls=[]
    for mode in ('uniform','visible'):
        identity='native-control-'+mode+'-v1';p=policy(doc['queries']['observations'],mode)
        b=bundle(doc,p,identity);v=evaluate(doc,b,entry,expected_policy_id=identity,expected_context_source=context_source)
        assert v['supported'] and v['own_history_likelihood']>0
        delta_error=posterior_error=None
        if kinds[:2]==['fold','call'] and not zero_rake:
            original=policy(old['queries']['observations'],mode);index={(o['hi'],o['lo']):i for i,o in enumerate(doc['queries']['observations'])}
            for o,row in zip(old['queries']['observations'],original):assert row==p[index[(o['hi'],o['lo'])]]
            reference,detail=posterior(old,original,prior)
            delta_error=abs((v['action_values'][1]-v['action_values'][0])-reference['call_minus_fold_bb'])
            posterior_error=float(np.max(abs(np.asarray(v['posterior'])-detail['posterior'])))
            assert delta_error<1e-9 and posterior_error<1e-12
        records.append(dict(mode=mode,policy_id=identity,query_sha256=b['query_sha256'],probabilities_sha256=b['probabilities_sha256'],
            action_values=v['action_values'],value=v['value'],regrets=v['regrets'],opponent_mass=v['opponent_mass'],
            own_likelihood=v['own_history_likelihood'],path_error=v['maximum_path_value_error'],
            old_fold_call_error=delta_error,old_posterior_error=posterior_error))
        # An actually taken earlier hero action becomes probability zero. It is
        # excluded from the opponent posterior and cannot remove this target.
        my=[link for link in doc['pairs'][0]['path'] if doc['queries']['observations'][link[0]]['actor']==doc['target']['actor']]
        assert my;prior_index,action,n=my[0];changed=copy.deepcopy(p);changed[prior_index]=[1/(n-1) if a<n and a!=action else 0. for a in range(4)]
        zero_id=identity+'-zero-own-reach';zb=bundle(doc,changed,zero_id)
        z=evaluate(doc,zb,entry,expected_policy_id=zero_id,expected_context_source=context_source)
        assert z['supported'] and z['own_history_likelihood']==0 and z['action_values']==v['action_values'] and z['posterior']==v['posterior']
        zero_controls.append(dict(mode=mode,supported=True,own_likelihood=0.,action_values_unchanged=True))
    p=policy(doc['queries']['observations'],'visible');b=bundle(doc,p,'negative-control-policy')
    def read_prob(value=b,source=context_source,identity='negative-control-policy'):
        return probabilities(doc,value,expected_policy_id=identity,expected_context_source=source)
    negatives={
        'wrong_policy':reject(lambda:read_prob(identity='other-policy')),
        'wrong_context':reject(lambda:read_prob(source=context_source+' ')),
    }
    q=copy.deepcopy(b);q['query_sha256']='0'*64;negatives['wrong_queries']=reject(lambda:read_prob(q))
    q=copy.deepcopy(b);q['probabilities'][0][0]+=0.01;negatives['mutated_probabilities']=reject(lambda:read_prob(q))
    i=next(i for i,o in enumerate(doc['queries']['observations']) if o['n']<4);q=copy.deepcopy(b)
    q['probabilities'][i]=[0.,0.,0.,1.];q['probabilities_sha256']=digest(q['probabilities'])
    negatives['illegal_action_probability']=reject(lambda:read_prob(q))
    q=copy.deepcopy(b);q['probabilities'][i]=[0.1]*4;q['probabilities_sha256']=digest(q['probabilities'])
    negatives['unnormalized_probability']=reject(lambda:read_prob(q))
    zero_entry=[{pair:0. for pair in e} for e in entry]
    unsupported=evaluate(doc,b,zero_entry,expected_policy_id='negative-control-policy',expected_context_source=context_source)
    assert not unsupported['supported'] and unsupported['opponent_mass']==0 and 'action_values' not in unsupported
    record=dict(name=name,checks=checks,root_actions=root['actions'],policies=records,zero_own_reach=zero_controls,
        negative_controls=negatives,zero_opponent_support_explicit=True,export_sha256=sha(STORE/(name+'-export.json')),seconds=time.perf_counter()-start)
    write(STORE/(name+'-checks.json'),record);return record


def main():
    start=time.monotonic();assert not any(p.exists() for p in (STORE,REG,RESULT,FAILURE,LOCK,OTHER))
    assert psutil.virtual_memory().available>=24*1024**3 and shutil.disk_usage(OUT).free>=2_000_000_000
    cases={c['case_id']:c for c in read(SELECTION)['cases']};fixtures=[];inputs={}
    query_path=OLD/'selection/deal-000-queries.json';free_rows=read(query_path)['observations']
    for name,case_id,override in CASES:
        c=cases[case_id];assert c['split']=='train';request,old=archive(case_id)
        assert (request['hi'],request['lo'])==(c['hi'],c['lo'])
        if override:
            choices=[o for o in free_rows if o['hi']==override and o['lo']==request['lo']];assert len(choices)==1
            decoded=observation(choices[0]);tail=decoded[4][len(decoded[4])-decoded[4][::-1].index(5):]
            assert tail==([] if c['actor']==0 else [1]);request['hi']=override
        fixtures.append((name,request,old))
        for suffix in ('.zip','.manifest.json'):
            p=OLD/'cases'/(case_id+suffix);inputs[str(p)]=sha(p)
    # Hash every local imported Python module, plus the native transitive sources.
    paths=[Path(__file__),PLAN,OUT/'BOARD-RIVER-FULL-ACTION-BRIDGE-PLAN.md',EXE,CONTEXT,SELECTION,query_path,
           ROOT/'crates/solver/examples/hu_river_action_queries_v1.rs',ROOT/'Cargo.lock']
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f and Path(f).is_relative_to(ROOT) and Path(f).suffix=='.py':paths.append(Path(f))
    paths.extend((ROOT/'crates/solver/examples/research_sampled').glob('*.rs'))
    paths.extend((ROOT/'crates/solver/src/evaluator').rglob('*.rs'))
    paths.extend((ROOT/'crates/solver/src/tree').rglob('*.rs'))
    for p in paths:inputs[str(p)]=sha(p)
    STORE.mkdir();acquired=False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        write(REG,dict(format=1,created_unix=time.time(),inputs=inputs,cases=[dict(name=n,request=r) for n,r,_ in fixtures],
            caps=dict(total_seconds=600,native_timeout_seconds=60,added_bytes=LIMIT,native_bytes=64_000_000,queries=250_000,nodes=500_000),
            policies=['uniform','visible-key-sha256-positive-v1','zero-own-ancestral-action'],
            extra_zero_rake_case='p0-raise',gpu_used=False,training=False,production_modified=False,
            python=sys.version,numpy=np.__version__,hardware_sharing='CPU-only bounded checks; other applications remain running.'))
        records=[]
        for name,request,old in fixtures:
            assert time.monotonic()-start<600 and psutil.virtual_memory().available>=24*1024**3
            records.append(case_control(name,request,old,CONTEXT))
            print(json.dumps(dict(case=name,passed=True,seconds=records[-1]['seconds'])),flush=True)
        context=read(CONTEXT);context['rake_fraction']=0.;context['rake_cap']=0.;zero_path=STORE/'zero-rake-context.json';write(zero_path,context)
        records.append(case_control('p0-raise-zero-rake',fixtures[0][1],fixtures[0][2],zero_path,zero_rake=True))
        request=fixtures[0][1];bad=[('unknown-field',dict(request,unexpected=True)),('invalid-card',dict(request,lo=str(62))) ]
        h=int(request['hi']);encoded=(h&((1<<63)-1))>>4
        bad.append(('terminal-history',dict(request,hi=str((1<<63)|(((encoded<<3)|1)<<4)|(h&15)))))
        rejections=[]
        for name,req in bad:
            source=STORE/(name+'-request.json');dest=STORE/(name+'-must-not-exist.json');write(source,req)
            proc=subprocess.run([str(EXE),str(CONTEXT),str(source),str(dest)],capture_output=True,text=True,timeout=60)
            assert proc.returncode!=0 and not dest.exists();rejections.append(dict(case=name,rejected=True,code=proc.returncode,stderr=proc.stderr))
        assert time.monotonic()-start<600
        for p,h in inputs.items():assert sha(p)==h,p
        combined=set().union(*(set(r['checks']['action_types']) for r in records));assert combined=={'check','fold','call','bet','raise'}
        assert sum(r['checks']['tie_terminals'] for r in records)>0 and sum(r['checks']['all_in_edges'] for r in records)>0
        write(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),cases=records,native_rejections=rejections,
            seconds=time.monotonic()-start,retained_bytes_before_result=added(),gpu_used=False,training=False,production_modified=False,
            scope='Full native river exporter and finite policy evaluator only; not an integrated sampled walker or evidence of better preflop ranges.'))
        assert added()<=LIMIT
        print(json.dumps(dict(passed=True,cases=len(records),seconds=time.monotonic()-start,retained_bytes=added())),flush=True)
    except Exception as e:
        write(FAILURE,dict(error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-start));raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
