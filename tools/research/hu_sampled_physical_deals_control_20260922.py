"""Check resumable panel and full-deck samplers against frozen and dense oracles."""
import copy
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from loopback_research_validation import idle
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS, MASKS, CLASSES

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-deals-v1'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p,d):
    with p.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(d,separators=(',',':'))+'\n')


def main():
    assert idle()
    paths=[Path(__file__),ROOT/'tools/research/sampled_physical_deals_v1.py',
           ROOT/'tools/research/storage_strategic_common_prior_20260920.py',
           ROOT/'tools/research/loopback_research_validation.py']+[OUT/p for p in
           ('bb-context-candidate.json','capacity-existing112-manifest.json',
            'sampled-poker-v1-fixture.json','sampled-deal-oracle-v1-result.json')]
    frozen={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    reg=OUT/(PREFIX+'-registration.json')
    save(reg,dict(inputs=frozen,panel_seed=2026092201,full_deck_seed=2026092501,
        maximum_seconds=120,full_deck_draws=512,
        checks='Reproduce all 8192 frozen panel deals; compare all board probabilities/masses; full-deck dense private-pair law; chunk and checkpoint identity; card legality and supported classes; invalid state rejection.',
        full_deck_law='Compatible physical private pairs proportional to frozen entry weights; then five public cards uniformly without replacement from remaining 48, with flop sorted and ordered turn/river.',
        scope='Sampling-law and continuation control only. Full deck changes the board population; no trained strategy or performance claim.',
        production_modified=False,no_gpu=True))
    started=time.monotonic()
    context,manifest=paths[4].read_text(),paths[5].read_text()
    panel=PhysicalDeals(context,mode='panel',seed=2026092201,manifest_source=manifest)
    oracle=json.loads(paths[7].read_text())['contexts'][1]
    assert oracle['context']=='bb_context'
    masses=np.array([r['compatible_pair_mass'] for r in oracle['rows']])
    probabilities=np.array([r['board_probability'] for r in oracle['rows']])
    panel_mass_error=float(np.max(np.abs(np.array(panel.masses)/masses-1)))
    panel_probability_error=float(np.max(np.abs(panel.board_probability-probabilities)))
    assert panel_mass_error<1e-12 and panel_probability_error<1e-14
    sample=panel.sample(8192);frozen_fixture=json.loads(paths[6].read_text())
    assert sample['deals']==frozen_fixture['deals']
    assert idle() and time.monotonic()-started<120
    full=PhysicalDeals(context,mode='full_deck',seed=2026092501)
    compatible=(MASKS[:,None]&MASKS[None,:])==0
    # Independent dense joint distribution; no subtraction identity in reference.
    joint=full.weights[0,:,None]*full.weights[1,None,:]*compatible
    total=float(joint.sum());joint/=total
    marginal=joint.sum(axis=1)
    marginal_error=float(np.max(np.abs(marginal-full.first[0])))
    reconstructed=np.zeros_like(joint)
    for i in range(len(PAIRS)):
        if full.first[0][i]==0:continue
        second=full.live[0][1]*((MASKS&MASKS[i])==0);second/=second.sum()
        reconstructed[i]=full.first[0][i]*second
    pair_error=float(np.max(np.abs(reconstructed-joint)))
    assert marginal_error<1e-14 and pair_error<1e-14 and abs(full.masses[0]/total-1)<1e-12
    # The full-deck law does not inherit the selected-board marginal distribution.
    fixed_private_marginal=np.sum(np.array(panel.first)*panel.board_probability[:,None],axis=0)
    panel_full_prior_tv=float(np.abs(fixed_private_marginal-marginal).sum()/2)
    assert panel_full_prior_tv>1e-5
    whole=full.sample(512)
    prefix=PhysicalDeals(context,mode='full_deck',seed=2026092501);first=prefix.sample(173)
    checkpoint=prefix.checkpoint();path=OUT/(PREFIX+'-checkpoint.json');save(path,checkpoint)
    resumed=PhysicalDeals.restore(json.loads(path.read_text()),context)
    tail=resumed.sample(339)
    assert first['deals']+tail['deals']==whole['deals'] and resumed.checkpoint()==full.checkpoint()
    panel_checkpoint=panel.checkpoint()
    panel_restored=PhysicalDeals.restore(panel_checkpoint,context,manifest)
    assert panel.sample(31)==panel_restored.sample(31) and panel.checkpoint()==panel_restored.checkpoint()
    pair_index={tuple(map(int,p)):i for i,p in enumerate(PAIRS)}
    observed=[set(),set()];flops=set()
    for deal in whole['deals']:
        assert len(deal)==9 and len(set(deal))==9 and all(0<=c<52 for c in deal)
        assert deal[:2]==sorted(deal[:2]) and deal[2:4]==sorted(deal[2:4]) and deal[4:7]==sorted(deal[4:7])
        for p in (0,1):
            i=pair_index[tuple(deal[2*p:2*p+2])]
            assert full.weights[p,i]>0;observed[p].add(int(CLASSES[i]))
        flops.add(tuple(deal[4:7]))
    # Independent direct full-deck replay: use dense marginal/conditional law,
    # and compare the entire physical draw stream including ordered runouts.
    rng=np.random.Generator(np.random.PCG64(2026092501));direct=[]
    for _ in range(512):
        i=int(rng.choice(len(PAIRS),p=marginal));j=int(rng.choice(len(PAIRS),p=joint[i]/marginal[i]))
        private=list(map(int,PAIRS[i]))+list(map(int,PAIRS[j]))
        remaining=np.array([c for c in range(52) if c not in private])
        draw=private+list(map(int,rng.choice(remaining,size=5,replace=False)))
        draw[:2]=sorted(draw[:2]);draw[2:4]=sorted(draw[2:4]);draw[4:7]=sorted(draw[4:7]);direct.append(draw)
    assert direct==whole['deals']
    rejected=[]
    variants=[lambda:PhysicalDeals(context,mode='full_deck',seed=1,manifest_source=manifest),
              lambda:PhysicalDeals(context,mode='panel',seed=1),
              lambda:PhysicalDeals.restore(checkpoint,context+' '),
              lambda:PhysicalDeals.restore(panel_checkpoint,context,manifest+' '),
              lambda:full.sample(-1),lambda:full.sample(65537)]
    invalid=copy.deepcopy(checkpoint);invalid['numpy_version']='changed-runtime'
    variants.append(lambda:PhysicalDeals.restore(invalid,context))
    before=full.checkpoint()
    for i,operation in enumerate(variants):
        try:operation()
        except ValueError:rejected.append(i)
        else:raise AssertionError('Invalid sampler input accepted')
    assert before==full.checkpoint()
    for name,h in frozen.items():assert sha(ROOT/name)==h,name
    full_path=OUT/(PREFIX+'-full-deck-fixture.json');save(full_path,whole)
    result=dict(passed=True,inputs_verified=len(frozen),frozen_panel_deals_reproduced=8192,
        maximum_panel_mass_relative_error=panel_mass_error,maximum_panel_probability_error=panel_probability_error,
        maximum_full_deck_marginal_error=marginal_error,maximum_full_deck_joint_error=pair_error,
        full_deck_dense_reference_deals_matched=512,full_deck_chunk_and_checkpoint_identity=True,
        panel_checkpoint_identity=True,full_deck_classes_observed=list(map(len,observed)),
        supported_classes=[len(set(CLASSES[w>0])) for w in full.weights],
        unique_physical_flops_in_draws=len(flops),panel_vs_full_deck_private_marginal_tv=panel_full_prior_tv,
        invalid_inputs_rejected=len(rejected),seconds=time.monotonic()-started,
        registration_sha256=sha(reg),artifacts={p.relative_to(ROOT).as_posix():sha(p) for p in (path,full_path)},
        physical_poker_convergence_qualified=False,production_modified=False)
    save(OUT/(PREFIX+'-result.json'),result);print(json.dumps(result))


if __name__=='__main__':main()
