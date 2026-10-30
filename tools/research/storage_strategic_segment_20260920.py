"""One registered, immutable 112-board segment. No automatic retries or promotion."""
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import psutil
from loopback_research_validation import idle
from storage_phase_run_20260920 import ROOT, OUT, EVIDENCE, SUB, read, sha
from storage_strategic_seed_20260920 import validate
from storage_weighted_input_preflight_20260920 import expected_manifest


def label(branch,target):
    return f'strategic-{branch}112-{target}-v1'


def verify_snapshot(snapshot):
    root=Path(snapshot['path'])
    assert {p.name for p in root.iterdir()}==set(snapshot['files'])
    assert all(p.is_file() for p in root.iterdir())
    for name,digest in snapshot['files'].items():assert sha(root/name)==digest,name
    assert sum(p.stat().st_size for p in root.iterdir())==snapshot['bytes']


def snapshot_record(root,result,identity,target,budget):
    index=read(root/'index.json')
    assert index['iteration']==target and len(index['entries'])==224
    assert index['identity']['external_sha256']==identity
    names={'index.json','complete','preflop.bin'}|{f'entry-{k}-generation-0.bin' for k in range(224)}
    assert {p.name for p in root.iterdir()}==names and all(p.is_file() for p in root.iterdir())
    for k,entry in enumerate(result['storage']['entries']):
        path=root/f'entry-{k}-generation-0.bin'
        assert path.stat().st_size==72+entry['bytes']
        with path.open('rb') as f:header=struct.unpack('<9Q',f.read(72))
        assert header[1:4]==(k,0,target) and list(header[1:])==index['entries'][k]
        assert sum(header[4:8])*4==entry['bytes']
    size=sum(p.stat().st_size for p in root.iterdir());assert size<=budget
    return dict(path=str(root),bytes=size,files={p.name:sha(p) for p in root.iterdir()})


