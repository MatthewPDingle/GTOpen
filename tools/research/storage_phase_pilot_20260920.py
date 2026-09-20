"""Three-iteration large-panel diagnosis after phase instrumentation qualification."""
import json
import os
from pathlib import Path
import subprocess
import sys
import psutil
from loopback_research_validation import idle
from storage_phase_run_20260920 import ROOT,OUT,EVIDENCE,SUB,read,sha,phase_review
from storage_expansion_pilot_review_20260920 import finite
LABEL='phase-pilot-v1'

def main():
    assert read(OUT/'phase-timing-v1-review.json')['passed']
    assert read(OUT/'phase-timing-v1-status.json')['step']=='complete-instrumentation-qualified'
    runtime=read(OUT/'phase-timing-v1-runtime-freeze.json');exe=Path(runtime['exe'])
    for p,h in runtime['inputs'].items():assert sha(ROOT/p)==h,p
    assert sha(exe)==runtime['exe_sha256']
    failure=read(OUT/'expansion-pilot-v1-failure-review.json');assert not failure['runtime_gate_passed'] and failure['capacity_observed']
    for p,h in failure['inputs_sha256'].items():assert sha(ROOT/p)==h,p
    assert idle()
    for d in [OUT,EVIDENCE]:assert not (d/'running.lock').exists()
    plan=read(OUT/'expansion-capacity-112.json');cap=plan['totals']
    ram=cap['ram_payload_total_bytes']
    device=cap['steady_gpu_payload_bytes']+max(sum(r['workspace_components_bytes']) for r in plan['rows'])
    host_free=psutil.virtual_memory().available
    gpu_free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
    assert ram<=72_000_000_000 and device<=18_000_000_000
    assert host_free>=ram+26_000_000_000 and gpu_free>=device+3_000_000_000
    manifest=OUT/'expansion-train-112.json';destination=OUT/f'{LABEL}-result.json';assert not destination.exists()
    scratch=Path('S:/GTOpen-research')/LABEL;assert not scratch.exists();scratch.mkdir()
    files=[Path(__file__),ROOT/'tools/research/storage_phase_run_20260920.py',ROOT/'tools/research/storage_expansion_pilot_review_20260920.py',
        OUT/'PHASE-PILOT-PROTOCOL.md',OUT/'phase-timing-v1-runtime-freeze.json',OUT/'phase-timing-v1-review.json',
        OUT/'phase-timing-v1-result.json',OUT/'expansion-pilot-v1-failure-review.json',OUT/'expansion-pilot-v1-result.json',
        OUT/'expansion-capacity-112.json',SUB,manifest,ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in files}
    with (OUT/f'{LABEL}-freeze.json').open('x') as f:json.dump(dict(inputs=frozen,exe=str(exe),exe_sha256=sha(exe),iterations=3,
        available_host_bytes=host_free,available_gpu_bytes=gpu_free,constructor_device_upper_bound=device),f,indent=2)
    status=dict(step='running-three-iteration-diagnostic',pid=os.getpid(),created=psutil.Process().create_time())
    def report():(OUT/f'{LABEL}-status.json').write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)
    with (OUT/'running.lock').open('x') as f:f.write(str(os.getpid()))
    env=os.environ.copy();env.update(GTO_SSD_STUDY_DIR=str(scratch),GTO_STORAGE_RAM_BYTES='72000000000',GTO_STORAGE_WRITE_CAP='0',
        GTO_RESEARCH_MAX_SECONDS='1800',GTO_RESEARCH_PROTOCOL=str((OUT/'PHASE-PILOT-PROTOCOL.md').relative_to(ROOT)))
    try:
        report()
        subprocess.run([sys.executable,'tools/research/loopback_research_validation.py',str(exe),LABEL,str(SUB.relative_to(ROOT)),
            str(manifest.relative_to(ROOT)),str(destination.relative_to(ROOT)),'3'],cwd=ROOT,env=env,check=True)
        for p,h in frozen.items():assert sha(ROOT/p)==h,p
        assert sha(exe)==runtime['exe_sha256']
        r=read(destination);finite(r);assert r['manifest']==read(manifest)
        assert r['boards']==[b['board'] for b in read(manifest)['boards']] and len(r['boards'])==112
        assert [x['iteration'] for x in r['records']]==[1,3]
        old=read(OUT/'expansion-pilot-v1-result.json')
        assert r['records'][0]['evaluation']==old['records'][0]['evaluation']
        for k in ['boards','board_weights','suit_orbits','root_normalizer','entry_cutoff']:assert r[k]==old[k],k
        for rec in r['records']:
            e=rec['evaluation'];assert abs(e['terminal_probability']-1)<1e-5 and e['conservation_error']<1e-4
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
        assert sum(e['bytes'] for e in entries)==cap['canonical_state_bytes']
        assert r['storage']['workspace_bytes']==cap['shared_gpu_workspace_bytes']
        for e in entries:
            assert not e['disk'] and e['read_bytes']==e['write_bytes']==0 and e['gpu_transfer_bytes']==9*e['bytes']
        guard=read(EVIDENCE/f'{LABEL}-status.json');assert guard['exit_code']==0 and guard['error'] is None
        samples=read(EVIDENCE/f'{LABEL}-resources.json')
        host=min(s['free_host_bytes'] for s in samples);gpu=min(s['free_gpu_bytes'] for s in samples)
        assert host>=20_000_000_000 and gpu>=3_000_000_000
        phases=phase_review((EVIDENCE/f'{LABEL}.log').read_text(),3,[1,3],r)
        review=dict(diagnostic_passed=True,original_20_iteration_gate_passed=False,first_checkpoint_exact=True,
            phase_measurements=phases,guard_seconds=guard['seconds'],minimum_free_host_bytes=host,minimum_free_gpu_bytes=gpu,
            result_sha256=sha(destination),production_ready=False,accuracy_claim=False,
            scope='112-board runtime attribution over three early iterations, not mature speed, convergence or accuracy.')
        with (OUT/f'{LABEL}-review.json').open('x') as f:json.dump(review,f,indent=2)
        status['step']='complete-diagnostic-reviewed'
    except Exception as e:status.update(step='stopped-for-review',error=repr(e));raise
    finally:report();(OUT/'running.lock').unlink()

if __name__=='__main__':main()
