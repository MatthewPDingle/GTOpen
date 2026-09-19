"""Interpret completed paired follow-ups without claiming a new equilibrium."""
import wizard_continuation_study as s


def report():
    floor=s.OUT/'floor-sensitivity';four=s.OUT/'fourbet-call'
    assert s.read(floor/'status.json')['stage']=='ready_for_review'
    assert s.read(four/'status.json')['stage']=='ready_for_review'
    fs=s.read(floor/'summary.json'); qs=s.read(four/'summary.json')
    assert qs['completed']==80 and all(r['probe_quality_pass'] for r in qs['results'])
    audit=s.read(s.OUT/'premium-branches.json');root=[1,2,0,0,0,0,0,0]
    decision=next(n for n in audit['nodes'] if n['path']==root)
    reply=next(n for n in audit['nodes'] if n['path']==root+[2])
    call_probability=reply['view']['actions'][1]['freq']
    aa=next(h for h in decision['selected_action_values'] if h['hand']=='AA')['action_ev_bb']
    sensitivity=[]
    for r in qs['results']:
        if r['hand']!='AA':continue
        shift=call_probability*(r['postflop_bb']-r['balanced_bb'])
        ci=[call_probability*(v-r['balanced_bb']) for v in r['ci95_bb']]
        sensitivity.append(dict(menu=r['menu'],saved_fourbet_ev_bb=aa[2],saved_jam_ev_bb=aa[3],
            called_branch_probability=call_probability,continuation_shift_bb=shift,shift_ci95_bb=ci,
            substituted_fourbet_ev_bb=aa[2]+shift,substituted_fourbet_ci95_bb=[aa[2]+v for v in ci]))
    s.write(s.OUT/'followup-analysis.json',dict(aa_fixed_policy_sensitivity=sensitivity,
        source_hashes={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in [floor/'summary.json',four/'summary.json',s.OUT/'premium-branches.json']},
        note='One leaf-value perturbation under frozen opponent responses; not a new preflop solution.'))
    lines=['# Continuation follow-ups','',
        'Both complete 80-board/menu panels passed the specified global and OOP probe convergence checks. These are controlled diagnostics, not deployed models.','',
        '## Range-weight sensitivity','',
        f"Raising the four tiny diagnostic hand weights from 0.001 to 0.01 added {fs['added_mass_fraction']*100:.4f}% to the prepared OOP combination mass. The table gives changes in gross values with paired 95% board-bootstrap intervals.",'',
        '| Hand | 50% menu change (bb) | 75% menu change (bb) |','|---|---:|---:|']
    hands=s.read(s.OUT/'fixtures.json')['probes']
    for hand in hands:
        cells=[]
        for menu in ('half','large'):
            r=next(r for r in fs['results'] if (r['hand'],r['menu'])==(hand,menu));lo,hi=r['paired_change_ci95_bb']
            cells.append(f"{r['change_bb']:+.3f} [{lo:+.3f}, {hi:+.3f}]")
        lines.append(f"| {hand} | {' | '.join(cells)} |")
    lines+=['','## Called four-bet branch','',
        'UTG raises to 45bb and LJ calls. Pot 93.5bb, stacks 155bb. These values use that branch\'s own ranges; they are not imported from the smaller call pot.','',
        '| Hand | Fast gross value | 50% menu gross value [95% interval] | 75% menu gross value [95% interval] |','|---|---:|---:|---:|']
    for hand in hands:
        rr=[next(r for r in qs['results'] if (r['hand'],r['menu'])==(hand,menu)) for menu in ('half','large')]
        cells=[f"{r['postflop_bb']:.2f} [{r['ci95_bb'][0]:.2f}, {r['ci95_bb'][1]:.2f}]" for r in rr]
        lines.append(f"| {hand} | {rr[0]['balanced_bb']:.2f} | {' | '.join(cells)} |")
    lines+=['','## Relevance to AA\'s preflop decision','',
        f"In the saved approximation, AA's 4-bet is worth {aa[2]:.4f}bb and its jam {aa[3]:.4f}bb relative to folding at that decision. LJ calls the 4-bet {call_probability*100:.2f}% of the time. Holding every response fixed, a 1bb change in AA's value in the called branch changes its 4-bet value by about {call_probability:.3f}bb.",'',
        '| Menu | Change in 4-bet value (bb) [95% interval] | Hypothetical 4-bet value (bb) |','|---|---:|---:|']
    for r in sensitivity:
        lo,hi=r['shift_ci95_bb'];lines.append(f"| {r['menu']} | {r['continuation_shift_bb']:+.2f} [{lo:+.2f}, {hi:+.2f}] | {r['substituted_fourbet_ev_bb']:.2f} |")
    lines+=['',
        'This applies only the measured leaf-price difference, including the documented tiny range preparation changes. It is not a re-solve: an actual change to the model would alter opening ranges, 4-betting ranges, and LJ\'s responses. It therefore cannot establish the final strategy or how much closer the complete game would come to Wizard.','',
        'Intervals describe sampled flops within restricted postflop betting trees. They omit range/model uncertainty and finite-sample equity-cache error. The small-floor check does not validate substantial range changes. Future rake and physical card removal also differ from the fast continuation approximation.','']
    (s.OUT/'FOLLOWUPS.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')


if __name__=='__main__':report()
