"""One reviewed infrastructure recovery; retain all original evidence and settings."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from storage_phase_run_20260920 import ROOT,OUT,EVIDENCE,SUB,read,sha
from storage_strategic_evaluator_controls_20260920 import static_preflight as evaluator_preflight, EXE
from loopback_research_validation import idle

from storage_strategic_confirm_register_20260922 import selection, REGISTRATION, PANEL, PROTOCOL

OLD_PREFIX='strategic-confirm190-v1'
PREFIX='strategic-confirm190-recovery-v1'
RECOVERY_PROTOCOL=OUT/'STRATEGIC-CONFIRM190-RECOVERY-PROTOCOL.md'
RECOVERY_REGISTRATION=OUT/(PREFIX+'-registration.json')
BUDGET=256*1024**2
RESERVE=32_000_000_000


def rel(path):return str(path.relative_to(ROOT))


def static_preflight():
    frozen=evaluator_preflight()
    registration=read(REGISTRATION)
    assert registration['passed'] and registration['new_panel_outcomes_read'] is False
    assert registration['boards']==190 and registration['workers']==570
    assert registration['iterations']==2000 and registration['maximum_total_seconds']==43200
    assert registration['maximum_worker_seconds']==900
    for p,digest in registration['inputs_sha256'].items():assert sha(ROOT/p)==digest,p
    panel,exclusions,count,mass=selection()
    assert read(PANEL)==panel and len(panel['boards'])==190
    assert count==registration['eligible_orbits'] and mass==registration['eligible_physical_mass']
    assert read(OUT/'strategic-reserved95-v1-review.json')['response_convergence_passed']
    prior=read(OUT/'strategic-reserved95-v1-status.json')
    assert prior['step']=='complete-awaiting-scientific-review'
    frozen.update(registration['inputs_sha256'])
    frozen[rel(REGISTRATION)]=sha(REGISTRATION)
    return frozen,panel



def recovery_preflight(register=False):
    frozen,panel=static_preflight()
    prior_status=OUT/(OLD_PREFIX+'-status.json')
    prior=read(prior_status)
    assert prior['step']=='stopped-for-review' and prior['completed_workers']==176
    assert prior['source']=='report47' and prior['board_index']==58 and prior['board']=='KcTd3h'
    assert prior['pid']==77264 and prior['created']==1790009768.4939656
    try:
        assert psutil.Process(prior['pid']).create_time()!=prior['created'],'Original runner still live'
    except psutil.NoSuchProcess:pass
    for path in [OUT/'running.lock',EVIDENCE/'running.lock',OUT/'strategic-segments-v1-queue.lock']:
        assert not path.exists(),path
    assert not [p.pid for p in psutil.process_iter(['name']) if p.info['name'] in ['continuation_transfer_streamed.exe','continuation_transfer.exe']]
    old_freeze=OUT/(OLD_PREFIX+'-freeze.json')
    for p,digest in read(old_freeze)['inputs_sha256'].items():assert sha(ROOT/p)==digest,p
    frozen.update(read(old_freeze)['inputs_sha256'])
    ledger=OUT/(OLD_PREFIX+'-completed-evidence.json');evidence=read(ledger)
    for p,digest in evidence.items():assert sha(ROOT/p)==digest,p
    names=['weighted','equal','report47'];leaves={n:[] for n in names}
    for ordinal in range(176):
        index,which=divmod(ordinal,3);name=OLD_PREFIX+f'-{names[which]}-{index:03}'
        output=OUT/(name+'-result.json');packed=output.with_suffix('.json.gz')
        review=output.with_name(output.stem+'-review.json');guard=EVIDENCE/(name+'-status.json')
        manifest=OUT/(OLD_PREFIX+f'-{index:03}-manifest.json')
        for path in [output,packed,review,guard,manifest]:assert rel(path) in evidence,path
        assert gzip.decompress(packed.read_bytes())==output.read_bytes()
        g=read(guard);assert g['exit_code']==0 and g['error'] is None
        r=read(review);assert r['kind']=='heldout' and r['preflop_exactly_preserved'] and r['iteration']==2000
        result=read(output);expected={**panel,'boards':[panel['boards'][index]]}
        assert result['manifest']==read(manifest)==expected
        assert result['boards']==[panel['boards'][index]['board']]
        assert result['records'][-1]['iteration']==2000 and result['terminal_values'] is not None
        leaves[names[which]].append(packed)
    failed=OLD_PREFIX+'-report47-058'
    failed_status=read(EVIDENCE/(failed+'-status.json'))
    assert failed_status['exit_code']!=0 and 'WinError 10055' in failed_status['error']
    failed_paths=[p for p in EVIDENCE.glob(failed+'*') if p.is_file()]
    failed_paths += [p for p in (EVIDENCE/'snapshots'/failed).rglob('*') if p.is_file()]
    failed_paths += [p for p in OUT.glob(failed+'*') if p.is_file()]
    assert any(p.name==failed+'-result.json' for p in failed_paths)
    recovery_inputs=[Path(__file__).resolve(),RECOVERY_PROTOCOL,prior_status,old_freeze,ledger,*failed_paths]
    frozen.update({rel(p):sha(p) for p in recovery_inputs})
    deadline=prior['created']+43200
    assert time.time()<deadline and idle()
    facts=dict(passed=True,prior_completed_workers=176,remaining_workers=394,workers=570,
               failed_attempt_preserved=True,retry_ordinal=176,retry_source='report47',retry_board_index=58,
               retry_reason='Reviewed Windows socket error in production-idle guard; not selected by strategy outcome.',
               original_deadline_unix=deadline,iterations=2000,maximum_worker_seconds=900,
               inputs_sha256=frozen,completed_evidence_sha256=evidence,
               partial_strategy_comparison_performed=False,production_ready=False)
    if register:
        assert not RECOVERY_REGISTRATION.exists()
        # Repeated read-only probes; keep the guard's fail-closed behavior unchanged.
        for _ in range(3):
            assert idle();time.sleep(2)
        with RECOVERY_REGISTRATION.open('x') as f:json.dump(facts,f,indent=2)
    else:
        registered=read(RECOVERY_REGISTRATION);assert registered==facts
    frozen[rel(RECOVERY_REGISTRATION)]=sha(RECOVERY_REGISTRATION)
    return frozen,panel,evidence,leaves,deadline


def main():
    if sys.argv[1:]==['--register']:
        recovery_preflight(register=True)
        print(json.dumps(dict(recovery_registered=True,completed_workers_verified=176,remaining_workers=394,gpu_launched=False)))
        return
    frozen,panel,prior_evidence,prior_leaves,wall_deadline=recovery_preflight()
    if sys.argv[1:]==['--preflight']:
        print(json.dumps(dict(recovery_preflight_passed=True,completed_workers_verified=176,remaining_workers=394,gpu_launched=False)))
        return
    assert not sys.argv[1:]
    control_path=OUT/'strategic-evaluator-controls-v1-review.json'
    controls=read(control_path)
    assert controls['passed'] and controls['new_reserved_results_read'] is False
    assert read(OUT/'strategic-evaluator-controls-v1-status.json')['step']=='complete-evaluator-controls-passed'
    assert read(OUT/'strategic-segments-v1-queue-status.json')['step']=='complete-training-awaiting-reserved-comparison'
    for p,digest in {**controls['inputs_sha256'],**controls['outputs_sha256']}.items():assert sha(ROOT/p)==digest,p
    frozen.update(controls['inputs_sha256']);frozen[rel(control_path)]=sha(control_path)
    final_path=OUT/'strategic-final-policies-v1-freeze.json';finals=read(final_path)
    assert len(finals['policies'])==2 and {p['branch'] for p in finals['policies']}=={'weighted','equal'}
    sources={b:OUT/f'strategic-{b}112-2000-v1-result.json' for b in ['weighted','equal']}
    sources['report47']=EVIDENCE/'report47-full-result.json'
    for p in finals['policies']:
        assert p['target']==2000 and sha(sources[p['branch']])==p['result_sha256']
    for path in sources.values():assert sha(path)==controls['inputs_sha256'][rel(path)]
    for path in [final_path,*sources.values()]:frozen[rel(path)]=sha(path)
    for path in [OUT/'running.lock',EVIDENCE/'running.lock',OUT/'strategic-segments-v1-queue.lock']:
        assert not path.exists(),path
    assert idle()
    workers=len(panel['boards'])*3;started=time.monotonic();deadline=started+(wall_deadline-time.time())
    assert shutil.disk_usage(ROOT).free>=RESERVE+(workers-176)*BUDGET
    with (OUT/(PREFIX+'-freeze.json')).open('x') as f:
        json.dump(dict(inputs_sha256=frozen,iterations=2000,workers=workers,maximum_total_seconds=43200,
                       maximum_worker_seconds=900,evidence_budget_per_worker=BUDGET,disk_reserve_bytes=RESERVE,
                       original_deadline_unix=wall_deadline,prior_completed_workers=176),f,indent=2)
    lock=OUT/'running.lock'
    with lock.open('x') as f:f.write(str(os.getpid()))
    status=dict(step='starting',pid=os.getpid(),created=psutil.Process().create_time(),completed_workers=176)
    evidence=dict(prior_evidence);leaves=prior_leaves

    def report():
        (OUT/(PREFIX+'-status.json')).write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)

    def verify():
        assert time.monotonic()<deadline,'Registered comparison deadline reached'
        for p,digest in frozen.items():assert sha(ROOT/p)==digest,p

    def cpu(*args):
        verify()
        subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,check=True,timeout=min(300,deadline-time.monotonic()))
        verify()

    try:
        report()
        for index,board in enumerate(panel['boards']):
            if (index+1)*3<=176:continue
            manifest=OUT/(PREFIX+f'-{index:03}-manifest.json')
            with manifest.open('x') as f:json.dump({**panel,'boards':[board]},f,indent=2)
            frozen[rel(manifest)]=sha(manifest)
            for source_number,(source_name,source) in enumerate(sources.items()):
                if index*3+source_number<176:continue
                verify();remaining=workers-status['completed_workers']
                assert shutil.disk_usage(ROOT).free>=RESERVE+remaining*BUDGET
                name=PREFIX+f'-{source_name}-{index:03}'
                output=OUT/(name+'-result.json');assert not output.exists()
                status.update(step='evaluating',source=source_name,board=board['board'],board_index=index);report()
                env=os.environ.copy();env.update(GTO_RESEARCH_MAX_SECONDS=str(min(900,deadline-time.monotonic())),
                                                GTO_RESEARCH_PROTOCOL=rel(RECOVERY_PROTOCOL))
                subprocess.run([sys.executable,'tools/research/loopback_research_validation.py',rel(EXE),name,
                                rel(SUB),rel(manifest),rel(output),'2000',rel(source)],cwd=ROOT,env=env,check=True)
                verify()
                guard=read(EVIDENCE/(name+'-status.json'));assert guard['exit_code']==0 and guard['error'] is None
                result=read(output)
                assert result['manifest']==read(manifest) and result['boards']==[board['board']]
                assert result['records'][-1]['iteration']==2000 and result['terminal_values'] is not None
                cpu('tools/research/continuation_transfer_review.py',rel(output),rel(source),'heldout')
                packed=output.with_suffix('.json.gz');raw=output.read_bytes();z=gzip.compress(raw,mtime=0)
                assert gzip.decompress(z)==raw
                with packed.open('xb') as f:f.write(z)
                artifacts=[output,packed,output.with_name(output.stem+'-review.json'),manifest]
                artifacts += [EVIDENCE/(name+s) for s in ['-freeze.json','-status.json','-resources.json','.log']]
                artifacts += [p for p in (EVIDENCE/'snapshots'/name).rglob('*') if p.is_file()]
                assert sum(p.stat().st_size for p in artifacts)<=BUDGET
                evidence.update({rel(p):sha(p) for p in artifacts});leaves[source_name].append(packed)
                status['completed_workers']+=1;report()
                (OUT/(PREFIX+'-completed-evidence.json')).write_text(json.dumps(evidence,indent=2))
        assert status['completed_workers']==workers
        for p,digest in evidence.items():assert sha(ROOT/p)==digest,p
        results=[]
        for source_name,source in sources.items():
            status.update(step='aggregating',source=source_name);report()
            output=OUT/(PREFIX+f'-{source_name}-result.json')
            cpu('tools/research/continuation_transfer_aggregate.py',rel(SUB),rel(PANEL),rel(source),rel(output),
                *[rel(p) for p in leaves[source_name]])
            cpu('tools/research/continuation_transfer_review.py',rel(output),rel(source),'heldout')
            e=read(output)['records'][-1]['evaluation']
            results.append(dict(source=source_name,result_sha256=sha(output),
                                **{k:e[k] for k in ['ev','expected_rake','gap_total','gaps','postflop_gap_total','root_frequencies']}))
        verify()
        settled=all(0<=r['postflop_gap_total']<.01 for r in results)
        with (OUT/(PREFIX+'-review.json')).open('x') as f:
            json.dump(dict(comparison_complete=True,response_convergence_passed=settled,results=results,
                           evidence_sha256=evidence,inputs_sha256=frozen,accuracy_claim=False,
                           recovery_registration_sha256=sha(RECOVERY_REGISTRATION),reused_workers=176,production_ready=False,
                           scope='Restricted eligible population and two-live-player game; full deviation and postflop residual reported separately.'),f,indent=2)
        status['step']='complete-awaiting-scientific-review' if settled else 'complete-underconverged-awaiting-review'
    except Exception as ex:
        status.update(step='stopped-for-review',error=repr(ex));raise
    finally:
        report();lock.unlink()


if __name__=='__main__':main()
