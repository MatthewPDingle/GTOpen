"""Describe retained historical action-difference variability, not confidence."""
import argparse
import json
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_checkpoint_v1 import read_object
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--source',choices=['pilot','dense'],required=True)
    args = parser.parse_args(); started = time.monotonic()
    assert idle() and psutil.virtual_memory().available >= 20_000_000_000
    if args.source == 'pilot':
        regpath = OUT/'sampled-physical-cached-fit-v1-registration.json'
        reg = json.loads(regpath.read_text()); objects = Path(reg['objects']); ref = reg['checkpoint']
        for p,h in reg['inputs'].items(): assert sha(p) == h,p
        source_paths = [regpath]
    else:
        regpath = OUT/'sampled-physical-dense-pilot-v1-registration.json'
        reg = json.loads(regpath.read_text())
        for p,h in reg['inputs'].items(): assert sha(ROOT/p) == h,p
        reviewpath = OUT/'sampled-physical-dense-pilot-v1-independent-review.json'
        review = json.loads(reviewpath.read_text())
        assert review['passed'] and review['terminal_complete'] and review['completed_iterations'] == 78
        assert review['source_registration_sha256'] == sha(regpath)
        for p,h in review['evidence_hashes'].items(): assert sha(p) == h,p
        objects = Path(reg['store'])/'checkpoint-objects'; ref = review['checkpoint']
        source_paths = [regpath,reviewpath]
    checkpoint = json.loads(read_object(objects,ref)); reservoir = checkpoint['reservoirs'][0]
    assert checkpoint['completed_iterations'] == 78
    read_object(objects,reservoir)
    evidence = {str(p):sha(p) for p in [*source_paths,objects/ref['file'],objects/reservoir['file'],Path(__file__)]}
    with np.load(objects/reservoir['file'],allow_pickle=False) as f:
        mask = f['keys'][:,0] == 1
        keys = f['keys'][mask]; values = f['values'][mask]
        iterations = f['iterations'][mask]
        assert np.all(f['arity'][mask] == 4) and np.isfinite(values).all()
        assert len(values) > 0 and np.all((iterations >= 1) & (iterations <= 78))
    rows = []
    for key in np.unique(keys,axis=0):
        mask = np.all(keys == key,axis=1); a = values[mask]
        # The state-value baseline cancels; these are paired sampled action
        # return differences, still from changing historical strategies.
        delta = a[:,1:]-a[:,0,None]
        count = len(a); sd = delta.std(0,ddof=1) if count > 1 else None
        rows.append(dict(hi=str(int(key[0])),lo=str(int(key[1])),retained_visits=count,
            distinct_updates=len(np.unique(iterations[mask])),
            mean_action_difference_bb=delta.mean(0).tolist(),
            sample_standard_deviation_bb=sd.tolist() if sd is not None else None,
            descriptive_std_over_sqrt_count_bb=(sd/np.sqrt(count)).tolist() if sd is not None else None))
    supported = [r for r in rows if r['retained_visits'] > 1]
    counts = np.array([r['retained_visits'] for r in rows])
    sd = np.array([r['sample_standard_deviation_bb'] for r in supported])
    ratios = np.array([r['descriptive_std_over_sqrt_count_bb'] for r in supported])
    summary = dict(root_classes=len(rows),retained_root_visits=int(counts.sum()),
        count_quantiles=np.quantile(counts,[0,.25,.5,.75,1]).tolist(),
        classes_with_at_least_two_visits=len(supported),
        median_sample_standard_deviation_bb=np.median(sd,axis=0).tolist(),
        median_descriptive_std_over_sqrt_count_bb=np.median(ratios,axis=0).tolist(),
        median_absolute_historical_mean_bb=np.median(np.abs([r['mean_action_difference_bb'] for r in rows]),axis=0).tolist())
    for p,h in evidence.items(): assert sha(p) == h,p
    assert idle() and time.monotonic()-started < 120
    result = dict(source=args.source,source_checkpoint=ref,evidence_hashes=evidence,
        action_order=['call minus fold','raise minus fold','jam minus fold'],summary=summary,rows=rows,
        seconds=time.monotonic()-started,accuracy_qualified=False,production_modified=False,
        scope='Descriptive retained-data variability across changing historical strategies. Ratios are not confidence intervals, do not establish independent effective samples, and are not uncertainty estimates for current-policy EVs. No new outcomes, fitting, candidate selection, or held-out test access.')
    save(OUT/f'sampled-physical-{args.source}-root-noise-v1-result.json',result)
    print(json.dumps(dict(source=args.source,summary=summary,seconds=result['seconds'])))


if __name__ == '__main__': main()
