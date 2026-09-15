"""Offline, hand-level continuation pilot. No connection to the live app.

prepare/run/fit/report. Frozen synthetic training fixtures; the saved SB=0.5
game is external evaluation only. Requires numpy and the existing audit runner.
"""
from pathlib import Path
import collections
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/continuation/range-value-pilot-20260915'
AUDIT = ROOT / 'research/preflop-evolution/continuation/balanced-sb05-20260915'
RANKS = '23456789TJQKA'
PARTS = [(max(i//13, i%13), min(i//13, i%13), i//13 > i%13) for i in range(169)]
LABELS = [RANKS[a]+RANKS[b]+('' if a == b else 's' if s else 'o') for a,b,s in PARTS]
INDEX = {h:i for i,h in enumerate(LABELS)}
COMBOS = np.array([6 if a == b else 4 if s else 12 for a,b,s in PARTS])


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def manifest():
    m = json.loads((OUT/'manifest.json').read_text())
    payload = {k:v for k,v in m.items() if k != 'id'}
    assert hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest() == m['id']
    for path,key in [(ROOT/'cache/preflop_eq169.bin','equity_sha256'),
                     (ROOT/'cache/realization_fit.json','fit_sha256'),
                     (AUDIT/'fixtures.json','audit_fixtures_sha256')]:
        assert sha(path) == m[key], f'Changed input: {path}'
    return m


def matrices():
    """Exact compatible-combo counts and symmetrized cached pairwise equity."""
    pairs = [(a,b) for a in range(52) for b in range(a+1,52)]
    masks = np.array([(1<<a)|(1<<b) for a,b in pairs], dtype=np.uint64)
    classes = []
    for a,b in pairs:
        hi,lo = max(a//4,b//4),min(a//4,b//4)
        classes.append(hi*13+lo if a%4 == b%4 or hi == lo else lo*13+hi)
    classes = np.array(classes)
    counts = np.zeros((169,169))
    left,right = np.where((masks[:,None]&masks[None,:]) == 0)
    np.add.at(counts, (classes[left],classes[right]), 1)
    assert np.array_equal(counts, counts.T)
    assert np.array_equal(counts.sum(axis=1), COMBOS*1225)
    data = (ROOT/'cache/preflop_eq169.bin').read_bytes()
    assert len(data) == 4+169*169*4 and int.from_bytes(data[:4], 'little') == 20000
    eq = np.frombuffer(data[4:], dtype='<f4').reshape(169,169).astype(float)
    eq = (eq+1-eq.T)/2
    np.fill_diagonal(eq, .5)
    return counts,eq


def weights(text):
    """Deliberately explicit classes, avoiding range-parser shorthand ambiguity."""
    w = np.zeros(169)
    for token in text.split(','):
        h,*fraction = token.split(':')
        w[INDEX[h]] = float(fraction[0]) if fraction else 1
    return w.tolist()


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    audit = json.loads((AUDIT/'fixtures.json').read_text())
    excluded = {b['board'] for p in [AUDIT/'manifest.json', AUDIT/'extension/manifest.json']
                for b in json.loads(p.read_text())['boards']}
    groups = collections.defaultdict(list)
    for board,iso in audit['canonical_flops']:
        if board in excluded:
            continue
        cards = [board[i:i+2] for i in range(0,6,2)]
        key = ('paired' if len({c[0] for c in cards}) < 3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))+'suits'
        groups[key].append((board,iso))
    boards = []
    for key,items in sorted(groups.items()):
        items.sort(key=lambda x: hashlib.sha256(('range-value-pilot-v1'+x[0]).encode()).digest())
        for board,iso in items[:4]:
            boards.append(dict(board=board,iso_weight=iso,stratum=key,inclusion_probability=4/len(items)))
    assert len(boards) == 20 and not excluded.intersection(b['board'] for b in boards)
    # These are designed training distributions, not claimed population ranges.
    ranges = {
        'linear': 'AA,KK,QQ,JJ,TT,99,88,77,66:0.5,AKs,AQs,AJs,ATs,A9s:0.5,A5s:0.5,A4s:0.25,KQs,KJs,KTs:0.5,QJs,QTs:0.5,JTs,T9s:0.5,98s:0.25,AKo,AQo,AJo:0.5,KQo:0.5',
        'capped': 'AA:0.05,KK:0.1,QQ:0.3,JJ,TT,99,88,77,66,55,44:0.5,33:0.5,22:0.5,AKs:0.25,AQs,AJs,ATs,A9s,A8s:0.5,A5s,A4s,KQs,KJs,KTs,QJs,QTs,JTs,T9s,98s,87s,76s,65s:0.5,54s:0.5,AKo:0.1,AQo:0.5,AJo:0.25,KQo:0.5',
        'polar': 'AA,KK,QQ,JJ:0.5,TT:0.25,99:0.1,88:0.1,55:0.1,AKs,AQs,AJs:0.5,ATs:0.25,A5s,A4s,A3s:0.5,A2s:0.5,KQs:0.5,KJs:0.25,QJs:0.25,JTs:0.25,T9s:0.5,98s:0.5,87s:0.5,76s:0.25,65s:0.25,54s:0.25,AKo,AQo:0.25',
        'broad': 'AA:0.2,KK:0.3,QQ:0.5,JJ,TT,99,88,77,66,55,44,33,22,AKs,AQs,AJs,ATs,A9s,A8s,A7s,A6s,A5s,A4s,A3s,A2s,KQs,KJs,KTs,K9s,K8s:0.5,QJs,QTs,Q9s:0.5,JTs,J9s:0.5,T9s,T8s:0.5,98s,97s:0.5,87s,86s:0.5,76s,75s:0.5,65s,54s,AKo:0.3,AQo,AJo,ATo:0.5,KQo,KJo:0.5,QJo:0.5',
    }
    families = [('linear_capped','linear','capped'), ('polar_broad','polar','broad'), ('linear_broad','linear','broad')]
    cases = []
    for family,a,b in families:
        for reverse in [False,True]:
            oop,ip = (b,a) if reverse else (a,b)
            for spr in [3,12]:
                cases.append(dict(id=f'{family}-{"reverse" if reverse else "forward"}-spr{spr}',family=family,
                                  pot=20,stack=20*spr,weights=[weights(ranges[oop]),weights(ranges[ip])],
                                  range_oop=ranges[oop],range_ip=ranges[ip],menu='half'))
    jobs = []
    for b in boards:
        for c in cases:
            size = {'bet':[{'PotPct':50}],'raise':[{'PotPct':100}],'donk':[{'PotPct':50}]}
            cfg = dict(board=b['board'],range_oop=c['range_oop'],range_ip=c['range_ip'],tree=dict(
                starting_pot=c['pot'],effective_stack=c['stack'],rake_pct=0,rake_cap=0,
                oop=[size]*3,ip=[size]*3,max_raises=1,add_allin=False,allin_threshold=.85))
            jobs.append(dict(**b,case=c['id'],menu='half',id=c['id']+'-'+b['board'],config=cfg))
    binary = ROOT/'target/balanced-continuation-audit-gpu.exe'
    manifest = dict(schema=1,cases=cases,boards=boards,jobs=jobs,target_gap_pct=.1,max_iterations=1000,
                    binary_sha256=sha(binary),equity_sha256=sha(ROOT/'cache/preflop_eq169.bin'),
                    fit_sha256=sha(ROOT/'cache/realization_fit.json'),audit_fixtures_sha256=sha(AUDIT/'fixtures.json'),
                    protocol=dict(training='12 synthetic cases, three range-pair families, both position orientations, SPR 3 and 12; 20 stratified boards excluding all 40 external audit boards.',
                        target='Per-hand gross EV / pot minus per-hand board equity; compatible pair-mass weighted board average, plus cached preflop equity control variate.',
                        validation='Regularization chosen by leave-one-range-pair-family-out; families share some component ranges, so this is not fully independent. Entire saved-game ranges and all audit boards external only.',
                        inference='Ridge residual with range descriptors and hand features, plus zero-sum centering; no board features, hand-specific free parameters or clamping to pot.',
                        candidates=[.01,.1,1,10,100],
                        gate='External pair-mass weighted hand MAE must improve >=15% over Balanced and raw equity, in each call/3bet branch at the supported 50% menu. 75% is a stress test. No live integration from this pilot alone.',
                        limitations='Zero-rake HU, one raise/street, no extra jam, designed ranges. Board sampling and cached equity are approximate. Per-hand strategy convergence can be weaker than aggregate gap. No preflop equilibrium or GPU speed claim.'))
    manifest['id'] = hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    path = OUT/'manifest.json'
    if path.exists():
        assert json.loads(path.read_text()) == manifest, 'Frozen manifest differs'
    else:
        dump(path,manifest)
    print('Frozen',len(jobs),'jobs:',manifest['id'])


def run():
    m = manifest()
    binary = ROOT/'target/balanced-continuation-audit-gpu.exe'
    assert sha(binary) == m['binary_sha256']
    assert sha(ROOT/'cache/preflop_eq169.bin') == m['equity_sha256']
    env = dict(os.environ)
    env['PATH'] = str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    subprocess.run([str(binary),'run',str(OUT/'manifest.json'),*sys.argv[2:]],cwd=ROOT,env=env,check=True)


def context(case, counts, eq):
    w = np.array(case['weights'])
    joint = counts*w[0,:,None]*w[1,None,:]
    z = joint.sum()
    mass = np.array([joint.sum(axis=1),joint.sum(axis=0)])/z
    raw = [];balanced = [];features = []
    base = np.array(json.loads((ROOT/'cache/realization_fit.json').read_text())['class_base'])
    independent = w*COMBOS
    independent /= independent.sum(axis=1,keepdims=True)
    spr = case['stack']/case['pot']
    names = None
    descriptors = np.array([[float(a == b),float(s),(a+b)/24,float(a == 12),float(a-b <= 2 and a != b)] for a,b,s in PARTS])
    summaries = independent@descriptors
    for p in range(2):
        opp = counts*w[1-p,None,:]
        q = (opp*eq).sum(axis=1)/opp.sum(axis=1)
        raw.append(q)
        pos = .92 if p == 0 else 1.08
        a = eq*base[:,None]*pos
        b = (1-eq)*base[None,:]*(2-pos)
        relative = a/np.maximum(a+b,1e-12)
        e_ind = eq@independent[1-p]
        balanced.append(e_ind+min(spr/8,1)*(relative@independent[1-p]-e_ind))
        rows = []
        for h,(hi,lo,suited) in enumerate(PARTS):
            hand = dict(equity=q[h],equity2=q[h]**2,pair=float(hi == lo),suited=float(suited),
                        high=hi/12,low=lo/12,gap=(hi-lo)/12,ace=float(hi == 12),
                        connected=float(0 < hi-lo <= 2),equity_pair=q[h]*float(hi == lo),
                        equity_suited=q[h]*float(suited))
            ctx = dict(ip=float(p),log_spr=np.log1p(spr))
            for side,summary in [('own',summaries[p]),('opp',summaries[1-p])]:
                for label,v in zip(['pairs','suited','ranks','aces','connected'],summary):
                    ctx[side+'_'+label] = v
            row = {'bias':1.,**hand,**ctx}
            for hn in ['equity','pair','suited','low','ace']:
                for cn in ['ip','log_spr','own_pairs','opp_pairs','own_ranks','opp_ranks']:
                    row[hn+'*'+cn] = hand[hn]*ctx[cn]
            if names is None:
                names = list(row)
            assert list(row) == names
            rows.append(list(row.values()))
        features.append(rows)
    return dict(raw=np.array(raw),balanced=np.array(balanced),mass=mass,x=np.array(features),names=names)


def aggregate(case, rows):
    numerator = np.zeros((2,169));mass = np.zeros((2,169));raw = np.zeros((2,169))
    for r in rows:
        assert r['target_met'], 'Unconverged reference'
        j = r['job'];boardw = j['iso_weight']/j['inclusion_probability']
        for p in range(2):
            for h in r['hands'][p]:
                k = INDEX[h['hand']];w = boardw*h['pair_mass']
                mass[p,k] += w
                numerator[p,k] += w*(h['ev_bb']/case['pot']-h['equity'])
                raw[p,k] += w*h['ev_bb']/case['pot']
    return np.divide(numerator,mass,out=np.zeros_like(mass),where=mass>0),mass,np.divide(raw,mass,out=np.zeros_like(mass),where=mass>0)


def load_training(m,counts,eq):
    cases = []
    for c in m['cases']:
        rows = []
        for j in m['jobs']:
            if j['case'] != c['id']:
                continue
            r = json.loads((OUT/'jobs'/f"{j['id']}.json").read_text())
            assert r['job'] == j and r['manifest_id'] == m['id']
            rows.append(r)
        ctx = context(c,counts,eq)
        residual,observed,uncorrected = aggregate(c,rows)
        ctx.update(case=c,residual=residual,observed=observed,uncorrected=uncorrected)
        cases.append(ctx)
    return cases


def fit_ridge(cases,alpha):
    x = np.concatenate([c['x'].reshape(-1,c['x'].shape[-1]) for c in cases])
    y = np.concatenate([c['residual'].ravel() for c in cases])
    w = np.concatenate([(c['mass']*(c['observed']>0)).ravel()/2 for c in cases])
    w /= w.sum()
    mean = (w[:,None]*x).sum(axis=0)
    scale = np.sqrt((w[:,None]*(x-mean)**2).sum(axis=0))
    scale[scale<1e-6] = 1
    mean[0] = 0;scale[0] = 1
    z = (x-mean)/scale
    penalty = np.eye(z.shape[1])*alpha/len(cases)
    penalty[0,0] = 1e-10
    coef = np.linalg.solve(z.T@(w[:,None]*z)+penalty,z.T@(w*y))
    return dict(mean=mean.tolist(),scale=scale.tolist(),coef=coef.tolist(),alpha=alpha)


def predict(c,model):
    correction = ((c['x']-np.array(model['mean']))/np.array(model['scale']))@np.array(model['coef'])
    # Each player's mass sums to one. Remove half of the summed residual means.
    # Raw compatible equity already sums to one in expectation.
    correction -= (correction*c['mass']).sum()/2
    pred = c['raw']+correction
    assert abs((pred*c['mass']).sum()-1) < 1e-9
    return pred


def metrics(c,pred):
    mask = c['observed']>0
    w = c['mass']*mask;w /= w.sum()
    target = c['raw']+c['residual']
    return {name:float((w*np.abs(v-target)).sum()*100) for name,v in
            [('candidate',pred),('balanced',c['balanced']),('raw',c['raw'])]}


def fit():
    m = manifest()
    counts,eq = matrices();cases = load_training(m,counts,eq)
    families = sorted({c['case']['family'] for c in cases})
    scores = []
    for alpha in m['protocol']['candidates']:
        results = []
        for family in families:
            model = fit_ridge([c for c in cases if c['case']['family'] != family],alpha)
            for c in cases:
                if c['case']['family'] == family:
                    results.append(dict(case=c['case']['id'],**metrics(c,predict(c,model))))
        scores.append(dict(alpha=alpha,mae_pct_pot=float(np.mean([r['candidate'] for r in results])),cases=results))
    best = min(scores,key=lambda s:s['mae_pct_pot'])
    model = fit_ridge(cases,best['alpha'])
    model.update(schema=1,feature_names=cases[0]['names'],training_manifest=m['id'],
                 production_enabled=False,support='Research only: zero-rake heads-up, SPR 3-12, 50% bets, one 100% raise/street, no extra jam.')
    dump(OUT/'candidate.json',model)
    dump(OUT/'cross-validation.json',dict(scores=scores,selected_alpha=best['alpha']))
    print('Selected alpha',best['alpha'],'family CV MAE % pot',best['mae_pct_pot'])


def report():
    m = manifest()
    counts,eq = matrices()
    model = json.loads((OUT/'candidate.json').read_text())
    assert model['training_manifest'] == m['id']
    f = json.loads((AUDIT/'fixtures.json').read_text())
    results = [];contexts = []
    for case in f['cases']:
        for menu in ['half','large']:
            rows = []
            for directory in [AUDIT,AUDIT/'extension']:
                audit_manifest = json.loads((directory/'manifest.json').read_text())
                for j in audit_manifest['jobs']:
                    if j['case'] == case['id'] and j['menu'] == menu:
                        r = json.loads((directory/'jobs'/f"{j['id']}.json").read_text())
                        assert r['job'] == j and r['manifest_id'] == audit_manifest['id']
                        rows.append(r)
            c = context(case,counts,eq)
            residual,observed,uncorrected = aggregate(case,rows)
            c.update(residual=residual,observed=observed,uncorrected=uncorrected)
            pred = predict(c,model);target = c['raw']+residual
            row = dict(case=case['id'],menu=menu,boards=len(rows),mae_pct_pot=metrics(c,pred),
                       range_mean_bb=(pred*c['mass']).sum(axis=1).tolist(),probes=[],
                       reference_cv_pot_sum_pct=float((target*c['mass']).sum()*100),
                       spr=case['stack']/case['pot'])
            row['range_mean_bb'] = [v*case['pot'] for v in row['range_mean_bb']]
            for h in f['probes']:
                k = INDEX[h]
                row['probes'].append(dict(hand=h,balanced_bb=c['balanced'][1,k]*case['pot'],
                    candidate_bb=pred[1,k]*case['pot'],reference_cv_bb=target[1,k]*case['pot'],
                    reference_raw_bb=uncorrected[1,k]*case['pot']))
            # Hand-unweighted probe errors complement weighted errors: tiny probes
            # must not disappear from the metric when current preflop folds them.
            ids = [INDEX[h] for h in f['probes']]
            row['probe_mae_bb'] = {name:float(np.abs(v[1,ids]-target[1,ids]).mean()*case['pot'])
                for name,v in [('candidate',pred),('balanced',c['balanced']),('raw',c['raw'])]}
            # Frozen-model uncertainty: resample boards, never individual hands.
            # Reuse the same draws for each model and menu to retain pairing.
            rng = np.random.default_rng(15092026)
            groups = collections.defaultdict(list)
            num = np.zeros((len(rows),2,169));den = np.zeros_like(num)
            for i,r in enumerate(rows):
                j = r['job'];groups[j['stratum']].append(i)
                for p in range(2):
                    for h in r['hands'][p]:
                        k = INDEX[h['hand']]
                        w = j['iso_weight']/j['inclusion_probability']*h['pair_mass']
                        den[i,p,k] = w
                        num[i,p,k] = w*(h['ev_bb']/case['pot']-h['equity'])
            draws = np.zeros((1000,len(rows)))
            for b in range(len(draws)):
                for indices in groups.values():
                    for i in rng.choice(indices,len(indices)):
                        draws[b,i] += 1
            bn = np.einsum('bi,iph->bph',draws,num)
            bd = np.einsum('bi,iph->bph',draws,den)
            bt = c['raw']+np.divide(bn,bd,out=np.zeros_like(bn),where=bd>0)
            bw = c['mass']*(bd>0)
            bw /= bw.sum(axis=(1,2),keepdims=True)
            errors = {name:(bw*np.abs(v-bt)).sum(axis=(1,2))*100 for name,v in
                      [('candidate',pred),('balanced',c['balanced']),('raw',c['raw'])]}
            row['paired_improvement_ci95_pct_pot'] = {name:np.quantile(errors[name]-errors['candidate'],[.025,.975]).tolist()
                                                     for name in ['balanced','raw']}
            results.append(row);contexts.append(c)
    gate = all(r['mae_pct_pot']['candidate'] <= .85*min(r['mae_pct_pot']['balanced'],r['mae_pct_pot']['raw'])
               for r in results if r['menu'] == 'half')
    start = time.perf_counter()
    for _ in range(1000):
        predict(contexts[0],model)
    inference_us = (time.perf_counter()-start)*1e3
    out = dict(external_results=results,promotion_gate_passed=gate,production_enabled=False,
               inference_only_numpy_us=inference_us,
               timing_note='Warm NumPy, one 338-hand value vector with precomputed features; excludes range features, GPU transfer and CFR integration. Not a GPU/preflop speed measurement.')
    dump(OUT/'evaluation.json',out)
    print(json.dumps(out,indent=2))


def plot():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    result = json.loads((OUT/'evaluation.json').read_text())
    references = json.loads((AUDIT/'summary.json').read_text())
    fig,axes = plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for ax,branch,title in zip(axes,['call','threebet'],['After calling the open','After 3-betting and getting called']):
        row = next(r for r in result['external_results'] if r['case'] == branch and r['menu'] == 'half')
        ref = next(r for r in references['results'] if r['case'] == branch and r['menu'] == 'half')
        x = np.arange(len(row['probes']))
        baseline = [r['balanced_bb'] for r in row['probes']]
        candidate = [r['candidate_bb'] for r in row['probes']]
        actual = np.array([r['reference_cv_bb'] for r in row['probes']])
        ci = np.array([r['cv_ci95_bb'] for r in ref['hands']])
        np.testing.assert_allclose(actual,[r['cv_postflop_bb'] for r in ref['hands']],atol=1e-6)
        ax.scatter(x-.2,baseline,label='Balanced',marker='s',color='#888888',s=35)
        ax.scatter(x,candidate,label='Learned pilot',marker='D',color='#bd6735',s=35)
        ax.errorbar(x+.2,actual,yerr=[actual-ci[:,0],ci[:,1]-actual],fmt='o',capsize=3,color='#357ca5',label='Postflop reference')
        ax.set_xticks(x,[r['hand'] for r in row['probes']]);ax.set_title(title)
        ax.set_ylabel('Gross continuation value (bb)');ax.grid(axis='y',alpha=.2)
        ax.legend(fontsize=8)
    fig.suptitle('Independent saved-game check: six probe hands',fontsize=14)
    fig.supxlabel('50% bet menu, 40 held-out flops. Reference bars: conditional 95% board-bootstrap intervals.\nThe learned pilot was fitted on different ranges and boards. These are not full preflop action EVs.',fontsize=9)
    fig.savefig(OUT/'comparison.png',dpi=160);plt.close(fig)


def diagnose():
    """Post-evaluation diagnostics only; never retunes the frozen candidate."""
    m = manifest();counts,eq = matrices()
    training = load_training(m,counts,eq)
    model = json.loads((OUT/'candidate.json').read_text())
    f = json.loads((AUDIT/'fixtures.json').read_text())
    def describe(case):
        d = np.array(case['weights'])*COMBOS
        d /= d.sum(axis=1,keepdims=True)
        return [dict(nonzero_classes=int(np.count_nonzero(x)),effective_classes=float(1/(x*x).sum()),
                     pair_fraction=float(x[[a == b for a,b,_ in PARTS]].sum()),
                     suited_fraction=float(x[[s for _,_,s in PARTS]].sum())) for x in d]
    all_descriptions = [d for c in m['cases'] for d in describe(c)]
    bounds = {k:[min(d[k] for d in all_descriptions),max(d[k] for d in all_descriptions)] for k in all_descriptions[0]}
    external = []
    for case in f['cases']:
        rows = []
        for directory in [AUDIT,AUDIT/'extension']:
            for path in (directory/'jobs').glob('*.json'):
                r = json.loads(path.read_text())
                if r['job']['case'] == case['id'] and r['job']['menu'] == 'half':
                    rows.append(r)
        c = context(case,counts,eq)
        residual,observed,_ = aggregate(case,rows)
        target = c['raw']+residual;pred = predict(c,model)
        worst = []
        for p in range(2):
            for h in range(169):
                if c['mass'][p,h] <= 0 or observed[p,h] <= 0:
                    continue
                score = c['mass'][p,h]*abs(pred[p,h]-target[p,h])/2
                worst.append(dict(player='OOP' if p == 0 else 'IP',hand=LABELS[h],range_mass=float(c['mass'][p,h]),
                                  contribution_pct_pot=float(score*100),candidate_bb=float(pred[p,h]*case['pot']),
                                  reference_bb=float(target[p,h]*case['pot']),balanced_bb=float(c['balanced'][p,h]*case['pot'])))
        external.append(dict(case=case['id'],ranges=describe(case),largest_errors=sorted(worst,key=lambda x:-x['contribution_pct_pot'])[:8]))
    # Identical ranges, disjoint half-board samples. This measures sampling
    # instability, not independent prediction accuracy and not a formal CI.
    splits = []
    groups = collections.defaultdict(list)
    for b in m['boards']:
        groups[b['stratum']].append(b['board'])
    first = {b for bs in groups.values() for b in bs[:2]}
    for c in training:
        case = c['case'];parts = [[],[]]
        for j in m['jobs']:
            if j['case'] == case['id']:
                r = json.loads((OUT/'jobs'/f"{j['id']}.json").read_text())
                parts[0 if j['board'] in first else 1].append(r)
        a,ma,_ = aggregate(case,parts[0]);b,mb,_ = aggregate(case,parts[1])
        w = c['mass']*(ma>0)*(mb>0);w /= w.sum()
        splits.append(dict(case=case['id'],split_difference_pct_pot=float((w*np.abs(a-b)).sum()*100)))
    out = dict(training_range_bounds=bounds,external=external,training_board_split=splits,
               note='Post-hoc explanation only; no candidate weights changed and no new independent test claimed.')
    dump(OUT/'diagnostics.json',out)
    print(json.dumps(out,indent=2))


if __name__ == '__main__':
    {'prepare':prepare,'run':run,'fit':fit,'report':report,'plot':plot,'diagnose':diagnose}[sys.argv[1]]()
