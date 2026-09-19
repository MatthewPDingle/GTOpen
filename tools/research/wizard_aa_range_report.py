"""Report the completed, paired material-AA range experiment."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import wizard_continuation_study as s


def run():
    out=s.OUT/'aa-range-sensitivity'
    assert s.read(out/'status.json')['stage']=='ready_for_review'
    base,=s.read(s.OUT/'fixtures.json')['cases'];labels=[h['hand'] for h in base['balanced']['hands'][0]]
    aa=labels.index('AA');counts=np.array([6 if len(h)==2 else 4 if h.endswith('s') else 12 for h in labels])
    original_share=base['weights'][0][aa]*6/(np.array(base['weights'][0])@counts)
    rows=[];variants={}
    for name in ('quarter','full'):
        validation=s.read(out/name/'validation.json');assert validation['jobs']==80
        data=s.read(out/name/'summary.json');case,=s.read(out/name/'fixtures.json')['cases'];variants[name]=data
        for a,b in zip(base['balanced']['hands'][0],case['balanced']['hands'][0]):assert abs(a['value_bb']-b['value_bb'])<.0001
        for r in data['results']:
            if r['hand']=='AA':rows.append(dict(variant=name,aa_share=data['aa_combo_mass_fraction'],**r))
    fig,ax=plt.subplots(1,2,figsize=(12,4.6),layout='constrained')
    colors={'half':'#3177b8','large':'#d27832'}
    for menu in ('half','large'):
        selected=[r for r in rows if r['menu']==menu]
        x=[100*original_share]+[100*r['aa_share'] for r in selected]
        y=[0]+[r['change_bb'] for r in selected]
        low=[0]+[r['paired_change_ci95_bb'][0] for r in selected]
        high=[0]+[r['paired_change_ci95_bb'][1] for r in selected]
        ax[0].errorbar(x,y,yerr=[np.array(y)-low,np.array(high)-y],marker='o',capsize=4,label=f'{menu} menu',color=colors[menu])
    ax[0].axhline(0,color='#666',linestyle='--',label='Fast model: no change')
    ax[0].set(xlabel='AA share of OOP calling combinations (%)',ylabel='Change in AA continuation value (bb)',title='Opponent adaptation changes AA value')
    ax[0].legend(fontsize=8);ax[0].grid(alpha=.15)
    hands=['A5s','KQo','QJs','99','88','55','76s'];positions=np.arange(len(hands))
    for k,menu in enumerate(('half','large')):
        rr=[next(r for r in variants['full']['results'] if r['hand']==h and r['menu']==menu) for h in hands]
        y=np.array([r['change_bb'] for r in rr]);lo=np.array([r['paired_change_ci95_bb'][0] for r in rr]);hi=np.array([r['paired_change_ci95_bb'][1] for r in rr])
        ax[1].errorbar(positions+(k-.5)*.18,y,yerr=[y-lo,hi-y],fmt='o',capsize=3,color=colors[menu],label=menu)
    ax[1].axhline(0,color='#666',linestyle='--');ax[1].set(xticks=positions,xticklabels=hands,ylabel='Change in continuation value (bb)',title='Effect on other hands at 6.37% AA')
    ax[1].grid(alpha=.15)
    fig.suptitle('Fixed LJ range; postflop strategies re-solved. Paired 95% board intervals.',fontsize=11)
    fig.savefig(out/'range-interaction.png',dpi=170);plt.close(fig)
    lines=['# Material AA range sensitivity: completed','',
        'All 160 registered solves passed the global and per-probe gates. Independent accounting reproduced range means within 4e-14bb. No solver or production changes.','',
        '**Finding:** AA loses substantial value when it becomes a meaningful part of the calling range and the opponent adapts postflop. The fast Balanced approximation cannot represent this response: its OOP hand values depend on the opponent range but not on the composition of OOP\'s own range.','',
        '| AA combination share | Bet menu | Explicit AA value | Change from original [paired 95% interval] |','|---|---|---:|---:|']
    for r in rows:
        lo,hi=r['paired_change_ci95_bb'];lines.append(f"| {100*r['aa_share']:.2f}% | {r['menu']} | {r['material_aa_range_bb']:.2f}bb | {r['change_bb']:+.2f} [{lo:+.2f}, {hi:+.2f}]bb |")
    lines+=['',
        f"Originally AA is {100*original_share:.4f}% of this prepared range, worth 65.50/67.78bb in the explicit half/large menus. Its fast-model value stays 31.76bb throughout. These are gross postflop continuation values; subtract 12bb to compare with folding at the preceding preflop call decision.", '',
        '![Range composition sensitivity](range-interaction.png)','',
        'At the largest AA inclusion, A5s, KQo and QJs each gain roughly 0.7–1.2bb; their paired intervals exclude zero in both menus. Effects on the other probes are less clear. Strengthening the range changes the opponent\'s play and can protect weaker hands.','',
        'The AA call value after subtracting 12bb falls to about 40.12/39.56bb. That removes the earlier apparent dominance over the separately priced 4-bet, but does not establish a new preferred action: moving AA into calls would also change the 4-bet and jam ranges, and LJ\'s preflop response. Those branches were not jointly re-solved here.','',
        '## Consequence for the research','',
        'A correction based only on the hero hand, its equity and the opponent range cannot capture this effect. A useful continuation model must represent both players\' range composition and be tested on controlled own-range changes, not merely fit isolated absolute values. This experiment gives a concrete development diagnostic for that property. It does not by itself prove a new learned model will generalize.','',
        'Next: assess the same effect when strength moves between competing branches rather than only being injected into one. Use coherent action probabilities and paired continuation values; keep this now-inspected case in development and reserve fresh range contexts/boards for validation. Avoid simply increasing a scalar AA value or tuning to Wizard\'s displayed percentages.','',
        'Limitations: one fixed LJ range and one 200bb raked case; 40 sampled flops; two restricted postflop menus; unchanged preflop responses. AA weights 0.25 and 1.0 are normalized range weights, not literal preceding action frequencies. Intervals reflect board sampling only.','']
    (out/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    print('Completed material range report')


if __name__=='__main__':run()
