"""Offline AA card-removal sensitivity and selected public UI comparisons.

No re-solve or replacement of the saved opponent policies is performed.
"""
import numpy as np
import wizard_continuation_study as s


def run():
    audit=s.read(s.OUT/'premium-branches.json');root=[1,2,0,0,0,0,0,0]
    node=lambda suffix:next(n for n in audit['nodes'] if n['path']==root+suffix)
    case,=s.read(s.OUT/'fourbet-call/fixtures.json')['cases']
    labels=[h['hand'] for h in case['original_balanced']['hands'][0]]
    aa=labels.index('AA')
    pairs=[(a,b) for a in range(52) for b in range(a+1,52)]
    masks=np.array([(1<<a)|(1<<b) for a,b in pairs],dtype=np.uint64)
    cls=np.array([max(a//4,b//4)*13+min(a//4,b//4) if a%4==b%4 or a//4==b//4 else min(a//4,b//4)*13+max(a//4,b//4) for a,b in pairs])
    counts=np.zeros((169,169));a,b=np.where((masks[:,None]&masks[None,:])==0)
    np.add.at(counts,(cls[a],cls[b]),1)
    assert counts.sum()==1326*1225 and counts[aa,aa]==6
    combos=np.bincount(cls,minlength=169)
    eq=np.frombuffer((s.ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
    eq=(eq+1-eq.T)/2;np.fill_diagonal(eq,.5)
    reach=np.array(node([])['view']['reaches_all'][2])
    four=np.array(node([2])['view']['strategy']).reshape(3,169)
    jam=np.array(node([3])['view']['strategy']).reshape(2,169)
    aa_continue=node([2,2])['view']['strategy'][169+aa]
    assert aa_continue>1-1e-6
    gross=case['original_balanced']['hands'][0][aa]['value_bb']
    connected=s.read(s.OUT/'connected-aa-sensitivity.json')['results']
    rows=[]
    for name,weight in [('independent',combos),('compatible',counts[aa])]:
        mass=weight*reach;mass/=mass.sum()
        pj=float(mass@jam[1]);qj=float((mass*jam[1])@eq[aa]/pj)
        pf=four@mass;qf=float((mass*four[2])@eq[aa]/pf[2])
        jam_ev=(1-pj)*27.5+pj*(397.5*qj-194)
        four_fast=pf[0]*27.5+pf[1]*(gross-39)+pf[2]*(397.5*qf-194)
        menus=[]
        for r in connected:
            if r['estimator']!='direct':continue
            # Connected values use the same original reply probability. Invert
            # their isolated called-branch replacement to recover the price.
            saved=next(h['action_ev_bb'][2] for h in node([])['selected_action_values'] if h['hand']=='AA')
            prepared=case['balanced']['hands'][0][aa]['value_bb']
            price=prepared+(r['fourbet_bb']-saved)/node([2])['view']['actions'][1]['freq']
            value=pf[0]*27.5+pf[1]*(price-39)+pf[2]*(397.5*qf-194)
            menus.append(dict(menu=r['menu'],fourbet_bb=float(value),call_bb=r['call_bb'],jam_bb=float(jam_ev)))
        rows.append(dict(weighting=name,jam_bb=float(jam_ev),jam_call_probability=pj,jam_called_equity=qj,
            fourbet_reply_probabilities=pf.tolist(),fivebet_called_equity=qf,fourbet_fast_bb=float(four_fast),explicit_menus=menus))
    expected=next(h['action_ev_bb'] for h in node([])['selected_action_values'] if h['hand']=='AA')
    assert abs(rows[0]['jam_bb']-expected[3])<1e-4
    assert abs(rows[0]['fourbet_fast_bb']-expected[2])<1e-4
    capture=s.read(s.OUT/'wizard-opponent-ui.json')
    comparisons=[]
    for h,values in capture['versus_fourbet45']['hands'].items():
        i=labels.index(h)
        comparisons.append(dict(hand=h,wizard_percent=values,gtopen_percent=dict(zip(('fold','call','jam'),(four[:,i]*100).tolist()))))
    jam_comparisons=[]
    for h,call in capture['versus_jam200']['call_percent'].items():
        jam_comparisons.append(dict(hand=h,wizard_call_percent=call,gtopen_call_percent=float(jam[1,labels.index(h)]*100)))
    out=dict(results=rows,fourbet_hand_comparison=comparisons,jam_hand_comparison=jam_comparisons,
        source_hashes={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in [s.OUT/'premium-branches.json',s.OUT/'fourbet-call/fixtures.json',s.OUT/'connected-aa-sensitivity.json',s.OUT/'wizard-opponent-ui.json',s.ROOT/'cache/preflop_eq169.bin']},
        limitations='Exact two-hand compatibility counts, sampled class equity cache. Folded-player card removal omitted. Policies fixed; prepared continuation ranges documented separately. Wizard hand percentages are rounded visible UI values, not replacement policies. No uncertainty interval for this exploratory accounting change.')
    s.write(s.OUT/'premium-card-audit.json',out)
    lines=['# Premium response and card-removal audit','',
        'Research only. Conditioning the saved LJ policies on holding AA changes opponent response frequencies and showdown equity. It does not re-solve the game or account for cards held by folded seats.','',
        '| AA estimate | Original independent classes | Two-hand compatible cards |',
        '|---|---:|---:|',
        f"| Jam EV | {rows[0]['jam_bb']:.2f} | {rows[1]['jam_bb']:.2f} |",
        f"| 4-bet EV with original fast continuation | {rows[0]['fourbet_fast_bb']:.2f} | {rows[1]['fourbet_fast_bb']:.2f} |",'']
    for r in rows[1]['explicit_menus']:
        lines.append(f"With explicit {r['menu']} continuation: call {r['call_bb']:.2f}bb, 4-bet {r['fourbet_bb']:.2f}bb, jam {r['jam_bb']:.2f}bb. Calling still has the highest point estimate. These are fixed-policy sensitivities, not new equilibrium action values.")
    lines+=['','## Opponent policy differences','',
        'Wizard was inspected at the same 200bb NL25 case. Reserved 100bb cases were not opened. Its unconditioned response to 4-bet 45 is fold 46.5%, call 29.9%, jam 23.7%; GTOpen is 40.9%, 41.1%, 18.0%. Rounded Wizard totals can differ from 100%.','',
        '| Hand vs 4-bet | Wizard call / jam | GTOpen call / jam |','|---|---:|---:|']
    for r in comparisons:
        w,g=r['wizard_percent'],r['gtopen_percent']
        lines.append(f"| {r['hand']} | {w['call']:.1f}% / {w['jam']:.1f}% | {g['call']:.1f}% / {g['jam']:.1f}% |")
    lines+=['','| Hand vs jam | Wizard call | GTOpen call |','|---|---:|---:|']
    for r in jam_comparisons:lines.append(f"| {r['hand']} | {r['wizard_call_percent']:.1f}% | {r['gtopen_call_percent']:.1f}% |")
    lines+=['', 'These policies respond to different entering ranges and continuation models. The comparison locates disagreement; it does not establish that copying a Wizard frequency into GTOpen fixes its value model. The next experiment should test coupled range and policy adaptation rather than add a scalar premium-hand bonus.','']
    (s.OUT/'PREMIUM-RESPONSES.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    print([(r['weighting'],r['jam_bb'],r['fourbet_fast_bb']) for r in rows])


if __name__=='__main__':run()
