"""Expose hand-level postflop residuals hidden by small own preflop reach.

SUBTREE MANIFEST SOURCE OUTPUT_PREFIX WORKER...; complete panels only.
This descriptive audit never prunes hands or changes the registered gates.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import continuation_transfer_aggregate as transfer
import integrated_coverage as c


def entry_joint(tree,manifest):
    w=np.asarray(tree['incoming_class_mass'])[:,c.CLASSES]/c.COUNTS[c.CLASSES]
    w/=w.max(1)[:,None]
    w[w<1e-5]=0
    ix=[np.flatnonzero(x) for x in w]
    masks=[c.MASKS[x] for x in ix]
    raw=w[0,ix[0]][:,None]*w[1,ix[1]][None,:]*((masks[0][:,None]&masks[1][None,:])==0)
    chance=np.zeros_like(raw)
    total=sum(b['weight'] for b in manifest['boards'])
    for board in manifest['boards']:
        for perm in c.PERMS:
            bm=np.uint64(sum(1<<card for card in c.cards(c.relabel(board['board'],perm))))
            legal=[(m&bm)==0 for m in masks]
            chance+=board['weight']/total/24*legal[0][:,None]*legal[1][None,:]
    return w,ix,raw*chance


def terminal_reaches(tree,policy,ix):
    result={}
    def walk(i,reaches,path):
        node=tree['nodes'][i]
        if node['kind']!=0:
            result[i]=(reaches,path)
            return
        actor=node['actor']
        for a,child in enumerate(node['children']):
            next_reach=[r.copy() for r in reaches]
            next_reach[actor]*=np.asarray(policy[i][a])[ix[actor]]
            walk(child,next_reach,path+[node['actions'][a]['label']])
    walk(0,[np.ones(len(x)) for x in ix],[])
    return result


def diagnose(tree,manifest,source,workers):
    combined=transfer.aggregate(tree,manifest,source,workers)
    e=combined['records'][-1]['evaluation']
    w,ix,joint=entry_joint(tree,manifest)
    z=float(joint.sum())
    assert abs(z/combined['root_normalizer']-1)<1e-7
    by_board={x['boards'][0]:x for x in workers}
    reaches=terminal_reaches(tree,e['preflop_policy'],ix)
    branches=[]
    reconstructed=np.zeros(2)
    for i,(reach,path) in reaches.items():
        node=tree['nodes'][i]
        if node['kind']!=2 or min(node['invested'])>=200:
            continue
        actual=float((joint*reach[0][:,None]*reach[1][None,:]).sum()/z)
        for p in range(2):
            difference=np.zeros(1326)
            for board,q in zip(combined['boards'],combined['board_weights']):
                v=by_board[board]['terminal_values']['values']
                difference+=q*(np.asarray(v[2*p+1][i])-np.asarray(v[2*p][i]))
            numerator=difference[ix[p]]*w[p,ix[p]]
            counterfactual=(joint*reach[1][None,:]).sum(1) if p==0 else (joint*reach[0][:,None]).sum(0)
            contribution=float(numerator@reach[p]/z)
            reconstructed[p]+=contribution
            rows=[]
            for cls in range(169):
                mask=c.CLASSES[ix[p]]==cls
                den=float(counterfactual[mask].sum())
                if den<=0:
                    continue
                num=float(numerator[mask].sum())
                own=float(counterfactual[mask]@reach[p][mask]/den)
                rows.append(dict(hand=e['hands'][cls]['hand'],own_path_probability=own,
                    counterfactual_mass=den/z,actual_mass=float(counterfactual[mask]@reach[p][mask]/z),
                    conditional_postflop_gain_bb=num/den,
                    contribution_bb=float(numerator[mask]@reach[p][mask]/z)))
            assert abs(sum(r['contribution_bb'] for r in rows)-contribution)<1e-8
            branches.append(dict(node=i,path=path,seat=p,branch_probability=actual,
                                 reached_residual_bb=contribution,hands=rows))
    assert max(abs(reconstructed-np.asarray(e['postflop_gaps'])))<1e-6
    return dict(iteration=combined['records'][-1]['iteration'],boards=len(combined['boards']),
        postflop_residual_bb=e['postflop_gap_total'],reconstructed_by_player_bb=reconstructed.tolist(),
        branches=branches,accounting=combined['independent_accounting'],
        interpretation='Conditional residual is the gain from changing this hand\'s postflop play against the fixed opponent, averaged over this panel. Counterfactual mass removes only this seat\'s earlier action probabilities; it retains the entering hand distribution and opponent actions. Own path probability explains why a large conditional residual can receive tiny weight in the overall gap. These are diagnostics, not per-hand error bounds, accuracy certificates or new acceptance thresholds. Hands are never dropped because they are off path.')


def main():
    tree_path,manifest_path,source_path,prefix,*worker_paths=sys.argv[1:]
    prefix=Path(prefix)
    assert not prefix.with_suffix('.json').exists() and not prefix.with_suffix('.md').exists()
    result=diagnose(*[transfer.read(p) for p in [tree_path,manifest_path,source_path]],
                    [transfer.read(p) for p in worker_paths])
    files=[tree_path,manifest_path,source_path,*worker_paths,__file__,transfer.__file__]
    result['inputs_sha256']={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files}
    prefix.with_suffix('.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    lines=['# Conditional postflop residuals','',result['interpretation'],'',
           f'Complete panel: {result["boards"]} boards, {result["iteration"]} iterations per board. '
           f'Overall postflop residual: {result["postflop_residual_bb"]:.8f} bb.','',
           'Tables show the largest conditional residuals among all supported hands. '
           'Every supported hand is retained in the JSON, including very small counterfactual masses.']
    summary=[]
    for branch in result['branches']:
        lines += ['',f'## Seat {branch["seat"]}: '+ ' / '.join(branch['path']),'',
                  f'Actual branch probability: {branch["branch_probability"]*100:.6f}%; '
                  f'reached residual: {branch["reached_residual_bb"]:.8f} bb.','',
                  '| Hand | Own path probability | Counterfactual mass | Conditional gain (bb) | Overall contribution (bb) |',
                  '|---|---:|---:|---:|---:|']
        ordered=sorted(branch['hands'],key=lambda r:r['conditional_postflop_gain_bb'],reverse=True)
        for row in ordered[:20]:
            lines.append(f'| {row["hand"]} | {row["own_path_probability"]:.3g} | '
                         f'{row["counterfactual_mass"]:.3g} | {row["conditional_postflop_gain_bb"]:.6f} | '
                         f'{row["contribution_bb"]:.8f} |')
        summary.append(dict(node=branch['node'],seat=branch['seat'],largest=ordered[0] if ordered else None))
    prefix.with_suffix('.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps(dict(overall_postflop_residual_bb=result['postflop_residual_bb'],largest_conditional_by_branch=summary)))


if __name__=='__main__':
    main()
