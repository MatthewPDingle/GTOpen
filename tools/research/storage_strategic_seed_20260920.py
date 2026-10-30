"""Initial weighted 112-board checkpoint and fresh-process restore, after all small gates."""
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle
from storage_phase_run_20260920 import ROOT,OUT,EVIDENCE,SUB,read,sha
from storage_expansion_pilot_review_20260920 import finite
from storage_weighted_input_preflight_20260920 import expected_manifest
LABEL='strategic-weighted112-seed-v1'
MANIFEST=OUT/'expansion-train-112-chance-weight-v1.json'

def validate(r,cap,transfers,manifest):
    finite(r);assert r['manifest']==manifest
    assert r['boards']==[b['board'] for b in manifest['boards']] and len(r['boards'])==112
    total=sum(b['weight'] for b in manifest['boards']);weights=[b['weight']/total for b in manifest['boards']]
    assert all(math.isclose(a,b,rel_tol=0,abs_tol=2e-16) for a,b in zip(r['board_weights'],weights))
    assert abs(sum(r['board_weights'])-1)<1e-12 and len(r['board_weights'])==112
    assert r['root_normalizer']>0 and r['suit_orbits'] is True and r['entry_cutoff']==.00001
    for row in r['records']:
        e=row['evaluation'];assert abs(e['terminal_probability']-1)<1e-5 and e['conservation_error']<1e-4
        assert min(e['gaps'])>-1e-4 and abs(sum(e['ev'])+e['expected_rake']-3.5)<1e-4
        assert abs(sum(e['root_frequencies'])-1)<1e-5 and abs(sum(h['root_mass'] for h in e['hands'])-1)<1e-5
        for h in e['hands']:
            assert all(-1e-12<=p<=1+1e-12 for p in h['strategy'])
            if h['root_mass']>0:assert abs(sum(h['strategy'])-1)<1e-10
        for node in e['preflop_policy']:
            if not node:continue
            assert all(len(a)==1326 for a in node)
            for column in zip(*node):assert all(-1e-12<=p<=1+1e-12 for p in column) and abs(sum(column)-1)<1e-10
    entries=r['storage']['entries'];assert len(entries)==224
    assert sum(e['bytes'] for e in entries)==cap['canonical_state_bytes'] and r['storage']['workspace_bytes']==cap['shared_gpu_workspace_bytes']
    for e in entries:assert not e['disk'] and e['read_bytes']==e['write_bytes']==0 and e['gpu_transfer_bytes']==transfers*e['bytes']

