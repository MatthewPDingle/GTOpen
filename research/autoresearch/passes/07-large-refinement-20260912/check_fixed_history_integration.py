"""Verify full-iteration mechanics without claiming large-game qualification."""
from check_joint import *


def verify():
    for v in (1,2,3):
        r=read(f'fixed-history-integration-tests-v{v}-exit.json')
        require(r['returncode']==101 and r['reason'] is None,'Missing failed predecessor evidence')
    r=read('fixed-history-integration-tests-v4-exit.json')
    require(r['returncode']==0 and r['reason'] is None,'Incomplete v4 tests')
    lines=(RAW/'fixed-history-integration-tests-v4.log').read_text().splitlines()
    def records(tag):return [json.loads(x.split(tag+' ',1)[1]) for x in lines if tag+' ' in x]
    iterations=records('FIXED_HISTORY_ITERATION');admission=records('FIXED_HISTORY_ADMISSION');kernel=records('FIXED_HISTORY_KERNEL')
    require([(r['calibrated'],r['unequal']) for r in iterations]==[(c,u) for c in (False,True) for u in (False,True)],'Missing iteration cases')
    for r in iterations:
        require(r['start_iteration']==17 and r['end_iteration']==21,'Wrong retained age')
        for k in ('capture_eager_equal','native_final_evaluation_equal','fixed_bookkeeping_matches_native','histories_finite'):
            require(r[k] is True,'Integration invariant failed')
        require(r['continuation_qualified'] is False,'Unqualified promotion')
    require(len(admission)==1 and admission[0]['nodes']==526,'Missing admission fixture')
    for k in ('host_discount_bitwise_equal','incompatible_modes_rejected','invalid_inputs_preserved_state'):
        require(admission[0][k] is True,'Admission/discount failure')
    require(len(kernel)==4 and all(r['capture_eager_bitwise_equal'] for r in kernel),'Missing kernel recheck')
    require(any('5 passed; 0 failed' in x for x in lines),'Incomplete test suite')
    return dict(evidence_verified=True,iterations=iterations,admission=admission[0],
                continuation_qualified=False,scope='Engine integration mechanics; no branch ownership, persistence or convergence qualification')


if __name__=='__main__':print(json.dumps(verify(),indent=2))
