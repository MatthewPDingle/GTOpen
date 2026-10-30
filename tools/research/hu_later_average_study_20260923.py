"""Run the fixed fresh-bank study only after all execution controls pass."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from reboot_research_idle_v1 import idle

PREFIX='later-average-study-v1'
TD=ROOT/'tools/research'


def main():
    assert '--run' in sys.argv and idle()
    for name in ('representative-coverage-20260919','symmetric-bridge-20260919'):
        assert not (ROOT/'research/preflop-evolution'/name/'running.lock').exists()
    inputs={}
    for prefix,review_kind in [('later-average-weight-control-v1','result'),
                               ('later-average-fresh-control-v1','independent-review'),
                               ('later-average-exact-control-v1','independent-review')]:
        rp=OUT/f'{prefix}-registration.json';ap=OUT/f'{prefix}-{review_kind}.json'
        reg,audit=read(rp),read(ap)
        assert audit['passed']
        assert audit.get('registration_sha256',audit.get('source_registration_sha256'))==sha(rp)
        inputs.update(reg['inputs']);inputs.update(audit.get('evidence_hashes',{}))
        if 'result_sha256' in audit:
            pp=OUT/f'{prefix}-result.json';assert audit['result_sha256']==sha(pp)
            inputs[str(pp)]=sha(pp)
        inputs.update({str(rp):sha(rp),str(ap):sha(ap)})
    stages=[('training','hu_later_average_fresh_pilot_20260923.py',['--run']),
            ('training-audit','hu_later_average_fresh_review_20260923.py',[]),
            ('exact-evaluation','hu_later_average_exact_evaluation_20260923.py',[]),
            ('exact-audit','hu_later_average_exact_review_20260923.py',[])]
    for p in [Path(__file__),OUT/'LATER-WEIGHTED-AVERAGING-PLAN.md',*[TD/name for _,name,_ in stages]]:
        inputs[str(p)]=sha(p)
    for p,h in inputs.items():assert sha(p)==h,p
    rp=OUT/f'{PREFIX}-registration.json'
    reg=dict(inputs=inputs,stages=stages,maximum_seconds=21600,production_modified=False,
        stopping='Stop on first stage failure; no automatic retries, wider evaluation or promotion.',
        scope='Fixed one-seed equal versus linear output-average comparison, with narrow exact endpoint screen and independent audits.')
    save(rp,reg);start=time.monotonic();records=[];error=None;child=None
    def status(state,**extra):
        p=OUT/f'{PREFIX}-status.json';tmp=p.with_suffix('.tmp')
        save(tmp,dict(state=state,controller_pid=os.getpid(),seconds=time.monotonic()-start,
             stages=records,production_modified=False,**extra));tmp.replace(p)
    env=os.environ.copy();env.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',PYTHONUNBUFFERED='1')
    try:
        for label,name,args in stages:
            assert idle() and time.monotonic()-start<reg['maximum_seconds']
            for p,h in inputs.items():assert sha(p)==h,p
            began=time.monotonic()
            with (OUT/f'{PREFIX}-{label}.log').open('x') as log:
                child=subprocess.Popen([sys.executable,str(TD/name),*args],cwd=ROOT,env=env,
                    stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                status('running',stage=label,worker_pid=child.pid)
                code=child.wait()
            records.append(dict(stage=label,exit_code=code,seconds=time.monotonic()-began))
            assert code==0,f'{label} failed; preserve logs and do not retry'
            print(json.dumps(records[-1]),flush=True)
        for p,h in inputs.items():assert sha(p)==h,p
        final=read(OUT/'later-average-exact-v1-result.json')
        review=read(OUT/'later-average-exact-v1-independent-review.json')
        assert review['passed'] and review['result_sha256']==sha(OUT/'later-average-exact-v1-result.json')
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),stages=records,
            screening_passed=final['screening_passed'],seconds=time.monotonic()-start,
            accuracy_qualified=False,production_modified=False,scope=reg['scope']))
    except Exception as exc:error=repr(exc);raise
    finally:status('stopped' if error else 'complete',error=error)


if __name__=='__main__':main()
