"""Verify the standalone fixed-unit GPU kernel proof; not continuation quality."""
from check_joint import *


def verify():
    process=read('fixed-history-kernel-tests-v1-exit.json')
    require(process['returncode']==0 and process['reason'] is None,'Incomplete kernel test')
    rows=[json.loads(line.split('FIXED_HISTORY_KERNEL ',1)[1]) for line in
          (RAW/'fixed-history-kernel-tests-v1.log').read_text().splitlines() if 'FIXED_HISTORY_KERNEL ' in line]
    require([(r['calibrated'],r['unequal']) for r in rows]==[(c,u) for c in (False,True) for u in (False,True)],'Wrong coverage')
    for r in rows:
        require(r['nodes']==526 and r['levels']==11 and r['learning_entries_checked']==129454,'Wrong fixture coverage')
        require(r['extra_device_bytes']==8*r['nodes'],'Incorrect unit allocation')
        for key,limit in [('worst_regret_error',.002),('worst_average_error',.002),('worst_value_error_bb',.0002)]:
            require(math.isfinite(r[key]) and 0<=r[key]<limit,'Kernel arithmetic mismatch')
            if not r['unequal']:require(r[key]==0,'Unit-one native mismatch')
        for key in ('capture_eager_bitwise_equal','fixed_histories_preserved','tiny_initial_policy_preserved'):
            require(r[key] is True,'Policy or capture preservation failure')
        require(r['continuation_qualified'] is False,'Unjustified continuation claim')
    return dict(evidence_verified=True,cases=rows,continuation_qualified=False,
                scope='Standalone up-kernel arithmetic and graph replay only; no full iteration, admission or large-game result')


if __name__=='__main__':print(json.dumps(verify(),indent=2))