def main():
    assert len(sys.argv)==3
    branch=sys.argv[1];target=int(sys.argv[2]);assert branch in ['weighted','equal']
    name=label(branch,target)
    registration=read(OUT/'strategic-segments-v1-registration.json')
    assert registration['reviewed_for_launch'] is True
    required=[Path(__file__),ROOT/'tools/research/storage_strategic_seed_20260920.py',
        ROOT/'tools/research/storage_weighted_input_preflight_20260920.py',
        ROOT/'tools/research/storage_phase_run_20260920.py',ROOT/'tools/research/storage_expansion_pilot_review_20260920.py',
        ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py',
        OUT/'expansion-capacity-112.json',OUT/'STRATEGIC-SEGMENTS-PROTOCOL.md']
    assert {str(p.relative_to(ROOT)) for p in required}<=set(registration['inputs_sha256'])
    schedule_path=OUT/'strategic-segments-v1-proposed-schedule.json'
    assert sha(schedule_path)==registration['schedule_sha256']
    plan=read(schedule_path)
    def verify():
        for p,digest in {**plan['inputs_sha256'],**registration['inputs_sha256']}.items():assert sha(ROOT/p)==digest,p
        assert sha(schedule_path)==registration['schedule_sha256']
    verify()
    found=[(i,s) for i,s in enumerate(plan['stages']) if s['branch']==branch and s['target']==target]
    assert len(found)==1;ordinal,stage=found[0];start=stage['start']
    assert 0<stage['maximum_seconds']<=43200 and stage['maximum_checkpoint_write_bytes']==64*1024**3
    for previous in plan['stages'][:ordinal]:
        old=read(OUT/(label(previous['branch'],previous['target'])+'-review.json'))
        assert old['segment_passed'] and old['target']==previous['target']
    runtime=read(OUT/'checkpoint-v1-runtime-freeze.json');exe=Path(runtime['exe'])
    for p,digest in runtime['inputs'].items():assert sha(ROOT/p)==digest,p
    assert sha(exe)==runtime['exe_sha256']
    manifest=OUT/('expansion-train-112-chance-weight-v1.json' if branch=='weighted' else 'expansion-train-112.json')
    parsed=expected_manifest() if branch=='weighted' else read(manifest)
    identity=dict(executable_sha256=sha(exe),source_manifest_sha256=sha(OUT/'checkpoint-v1-build-freeze.json'),
                  subtree_sha256=sha(SUB),boards_sha256=sha(manifest))
    predecessor=None;prior_result=None;prior_review=None
    if start:
        if start==20:
            prior_review=OUT/'strategic-weighted112-seed-v1-review.json';seed=read(prior_review)
            assert branch=='weighted' and seed['seed_and_fresh_restore_passed']
            predecessor=seed['snapshot'];prior_result=OUT/'strategic-weighted112-seed-v1-save-result.json'
            assert sha(prior_result)==seed['result_sha256']['save']
        else:
            prior_review=OUT/(label(branch,start)+'-review.json');previous=read(prior_review);assert previous['segment_passed']
            predecessor=previous['snapshot'];prior_result=OUT/(label(branch,start)+'-result.json')
            assert sha(prior_result)==previous['result_sha256']
        verify_snapshot(predecessor)
    def admission():
        verify();assert idle()
        cap=read(OUT/'expansion-capacity-112.json');totals=cap['totals']
        device=totals['steady_gpu_payload_bytes']+max(sum(r['workspace_components_bytes']) for r in cap['rows'])
        assert psutil.virtual_memory().available>=totals['ram_payload_total_bytes']+26_000_000_000
        free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
        assert totals['ram_payload_total_bytes']<=72_000_000_000 and device<=18_000_000_000 and free>=device+3_000_000_000
        remaining=sum(s['maximum_checkpoint_write_bytes'] for s in plan['stages'][ordinal:])
        assert shutil.disk_usage('S:/').free>=remaining+plan['disk_free_reserve_bytes']
        return totals
    cap=admission()
    for d in [OUT,EVIDENCE]:assert not (d/'running.lock').exists()
    root=Path('S:/GTOpen-research/strategic-segments-v1')/name
    root.parent.mkdir(exist_ok=True);root.mkdir();parking=root/'parking';parking.mkdir()
    saved=root/'final';identity_path=OUT/(name+'-identity.json')
    with identity_path.open('x') as f:json.dump(identity,f,indent=2)
    destination=OUT/(name+'-result.json');assert not destination.exists()
    fixed={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),identity_path,manifest,SUB,schedule_path,
        OUT/'strategic-segments-v1-registration.json',OUT/'STRATEGIC-SEGMENTS-PROTOCOL.md']}
    if prior_result is not None:
        fixed.update({str(p.relative_to(ROOT)):sha(p) for p in [prior_result,prior_review]})
    with (OUT/(name+'-freeze.json')).open('x') as f:
        json.dump(dict(inputs=fixed,exe=str(exe),exe_sha256=sha(exe),stage=stage,predecessor=predecessor),f,indent=2)
    status=dict(step='starting',pid=os.getpid(),created=psutil.Process().create_time(),branch=branch,start=start,target=target)
    def report():(OUT/(name+'-status.json')).write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)
    with (OUT/'running.lock').open('x') as f:f.write(str(os.getpid()))
    try:
        env=os.environ.copy()
        for key in ['GTO_RESUME_CHECKPOINT','GTO_SAVE_CHECKPOINT','GTO_RESTORED_COPY','GTO_CHECKPOINT_FORMAT_ROOT']:env.pop(key,None)
        env.update(GTO_SSD_STUDY_DIR=str(parking),GTO_STORAGE_RAM_BYTES='72000000000',GTO_STORAGE_WRITE_CAP='0',
                   GTO_STUDY_IDENTITY_FILE=str(identity_path),GTO_SAVE_CHECKPOINT=str(saved),
                   GTO_CHECKPOINT_WRITE_CAP=str(stage['maximum_checkpoint_write_bytes']),
                   GTO_RESEARCH_MAX_SECONDS=str(stage['maximum_seconds']),
                   GTO_RESEARCH_PROTOCOL=str((OUT/'STRATEGIC-SEGMENTS-PROTOCOL.md').relative_to(ROOT)))
        if predecessor is not None:env['GTO_RESUME_CHECKPOINT']=predecessor['path']
        status['step']='running';report()
        subprocess.run([sys.executable,'tools/research/loopback_research_validation.py',str(exe),name,str(SUB.relative_to(ROOT)),
                        str(manifest.relative_to(ROOT)),str(destination.relative_to(ROOT)),str(target)],cwd=ROOT,env=env,check=True)
        verify()
        for p,digest in runtime['inputs'].items():assert sha(ROOT/p)==digest,p
        for p,digest in fixed.items():assert sha(ROOT/p)==digest,p
        assert sha(exe)==runtime['exe_sha256']
        guard=read(EVIDENCE/(name+'-status.json'));assert guard['exit_code']==0 and guard['error'] is None
        samples=read(EVIDENCE/(name+'-resources.json'))
        assert min(s['free_host_bytes'] for s in samples)>=20_000_000_000 and min(s['free_gpu_bytes'] for s in samples)>=3_000_000_000
        result=read(destination);validate(result,cap,3*(target-start),parsed)
        assert result['resumed_iteration']==start and [r['iteration'] for r in result['records']]==stage['evaluation_iterations']
        if predecessor is not None:
            before=read(prior_result)
            assert result['records'][0]['evaluation']==before['records'][-1]['evaluation']
            for key in ['boards','board_weights','root_normalizer','entry_cutoff','suit_orbits']:assert result[key]==before[key]
            verify_snapshot(predecessor)
        snapshot=snapshot_record(saved,result,identity,target,stage['maximum_checkpoint_write_bytes'])
        gap=result['records'][-1]['evaluation']['gap_total']
        review=dict(segment_passed=True,branch=branch,start=start,target=target,snapshot=snapshot,result_sha256=sha(destination),
                    guard_seconds=guard['seconds'],restored_scientific_boundary_exact=predecessor is not None,
                    final_within_panel_gap=gap,endpoint_status=('underconverged' if gap>.01 else 'within-panel-threshold') if target==2000 else 'intermediate',
                    accuracy_claim=False,production_ready=False)
        with (OUT/(name+'-review.json')).open('x') as f:json.dump(review,f,indent=2)
        status['step']='complete-segment-reviewed'
    except Exception as e:status.update(step='stopped-for-review',error=repr(e));raise
    finally:report();(OUT/'running.lock').unlink()


if __name__=='__main__':main()
