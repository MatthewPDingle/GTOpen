"""Fix visible diagnostic cases from old control hands before policy inference."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from pathlib import Path
import hashlib
import json
import time
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT,OUT,read,sha,verify
from owned_columnar_evaluation_archive_v1 import ColumnarEvaluationReader
from board_river_strength_features_v1 import geometry
from bounded_parallel_evaluation_archive_v2 import install_fast_decoder
from board_prefix_publication_v1 import atomic_json


def main():
    began=time.monotonic()
    def guard():
        assert time.monotonic()-began<120 and psutil.virtual_memory().available>24_000_000_000
    original=OUT/'weighted-complete-board-root-study-v1-result.json';source_result=read(original)
    plan=OUT/'BOARD-RIVER-OPPONENT-REACH-PLAN.md'
    destination=OUT/'board-river-opponent-reach-v1-selected-cases.json'
    assert not destination.exists()
    route=source_result['routes']['test-000000'];root=Path(source_result['store'])/route['attempt']
    inputs={str(p):sha(p) for p in (Path(__file__),original,plan,root/'test-000000.manifest.json',root/'test-000000.xz',
        OUT/'board-later-public-state-catalog-v1.json',OUT/'bb-context-candidate.json')}
    install_fast_decoder();reader=ColumnarEvaluationReader(root,{'test-000000':route['manifest_sha256']},guard=guard)
    query=reader.read_json(root/'test-000000/queries.json');obs=query['observations']
    assert len(obs)==14547 and query['context_source']==(OUT/'bb-context-candidate.json').read_text()
    eligible,public=geometry(np.array([o['active_features'] for o in obs],dtype=np.int64),
        np.array([o['n'] for o in obs],dtype=np.int64),read(OUT/'board-later-public-state-catalog-v1.json'))
    assert int(eligible.sum())==7296
    bands=[('under10',0,10),('10to50',10,50),('50to100',50,100),('100to200',100,200),('200plus',200,float('inf'))]
    selected=[];strata=[];seen=set()
    for actor in (0,1):
        for label,low,high in bands:
            candidates=[]
            for i,o in enumerate(obs):
                if o['actor']!=actor or not eligible[i] or not low<=public[i,0]<high:continue
                key=(o['hi'],o['lo']);score=hashlib.sha256(f'9289902|{key[0]}|{key[1]}'.encode()).hexdigest()
                candidates.append((score,i))
            assert len({(obs[i]['hi'],obs[i]['lo']) for _,i in candidates})==len(candidates)
            candidates.sort();chosen=candidates[:8]
            strata.append(dict(actor=actor,pot_band=label,available=len(candidates),selected=len(chosen)))
            for score,i in chosen:
                o=obs[i];key=(o['hi'],o['lo']);assert key not in seen;seen.add(key)
                selected.append(dict(case_id=f'river-{len(selected):03d}',selection_sha256=score,
                    source_query_index=i,hi=key[0],lo=key[1],actor=actor,phase=o['phase'],n=o['n'],pot_band=label,
                    pot=float(public[i,0]),amount_to_call=float(public[i,1]),rake=float(public[i,2]),branch_total=float(public[i,3])))
    assert 0<len(selected)<=80 and all(c['phase']==3 and 2<=c['n']<=4 for c in selected)
    verify(inputs)
    output=dict(format=1,complete=True,passed=True,inputs=inputs,source_route=route,
        query_sha256=reader.sha256(root/'test-000000/queries.json'),seed=9289902,
        selection='Lowest SHA256 of decimal seed|hi|lo per actor and pot stratum; up to eight each.',
        cases=selected,strata=strata,selected_cases=len(selected),eligible_source_observations=7296,
        prior_physical_deals=32,new_physical_deals=0,learned_policy_inference=False,payoffs_scored=False,
        pilot_results_read=False,gpu_initialized=False,production_modified=False,seconds=time.monotonic()-began)
    atomic_json(destination,output);print(json.dumps(dict(passed=True,selected_cases=len(selected),strata=strata,seconds=output['seconds'])))


if __name__=='__main__':main()
