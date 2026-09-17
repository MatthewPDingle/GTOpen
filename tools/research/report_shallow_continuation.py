"""Independent checks and plots for the completed shallow-continuation screen."""
import collections
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shallow_continuation_audit as run
import shallow_continuation_fit as fit
import evaluate_holdem_call_audit as call_audit


def main():
    m=run.checked(); data=run.read(run.OUT/'evaluation.json'); model=run.read(run.OUT/'candidate.json')
    assert data['candidate_sha256']==run.pilot.sha(run.OUT/'candidate.json')
    freeze=run.read(run.OUT/'evaluation-freeze.json')
    for p,h in freeze['inputs'].items(): assert run.pilot.sha(run.ROOT/p)==h,p
    for ident,h in data['reference_hashes'].items(): assert run.pilot.sha(run.OUT/'jobs'/(ident+'.json'))==h,ident
    oldeval=run.read(run.old.OUT/'evaluation.json')
    for ident,h in oldeval['new_job_sha256'].items():
        p=run.old.OUT/'jobs'/(ident+'.json')
        if not p.exists(): p=run.prior.OUT/'jobs'/(ident+'.json')
        assert run.pilot.sha(p)==h,ident
    callm=run.prior.checked(); callrows=[]
    for j in callm['jobs']:
        row=run.read(run.prior.OUT/'jobs'/(j['id']+'.json')); run.prior.validate(row,j,callm); callrows.append(row)
    repeated_call=call_audit.summarize(callm,callrows)
    previous_call=run.read(run.prior.OUT/'evaluation.json')
    for key in ['records','counts','pair_weighted_mae_bb']:
        assert repeated_call[key]==previous_call[key],key
    regression=run.read(run.OUT/'action-regression.json')
    assert regression['call_versus_fold_max_value_change_bb']==0
    repeated_call.update(repeated_at=run.now(), shallow_leaf_does_not_affect_call_action=True,
                         prior_audit_sha256=run.pilot.sha(run.prior.OUT/'evaluation.json'))
    run.write(run.OUT/'call-fold-regression.json',repeated_call)
    # Reconstruct reference means directly from individual rows in scalar loops,
    # avoiding the evaluation's vectorized mass/EV matrices.
    maximum=0.; masses=[]; gaps=[]; seconds=0.
    for case in m['cases']:
        if case['partition']=='train': continue
        rows=[]
        for j in m['jobs']:
            if j['case']==case['id']:
                row=run.read(run.OUT/'jobs'/(j['id']+'.json')); run.old.validate(row,j,m)
                rows.append((row,j['iso_weight']/j['inclusion_probability']))
        if case['partition']=='confirmation':
            oldm=run.old.checked()
            for j in oldm['jobs']:
                if j['case']=='fourbet-call': rows.append((run.read(run.old.OUT/'jobs'/(j['id']+'.json')),j['iso_weight']))
        c=fit.context(case); observed=next(r for r in data['cases'] if r['case']==case['id'])
        lookup={(r['side'],r['hand']):r for r in observed['records']}
        accum=collections.defaultdict(lambda:np.zeros(3))
        for row,factor in rows:
            for side in range(2):
                for hand in row['hands'][side]:
                    weight=factor*hand['pair_mass']
                    accum[(side,hand['hand'])]+=weight*np.array([1.,hand['ev_bb'],hand['ev_bb']-case['pot']*hand['equity']])
        for (side,label),a in accum.items():
            expected=lookup[(['OOP','IP'][side],label)]
            raw=a[1]/a[0]; cv=a[2]/a[0]+case['pot']*c['raw'][side,run.pilot.INDEX[label]]
            maximum=max(maximum,abs(raw-expected['direct_bb']),abs(cv-expected['corrected_bb']))
        prediction=fit.predict(c,model)
        masses.append(abs((c['mass']*prediction).sum()-1))
    assert maximum<1e-10 and max(masses)<1e-10
    for j in m['jobs']:
        row=run.read(run.OUT/'jobs'/(j['id']+'.json')); run.old.validate(row,j,m)
        gaps.extend([row['gap_pct'],row['gpu_gap_pct']]); seconds+=row['seconds']
    audit=dict(checked_at=run.now(),references=len(m['jobs']),reference_seconds=seconds,
               max_cpu_or_gpu_gap_pct=max(gaps),independent_mean_error_bb=maximum,
               max_pot_accounting_error_fraction=max(masses),production_enabled=False)
    run.write(run.OUT/'independent-audit.json',audit)
    plt.rcParams.update({'figure.facecolor':'#171b22','axes.facecolor':'#202632','axes.edgecolor':'#8290a3',
                         'text.color':'#e6edf5','axes.labelcolor':'#e6edf5','xtick.color':'#e6edf5','ytick.color':'#e6edf5',
                         'font.size':11,'savefig.facecolor':'#171b22'})
    fig,axs=plt.subplots(1,2,figsize=(13,4.8),layout='constrained')
    labels=['Original 4-bet spot','Mixed held-out ranges','Premium-heavy held-out ranges']
    x=np.arange(3); width=.25
    for i,(name,color) in enumerate([('balanced','#d98b66'),('raw','#8a96ab'),('candidate','#70bf96')]):
        ys=[45*c['scores_pot_fraction'][name]['corrected'] for c in data['cases']]
        bars=axs[0].bar(x+(i-1)*width,ys,width,label={'balanced':'Old fallback','raw':'Raw equity','candidate':'Test correction'}[name],color=color)
        axs[0].bar_label(bars,fmt='%.2f',padding=3,fontsize=9)
    axs[0].set_xticks(x,labels,fontsize=9); axs[0].set_ylabel('Average value error (bb; lower is better)')
    axs[0].set_title('New range tests · both players'); axs[0].legend(fontsize=9)
    reg=run.read(run.OUT/'action-regression.json'); errors=reg['call_versus_raise_mae_bb']
    names=['balanced','candidate','shallow_candidate']; colors=['#d98b66','#8a96ab','#70bf96']
    bars=axs[1].bar(np.arange(3),[errors[n]['corrected'] for n in names],color=colors)
    axs[1].bar_label(bars,fmt='%.3f',padding=4)
    axs[1].set_xticks(np.arange(3),['Balanced','Previous research model','With test correction'],fontsize=9)
    axs[1].set_ylabel('Call versus 3-bet error (bb; lower is better)')
    axs[1].set_title('Original action audit · same frozen policy')
    for ax in axs:
        ax.spines[['top','right']].set_visible(False); ax.set_ylim(0,ax.get_ylim()[1]*1.16)
    fig.suptitle('Shallow continuation experiment — research only',fontsize=16)
    fig.savefig(run.OUT/'comparison.png',dpi=160); plt.close(fig)
    with (run.OUT/'REPORT.md').open('a',encoding='utf-8',newline='\n') as f:
        f.write('\n## Verification\n\n')
        f.write(f"All {audit['references']} new references passed CPU and GPU gap checks (maximum {max(gaps):.5f}% pot). "
                f"Independent scalar aggregation agreed within {maximum:.2g} bb. "
                f"Offline solver time: {seconds/60:.1f} minutes, excluding process startup.\n\n")
        f.write('![Held-out and action errors](comparison.png)\n\n')
        f.write('Reproduce: run `shallow_continuation_audit.py run`, then `shallow_continuation_fit.py`, '
                '`evaluate_shallow_continuation.py`, and `report_shallow_continuation.py` from `tools/research`. '
                'Training refuses to overwrite a frozen candidate; skip that step when replaying the existing candidate. '
                'Frozen source files, local binaries and saved-game inputs are identified in `manifest.json`.\n')
    print(json.dumps(audit,indent=2),flush=True)


if __name__=='__main__': main()
