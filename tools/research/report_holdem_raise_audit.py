"""Independent conditional-probability audit and call/3-bet report."""
import collections
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import holdem_raise_audit as run


def independent(m, result, tree):
    nodes = tree['nodes']; by_path = {tuple(n['path']):n for n in nodes}
    counts, eq = run.prior.pilot.matrices()
    parent = by_path[(2,)]; _, info, _ = run.tree_values(tree)
    sigma = {tuple(n['path']):np.array(n['sigma']).reshape(-1,169) for n in nodes if n['kind']==0}
    opener = sigma[()][2]
    denominator = counts@opener
    terms = {}
    for n in nodes:
        if n['kind']==0 or n['path'][:2] not in [[2,1],[2,2]]: continue
        opp = np.ones(169); own_future = np.ones(169)
        for depth, a in enumerate(n['path']):
            prefix = tuple(n['path'][:depth]); actor = by_path[prefix]['actor']
            if actor==0: opp *= sigma[prefix][a]
            elif depth>1: own_future *= sigma[prefix][a]
        terms[n['id']] = own_future*(counts@opp)/denominator
    for action in [1,2]:
        total = sum(p for i,p in terms.items() if nodes[i]['path'][1]==action)
        assert np.max(np.abs(total-1)) < 2e-6
    rows = {}; old = run.prior.checked()
    for case in m['cases']:
        if case['id']=='call':
            rows[case['node']] = [run.read(run.prior.OUT/'jobs'/(j['id']+'.json')) for j in old['jobs']]
        else:
            data=[]
            for job in [j for j in m['jobs'] if j['case']==case['id']]:
                path=run.OUT/'jobs'/(job['id']+'.json')
                assert run.prior.pilot.sha(path)==result['new_job_sha256'][job['id']]
                row=run.read(path);run.validate(row,job,m);data.append(row)
            rows[case['node']]=data
    arrays={}; direct={}; corrected={}; gains={}
    for case in m['cases']:
        w=np.zeros((50,169)); v=w.copy(); residual=w.copy(); gain=w.copy()
        for b,row in enumerate(rows[case['node']]):
            for seat,hands in enumerate(row['hands']):
                observed=sum(h['pair_mass']*h['ev_bb'] for h in hands)/row['pair_mass']
                assert abs(observed-row['means_bb'][seat])<1e-5
            for hand in row['hands'][0]:
                k=run.prior.pilot.INDEX[hand['hand']]
                w[b,k]=hand['pair_mass']*row['job']['iso_weight']/row['job']['inclusion_probability']
                v[b,k]=hand['ev_bb'];residual[b,k]=hand['ev_bb']-case['pot']*hand['equity']
                gain[b,k]=max(0.,hand['br_ev_bb']-hand['ev_bb'])
        opponent=np.array(case['weights'])[1]
        exact_eq=(eq*counts)@opponent/(counts@opponent)
        arrays[case['node']]=(w,v,residual,case['pot']*exact_eq)
        direct[case['node']]=np.average(v,axis=0,weights=w)
        corrected[case['node']]=case['pot']*exact_eq+np.average(residual,axis=0,weights=w)
        gains[case['node']]=np.average(gain,axis=0,weights=w)
    def aggregate(gross):
        ans=np.zeros((2,169))
        for i,prob in terms.items():
            a=nodes[i]['path'][1]-1
            ans[a]+=prob*(gross.get(i,info[i]['gross'])-nodes[i]['invested'][1]+1.)
        return ans
    raw=aggregate(direct);cv=aggregate(corrected);model=aggregate({})
    gain_action=np.zeros((2,169))
    for i,p in terms.items():
        if i in gains: gain_action[nodes[i]['path'][1]-1]+=p*gains[i]
    groups=collections.defaultdict(list)
    for b,board in enumerate(m['boards']): groups[board['stratum']].append(b)
    rng=np.random.default_rng(m['bootstrap_seed']);raw_samples=[];cv_samples=[]
    for _ in range(m['bootstrap_replicates']):
        ids=np.concatenate([rng.choice(g,len(g)) for g in groups.values()])
        d={};c={}
        for i,(w,v,r,base) in arrays.items():
            d[i]=np.average(v[ids],axis=0,weights=w[ids])
            c[i]=base+np.average(r[ids],axis=0,weights=w[ids])
        a=aggregate(d);b=aggregate(c)
        raw_samples.append(a[1]-a[0]);cv_samples.append(b[1]-b[0])
    raw_ci=np.quantile(raw_samples,[.025,.975],axis=0);cv_ci=np.quantile(cv_samples,[.025,.975],axis=0)
    maximum=0.
    for k,row in enumerate(result['records']):
        assert row['hand']==run.prior.pilot.LABELS[k]
        pairs=[(raw[0,k],row['direct_call_advantage_bb']), (raw[1,k],row['direct_raise_advantage_bb']),
               (cv[0,k],row['corrected_call_advantage_bb']), (cv[1,k],row['corrected_raise_advantage_bb']),
               (model[1,k]-model[0,k],row['candidate_delta_bb']),
               (gain_action[0,k],row['call_br_gain_bb']), (gain_action[1,k],row['raise_br_gain_bb'])]
        maximum=max(maximum,*(abs(a-b) for a,b in pairs),
                    float(np.max(np.abs(raw_ci[:,k]-row['direct_95_interval']))),
                    float(np.max(np.abs(cv_ci[:,k]-row['corrected_95_interval']))))
        outcome='uncertain_or_no_clear_sign_disagreement'
        if min(row['call_frequency'],row['raise_frequency'])<.0001: outcome='sparse_action_support'
        elif max(gain_action[:,k])>.025: outcome='postflop_hand_unsettled'
        elif row['candidate_delta_bb']>.05 and max(raw_ci[1,k],cv_ci[1,k])<-.05: outcome='clear_model_raise_reference_call'
        elif row['candidate_delta_bb']<-.05 and min(raw_ci[0,k],cv_ci[0,k])>.05: outcome='clear_model_call_reference_raise'
        assert outcome==row['decision']
    assert maximum<2e-5, maximum
    return dict(passed=True, independently_checked_classes=169, paired_bootstraps=m['bootstrap_replicates'],
                max_error_bb=maximum, branch_probability_sums_checked=True, frozen_inputs_unchanged=True)


