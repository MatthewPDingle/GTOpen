"""Exact finite-sum qualification of board/private-pair sampling, not a trainer."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from storage_strategic_common_prior_20260920 import PAIRS, MASKS, CLASSES, COUNTS

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'research/preflop-evolution'
OUT=BASE/'blind-defense-20260922'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    paths={'manifest':OUT/'capacity-existing112-manifest.json',
           'bb_context':OUT/'bb-context-candidate.json',
           'original_context':BASE/'conditional-hu-20260919/subtree.json',
           'original_result':BASE/'ssd-storage-20260920/strategic-weighted112-2000-v1-result.json',
           'script':Path(__file__),
           'card_helpers':ROOT/'tools/research/storage_strategic_common_prior_20260920.py'}
    reg_path=OUT/'sampled-deal-oracle-v1-registration.json'
    result_path=OUT/'sampled-deal-oracle-v1-result.json'
    assert not reg_path.exists() and not result_path.exists()
    registration={'created_at_unix':time.time(),'inputs':{str(p.relative_to(ROOT)):sha(p) for p in paths.values()},
        'scope':'All 112 fixed flops, full supported physical private pairs, original and BB contexts. Finite-sum identity only; no sampled regret updates, averaging or convergence claim.',
        'joint_law':'P(board,i,j) proportional to board_weight * entry0[i] * entry1[j] * physical_compatibility',
        'candidate':'Draw board with probability proportional to weight times compatible pair mass; draw first hand by its compatible marginal, then second hand conditional on first.',
        'gates':{'max_conditional_pair_error':1e-14,'relative_normalizer_error':1e-12,'original_engine_normalizer_relative_error':1e-6},
        'negative_controls':['board weights without compatible mass','first hand without compatible opponent mass'],
        'symmetry_limit':'Checks canonical board coordinates and class marginals. Full physical preflop symmetry requires shared uniform global suit relabeling; not implemented by this oracle.'}
    reg_path.write_text(json.dumps(registration,indent=2),encoding='utf-8',newline='\n')
    manifest=json.loads(paths['manifest'].read_text())
    boards=manifest['boards'];assert len(boards)==112
    weights=np.array([r['weight'] for r in boards],dtype=float);weights/=weights.sum()
    compatible=(MASKS[:,None]&MASKS[None,:])==0
    records=[];started=time.monotonic()
    for key in ['original_context','bb_context']:
        context=json.loads(paths[key].read_text())
        w=np.array(context['incoming_class_mass'])[:,CLASSES]/COUNTS[CLASSES]
        w/=w.max(1)[:,None];w[w<1e-5]=0
        rows=[];pair_error=0.;normalizer_error=0.;naive_pair_tv=0.
        for row in boards:
            board=row['board'];assert len(board)==6
            cs=['23456789TJQKA'.index(board[i])*4+'cdhs'.index(board[i+1]) for i in [0,2,4]]
            assert len(set(cs))==3
            mask=sum(1<<c for c in cs)
            legal=(MASKS & np.uint64(mask))==0
            live=w*legal[None,:]
            # Independent dense reference versus card-subtraction sampler.
            joint=live[0,:,None]*live[1,None,:]*compatible
            z=float(joint.sum());assert z>0
            cards=np.bincount(PAIRS.ravel(),weights=np.repeat(live[1],2),minlength=52)
            available=live[1].sum()-cards[PAIRS[:,0]]-cards[PAIRS[:,1]]+live[1]
            available=np.maximum(available,0.)
            analytic=float(live[0]@available)
            normalizer_error=max(normalizer_error,abs(analytic/z-1))
            first=live[0]*available/analytic
            second=np.divide(live[1,None,:]*compatible,available[:,None],out=np.zeros_like(joint),where=available[:,None]>0)
            sampled=first[:,None]*second
            pair_error=max(pair_error,float(np.max(abs(sampled-joint/z))))
            assert abs(float(sampled.sum())-1)<1e-12
            naive=live[0,:,None]/live[0].sum()*second
            naive_pair_tv=max(naive_pair_tv,float(abs(naive-joint/z).sum()/2))
            rows.append({'board':board,'compatible_pair_mass':z})
        masses=np.array([r['compatible_pair_mass'] for r in rows])
        global_z=float(weights@masses)
        board_probability=weights*masses/global_z
        assert abs(float(board_probability.sum())-1)<1e-12
        naive_board_tv=float(abs(board_probability-weights).sum()/2)
        assert pair_error<1e-14 and normalizer_error<1e-12
        assert naive_pair_tv>1e-5 and naive_board_tv>1e-5
        original_error=None
        if key=='original_context':
            original=json.loads(paths['original_result'].read_text())
            assert original['boards']==[r['board'] for r in boards]
            assert np.max(abs(np.array(original['board_weights'])-weights))<1e-12
            original_error=abs(global_z/original['root_normalizer']-1)
            assert original_error<1e-6
        for i,r in enumerate(rows):r['board_probability']=float(board_probability[i])
        records.append({'context':key,'global_normalizer':global_z,'max_pair_probability_error':pair_error,
            'max_card_subtraction_normalizer_relative_error':normalizer_error,
            'original_engine_normalizer_relative_error':original_error,
            'naive_board_law_tv':naive_board_tv,'maximum_naive_private_pair_tv':naive_pair_tv,'rows':rows})
    for name,h in registration['inputs'].items():assert sha(ROOT/name)==h
    result={'passed':True,'contexts':records,'registration_sha256':sha(reg_path),
            'elapsed_seconds':time.monotonic()-started,'gpu_used':False,'trainer_qualified':False,
            'strategy_accuracy_claim':False,'production_modified':False}
    result_path.write_text(json.dumps(result,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps({**result,'contexts':[{k:v for k,v in c.items() if k!='rows'} for c in records]},indent=2))


if __name__=='__main__':main()
