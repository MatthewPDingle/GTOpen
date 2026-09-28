"""Replay the frozen native controls under a complete Rust-source inventory."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import traceback

ROOT=Path('T:/Dev/GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
OLD='river-full-action-control-v1'
NAME='river-full-action-provenance-v1'
STORE=OUT/NAME
REG=OUT/(NAME+'-registration.json')
RESULT=OUT/(NAME+'-result.json')
FAILURE=OUT/(NAME+'-failure.json')
PLAN=OUT/'RIVER-FULL-ACTION-PROVENANCE-PLAN.md'
EXE=ROOT/'target/release/examples/hu_river_action_queries_v1.exe'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def size():return sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())+sum(p.stat().st_size for p in (REG,RESULT,FAILURE) if p.exists())
def write(path,value):
    data=(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    assert size()+len(data)<100_000_000
    with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())


def main():
    start=time.monotonic();assert not any(p.exists() for p in (STORE,REG,RESULT,FAILURE,LOCK,OTHER))
    old_reg_path=OUT/(OLD+'-registration.json');old_result_path=OUT/(OLD+'-result.json')
    old_reg=read(old_reg_path);old_result=read(old_result_path)
    assert old_result['passed'] and old_result['complete'] and old_result['registration_sha256']==sha(old_reg_path)
    for p,h in old_reg['inputs'].items():assert sha(p)==h,p
    assert str(EXE) in old_reg['inputs']
    paths=[Path(__file__),PLAN,old_reg_path,old_result_path,EXE,ROOT/'Cargo.toml',ROOT/'Cargo.lock',
           ROOT/'crates/solver/Cargo.toml',ROOT/'crates/solver/examples/hu_river_action_queries_v1.rs']
    paths.extend((ROOT/'crates/solver/src').rglob('*.rs'))
    paths.extend((ROOT/'crates/solver/examples/research_sampled').glob('*.rs'))
    paths.extend((ROOT/'crates/solver').glob('build.rs'))
    for expected in ('tree.rs','evaluator.rs'):assert ROOT/'crates/solver/src'/expected in paths
    inputs=dict(old_reg['inputs']);inputs.update({str(p):sha(p) for p in paths})
    fixtures=[]
    for c in old_result['cases']:
        n=c['name'];folder=OUT/OLD;request=folder/(n+'-request.json');original=folder/(n+'-export.json')
        context=folder/'zero-rake-context.json' if 'zero-rake' in n else OUT/'bb-context-candidate.json'
        assert sha(original)==c['export_sha256']
        for p in (request,original,context):inputs[str(p)]=sha(p)
        fixtures.append((n,context,request,original))
    for n in ('unknown-field','invalid-card','terminal-history'):
        request=OUT/OLD/(n+'-request.json');inputs[str(request)]=sha(request)
    STORE.mkdir();acquired=False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        write(REG,dict(format=1,created_unix=time.time(),inputs=inputs,cases=[n for n,*_ in fixtures],
            reason='Initial Rust inventory used directory globs for tree.rs/evaluator.rs. Preserve initial registration; qualify replay with explicit full solver source inventory.',
            maximum_seconds=180,per_native_seconds=60,maximum_added_bytes=100_000_000,gpu_used=False,production_modified=False))
        replay=[]
        for n,context,request,original in fixtures:
            assert time.monotonic()-start<180 and size()+64_000_000<100_000_000
            dest=STORE/(n+'-export.json');t=time.perf_counter()
            p=subprocess.run([str(EXE),str(context),str(request),str(dest)],capture_output=True,text=True,timeout=60)
            record=dict(case=n,code=p.returncode,stdout=p.stdout,stderr=p.stderr,seconds=time.perf_counter()-t)
            write(STORE/(n+'-execution.json'),record)
            assert p.returncode==0 and dest.exists() and sha(dest)==sha(original)
            replay.append(dict(case=n,sha256=sha(dest),bytes=dest.stat().st_size,byte_identical=True,seconds=record['seconds']))
        negative=[]
        for n in ('unknown-field','invalid-card','terminal-history'):
            dest=STORE/(n+'-must-not-exist.json');request=OUT/OLD/(n+'-request.json')
            p=subprocess.run([str(EXE),str(OUT/'bb-context-candidate.json'),str(request),str(dest)],capture_output=True,text=True,timeout=60)
            assert p.returncode!=0 and not dest.exists();negative.append(dict(case=n,rejected=True,code=p.returncode,stderr=p.stderr))
        for p,h in inputs.items():assert sha(p)==h,p
        assert time.monotonic()-start<180
        write(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),original_result_sha256=sha(old_result_path),
            replay=replay,native_negative_controls=negative,source_inventory_files=len(inputs),seconds=time.monotonic()-start,
            bytes_before_result=size(),gpu_used=False,production_modified=False,
            scope='Byte-identical native exports and rejection behavior under a complete source inventory. Original numerical control results remain unchanged.'))
        print(json.dumps(dict(passed=True,cases=len(replay),seconds=time.monotonic()-start,bytes=size())),flush=True)
    except Exception as e:
        write(FAILURE,dict(error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
