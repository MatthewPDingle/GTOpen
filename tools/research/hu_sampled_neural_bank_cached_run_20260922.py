"""Same learning control with cached checkpoint reads and recovered evaluation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle
from hu_sampled_convergence_fixture_20260922 import evaluate
from hu_sampled_policy_bank_20260922 import check

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
PREFIX='sampled-neural-bank-cached-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert idle() and not LOCK.exists()
    assert not (LOCK.parent.parent/'symmetric-bridge-20260919/running.lock').exists()
    original=OUT/'sampled-neural-max-v1-registration.json'
    previous=json.loads(original.read_text());fixture=ROOT/previous['fixture']
    assert (OUT/'sampled-neural-max-v1-review.json').is_file(),'Finish and verify prefix comparison first.'
    data=json.loads(fixture.read_text());controls=check(data)
    reg=OUT/(PREFIX+'-registration.json');assert not reg.exists()
    worker=ROOT/'tools/research/hu_sampled_neural_bank_cached_control_20260922.py'
    paths=[Path(__file__),worker,original,fixture,
        ROOT/'tools/research/hu_sampled_policy_bank_20260922.py',
        ROOT/'tools/research/hu_sampled_neural_control_20260922.py',
        ROOT/'tools/research/hu_sampled_neural_fallback_20260922.py',
        ROOT/'tools/research/hu_sampled_convergence_fixture_20260922.py',
        ROOT/'tools/research/hu_sampled_updates_oracle_20260922.py',
        ROOT/'tools/research/loopback_research_validation.py',
        ROOT/'tools/research/hu_sampled_neural_bank_control_20260922.py',
        ROOT/'target/research-sampled/sampled-bank-reader-v1-snapshot.npz',
        OUT/'sampled-neural-bank-v1-case0-seed17.json',
        OUT/'sampled-bank-reader-v1-result.json']
    paths += [OUT/f'sampled-neural-max-v1-case{case}-seed{seed}.json' for case in [0,1] for seed in [17,31]]
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    config=dict(previous['config']);config.update(max_iterations=2048,
        checkpoints=[1,16,32,64,128,256,512,768,1024,1536,2048])
    record=dict(inputs=frozen,created_at_unix=time.time(),maximum_seconds=6000,
        fixture=str(fixture.relative_to(ROOT)),output_prefix=str((OUT/PREFIX).relative_to(ROOT)),
        bank_prefix='target/research-sampled/'+PREFIX,
        recovery_snapshot='target/research-sampled/sampled-bank-reader-v1-snapshot.npz',
        recovery_partial_result=str((OUT/'sampled-neural-bank-v1-case0-seed17.json').relative_to(ROOT)),
        io_change='Load each compressed model array once before indexing iterations. No training changes. Recovered interrupted snapshot evaluated before deterministic restart.',
        reference_prefix=str((OUT/'sampled-neural-max-v1').relative_to(ROOT)),
        cases=[0,1],seeds=[17,31],config=config,
        method='Retained neural advantage models with observable own-reach-weighted averaging; ordinary equal iteration weights',
        changes='Replace learned average-policy model with a saved model bank; extend stopping budget. Advantage fitting and traversal unchanged.',
        comparison='Must reproduce every shared max-v1 exact-average checkpoint within 1e-10, not merely similar aggregate gaps.',
        bank='Initial uniform policy plus all actually played trained models; final unused model excluded; complete bank saved and reloaded at checkpoints.',
        memory='Bank grows linearly with iterations: at cap, 4094 networks of 6211 float32 parameters, 101711336 bytes before scales/overheads. Not constant storage.',
        stopping='Exact summed finite BR gain <= .01 on two consecutive checkpoints, otherwise stop at 2048. No extension without a new registration.',
        finite_only='All-info arrays serve only as small-game replay oracles; they are not a scalable physical-poker representation.',
        no_automatic_retry=True,production_modified=False)
    save(reg,record);save(OUT/(PREFIX+'-controls.json'),controls)
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    child=None;error=None;started=time.monotonic();next_resource=0;samples=[]
    try:
        env=os.environ.copy();env['CUBLAS_WORKSPACE_CONFIG']=':4096:8';env['PYTHONUNBUFFERED']='1';env['OMP_NUM_THREADS']='2'
        with (OUT/(PREFIX+'.log')).open('x') as log:
            child=subprocess.Popen([sys.executable,str(worker),str(reg)],cwd=ROOT,env=env,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                time.sleep(2);elapsed=time.monotonic()-started
                assert elapsed<record['maximum_seconds'],'Registered deadline reached; keep checkpoints.'
                assert idle(),'Production active; stopping only research.'
                if elapsed>=next_resource:
                    host=psutil.virtual_memory().available
                    gpu=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
                    samples.append(dict(seconds=elapsed,free_host_bytes=host,free_gpu_bytes=gpu))
                    save(OUT/(PREFIX+'-resources.json'),samples);next_resource=elapsed+10
                    assert host>=20_000_000_000 and gpu>=3_000_000_000,'Memory reserve reached.'
            assert child.returncode==0,f'Research exited {child.returncode}; no automatic retry.'
    except Exception as ex:error=str(ex);raise
    finally:
        if child is not None and child.poll() is None:child.terminate();child.wait(timeout=20)
        save(OUT/(PREFIX+'-status.json'),dict(exit_code=child.returncode if child else None,error=error,seconds=time.monotonic()-started))
        LOCK.unlink()
    summaries=[];max_error=0.
    for case in record['cases']:
        for seed in record['seeds']:
            path=OUT/f'{PREFIX}-case{case}-seed{seed}.json';run=json.loads(path.read_text())
            assert run['terminal'];streak=0
            for i,c in enumerate(run['checkpoints']):
                p=c['average_policy']
                for lo,hi in zip(data['offsets'],data['offsets'][1:]):assert min(p[lo:hi])>=0 and abs(sum(p[lo:hi])-1)<1e-12
                exact=evaluate(data,p,case);max_error=max(max_error,abs(exact['gap']-c['evaluation']['gap']))
                streak=streak+1 if exact['gap']<=config['target_gap'] else 0
                assert c['target_streak']==streak
                assert c['maximum_own_reach_average_error']<1e-12 and c['maximum_saved_model_replay_error']<1e-12
                if i<len(run['checkpoints'])-1:assert streak<2
            last=run['checkpoints'][-1]
            assert run['target_reached_twice']==(streak>=2)
            if streak<2:assert last['iteration']==config['max_iterations']
            assert sha(ROOT/last['bank']['path'])==last['bank']['sha256']
            summaries.append(dict(case=case,seed=seed,seconds=run['seconds'],iterations=last['iteration'],
                final_gap=last['evaluation']['gap'],target_reached_twice=streak>=2,bank=last['bank'],result_sha256=sha(path)))
    assert max_error<1e-10 and all(sha(ROOT/p)==h for p,h in frozen.items())
    save(OUT/(PREFIX+'-review.json'),dict(implementation_checks_passed=True,inputs_verified=len(frozen),
        maximum_gap_reconstruction_error=max_error,registration_sha256=sha(reg),runs=summaries,
        all_candidates_reached_target=all(r['target_reached_twice'] for r in summaries),
        physical_poker_convergence_qualified=False,production_modified=False))
    print(json.dumps(summaries,indent=2))


if __name__=='__main__':main()
