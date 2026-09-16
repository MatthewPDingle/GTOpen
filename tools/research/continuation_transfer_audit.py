"""Archive changed-policy reference provenance and physical-value diagnostics."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import datetime as dt
import sys

import continuation_policy_transfer_optimized as optimized
import continuation_prediction_bounds as bounds

study=optimized.study


def verify_freeze(frozen,manifest,candidate_sha):
    assert frozen['sha256']==candidate_sha and frozen['evaluation_manifest_id']==manifest['id']
    assert frozen['references_at_freeze']==0
    timestamp=dt.datetime.fromisoformat(frozen['frozen_at'])
    assert timestamp.tzinfo is not None
    return timestamp.timestamp()


def verify_time(modified,frozen):
    assert modified>=frozen,'Reference predates the frozen ranges/model'


def run(name):
    assert name in ['N16','N17','N20']
    directory=optimized.OUT/name
    assert (directory/'evaluation.json').exists(),'Wait for a complete evaluation'
    runner=optimized.adapter().adapter(directory);manifest=runner.checked('prospective')
    model=study.read(directory/'candidate.json');candidate_sha=study.pilot.sha(directory/'candidate.json')
    assert candidate_sha==study.pilot.sha(optimized.original.BASE/'shrunk-residual-20260916/candidate.json')
    frozen=study.read(directory/'candidate-freeze.json')
    timestamp=verify_freeze(frozen,manifest,candidate_sha)
    result=study.read(directory/'evaluation.json')
    assert result['candidate_sha256']==candidate_sha
    assert {r['case'] for r in result['cases']}=={c['id'] for c in manifest['cases']}
    assert result['accuracy_screen_passed']==optimized.original.case_gate(result['cases'])
    assert len(manifest['cases'])==4 and len(manifest['boards'])==50 and len(manifest['jobs'])==200
    files={};maximum=dict(cpu_gap_pct=0.,gpu_gap_pct=0.,pot_accounting_error_bb=0.)
    for job in manifest['jobs']:
        path=directory/'prospective/jobs'/f"{job['id']}.json"
        verify_time(path.stat().st_mtime,timestamp)
        row=study.read(path);optimized.original.bridge.validate_reference(row,job,manifest)
        files[str(path.relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(path)
        maximum['cpu_gap_pct']=max(maximum['cpu_gap_pct'],row['gap_pct'])
        maximum['gpu_gap_pct']=max(maximum['gpu_gap_pct'],row['gpu_gap_pct'])
        maximum['pot_accounting_error_bb']=max(maximum['pot_accounting_error_bb'],abs(sum(row['means_bb'])-job['config']['tree']['starting_pot']))
    contexts=runner.contexts('prospective')
    physical=[bounds.inspect(c,bounds.shrunk.network.predict(c,model)) for c in contexts]
    result=dict(checked_at=study.night.now(),model=name,candidate_sha256=candidate_sha,manifest_id=manifest['id'],
        audited_references=len(files),all_references_after_freeze=True,reference_hashes=files,maxima=maximum,
        evaluation_sha256=study.pilot.sha(directory/'evaluation.json'),source_sha256=study.pilot.sha(__file__),
        physical_predictions=physical,physical_bounds_passed=all(r['passed'] for r in physical),production_enabled=False,
        caveat='Integrity and physical bounds complement the fixed accuracy gate; neither establishes full-game convergence or untouched-scenario generalization.')
    study.night.dump(directory/'reference-audit.json',result)
    print(dict(references=len(files),physical_bounds_passed=result['physical_bounds_passed'],maxima=maximum),flush=True)


if __name__=='__main__':run(sys.argv[1])
