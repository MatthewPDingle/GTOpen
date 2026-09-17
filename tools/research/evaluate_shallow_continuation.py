"""Held-out shallow references and a frozen-policy action regression audit."""
import collections
import copy
import json
import numpy as np
import shallow_continuation_audit as run
import shallow_continuation_fit as fit
import evaluate_holdem_raise_audit as action


def load(case,m):
    rows=[]
    for j in m['jobs']:
        if j['case']==case['id']:
            row=run.read(run.OUT/'jobs'/(j['id']+'.json')); run.old.validate(row,j,m); rows.append(row)
    fixed=0
    if case['partition']=='confirmation':
        oldm=run.old.checked(); fixed_rows=[]
        for j in oldm['jobs']:
            if j['case']=='fourbet-call':
                row=run.read(run.old.OUT/'jobs'/(j['id']+'.json')); run.old.validate(row,j,oldm)
                row=copy.deepcopy(row); row['job']['inclusion_probability']=1.; fixed_rows.append(row)
        fixed=len(fixed_rows); rows=fixed_rows+rows
    return rows,fixed


def bootstrap(case,rows,fixed,seed,reps):
    mass,ev,residual,gain=fit.arrays(case,rows); c=fit.context(case)
    rng=np.random.default_rng(seed); groups=collections.defaultdict(list)
    for i,r in enumerate(rows[fixed:],fixed): groups[r['job']['stratum']].append(i)
    draws=np.zeros((reps,len(rows))); draws[:,:fixed]=1.
    for ids in groups.values():
        selected=rng.choice(ids,(reps,len(ids)))
        for b in range(reps): draws[b]+=np.bincount(selected[b],minlength=len(rows))
    den=(draws@mass.reshape(len(rows),-1)).reshape(reps,2,169)
    assert (den>0).all()
    direct=(draws@ev.reshape(len(rows),-1)).reshape(reps,2,169)/den
    cv=c['raw']+(draws@residual.reshape(len(rows),-1)).reshape(reps,2,169)/den
    return direct,cv


def compare(case,rows,fixed,model,m):
    c=fit.aggregate(case,rows); prediction=fit.predict(c,model)
    values=dict(candidate=prediction,balanced=c['balanced'],raw=c['raw'])
    w=c['mass']*c['qualified']; w/=w.sum()
    scores={name:{key:fit.score(c,pred,key) for key in ['direct','corrected']} for name,pred in values.items()}
    direct,cv=bootstrap(case,rows,fixed,m['bootstrap_seed'],m['bootstrap_replicates'])
    intervals={}
    for key,samples in [('direct',direct),('corrected',cv)]:
        base=(w*abs(samples-values['balanced'])).sum(axis=(1,2))
        trial=(w*abs(samples-prediction)).sum(axis=(1,2))
        intervals[key]=np.quantile(base-trial,[.025,.975]).tolist()
    qualified_mass=float((c['mass']*c['qualified']).sum()/2)
    gate=dict(corrected_improves_10pct=scores['candidate']['corrected']<=.9*scores['balanced']['corrected'],
              direct_regression_within_5pct=scores['candidate']['direct']<=1.05*scores['balanced']['direct'],
              qualified_mass_95pct=qualified_mass>=.95)
    records=[]
    for p in range(2):
        for k,h in enumerate(run.pilot.LABELS):
            records.append(dict(side=['OOP','IP'][p],hand=h,mass=float(c['mass'][p,k]),qualified=bool(c['qualified'][p,k]),
                br_gain_bb=float(c['gain'][p,k]*case['pot']),
                **{name+'_bb':float(pred[p,k]*case['pot']) for name,pred in values.items()},
                direct_bb=float(c['direct'][p,k]*case['pot']),corrected_bb=float(c['corrected'][p,k]*case['pot']),
                direct_95_bb=(case['pot']*np.quantile(direct[:,p,k],[.025,.975])).tolist(),
                corrected_95_bb=(case['pot']*np.quantile(cv[:,p,k],[.025,.975])).tolist()))
    side_scores={}
    for p in range(2):
        sw=c['mass'][p]*c['qualified'][p]; sw/=sw.sum()
        side_scores[['OOP','IP'][p]]={name:float(sw@abs(pred[p]-c['corrected'][p])) for name,pred in values.items()}
    return dict(case=case['id'],boards=len(rows),old_certainty_boards=fixed,qualified_pair_mass=qualified_mass,
                scores_pot_fraction=scores,side_corrected_mae_pot_fraction=side_scores,
                balanced_minus_candidate_mae_95_pot_fraction=intervals,gates=gate,passes=all(gate.values()),
                records=records),c


