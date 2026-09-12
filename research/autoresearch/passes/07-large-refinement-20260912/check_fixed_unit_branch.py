"""Check the branch ownership integration evidence."""
from check_joint import *


def verify():
    p=read('fixed-unit-branch-tests-v1-exit.json');require(p['returncode']==0 and p['reason'] is None,'Incomplete tests')
    lines=(RAW/'fixed-unit-branch-tests-v1.log').read_text().splitlines()
    def records(tag):return [json.loads(x.split(tag+' ',1)[1]) for x in lines if tag+' ' in x]
    cases=records('FIXED_UNIT_BRANCH');rejected=records('FIXED_UNIT_REJECTION')
    require([c['calibrated'] for c in cases]==[False,True],'Missing continuation fixture')
    for c in cases:
        require(c['branches']==2 and c['local_age']==3 and c['start_global_age']==17 and c['end_global_age']==19,'Wrong schedule')
        for k in ('split_continuation_exact','ownership_and_factors_verified','outside_copyback_unchanged','units_retained','native_evaluation_equal'):
            require(c[k] is True,'Branch invariant failed')
        require(c['qualified'] is False,'Unqualified promotion')
    require(len(rejected)==1,'Missing rejection coverage')
    for k in ('overlap_rejected_before_mutation','changed_state_rejected','other_owner_rejected','cancellation_rejected','device_admission_failure_poisons','invalid_continuation_preserved_histories'):
        require(rejected[0][k] is True,'Rejection invariant failed')
    require(rejected[0]['persistent_resume_supported'] is False,'Unsafe persistence claim')
    return dict(evidence_verified=True,cases=cases,rejections=rejected[0],large_game_qualified=False)


if __name__=='__main__':print(json.dumps(verify(),indent=2))
