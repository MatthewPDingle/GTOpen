"""Physical continuation-value bounds; not a statistical accuracy estimate."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys
import numpy as np
import continuation_shrunk_residual as shrunk
import continuation_compact_residual as timing

study=shrunk.study


def inspect(c,pred):
    pred=np.asarray(pred);assert pred.shape==(2,169) and np.isfinite(pred).all()
    spr=c['case']['stack']/c['case']['pot'];lower=-spr;upper=1+spr
    excess=np.maximum(np.maximum(lower-pred,pred-upper),0.)
    bad=excess>1e-8
    return dict(case=c['case']['id'],spr=spr,minimum=float(pred.min()),maximum=float(pred.max()),
        lower_bound=lower,upper_bound=upper,violating_hands=int(bad.sum()),
        violating_mass_fraction=float((bad*c['mass']).sum()/2),max_excess=float(excess.max()),
        pot_accounting_error=float(abs((pred*c['mass']).sum()-1)),
        passed=bool(not bad.any() and abs((pred*c['mass']).sum()-1)<1e-8))


def run(partition):
    assert partition in ['training','prospective'];timing.require_no_timing()
    model=study.read(shrunk.OUT/'candidate.json');sha=study.pilot.sha(shrunk.OUT/'candidate.json')
    assert sha==study.read(shrunk.OUT/'candidate-freeze.json')['sha256']
    if partition=='training':cases=study.fit.load_cases('train')+study.contexts('development')
    else:
        assert (shrunk.OUT/'evaluation.json').exists(),'Wait for the complete fresh evaluation'
        import continuation_shrunk_evaluation as evaluation
        cases=evaluation.adapter().contexts('prospective')
    rows=[inspect(c,shrunk.network.predict(c,model)) for c in cases]
    result=dict(candidate_sha256=sha,partition=partition,cases=rows,passed=all(r['passed'] for r in rows),
        checked_at=study.night.now(),source_sha256=study.pilot.sha(__file__),production_enabled=False,
        interpretation='Zero-rake HU net value from future play is between minus remaining stack and pot plus remaining stack. Negative values within those limits can be legal. Passing bounds does not establish accuracy.')
    study.night.dump(shrunk.OUT/(partition+'-prediction-bounds.json'),result)
    print(dict(partition=partition,cases=len(rows),passed=result['passed'],violating_hands=sum(r['violating_hands'] for r in rows)),flush=True)
    return result


if __name__=='__main__':run(sys.argv[1])
