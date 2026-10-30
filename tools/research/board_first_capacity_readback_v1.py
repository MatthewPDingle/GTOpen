"""Read-only native topology and actual-range board capacity measurement."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
import numpy as np
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS,MASKS

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    began=time.monotonic()
    cp=OUT/'bb-context-candidate.json'
    exe=ROOT/'target/release/examples/hu_board_first_capacity_v1.exe'
    src=ROOT/'crates/solver/examples/hu_board_first_capacity_v1.rs'
    native=json.loads(subprocess.check_output([str(exe),str(cp)],creationflags=subprocess.CREATE_NO_WINDOW))
    assert native['passed'] and native['decision_histories_per_complete_runout']==455
    sampler=PhysicalDeals(cp.read_text(),mode='full_deck',seed=0)
    compatible=(MASKS[:,None]&MASKS[None,:])==0
    joint=sampler.weights[0,:,None]*sampler.weights[1,None,:]*compatible
    total=float(joint.sum())
    error=float(np.max(np.abs(joint.sum(1)/total-sampler.first[0])))
    assert error<1e-12 and abs(total/sampler.masses[0]-1)<1e-12
    # Every hand pair permits C(48,5) unordered five-card boards. The same ratio
    # applies to sorted flop plus ordered turn/river: the factor of 20 cancels.
    ratio=math.comb(52,5)/math.comb(48,5)
    rows=[]
    for board in ([0,5,10,15,20],[48,49,50,0,4],[0,4,8,12,16]):
        mask=np.uint64(sum(1<<c for c in board))
        legal=(MASKS&mask)==0
        live=sampler.weights*legal
        counts=np.count_nonzero(live,axis=1)
        full=live[0,:,None]*live[1,None,:]*compatible
        mass=float(full.sum())
        bycard=np.bincount(PAIRS.ravel(),weights=np.repeat(live[1],2),minlength=52)
        second=live[1].sum()-bycard[PAIRS[:,0]]-bycard[PAIRS[:,1]]+live[1]
        fast=live[0]*second
        marginal_error=float(np.max(np.abs(fast-full.sum(1))))
        assert marginal_error<1e-9 and abs(float(fast.sum())-mass)<1e-8
        # An upper bound prior to suit-canonical query deduplication. This is
        # observation storage only, not a complete GPU memory requirement.
        context=json.loads(cp.read_text())
        histories=[sum(1 for n in context['nodes'] if len(n['children']) and n['actor']==p) for p in (0,1)]
        for branch in native['branches']:
            for p in (0,1):histories[p]+=sum(branch['actions_by_player_street'][p])
        assert sum(histories)==455
        observations=sum(int(n)*h for n,h in zip(counts,histories))
        dense_pairs=int(counts[0]*counts[1])
        rows.append(dict(board=board,live_private_hands=counts.tolist(),
            supported_compatible_pairs=int(np.count_nonzero(full)),dense_pair_slots=dense_pairs,
            board_importance_mass_ratio=mass/total*ratio,
            dense_vs_card_subtraction_max_error=marginal_error,
            raw_observation_upper_bound=observations,
            float32_302_feature_matrix_mib=observations*302*4/2**20,
            one_float64_pair_matrix_mib=dense_pairs*8/2**20,
            one_float64_pair_value_per_decision_gib=dense_pairs*455*8/2**30))
    paths=[cp,exe,src,Path(__file__),ROOT/'tools/research/sampled_physical_deals_v1.py',
           ROOT/'tools/research/storage_strategic_common_prior_20260920.py',
           *[(ROOT/'crates/solver/examples/research_sampled'/f) for f in
             ('state.rs','poker_reference_v1.rs','observation_v1.rs','batch_queries_v1.rs')]]
    result=dict(passed=True,inputs={str(p):sha(p) for p in paths},native=native,boards=rows,
        original_sampler_marginal_max_error=error,seconds=time.monotonic()-began,gpu_used=False,
        production_modified=False,training_changed=False,
        scope='Topology and allocation arithmetic for three fixed physical runouts. No all-pair payoff calculation, full-deck board expectation, GPU peak allocation or speed measurement.')
    with (OUT/'board-first-capacity-readback-v1-result.json').open('x') as f:
        json.dump(result,f,separators=(',',':'),allow_nan=False)
    print(json.dumps(dict(passed=True,seconds=result['seconds'],boards=rows)),flush=True)


if __name__=='__main__':main()
