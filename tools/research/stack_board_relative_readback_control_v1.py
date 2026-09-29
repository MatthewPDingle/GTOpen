"""CPU qualification of independent inference using retained probes, not labels."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import argparse,hashlib,json,time,traceback,uuid
from pathlib import Path
import numpy as np
import psutil
import torch
from board_prefix_publication_v1 import atomic_json
from stack_board_relative_readback_v1 import dense_scores,call_probability
from stack_board_relative_model_v1 import load_models
from stack_price_learning_fit_v1 import scores
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK,OTHER

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
REG=OUT/'stack-board-relative-readback-control-v1-registration.json'
RESULT=OUT/'stack-board-relative-readback-control-v1-result.json'
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main(run):
    proof=OUT/'stack-board-relative-model-control-v1-result.json';previous=read(proof)
    probe=Path('S:/GTOpen-research/stack-board-relative-model-control-v1/probe-inputs.npz')
    assert previous['passed'] and previous['cpu_initial_outputs_exact']
    for path,h in previous['artifacts'].items():assert sha(path)==h,path
    paths=[Path(__file__),ROOT/'tools/research/stack_board_relative_readback_v1.py',
        ROOT/'tools/research/stack_board_relative_model_v1.py',ROOT/'tools/research/stack_price_learning_fit_v1.py',proof,probe]
    paths.extend(Path(ref['file']) for r in previous['records'] for ref in r['round_trips'])
    spec=dict(inputs={str(p):sha(p) for p in paths},maximum_seconds=60,
        maximum_score_error=1e-6,synthetic_extension_seed=9296903,
        new_training=False,new_test_data=False,gpu_used=False)
    if not run:print(json.dumps(dict(preflight_passed=True)));return
    assert not any(p.exists() for p in (REG,RESULT,LOCK,OTHER))
    assert production_available() and psutil.cpu_percent(interval=1)<50
    assert psutil.virtual_memory().available>28_000_000_000
    started=time.monotonic()
    with LOCK.open('x') as stream:stream.write(str(os.getpid()))
    try:
        atomic_json(REG,spec);torch.set_num_threads(1)
        with np.load(probe,allow_pickle=False) as z:x=z['features'].copy();actors=z['actors'].copy()
        assert x.shape==(960,387) and set(actors)=={0,1}
        records=[];rng=np.random.default_rng(spec['synthetic_extension_seed'])
        for r in previous['records']:
            for width,ref in zip((362,387),r['round_trips']):
                model=load_models(ref,r['seed'],width,'cpu')
                variants=('original',) if width==362 else ('original','synthetic_nonzero_extension')
                for variant in variants:
                    if variant!='original':
                        with torch.no_grad():
                            for head in model:
                                head[0].weight[:,362:].copy_(torch.from_numpy(rng.normal(0,.03,(64,25)).astype('float32')))
                    weights={f'p{a}.{k}':v.detach().numpy().copy() for a,m in enumerate(model) for k,v in m.state_dict().items()}
                    selected=x[:,:width].copy()
                    with torch.no_grad():expected=scores(model,torch.from_numpy(selected),torch.from_numpy(actors)).numpy()
                    actual=np.empty_like(expected)
                    for actor in (0,1):actual[actors==actor]=dense_scores(weights,selected[actors==actor],actor,width)
                    error=float(np.max(abs(actual-expected)));assert error<spec['maximum_score_error'],error
                    records.append(dict(seed=r['seed'],width=width,variant=variant,rows=len(x),maximum_score_error=error))
        edge=np.asarray([[2,0],[1,3],[0,3],[-1,-1],[-2,-1],[0,0]],dtype='float32')
        assert np.array_equal(call_probability(edge),[0,.75,1,0,1,0])
        for bad in (np.array([[np.nan,1]]),np.array([[1,np.inf]])):
            try:call_probability(bad)
            except AssertionError:pass
            else:raise AssertionError('Nonfinite predictions accepted')
        assert not torch.cuda.is_initialized()
        for p,h in spec['inputs'].items():assert sha(p)==h,p
        elapsed=time.monotonic()-started;assert elapsed<spec['maximum_seconds']
        assert production_available() and not OTHER.exists() and psutil.virtual_memory().available>24_000_000_000
        result=dict(passed=True,registration_sha256=sha(REG),records=records,
            maximum_score_error=max(r['maximum_score_error'] for r in records),rows=sum(r['rows'] for r in records),
            policy_edge_cases=6,nonfinite_cases_rejected=2,seconds=elapsed,
            synthetic_weights_only=True,new_training=False,new_test_data=False,gpu_used=False,production_modified=False)
        atomic_json(RESULT,result);print(json.dumps(result),flush=True)
    except BaseException as error:
        atomic_json(OUT/('stack-board-relative-readback-control-v1-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),traceback=traceback.format_exc()))
        raise
    finally:
        assert LOCK.read_text()==str(os.getpid());LOCK.unlink()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');main(p.parse_args().run)
