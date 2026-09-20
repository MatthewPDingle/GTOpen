"""Freeze a common live-pair entry prior before comparing learned policies."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json
from pathlib import Path
import numpy as np
from storage_phase_run_20260920 import ROOT,OUT,SUB,read,sha

PAIRS=np.array([(a,b) for a in range(52) for b in range(a+1,52)])
MASKS=np.array([(1<<int(a))|(1<<int(b)) for a,b in PAIRS],dtype=np.uint64)
CLASSES=np.array([max(a//4,b//4)*13+min(a//4,b//4) if a%4==b%4 or a//4==b//4
                  else min(a//4,b//4)*13+max(a//4,b//4) for a,b in PAIRS])
COUNTS=np.bincount(CLASSES,minlength=169)


def prior(weights):
    assert weights.shape==(2,1326) and np.all(np.isfinite(weights)) and np.all(weights>=0)
    joint=weights[0,:,None]*weights[1,None,:]*((MASKS[:,None]&MASKS[None,:])==0)
    total=float(joint.sum());assert total>0
    dense=np.array([joint.sum(1),joint.sum(0)])/total
    independent=[]
    for p in range(2):
        opposite=weights[1-p]
        bycard=np.bincount(PAIRS.ravel(),weights=np.repeat(opposite,2),minlength=52)
        available=opposite.sum()-bycard[PAIRS[:,0]]-bycard[PAIRS[:,1]]+opposite
        raw=weights[p]*available
        assert abs(raw.sum()/total-1)<1e-12
        independent.append(raw/total)
    error=float(np.max(abs(dense-independent)));assert error<1e-12
    assert np.max(abs(dense.sum(1)-1))<1e-12 and np.min(dense)>=0
    return dense,total,error


def main():
    uniform,z,error=prior(np.ones((2,1326)))
    assert z==1326*1225 and np.max(abs(uniform-1/1326))<1e-15
    aces=np.zeros((2,1326));aces[:,CLASSES==168]=1
    aa,z,_=prior(aces);assert z==6 and np.all(aa[:,CLASSES!=168]==0)
    assert np.max(abs(aa[:,CLASSES==168]-1/6))<1e-15
    subtree=read(SUB)
    weights=np.array(subtree['incoming_class_mass'])[:,CLASSES]/COUNTS[CLASSES]
    weights/=weights.max(1)[:,None]
    before=weights.sum(1);weights[weights<1e-5]=0
    removed=1-weights.sum(1)/before;assert np.max(removed)<1e-5
    marginal,z,error=prior(weights)
    class_prior=np.array([np.bincount(CLASSES,weights=row,minlength=169) for row in marginal])
    # Verify combo ordering against the independent existing reporting path.
    import integrated_coverage as old
    assert np.array_equal(PAIRS,np.array(old.PAIRS)) and np.array_equal(CLASSES,old.CLASSES)
    report=dict(scope='Common full-deck two-live-player entry prior before a flop; earlier folds omitted.',
                purpose='Standardized policy frequencies and policy distance only; heldout EVs retain their own board-conditioned prior.',
                entry_cutoff=1e-5,normalizer=z,combo_prior=marginal.tolist(),class_prior=class_prior.tolist(),
                combo_classes=CLASSES.tolist(),supported_classes=[int(np.count_nonzero(x)) for x in class_prior],
                dense_vs_card_subtraction_max_error=error,removed_entry_mass_fraction=removed.tolist(),
                controls=dict(uniform_compatible_pairs=1326*1225,aa_vs_aa_compatible_pairs=6),
                policies_read=False,reserved_strategic_results_read=False,
                inputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),SUB,ROOT/'tools/research/integrated_coverage.py']})
    with (OUT/'strategic-common-prior-v1.json').open('x') as f:json.dump(report,f,indent=2,allow_nan=False)
    print(json.dumps({k:v for k,v in report.items() if k not in ['combo_prior','class_prior','combo_classes','inputs_sha256']},indent=2))


if __name__=='__main__':main()
