"""Requalify the frozen-policy evaluator after training. --preflight is CPU-only."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
from storage_phase_run_20260920 import ROOT, OUT, EVIDENCE, SUB, read, sha
from loopback_research_validation import idle
import continuation_transfer_aggregate as aggregate

DEV = OUT.parent/'integrated-coverage-20260919'
EXE = ROOT/'target/release/examples/continuation_transfer_streamed.exe'
PROTOCOL = OUT/'STRATEGIC-EVALUATOR-CONTROLS.md'
PREFIX = 'strategic-evaluator-controls-v1'


def rel(path):
    return str(path.relative_to(ROOT))


def static_preflight():
    original = read(EVIDENCE/'transfer-controls-v3-freeze.json')['inputs']
    files = [EXE,SUB,ROOT/'tools/research/continuation_transfer_aggregate.py',
             ROOT/'tools/research/continuation_transfer_review.py',
             DEV/'old-two-orbits-result.json',DEV/'old-two-orbits.json',DEV/'orbit-river.json']
    files += [EVIDENCE/f'transfer-control-{kind}.json' for kind in ['fold','call','fourbet','jam']]
    for p in files:
        assert sha(p) == original[rel(p)], p
    assert sha(EXE) == '1203c744b108bfe9d7ded463242c6b066a8a22df8e5fbcdb052cdf2bb3d7282f'
    prior = read(EVIDENCE/'transfer-v3-paged-two-result-review.json')
    assert prior['kind'] == 'development-two' and prior['iteration'] == 2000
    assert prior['preflop_exactly_preserved'] and prior['final']['postflop_gap_total'] < .01
    reference = read(EVIDENCE/'transfer-v3-paged-two-result.json')
    assert reference['records'][-1]['evaluation']['preflop_policy'] == read(DEV/'old-two-orbits-result.json')['records'][-1]['evaluation']['preflop_policy']
    for key,value in prior['final'].items():
        assert reference['records'][-1]['evaluation'][key] == value
    files += [Path(__file__),PROTOCOL,EVIDENCE/'transfer-v3-paged-two-result.json',
              EVIDENCE/'transfer-v3-paged-two-result-review.json',
              EVIDENCE/'transfer-controls-v3-freeze.json',
              ROOT/'tools/research/integrated_coverage_review.py',ROOT/'tools/research/integrated_coverage.py',
              ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']
    return {rel(p):sha(p) for p in files}


def main():
    frozen = static_preflight()
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(dict(static_preflight_passed=True,gpu_launched=False,
                              final_policy_gate_not_checked=True,registered_worker_count=9)))
        return
    assert not sys.argv[1:]
    assert read(OUT/'strategic-segments-v1-queue-status.json')['step'] == 'complete-training-awaiting-reserved-comparison'
    assert not (OUT/'strategic-segments-v1-queue.lock').exists()
    assert not (OUT/'running.lock').exists() and not (EVIDENCE/'running.lock').exists()
    assert idle()
    final_path = OUT/'strategic-final-policies-v1-freeze.json'
    finals = read(final_path)
    assert finals['registration_sha256'] == sha(OUT/'strategic-segments-v1-registration.json')
    assert finals['accuracy_claim'] is False and finals['production_ready'] is False
    assert len(finals['policies']) == 2
    assert {(p['branch'],p['target']) for p in finals['policies']} == {('weighted',2000),('equal',2000)}
    sources = {}
    for p in finals['policies']:
        name = f"strategic-{p['branch']}112-2000-v1"
        result = OUT/(name+'-result.json');review = OUT/(name+'-review.json')
        assert sha(result) == p['result_sha256'] and sha(review) == p['review_sha256']
        assert read(review)['segment_passed'] and read(result)['records'][-1]['iteration'] == 2000
        sources[p['branch']] = result
        frozen.update({rel(result):sha(result),rel(review):sha(review)})
    sources['report47'] = EVIDENCE/'report47-full-result.json'
    assert sha(sources['report47']) == 'a1dbdd97d585e7603b8e117c2055c4be3b19804208b11c406e7ecf3c5c3afc22'
    frozen.update({rel(final_path):sha(final_path),rel(sources['report47']):sha(sources['report47']),
                   rel(OUT/'strategic-segments-v1-registration.json'):sha(OUT/'strategic-segments-v1-registration.json')})
    status = dict(step='starting',pid=os.getpid())
    with (OUT/(PREFIX+'-freeze.json')).open('x') as f:
        json.dump(dict(inputs_sha256=frozen,maximum_seconds_per_worker=900),f,indent=2)
    lock = OUT/'running.lock'
    with lock.open('x') as f:f.write(str(os.getpid()))

    def verify():
        for p,digest in frozen.items():assert sha(ROOT/p) == digest,p

    def report():
        (OUT/(PREFIX+'-status.json')).write_text(json.dumps(status,indent=2))
        print(json.dumps(status),flush=True)

    def run(*args):
        verify()
        subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,check=True)
        verify()

    def worker(suffix,panel,source,count,kind):
        name = PREFIX+'-'+suffix
        result = OUT/(name+'-result.json');assert not result.exists()
        status['step'] = suffix;report();verify()
        env = os.environ.copy()
        env.update(GTO_RESEARCH_MAX_SECONDS='900',GTO_RESEARCH_PROTOCOL=rel(PROTOCOL))
        subprocess.run([sys.executable,'tools/research/loopback_research_validation.py',rel(EXE),name,
                        rel(SUB),rel(panel),rel(result),str(count),rel(source)],cwd=ROOT,env=env,check=True)
        verify()
        g = read(EVIDENCE/(name+'-status.json'));assert g['exit_code'] == 0 and g['error'] is None
        run('tools/research/continuation_transfer_review.py',rel(result),rel(source),kind)
        assert read(result)['records'][-1]['iteration'] == count
        return result

    try:
        report()
        for kind in ['fold','call','fourbet','jam']:
            source = EVIDENCE/f'transfer-control-{kind}.json'
            result = worker(kind,DEV/'orbit-river.json',source,100,kind)
            combined = OUT/(PREFIX+'-aggregate-'+kind+'-result.json')
            run('tools/research/continuation_transfer_aggregate.py',rel(SUB),rel(DEV/'orbit-river.json'),rel(source),rel(combined),rel(result))
            a=read(result)['records'][-1]['evaluation'];b=read(combined)['records'][-1]['evaluation']
            for field in ['ev','gaps','postflop_gaps','root_frequencies']:
                assert np.max(abs(np.asarray(a[field])-b[field])) < 1e-7
        for kind,source in sources.items():
            worker('import-'+kind,DEV/'orbit-river.json',source,100,'import')
        panel = read(DEV/'old-two-orbits.json');leaves=[]
        assert len(panel['boards']) == 2
        for i,board in enumerate(panel['boards']):
            path=OUT/(PREFIX+f'-development-{i}-manifest.json')
            with path.open('x') as f:json.dump({**panel,'boards':[board]},f,indent=2)
            frozen[rel(path)] = sha(path)
            leaves.append(worker(f'development-{i}',path,DEV/'old-two-orbits-result.json',2000,'import'))
        combined = OUT/(PREFIX+'-development-result.json')
        run('tools/research/continuation_transfer_aggregate.py',rel(SUB),rel(DEV/'old-two-orbits.json'),
            rel(DEV/'old-two-orbits-result.json'),rel(combined),*map(rel,leaves))
        run('tools/research/continuation_transfer_review.py',rel(combined),rel(DEV/'old-two-orbits-result.json'),'development-two')
        a=read(EVIDENCE/'transfer-v3-paged-two-result.json')['records'][-1]['evaluation']
        b=read(combined)['records'][-1]['evaluation']
        errors={k:float(np.max(abs(np.asarray(a[k])-b[k]))) for k in ['ev','gaps','postflop_gaps','root_frequencies']}
        assert max(errors[k] for k in ['ev','gaps','postflop_gaps']) < 1e-4 and errors['root_frequencies'] < 1e-7
        verify()
        with (OUT/(PREFIX+'-review.json')).open('x') as f:
            json.dump(dict(passed=True,development_errors=errors,workers=9,new_reserved_results_read=False,
                           accuracy_claim=False,production_ready=False,inputs_sha256=frozen,
                           outputs_sha256={rel(p):sha(p) for p in OUT.glob(PREFIX+'*-result*.json')}),f,indent=2)
        status['step']='complete-evaluator-controls-passed'
    except Exception as ex:
        status.update(step='stopped-for-review',error=repr(ex));raise
    finally:
        report();lock.unlink()


if __name__ == '__main__':main()
