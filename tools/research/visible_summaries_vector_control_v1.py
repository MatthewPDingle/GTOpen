"""Register and compare batched summaries/preparation with frozen references."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
from sampled_visible_poker_features_v1 import visible_summaries
from sampled_visible_features_bulk_v1 import features as reference_features
from visible_summaries_vector_v1 import summaries,features
from river_query_preparation_vector_v1 import prepare
from river_current_policy_math_v1 import CurrentPolicy
from board_training_checkpoint_v1 import model_document,validate_model
from board_training_policy_v1 import RootTable
from weighted_preflop_table_v1 import Table
from preflop_allin_matrix_v1 import AllinMatrix

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='visible-summaries-vector-control-v1';REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');FAILURE=OUT/(NAME+'-failure.json')
PLAN=OUT/'VISIBLE-SUMMARIES-VECTOR-PLAN.md';PILOT=OUT/'river-current-policy-pilot-v1-result.json';PILOT_REG=OUT/'river-current-policy-pilot-v1-registration.json'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):
    data=(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode();assert len(data)<1_000_000
    with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def same(a,b):assert a.dtype==b.dtype and a.shape==b.shape and a.tobytes()==b.tobytes()
def rejected(fn):
    try:fn()
    except (ValueError,AssertionError):return True
    raise AssertionError('Invalid features accepted')


def main():
    assert not any(p.exists() for p in (REG,RESULT,FAILURE));start=time.monotonic()
    pilot=read(PILOT);oldreg=read(PILOT_REG);assert pilot['passed'] and pilot['complete'] and pilot['registration_sha256']==sha(PILOT_REG)
    profile=OUT/'river-current-policy-prepare-profile-v1-result.json';assert read(profile)['passed']
    inputs=dict(oldreg['inputs']);inputs.update({str(p):sha(p) for p in (Path(__file__),PLAN,PILOT,PILOT_REG,profile)})
    for c in pilot['cases']:
        assert sha(c['export_path'])==c['export_sha256'];inputs[c['export_path']]=c['export_sha256']
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f and Path(f).is_relative_to(ROOT) and Path(f).suffix=='.py':inputs[str(f)]=sha(f)
    for p,h in inputs.items():assert sha(p)==h,p
    write(REG,dict(inputs=inputs,seed=9289992,random_examples=40000,board_lengths=[0,3,4,5],
        timing_order=['reference','vector','vector','reference'],cases=[c['case'] for c in pilot['cases']],
        required='Bitwise identical float32 features and all float64/integer/bool preparation arrays; both implementations reject malformed features.',
        maximum_seconds=180,maximum_added_bytes=2_000_000,gpu_used=False,production_modified=False,
        storage_basis='Uses under 2 MB of the preceding pilot allocation allowance; no new dataset archive.',created_unix=time.time()))
    try:
        rng=np.random.Generator(np.random.PCG64(9289992));cards=[]
        for count in (0,3,4,5):
            for _ in range(10000):
                c=rng.choice(52,size=2+count,replace=False).tolist();cards.append(c+[52]*(5-count))
        crafted=[[48,44,40,36,32,1,6],[48,0,4,8,12,21,26],[48,49,50,51,44,9,14],
                 [48,49,50,44,45,46,3],[48,24,44,36,4,1,10],[48,1,6,11,12,29,34],
                 [48,49,50,44,43,1,6],[48,49,44,45,40,41,3],[48,49,44,41,38,15,0],
                 [48,45,38,31,20,9,2],[1,6,32,36,40,44,48]]
        for c in crafted:
            for perm in itertools.permutations(range(4)):
                transformed=[x//4*4+perm[x%4] for x in c]
                cards.extend([transformed,transformed[:2][::-1]+transformed[2:][::-1]])
        data=np.asarray(cards,dtype=np.int16);t=time.perf_counter();expected=np.asarray([visible_summaries(c[:2],[x for x in c[2:] if x<52]) for c in cards]);scalar=time.perf_counter()-t
        t=time.perf_counter();candidate=summaries(data);vector=time.perf_counter()-t;same(expected,candidate)
        categories=sorted(set(candidate[40000:,:9].argmax(1).tolist()));assert categories==list(range(9))
        identity=oldreg['policies'][0];source=(OUT/'bb-context-candidate.json').read_text()
        cp=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json');mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
        args=dict(catalog_source=cp.read_text(),matrix_sha256=sha(mp),entry_mass=AllinMatrix(read(mp),source).btn_mass,root_config=identity['root_config'])
        model=model_document(identity['folder'],identity['reference'],context_source=source,**args);root,_,exact=validate_model(model,context_source=source,**args)
        engine=object.__new__(CurrentPolicy);engine.context_source=source
        engine.tables=[Table(t,source) for t in model['preflop_tables'] if t is not None]+[exact,RootTable(root,source,args['catalog_source'])]
        reports=[];base=None
        for c in pilot['cases']:
            doc=read(c['export_path']);query=doc['queries'];obs=query['observations']
            if base is None:base=copy.deepcopy(next(o for o in obs if o['phase']==3))
            same(reference_features(obs),features(obs));first=engine.prepare(query);second=prepare(engine,query)
            for k in ('table','mask','arity'):same(first[k],second[k])
            for k in ('features','actors','legal','prior','action','valid'):
                same(getattr(first['arrays'],k),getattr(second['arrays'],k));assert not getattr(second['arrays'],k).flags.writeable
            timing=[]
            for kind in ('reference','vector','vector','reference'):
                t=time.perf_counter();prepared=engine.prepare(query) if kind=='reference' else prepare(engine,query)
                timing.append(dict(kind=kind,seconds=time.perf_counter()-t))
            reports.append(dict(case=c['case'],rows=len(obs),bitwise_identical=True,timing=timing))
        bad=[]
        for name,edit in (
            ('short',lambda a:a.pop()),('boolean',lambda a:a.__setitem__(0,True)),
            ('float',lambda a:a.__setitem__(0,float(a[0]))),('overflow',lambda a:a.__setitem__(0,65536)),
            ('duplicate_group',lambda a:a.__setitem__(1,a[0])),('missing_mismatch',lambda a:a.__setitem__(0,13)),
            ('future_card',lambda a:a.__setitem__(15,135)),('history_gap',lambda a:a.__setitem__(17,155)),
            ('duplicate_card',lambda a:(a.__setitem__(2,19+a[0]),a.__setitem__(3,19+a[1])))):
            o=copy.deepcopy(base);edit(o['active_features'])
            bad.append(dict(case=name,reference_rejected=rejected(lambda:reference_features([o])),vector_rejected=rejected(lambda:features([o]))))
        same(reference_features([]),features([]));same(summaries(np.empty((0,7),dtype=np.int16)),np.empty((0,33),dtype=np.float32))
        for p,h in inputs.items():assert sha(p)==h,p
        old=sum(t['seconds'] for r in reports for t in r['timing'] if t['kind']=='reference')
        new=sum(t['seconds'] for r in reports for t in r['timing'] if t['kind']=='vector')
        assert time.monotonic()-start<180
        write(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),direct_examples=len(cards),crafted_categories=categories,
            direct_features_identical=True,direct_scalar_seconds=scalar,direct_vector_seconds=vector,direct_speedup=scalar/vector,
            cases=reports,invalid_controls=bad,reference_preparation_seconds=old,vector_preparation_seconds=new,
            preparation_speedup=old/new,faster=new<old,seconds=time.monotonic()-start,gpu_used=False,production_modified=False,
            scope='Visible summary and CPU preparation equivalence/performance only; no changed policy, training target or integrated solver speedup.'))
        print(json.dumps(dict(passed=True,examples=len(cards),cases=len(reports),direct_speedup=scalar/vector,preparation_speedup=old/new,seconds=time.monotonic()-start)),flush=True)
    except Exception as e:write(FAILURE,dict(error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-start));raise


if __name__=='__main__':main()
