"""Bounded paired-evaluation control; no new trained poker policy."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
import numpy as np
from sampled_evaluation_intervals_v1 import Plan, PairedEvaluation
from hu_sampled_convergence_fixture_20260922 import evaluate
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-evaluation-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
def rejected(f):
    try:f()
    except ValueError:return 1
    raise AssertionError('Invalid evaluation accepted')

def deal_values(data, policy, case, player):
    # Explicit forward terminal enumeration, separate from reverse evaluator.
    def visit(deal,node,reach):
        n=data['arity'][node]
        if not n:return reach*data['cases'][case]['utilities'][deal][node][player]
        offset=data['offsets'][data['deal_infos'][deal][node]]
        return sum(visit(deal,data['children'][node][a],reach*policy[offset+a]) for a in range(n))
    return np.array([visit(d,0,1.) for d in range(24)])

def main():
    assert idle()
    fixture=OUT/'sampled-convergence-v1-fixture.json'
    exe=ROOT/'target/release/examples/hu_sampled_payoff_bounds.exe'
    context=OUT/'bb-context-candidate.json'
    paths=[Path(__file__),fixture,exe,context]+[ROOT/p for p in [
        'tools/research/sampled_evaluation_intervals_v1.py',
        'tools/research/hu_sampled_convergence_fixture_20260922.py',
        'tools/research/hu_sampled_updates_oracle_20260922.py',
        'tools/research/loopback_research_validation.py',
        'crates/solver/examples/hu_sampled_payoff_bounds.rs',
        'crates/solver/examples/research_sampled/state.rs',
        'crates/solver/examples/research_sampled/poker_reference_v1.rs']]
    frozen={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in paths}
    reg=OUT/(PREFIX+'-registration.json');assert not reg.exists()
    save(reg,dict(inputs=frozen,seed=2026092307,policy_seed=172903,looks=[8192,32768],
        series=['case0-player0','case0-player1','case1-player0','case1-player1'],alpha=.05,
        method='Two-sided Maurer-Pontil Theorem 4 plus union bound across registered looks and series.',
        source='https://www.cs.mcgill.ca/~colt2009/papers/012.pdf',
        scope='Finite-game IID deal-evaluation control and full physical public-tree payoff bounds. No learned physical-poker strength claim.',
        confidence_scope='Fixed tested policy difference, conditional on frozen chance law; not a best-response upper bound.',
        maximum_seconds=180,no_gpu=True,production_modified=False))
    started=time.monotonic();bounds_path=OUT/(PREFIX+'-poker-bounds.json')
    run=subprocess.run([str(exe),str(context),str(bounds_path)],cwd=ROOT,capture_output=True,text=True,
                       timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    assert run.returncode==0,run.stderr
    physical=json.loads(bounds_path.read_text());assert physical['public_terminal_templates']>500
    # Synthetic constant data must not be reported with zero uncertainty.
    plan=Plan(-1.,1.,('constant',),(100,))
    constant=PairedEvaluation(plan,'constant')
    for _ in range(100):constant.add_difference(.25)
    constant_ci=constant.interval();assert constant_ci['sample_variance']==0 and constant_ci['radius']>0
    invalid=0
    for x in [math.nan,math.inf,-math.inf,2.]:
        invalid+=rejected(lambda x=x: PairedEvaluation(plan,'constant').add_difference(x))
    invalid+=rejected(lambda:PairedEvaluation(plan,'unknown'))
    invalid+=rejected(lambda:PairedEvaluation(plan,'constant').interval())
    invalid+=rejected(lambda:constant.add_difference(.25))
    invalid+=rejected(lambda:constant.merge(constant))
    invalid+=rejected(lambda:Plan(-1.,1.,('a','a'),(10,)))
    invalid+=rejected(lambda:Plan(-1.,1.,('a',),(10,9)))
    invalid+=rejected(lambda:Plan(-1.,1.,('a',),(10,),0.))
    data=json.loads(fixture.read_text());rng=np.random.default_rng(172903)
    baseline=[];alternative=[]
    for node,_,_ in data['information_keys']:
        n=data['arity'][node];baseline.extend([1/n]*n);alternative.extend(rng.dirichlet(np.ones(n)))
    baseline=np.array(baseline);alternative=np.array(alternative)
    owners=np.repeat([data['actors'][i[0]] for i in data['information_keys']],np.diff(data['offsets']))
    # Freeze policies before any test draws. Each series changes only one player.
    series=tuple(f'case{c}-player{p}' for c in range(2) for p in range(2))
    terminal_values=np.array([data['cases'][c]['utilities'][d][n][p]
        for c in range(2) for d in range(24) for n in range(19) if not data['arity'][n] for p in range(2)])
    width=float(terminal_values.max()-terminal_values.min())
    plan=Plan(-width,width,series,(8192,32768))
    save(OUT/(PREFIX+'-policies.json'),dict(baseline=baseline.tolist(),alternative=alternative.tolist(),
        plan=dict(lower=plan.lower,upper=plan.upper,series=series,looks=plan.looks,alpha=plan.alpha)))
    rng=np.random.default_rng(2026092307);rows=[];errors=[];merge_errors=[];formula_errors=[]
    chance=np.array(data['probabilities']);assert abs(chance.sum()-1)<1e-12
    for case in range(2):
        for player in range(2):
            assert idle() and time.monotonic()-started<180
            policy=np.where(owners==player,alternative,baseline)
            differences=deal_values(data,policy,case,player)-deal_values(data,baseline,case,player)
            exact=float(chance@differences)
            oracle=evaluate(data,policy.tolist(),case)['ev'][player]-evaluate(data,baseline.tolist(),case)['ev'][player]
            errors.append(abs(exact-oracle));assert errors[-1]<1e-12
            draws=rng.choice(24,size=plan.looks[-1],p=chance);values=differences[draws]
            label=f'case{case}-player{player}';acc=PairedEvaluation(plan,label);cis=[]
            for i,value in enumerate(values,1):
                acc.add_difference(float(value))
                if i in plan.looks:
                    ci=acc.interval();var=float(np.var(values[:i],ddof=1))
                    radius=(math.sqrt(2*var*math.log(4*8/.05)/i)+7*2*width*math.log(4*8/.05)/(3*(i-1)))
                    formula_errors.append(max(abs(ci['sample_variance']-var),abs(ci['radius']-radius)))
                    assert formula_errors[-1]<1e-10
                    cis.append(dict(**ci,exact_difference=exact,exact_inside=ci['lower']<=exact<=ci['upper']))
            left=PairedEvaluation(plan,label);right=PairedEvaluation(plan,label)
            for value in values[:10001]:left.add_difference(float(value))
            for value in values[10001:]:right.add_difference(float(value))
            left.merge(right);merge_errors.append(max(abs(left.mean-acc.mean),abs(left.m2-acc.m2)/acc.count))
            assert merge_errors[-1]<1e-10
            # Direct pairwise sample-variance identity, independent of Welford.
            small=values[:97];pairwise=sum((small[i]-small[j])**2 for i in range(97) for j in range(i+1,97))/(97*96)
            assert abs(pairwise-np.var(small,ddof=1))<1e-10
            rows.append(dict(series=label,observations=len(values),intervals=cis))
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    result=dict(passed=True,inputs_verified=len(frozen),rows=rows,invalid_inputs_rejected=invalid,
        exact_profile_difference_error=max(errors),variance_and_formula_error=max(formula_errors),
        merged_batch_error=max(merge_errors),constant_data_interval=constant_ci,
        physical_payoff_bounds=physical,seconds=time.monotonic()-started,
        physical_poker_convergence_qualified=False,
        scope='Math and implementation control. Observed coverage in eight intervals is not empirical proof of 95% coverage.',
        registration_sha256=sha(reg),production_modified=False)
    save(OUT/(PREFIX+'-result.json'),result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['rows','constant_data_interval','physical_payoff_bounds']}))

if __name__=='__main__':main()
