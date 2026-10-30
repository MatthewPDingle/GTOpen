"""Post-diagnostic attribution of rare-path policy mass to initialization."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import time
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT,OUT,LOCK,OTHER,read,sha,verify
from board_prefix_publication_v1 import atomic_json
from board_training_policy_v1 import probabilities
from preflop_allin_matrix_v1 import AllinMatrix
from bounded_parallel_evaluation_archive_v2 import production_available

PREFIX='board-river-opponent-reach-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
CONTEXT=OUT/'bb-context-candidate.json'
IDENTITY=STORE/'bank-identities.json'
MATRIX=OUT/'preflop-allin-matrix-control-v1-matrix.json'
CATALOG=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')


def one(case_id):
    folder=STORE/'cases'/case_id;doc=read(folder/'export.json');result=read(folder/'result.json')
    assert result['export_sha256']==sha(folder/'export.json')
    source=CONTEXT.read_text();entry=AllinMatrix(read(MATRIX),source).btn_mass;out=[]
    for bank_index,identity in enumerate(read(IDENTITY)['source_banks']):
        ref=identity['model_references'][0];path=Path('S:/GTOpen-research/board-root-matched-prefix-v1')/identity['arm']/'objects'/ref['file']
        assert sha(path)==ref['sha256'];model=read(path);assert model['generation']==0
        p,_=probabilities(doc['queries'],model,device='cpu',catalog_source=CATALOG.read_text(),
            matrix_sha256=sha(MATRIX),entry_mass=entry,root_config=identity['root_config'])
        q=doc['target']['query_index'];initial_reach=1.
        for j,a,n in doc['queries']['observations'][q]['own_history']:initial_reach*=p[j,a]
        record=result['records'][bank_index];total=record['original_target_own_reach']
        assert total>0 and initial_reach<=total+1e-12
        ratio=float(initial_reach/total);assert ratio<=1+1e-12
        expected=record['conditional']['hero_own_likelihood']*sum(range(1,79))
        error=abs(total-expected);assert error<1e-9*max(1,total)
        only=abs(ratio-1)<1e-12
        if only:
            with np.load(folder/'policies.npz',allow_pickle=False) as saved:
                assert np.max(abs(p[q]-saved[f'policy_{bank_index*2}'][q]))<1e-10
        out.append(dict(case_id=case_id,bank=record['bank'],actor=doc['target']['actor'],pot_band=result['case']['pot_band'],
            initial_target_reach=float(initial_reach),total_target_reach=total,initial_share=ratio,initial_only_to_numerical_tolerance=only,
            behavioral_vs_mixture_reach_error=error,hero_own_likelihood=record['conditional']['hero_own_likelihood'],
            restricted_switch_gain_bb=record['original']['restricted_switch_gain_bb']))
    return out


def summarize(rows):
    def bucket(items):
        return dict(cases=len(items),mean_local_gain_bb=float(np.mean([r['restricted_switch_gain_bb'] for r in items])) if items else None,
            median_local_gain_bb=float(np.median([r['restricted_switch_gain_bb'] for r in items])) if items else None,
            median_hero_history_likelihood=float(np.median([r['hero_own_likelihood'] for r in items])) if items else None)
    return dict(cases=len(rows),median_initial_share=float(np.median([r['initial_share'] for r in rows])),
        initial_only=bucket([r for r in rows if r['initial_only_to_numerical_tolerance']]),
        later_generations_contribute=bucket([r for r in rows if not r['initial_only_to_numerical_tolerance']]))


def main():
    began=time.monotonic();reg=OUT/(PREFIX+'-attribution-registration.json');destination=OUT/(PREFIX+'-attribution.json')
    assert not reg.exists() and not destination.exists() and not LOCK.exists() and not OTHER.exists();acquired=False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;assert production_available() and psutil.virtual_memory().available>24_000_000_000
        review=OUT/(PREFIX+'-independent-review.json');assert read(review)['passed']
        result=OUT/(PREFIX+'-result.json');sources=[Path(__file__),review,result,IDENTITY,MATRIX,CATALOG,CONTEXT,
            ROOT/'tools/research/board_training_policy_v1.py']
        for identity in read(IDENTITY)['source_banks']:
            sources.append(Path('S:/GTOpen-research/board-root-matched-prefix-v1')/identity['arm']/'objects'/identity['model_references'][0]['file'])
        hashes={str(p):sha(p) for p in sources}
        atomic_json(reg,dict(inputs=hashes,post_hoc=True,reason='Largest diagnostic costs occurred at tiny hero reaches and uniform-looking policies.',
            cases=80,workers=4,maximum_seconds=300,scope='Describe initialization contribution; do not change policy weights or discard cases.'))
        with ProcessPoolExecutor(max_workers=4) as pool:
            rows=[]
            for chunk in pool.map(one,read(result)['routes']):
                assert time.monotonic()-began<300 and production_available() and not OTHER.exists();rows.extend(chunk)
        verify(hashes)
        output=dict(passed=True,complete=True,post_hoc=True,registration_sha256=sha(reg),rows=rows,
            summary=summarize(rows),by_bank={b:summarize([r for r in rows if r['bank']==b]) for b in ('A','B')},
            maximum_reach_identity_error=max(r['behavioral_vs_mixture_reach_error'] for r in rows),seconds=time.monotonic()-began,
            gpu_used=False,production_modified=False,policies_changed=False)
        atomic_json(destination,output);print(json.dumps({k:output[k] for k in ('passed','summary','by_bank','maximum_reach_identity_error','seconds')}),flush=True)
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
