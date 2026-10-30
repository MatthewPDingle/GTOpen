"""Guarded GPU inference, gradient and fitted-weight transport qualification.

Optional bounded queue waits for the existing research GPU lock. No live solver
or other research process is stopped to obtain the device.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
import psutil
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
PREFIX='sampled-physical-gpu-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')

def worker(reg):
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    assert torch.cuda.is_available()
    source=json.loads((OUT/'sampled-physical-fit-v1-records.json').read_text())
    stored=json.loads((OUT/'sampled-physical-fit-v1-weights.json').read_text())
    rust=json.loads((OUT/'sampled-physical-fit-v1-replay.json').read_text())['rows']
    obs=source['observations'];x=np.zeros((len(obs),269),np.float32);mask=np.zeros((len(obs),4),np.float32)
    actors=np.array([o['actor'] for o in obs])
    for i,o in enumerate(obs):x[i,o['active_features']]=1;mask[i,:o['n']]=1
    cpu_x=torch.from_numpy(x);gpu_x=cpu_x.cuda()
    def network():return torch.nn.Sequential(torch.nn.Linear(269,64),torch.nn.ReLU(),torch.nn.Linear(64,64),torch.nn.ReLU(),torch.nn.Linear(64,4))
    def load(net,weights):
        for i,l in enumerate([0,2,4]):
            with torch.no_grad():
                net[l].weight.copy_(torch.tensor(weights[f'w{i}']).reshape(net[l].weight.shape))
                net[l].bias.copy_(torch.tensor(weights[f'b{i}']))
    def policies(scores):
        out=np.maximum(scores,0)*mask
        positive=out.sum(axis=1)>0
        out[positive]/=out[positive].sum(axis=1,keepdims=True)
        for i in np.flatnonzero(~positive):out[i,int(np.argmax(scores[i,:obs[i]['n']]))]=1
        return out
    teacher=np.zeros((len(obs),4));metrics=[];networks=[];trained=np.zeros_like(teacher)
    scales=[];maximum_gradient_error=0.;maximum_gradient_relative=0.
    for player in range(2):
        cpu=network();load(cpu,stored['networks'][player]);gpu=network().cuda();gpu.load_state_dict(cpu.state_dict())
        with torch.no_grad():
            cpu_scores=cpu(cpu_x).numpy().astype(float);gpu_scores=gpu(gpu_x).cpu().numpy().astype(float)
        teacher[actors==player]=gpu_scores[actors==player]
        inference_error=float(np.max(np.abs(cpu_scores-gpu_scores)))
        assert inference_error<reg['tolerances']['score']
        rows=[r for r in source['records'] if r[1]==player and r[2]>0]
        ids=np.array([r[0] for r in rows]);raw=np.array([r[3] for r in rows]);counts=np.bincount(ids,minlength=len(obs))
        assert np.all(actors[ids]==player)
        scale=max(.01,float(np.sqrt(np.mean(raw**2))));target=raw/scale
        sums=np.stack([np.bincount(ids,weights=target[:,a],minlength=len(obs)) for a in range(4)],axis=1)
        means=(sums/np.maximum(counts[:,None],1)).astype(np.float32)
        weights=(mask*counts[:,None]).astype(np.float32);denom=float(weights.sum())
        mean=torch.from_numpy(means);weight=torch.from_numpy(weights)
        gpu_mean=mean.cuda();gpu_weight=weight.cuda()
        cpu_loss=((cpu(cpu_x)-mean).square()*weight).sum()/denom
        gpu_loss=((gpu(gpu_x)-gpu_mean).square()*gpu_weight).sum()/denom
        cpu_loss.backward();gpu_loss.backward()
        for a,b in zip(cpu.parameters(),gpu.parameters()):
            ga=a.grad.detach().numpy().astype(float);gb=b.grad.detach().cpu().numpy().astype(float)
            error=float(np.max(np.abs(ga-gb)));scale_g=max(1.,float(np.max(np.abs(ga))))
            maximum_gradient_error=max(maximum_gradient_error,error)
            maximum_gradient_relative=max(maximum_gradient_relative,error/scale_g)
            assert error<=reg['tolerances']['gradient_absolute']+reg['tolerances']['gradient_relative']*float(np.max(np.abs(ga)))
        # Fresh seeded network; the loaded teacher was only a transport/gradient control.
        torch.manual_seed(9101+player);cpu=network();gpu=network().cuda();gpu.load_state_dict(cpu.state_dict())
        opt=torch.optim.Adam(gpu.parameters(),lr=.003)
        def loss():return ((gpu(gpu_x)-gpu_mean).square()*gpu_weight).sum()/denom
        before=float(loss().detach())
        for _ in range(128):
            current=loss();opt.zero_grad(set_to_none=True);current.backward();opt.step()
        after=float(loss().detach());assert np.isfinite(after) and after<before
        with torch.no_grad():scores=gpu(gpu_x).cpu().numpy().astype(float)
        trained[actors==player]=scores[actors==player]
        state=gpu.state_dict();export={}
        for i,l in enumerate([0,2,4]):
            export[f'w{i}']=state[f'{l}.weight'].cpu().numpy().flatten().tolist()
            export[f'b{i}']=state[f'{l}.bias'].cpu().numpy().tolist()
        networks.append(export);scales.append(scale)
        metrics.append(dict(player=player,cpu_gpu_inference_error=inference_error,
            normalized_fit_loss_before=before,normalized_fit_loss_after=after))
    rust_scores=np.array([r['scores'] for r in rust]);rust_policies=np.array([r['policy'] for r in rust])
    teacher_score_error=float(np.max(np.abs(teacher-rust_scores)))
    teacher_policy_error=float(np.max(np.abs(policies(teacher)-rust_policies)))
    artifact=OUT/(PREFIX+'-weights.json');save(artifact,dict(networks=networks,advantage_scales=scales,
        scope='GPU fixed-data fitting control only. No self-play accuracy claim.'))
    result_path=OUT/(PREFIX+'-replay.json')
    exe=ROOT/'target/release/examples/hu_sampled_physical_fit_control.exe'
    r=subprocess.run([str(exe),'infer',str(OUT/'bb-context-candidate.json'),str(OUT/'sampled-physical-fit-v1-records.json'),str(artifact),str(result_path)],
        cwd=ROOT,capture_output=True,text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    assert r.returncode==0,r.stderr
    replay=json.loads(result_path.read_text())['rows']
    trained_score_error=float(np.max(np.abs(trained-np.array([r['scores'] for r in replay]))))
    trained_policy_error=float(np.max(np.abs(policies(trained)-np.array([r['policy'] for r in replay]))))
    passed=(max(teacher_score_error,trained_score_error)<reg['tolerances']['score']
        and max(teacher_policy_error,trained_policy_error)<reg['tolerances']['policy'])
    result=dict(passed=passed,observations=len(obs),fits=metrics,
        teacher_rust_score_error=teacher_score_error,teacher_rust_policy_error=teacher_policy_error,
        trained_rust_score_error=trained_score_error,trained_rust_policy_error=trained_policy_error,
        maximum_gradient_absolute_error=maximum_gradient_error,maximum_gradient_scaled_error=maximum_gradient_relative,
        peak_allocated_gpu_bytes=torch.cuda.max_memory_allocated(),torch_version=torch.__version__,device=torch.cuda.get_device_name(),
        tf32_enabled=False,physical_poker_convergence_qualified=False,production_modified=False,
        artifacts={p.name:sha(p) for p in [artifact,result_path]})
    save(OUT/(PREFIX+'-result.json'),result);print(json.dumps(result),flush=True);assert passed

def main():
    wait='--wait' in sys.argv;queue_start=time.monotonic()
    # Do not infer that an owner has stopped from a stale result file.
    while LOCK.exists():
        assert wait,'Research GPU is reserved; run later or explicitly queue with --wait.'
        assert time.monotonic()-queue_start<1800,'Queue deadline reached; no automatic retry.'
        assert idle(),'Production active; canceling queued research.'
        try:owner=int(LOCK.read_text().strip())
        except FileNotFoundError:continue
        assert psutil.pid_exists(owner),'Stale research lock; inspect owner before continuing.'
        time.sleep(2)
    assert idle() and not (LOCK.parent.parent/'symmetric-bridge-20260919/running.lock').exists()
    prior=OUT/'sampled-physical-fit-v1-result.json';assert json.loads(prior.read_text())['passed']
    exe=ROOT/'target/release/examples/hu_sampled_physical_fit_control.exe'
    paths=[Path(__file__),prior,exe]+[OUT/p for p in ['bb-context-candidate.json','sampled-physical-fit-v1-records.json',
        'sampled-physical-fit-v1-weights.json','sampled-physical-fit-v1-replay.json']]+[ROOT/p for p in [
        'crates/solver/examples/hu_sampled_physical_fit_control.rs','crates/solver/examples/research_sampled/state.rs',
        'crates/solver/examples/research_sampled/poker_reference_v1.rs','crates/solver/examples/research_sampled/observation_v1.rs',
        'crates/solver/examples/research_sampled/network_v1.rs','crates/solver/examples/research_sampled/policy_walk_v1.rs',
        'tools/research/loopback_research_validation.py']]
    frozen={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in paths}
    reg_path=OUT/(PREFIX+'-registration.json');assert not reg_path.exists()
    reg=dict(inputs=frozen,steps=128,learning_rate=.003,model_seeds=[9101,9102],maximum_seconds=180,
        queue_limit_seconds=1800,queue_seconds=time.monotonic()-queue_start,
        tolerances=dict(score=2e-5,policy=1e-4,gradient_absolute=1e-5,gradient_relative=1e-4),
        scope='Physical fixed-data GPU inference, gradient and trained-weight transport control; no policy-strength claim.',
        architecture=[269,64,64,4],tf32=False,production_modified=False,no_automatic_retry=True)
    child=None;error=None;started=time.monotonic();samples=[]
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        save(reg_path,reg)
        env=os.environ.copy();env['CUBLAS_WORKSPACE_CONFIG']=':4096:8';env['PYTHONUNBUFFERED']='1';env['OMP_NUM_THREADS']='2'
        with (OUT/(PREFIX+'.log')).open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__)),'--worker',str(reg_path)],cwd=ROOT,env=env,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                time.sleep(2);elapsed=time.monotonic()-started
                assert elapsed<180 and idle(),'Deadline or production activity; stopping only research child.'
                host=psutil.virtual_memory().available
                gpu=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
                samples.append(dict(seconds=elapsed,host_free_bytes=host,gpu_free_bytes=gpu))
                assert host>=20_000_000_000 and gpu>=3_000_000_000,'Memory reserve reached.'
            assert child.returncode==0,f'Worker failed: {child.returncode}; retain outputs, no retry.'
        assert all(sha(ROOT/p)==h for p,h in frozen.items())
        result=OUT/(PREFIX+'-result.json');assert json.loads(result.read_text())['passed']
        save(OUT/(PREFIX+'-review.json'),dict(passed=True,inputs_verified=len(frozen),registration_sha256=sha(reg_path),
            result_sha256=sha(result),seconds=time.monotonic()-started,physical_poker_convergence_qualified=False))
    except Exception as ex:error=str(ex);raise
    finally:
        if child is not None and child.poll() is None:child.terminate();child.wait(timeout=20)
        save(OUT/(PREFIX+'-status.json'),dict(error=error,exit_code=child.returncode if child else None,seconds=time.monotonic()-started))
        save(OUT/(PREFIX+'-resources.json'),samples);LOCK.unlink()
    print((OUT/(PREFIX+'-result.json')).read_text())

if __name__=='__main__':
    if '--worker' in sys.argv:worker(json.loads(Path(sys.argv[-1]).read_text()))
    else:main()
