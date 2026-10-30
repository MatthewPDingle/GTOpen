"""CPU controls for neutral extension, gradient wiring and checkpoint identity."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import argparse,hashlib,json
from pathlib import Path
import sys,time,traceback,uuid
import numpy as np
import psutil
import torch
from stack_board_relative_model_v1 import fresh,load_models,MODEL_TYPE
from stack_price_learning_fit_v1 import scores,save_models
from stack_price_learning_data_v2 import card_factors,public_factors
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import create,measure
from global_research_inventory_v3 import measure as inventory
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK,OTHER

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='stack-board-relative-model-control-v1';STORE=Path('S:/GTOpen-research')/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main(run):
    feature_result=OUT/'stack-board-relative-feature-control-v1-result.json';f=read(feature_result)
    fr=OUT/'stack-board-relative-feature-control-v1-registration.json'
    assert f['passed'] and f['maximum_oracle_error']==0 and f['registration_sha256']==sha(fr)
    for p,h in read(fr)['inputs'].items():assert sha(p)==h,p
    invproof=OUT/'global-research-inventory-v3-control-v2.json';ip=OUT/'global-research-inventory-v3-registration-v2.json'
    assert read(invproof)['passed'] and read(invproof)['registration_sha256']==sha(ip)
    for p,h in read(ip)['inputs'].items():assert sha(p)==h
    paths=[Path(__file__),feature_result,fr,invproof,ip,OUT/'STACK-BOARD-RELATIVE-IMPLEMENTATION.md']
    paths.extend(Path(r['file']) for r in f['records'])
    paths.extend(GEOMETRY/f'stack-{d}-public.json' for d in (20,40,100,200,400))
    for m in list(sys.modules.values()):
        p=getattr(m,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    spec=dict(inputs={str(p):sha(p) for p in paths},model_type=MODEL_TYPE,seeds=[9296901,9296902],
        widths=[362,387],maximum_seconds=600,maximum_new_bytes=32_000_000,reserve_bytes=32_000_000,
        probe_indices=[0,1,180,360,540,720,900,1080],contexts='First and last legal river states of each fitting depth',
        checks=['exact_initial_score_and_weight_parity','extra_feature_gradient','checkpoint_round_trip',
                'wrong_hash_rejection','wrong_width_rejection','original_input_prefix','no_cuda'],
        gpu_used=False,new_policy_training=False,production_modified=False)
    if not run:print(json.dumps(dict(preflight_passed=True,widths=spec['widths'],gpu_used=False)));return
    assert not any(p.exists() for p in (REG,RESULT,STORE,LOCK,OTHER))
    assert production_available() and psutil.cpu_percent(interval=1)<50
    assert psutil.virtual_memory().available>28_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
    start=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic();assert now-start<600
        if now-last<2:return
        assert production_available() and not OTHER.exists() and psutil.virtual_memory().available>24_000_000_000
        assert psutil.disk_usage('S:/').free>40_000_000_000 and psutil.cpu_percent(interval=None)<75
        last=now
    with LOCK.open('x') as stream:stream.write(str(os.getpid()))
    try:
        accounting=inventory();assert sum(v['allocated_file_bytes'] for v in accounting)+64_000_000<=800_000_000_000
        atomic_json(REG,spec);create(STORE);atomic_json(STORE/'admission.json',dict(inventory=accounting))
        torch.set_num_threads(4);torch.use_deterministic_algorithms(True);psutil.cpu_percent(interval=None)
        public=[]
        for depth in (20,40,100,200,400):
            context=public_factors(read(GEOMETRY/f'stack-{depth}-public.json'))
            for i in (0,len(context['rows'])-1):public.append((context['features'][i],int(context['economics'][i,3])))
        xs=[];actors=[];prefix=[]
        for ref in f['records']:
            guard();assert sha(ref['file'])==ref['sha256']
            base=card_factors(ref['board'])['features']
            with np.load(ref['file'],allow_pickle=False) as z:extra=z['features'].copy()
            assert base.shape==(1081,362) and extra.shape==(1081,25)
            for i in spec['probe_indices']:
                for vector,actor in public:
                    original=base[i]+vector;extended=np.r_[original,extra[i]]
                    assert np.array_equal(extended[:362],original)
                    prefix.append(original);xs.append(extended);actors.append(actor)
        x=torch.as_tensor(np.asarray(xs),dtype=torch.float32);a=torch.as_tensor(actors,dtype=torch.long)
        assert set(actors)=={0,1};records=[]
        with (STORE/'probe-inputs.npz').open('xb') as stream:np.savez_compressed(stream,features=x.numpy(),actors=a.numpy())
        for seed in spec['seeds']:
            guard();baseline=fresh(seed,362,'cpu');candidate=fresh(seed,387,'cpu')
            for old,new in zip(baseline,candidate):
                assert torch.equal(old[0].weight,new[0].weight[:,:362]) and torch.count_nonzero(new[0].weight[:,362:])==0
                assert torch.equal(old[0].bias,new[0].bias)
                for layer in (2,4):
                    for k,v in old[layer].state_dict().items():assert torch.equal(v,new[layer].state_dict()[k])
            with torch.no_grad():
                left=scores(baseline,x[:,:362].contiguous(),a);right=scores(candidate,x,a)
            assert torch.equal(left,right),'Neutral extension changed initial predictions'
            references=[]
            for width,model in ((362,baseline),(387,candidate)):
                ref=save_models(STORE/f'seed-{seed}-width-{width}.npz',model);references.append(ref)
                restored=load_models(ref,seed,width,'cpu')
                with torch.no_grad():assert torch.equal(scores(restored,x[:,:width].contiguous(),a),left)
                for old,new in zip(model.parameters(),restored.parameters()):assert torch.equal(old,new)
                try:load_models(dict(ref,sha256='0'*64),seed,width,'cpu')
                except ValueError:pass
                else:raise AssertionError('Changed checkpoint hash accepted')
                try:load_models(ref,seed,387 if width==362 else 362,'cpu')
                except RuntimeError:pass
                else:raise AssertionError('Wrong checkpoint dimensions accepted')
            candidate.zero_grad(set_to_none=True);scores(candidate,x,a)[:,1].sum().backward()
            gradients=[float(m[0].weight.grad[:,362:].abs().sum()) for m in candidate]
            assert all(np.isfinite(v) and v>0 for v in gradients),'Extra inputs do not influence training gradients'
            records.append(dict(seed=seed,rows=len(x),maximum_initial_score_error=0.,
                additional_gradient_l1=gradients,round_trips=references,initial_parameters_identical=True))
        for width in (361,386,388):
            try:fresh(1,width,'cpu')
            except ValueError:pass
            else:raise AssertionError('Unregistered model width accepted')
        try:scores(candidate,x[:,:386],a)
        except ValueError:pass
        else:raise AssertionError('Wrong input width accepted')
        assert not torch.cuda.is_initialized()
        for p,h in spec['inputs'].items():assert sha(p)==h,p
        guard();size=measure(STORE);assert size['logical_bytes']<32_000_000
        result=dict(passed=True,registration_sha256=sha(REG),model_type=MODEL_TYPE,records=records,
            rows=len(x),cpu_initial_outputs_exact=True,extra_columns_learnable=True,checkpoint_round_trips_exact=True,
            original_input_prefix_exact=True,wrong_hash_and_width_rejected=True,
            seconds=time.monotonic()-start,storage=size,gpu_used=False,new_policy_training=False,
            synthetic_gradient_probe_only=True,production_modified=False,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()})
        atomic_json(RESULT,result);print(json.dumps({k:v for k,v in result.items() if k not in ('records','artifacts')}),flush=True)
    except BaseException as e:
        atomic_json(OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(e),traceback=traceback.format_exc()))
        raise
    finally:
        assert LOCK.read_text()==str(os.getpid());LOCK.unlink()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');main(p.parse_args().run)
