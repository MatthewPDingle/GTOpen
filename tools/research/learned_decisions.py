"""Frozen-model export and controlled preflop decision research (no live API writes)."""
import hashlib,json,pathlib,sys,os,subprocess,urllib.request,time
import numpy as np
import continuation_overnight_fit as fit
import continuation_overnight as night
import range_value_pilot as pilot

ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/continuation/learned-decisions-20260916'
def write(p,v):p.write_bytes((json.dumps(v,indent=2,allow_nan=False)+'\n').encode())
def export():
    OUT.mkdir(exist_ok=True)
    model=json.loads((night.OUT/'candidate.json').read_text())
    assert model['encoder']['kind']=='shape' and not model['production_enabled']
    names=model['feature_names']
    expressions={k:k for k in ['equity','pair','suited','high','low','gap','ace','connected','log_spr']}
    expressions.update(bias='1.0',equity2='(equity*equity)',equity_pair='(equity*pair)',equity_suited='(equity*suited)',ip='((double)s)',own_hand_mass='dist[x]',opponent_same_class_mass='dist[(1-s)*169+h]')
    for side,seat in [('own','s'),('opp','(1-s)')]:
        for i,label in enumerate(['pairs','suited','ranks','aces','connected']):expressions[side+'_'+label]=f'desc[{seat}*5+{i}]'
        for i,label in enumerate(['entropy','effective','maximum','top3','high_pairs','low_pairs','offsuit_broadway','suited_connected']):expressions[side+'_'+label]=f'summary[{seat}*8+{i}]'
    def expr(name):
        if name in expressions:return expressions[name]
        return '('+'*'.join(expr(k) for k in name.split('*'))+')'
    coef=np.array(model['coef'])/np.array(model['scale']);bias=-float(coef@np.array(model['mean']))
    expression=format(bias,'.17g')+'\n'+''.join(f'+({v:.17g})*({expr(n)})\n' for n,v in zip(names,coef))
    sha=pilot.sha(night.OUT/'candidate.json')
    source=f'// Frozen candidate SHA256: {sha}\n'+(ROOT/'tools/research/learned_decision_kernel.cu').read_text().replace('__FEATURE_EXPRESSION__',expression)
    (OUT/'candidate.cu').write_bytes(source.encode())
    counts,eq=pilot.matrices();fixtures=json.loads((night.OUT/'fixtures.json').read_text())
    tests=[]
    for c in fixtures['cases']:
        ctx=pilot.context(c,counts,eq);ctx.update(base_x=ctx['x'].copy(),base_names=ctx['names'],case=c)
        pred=fit.predict(ctx,model)
        tests.append(dict(id=c['id'],weights=c['weights'],spr=c['stack']/c['pot'],expected=pred.tolist()))
    write(OUT/'inference-fixtures.json',dict(candidate_sha256=sha,cases=tests))
    print('Exported frozen candidate and',len(tests),'Python parity fixtures.')

def freeze():
    paths=['research/preflop-evolution/continuation/range-value-overnight-20260915-full-query/candidate.json',
           'research/preflop-evolution/continuation/learned-decisions-20260916/candidate.cu',
           'saves/preflop/balanced-sb05-continuation-20260915.gtop','cache/preflop_eq169.bin',
           'cache/realization_fit.json','target/learned-decisions/release/examples/learned_decisions.exe',
           'crates/solver/src/preflop/gpu/learned.rs','crates/solver/examples/learned_decisions.rs']
    manifest=dict(files={p:pilot.sha(ROOT/p) for p in paths},production_enabled=False,
                  protocol='README.md; stop extension if structural accounting or finite-value checks fail')
    p=OUT/'manifest.json'
    if p.exists():assert json.loads(p.read_text())==manifest,'Frozen inputs changed'
    else:write(p,manifest)
    return manifest

def idle():
    for endpoint in ['preflop/status','status']:
        with urllib.request.urlopen('http://localhost:56708/api/'+endpoint,timeout=5) as r:status=json.load(r)
        if status.get('state','').lower() not in ['', 'idle','done','stopped','complete','error']:
            raise RuntimeError('Live app is busy; research has not started: '+str(status.get('state')))

