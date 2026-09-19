"""Completed-panel report for the registered AA feedback experiment."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import aa_joint_response_study as t


def main():
    m=t.checked();v=t.s.read(t.OUT/'validation.json');assert v['completed']==len(m['jobs'])==400
    d=t.s.read(t.OUT/'summary.json');assert d['completed_cases']==5
    robustness=t.s.read(t.OUT/'response-robustness.json')
    fig,ax=plt.subplots(figsize=(10,6.2),layout='constrained')
    for menu,color,label in [('half','#377bb5','Call: 50% pot menu'),('large','#438a59','Call: 75% pot menu')]:
        rows=sorted((r for r in d['results'] if r['menu']==menu),key=lambda r:r['q'])
        x=np.array([r['q'] for r in rows])*100;y=np.array([r['call_value_bb'] for r in rows])
        lo=np.array([r['call_ci95_bb'][0] for r in rows]);hi=np.array([r['call_ci95_bb'][1] for r in rows])
        ax.errorbar(x+(-.7 if menu=='half' else .7),y,yerr=[y-lo,hi-y],fmt='o-',capsize=4,color=color,label=label)
    rows=sorted((r for r in d['results'] if r['menu']=='half'),key=lambda r:r['q'])
    ax.scatter([r['q']*100 for r in rows],[r['jam_value_bb'] for r in rows],color='#bc4b55',marker='x',s=65,label='Jam: pure LJ best response')
    rr=sorted((r for r in robustness['results'] if r['lj_loss_budget_bb']==.001),key=lambda r:r['q'])
    for i,r in enumerate(rr):
        ax.plot([r['q']*100]*2,[r['minimum']['aa_jam_value_bb'],r['maximum']['aa_jam_value_bb']],color='#bc4b55',lw=6,alpha=.3,
            label='Jam envelope: LJ response loss ≤0.001 bb' if i==0 else None)
    ax.axhline(20.2768532,color='#777777',ls='--',label='Balanced, compatible cards: AA call')
    ax.set(xlabel='AA call frequency at the preflop decision (%)',ylabel='AA value relative to folding (bb)',
        xlim=(-4,104),ylim=(0,130),title='AA feedback study — other preflop hands remain fixed')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.14),ncol=2,fontsize=8)
    ax.text(.02,.98,'Call bars: 95% board-sampling intervals\nJam bands: numerical response sensitivity, not confidence intervals',
        transform=ax.transAxes,va='top',fontsize=8)
    fig.savefig(t.OUT/'aa-feedback.png',dpi=160)
    # Paired board resampling isolates the own-range change from the choice of
    # flops. Same resampling seed/strata as the primary estimates.
    boards=m['boards'];index={b['board']:i for i,b in enumerate(boards)}
    rng=np.random.default_rng(19092026);draws=np.zeros((5000,len(boards)))
    for group in sorted({b['stratum'] for b in boards}):
        inds=[i for i,b in enumerate(boards) if b['stratum']==group]
        for row in draws:np.add.at(row,rng.choice(inds,len(inds)),1)
    samples={};changes=[]
    for case in t.s.read(t.OUT/'fixtures.json')['cases']:
        for menu in ['half','large']:
            mass=np.zeros(len(boards));total=mass.copy()
            for j in m['jobs']:
                if j['case']!=case['id'] or j['menu']!=menu:continue
                r=t.s.read(t.OUT/'jobs'/(j['id']+'.json'))
                h=next(h for h in r['hands'][0] if h['hand']=='AA');i=index[j['board']]
                mass[i]=h['pair_mass']*j['iso_weight']/j['inclusion_probability'];total[i]=mass[i]*h['ev_bb']
            samples[case['q'],menu]=draws@total/(draws@mass)-12
    for row in sorted(d['results'],key=lambda r:(r['menu'],r['q'])):
        base=next(r for r in d['results'] if r['q']==0 and r['menu']==row['menu'])
        delta=samples[row['q'],row['menu']]-samples[0.,row['menu']]
        changes.append(dict(q=row['q'],menu=row['menu'],change_from_rare_aa_bb=row['call_value_bb']-base['call_value_bb'],
            paired_ci95_bb=np.quantile(delta,[.025,.975]).tolist()))
    t.s.write(t.OUT/'paired-changes.json',dict(results=changes,note='Paired board-bootstrap own-range effects; sampling uncertainty only.'))
    other_changes=[]
    for hand in t.s.read(t.OUT/'fixtures.json')['probes']:
        for menu in ['half','large']:
            arrays=[];means=[]
            for name in ['q000','q100']:
                mass=np.zeros(len(boards));total=mass.copy()
                for j in m['jobs']:
                    if j['case']!=name or j['menu']!=menu:continue
                    r=t.s.read(t.OUT/'jobs'/(j['id']+'.json'))
                    h=next((h for h in r['hands'][0] if h['hand']==hand),None)
                    if h is None:continue
                    i=index[j['board']];mass[i]=h['pair_mass']*j['iso_weight']/j['inclusion_probability'];total[i]=mass[i]*h['ev_bb']
                arrays.append(draws@total/(draws@mass));means.append(float(total.sum()/mass.sum()))
            other_changes.append(dict(hand=hand,menu=menu,change_bb=means[1]-means[0],
                paired_ci95_bb=np.quantile(arrays[1]-arrays[0],[.025,.975]).tolist()))
    t.s.write(t.OUT/'other-hand-effects.json',dict(results=other_changes,
        note='Exploratory reuse of the eight qualified OOP probes: always-calling AA minus rare-AA range, all other preflop hand policies fixed. Paired board-sampling intervals only.'))
    lines=['# AA call/jam feedback: completed','',
        'All 400 registered GPU solves passed the configured global and per-hand checks. No production changes.',
        '', 'The experiment moves AA coherently between calls and jams. LJ adapts its all-in response; both players adapt postflop. Other preflop hands and all earlier ranges remain fixed. It is a restricted diagnostic, not a new full-game equilibrium.',
        '', '![AA feedback](aa-feedback.png)', '',
        '| AA calls | Postflop bet menu | AA call value [95% interval] | AA jam vs pure best response |',
        '|---|---|---:|---:|']
    for r in sorted(d['results'],key=lambda r:(r['q'],r['menu'])):
        lo,hi=r['call_ci95_bb'];lines.append(f"| {100*r['q']:.0f}% | {r['menu']} | {r['call_value_bb']:.2f} [{lo:.2f}, {hi:.2f}] | {r['jam_value_bb']:.2f} |")
    lines+=['', 'Values are incremental bb relative to folding at the preflop decision. Call values subtract the additional 12 bb investment. The zero-calling boundary uses a tiny AA probe, not a literal zero-mass postflop query.',
        '', '## Interpretation', '',
        'The Balanced model with corrected card accounting assigns AA a call value of about 20.28 bb regardless of how often AA joins its own calling range. The explicit solves measure the range-dependent response that this fixed approximation misses.',
        '', 'Moving from rare AA calls to always calling lowers AA\'s explicit value by 14.05 bb in the half-pot menu (paired 95% interval: -16.48 to -11.78) and 17.78 bb in the larger menu (-20.07 to -15.44). Meanwhile A5s, KQo, QJs and 55 gain roughly 0.86–1.49 bb; their paired intervals exclude zero in both menus. A stronger calling range changes the opponent\'s play and protects some other hands. These exploratory cross-hand effects are recorded in other-hand-effects.json.',
        '', 'When AA moves out of the jam range, LJ can profitably call more hands. That makes an AA deviation back to jamming more valuable. Therefore the attractive rare-AA call value cannot simply be assigned to AA at every calling frequency.',
        '', 'The starting point is numerically delicate: TT and AKo are almost indifferent against a jam. Exact switching points below one millionth of AA call frequency are not credible real-poker precision. Responses costing LJ only 0.001 bb per reached jam can give AA jam values from 44.43 to 74.27 bb at that boundary. Both call-menu point estimates lie inside this envelope. Board-bootstrap intervals alone therefore do not establish a robust preferred action at the starting point.',
        '', 'At the positive registered call frequencies, the opponent response and the jam value are much less sensitive to that small response-loss budget. Do not interpolate these five points into a precise equilibrium mixing rate: other UTG hands are fixed, the smaller 4-bet is excluded for AA, and intervening response switches are discontinuous.',
        '', '## Consequence', '',
        'A useful replacement must update all relevant preflop ranges and postflop continuations coherently. This experiment rejects the shortcut of inserting the rare-AA postflop value as a fixed calling bonus. It does not show that explicit postflop values alone will reproduce Wizard, nor certify these restricted response frequencies for play.',
        '', 'The next implementation experiment should use a controlled small game with both calling and raising continuations active, a consistent card prior, and continuation values evaluated at each current range state. Validate the backed-up decisions and both players\' responses together before attempting a full-game deployment.',
        '', '## Verification and limits', '',
        f"GPU and full-enumeration CPU global gaps all met 0.05% pot. The maximum independently decoded OOP probe best-response gain was {v['max_decoded_probe_br_gain_bb']:.8f} bb (limit 0.05). Mean reconstruction error was {v['max_mean_reconstruction_error_bb']:.3g} bb. Independent physical-card enumeration reproduced AA flop pair mass within {v['max_aa_pair_mass_relative_error']:.3g} relative error.",
        '', 'The 40 stratified flops and two postflop menus match the earlier diagnostic panel. Bootstrap intervals cover board sampling only. They omit equity-cache error, fixed earlier ranges, folded-card bunching, range trimming, restricted menus and model error. The response envelopes are a separate numerical-sensitivity calculation, not statistical confidence bounds.',
        '', 'See PROTOCOL.md, RESPONSE-ROBUSTNESS.md, manifest.json, fixtures.json, summary.json, paired-changes.json, response-thresholds.json, response-robustness.json, validation.json and jobs/ for the registration and raw evidence.']
    physical=t.s.read(t.OUT/'physical-review.json')
    lines+=['', '## Physical all-in cross-check', '',
        'A separate 32-million-deal check per hand evaluates actual shared boards and holdings for TT and AKo, with the frozen earlier history. It does not use the cached equity table. At the zero-calling boundary:', '',
        '| LJ hand | Two-live-hand call EV [95% MC interval] | Including six earlier folds |',
        '|---|---:|---:|']
    for hand in ['TT','AKo']:
        rr=[next(r for r in physical['results'] if r['hand']==hand and r['q']==0 and r['mode']==mode)
            for mode in ['two_live_hands','including_six_folds']]
        cells=[f"{r['call_ev_bb']:.3f} [{r['ci95_bb'][0]:.3f}, {r['ci95_bb'][1]:.3f}]" for r in rr]
        lines.append(f"| {hand} | {cells[0]} | {cells[1]} |")
    lines+=['', 'TT and AKo both remain consistent with near-indifference in the two-live-hand experiment. Conditioning on the six earlier folds lowers TT\'s call value by about 1.30 bb (paired 95% interval: -1.42 to -1.18 bb); TT then clearly prefers folding in this fixed range state. The corresponding AKo effect is small and its call/fold sign remains unresolved.',
        '', 'Thus the earlier small folded-card effect on AA cannot be generalized to every near-indifferent response. The pure two-player response curve is a controlled diagnostic with a material missing factor, not a prescription for this eight-player history. See PHYSICAL-PROTOCOL.md, physical-freeze.json, physical-batches.json, physical-review.json and physical-range-check.json.']
    (t.OUT/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    files=[t.OUT/f for f in ['README.md','aa-feedback.png','paired-changes.json','summary.json','validation.json','response-robustness.json',
        'physical-review.json','physical-batches.json','physical-range-check.json','response-lp-check.json','other-hand-effects.json']]
    files+=[t.s.ROOT/'tools/research'/f for f in ['aa_joint_response_verify.py','aa_joint_response_report.py']]
    t.s.write(t.OUT/'report-hashes.json',{p.relative_to(t.s.ROOT).as_posix():t.s.sha(p) for p in files})


if __name__=='__main__':main()