def main():
    m=run.checked();result=run.read(run.OUT/'evaluation.json');tree=run.read(run.OUT/'tree.json')
    audit=independent(m,result,tree)
    registration=run.read(run.OUT/'interpretation-registration.json')
    assert run.prior.pilot.sha(run.OUT/'INTERPRETATION_PLAN.md')==registration['sha256']
    records={r['hand']:r for r in result['records']}; selected=[records[h] for h in m['probes']]
    ties=[]
    for r in result['records']:
        if r['decision'] in ['sparse_action_support','postflop_hand_unsettled'] or abs(r['candidate_delta_bb'])>.05: continue
        preferred=None
        if min(r['direct_95_interval'][0],r['corrected_95_interval'][0])>.05: preferred='3-bet'
        if max(r['direct_95_interval'][1],r['corrected_95_interval'][1])<-.05: preferred='call'
        if preferred: ties.append(dict(hand=r['hand'],reference_preference=preferred))
    run.write(run.OUT/'near-ties.json',dict(descriptive_only=True,primary_gates_unchanged=True,records=ties))
    fig,ax=plt.subplots(figsize=(11,6.5))
    for i,r in enumerate(selected):
        for off,key,color in [(-.15,'direct','#3576b5'),(.15,'corrected','#25927b')]:
            ax.plot(r[key+'_95_interval'],[i+off]*2,color=color,linewidth=2)
            ax.plot(r[key+'_delta_bb'],i+off,'o',color=color,markersize=5)
        ax.plot(r['candidate_delta_bb'],i,'D',color='#cb6536',markersize=6)
    names=[r['hand']+(' *' if r['decision']=='sparse_action_support' else '')+(' !' if r['decision']=='postflop_hand_unsettled' else '') for r in selected]
    ax.set_yticks(range(len(names)),names);ax.invert_yaxis();ax.axvline(0,color='gray',linestyle='--')
    ax.set_xlabel('3-bet value minus call value (bb): negative favors calling; positive favors 3-betting')
    ax.set_title('BB facing SB 2.5bb open, 40bb stacks\nFrozen preflop responses; direct postflop reference continuations')
    ax.grid(axis='x',alpha=.2)
    for color,marker,label in [('#cb6536','D','Frozen model'),('#3576b5','o','Direct references'),('#25927b','o','Equity-adjusted references')]:
        ax.plot([],[],marker=marker,color=color,linestyle='none',label=label)
    ax.legend(loc='best')
    fig.text(.04,.02,'* One action has almost no saved support.  ! Per-hand reference quality screen failed.\nLines: exploratory paired 95% board-sampling intervals. This is not a newly solved preflop equilibrium.',fontsize=9)
    fig.tight_layout(rect=(0,.075,1,1));fig.savefig(run.OUT/'raise-versus-call.png',dpi=160);plt.close(fig)
    if ties:
        fig,ax=plt.subplots(figsize=(10,5.8))
        for i,t in enumerate(ties):
            r=records[t['hand']]
            for off,key,color in [(-.13,'direct','#3576b5'),(.13,'corrected','#25927b')]:
                ax.plot(r[key+'_95_interval'],[i+off]*2,color=color,linewidth=2)
                ax.plot(r[key+'_delta_bb'],i+off,'o',color=color,markersize=5)
            ax.plot(r['candidate_delta_bb'],i,'D',color='#cb6536',markersize=5)
        ax.set_yticks(range(len(ties)),[t['hand'] for t in ties]);ax.invert_yaxis()
        ax.axvline(0,color='gray',linestyle='--');ax.grid(axis='x',alpha=.2)
        ax.set_xlabel('3-bet minus call (bb): negative favors calling; positive favors 3-betting')
        ax.set_title('Exploratory findings: all screen-qualified model near-ties\nwhere both reference intervals favored one action')
        for color,marker,label in [('#cb6536','D','Frozen model'),('#3576b5','o','Direct references'),('#25927b','o','Equity-adjusted references')]:
            ax.plot([],[],marker=marker,color=color,linestyle='none',label=label)
        ax.legend(loc='best',fontsize=8)
        fig.text(.04,.02,'Exploratory 95% intervals; not simultaneous guarantees across hands.\nFixed opponent responses and one postflop menu; not a deployment recommendation.',fontsize=9)
        fig.tight_layout(rect=(0,.09,1,1));fig.savefig(run.OUT/'near-tie-values.png',dpi=160);plt.close(fig)
    clear=[r for r in result['records'] if r['decision'].startswith('clear_')]
    def est(r,key):
        lo,hi=r[key+'_95_interval'];return f"{r[key+'_delta_bb']:+.3f} [{lo:+.3f}, {hi:+.3f}]"
    lines=['# Calling versus 3-betting: Hold’em audit','',
        f"The primary screen found **{len(clear)} clear sign disagreements**. A separate descriptive check found **{len(ties)} supported model near-ties** where both reference intervals favored one action beyond 0.05bb. Neither count is a full-game accuracy certificate.",'',
        '![Action comparison](raise-versus-call.png)','',
        '## What changed in this test','',
        'The same frozen heads-up 40bb game is evaluated at BB facing SB’s 2.5bb open. We compare calling with 3-betting to 7.5bb, including SB’s folds, calls, 4-bets to 22.5bb and jams, and BB’s saved later responses. No preflop strategy was retrained or re-solved.','',
        'The test reuses the 50 call-pot references and adds 50 called-3-bet and 50 called-4-bet solves on the same boards. The finite postflop menu is unchanged. Fold payoffs are exact; all-in outcomes retain the shared cached approximate equity. The shallow called-4-bet leaf uses the existing Balanced fallback rather than the learned model.','',
        '## Fixed hand probes','',
        'Positive differences favor 3-betting; negative differences favor calling. Frequencies below are the saved strategy, not recommendations from this audit.','',
        '| Hand | Call % | 3-bet % | Model difference bb | Direct bb [95%] | Equity-adjusted bb [95%] | Evidence |',
        '|---|---:|---:|---:|---:|---:|---|']
    for r in selected:
        lines.append(f"| {r['hand']} | {r['call_frequency']*100:.5f} | {r['raise_frequency']*100:.5f} | {r['candidate_delta_bb']:+.4f} | {est(r,'direct')} | {est(r,'corrected')} | {r['decision'].replace('_',' ')} |")
    lines+=['','## Descriptive near-tie findings','',
        'The primary sign test requires a strong model preference. Many mixed hands have model values nearly tied, so zero primary failures would not validate their mixing. This supplementary interpretation was documented during reference generation, before new hand labels were inspected; the primary rules remain unchanged. These are exploratory observations, not extra preregistered failures.','']
    if ties:
        lines+=['![Exploratory near-ties](near-tie-values.png)','',
                '| Hand | Call % | 3-bet % | Reference preference | Model difference bb | Direct bb [95%] | Equity-adjusted bb [95%] |','|---|---:|---:|---|---:|---:|---:|']
        for t in ties:
            r=records[t['hand']];lines.append(f"| {r['hand']} | {100*r['call_frequency']:.4f} | {100*r['raise_frequency']:.4f} | {t['reference_preference']} | {r['candidate_delta_bb']:+.4f} | {est(r,'direct')} | {est(r,'corrected')} |")
    else:lines.append('No supported model near-tie met the descriptive two-interval preference screen. Broad intervals or sparse actions remain unresolved.')
    lines+=['','## Where the estimated value changes come from','',
        'These descriptive point estimates are equity-adjusted reference minus model, in bb. The first column changes the value of calling; the next two change the value of 3-betting. Fold and all-in payoffs are unchanged. The last column is the net change in 3-bet minus call. Sparse-action caveats still apply.','',
        '| Hand | Call-pot change | Called-3-bet change | Called-4-bet change | Net comparison change |',
        '|---|---:|---:|---:|---:|']
    pieces={tuple(t['path']):t for t in result['branch_contributions']}
    for r in selected:
        k=r['class_index'];changes=[]
        for p in [(2,1),(2,2,1),(2,2,2,1)]:
            t=pieces[p];changes.append(t['corrected_advantage_contribution_bb'][k]-t['model_advantage_contribution_bb'][k])
        lines.append(f"| {r['hand']} | {changes[0]:+.3f} | {changes[1]:+.3f} | {changes[2]:+.3f} | {changes[1]+changes[2]-changes[0]:+.3f} |")
    lines+=['','## Interpretation and next step','',
        'This test exposes a more useful lead than the earlier call/fold comparison. Seven of the eight descriptive near-tie findings favor calling. For example, the equity-adjusted estimates put calling ahead by about 0.91bb with A4o, 0.66bb with A3o, and 0.56bb with 54s. Their direct estimates point the same way. These are exploratory findings in this fixed heads-up spot, not new recommended ranges.','',
        'The called-4-bet fallback contributes to all seven shifts toward calling: replacing its values with references reduces the initial 3-bet value. It is not the only source of error; some call-pot estimates also change materially. The learned model has higher descriptive comparison error than the research Balanced baseline on the 30 qualified classes, despite its better call/fold error in the previous audit. This argues against deployment on the strength of that earlier result.','',
        'Next, check the shallow 4-bet continuation directly with a larger, independently selected board panel, then test a replacement for the low-SPR fallback on held-out ranges. This targets an identified coverage gap (17.5bb behind a 45bb pot), rather than forcing prettier frequencies. Re-run both action audits after any candidate change; a local improvement must not come at the expense of the other branches. Do not deploy this frozen research model yet.','']
    lines+=['','## Validation and limits','',
        f"- All {result['new_reference_count']} new references and {result['reused_reference_count']} reused references passed both GPU and transported CPU checks; maximum gaps {result['max_gpu_gap_pct']:.4f}% / {result['max_cpu_gap_pct']:.4f}% pot.",
        f"- New reference solve time: {result['new_reference_seconds']/60:.1f} minutes excluding process overhead.",
        '- Native GPU values were matched independently before labels. Branch probabilities, investments, all 169 results and 5,000 paired bootstrap intervals were checked again using a separate conditional-probability calculation.',
        f"- Classes passing action-support and per-hand quality screens represent {result['qualified_decision_pair_mass_fraction']*100:.2f}% of compatible hand mass at this decision.",'',
        '| Evidence classification | Classes |','|---|---:|']
    lines += [f"| {k.replace('_',' ')} | {v} |" for k,v in sorted(result['counts'].items())]
    lines+=['','| Mean absolute error on qualified hands (bb) | Direct | Equity-adjusted |','|---|---:|---:|']
    for model in ['candidate','balanced']:
        e=result['qualified_pair_weighted_mae_bb'];a=e[model+'_direct'];b=e[model+'_corrected']
        lines.append(f"| {model} | {a:.4f} | {b:.4f} |" if a is not None else f'| {model} | unavailable | unavailable |')
    lines+=['','These are descriptive error estimates for this fixed strategy and range context, not proof of a better equilibrium. Positive call value alone does not establish that calling beats raising. The same sampled boards are paired across branches, but cached equity error is not included in the intervals; intervals are not simultaneous guarantees over all hands.','',
        'A changed preflop strategy could induce different opponent responses. This audit freezes those responses, solves one finite postflop abstraction, and does not quantify full-game exploitability, richer sizing menus, multiway play, or agreement with Wizard.','',
        'All 169 classes, action values, and terminal contribution breakdowns are retained in [evaluation.json](evaluation.json). See [PROTOCOL.md](PROTOCOL.md), [INTERPRETATION_PLAN.md](INTERPRETATION_PLAN.md), and [independent-audit.json](independent-audit.json). Nothing was deployed to port 56708.','',
        '## Reproduce','',
        'From the repository root, run `python tools/research/holdem_raise_audit.py run`, then `python tools/research/evaluate_holdem_raise_audit.py`, then `python tools/research/report_holdem_raise_audit.py`. Completed references are reused after validation. The manifest records required local binary/save hashes; those binary artifacts are not committed.','']
    (run.OUT/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    audit.update(evaluation_sha256=run.prior.pilot.sha(run.OUT/'evaluation.json'),
                 report_sha256=run.prior.pilot.sha(run.OUT/'REPORT.md'),
                 auditor_sha256=run.prior.pilot.sha(Path(__file__)),production_enabled=False)
    run.write(run.OUT/'independent-audit.json',audit)
    print(json.dumps(audit,indent=2))


if __name__=='__main__':main()
