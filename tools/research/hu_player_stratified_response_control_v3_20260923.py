"""Independent compatible-pair conditioning checks for both responder seats."""
import json
import time
from pathlib import Path
import numpy as np
from sampled_player_stratified_response_deals_v2 import sample, private_law
from sampled_stratified_response_deals_v1 import sample as bb_v1
from sampled_physical_root_evaluation_v1 import ROOT,sha,save,hand_class
from storage_strategic_common_prior_20260920 import PAIRS, MASKS, CLASSES

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='player-stratified-response-control-v3'


def independent_joint(context):
    # Reconstruct per-combination weights from class masses independently of
    # PhysicalDeals, then enumerate compatibility with explicit card sets.
    counts=np.bincount([hand_class(list(map(int,p))) for p in PAIRS],minlength=169)
    masses=np.asarray(context['incoming_class_mass'],dtype=float)
    weights=np.array([[masses[p,hand_class(list(map(int,pair)))]/counts[hand_class(list(map(int,pair)))] for pair in PAIRS] for p in (0,1)])
    weights/=weights.max(1)[:,None];weights[weights<1e-5]=0
    joint=np.zeros((1326,1326))
    for i,(a,b) in enumerate(PAIRS):
        compatible=(PAIRS[:,0]!=a)&(PAIRS[:,0]!=b)&(PAIRS[:,1]!=a)&(PAIRS[:,1]!=b)
        joint[i]=weights[0,i]*weights[1]*compatible
    return joint/joint.sum(),weights


def main():
    started=time.monotonic();cp=OUT/'bb-context-candidate.json';source=cp.read_text()
    sources=[Path(__file__),cp,*[ROOT/'tools/research'/n for n in (
        'sampled_player_stratified_response_deals_v2.py','sampled_stratified_response_deals_v1.py',
        'sampled_physical_deals_v1.py','sampled_physical_root_evaluation_v1.py','storage_strategic_common_prior_20260920.py')]]
    inputs={str(p):sha(p) for p in sources};rp=OUT/f'{PREFIX}-registration.json'
    assert not rp.exists()
    save(rp,dict(inputs=inputs,seeds=[193931,193932],per_class=16,
        scope='CPU sampling-law and role-preservation controls only; no model queries or strategic evaluation.'))
    context=json.loads(source);joint,weights=independent_joint(context)
    classes=list(range(169));rows=[];max_error=0.;max_conditional=0.;streams=[]
    for player in (0,1):
        oriented=joint if player==0 else joint.T
        expected_marginal=oriented.sum(1)
        classes=[c for c in range(169) if expected_marginal[CLASSES==c].sum()>0]
        seed=193931+player
        a=sample(source,player=player,seed=seed,per_class=16,classes=classes)
        assert a==sample(source,player=player,seed=seed,per_class=16,classes=classes)
        assert a['deals']!=sample(source,player=player,seed=seed+101,per_class=16,classes=classes)['deals']
        assert np.bincount(a['hand_classes'],minlength=169).tolist()==[16 if c in classes else 0 for c in range(169)]
        assert [hand_class(d[2*player:2*player+2]) for d in a['deals']]==a['hand_classes']
        assert all(len(d)==len(set(d))==9 and all(type(x) is int and 0<=x<52 for x in d) for d in a['deals'])
        base,marginal,opponent=private_law(source,player=player,seed=seed)
        oriented=joint if player==0 else joint.T
        expected_marginal=oriented.sum(1)
        max_error=max(max_error,float(np.max(abs(marginal-expected_marginal))))
        for c in classes:
            mask=CLASSES==c;mass=expected_marginal[mask].sum()
            actual_class_mass=marginal[mask].sum()
            assert abs(a['original_class_masses'][classes.index(c)]-mass)<1e-13
            for i in np.flatnonzero(mask & (marginal>0)):
                cond=opponent*((MASKS&MASKS[i])==0);cond/=cond.sum()
                actual=marginal[i]/actual_class_mass*cond
                expected=oriented[i]/mass
                max_conditional=max(max_conditional,float(np.max(abs(actual-expected))))
        if player==0:
            old=bb_v1(source,seed=seed,per_class=16,classes=classes)
            assert a['deals']==old['deals'] and a['original_class_masses']==old['original_class_masses']
        streams.append(a);rows.append(dict(player=player,deals=len(a['deals']),classes=len(classes),supported_classes=classes,per_class=16,repeat_exact=True))
    assert max_error<1e-13 and max_conditional<1e-12
    # Swapping the entry ranges and actor must swap private columns without
    # changing the shared board when the RNG seed is retained.
    classes=list(range(169))
    swapped=dict(context,incoming_class_mass=context['incoming_class_mass'][::-1])
    a=sample(source,player=0,seed=193933,per_class=4,classes=classes)
    b=sample(json.dumps(swapped),player=1,seed=193933,per_class=4,classes=classes)
    assert [d[2:4]+d[:2]+d[4:] for d in a['deals']]==b['deals']
    rejected=0
    bad=[dict(player=True),dict(player=-1),dict(player=2),dict(per_class=0),dict(per_class=True),
        dict(per_class=513),dict(classes=[]),dict(classes=[1,1]),dict(classes=[2,1]),dict(classes=[169]),dict(seed=-1)]
    for override in bad:
        kwargs=dict(player=0,seed=0,per_class=1,classes=[0]);kwargs.update(override)
        try:sample(source,**kwargs)
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid request accepted')
    for player in (0,1):
        sparse=json.loads(source);sparse['incoming_class_mass'][player][0]=0
        try:sample(json.dumps(sparse),player=player,seed=0,per_class=1,classes=[0])
        except ValueError:rejected+=1
        else:raise AssertionError('Unsupported actor class accepted')
    assert rejected==13
    for p,h in inputs.items():assert sha(p)==h,p
    result=dict(passed=True,registration_sha256=sha(rp),inputs=inputs,players=rows,
        maximum_combo_marginal_error=max_error,maximum_joint_conditional_error=max_conditional,
        player_zero_matches_v1_exactly=True,role_swap_exact=True,negative_controls=rejected,
        seconds=time.monotonic()-started,gpu_used=False,production_modified=False,strategic_evaluation=False,
        scope='Both actor-conditional private pair laws match independent enumeration; physical player columns and shared board are preserved. Separate response-training streams remain required; neither is an unweighted population test.')
    save(OUT/f'{PREFIX}-result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='inputs'}))


if __name__=='__main__':main()
