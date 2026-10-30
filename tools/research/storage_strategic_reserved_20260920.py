"""Common reserved evaluation after final policies and evaluator controls pass.

--preflight validates static identity only, without GPU or reserved outcomes.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from storage_phase_run_20260920 import ROOT,OUT,EVIDENCE,SUB,read,sha
from storage_strategic_evaluator_controls_20260920 import static_preflight as evaluator_preflight, EXE
from loopback_research_validation import idle

PREFIX='strategic-reserved95-v1'
PANEL=OUT/'expansion-reserved-95-evaluation-v1.json'
PROTOCOL=OUT/'STRATEGIC-RESERVED-RUNTIME.md'
BUDGET=256*1024**2
RESERVE=32_000_000_000


def rel(path):return str(path.relative_to(ROOT))


def static_preflight():
    frozen=evaluator_preflight()
    adapter=read(OUT/'reserved-evaluation-manifest-v1-review.json')
    assert adapter['passed'] and adapter['all_boards_weights_and_selection_metadata_unchanged']
    for p,digest in adapter['inputs_sha256'].items():assert sha(ROOT/p)==digest,p
    panel=read(PANEL)
    assert len(panel['boards'])==95 and len({b['board'] for b in panel['boards']})==95
    assert panel['future_card_policy']=='plain_explicit' and panel['reserved'] is True
    frozen.update(adapter['inputs_sha256'])
    files=[Path(__file__),PROTOCOL,PANEL,OUT/'reserved-evaluation-manifest-v1-review.json',
           OUT/'STRATEGIC-COMPARISON-PLAN.md',OUT/'STRATEGIC-COMMON-PRIOR.md']
    frozen.update({rel(p):sha(p) for p in files})
    return frozen,panel


def main():
    frozen,panel=static_preflight()
    if sys.argv[1:]==['--preflight']:
        print(json.dumps(dict(static_preflight_passed=True,workers=285,gpu_launched=False,
                              final_policy_and_evaluator_gates_not_checked=True)))
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
    workers=95*3;started=time.monotonic();deadline=started+43200
    assert shutil.disk_usage(ROOT).free>=RESERVE+workers*BUDGET
    with (OUT/(PREFIX+'-freeze.json')).open('x') as f:
        json.dump(dict(inputs_sha256=frozen,iterations=2000,workers=workers,maximum_total_seconds=43200,
                       maximum_worker_seconds=900,evidence_budget_per_worker=BUDGET,disk_reserve_bytes=RESERVE),f,indent=2)
    lock=OUT/'running.lock'
    with lock.open('x') as f:f.write(str(os.getpid()))
    status=dict(step='starting',pid=os.getpid(),completed_workers=0)
    evidence={};leaves={name:[] for name in sources}

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
            manifest=OUT/(PREFIX+f'-{index:03}-manifest.json')
            with manifest.open('x') as f:json.dump({**panel,'boards':[board]},f,indent=2)
            frozen[rel(manifest)]=sha(manifest)
            for source_name,source in sources.items():
                verify();remaining=workers-status['completed_workers']
                assert shutil.disk_usage(ROOT).free>=RESERVE+remaining*BUDGET
                name=PREFIX+f'-{source_name}-{index:03}'
                output=OUT/(name+'-result.json');assert not output.exists()
                status.update(step='evaluating',source=source_name,board=board['board'],board_index=index);report()
                env=os.environ.copy();env.update(GTO_RESEARCH_MAX_SECONDS=str(min(900,deadline-time.monotonic())),
                                                GTO_RESEARCH_PROTOCOL=rel(PROTOCOL))
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
        assert status['completed_workers']==285
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
                           evidence_sha256=evidence,inputs_sha256=frozen,accuracy_claim=False,production_ready=False,
                           scope='Restricted eligible population and two-live-player game; full deviation and postflop residual reported separately.'),f,indent=2)
        status['step']='complete-awaiting-scientific-review' if settled else 'complete-underconverged-awaiting-review'
    except Exception as ex:
        status.update(step='stopped-for-review',error=repr(ex));raise
    finally:
        report();lock.unlink()


if __name__=='__main__':main()
