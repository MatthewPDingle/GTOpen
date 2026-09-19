"""Review the completed, hand-qualified fixed-range continuation experiment."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import wizard_continuation_study as s


def report():
    m=s.checked()
    pm=s.read(s.OUT/'precision/manifest.json')
    assert s.read(s.OUT/'precision/status.json')['stage']=='ready_for_review'
    summary=s.read(s.OUT/'precision-summary.json')
    first=s.read(s.OUT/'summary.json')
    assert summary['completed']==80 and all(r['probe_quality_pass'] for r in summary['results'])
    fixtures=s.read(s.OUT/'fixtures.json'); case,=fixtures['cases']
    compatibility=s.read(s.OUT/'card-compatibility-audit.json')
    precision_ids={j['id'] for j in pm['jobs']}
    rows=[]
    for j in m['jobs']:
        refined=j['id'] in precision_ids
        r=s.read(s.OUT/('precision/jobs' if refined else 'jobs')/(j['id']+'.json'))
        s.validate(r,j,pm if refined else m)
        rows.append(r)
    # Overall range-level rake: board probability includes compatible pair mass.
    rake={}
    for menu in ('half','large'):
        rr=[r for r in rows if r['job']['menu']==menu]
        weights=np.array([r['job']['iso_weight']/r['job']['inclusion_probability']*r['pair_mass'] for r in rr])
        rake[menu]=float(np.average([r['expected_rake_bb'] for r in rr],weights=weights))
    diagnostics=dict(parent_manifest_id=m['id'],precision_manifest_id=pm['id'],
        expected_rake_bb=rake,balanced_starting_pot_rake_bb=case['pot']*.04,
        precision_shifts=[dict(menu=r['menu'],hand=r['hand'],
            direct_change_bb=r['postflop_bb']-next(a['postflop_bb'] for a in first['results'] if (a['menu'],a['hand'])==(r['menu'],r['hand'])),
            control_change_bb=r['equity_control_bb']-next(a['equity_control_bb'] for a in first['results'] if (a['menu'],a['hand'])==(r['menu'],r['hand'])))
            for r in summary['results']],
        source_hashes={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in
            [Path(__file__),s.ROOT/'tools/research/wizard_continuation_study.py',s.OUT/'precision-summary.json',s.OUT/'card-compatibility-audit.json']})
    s.write(s.OUT/'report-provenance.json',diagnostics)
    hands=fixtures['probes']; colors={'half':'#3587b4','large':'#bc6133'}
    fig,axes=plt.subplots(1,2,figsize=(12,5),sharey=True)
    for ax,controlled in zip(axes,(False,True)):
        for menu,offset in [('half',-.13),('large',.13)]:
            rr=[next(r for r in summary['results'] if r['menu']==menu and r['hand']==h) for h in hands]
            values=np.array([r['equity_control_bb' if controlled else 'postflop_bb']-r['balanced_bb'] for r in rr])
            cis=np.array([r['equity_control_ci95_bb' if controlled else 'ci95_bb'] for r in rr])
            cis-=np.array([r['balanced_bb'] for r in rr])[:,None]
            # Plot endpoints explicitly; percentile intervals need not enclose point estimates.
            y=np.arange(len(hands))+offset
            ax.hlines(y,cis[:,0],cis[:,1],color=colors[menu],lw=2)
            ax.scatter(values,y,color=colors[menu],label=('50%' if menu=='half' else '75%')+' pot menu',s=25)
        ax.axvline(0,color='#555',lw=1);ax.grid(axis='x',alpha=.2)
        ax.set_yticks(range(len(hands)),hands);ax.set_xlabel('Explicit postflop minus fast value (bb)')
        ax.set_title('Equity control (secondary)' if controlled else 'Direct board estimate (primary)')
    axes[0].invert_yaxis();axes[0].legend(loc='best',fontsize=8)
    fig.suptitle('Fixed UTG call range versus LJ 3-bet range: 40 flops, 95% bootstrap intervals')
    fig.text(.5,.01,'Restricted betting trees; fixed perturbed ranges. Intervals omit model uncertainty. Equity control uses a sampled cache.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.04,1,.95]);fig.savefig(s.OUT/'continuation-values.png',dpi=160);plt.close(fig)
    lines=['# Fixed-range continuation results','',
        'This experiment tests the postflop value estimate for one saved branch. It does not produce new preflop ranges, certify agreement with Wizard, or test a full postflop betting tree. Production is unchanged.','',
        f"All 80 references pass the global target; {len(precision_ids)} were rerun with the stricter per-hand check. Every sampled probe has an OOP best-response gain at most 0.05bb. That is a convergence diagnostic, not a rigorous bound on value error.",'',
        'Values below are gross continuation values before subtracting the additional 12bb preflop call. Positive differences mean the explicit postflop solve values the hand more highly than the fast approximation.','',
        '| Hand | Fast value | 50% menu value [95% interval] | 75% menu value [95% interval] |',
        '|---|---:|---:|---:|']
    for hand in hands:
        a,b=[next(r for r in summary['results'] if r['menu']==menu and r['hand']==hand) for menu in ('half','large')]
        def cell(r):return f"{r['postflop_bb']:.2f} [{r['ci95_bb'][0]:.2f}, {r['ci95_bb'][1]:.2f}]"
        lines.append(f"| {hand} | {a['balanced_bb']:.2f} | {cell(a)} | {cell(b)} |")
    lines += ['', '![Continuation value comparison](continuation-values.png)','',
        f"The stricter hand checks changed the direct estimates by up to {max(abs(r['direct_change_bb']) for r in diagnostics['precision_shifts']):.3f}bb and the equity-control estimates by up to {max(abs(r['control_change_bb']) for r in diagnostics['precision_shifts']):.3f}bb. These shifts measure numerical sensitivity within the same tree; they do not measure abstraction error.",'',
        '## Interpretation limits','',
        f"The fast model removes {case['pot']*.04:.2f}bb rake from the starting pot. The explicit trees collect an estimated {rake['half']:.2f}bb (50% menu) / {rake['large']:.2f}bb (75% menu) across the range, including later betting. Rake treatment therefore contributes to the comparison; this experiment does not isolate its hand-specific effect.",'',
        f"A separate static audit adds two-player physical-card compatibility to the unchanged fast formula. It shifts these eight probe values by at most {max(abs(r['change_bb']) for r in compatibility['results']):.3f}bb, much less than AA's observed discrepancy. This does not account for cards held by folded players; see `card-compatibility-audit.json`.",'',
        'The direct estimator is primary. The secondary equity control reduces board noise using a preflop equity cache whose mean is itself sampled. Its narrower intervals do not include cache error. Both use the same paired, stratified board resamples. Only eight flops per texture stratum were sampled; neither interval captures betting abstraction, range estimation, or folded-card-removal uncertainty.','',
        'The inputs preserve the saved ranges apart from documented tiny trimming and injected probe weights. A hand given negligible weight can have an unstable counterfactual value even when the overall solution is settled. Passing the hand check improves numerical confidence; it does not validate extrapolation to a substantially different range.','',
        'The AA 4-bet-versus-jam discrepancy is outside this call-branch test. Testing it requires its own continuation ranges and opponent responses.','',
        'See `PROTOCOL.md`, `precision/PROTOCOL.md`, both manifests, raw job records, and `report-provenance.json` for reproducibility.','']
    (s.OUT/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')


if __name__=='__main__':report()
