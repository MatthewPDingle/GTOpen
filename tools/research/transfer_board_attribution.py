"""Attribute one panel-wide preflop deviation to boards without a flop oracle.

SUBTREE MANIFEST SOURCE OUTPUT_PREFIX WORKER... . Descriptive only.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import continuation_transfer_aggregate as transfer
import integrated_coverage as coverage
from transfer_decision_diagnostics import root_values


def contributions(values, chance, sigma, own, z):
    # Pick once per private combo, AFTER averaging hidden boards. Individual
    # boards may contribute negatively to that same preflop deviation.
    q = np.einsum('b,bah->ah',chance,values)
    selected = q.argmax(axis=0)
    current = np.einsum('ah,bah->bh',sigma,values)
    chosen = values[:,selected,np.arange(len(own))]
    pieces = chance[:,None]*(chosen-current)*own[None,:]/z
    gain = float((q.max(0)-(q*sigma).sum(0)) @ own/z)
    assert abs(pieces.sum()-gain)<1e-9
    return pieces,selected,gain


def hidden_chance_control():
    values=np.array([[[1.],[-1.]],[[-1.],[1.]]])
    pieces,_,gain=contributions(values,np.array([.5,.5]),np.array([[.5],[.5]]),np.ones(1),1.)
    oracle=float(np.mean(values.max(axis=1)))
    assert gain==0 and pieces.sum()==0 and oracle==1
    assert np.any(pieces<0) and np.any(pieces>0)
    return dict(panel_choice_gain=gain,invalid_board_oracle_gain=oracle,
                signed_contributions_preserved=True)


def main():
    tree_path,panel_path,source_path,prefix,*worker_paths=sys.argv[1:]
    prefix=Path(prefix)
    assert not prefix.with_suffix('.json').exists() and not prefix.with_suffix('.md').exists()
    control=hidden_chance_control()
    tree,panel,source=[transfer.read(p) for p in [tree_path,panel_path,source_path]]
    workers=[transfer.read(p) for p in worker_paths]
    combined=transfer.aggregate(tree,panel,source,workers)
    evaluation=combined['records'][-1]['evaluation']
    policy=evaluation['preflop_policy']
    by_board={w['boards'][0]:w for w in workers}
    values=[]
    for board in combined['boards']:
        leaves=np.zeros((len(tree['nodes']),1326))
        for i,n in enumerate(tree['nodes']):
            if n['kind']!=0:
                leaves[i]=by_board[board]['terminal_values']['values'][0][i]
        values.append(root_values(tree['nodes'],policy,leaves))
    own=np.asarray(tree['incoming_class_mass'][0])[coverage.CLASSES]/coverage.COUNTS[coverage.CLASSES]
    own/=own.max()
    own[own<1e-5]=0
    chance=np.asarray(combined['board_weights'])
    pieces,choice,gain=contributions(np.asarray(values),chance,np.asarray(policy[0]),own,combined['root_normalizer'])
    assert gain>=-1e-8 and gain<=evaluation['gaps'][0]+1e-5
    ranks='23456789TJQKA'
    boards=[]
    for i,board in enumerate(combined['boards']):
        hand_pieces=np.bincount(coverage.CLASSES,weights=pieces[i],minlength=169)
        high=max(board[::2],key=ranks.index)
        joint=chance[i]*by_board[board]['root_normalizer']/combined['root_normalizer']
        boards.append(dict(board=board,high_card=high,chance_weight=float(chance[i]),
                           private_conditioned_weight=float(joint),
                           root_gain_contribution_bb=float(pieces[i].sum()),
                           hand_contributions_bb=hand_pieces.tolist()))
    groups=[]
    for rank in reversed(ranks):
        rows=[r for r in boards if r['high_card']==rank]
        if rows:
            groups.append(dict(high_card=rank,boards=len(rows),
                               private_conditioned_weight=sum(r['private_conditioned_weight'] for r in rows),
                               contribution_bb=sum(r['root_gain_contribution_bb'] for r in rows)))
    assert abs(sum(r['contribution_bb'] for r in groups)-gain)<1e-9
    assert abs(sum(r['private_conditioned_weight'] for r in groups)-1)<1e-9
    paths=[tree_path,panel_path,source_path,*worker_paths,__file__,transfer.__file__]
    result=dict(root_only_gain_bb=gain,full_oop_gain_bb=evaluation['gaps'][0],
                iteration=combined['records'][-1]['iteration'],hidden_chance_control=control,
                chosen_action_by_combo=choice.tolist(),high_cards=groups,boards=boards,
                hand_labels=[r['hand'] for r in evaluation['hands']],
                inputs_sha256={str(p):hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths},
                interpretation='Signed contributions to ONE deviation chosen on the COMPLETE panel. No best action is chosen separately by board or high card. Postflop and later preflop actions remain fixed. Descriptive attribution, not a new acceptance gate, independent validation, causal diagnosis, or full-deck estimate.')
    prefix.with_suffix('.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    lines=['# Board contributions to the entering decision deviation','',result['interpretation'],'',
           f'Complete panel root-only gain: {gain:.9f} bb.','',
           'Negative contributions must remain: a decision made before the flop can lose on some future boards. '
           'The tables sum signed contributions; they do not add board-specific best responses.','',
           '| Flop high card | Boards | Private-conditioned weight | Signed contribution (bb) |',
           '|---|---:|---:|---:|']
    for row in groups:
        lines.append(f'| {row["high_card"]} | {row["boards"]} | {row["private_conditioned_weight"]*100:.3f}% | {row["contribution_bb"]:.6f} |')
    lines+=['','## Individual boards, ordered by absolute contribution','',
            '| Board | Private-conditioned weight | Signed contribution (bb) |','|---|---:|---:|']
    for row in sorted(boards,key=lambda r:abs(r['root_gain_contribution_bb']),reverse=True):
        lines.append(f'| {row["board"]} | {row["private_conditioned_weight"]*100:.3f}% | {row["root_gain_contribution_bb"]:.6f} |')
    prefix.with_suffix('.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps(dict(root_only_gain_bb=gain,high_cards=groups,hidden_chance_control=control)))


if __name__=='__main__':
    main()
