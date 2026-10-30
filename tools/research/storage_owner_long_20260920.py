"""After small qualification, check owner-only transfers against the exact 500-step trajectory."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle
from storage_owner_review_20260920 import science
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
EVIDENCE=OUT.parent/'representative-coverage-20260919'
SUB=OUT.parent/'conditional-hu-20260919/subtree.json'
LABEL='owner-download-v1-long'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    status=dict(step='waiting-for-small-qualification',pid=os.getpid(),created=psutil.Process().create_time())
    path=OUT/f'{LABEL}-status.json'
    with path.open('x') as f:json.dump(status,f,indent=2)
    def report():path.write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)
    lock_owned=False
    try:
        prior=read(OUT/'owner-download-v1-status.json')
        try:
            p=psutil.Process(prior['pid'])
            if p.create_time()==prior['created']:
                start=time.monotonic()
                while True:
                    try:p.wait(timeout=30);break
                    except psutil.TimeoutExpired:assert time.monotonic()-start<1800,'Small-run wait expired; inspect without restarting'
        except psutil.NoSuchProcess:pass
        assert read(OUT/'owner-download-v1-status.json')['step']=='complete-awaiting-review'
        if not (OUT/'owner-download-v1-review.json').exists():
            subprocess.run([sys.executable,'tools/research/storage_owner_review_20260920.py'],cwd=ROOT,check=True)
        assert read(OUT/'owner-download-v1-review.json')['passed']
        runtime=read(OUT/'owner-download-v1-runtime-freeze.json')
        for p,h in runtime['inputs'].items():assert sha(ROOT/p)==h,p
        exe=Path(runtime['executables']['connected']['path'])
        assert sha(exe)==runtime['executables']['connected']['sha256']
        old=read(OUT/'long-ram-v1-review.json');assert old['passed']
        references={n:OUT/f'long-ram-v1-{n}-result.json' for n in ['resident','ram']}
        for n,p in references.items():assert sha(p)==old['result_sha256'][n]
        assert idle() and not (OUT/'running.lock').exists() and not (EVIDENCE/'running.lock').exists()
        files=[Path(__file__),OUT/'OWNER-LONG-PROTOCOL.md',OUT/'owner-download-v1-review.json',OUT/'owner-download-v1-runtime-freeze.json',
            OUT/'long-ram-v1-review.json',*references.values(),SUB,OUT/'connected-three.json',ROOT/'tools/research/storage_owner_review_20260920.py']
        frozen={str(p.relative_to(ROOT)):sha(p) for p in files}
        with (OUT/f'{LABEL}-freeze.json').open('x') as f:json.dump(dict(inputs=frozen,executable=str(exe),executable_sha256=sha(exe)),f,indent=2)
        with (OUT/'running.lock').open('x') as f:f.write(str(os.getpid()))
        lock_owned=True
        scratch=Path('S:/GTOpen-research')/LABEL;assert not scratch.exists();scratch.mkdir()
        result_path=OUT/f'{LABEL}-result.json';assert not result_path.exists()
        env=os.environ.copy();env.update(GTO_SSD_STUDY_DIR=str(scratch),GTO_STORAGE_RAM_BYTES=str(2**63),GTO_STORAGE_WRITE_CAP='0',
            GTO_RESEARCH_MAX_SECONDS='1800',GTO_RESEARCH_PROTOCOL=str((OUT/'OWNER-LONG-PROTOCOL.md').relative_to(ROOT)))
        status['step']='running-500-iteration-qualification';report()
        subprocess.run([sys.executable,'tools/research/loopback_research_validation.py',str(exe),LABEL,
            str(SUB.relative_to(ROOT)),str((OUT/'connected-three.json').relative_to(ROOT)),str(result_path.relative_to(ROOT)),'500'],cwd=ROOT,env=env,check=True)
        for p,h in frozen.items():assert sha(ROOT/p)==h,p
        assert sha(exe)==runtime['executables']['connected']['sha256']
        result=read(result_path);base=read(references['ram'])
        assert science(result)==science(base)==science(read(references['resident']))
        assert result['manifest']==read(OUT/'connected-three.json')
        assert [r['iteration'] for r in result['records']]==[1,20,100,500]
        for e,b in zip(result['storage']['entries'],base['storage']['entries']):
            assert e['bytes']==b['bytes'] and not e['disk'] and e['read_bytes']==e['write_bytes']==0
            assert e['gpu_transfer_bytes']==3*500*e['bytes']
            assert 4*e['gpu_transfer_bytes']==3*b['gpu_transfer_bytes']
        assert len(result['storage']['entries'])==6 and result['storage']['workspace_bytes']==base['storage']['workspace_bytes']
        guard=read(EVIDENCE/f'{LABEL}-status.json');assert guard['exit_code']==0 and guard['error'] is None
        samples=read(EVIDENCE/f'{LABEL}-resources.json')
        assert min(s['free_host_bytes'] for s in samples)>=20_000_000_000
        assert min(s['free_gpu_bytes'] for s in samples)>=3_000_000_000
        records=result['records']
        review=dict(passed=True,all_scientific_checkpoints_exact=True,iterations=500,transfer_fraction=.75,ssd_state_writes=0,
            total_seconds=records[-1]['elapsed_seconds'],seconds_per_iteration_100_to_500=(records[-1]['elapsed_seconds']-records[-2]['elapsed_seconds'])/400,
            final_gap=records[-1]['evaluation']['gap_total'],result_sha256=sha(result_path),production_ready=False,
            speed_improvement_claim=False,scope='Longer exact trajectory qualification on the three development boards. Fresh paired timing still required.')
        with (OUT/f'{LABEL}-review.json').open('x') as f:json.dump(review,f,indent=2)
        status['step']='complete-long-correctness-passed';print(json.dumps(review,indent=2),flush=True)
    except Exception as e:status.update(step='stopped-for-review',error=repr(e));raise
    finally:
        if lock_owned:(OUT/'running.lock').unlink()
        report()

if __name__=='__main__':main()