def action_regression(model):
    m=run.old.checked(); tree=run.read(run.old.OUT/'tree.json'); rows={}
    oldcall=run.prior.checked()
    rows['call']=[run.read(run.prior.OUT/'jobs'/(j['id']+'.json')) for j in oldcall['jobs']]
    for cid in ['threebet-call','fourbet-call']:
        rows[cid]=[run.read(run.old.OUT/'jobs'/(j['id']+'.json')) for j in m['jobs'] if j['case']==cid]
    result=action.evaluate(m,rows,tree)
    before,info,reaches=run.old.tree_values(tree)
    case=m['cases'][2]; c=fit.context(case); gross=case['pot']*fit.predict(c,model)[0]
    # Direct parity of the exact Balanced baseline avoids comparing with the
    # older pilot helper's independent-card approximation.
    assert np.max(abs(c['balanced'][0]*case['pot']-info[case['node']]['gross']))<2e-5
    after,_,_=run.old.tree_values(tree,replacement={case['node']:gross})
    terms,parent,den=action.terminal_coefficients(tree,info)
    conditional=(after-before)[parent['children']]/den
    assert np.max(abs(conditional[[0,1,3]]))<1e-12
    expected=terms[case['node']]['coefficient']*(gross-info[case['node']]['gross'])
    assert np.max(abs(conditional[2]-expected))<1e-10
    records=[]
    for k,r in enumerate(result['records']):
        r=dict(r); r['shallow_candidate_delta_bb']=r['candidate_delta_bb']+float(conditional[2,k])
        r['shallow_decision']=action.classify(r['shallow_candidate_delta_bb'],r['direct_95_interval'],r['corrected_95_interval'],
                                           r['call_frequency'],r['raise_frequency'],r['call_br_gain_bb'],r['raise_br_gain_bb'])
        records.append(r)
    counts,eq=run.pilot.matrices()
    joint=counts*(reaches[parent['id'],1]/run.pilot.COMBOS)[:,None]*(reaches[parent['id'],0]/run.pilot.COMBOS)[None,:]
    mass=joint.sum(axis=1)/joint.sum()
    qualified=np.array([r['decision'] not in ['sparse_action_support','postflop_hand_unsettled'] for r in records])
    w=mass*qualified; w/=w.sum()
    metrics={}
    for name in ['candidate','balanced','shallow_candidate']:
        metrics[name]={key:float(w@np.array([abs(r[name+'_delta_bb']-r[key+'_delta_bb']) for r in records])) for key in ['direct','corrected']}
    return dict(records=records,call_versus_raise_mae_bb=metrics,
                call_versus_fold_max_value_change_bb=float(abs(conditional[1]).max()),
                unchanged_call_audit_sha256=run.pilot.sha(run.prior.OUT/'evaluation.json'),
                old_counts=result['counts'],new_counts=dict(collections.Counter(r['shallow_decision'] for r in records)),
                production_enabled=False)


