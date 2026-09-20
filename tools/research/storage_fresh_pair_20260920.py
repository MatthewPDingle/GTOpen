"""Fixed-order fresh A/B timing of the qualified exact storage implementation."""
import hashlib
import json
import os
from pathlib import Path
import statistics
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
LABEL='storage-fresh-pair-v1'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    names=['owner-download-v1','reuse-download-v1']
    reviews={n:read(OUT/f'{n}-long-review.json') for n in names}
    for n in names:
        assert reviews[n]['passed'] and read(OUT/f'{n}-review.json')['passed']
        assert sha(OUT/f'{n}-long-result.json')==reviews[n]['result_sha256']
    selected=min(names,key=lambda n:reviews[n]['total_seconds'])
    prior=read(OUT/'connected-v2-runtime-freeze.json')
    matches=[(p,h) for p,h in prior['executables'].items() if 'stored' in p];assert len(matches)==1
    base=ROOT/'target/qualified-paging'/('ssd-connected-v2-'+Path(matches[0][0]).name)
    assert sha(base)==matches[0][1]
    chosen=read(OUT/f'{selected}-runtime-freeze.json')['executables']['connected']
    candidate=Path(chosen['path']);assert sha(candidate)==chosen['sha256']
    reference_path=OUT/'long-ram-v1-resident-result.json'
    reference_review=read(OUT/'long-ram-v1-review.json');assert reference_review['passed']
    assert sha(reference_path)==reference_review['result_sha256']['resident']
    assert sha(OUT/'long-ram-v1-ram-result.json')==reference_review['result_sha256']['ram']
    reference=read(reference_path)
    assert idle() and not (OUT/'running.lock').exists() and not (EVIDENCE/'running.lock').exists()
    files=[Path(__file__),OUT/'FRESH-PAIR-PROTOCOL.md',SUB,OUT/'connected-three.json',reference_path,
        OUT/'long-ram-v1-review.json',OUT/'long-ram-v1-ram-result.json',
        OUT/'connected-v2-runtime-freeze.json',OUT/f'{selected}-runtime-freeze.json',
        ROOT/'tools/research/storage_owner_review_20260920.py',ROOT/'tools/research/loopback_research_validation.py',
        ROOT/'tools/research/paged_continuation_validation.py']
    for n in names:files += [OUT/f'{n}-long-review.json',OUT/f'{n}-long-result.json',OUT/f'{n}-review.json']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in files}
    binary_hashes={str(p):sha(p) for p in [base,candidate]}
    with (OUT/f'{LABEL}-freeze.json').open('x') as f:json.dump(dict(inputs=frozen,binaries=binary_hashes,
        selected_candidate=selected,order=['a1','b1','b2','a2'],iterations=500),f,indent=2)
    def verify():
        for p,h in frozen.items():assert sha(ROOT/p)==h,p
        for p,h in binary_hashes.items():assert sha(Path(p))==h,p
    status=dict(step='starting',pid=os.getpid(),created=psutil.Process().create_time(),selected_candidate=selected,completed=[])
    def report():(OUT/f'{LABEL}-status.json').write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)
    with (OUT/'running.lock').open('x') as f:f.write(str(os.getpid()))
    started=time.monotonic();results={}
    try:
        for name in ['a1','b1','b2','a2']:
            verify();assert idle();remaining=6000-(time.monotonic()-started);assert remaining>0
            exe=base if name[0]=='a' else candidate
            scratch=Path('S:/GTOpen-research')/(LABEL+'-'+name);assert not scratch.exists();scratch.mkdir()
            destination=OUT/f'{LABEL}-{name}-result.json';assert not destination.exists()
            env=os.environ.copy();env.update(GTO_SSD_STUDY_DIR=str(scratch),GTO_STORAGE_RAM_BYTES=str(2**63),GTO_STORAGE_WRITE_CAP='0',
                GTO_RESEARCH_MAX_SECONDS=str(min(1800,remaining)),GTO_RESEARCH_PROTOCOL=str((OUT/'FRESH-PAIR-PROTOCOL.md').relative_to(ROOT)))
            status['step']=name;report()
            subprocess.run([sys.executable,'tools/research/loopback_research_validation.py',str(exe),LABEL+'-'+name,
                str(SUB.relative_to(ROOT)),str((OUT/'connected-three.json').relative_to(ROOT)),str(destination.relative_to(ROOT)),'500'],
                cwd=ROOT,env=env,check=True)
            verify();r=read(destination);assert science(r)==science(reference)
            assert r['manifest']==read(OUT/'connected-three.json') and [x['iteration'] for x in r['records']]==[1,20,100,500]
            entries=r['storage']['entries'];assert len(entries)==6
            for e in entries:
                assert not e['disk'] and e['read_bytes']==e['write_bytes']==0
                assert e['gpu_transfer_bytes']==(4 if name[0]=='a' else 3)*500*e['bytes']
            original=read(OUT/'long-ram-v1-ram-result.json')['storage']
            assert [e['bytes'] for e in entries]==[e['bytes'] for e in original['entries']]
            assert r['storage']['workspace_bytes']==original['workspace_bytes']
            guard=read(EVIDENCE/f'{LABEL}-{name}-status.json');assert guard['exit_code']==0 and guard['error'] is None
            samples=read(EVIDENCE/f'{LABEL}-{name}-resources.json')
            assert min(s['free_host_bytes'] for s in samples)>=20_000_000_000 and min(s['free_gpu_bytes'] for s in samples)>=3_000_000_000
            rec=r['records'];results[name]=dict(total_seconds=rec[-1]['elapsed_seconds'],
                interval_seconds_per_iteration=(rec[-1]['elapsed_seconds']-rec[-2]['elapsed_seconds'])/400,result_sha256=sha(destination))
            status['completed'].append(name);report()
        metric='interval_seconds_per_iteration'
        pairs=[results['b1'][metric]/results['a1'][metric],results['b2'][metric]/results['a2'][metric]]
        a=[results[n][metric] for n in ['a1','a2']];b=[results[n][metric] for n in ['b1','b2']]
        spread=max(a)/min(a)-1;ratio=statistics.median(b)/statistics.median(a)
        review=dict(correctness_passed=True,selected_candidate=selected,results=results,paired_ratios=pairs,
            ratio_of_medians=ratio,baseline_spread=spread,repeatable_fixture_improvement=spread<=.1 and max(pairs)<=.95,
            inconclusive=spread>.1,production_ready=False,broader_forest_speed_claim=False,
            scope='Four fresh 500-iteration runs in ABBA order on the three development boards; interval includes final evaluation. No change to convergence or broad accuracy.')
        with (OUT/f'{LABEL}-review.json').open('x') as f:json.dump(review,f,indent=2)
        status['step']='complete-reviewed';print(json.dumps(review,indent=2),flush=True)
    except Exception as e:status.update(step='stopped-for-review',error=repr(e));raise
    finally:report();(OUT/'running.lock').unlink()

if __name__=='__main__':main()
