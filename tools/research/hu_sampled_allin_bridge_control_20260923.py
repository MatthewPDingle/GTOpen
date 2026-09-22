"""Versioned conditional-all-in bridge control; old fixtures, no training changes."""
import copy
import json
import math
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from hu_sampled_physical_dense_btn_jam_diagnosis_20260923 import showdown

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-allin-bridge-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
ESTIMATOR = 'conditional-preflop-allin-v1'


def main():
    start = time.monotonic()
    def guard():
        assert idle() and time.monotonic()-start < 900
        assert psutil.virtual_memory().available >= 20_000_000_000
        assert psutil.disk_usage(str(STORE.parent)).free >= 40_000_000_000
    guard()
    parentpath = OUT/'sampled-physical-allin-board-control-v1-result.json'
    parent = json.loads(parentpath.read_text()); assert parent['passed']
    for p,h in parent['artifacts'].items(): assert sha(p)==h,p
    boardstore = Path('S:/GTOpen-research/sampled-physical-allin-board-control-v1')
    boards = json.loads((boardstore/'input.json').read_text())['cases'][:16]
    exact = json.loads((boardstore/'native.json').read_text())[:16]
    fixturepath = Path('S:/GTOpen-research/sampled-physical-gpu-bank-v1/queries.json')
    fixture = json.loads(fixturepath.read_text())
    base = json.loads(fixture['batch_source'])
    contextpath = OUT/'bb-context-candidate.json'
    context = json.loads(contextpath.read_text())
    oldexe = ROOT/'target/release/examples/hu_sampled_batch_bridge_v2.exe'
    newexe = ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe'
    paths = [Path(__file__),parentpath,fixturepath,contextpath,oldexe,newexe,
        boardstore/'input.json',boardstore/'native.json',ROOT/'Cargo.lock',
        ROOT/'tools/research/hu_sampled_physical_dense_btn_jam_diagnosis_20260923.py']
    paths += [ROOT/'crates/solver/examples'/p for p in [
        'hu_sampled_batch_bridge_v2.rs','hu_sampled_allin_bridge_v3.rs',
        'research_sampled/policy_walk_v1.rs','research_sampled/policy_walk_allin_v1.rs',
        'research_sampled/allin_counts_v1.rs','research_sampled/poker_reference_v1.rs',
        'research_sampled/observation_v1.rs','research_sampled/batch_queries_v1.rs',
        'research_sampled/state.rs']]
    reg = dict(inputs={str(p):sha(p) for p in paths},
        private_pair_fixtures=16,replicates=32,action_seed_base=94401,board_order_seed=95501,
        rake_cases=[[.05,2.],[0.,0.],[.05,0.],[.10,8.5]],
        policies=['uniform','unequal legal-action weights','force preflop jam then call'],
        rejected_inputs=['old batch format','wrong private cards','bad count total','duplicate cards',
            'missing label','unknown label field','wrong estimator','old policy format','stale policy batch'],
        tolerance_bb=1e-9,maximum_seconds=900,
        scope='Transport and payout correctness on old fixtures. Compare paired board/action-sampling variances under fixed uniform policies on 16 private pairs and 32 replicates; this is not trained-policy quality, a population variance guarantee, or a new strength evaluation.',
        production_modified=False)
    regpath = OUT/f'{PREFIX}-registration.json'; save(regpath,reg)
    assert not STORE.exists(); STORE.mkdir()
    artifacts = {}; calls = 0; checks = 0; postchecks = 0; rejected = 0
    max_reference = 0.; max_degenerate = 0.; max_forced_jam = 0.
    def invoke(exe,mode,cp,bp,pp,op,fail=False):
        nonlocal calls
        guard(); calls += 1
        done = subprocess.run([str(exe),mode,str(cp),str(bp),str(pp),str(op)],cwd=ROOT,
            capture_output=True,text=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
        if fail:
            assert done.returncode != 0 and not op.exists(),done.stdout
            return
        assert done.returncode==0,done.stderr[-3000:]
        artifacts[str(op)] = sha(op)
        return json.loads(op.read_text())
    def put(p,v):
        save(p,v); artifacts[str(p)] = sha(p); return p
    def counts(deals,degenerate=False):
        result=[]
        for i,d in enumerate(deals):
            r=exact[i]; assert r['private_cards']==d[:4]
            w,t,l=r['wins'],r['ties'],r['losses']
            if degenerate:
                winner=showdown(d);w=1712304 if winner==0 else 0
                t=1712304 if winner==-1 else 0;l=1712304-w-t
            result.append(dict(private_cards=d[:4],wins=w,ties=t,losses=l,boards=1712304))
        return result
    def run_case(name,c,deals,seed,policy_kind,degenerate=False):
        nonlocal checks,postchecks,max_reference,max_degenerate,max_forced_jam
        folder=STORE/name; folder.mkdir()
        cp=put(folder/'context.json',c)
        b=copy.deepcopy(base);b.update(batch_id=name,seed=seed,deals=deals,format=2)
        bp=put(folder/'batch-v2.json',b)
        b3=copy.deepcopy(b);b3.update(format=3,terminal_estimator=ESTIMATOR,allin_counts=counts(deals,degenerate))
        b3p=put(folder/'batch-v3.json',b3)
        q=invoke(newexe,'queries',cp,b3p,'-',folder/'queries-v3.json')
        q2=invoke(oldexe,'queries',cp,bp,'-',folder/'queries-v2.json')
        assert q['observations']==q2['observations'] and q['raw_queries']==q2['raw_queries']
        obs=q['observations'];policies=[]
        for o in obs:
            n=o['n'];p=[0.]*4
            if policy_kind==2 and o['phase']==0:p[n-1]=1.
            else:
                weights=np.arange(1,n+1,dtype=float) if policy_kind==1 else np.ones(n)
                p[:n]=(weights/weights.sum()).tolist()
            policies.append(dict(hi=o['hi'],lo=o['lo'],actor=o['actor'],n=n,probabilities=p))
        doc=dict(format=2,context_source=cp.read_text(),batch_source=bp.read_text(),policies=policies)
        pp=put(folder/'policy-v2.json',doc)
        doc3=dict(doc,format=3,terminal_estimator=ESTIMATOR,batch_source=b3p.read_text())
        pp3=put(folder/'policy-v3.json',doc3)
        old=invoke(oldexe,'verify',cp,bp,pp,folder/'updates-v2.json')
        new=invoke(newexe,'verify',cp,b3p,pp3,folder/'updates-v3.json')
        assert new['verified_cashflow_traversals']==new['verified_query_lookup_traversals']==2*len(deals)
        assert new['maximum_query_lookup_error']==0
        max_reference=max(max_reference,new['maximum_cashflow_error']);checks+=2*len(deals)
        assert len(old['records'])==len(new['records'])
        for a,b in zip(old['records'],new['records']):
            assert a[:3]==b[:3]
            if obs[a[0]]['phase']!=0 or a[2]<0:
                assert a==b;postchecks+=1
            if degenerate:max_degenerate=max(max_degenerate,max(abs(x-y) for x,y in zip(a[3],b[3])))
        if degenerate:
            for a,b in zip(old['roots'],new['roots']):
                assert a[:2]==b[:2];max_degenerate=max(max_degenerate,abs(a[2]-b[2]))
        def roots(u):
            rv=[v for _,actor,v in u['roots'] if actor==0]
            rr=[v for i,actor,tag,v in u['records'] if actor==0 and tag==4 and int(obs[i]['hi'])==1]
            assert len(rv)==len(rr)==len(deals)
            return np.asarray(rr)+np.asarray(rv)[:,None],np.asarray(rr)
        if policy_kind==2:
            values,_=roots(new)
            node=c['nodes'][14];pot=node['pot'];rake=pot*c['rake_fraction']
            if c['rake_cap']>0:rake=min(rake,c['rake_cap'])
            for i,row in enumerate(b3['allin_counts']):
                equity=(row['wins']+.5*row['ties'])/row['boards']
                expected=equity*(pot-rake)-node['invested'][0]
                max_forced_jam=max(max_forced_jam,abs(values[i,3]-expected))
        return roots(old),roots(new),(cp,b3p,pp3,b3,doc3)
    try:
        for j,(rate,cap) in enumerate(reg['rake_cases']):
            c=copy.deepcopy(context);c.update(rake_fraction=rate,rake_cap=cap)
            for kind in range(3):
                run_case(f'payout-{j}-{kind}',c,base['deals'],94400,kind)
            run_case(f'observed-outcome-{j}',c,base['deals'],94400,1,True)
        oldvalues=[];newvalues=[];oldregrets=[];newregrets=[]
        order_rng=np.random.Generator(np.random.PCG64(reg['board_order_seed']))
        for rep in range(reg['replicates']):
            deals=[]
            for case in boards:
                board=order_rng.permutation(case['sampled_boards'][rep]).tolist()
                board[:3]=sorted(board[:3]);deals.append(case['private_cards']+board)
            old,new,last=run_case(f'noise-{rep:02}',context,deals,94401+rep,0)
            oldvalues.append(old[0]);oldregrets.append(old[1]);newvalues.append(new[0]);newregrets.append(new[1])
        cp,bp,pp,b,policy=last
        for i,reason in enumerate(reg['rejected_inputs']):
            bad=copy.deepcopy(b);badpolicy=copy.deepcopy(policy)
            if i==0:bad['format']=2
            elif i==1:bad['allin_counts'][0]['private_cards']=bad['allin_counts'][0]['private_cards'][::-1]
            elif i==2:bad['allin_counts'][0]['wins']+=1
            elif i==3:bad['deals'][0][4]=bad['deals'][0][0]
            elif i==4:bad['allin_counts'].pop()
            elif i==5:bad['allin_counts'][0]['equity']=.5
            elif i==6:bad['terminal_estimator']='sampled'
            elif i==7:badpolicy['format']=2
            else:badpolicy['batch_source']='stale'
            badp=put(STORE/f'bad-{i}-batch.json',bad)
            if i!=8:badpolicy['batch_source']=badp.read_text()
            badpp=put(STORE/f'bad-{i}-policy.json',badpolicy)
            invoke(newexe,'verify',cp,badp,badpp,STORE/f'bad-{i}-output.json',True);rejected+=1
        # A v2 consumer must not silently accept the new meaning.
        invoke(oldexe,'queries',cp,bp,'-',STORE/'legacy-rejection-output.json',True);rejected+=1
        assert max_reference<1e-9 and max_degenerate<1e-9 and max_forced_jam<1e-9
        samples=put(STORE/'samples.json',dict(old_action_values=oldvalues and np.asarray(oldvalues).tolist(),
            new_action_values=np.asarray(newvalues).tolist(),old_regrets=np.asarray(oldregrets).tolist(),
            new_regrets=np.asarray(newregrets).tolist()))
        def variances(xs):return np.asarray(xs).var(axis=0,ddof=1).mean(axis=0).tolist()
        result=dict(passed=True,registration_sha256=sha(regpath),verified_traversals=checks,
            unchanged_postflop_and_opponent_records=postchecks,rejected_inputs=rejected,
            maximum_cashflow_error_bb=max_reference,maximum_observed_outcome_error_bb=max_degenerate,
            maximum_forced_jam_cashflow_error_bb=max_forced_jam,action_order=['fold','call','raise','jam'],
            old_action_variance_bb2=variances(oldvalues),new_action_variance_bb2=variances(newvalues),
            old_advantage_variance_bb2=variances(oldregrets),new_advantage_variance_bb2=variances(newregrets),
            artifacts=artifacts,native_calls=calls,seconds=time.monotonic()-start,
            production_modified=False,accuracy_qualified=False,scope=reg['scope'])
        for p,h in reg['inputs'].items():assert sha(p)==h,p
        guard();save(OUT/f'{PREFIX}-result.json',result)
        print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}))
    except Exception as exc:
        save(OUT/f'{PREFIX}-failure.json',dict(error=str(exc),seconds=time.monotonic()-start));raise


if __name__=='__main__':main()
