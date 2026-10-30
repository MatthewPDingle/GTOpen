"""Independent evidence and boundary review before observer admission."""
import hashlib
import json
import os
from pathlib import Path
import time
import psutil

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='stack-context-completion-handoff-v3-readback-result.json'


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def main():
    target=OUT/NAME
    assert not target.exists()
    result_path=OUT/'stack-context-completion-handoff-v3-check-result.json'
    attempt_path=OUT/'stack-context-completion-handoff-v3-check-attempt.json'
    r,a=read(result_path),read(attempt_path)
    assert r['complete'] and r['passed'] and r['inputs']==a['inputs']
    assert r['scientific_samples']==r['native_calls']==r['fits']==r['child_launches']==0 and not r['gpu']
    assert r['qualification_only'] and not r['actual_full_bank_resource_check'] and not r['scientific_evaluation_complete']
    for p,identity in r['inputs'].items():assert sha(p)==identity
    for p,identity in r['synthetic_boundary_artifacts'].items():assert sha(p)==identity
    assert r['normal_exit_race_controls']==5 and r['guarded_combinations']==24
    assert len(r['corruption_rejections'])==len(set(r['corruption_rejections']))==15
    assert len(r['decision_controls'])==16
    for row in r['decision_controls']:
        s=row['state']
        if s['failure']:expected='review-failure'
        elif s['external_owner']:expected='wait-owner'
        elif s['training_alive']:expected='wait-training'
        elif not s['training_complete']:
            expected='review-training' if not s['clean_training_boundary'] else ('review-deadline' if s['training_deadline_expired'] else 'training')
        else:
            expected='done'
            for phase in ('throughput','evaluation','readback'):
                q=s[phase]
                if q['complete']:continue
                expected='wait-'+phase if q['alive'] else ('review-'+phase if q['started'] else phase)
                break
        assert expected==row['expected']
    good=OUT/'stack-context-completion-handoff-v3-check-fixtures/good'
    name='stack-context-parallel-continuation-v2'
    invocation=good/(name+'-invocation-qualification.json');meta=read(invocation)
    proof=r['successful_completed_boundary'];assert sha(invocation)==proof['invocation_sha256']
    arms=('A-baseline','A-relative','B-baseline','B-relative')
    for arm in arms:
        progress=good/arm/'progress.json';n=read(progress)['completed_cycles'];assert n==proof['counts'][arm]
        if meta['boundaries'][arm]==64:assert n==64;continue
        end=read(good/(name+'-qualification-'+arm+'.json'))
        assert end['complete'] is False and end['stopped_at_complete_boundary'] is True and not end.get('failed')
        assert end['progress_sha256']==sha(progress) and n>=meta['boundaries'][arm]
        assert not (good/arm/f'cycle-{n+1:04d}').exists() and not (good/arm/f'archive-{n+1:04d}').exists()
    # Failed v2 check is a fixture-name defect, not a failed/retried science job.
    failed=read(OUT/'stack-context-completion-handoff-v2-check-failure.json')
    assert "'dict' object has no attribute 'object'" in failed['error']
    old=(ROOT/'tools/research/stack_context_completion_handoff_v2.py').read_bytes()
    current=(ROOT/'tools/research/stack_context_completion_handoff_v3.py').read_bytes()
    assert current==old.replace(b'completion-handoff-v2',b'completion-handoff-v3')
    oldq=(ROOT/'tools/research/stack_context_completion_handoff_check_v2.py').read_bytes()
    expectedq=oldq.replace(b'completion_handoff_v2',b'completion_handoff_v3').replace(b'handoff-v2',b'handoff-v3').replace(b'HANDOFF-V2',b'HANDOFF-V3')
    expectedq=expectedq.replace(b'from unittest.mock import patch',b'from unittest.mock import patch as mock_patch').replace(b'with patch.object(',b'with mock_patch.object(')
    assert expectedq==(ROOT/'tools/research/stack_context_completion_handoff_check_v3.py').read_bytes()
    processes=[]
    for pid,created,parent in ((84788,1790752536.9318762,2980),(94544,1790753443.077002,84788),
        (100604,1790753511.1853917,94544),(93416,1790753512.997676,94544),
        (104568,1790753514.8583736,94544),(81788,1790753516.7905183,94544)):
        p=psutil.Process(pid);assert abs(p.create_time()-created)<.01 and p.ppid()==parent
        processes.append(dict(pid=pid,created=p.create_time(),parent=p.ppid(),command=p.cmdline()))
    status=read(OUT/(name+'-status.json'));assert status['stage']=='parallel-training' and time.time()-status['unix']<60
    reg=OUT/'stack-context-matched-learning-v1-registration.json'
    assert sha(reg)=='ea0665fcb2ae2888a0aca0fd8ee282d06656d013fa41d98e8981cdc3f52c25e3'
    answer=dict(complete=True,passed=True,unix=time.time(),reader_sha256=sha(__file__),check_result_sha256=sha(result_path),
        check_attempt_sha256=sha(attempt_path),authenticated_inputs=len(r['inputs']),
        authenticated_synthetic_artifacts=len(r['synthetic_boundary_artifacts']),independent_order_controls=16,
        independent_successful_boundary_verified=True,normal_child_exit_race_controls=5,
        v2_failure_preserved=True,v3_changes_only_fixture_alias_and_namespace=True,
        qualification_only=True,child_launches=0,new_scientific_work=False,production_modified=False,
        live_processes=processes,registration_sha256=sha(reg))
    with target.open('xb') as f:f.write((json.dumps(answer,sort_keys=True,separators=(',',':'))+'\n').encode());f.flush();os.fsync(f.fileno())
    print(json.dumps({k:answer[k] for k in ('passed','authenticated_inputs','authenticated_synthetic_artifacts','independent_order_controls')}))


if __name__=='__main__':main()
