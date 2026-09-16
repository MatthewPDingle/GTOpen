"""Archive complete fresh-reference integrity checks without refitting a model."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import datetime as dt
import sys
import continuation_bridge_run as bridge
import continuation_policy_transfer as transfer

study=bridge.study


def audit(name):
    folders={'N09':'recalibrated-priors-20260916','N15':'shrunk-residual-20260916'}
    directory=transfer.BASE/folders[name]
    runner=transfer.adapter(directory);m=runner.checked('prospective')
    provenance=study.read(directory/'evaluation-provenance.json')
    registration=study.read(directory/'evaluation-registration.json')
    assert provenance['candidate_sha256']==registration['candidate_sha256']==study.pilot.sha(directory/'candidate.json')
    timestamp=dt.datetime.fromisoformat(registration['registered_at']).timestamp()
    maxima=dict(cpu_gap_pct=0.,gpu_gap_pct=0.,pot_accounting_error_bb=0.)
    for job in m['jobs']:
        path=directory/'prospective/jobs'/f"{job['id']}.json"
        relative=str(path.relative_to(study.ROOT)).replace('\\','/')
        assert study.pilot.sha(path)==provenance['files'][relative]
        assert path.stat().st_mtime>=timestamp
        row=study.read(path);bridge.validate_reference(row,job,m)
        maxima['cpu_gap_pct']=max(maxima['cpu_gap_pct'],row['gap_pct'])
        maxima['gpu_gap_pct']=max(maxima['gpu_gap_pct'],row['gpu_gap_pct'])
        maxima['pot_accounting_error_bb']=max(maxima['pot_accounting_error_bb'],abs(sum(row['means_bb'])-job['config']['tree']['starting_pot']))
    result=dict(checked_at=study.night.now(),audited=len(m['jobs']),manifest_id=m['id'],maxima=maxima,
        all_references_after_registration=True,all_reference_hashes_match=True,production_enabled=False,
        evaluation_sha256=study.pilot.sha(directory/'evaluation.json'),
        caveat='Reference integrity and average solve accuracy do not bound every rare-hand value or establish model validity.')
    study.night.dump(directory/'reference-audit.json',result)
    print(result,flush=True)


if __name__=='__main__':audit(sys.argv[1])
