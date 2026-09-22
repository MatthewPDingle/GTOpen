"""Run the admitted combined trial and its fixed evaluations sequentially."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-visible-hybrid-trial-study-v1'
TD=ROOT/'tools/research'


def main():
    assert '--run' in sys.argv and idle()
    for name in ('representative-coverage-20260919','symmetric-bridge-20260919'):
        assert not (ROOT/'research/preflop-evolution'/name/'running.lock').exists()
    control_path=OUT/'sampled-visible-hybrid-allin-control-v1-independent-review.json'
    adapter_path=OUT/'sampled-visible-hybrid-trial-adapter-control-v1-result.json'
    control=json.loads(control_path.read_text());adapter=json.loads(adapter_path.read_text())
    assert control['passed'] and control['terminal_complete'] and control['completed_iterations']==4
    assert min(control['nonuniform_table_rows'])>0 and adapter['passed'] and adapter['complete_deals']==256
    ap=OUT/'sampled-visible-hybrid-trial-adapter-control-v1-registration.json'
    assert adapter['registration_sha256']==sha(ap)
    for p,h in {**json.loads(ap.read_text())['inputs'],**adapter['artifacts']}.items():assert sha(p)==h,p
    assert adapter['maximum_policy_error']<1e-10 and adapter['maximum_payoff_error_bb']<1e-8
    stages=[('training','hu_visible_hybrid_trial_pilot_20260923.py',['--run']),
        ('training-audit','hu_visible_hybrid_trial_review_20260923.py',[]),
        ('evaluation-admission','hu_visible_hybrid_trial_evaluation_20260923.py',['--prepare']),
        ('bb-evaluation','hu_visible_hybrid_trial_evaluation_20260923.py',['--run']),
        ('bb-audit','hu_visible_hybrid_trial_evaluation_review_20260923.py',[]),
        ('btn-evaluation','hu_visible_hybrid_trial_btn_evaluation_20260923.py',[]),
        ('btn-audit','hu_visible_hybrid_trial_btn_review_20260923.py',[])]
    inputs=[Path(__file__),control_path,adapter_path,ap,
        OUT/'VISIBLE-HYBRID-TRIAL-PLAN.md',
        TD/'sampled_visible_hybrid_allin_evaluation_v1.py',
        *[TD/name for _,name,_ in stages]]
    registration=dict(inputs={str(p):sha(p) for p in inputs},stages=stages,
        maximum_seconds=21600,production_modified=False,
        scope='Fixed combined candidate and both predeclared deviation families; stop on first failure, no retries or model promotion.')
    rp=OUT/f'{PREFIX}-registration.json';save(rp,registration)
    started=time.monotonic();records=[];child=None;error=None
    env=os.environ.copy();env.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONUNBUFFERED='1')
    def status(state,**extra):
        p=OUT/f'{PREFIX}-status.json';temporary=p.with_suffix('.tmp')
        save(temporary,dict(state=state,controller_pid=os.getpid(),seconds=time.monotonic()-started,
            stages=records,production_modified=False,**extra));temporary.replace(p)
    try:
        for label,name,args in stages:
            assert idle() and time.monotonic()-started<registration['maximum_seconds']
            for p,h in registration['inputs'].items():assert sha(p)==h,p
            began=time.monotonic()
            with (OUT/f'{PREFIX}-{label}.log').open('x') as log:
                child=subprocess.Popen([sys.executable,str(TD/name),*args],cwd=ROOT,env=env,
                    stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                status('running',stage=label,worker_pid=child.pid)
                # Each child owns its native/GPU lifecycle, idle and resource guards.
                code=child.wait()
            records.append(dict(stage=label,exit_code=code,seconds=time.monotonic()-began))
            assert code==0,f'{label} failed; inspect its preserved log, no retry'
            print(json.dumps(records[-1]),flush=True)
        for p,h in registration['inputs'].items():assert sha(p)==h,p
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),
            stages=records,seconds=time.monotonic()-started,production_modified=False,
            accuracy_qualified=False,scope='Execution and audits complete; strategic findings require analysis.'))
    except Exception as exc:error=str(exc);raise
    finally:
        status('stopped' if error else 'complete',error=error)


if __name__=='__main__':main()
