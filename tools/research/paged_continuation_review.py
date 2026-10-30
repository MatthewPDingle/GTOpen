"""Independent accounting and trajectory check for the paged connected game."""
import json
from pathlib import Path
import numpy as np
import integrated_coverage_review as review

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/representative-coverage-20260919'

def run():
    new=json.loads((OUT/'paged-two-result.json').read_text())
    old=json.loads((OUT.parent/'integrated-coverage-20260919/old-two-orbits-result.json').read_text())
    assert new['records'][-1]['iteration']==old['records'][-1]['iteration']==2000
    audit=review.audit_result(new)
    a=new['records'][-1]['evaluation'];b=old['records'][-1]['evaluation']
    # Max per-combo TV bounds its weighted mean for every normalized prior.
    tv=abs(np.array(a['preflop_policy'][0])-b['preflop_policy'][0]).sum(0)/2
    ev=float(max(abs(np.array(a['ev'])-b['ev'])))
    exact=all(x['evaluation']==y['evaluation'] for x,y in zip(new['records'],old['records']))
    gates=dict(ev=ev<.0001,policy=float(tv.max())<.0001,
               converged=a['gap_total']<.01,nonnegative=min(a['gaps'])>-1e-5)
    out=dict(audit=audit,gates=gates,passed=all(gates.values()),
             max_ev_difference_bb=ev,max_combo_policy_tv=float(tv.max()),
             every_checkpoint_evaluation_identical=exact,workspace_bytes=new['workspace_bytes'],
             transferred_bytes=new['transferred_bytes'],seconds=new['records'][-1]['elapsed_seconds'])
    path=OUT/'paged-two-review.json';assert not path.exists();path.write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))
    if not out['passed']:raise SystemExit(1)

if __name__=='__main__':run()
