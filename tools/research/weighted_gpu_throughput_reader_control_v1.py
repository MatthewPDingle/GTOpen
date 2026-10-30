"""CPU qualification of independent information-set mapping and rejection."""
import copy
import json
from pathlib import Path
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save
from weighted_gpu_throughput_inputs_v1 import retained_inputs
from weighted_gpu_throughput_readback_v1 import index_rows, compare_rows

PREFIX = 'weighted-gpu-throughput-reader-control-v1'


def fixture(query):
    observations = query['observations']; n = len(observations)
    probabilities = np.zeros((4,n,4), dtype=np.float64); reaches = np.zeros((4,n), dtype=np.float64)
    for i, o in enumerate(observations):
        for bank in range(4):
            weights=np.asarray([1+(int(o['lo'])+a+bank)%7 for a in range(o['n'])], dtype=np.float64)
            probabilities[bank,i,:o['n']]=weights/weights.sum()
            reaches[bank,i]=float((int(o['lo'])+bank)%31)
    return index_rows(query,probabilities,reaches)


def main():
    began=time.monotonic(); assert psutil.cpu_percent(interval=.2)<50
    assert psutil.virtual_memory().available>24_000_000_000
    _,queries,paths=retained_inputs()
    prepared_path=OUT/'weighted-gpu-throughput-preparation-v1-result.json'
    prepared=read(prepared_path); registration=OUT/'weighted-gpu-throughput-preparation-v1-registration.json'
    assert prepared['passed'] and prepared['registration_sha256']==sha(registration)
    for p,h in prepared['artifacts'].items():assert sha(p)==h
    query_path=next(Path(p) for p in prepared['artifacts'] if Path(p).name=='queries.json')
    combined=read(query_path)
    paths.extend((prepared_path,registration,query_path,Path(__file__).resolve(),
        Path(__file__).with_name('weighted_gpu_throughput_readback_v1.py'),
        Path(__file__).with_name('weighted_gpu_throughput_inputs_v1.py')))
    inputs={str(p):sha(p) for p in paths};rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=inputs,maximum_seconds=120,gpu_used=False,training_started=False,
        scope='Independent native-key row/history mapping with varied synthetic probabilities/reaches on real retained query geometry.'))
    reference={}
    for query in queries:
        rows=fixture(query);shared=reference.keys()&rows.keys()
        if shared:assert compare_rows({k:reference[k] for k in shared},{k:rows[k] for k in shared})==(0.,0.)
        for k,v in rows.items():reference.setdefault(k,v)
    candidate=fixture(combined);assert compare_rows(reference,candidate)==(0.,0.)
    reordered=copy.deepcopy(combined);n=len(reordered['observations']);reordered['observations'].reverse()
    for o in reordered['observations']:o['own_history']=[[n-1-i,a,count] for i,a,count in o['own_history']]
    assert compare_rows(reference,fixture(reordered))==(0.,0.)
    rejected=[];first=next(iter(candidate))
    for kind in ('probabilities','reach'):
        wrong=copy.deepcopy(candidate)
        if kind=='probabilities':wrong[first][1][0,:2]+=[.001,-.001]
        else:wrong[first][2][0]+=.001
        try:compare_rows(reference,wrong)
        except AssertionError:rejected.append(kind)
    wrong=copy.deepcopy(combined)
    link=next(o for o in wrong['observations'] if o['own_history'])['own_history'][0]
    link[1]=(link[1]+1)%link[2]
    try:compare_rows(reference,fixture(wrong))
    except AssertionError:rejected.append('valid_but_different_history_action')
    wrong=copy.deepcopy(candidate);wrong.pop(first)
    try:compare_rows(reference,wrong)
    except AssertionError:rejected.append('missing_observation')
    assert rejected==['probabilities','reach','valid_but_different_history_action','missing_observation']
    for p,h in inputs.items():assert sha(p)==h,p
    assert time.monotonic()-began<120
    result=dict(passed=True,registration_sha256=sha(rp),unique_observations=len(reference),
        same_deal_batch_union_exact=True,remapped_row_order_exact=True,rejected_perturbations=rejected,
        seconds=time.monotonic()-began,gpu_used=False,production_modified=False,
        limitation='Tests independent row comparison. Real saved-capture transport readback requires the future completed GPU benchmark; no trained-policy equivalence or timing result yet.')
    save(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result),flush=True)


if __name__=='__main__':main()
