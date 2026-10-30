"""Register and qualify board selection, independent metrics, and data preparation."""
import time
START=time.monotonic()
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',CUDA_VISIBLE_DEVICES='-1')
import io,json,sys,traceback,uuid
from contextlib import redirect_stdout
from pathlib import Path
import numpy as np
import torch
import river_matched_training_pilot_v1 as pilot
import stack_board_balanced_sampler_control_v1 as sampler_control
import stack_board_balanced_metrics_control_v1 as metric_control
from stack_board_balanced_data_v1 import prepare,load,extended_context,cpu_admission,Guard
from stack_board_balanced_sampler_v1 import board_cell
from stack_price_learning_data_v2 import public_factors
from stack_price_reference_control_v1 import NATIVE,RANKS

OUT,ROOT=pilot.OUT,pilot.ROOT
STORE=Path('S:/GTOpen-research/stack-board-balanced-control-v1')
OLD=OUT/'stack-board-relative-learning-v1-prepared.json'
OLDREG=OUT/'stack-board-relative-learning-v1-registration.json'
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
read,sha,write=pilot.read,pilot.sha,pilot.atomic_json

def progress(state,**values):print(json.dumps(dict(state=state,**values)),flush=True)

def sources():
    paths=[Path(__file__),NATIVE,RANKS,OLD,OLDREG,
        OUT/'STACK-BOARD-BALANCED-COVERAGE-PROPOSAL.md',OUT/'STACK-BOARD-BALANCED-IMPLEMENTATION.md']
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    # Freeze all new source files, including readback-only dependencies.
    paths.extend((ROOT/'tools/research').glob('stack_board_balanced_*_v1.py'))
    paths.append(ROOT/'tools/research/stack_board_relative_readback_v1.py')
    return {str(p):sha(p) for p in paths}

def control(kind,inputs,action):
    name='stack-board-balanced-'+kind+'-control-v1'
    rp,dest=(OUT/(name+suffix+'.json') for suffix in ('-registration','-result'))
    assert not rp.exists() and not dest.exists(),'Preserve completed or failed control evidence'
    write(rp,dict(inputs=inputs,kind=kind,maximum_seconds=120,synthetic_or_retained_data_only=True,
        new_scientific_fits=False,production_modified=False))
    try:
        result=action()
        pilot.verify(inputs)
        assert time.monotonic()-START<120 and not torch.cuda.is_initialized()
        result.update(passed=True,registration_sha256=sha(rp),seconds_since_invocation=time.monotonic()-START,
            gpu_used=False,new_scientific_fits=False,production_modified=False)
        assert 'retained_board_groups' in result
        write(dest,result)
        progress('control_passed',kind=kind,seconds=result['seconds_since_invocation'])
        return result
    except BaseException as error:
        write(dest,dict(passed=False,registration_sha256=sha(rp),error=repr(error),traceback=traceback.format_exc()))
        raise

def main():
    probe=cpu_admission()
    assert probe['admitted'],probe
    assert not STORE.exists()
    assert not any(OUT.glob('stack-board-balanced-*-control-v1-registration.json'))
    old=read(OLDREG)
    historical=set(map(tuple,old['excluded_probe_groups']))|{tuple(b['canonical_group']) for b in old['boards']}
    assert len(historical)==788
    records=[b for b in read(OLD)['records'] if b['split']=='fit'][:2]
    assert len(records)==2
    inputs=sources()
    for r in records:
        assert sha(r['file'])==r['sha256'] and sha(r['extra_file'])==r['extra_sha256']
        inputs.update({r['file']:r['sha256'],r['extra_file']:r['extra_sha256']})
    for depth in (20,40,100,200,400,60,150):
        p=GEOMETRY/f'stack-{depth}-public.json';inputs[str(p)]=sha(p)
    with pilot.LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        pilot.create(STORE)
        def sampler():
            deadline=START+60
            fixture=sampler_control.fixture_checks(deadline)
            retained=fixture['retained_fixture_canonical_groups']
            exclusions=sorted(historical|set(map(tuple,retained)))
            boards,qualification=sampler_control.qualify(9297100,exclusions,deadline)
            manifest=OUT/'stack-board-balanced-sampler-control-v1-boards.json'
            write(manifest,boards)
            return dict(fixtures=fixture,qualification=qualification,retained_board_groups=retained,
                excluded_probe_groups=exclusions,board_manifest=dict(file=str(manifest),sha256=sha(manifest)),
                new_equity_labels=0)
        sampling=control('sampler',inputs,sampler)
        def metrics():
            text=io.StringIO()
            with redirect_stdout(text):metric_control.run()
            result=json.loads(text.getvalue())
            assert result['passed'] and result['synthetic_only']
            return dict(synthetic=result,retained_board_groups=[])
        control('metrics',inputs,metrics)
        def data():
            guard=Guard(STORE,120-(time.monotonic()-START),progress)
            tasks=[dict(split='fit_random',index=i,board=r['board'],canonical_group=r['canonical_group'],cell=board_cell(r['board'])) for i,r in enumerate(records)]
            rebuilt,timing=prepare(tasks,STORE,guard,progress)
            arrays=0
            for original,new in zip(records,rebuilt):
                for left,right in ((original['file'],new['file']),(original['extra_file'],new['extra_file'])):
                    with np.load(left,allow_pickle=False) as a,np.load(right,allow_pickle=False) as b:
                        assert a.files==b.files
                        for name in a.files:assert np.array_equal(a[name],b[name]),name;arrays+=1
            loaded=load(rebuilt)
            assert len(loaded)==2 and all(b['features'].shape==(1081,387) for b in loaded)
            contexts=0
            for depth in (20,40,100,200,400,60,150):
                base=public_factors(read(GEOMETRY/f'stack-{depth}-public.json'))
                extended=extended_context(base)
                assert np.array_equal(base['features'],extended['features'][:,:362])
                assert not np.any(extended['features'][:,362:])
                assert np.array_equal(base['economics'],extended['economics'])
                contexts+=1
            guard()
            return dict(retained_board_groups=[r['canonical_group'] for r in records],records=rebuilt,
                exact_arrays=arrays,contexts_checked=contexts,workers=timing,independent_old_arrays_equal=True,
                artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()})
        control('data',inputs,data)
        assert pilot.study_measure(STORE)['logical_bytes']<8_000_000
        progress('all_controls_passed',seconds=time.monotonic()-START)
    finally:
        assert pilot.LOCK.read_text()==str(os.getpid());pilot.LOCK.unlink()

if __name__=='__main__':main()
