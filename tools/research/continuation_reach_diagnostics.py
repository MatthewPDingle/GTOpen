"""Read-only reach audit for completed source policies on their own chance panels.

Shows how much a reached-policy convergence metric can say about rare or
off-path decisions. No new solves, policy changes, or held-out results.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import integrated_coverage as c
import continuation_transfer_aggregate as transfer


def reach_rows(nodes, sigma, joint):
    """Exact pair-distribution walk; each seat's path products stay separate."""
    rows = []
    terminal_probability = 0.

    def walk(i, reach, path):
        nonlocal terminal_probability
        n = nodes[i]
        actual = float((joint*reach[0][:,None]*reach[1][None,:]).sum())
        if n['kind'] == 0:
            p = n['actor']
            assert sigma[i].shape == (len(n['children']), joint.shape[p])
            assert np.max(abs(sigma[i].sum(0)-1)) < 1e-10
            for action, child in enumerate(n['children']):
                next_reach = [r.copy() for r in reach]
                next_reach[p] *= sigma[i][action]
                walk(child, next_reach, path+[n['actions'][action]['label']])
            return
        terminal_probability += actual
        # All-in and fold terminals need no learned postflop continuation.
        if n['kind'] != 2 or min(n['invested']) >= 200:
            return
        seats = []
        for p in range(2):
            counterfactual = (joint*reach[1][None,:]).sum(1) if p == 0 else (joint*reach[0][:,None]).sum(0)
            den = float(counterfactual.sum())
            bands = {}
            for label, threshold in [('exactly_zero',0.),('at_most_1e-6',1e-6),('at_most_0.001',.001),('at_most_0.01',.01)]:
                bands[label] = float(counterfactual[reach[p] <= threshold].sum()/den) if den > 0 else None
            seats.append(dict(seat=p, counterfactual_mass=den,
                mean_own_path_probability=actual/den if den>0 else None,
                counterfactual_share_in_low_own_reach=bands))
        rows.append(dict(node=i, path=path, pot=n['pot'], on_policy_probability=actual, seats=seats))

    assert abs(joint.sum()-1) < 1e-10
    walk(0, [np.ones(joint.shape[0]),np.ones(joint.shape[1])], [])
    assert abs(terminal_probability-1) < 1e-9
    return rows, terminal_probability


def controls():
    nodes=[dict(kind=0,actor=0,children=[1,2],actions=[dict(label='fold'),dict(label='call')]),
           dict(kind=1,invested=[6,18]),dict(kind=2,invested=[18,18],pot=39.5)]
    joint=np.array([[.1,.2],[.3,.4]])
    fixed_fold=[np.array([[1.,1.],[0.,0.]]),np.array([]),np.array([])]
    rows,_=reach_rows(nodes,fixed_fold,joint)
    row=rows[0]
    assert row['on_policy_probability']==0
    assert row['seats'][0]['counterfactual_mass']==1
    assert row['seats'][0]['counterfactual_share_in_low_own_reach']['exactly_zero']==1
    assert row['seats'][1]['counterfactual_mass']==0
    assert row['seats'][1]['mean_own_path_probability'] is None
    mixed=[np.array([[.75,.25],[.25,.75]]),np.array([]),np.array([])]
    rows,_=reach_rows(nodes,mixed,joint)
    assert abs(rows[0]['on_policy_probability']-(.3*.25+.7*.75))<1e-12
    return True


def main():
    tree_path, source_path, output = map(Path,sys.argv[1:])
    assert not output.exists()
    tree,source=transfer.read(tree_path),transfer.read(source_path)
    assert source['records'][-1]['iteration']==2000, 'Completed registered sources only'
    assert source['suit_orbits'] is True and source['entry_cutoff']==1e-5
    w=np.array(tree['incoming_class_mass'])[:,c.CLASSES]/c.COUNTS[c.CLASSES]
    w/=w.max(1)[:,None];w[w<1e-5]=0
    ix=[np.flatnonzero(x) for x in w]
    masks=[c.MASKS[x] for x in ix]
    base=w[0,ix[0]][:,None]*w[1,ix[1]][None,:]*((masks[0][:,None]&masks[1][None,:])==0)
    chance=np.zeros_like(base)
    panel=source['manifest']
    den=sum(b['weight'] for b in panel['boards'])
    for b in panel['boards']:
        for perm in c.PERMS:
            bm=np.uint64(sum(1<<card for card in c.cards(c.relabel(b['board'],perm))))
            legal=[(m&bm)==0 for m in masks]
            chance+=b['weight']/den/24*legal[0][:,None]*legal[1][None,:]
    raw=base*chance
    assert abs(raw.sum()/source['root_normalizer']-1)<1e-7
    policy=source['records'][-1]['evaluation']['preflop_policy']
    sigma=[np.asarray(p)[:,ix[n['actor']]] if n['kind']==0 else np.array([]) for n,p in zip(tree['nodes'],policy)]
    rows,terminal=reach_rows(tree['nodes'],sigma,raw/raw.sum())
    result=dict(controls_passed=controls(),terminal_probability=terminal,
        source_iteration=2000,source_boards=len(panel['boards']),continuations=rows,
        interpretation='Counterfactual mass holds opponent path actions fixed and removes this seat\'s own path actions. Low-own-reach shares describe weakly weighted portions of a frozen-policy postflop convergence metric; they do not prove incorrect values. No threshold removes hands or changes a gate. Off-path policies remain legal but can be poorly determined. This diagnostic reads only the completed source\'s own development panel.',
        inputs_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [tree_path,source_path,Path(__file__)]})
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['inputs_sha256','interpretation']},indent=2))


if __name__=='__main__':
    main()