def main():
    parsed_manifest=expected_manifest()
    checkpoint=read(OUT/'checkpoint-long-v1-review.json');assert checkpoint['passed'] and checkpoint['all_scientific_checkpoints_exact']
    assert read(OUT/'checkpoint-long-v1-status.json')['step']=='complete-fresh-process-resume-qualified'
    phase=read(OUT/'phase-pilot-v1-review.json');assert phase['diagnostic_passed']
    times=phase['phase_measurements'];estimate=times['totals']['setup_seconds']+20*max(times['iteration_seconds'])+2*max(times['evaluation_seconds'])+240
    assert estimate<=1800,'Measured admission estimate exceeds initial deadline'
    chance=read(OUT/'chance-weight-v1-review.json');assert chance['passed']
    for p,h in chance['inputs_sha256'].items():assert sha(ROOT/p)==h,p
    runtime=read(OUT/'checkpoint-v1-runtime-freeze.json');exe=Path(runtime['exe'])
    for p,h in runtime['inputs'].items():assert sha(ROOT/p)==h,p
    assert sha(exe)==runtime['exe_sha256'] and idle()
    for d in [OUT,EVIDENCE]:assert not (d/'running.lock').exists()
    plan=read(OUT/'expansion-capacity-112.json');cap=plan['totals']
    device=cap['steady_gpu_payload_bytes']+max(sum(r['workspace_components_bytes']) for r in plan['rows'])
    def admission():
        assert idle() and psutil.virtual_memory().available>=cap['ram_payload_total_bytes']+26_000_000_000
        free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
        assert cap['ram_payload_total_bytes']<=72_000_000_000 and device<=18_000_000_000 and free>=device+3_000_000_000
    admission();root=Path('S:/GTOpen-research')/LABEL;assert not root.exists();root.mkdir()
    assert shutil.disk_usage(root).free>=100_000_000_000+64*1024**3
    identity=OUT/f'{LABEL}-identity.json'
    with identity.open('x') as f:json.dump(dict(executable_sha256=sha(exe),source_manifest_sha256=sha(OUT/'checkpoint-v1-build-freeze.json'),
        subtree_sha256=sha(SUB),boards_sha256=sha(MANIFEST)),f,indent=2)
    files=[Path(__file__),SUB,MANIFEST,identity,OUT/'STRATEGIC-SEED-PROTOCOL.md',OUT/'STRATEGIC-COMPARISON-PLAN.md',
        OUT/'checkpoint-long-v1-review.json',OUT/'checkpoint-v1-runtime-freeze.json',OUT/'phase-pilot-v1-review.json',
        OUT/'chance-weight-v1-review.json',OUT/'expansion-capacity-112.json',
        OUT/'weighted-input-readback-v1.json',OUT/'weighted-input-readback-v1-review.json',
        OUT/'checkpoint-v1-build.log',ROOT/'tools/research/storage_weighted_input_preflight_20260920.py',
        ROOT/'tools/research/storage_phase_run_20260920.py',ROOT/'tools/research/storage_expansion_pilot_review_20260920.py',
        ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in files}
    with (OUT/f'{LABEL}-freeze.json').open('x') as f:json.dump(dict(inputs=frozen,exe=str(exe),exe_sha256=sha(exe),
        admission_estimate_seconds=estimate,maximum_snapshot_write_bytes=64*1024**3),f,indent=2)
    status=dict(step='starting',pid=os.getpid(),created=psutil.Process().create_time())
    def report():(OUT/f'{LABEL}-status.json').write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)
    def verify():
        for p,h in frozen.items():assert sha(ROOT/p)==h,p
        assert sha(exe)==runtime['exe_sha256']
    snapshot=root/'iteration-20';results={};snapshot_hashes=None;guards={}
    with (OUT/'running.lock').open('x') as f:f.write(str(os.getpid()))
    try:
        for name,limit in [('save',1800),('restore',1200)]:
            admission();verify();scratch=root/(name+'-parking');scratch.mkdir();destination=OUT/f'{LABEL}-{name}-result.json';assert not destination.exists()
            env=os.environ.copy()
            for k in ['GTO_RESUME_CHECKPOINT','GTO_SAVE_CHECKPOINT','GTO_RESTORED_COPY','GTO_CHECKPOINT_FORMAT_ROOT']:env.pop(k,None)
            env.update(GTO_SSD_STUDY_DIR=str(scratch),GTO_STORAGE_RAM_BYTES='72000000000',GTO_STORAGE_WRITE_CAP='0',
                GTO_STUDY_IDENTITY_FILE=str(identity),GTO_CHECKPOINT_WRITE_CAP=str(64*1024**3),GTO_RESEARCH_MAX_SECONDS=str(limit),
                GTO_RESEARCH_PROTOCOL=str((OUT/'STRATEGIC-SEED-PROTOCOL.md').relative_to(ROOT)))
            env['GTO_SAVE_CHECKPOINT' if name=='save' else 'GTO_RESUME_CHECKPOINT']=str(snapshot)
            status['step']=name;report()
            subprocess.run([sys.executable,'tools/research/loopback_research_validation.py',str(exe),LABEL+'-'+name,str(SUB.relative_to(ROOT)),
                str(MANIFEST.relative_to(ROOT)),str(destination.relative_to(ROOT)),'20'],cwd=ROOT,env=env,check=True)
            verify();guard=read(EVIDENCE/f'{LABEL}-{name}-status.json');assert guard['exit_code']==0 and guard['error'] is None
            samples=read(EVIDENCE/f'{LABEL}-{name}-resources.json')
            assert min(s['free_host_bytes'] for s in samples)>=20_000_000_000 and min(s['free_gpu_bytes'] for s in samples)>=3_000_000_000
            r=read(destination);validate(r,cap,60 if name=='save' else 0,parsed_manifest)
            assert r['resumed_iteration']==(0 if name=='save' else 20)
            assert [x['iteration'] for x in r['records']]==([1,20] if name=='save' else [20])
            if name=='save':
                index=read(snapshot/'index.json');assert index['iteration']==20 and len(index['entries'])==224
                assert index['identity']['external_sha256']==read(identity)
                expected={'index.json','complete','preflop.bin'}|{f'entry-{k}-generation-0.bin' for k in range(224)}
                assert {p.name for p in snapshot.iterdir()}==expected and all(p.is_file() for p in snapshot.iterdir())
                for k,e in enumerate(r['storage']['entries']):
                    path=snapshot/f'entry-{k}-generation-0.bin';assert path.stat().st_size==72+e['bytes']
                    with path.open('rb') as f:header=struct.unpack('<9Q',f.read(72))
                    assert header[1:4]==(k,0,20) and list(header[1:])==index['entries'][k] and sum(header[4:8])*4==e['bytes']
                assert sum(p.stat().st_size for p in snapshot.iterdir())<=64*1024**3
                snapshot_hashes={p.name:sha(p) for p in snapshot.iterdir()}
                with (OUT/f'{LABEL}-snapshot.json').open('x') as f:json.dump(dict(path=str(snapshot),files=snapshot_hashes,
                    bytes=sum(p.stat().st_size for p in snapshot.iterdir())),f,indent=2)
            else:
                assert r['records'][0]['evaluation']==results['save']['records'][-1]['evaluation']
                for key in ['boards','board_weights','root_normalizer','entry_cutoff','suit_orbits']:assert r[key]==results['save'][key]
                assert {p.name:sha(p) for p in snapshot.iterdir()}==snapshot_hashes
            results[name]=r;guards[name]=guard
        review=dict(seed_and_fresh_restore_passed=True,iterations=20,boards=112,restored_scientific_checkpoint_exact=True,
            snapshot=read(OUT/f'{LABEL}-snapshot.json'),guard_seconds={k:g['seconds'] for k,g in guards.items()},
            save_after_final_evaluation_and_teardown_seconds=guards['save']['seconds']-results['save']['records'][-1]['elapsed_seconds'],
            construction_and_restore_seconds=results['restore']['phase_timing']['setup_seconds'],
            final_gap=results['save']['records'][-1]['evaluation']['gap_total'],
            result_sha256={k:sha(OUT/f'{LABEL}-{k}-result.json') for k in results},production_ready=False,converged=False,accuracy_claim=False)
        with (OUT/f'{LABEL}-review.json').open('x') as f:json.dump(review,f,indent=2)
        status['step']='complete-seed-and-restore-qualified'
    except Exception as e:status.update(step='stopped-for-review',error=repr(e));raise
    finally:report();(OUT/'running.lock').unlink()

if __name__=='__main__':main()
