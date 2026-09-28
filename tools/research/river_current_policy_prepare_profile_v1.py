"""CPU-only profile of unchanged qualified query preparation."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import cProfile
import hashlib
import json
from pathlib import Path
import pstats
import sys
import time
import traceback
import numpy as np
from river_current_policy_math_v1 import CurrentPolicy
from board_training_checkpoint_v1 import model_document,validate_model
from board_training_policy_v1 import RootTable
from weighted_preflop_table_v1 import Table
from preflop_allin_matrix_v1 import AllinMatrix

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-current-policy-prepare-profile-v1'
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');FAILURE=OUT/(NAME+'-failure.json')
PILOT=OUT/'river-current-policy-pilot-v1-result.json';PILOT_REG=OUT/'river-current-policy-pilot-v1-registration.json'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(path,value):
    data=(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode();assert len(data)<1_000_000
    with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())


def main():
    assert not any(p.exists() for p in (REG,RESULT,FAILURE));start=time.monotonic()
    result=read(PILOT);reg=read(PILOT_REG);assert result['passed'] and result['complete'] and result['registration_sha256']==sha(PILOT_REG)
    identity=reg['policies'][0];cases=[next(c for c in result['cases'] if c['case']==n) for n in ('p0-check','p1-jam-raise')]
    inputs=dict(reg['inputs']);inputs.update({str(p):sha(p) for p in (Path(__file__),PILOT,PILOT_REG)})
    for c in cases:
        assert sha(c['export_path'])==c['export_sha256'];inputs[c['export_path']]=c['export_sha256']
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f and Path(f).is_relative_to(ROOT) and Path(f).suffix=='.py':inputs[str(f)]=sha(f)
    for p,h in inputs.items():assert sha(p)==h,p
    write(REG,dict(inputs=inputs,cases=[c['case'] for c in cases],policy_id=identity['policy_id'],cpu_only=True,
        maximum_seconds=120,maximum_added_bytes=2_000_000,scope='cProfile call attribution of unchanged preparation, no changed policy, labels or fitting.',
        created_unix=time.time(),storage_basis='Immediately preceding bounded pilot admitted 100 MB with >80 GB margin; this profile adds <2 MB only.'))
    try:
        source=(OUT/'bb-context-candidate.json').read_text();cp=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
        mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
        args=dict(catalog_source=cp.read_text(),matrix_sha256=sha(mp),entry_mass=AllinMatrix(read(mp),source).btn_mass,root_config=identity['root_config'])
        model=model_document(identity['folder'],identity['reference'],context_source=source,**args)
        root,_,exact=validate_model(model,context_source=source,**args)
        # Prepare does not access the inference weights. Construct its exact CPU
        # state without allocating CUDA merely to profile CPU code.
        engine=object.__new__(CurrentPolicy);engine.context_source=source
        engine.tables=[Table(t,source) for t in model['preflop_tables'] if t is not None]+[exact,RootTable(root,source,args['catalog_source'])]
        reports=[]
        for case in cases:
            query=read(case['export_path'])['queries'];reference=engine.prepare(query)
            profiler=cProfile.Profile();t=time.perf_counter();candidate=profiler.runcall(engine.prepare,query);wall=time.perf_counter()-t
            for key in ('table','mask','arity'):assert np.array_equal(candidate[key],reference[key])
            for key in ('features','actors','legal','prior','action','valid'):assert np.array_equal(getattr(candidate['arrays'],key),getattr(reference['arrays'],key))
            stats=pstats.Stats(profiler);rows=[]
            for (filename,line,name),(primitive,calls,own,total,_) in stats.stats.items():
                rows.append(dict(file=filename,line=line,function=name,primitive_calls=primitive,calls=calls,self_seconds=own,cumulative_seconds=total))
            rows.sort(key=lambda r:r['cumulative_seconds'],reverse=True)
            reports.append(dict(case=case['case'],rows=len(query['observations']),profiled_seconds=wall,top=rows[:45],prepared_arrays_identical=True))
        for p,h in inputs.items():assert sha(p)==h,p
        assert time.monotonic()-start<120
        write(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),reports=reports,seconds=time.monotonic()-start,gpu_used=False,production_modified=False))
        print(json.dumps(dict(passed=True,seconds=time.monotonic()-start,profiles=[dict(case=r['case'],top=r['top'][:10]) for r in reports])),flush=True)
    except Exception as e:write(FAILURE,dict(error=repr(e),traceback=traceback.format_exc()));raise


if __name__=='__main__':main()
