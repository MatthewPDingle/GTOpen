"""Register and review the isolated highest-regret fallback candidate."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle
from hu_sampled_convergence_fixture_20260922 import evaluate
from hu_sampled_neural_checks_20260922 import check

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
PREFIX='sampled-neural-max-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert idle(),'Production is active; no research started.'
    assert not LOCK.exists()
    assert not (LOCK.parent.parent/'symmetric-bridge-20260919/running.lock').exists()
    fixture=OUT/'sampled-convergence-v1-fixture.json'
    data=json.loads(fixture.read_text())
    controls=check(data)
    reg=OUT/(PREFIX+'-registration.json');assert not reg.exists()
    paths=[Path(__file__),fixture,ROOT/'tools/research/hu_sampled_neural_max_control_20260922.py',
        ROOT/'tools/research/hu_sampled_neural_checks_20260922.py',
        ROOT/'tools/research/hu_sampled_convergence_fixture_20260922.py',
        ROOT/'tools/research/hu_sampled_convergence_run_20260922.py',
        ROOT/'tools/research/hu_sampled_updates_oracle_20260922.py',
        ROOT/'tools/research/loopback_research_validation.py',
        ROOT/'tools/research/hu_sampled_neural_control_20260922.py',
        ROOT/'tools/research/hu_sampled_neural_fallback_20260922.py',
        OUT/'sampled-neural-v1-registration.json']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    config=dict(reservoir_capacity=32768,traversals_per_player=256,max_iterations=256,
        advantage_train_steps=128,strategy_train_steps=512,
        checkpoints=[1,16,32,64,128,256],target_gap=.01,consecutive_checks=2)
    record=dict(inputs=frozen,created_at_unix=time.time(),maximum_seconds=1200,
        fixture=str(fixture.relative_to(ROOT)),output_prefix=str((OUT/PREFIX).relative_to(ROOT)),
        cases=[0,1],seeds=[17,31],config=config,
        architecture='28 observable one-hot inputs, 64 ReLU, 64 ReLU, 3 outputs; separate player advantage and average models',
        optimization='New deterministic model each fit; Adam lr .003; minibatch 512; float32; no TF32',
        reservoirs='Separate uniform priority reservoirs per player and target type; per-visit instantaneous targets; ordinary equal iteration weighting',
        masking='Train legal actions only; advantage positive regret matching with highest legal regret fallback; average masked softmax',
        isolated_change='Only all-nonpositive inference fallback changes from uniform to highest legal score. Initial uniform policy and every other v1 setting retained.',
        motivation='Post-hoc fitting diagnosis plus Brown et al. ICML 2019 equation 4 discussion; new self-play test required.',
        averaging='Primary bounded learned average; exact own-reach and sampled visitation averages are finite-only diagnostics',
        acceptance='Primary independent exact summed BR gain <=.01 twice; no production qualification even if passed',
        no_automatic_retry=True,python_executable=sys.executable,python_sha256=sha(Path(sys.executable)))
    save(reg,record);save(OUT/(PREFIX+'-controls.json'),controls)
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    child=None;start=time.monotonic();error=None;samples=[];next_resource=0
    try:
        env=os.environ.copy();env['CUBLAS_WORKSPACE_CONFIG']=':4096:8';env['PYTHONUNBUFFERED']='1'
        env['OMP_NUM_THREADS']='2'
        with (OUT/(PREFIX+'.log')).open('x') as log:
            child=subprocess.Popen([sys.executable,str(paths[2]),str(reg)],cwd=ROOT,env=env,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                time.sleep(2)
                elapsed=time.monotonic()-start
                assert elapsed<record['maximum_seconds'],'Registered deadline reached; no retry.'
                assert idle(),'Production became active; stopping only research.'
                if elapsed>=next_resource:
                    host=psutil.virtual_memory().available
                    gpu=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
                    samples.append(dict(seconds=elapsed,free_host_bytes=host,free_gpu_bytes=gpu))
                    save(OUT/(PREFIX+'-resources.json'),samples);next_resource=elapsed+10
                    assert host>=20_000_000_000 and gpu>=3_000_000_000,'Memory reserve reached.'
            assert child.returncode==0,f'Research exited {child.returncode}; preserve failure.'
    except Exception as ex:
        error=str(ex)
        raise
    finally:
        if child is not None and child.poll() is None:child.terminate();child.wait(timeout=20)
        save(OUT/(PREFIX+'-status.json'),dict(exit_code=child.returncode if child else None,error=error,seconds=time.monotonic()-start))
        LOCK.unlink()
    summaries=[];max_error=0.
    for case in record['cases']:
        for seed in record['seeds']:
            path=OUT/f'{PREFIX}-case{case}-seed{seed}.json';run=json.loads(path.read_text())
            assert run['terminal'] and run['case']==case and run['seed']==seed
            streak=0
            for index,c in enumerate(run['checkpoints']):
                for name,e in c['evaluations'].items():
                    p=e['policy']
                    for lo,hi in zip(data['offsets'],data['offsets'][1:]):
                        assert min(p[lo:hi])>=0 and abs(sum(p[lo:hi])-1)<1e-12
                    exact=evaluate(data,p,case)
                    max_error=max(max_error,abs(exact['gap']-e['gap']),
                        *[abs(a-b) for name in ['ev','best_response'] for a,b in zip(exact[name],e[name])])
                streak=streak+1 if c['evaluations']['learned_average']['gap']<=config['target_gap'] else 0
                assert c['target_streak']==streak
                if index<len(run['checkpoints'])-1:assert streak<2
                for r in c['advantage_reservoirs']+c['strategy_reservoirs']:
                    assert r['retained']==min(r['seen'],config['reservoir_capacity'])
            assert run['target_reached_twice']==(streak>=2)
            if streak<2:assert run['checkpoints'][-1]['iteration']==config['max_iterations']
            summaries.append(dict(case=case,seed=seed,seconds=run['seconds'],target_reached_twice=streak>=2,
                last_iteration=run['checkpoints'][-1]['iteration'],
                final_gaps={k:v['gap'] for k,v in run['checkpoints'][-1]['evaluations'].items()},
                result_sha256=sha(path)))
    assert max_error<1e-10 and all(sha(ROOT/p)==h for p,h in frozen.items())
    review=dict(implementation_checks_passed=True,controls=controls,registration_sha256=sha(reg),
        inputs_verified=len(frozen),maximum_evaluation_error=max_error,runs=summaries,
        all_candidates_reached_target=all(r['target_reached_twice'] for r in summaries),
        actual_poker_convergence_qualified=False,production_modified=False)
    save(OUT/(PREFIX+'-review.json'),review)
    print(json.dumps(review,indent=2))


if __name__=='__main__':main()
