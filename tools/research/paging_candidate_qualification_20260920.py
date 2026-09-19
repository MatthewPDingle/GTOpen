"""Qualify the isolated upload-only candidate after accuracy work releases GPU.

Never builds, merges, deploys, or changes the production app. Existing guards
own GPU children, and the main shared lock covers the separate checkout.
"""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle
import paging_candidate_review as review

ROOT=Path(__file__).resolve().parents[2]
CAND=Path('T:/Dev/GTOpen-paging-research')
REL=Path('research/preflop-evolution/representative-coverage-20260919')
OUT=ROOT/REL
TARGET=CAND/REL
SUB=Path('research/preflop-evolution/conditional-hu-20260919/subtree.json')
PANEL=Path('research/preflop-evolution/integrated-coverage-20260919/old-two-orbits.json')
DEADLINE=datetime.fromisoformat('2026-09-20T09:00:00+09:30').timestamp()


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert not sys.argv[1:], 'No arguments accepted; this command executes GPU qualification'
    assert read(OUT/'overnight-accuracy-status.json')['step']=='complete-awaiting-scientific-review'
    supplement=OUT/'population-supplement-status.json'
    if supplement.exists():
        assert read(supplement)['step']=='complete-awaiting-scientific-review'
    for name in ['running.lock','overnight-accuracy.lock','full-population-supplement.lock']:
        assert not (OUT/name).exists(), f'Another research owner remains: {name}'
    assert idle() and DEADLINE-time.time()>=2700
    assert psutil.virtual_memory().available>=20_000_000_000
    free_gpu=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
    assert free_gpu>=3_000_000_000
    assert not (OUT.parent/'symmetric-bridge-20260919/running.lock').exists()
    assert not (TARGET/'running.lock').exists()
    build=read(TARGET/'paging-candidate-build-status.json')
    frozen={}
    for relative,digest in build['inputs'].items():
        path=CAND/relative
        assert sha(path)==digest,path
        frozen[str(path)]=digest
    binary=CAND/'target/qualified-paging/integrated_continuation_paged.exe'
    test=CAND/'target/qualified-paging/continuation_paging-test.exe'
    assert sha(binary)=='4cff5748e692d73156e412b21f62f07030f85178a127a1b6c82a156746fff0dc'
    assert sha(test)=='5dca1c26a38085d6fb656039ba16c65bb71bc1b3d1f8c737414f300a530da3ac'
    original=read(OUT/'paged-two-freeze.json')['inputs']
    for relative in [SUB,PANEL]:
        assert sha(ROOT/relative)==sha(CAND/relative)==original[str(relative)]
    baseline=OUT/'paged-two-result.json'
    assert sha(baseline)=='cf56de577e1c3092e32b04f60637bf8f7f5ecb82d8dfba63bec385f0fdfd2a09'
    old_exe=ROOT/'target/release/examples/integrated_continuation_paged.exe'
    assert sha(old_exe)==original[str(old_exe.relative_to(ROOT))]
    for path in [Path(__file__),Path(review.__file__),baseline,binary,test,old_exe,
                 ROOT/SUB,ROOT/PANEL,CAND/SUB,CAND/PANEL,TARGET/'PAGING-CANDIDATE-RUNTIME.md',
                 CAND/'tools/research/loopback_research_validation.py',
                 CAND/'tools/research/paged_continuation_validation.py',
                 ROOT/'tools/research/loopback_research_validation.py',
                 ROOT/'tools/research/paged_continuation_validation.py']:
        frozen[str(path)]=sha(path)
    def verify():
        for path,digest in frozen.items():
            assert sha(path)==digest,path
    def status(step,**extra):
        data=dict(step=step,pid=os.getpid(),updated_adelaide=datetime.now().astimezone().isoformat(),**extra)
        (OUT/'paging-candidate-qualification-status.json').write_text(json.dumps(data,indent=2))
        print(json.dumps(data),flush=True)
    def run_guard(root,label,exe,args,seconds):
        verify()
        assert DEADLINE>time.time() and idle()
        env=os.environ.copy()
        env['OPENBLAS_NUM_THREADS']='1'
        env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+';'+env['PATH']
        env['GTO_RESEARCH_MAX_SECONDS']=str(min(seconds,DEADLINE-time.time()))
        env['GTO_RESEARCH_PROTOCOL']=str(REL/('PAGING-CANDIDATE-RUNTIME.md' if root==CAND else 'PAGING-CANDIDATE-REVIEW.md'))
        status(label)
        # Never kill the guard externally and orphan its GPU child.
        subprocess.run([sys.executable,'tools/research/loopback_research_validation.py',
                        str(exe),label,*map(str,args)],cwd=root,env=env,check=True)
        result=read(root/REL/(label+'-status.json'))
        assert result['exit_code']==0 and result['error'] is None
    lock=OUT/'running.lock'
    owned=False
    try:
        with (OUT/'paging-candidate-qualification-freeze.json').open('x') as f:
            json.dump(dict(inputs_absolute=frozen,pid=os.getpid(),process_create_time=psutil.Process().create_time(),
                           deadline_adelaide='2026-09-20T09:00:00+09:30'),f,indent=2)
        with lock.open('x') as f:
            f.write(str(os.getpid()))
        owned=True
        run_guard(CAND,'ownavg-switch-test',test,['--nocapture','--test-threads=1'],600)
        log=(TARGET/'ownavg-switch-test.log').read_text()
        assert '1 passed; 0 failed; 0 ignored' in log and 'paging_preserves_resident_trajectories_and_rejects_invalid_inputs' in log
        candidate=TARGET/'ownavg-two-result.json'
        assert not candidate.exists()
        run_guard(CAND,'ownavg-two',binary,[SUB,PANEL,REL/candidate.name,'2000'],2400)
        proof=review.compare(review.read(baseline),review.read(candidate))
        with (OUT/'paging-candidate-exact-review.json').open('x') as f:
            json.dump({**proof,'input_sha256':{str(p):sha(p) for p in [baseline,candidate]}},f,indent=2)
        verify()
        assert lock.read_text()==str(os.getpid())
        lock.unlink()
        owned=False
        # A new baseline helps distinguish a transfer saving from machine drift.
        # If budget is short, retain a qualified candidate with historical-only
        # timing rather than overstating a fresh paired performance result.
        if DEADLINE-time.time()<1500:
            status('correctness-passed-fresh-timing-deferred',candidate_seconds=proof['candidate_seconds'])
            return
        fresh=OUT/'ownavg-fresh-baseline-result.json'
        assert not fresh.exists()
        run_guard(ROOT,'ownavg-fresh-baseline',old_exe,[SUB,PANEL,REL/fresh.name,'2000'],2400)
        def without_times(data):
            return {**data,'records':[{k:v for k,v in r.items() if k!='elapsed_seconds'} for r in data['records']]}
        assert review.canonical(without_times(review.read(fresh)))==review.canonical(without_times(review.read(baseline)))
        paired=review.compare(review.read(fresh),review.read(candidate))
        paired['input_sha256']={str(p):sha(p) for p in [fresh,candidate]}
        paired['order']='candidate switching test, candidate 2000-step run, fresh baseline 2000-step run'
        def late_seconds(path):
            records={r['iteration']:r['elapsed_seconds'] for r in read(path)['records']}
            return records[2000]-records[500]
        paired['late_interval_seconds']={'baseline':late_seconds(fresh),'candidate':late_seconds(candidate)}
        paired['timing_limitation']='One uncontended sequential pair; no repeated-run uncertainty estimate and no production speed claim.'
        with (OUT/'paging-candidate-paired-review.json').open('x') as f:
            json.dump(paired,f,indent=2)
        verify()
        status('complete-passed-research-only',candidate_seconds=proof['candidate_seconds'],
               fresh_baseline_seconds=paired['baseline_seconds'])
    except Exception as ex:
        status('stopped-for-review',error=str(ex))
        raise
    finally:
        if owned:
            assert lock.read_text()==str(os.getpid())
            lock.unlink()


if __name__=='__main__':
    main()
