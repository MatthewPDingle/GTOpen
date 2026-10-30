"""Guard convergence control; independently replay updates and every exact gap."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from loopback_research_validation import idle
from hu_sampled_convergence_fixture_20260922 import evaluate

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
EVIDENCE=ROOT/'research/preflop-evolution/representative-coverage-20260919'
PREFIX='sampled-convergence-v1'
MASK=(1<<64)-1
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def draws(state):
    while True:
        state=(state+0x9e3779b97f4a7c15)&MASK;z=state
        z=((z^(z>>30))*0xbf58476d1ce4e5b9)&MASK;z=((z^(z>>27))*0x94d049bb133111eb)&MASK
        yield ((z^(z>>31))>>11)/9007199254740992

def policy_from(regret,offsets):
    out=[]
    for lo,hi in zip(offsets,offsets[1:]):
        positive=[max(0.,r) for r in regret[lo:hi]];total=sum(positive)
        out.extend([p/total for p in positive] if total else [1/(hi-lo)]*(hi-lo))
    return out

def step(data,case,policy,seed,iteration):
    delta=[0.]*128;average=[0.]*128
    actor=data['actors'];child=data['children'];arity=data['arity'];infos=data['deal_infos'];offsets=data['offsets']
    utility=data['cases'][case]['utilities'];chance=data['probabilities']
    if seed==0:
        for d,q in enumerate(chance):
            def full(n,reach):
                if not arity[n]:return utility[d][n]
                p=actor[n];o=offsets[infos[d][n]];s=policy[o:o+arity[n]];values=[]
                for a,c in enumerate(child[n][:arity[n]]):
                    r=list(reach);r[p]*=s[a];values.append(full(c,r))
                value=[sum(s[a]*u[p] for a,u in enumerate(values)) for p in range(2)]
                for a,u in enumerate(values):
                    delta[o+a]+=q*reach[1-p]*(u[p]-value[p]);average[o+a]+=q*reach[p]*s[a]
                return value
            full(0,[1.,1.])
    else:
        round_seed=(seed+iteration*0x9e3779b97f4a7c15)&MASK
        for sample in range(512):
            rng=draws(round_seed^((sample*0xd1342543de82ef95)&MASK));x=next(rng);total=0.;d=23
            for candidate,q in enumerate(chance):
                total+=q
                if x<total:d=candidate;break
            updater=sample%2
            def sampled(n):
                if not arity[n]:return utility[d][n][updater]
                o=offsets[infos[d][n]];s=policy[o:o+arity[n]]
                if actor[n]!=updater:
                    x=next(rng);total=0.;chosen=arity[n]-1
                    for a,p in enumerate(s):
                        total+=p
                        if x<total:chosen=a;break
                    for a,p in enumerate(s):average[o+a]+=p
                    return sampled(child[n][chosen])
                values=[sampled(c) for c in child[n][:arity[n]]];value=sum(p*u for p,u in zip(s,values))
                for a,u in enumerate(values):delta[o+a]+=u-value
                return value
            sampled(0)
        delta=[v*(2/512) for v in delta];average=[v*(2/512) for v in average]
    return delta,average

def main():
    reg=OUT/(PREFIX+'-registration.json');result_path=OUT/(PREFIX+'-result.json')
    assert not reg.exists() and not result_path.exists() and idle()
    assert not (EVIDENCE/'running.lock').exists()
    fixture=OUT/(PREFIX+'-fixture.json');data=json.loads(fixture.read_text())
    for p,h in data['inputs'].items():assert sha(ROOT/p)==h,p
    exe=ROOT/'target/release/examples/hu_sampled_convergence_gpu.exe';kernel=OUT/'sampled_convergence_v1.cu'
    paths=[exe,kernel,fixture,Path(__file__),ROOT/'tools/research/hu_sampled_convergence_fixture_20260922.py',
        ROOT/'tools/research/hu_sampled_updates_oracle_20260922.py',ROOT/'crates/solver/examples/hu_sampled_convergence_gpu.rs',
        ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml',ROOT/'tools/research/loopback_research_validation.py',ROOT/'tools/research/paged_continuation_validation.py']
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    record=dict(inputs=frozen,created_at_unix=time.time(),maximum_seconds=300,
        purpose='Independent finite-game convergence control before function approximation; not an easier replacement for the full BB target.',
        variants=['constant-sum, dead money, no rake','action-dependent rake'],sample_seeds=[17,31,47,71],batch_traversals=512,
        full_reference='All 24 chance deals and all actions, same signed-regret matching and frozen update order.',
        stopping={'gap':0.01,'consecutive_checks':2,'checkpoints':[1,10,50,100,250,500,1000,2000,4000,8000,16000],'max_iterations':16000},
        verification={'gap_reconstruction_tolerance':1e-10,'initial_update_replay_tolerance':1e-9,
          'full_reference_first_ten_steps_replayed':True,'group_hidden_states_before_best_response':True},
        no_automatic_retry=True)
    reg.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    env=os.environ.copy();env['GTO_RESEARCH_MAX_SECONDS']='300';env['GTO_RESEARCH_PROTOCOL']=str(reg.relative_to(ROOT))
    cmd=[sys.executable,str(ROOT/'tools/research/loopback_research_validation.py'),str(exe),PREFIX,
         *[str(p.relative_to(ROOT)) for p in [fixture,kernel,result_path]]]
    run=subprocess.run(cmd,cwd=ROOT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
    for suffix in ['.log','-status.json','-resources.json','-freeze.json']:
        p=EVIDENCE/(PREFIX+suffix)
        if p.exists():shutil.copyfile(p,OUT/(PREFIX+suffix))
    assert run.returncode==0,'Keep failure evidence; no automatic restart.'
    guard=json.loads((OUT/(PREFIX+'-status.json')).read_text());assert guard['exit_code']==0 and guard['error'] is None
    result=json.loads(result_path.read_text());assert result['passed'] and len(result['runs'])==10
    max_gap_error=0.;max_update_error=0.;summaries=[]
    for run in result['runs']:
        case=run['case'];seed=run['seed'];regret=[0.]*128;average=[0.]*128;policy=policy_from(regret,data['offsets']);state_at={}
        for t in range(1,11 if seed==0 else 2):
            delta,inc=step(data,case,policy,seed,t);regret=[r+d for r,d in zip(regret,delta)];average=[a+d for a,d in zip(average,inc)]
            policy=policy_from(regret,data['offsets'])
            if t in [1,10]:state_at[t]={'regret':list(regret),'average':list(average),'policy':list(policy)}
        streak=0
        for index,c in enumerate(run['checkpoints']):
            p=c['average_policy']
            for lo,hi in zip(data['offsets'],data['offsets'][1:]):assert abs(sum(p[lo:hi])-1)<1e-12 and min(p[lo:hi])>=0
            exact=evaluate(data,p,case)
            error=max(abs(exact['gap']-c['gap']),*[abs(a-b) for name in ['ev','best_response'] for a,b in zip(exact[name],c[name])])
            max_gap_error=max(max_gap_error,error)
            if c['state_control'] is not None:
                expected=state_at[c['iteration']]
                for field in ['regret','average','policy']:
                    max_update_error=max(max_update_error,max(abs(a-b) for a,b in zip(expected[field],c['state_control'][field])))
            streak=streak+1 if exact['gap']<=.01 else 0
            assert streak==c['target_streak']
            if index<len(run['checkpoints'])-1:assert streak<2
        assert run['target_reached_twice']==(streak>=2)
        if streak<2:assert run['checkpoints'][-1]['iteration']==16000
        summaries.append({'case':case,'seed':seed,'method':run['method'],'target_reached_twice':run['target_reached_twice'],
            'iterations':run['checkpoints'][-1]['iteration'],'gap':run['checkpoints'][-1]['gap'],'seconds':run['seconds']})
    assert max_gap_error<1e-10 and max_update_error<1e-9
    assert all(sha(ROOT/p)==h for p,h in frozen.items())
    review=dict(passed=True,registration_sha256=sha(reg),result_sha256=sha(result_path),inputs_verified=len(frozen),guard=guard,
        maximum_independent_gap_error=max_gap_error,maximum_update_replay_error=max_update_error,runs=summaries,
        all_finite_control_runs_reached_target=all(r['target_reached_twice'] for r in summaries),
        actual_poker_convergence_qualified=False,production_modified=False)
    (OUT/(PREFIX+'-review.json')).write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(review,indent=2))

if __name__=='__main__':main()