def run():
    freeze();target=int(sys.argv[2]);assert target in [250,500,1000,2000]
    if target>250 and (OUT/'accounting-check.json').exists():
        if json.loads((OUT/'accounting-check.json').read_text())['max_independent_error']>1e-6:
            raise RuntimeError('Structural accounting gate failed; validate a new interface experiment before extending this run')
    env=dict(os.environ);env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    binary=ROOT/'target/learned-decisions/release/examples/learned_decisions.exe'
    for arm in ['balanced','candidate']:
        done=sorted(int(p.stem.split('-')[1]) for p in (OUT/arm).glob('iteration-*.json'))
        current=max(done,default=0)
        if current>=target:continue
        idle();source=OUT/arm/'policy.gtop' if current else ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop'
        command=[str(binary),'solve',str(source),str(OUT/arm),arm,str(target-current),str(OUT/'candidate.cu')]
        if current:command.append('resume')
        print('Starting',arm,current,'to',target,flush=True)
        with (OUT/arm/f'run-{target}.log').open('w') as log:
            proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            for line in proc.stdout:
                log.write(line);log.flush()
                if line.startswith(('iteration','completed')):print(arm,line.strip(),flush=True)
            if proc.wait():raise RuntimeError(f'{arm} failed; see log')
        write(OUT/'progress.json',dict(arm=arm,iteration=target,updated=time.time()))

def accounting():
    counts,eq=pilot.matrices();model=json.loads((night.OUT/'candidate.json').read_text())
    fixtures=json.loads((night.OUT/'fixtures.json').read_text());rows=[]
    for c in fixtures['cases']:
        ctx=pilot.context(c,counts,eq);ctx.update(base_x=ctx['x'].copy(),base_names=ctx['names'],case=c)
        pred=fit.predict(ctx,model);d=fit.distribution(ctx)
        rows.append(dict(id=c['id'],compatible_error_pot=float((ctx['mass']*pred).sum()-1),
                         independent_error_pot=float((d*pred).sum()-1)))
    result=dict(cases=rows,max_compatible_error=max(abs(r['compatible_error_pot']) for r in rows),
                max_independent_error=max(abs(r['independent_error_pot']) for r in rows),
                interpretation='Identical frozen predictions; only aggregation weights change. Independent preflop weighting does not preserve the compatible-mass centering.')
    write(OUT/'accounting-check.json',result);print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))