def evaluate():
    m=run.checked(); model=run.read(run.OUT/'candidate.json')
    assert run.pilot.sha(run.OUT/'candidate.json')==run.read(run.OUT/'candidate-freeze.json')['sha256']
    result=[]; confirmation=None
    for case in m['cases']:
        if case['partition']=='train': continue
        rows,fixed=load(case,m); item,c=compare(case,rows,fixed,model,m); result.append(item)
        if fixed:
            fresh=fit.aggregate(case,rows[fixed:])
            item['fresh_complement_corrected_values_bb']=(fresh['corrected']*case['pot']).tolist()
            item['fresh_complement_direct_values_bb']=(fresh['direct']*case['pot']).tolist()
            confirmation=c
        print(case['id'],item['gates'],item['scores_pot_fraction'],flush=True)
    regression=action_regression(model)
    run.write(run.OUT/'action-regression.json',regression)
    data=dict(manifest_id=m['id'],evaluated_at=run.now(),cases=result,
              passes_all_heldout=all(c['passes'] for c in result),production_enabled=False,
              candidate_sha256=run.pilot.sha(run.OUT/'candidate.json'),
              reference_hashes={j['id']:run.pilot.sha(run.OUT/'jobs'/(j['id']+'.json')) for j in m['jobs']})
    run.write(run.OUT/'evaluation.json',data)
    report(data,regression)


def report(data,regression):
    lines=['# Shallow 4-bet continuation: prospective test','',
           'Research only. Production port 56708 was not modified.','',
           '## Held-out range results','',
           '| Context | Boards | Qualified mass | Balanced MAE (bb) | Candidate MAE (bb) | Screen |',
           '|---|---:|---:|---:|---:|---|']
    for c in data['cases']:
        s=c['scores_pot_fraction']
        lines.append(f"| {c['case']} | {c['boards']} | {c['qualified_pair_mass']:.2%} | {45*s['balanced']['corrected']:.3f} | {45*s['candidate']['corrected']:.3f} | {'pass' if c['passes'] else 'fail'} |")
    lines+=['','Errors use the equity control variate and legal-pair mass, with both players equally weighted. '
            'The confirmation combines 50 old certainty boards with 100 newly sampled complement boards. '
            'The separate synthetic held-out contexts use 30 boards each.','',
            '## Original suspect hands, saved-game shallow leaf','',
            '| Hand | Balanced (bb) | Fresh complement estimate (bb) | Combined estimate (95% interval, bb) | Candidate (bb) |',
            '|---|---:|---:|---:|---:|']
    confirmation=data['cases'][0]
    for hand in ['A3o','A4o','54s','A8o','A3s','A4s','A8s','86o']:
        r=next(r for r in confirmation['records'] if r['side']=='OOP' and r['hand']==hand)
        fresh=confirmation['fresh_complement_corrected_values_bb'][0][run.pilot.INDEX[hand]]
        lo,hi=r['corrected_95_bb']
        lines.append(f"| {hand} | {r['balanced_bb']:.2f} | {fresh:.2f} | {r['corrected_bb']:.2f} [{lo:.2f}, {hi:.2f}] | {r['candidate_bb']:.2f} |")
    lines+=['','These are gross values conditional on reaching the 4-bet pot, not values of the original 3-bet. '
            'The original action comparison weights each leaf by the probability of reaching it.','',
            '## Frozen-policy action regression','',
            '| Model | Call/3-bet direct MAE (bb) | Call/3-bet corrected MAE (bb) |',
            '|---|---:|---:|']
    for name,s in regression['call_versus_raise_mae_bb'].items():
        lines.append(f"| {name} | {s['direct']:.3f} | {s['corrected']:.3f} |")
    lines+=['',f"Call/fold value change: {regression['call_versus_fold_max_value_change_bb']:.3g} bb. "
            'Only the shallow leaf changes; the original call audit and all other leaves remain unchanged.',
            '',f"Overall predeclared held-out screen: **{'PASS' if data['passes_all_heldout'] else 'FAIL'}**.",
            '', 'All results concern one finite, zero-rake heads-up postflop menu. '
            'Bootstrap intervals are per-hand descriptive intervals, not simultaneous guarantees. '
            'Saved-game action labels are reused, so action regression is not an independent new action experiment. '
            'A passing value screen would still require native integration, fresh equilibrium tests, boundary checks and speed measurements. '
            'A failing screen is not eligible for deployment.','']
    (run.OUT/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')


if __name__=='__main__': evaluate()
