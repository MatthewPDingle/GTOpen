"""Attribute exact all-in errors to every played generation, against fixed opponents.

Diagnostic only. Does not choose a checkpoint or change the evaluated average.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['OMP_NUM_THREADS'] = '2'
import copy
import json
from pathlib import Path
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from hu_exhaustive_btn_response_v2_20260923 import load_models
from reboot_research_idle_v1 import idle

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'allin-generation-attribution-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
GROUPS = {'initial': [0], 'early': list(range(1,26)), 'middle': list(range(26,52)), 'late': list(range(52,78))}


def read(path):
    return json.loads(Path(path).read_text())


def main():
    began = time.monotonic(); last = 0.
    def guard():
        nonlocal last
        now = time.monotonic(); assert now-began < 600
        if now-last >= 2:
            assert idle() and psutil.virtual_memory().available >= 20_000_000_000
            last = now
    guard(); assert not STORE.exists() and not LOCK.exists() and not OTHER.exists()
    paths = {}
    for label, prefix in [('btn','exhaustive-btn-response-v2'), ('bb','bb-fold-jam-response-v3')]:
        paths[label] = {k:OUT/f'{prefix}-{k}.json' for k in ('registration','result','independent-review','status')}
    docs = {label:{k:read(p) for k,p in pp.items()} for label,pp in paths.items()}
    inputs = {}
    for label,d in docs.items():
        pp = paths[label]
        assert d['status']['state'] == 'complete' and d['status']['error'] is None
        assert d['result']['passed'] and d['independent-review']['passed']
        assert d['result']['registration_sha256'] == d['independent-review']['registration_sha256'] == sha(pp['registration'])
        assert d['independent-review']['result_sha256'] == sha(pp['result'])
        inputs.update(d['registration']['inputs'])
        inputs.update({str(p):sha(p) for p in pp.values()})
    source_path = OUT/'bb-context-candidate.json'; source = source_path.read_text()
    catalog_path = Path(docs['btn']['registration']['catalog']); catalog = read(catalog_path)['native_observations']
    obs = [r['observation'] for r in catalog]
    assert len(obs) == 265 and all(o['own_history'] == [] and o['phase'] == 0 for o in obs)
    source_names = docs['btn']['registration']['candidates']
    assert set(source_names) == {'combined_269','visible_302'}
    for p in [Path(__file__), ROOT/'tools/research/hu_allin_generation_attribution_review_20260923.py',
              source_path, catalog_path, ROOT/'tools/research/hu_exhaustive_btn_response_v2_20260923.py',
              OUT/'ALLIN-GENERATION-ATTRIBUTION-PLAN.md']:
        inputs[str(p)] = sha(p)
    for p,h in inputs.items():
        assert sha(p) == h, p
    rp = OUT/f'{PREFIX}-registration.json'
    reg = dict(inputs=inputs, groups=GROUPS, candidates=source_names,
        catalog=str(catalog_path), store=str(STORE), context=str(source_path),
        btn_source=str(paths['btn']['result']), bb_source=str(paths['bb']['result']),
        maximum_seconds=600, review_maximum_seconds=900, complete_played_generations=list(range(78)), excluded_generation=78,
        method='Read-only individual model views after complete-bank validation; empty own histories permit equal-weight linear attribution. Independent reviewer reconstructs every prefix using the unmodified bank constructor.',
        opponent='For each candidate, hold the other player at its original complete 78-generation average.',
        selection=False, gpu_used=False, production_modified=False,
        scope='Post-hoc source-of-error diagnosis for two already inspected exact endpoints. No checkpoint selection, policy change, paired-opponent ranking, full-game convergence or deployment claim.')
    save(rp,reg); STORE.mkdir(); acquired=False; error=None
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True; output={}; artifacts={}
        for name,prefix in source_names.items():
            guard(); er=read(OUT/f'{prefix}-evaluation-v1-registration.json')
            documents,CpuBank,_=load_models(name,er,source)
            assert [d['generation'] for d in documents] == list(range(78))
            bank=CpuBank(documents,context_source=source)
            query=dict(context_source=source,observations=obs)
            complete,support=bank.average(query,guard=guard)
            assert np.array_equal(support,np.full(265,78.))
            policies=[]
            for generation in range(78):
                guard()
                # The stored documents retain their true generation identities.
                # Only the already validated in-memory model view is restricted.
                view=copy.copy(bank);view.models=[bank.models[generation]]
                if hasattr(view,'weights'):view.weights=np.ones((2,1))
                policy,one=view.average(query,guard=guard)
                assert np.array_equal(one,np.ones(265))
                policies.append(policy.tolist())
            policies=np.asarray(policies)
            policy_error=float(np.max(abs(policies.mean(0)-complete)))
            assert policy_error<1e-12
            prior_policy=read(docs['btn']['result']['candidates'][name]['policy_artifact'])
            bb_rows=docs['bb']['result']['candidates'][name]['classes']
            btn_rows=docs['btn']['result']['candidates'][name]['values']['classes']
            indices={(r['player'],r['hand_class']):i for i,r in enumerate(catalog)}
            for (player,c),i in indices.items():
                expected=prior_policy['root_probabilities'][c] if player==0 else [1-prior_policy['btn_call_probabilities'][c],prior_policy['btn_call_probabilities'][c],0,0]
                assert np.max(abs(complete[i]-expected))<1e-12
            records=[]
            for generation,p in enumerate(policies):
                bb_gain=0.;btn_gain=0.;jam_frequency=0.;call_mass=0.;jam_mass=0.
                for row in bb_rows:
                    c=row['hand_class'];q=p[indices[(0,c)]];m=row['entry_probability']
                    f,j=row['fold_value'],row['jam_value']
                    bb_gain+=m*((q[0]+q[3])*max(f,j)-q[0]*f-q[3]*j)
                    jam_frequency+=m*q[3]
                for row in btn_rows:
                    if row['entry_probability']==0:continue
                    c=row['hand_class'];q=p[indices[(1,c)]]
                    f,j=row['fold_value_per_entry'],row['call_value_per_entry']
                    btn_gain+=max(f,j)-q[0]*f-q[1]*j
                    call_mass+=row['jam_probability']*q[1];jam_mass+=row['jam_probability']
                assert min(bb_gain,btn_gain)>=-1e-10
                records.append(dict(generation=generation,bb_gain=float(bb_gain),btn_gain=float(btn_gain),
                    bb_jam_frequency=float(jam_frequency),btn_call_given_fixed_jam=float(call_mass/jam_mass)))
            expected_bb=docs['bb']['result']['candidates'][name]['gain_bb_per_entry']
            expected_btn=docs['btn']['result']['candidates'][name]['values']['gains_per_entry']['best']
            errors={metric:abs(sum(r[metric] for r in records)/78-expected) for metric,expected in [('bb_gain',expected_bb),('btn_gain',expected_btn)]}
            assert max(errors.values())<1e-10
            groups={label:{metric:dict(mean=sum(records[g][metric] for g in ids)/len(ids),
                contribution_to_full_average=sum(records[g][metric] for g in ids)/78)
                for metric in ('bb_gain','btn_gain')} for label,ids in GROUPS.items()}
            pp=STORE/f'{name}-generation-policies.json';save(pp,dict(ordered_catalog_sha256=sha(catalog_path),policies=policies.tolist()))
            artifacts[str(pp)]=sha(pp)
            output[name]=dict(policy_artifact=str(pp),policy_sha256=sha(pp),records=records,groups=groups,
                complete_policy_mean_error=policy_error,complete_endpoint_mean_errors=errors)
        for p,h in {**inputs,**artifacts}.items():assert sha(p)==h,p
        guard()
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),candidates=output,
            artifacts=artifacts,seconds=time.monotonic()-began,gpu_used=False,production_modified=False,
            accuracy_qualified=False,scope=reg['scope']))
        print(json.dumps({k:v['groups'] for k,v in output.items()}))
    except BaseException as exc:error=repr(exc);raise
    finally:
        try:save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if error else 'complete',error=error,seconds=time.monotonic()-began))
        finally:
            if acquired:
                assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