def evaluate():
    freeze();idle()
    env=dict(os.environ);env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    binary=ROOT/'target/learned-decisions/release/examples/learned_decisions.exe'
    for policy in ['balanced','candidate']:
        for price in ['balanced','candidate']:
            idle();out=OUT/f'{policy}-priced-{price}.json'
            with out.with_suffix('.log').open('w') as log:
                subprocess.run([str(binary),'evaluate',str(OUT/policy/'policy.gtop'),str(out),price,str(OUT/'candidate.cu')],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
            print('Read-only evaluation passed:',policy,'priced with',price,flush=True)

def analyze():
    results={arm:json.loads((OUT/arm/'iteration-250.json').read_text()) for arm in ['balanced','candidate']}
    assert results['balanced']['config']==results['candidate']['config']
    normalized=0;rows=[];checkpoints=[]
    for arm,data in results.items():
        for f in sorted((OUT/arm).glob('iteration-*.json')):
            d=json.loads(f.read_text());checkpoints.append(dict(arm=arm,iteration=d['iteration'],ev_sum_bb=sum(d['evs']),surrogate_gap_bb=sum(d['gaps']),seconds=d['seconds']))
        for row in data['views']:
            v=row['view'];p=np.array(v['strategy']).reshape(len(v['actions']),169)
            assert np.isfinite(p).all() and p.min()>=0 and p.max()<=1.000001
            assert np.max(abs(p.sum(axis=0)-1))<1e-5
            normalized+=169
    for a,b in zip(results['balanced']['views'],results['candidate']['views']):
        assert a['path']==b['path'];v=a['view'];w=b['view'];pa=np.array(v['strategy']).reshape(-1,169);pb=np.array(w['strategy']).reshape(-1,169)
        assert [x['label'] for x in v['actions']]==[x['label'] for x in w['actions']]
        rows.append(dict(path=a['path'],seat=v['actor_pos'],actions=[x['label'] for x in v['actions']],
                         balanced=[x['freq'] for x in v['actions']],candidate=[x['freq'] for x in w['actions']],
                         hand_weighted_tv=float((abs(pa-pb).sum(axis=0)/2*pilot.COMBOS).sum()/1326),
                         mixed_hands_balanced=int(((pa>.01).sum(axis=0)>1).sum()),mixed_hands_candidate=int(((pb>.01).sum(axis=0)>1).sum())))
    comparisons=[]
    for policy in ['balanced','candidate']:
        prices={m:json.loads((OUT/f'{policy}-priced-{m}.json').read_text()) for m in ['balanced','candidate']}
        bypath={m:{tuple(r['path']):r for r in d['rows']} for m,d in prices.items()}
        prefixes={tuple(p['path']):p for p in prices['balanced']['prefixes']}
        for path,prefix in prefixes.items():
            a=bypath['balanced'][path];b=bypath['candidate'][path];assert a['actions']==b['actions']
            mass=prefix['opponent_prefix_mass'];assert mass>0
            f=a['actions'].index('Fold');hands=[]
            for x,y in zip(a['hands'],b['hands']):
                qa=np.array(x['action_values_counterfactual_bb']);qb=np.array(y['action_values_counterfactual_bb'])
                assert np.isfinite(qa).all() and np.isfinite(qb).all()
                assert x['average_probabilities']==y['average_probabilities']
                hands.append(dict(hand=pilot.LABELS[x['class_index']],probabilities=x['average_probabilities'],
                                  balanced_ev_vs_fold=((qa-qa[f])/mass).tolist(),candidate_ev_vs_fold=((qb-qb[f])/mass).tolist()))
            comparisons.append(dict(policy=policy,path=list(path),seat=a['position'],actions=a['actions'],hands=hands))
    result=dict(status='rejected_direct_integration_accounting',iterations=250,normalization_checked_hand_rows=normalized,
                checkpoints=checkpoints,rows=rows,cross_pricing=comparisons,
                limitation='Diagnostic partial solves, not converged ranges or evidence of improved decision accuracy. Cross-pricing freezes a policy and its range-conditioned predictions; it is not an independent poker reference.')
    write(OUT/'comparison.json',result)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,5),gridspec_kw={'width_ratios':[2,1]})
    chosen=[r for r in rows if r['seat'] in ['SB','BB','UTG'] and r['path'] and 1 in r['path']]
    labels=[]
    for i,r in enumerate(chosen):
        idx=r['actions'].index('Call 6');labels.append(('Straddler' if r['seat']=='UTG' else r['seat'])+' vs '+('early open' if r['path'][0]==1 else 'BTN'))
        axes[0].barh(i-.17,r['balanced'][idx]*100,height=.32,color='#5086b8',label='Balanced' if i==0 else '')
        axes[0].barh(i+.17,r['candidate'][idx]*100,height=.32,color='#d48d45',label='Learned candidate' if i==0 else '')
    axes[0].set_yticks(range(len(labels)),labels);axes[0].invert_yaxis();axes[0].set_xlabel('Calling frequency (%)');axes[0].legend();axes[0].set_title('Blind / straddler calls at 250 iterations')
    for arm,color in [('balanced','#5086b8'),('candidate','#d48d45')]:
        c=sorted([c for c in checkpoints if c['arm']==arm],key=lambda x:x['iteration'])
        axes[1].plot([r['iteration'] for r in c],[r['ev_sum_bb'] for r in c],marker='o',color=color,label=arm)
    axes[1].axhline(0,color='black',linewidth=.8);axes[1].set_xlabel('Iterations');axes[1].set_ylabel('Sum of player EVs (bb/hand)');axes[1].set_title('Zero-rake accounting (should be zero)')
    fig.suptitle('Integration screen: learned candidate fails accounting check',fontsize=14)
    fig.text(.5,.01,'Partial solves for diagnosis only. Range changes are not evidence of improved poker accuracy.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.05,1,.94]);fig.savefig(OUT/'comparison.png',dpi=170);plt.close(fig)
    text=['# Learned continuation: first decision screen','',
          '**Result: do not deploy this direct integration.** The GPU port matches the frozen model, but its values do not balance when inserted into the current preflop chance model. The longer decision-quality study is withheld until that interface is corrected.','',
          'The ordinary app on port 56708 was left unchanged. No candidate weights were retrained, clipped, or tuned.','',
          '## What was tested','',
          'Two fresh copies of the saved zero-rake, SB 0.5, eight-player straddle scenario used identical trees and action menus. Both reached 250 iterations. The candidate replaced 6,585 heads-up continuation terminals with SPR 1–20; 36,483 other heads-up terminals retained the original pricing, as did multiway leaves. These counts are tree coverage, not the frequency with which play reaches those leaves.','',
          'Inference was checked against all 32 original Python fixtures. Maximum GPU/Python discrepancy was '+f"{json.loads((OUT/'inference-check.json').read_text())['max_absolute_error']:.3g}"+' of pot. All '+str(normalized)+' inspected hand rows were finite and normalized. Both saved policies were then evaluated under both pricing models without changing their strategy/regret arrays.','',
          '## Why the accounting gate failed','',
          'The learned model conditions on legal two-player card combinations. The current preflop engine combines independent hand-class weights. The same predictions balance to floating-point roundoff with the first weighting, but show up to 4.389% of pot imbalance with the second across the 32 original fixtures. This discrepancy can be reproduced in Python without running the GPU solver.','',
          '| Model | Iterations | Sum of player EVs, bb/hand | Diagnostic gap, bb |','|---|---:|---:|---:|']
    for c in sorted(checkpoints,key=lambda c:(c['iteration'],c['arm'])):
        text.append(f"| {c['arm']} | {c['iteration']} | {c['ev_sum_bb']:.8f} | {c['surrogate_gap_bb']:.5f} |")
    text+=['','At zero rake, the EV sum should be zero. The candidate gap freezes its range-conditioned predictions during the best-response pass: it is not full-game exploitability or a standard CFR convergence guarantee. Reaching a smaller gap would not repair the accounting mismatch.','',
           '## Observed range changes — diagnostic only','',
           '| Decision | Balanced call | Candidate call |','|---|---:|---:|']
    for r in chosen:
        idx=r['actions'].index('Call 6');name=('Straddler (UTG)' if r['seat']=='UTG' else r['seat'])+' facing '+('early open' if r['path'][0]==1 else 'BTN open')
        text.append(f"| {name} | {100*r['balanced'][idx]:.2f}% | {100*r['candidate'][idx]:.2f}% |")
    root=rows[0]
    text+=['',f"The first opener raised {root['balanced'][1]*100:.2f}% with Balanced and {root['candidate'][1]*100:.2f}% with the candidate.",
           '', 'These are partial solves, not converged reference ranges. They do not establish improvement over Wizard or full postflop solving. The original source family was also represented in training, so this is not a new independent generalization test.','',
           '![Diagnostic comparison](comparison.png)','',
           '## Same-policy pricing examples','',
           'The following holds each preflop policy fixed and changes only continuation pricing. Values are bb relative to folding at the selected node, with opponent prefix mass divided out. They diagnose sensitivity to the value model; neither column is an independent truth reference.','',
           '| Policy | Decision | Hand | Action | Balanced value | Candidate value |','|---|---|---|---|---:|---:|']
    for c in comparisons:
        if c['seat']!='BB' or 1 not in c['path']:continue
        for h in c['hands']:
            if h['hand'] not in ['KQo','AQs','TT']:continue
            for i,action in enumerate(c['actions']):
                if action.startswith(('Call','3-bet')):
                    name='vs early open' if c['path'][0]==1 else 'vs BTN'
                    text.append(f"| {c['policy']} | BB {name} | {h['hand']} | {action} | {h['balanced_ev_vs_fold'][i]:.3f} | {h['candidate_ev_vs_fold'][i]:.3f} |")
    text+=['','## Next step','',
           'Build and validate a consistent interface between range-conditioned continuation values and preflop counterfactual probabilities. Require zero-rake accounting and fixed-policy action-value checks before resuming longer learning runs. A common value offset chosen merely to make the totals balance would change the frozen predictions and would need separate validation; it is not silently applied here.',
           '', 'Only after that passes should we test whether changed blind calls and early-position decisions agree better with fresh postflop references. Better average prediction error alone is insufficient, particularly for sparse premium hands and ranges generated by the new policy itself.','',
           '## Reproduction and evidence','',
           '- `manifest.json` freezes the candidate, equity cache, source save, inference kernel and executable hashes. The 250 checkpoints resume the first 50 execution-check iterations; subsequent code changes before freezing only hardened CLI/experiment guards.',
           '- `comparison.json` contains every selected hand/action comparison, mixed-hand counts, normalization checks and checkpoint summaries.',
           '- `accounting-check.json` reproduces the weighting discrepancy on the original 32 fixtures.',
           '- `balanced-priced-*.json` and `candidate-priced-*.json` contain read-only cross-pricing outputs.',
           '- The planned 500/1,000/2,000 iteration extension was withheld at the structural gate. These 250-iteration results must not be marketed as completed convergence or accuracy validation.',
           '- See `validation.json` for completed checks. Experimental `.gtop` policies remain local, excluded from Git, and must not be loaded into the ordinary app.','']
    (OUT/'REVIEW.md').write_bytes('\n'.join(text).encode('utf-8'))
    print('Saved comparison.json and comparison.png;',normalized,'hand rows normalized.')

if __name__=='__main__':{'export':export,'freeze':freeze,'run':run,'accounting':accounting,'evaluate':evaluate,'analyze':analyze}[sys.argv[1]]()
