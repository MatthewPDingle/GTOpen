"""Post-hoc complete-sample diagnostic of conditional all-in evaluation.

Reuses the completed hybrid test population and its frozen responder. Does not
train or select a policy, draw new test deals, or produce new confidence claims.
Single CPU equity worker, no GPU inference or changes to active protocols.
"""
import json
from pathlib import Path
import subprocess
import time
import uuid

import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_allin_protocol_v3 import AllinCache,canonical
from hu_sampled_physical_dense_btn_jam_diagnosis_20260923 import showdown

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-allin-population-diagnostic-v1'
SOURCE='sampled-physical-hybrid-evaluation-v2'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    started=time.monotonic();last=0.;child=None;stage='preparing';error=None
    completed_keys=0;completed_deals=0
    def guard():
        nonlocal last
        now=time.monotonic()
        if now-last>=2:
            assert now-started<5400 and idle(),'Deadline or production activity'
            assert psutil.virtual_memory().available>=20_000_000_000
            assert psutil.disk_usage(str(STORE.parent)).free>=40_000_000_000
            last=now
    guard()
    source_paths={s:OUT/f'{SOURCE}-{s}.json' for s in ('registration','result','independent-review')}
    source_reg,source_result,source_review=[json.loads(source_paths[s].read_text()) for s in source_paths]
    assert source_review['passed'] and source_review['result_sha256']==sha(source_paths['result'])
    assert source_review['registration_sha256']==sha(source_paths['registration'])
    source_store=Path(source_reg['store']);context_path=Path(source_reg['context']);context=json.loads(context_path.read_text())
    response_path=source_store/'response.json';response=json.loads(response_path.read_text())
    assert sha(response_path)==source_result['response_sha256']
    learned_review=OUT/'sampled-physical-allin-learned-evaluation-control-v1-independent-review.json'
    learned_result=OUT/'sampled-physical-allin-learned-evaluation-control-v1-result.json'
    assert json.loads(learned_review.read_text())['source_result_sha256']==sha(learned_result)
    assert json.loads(learned_review.read_text())['passed']
    cache_review=OUT/'sampled-physical-allin-training-cache-v1-independent-review.json'
    oldcache=AllinCache.from_review(cache_review)
    keys=set();source_batches={}
    for offset in range(0,16384,16):
        guard();folder=source_store/f'{SOURCE}-test-{offset}'
        sp=folder/'summary.json';bp=folder/'batch.json'
        summary=json.loads(sp.read_text());batch=json.loads(bp.read_text())
        assert sha(sp)==source_result['batch_summary_hashes'][folder.name]
        assert sha(bp)==summary['artifacts']['batch.json'] and len(batch['deals'])==16
        keys.update(canonical(d[:4]) for d in batch['deals'])
        source_batches[str(sp)]=sha(sp);source_batches[str(bp)]=sha(bp)
    keys=sorted(keys);missing=[k for k in keys if k not in oldcache.rows]
    board_exe=ROOT/'target/release/examples/hu_allin_board_reference.exe'
    eval_exe=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    paths=[Path(__file__),*source_paths.values(),response_path,context_path,learned_review,learned_result,
           cache_review,board_exe,eval_exe,ROOT/'tools/research/sampled_allin_protocol_v3.py',
           ROOT/'tools/research/hu_sampled_physical_dense_btn_jam_diagnosis_20260923.py',
           ROOT/'crates/solver/examples/hu_sampled_profile_allin_evaluation_v1.rs',
           ROOT/'crates/solver/examples/hu_allin_board_reference.rs']
    registration=dict(inputs={str(p):sha(p) for p in paths},source_batches=source_batches,
        source_prefix=SOURCE,source_test_deals=16384,unique_keys=len(keys),cached_keys=len(keys)-len(missing),
        missing_keys=len(missing),equity_batch_size=20,native_batch_size=16,
        maximum_seconds=5400,host_reserve_bytes=20_000_000_000,disk_reserve_bytes=40_000_000_000,
        maximum_new_store_bytes=16_000_000_000,comparisons=source_reg['comparisons'],
        scope='Post-hoc conditional-all-in re-evaluation of all 16,384 already inspected hybrid test deals, retaining the original five policies and training-only responder. Descriptive means and variances only; no new confidence, candidate selection, refitting, fresh population test or deployment. Include exact equity cache construction cost.',
        production_modified=False)
    regpath=OUT/f'{PREFIX}-registration.json';assert not STORE.exists();save(regpath,registration);STORE.mkdir()
    save(STORE/'keys.json',keys);save(STORE/'missing-keys.json',missing)
    rows={k:oldcache.rows[k] for k in keys if k in oldcache.rows};cache_artifacts={};evaluation_artifacts={}
    native_seconds=0.;store_bytes=0
    def status():
        path=OUT/f'{PREFIX}-status.json';tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
        save(tmp,dict(state=stage,error=error,controller_pid=psutil.Process().pid,
             child_pid=child.pid if child is not None and child.poll() is None else None,
             completed_new_keys=completed_keys,total_new_keys=len(missing),completed_deals=completed_deals,
             seconds=time.monotonic()-started,production_modified=False));tmp.replace(path)
    def invoke(exe,args,log):
        nonlocal child
        guard();child=subprocess.Popen([str(exe),*map(str,args)],cwd=ROOT,stdout=log,
              stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);status()
        while child.poll() is None:
            time.sleep(.25);guard()
        assert child.returncode==0,f'Native failure: {exe.name}'
    try:
        stage='equity-cache';status()
        with (STORE/'native.log').open('x') as log:
            for offset in range(0,len(missing),20):
                guard();folder=STORE/f'equity-{offset:05d}';folder.mkdir()
                selected=missing[offset:offset+20]
                cases=[dict(private_cards=h,sampled_boards=[[c for c in range(52) if c not in h][:5]]) for h in selected]
                ip=folder/'input.json';op=folder/'native.json';save(ip,dict(format=1,cases=cases))
                invoke(board_exe,[ip,op],log);output=json.loads(op.read_text());assert len(output)==len(cases)
                for case,native in zip(cases,output):
                    assert native['private_cards']==list(case['private_cards'])
                    assert native['wins']+native['ties']+native['losses']==native['exact_boards']==1712304
                    assert native['equity']==(native['wins']+.5*native['ties'])/1712304
                    w=showdown(list(case['private_cards'])+case['sampled_boards'][0])
                    assert native['sampled_scores']==[1 if w<0 else 2 if w==0 else 0]
                    rows[tuple(case['private_cards'])]=dict(private_cards=native['private_cards'],wins=native['wins'],
                        ties=native['ties'],losses=native['losses'],boards=native['exact_boards'])
                    completed_keys+=1;native_seconds+=native['exact_seconds']
                cache_artifacts.update({str(p):sha(p) for p in (ip,op)})
                status()
                if offset%500==0:print(json.dumps(dict(stage=stage,new_keys=completed_keys,total=len(missing))),flush=True)
            cachepath=STORE/'cache.json';save(cachepath,dict(format=1,player_roles_fixed=True,rows=[rows[k] for k in keys]))
            cache=AllinCache(cachepath,sha(cachepath));cache_seconds=time.monotonic()-started
            stage='evaluation';status();all_rows=[];max_mix=0.;max_forward=0.
            for offset in range(0,16384,16):
                guard();source=source_store/f'{SOURCE}-test-{offset}';folder=STORE/f'test-{offset}';folder.mkdir()
                summary=json.loads((source/'summary.json').read_text());batch=json.loads((source/'batch.json').read_text())
                assert sha(source/'summary.json')==source_result['batch_summary_hashes'][source.name]
                for name,h in summary['artifacts'].items():assert sha(source/name)==h
                profile=json.loads((source/'profiles.json').read_text())
                assert profile['context_source']==context_path.read_text() and profile['batch_source']==(source/'batch.json').read_text()
                labelled=cache.batch(batch);bp=folder/'batch.json';save(bp,labelled)
                profile['batch_source']=bp.read_text();pp=folder/'profiles.json';save(pp,profile)
                native_path=folder/'native.json';invoke(eval_exe,[context_path,bp,pp,native_path],log)
                native=json.loads(native_path.read_text());expected_names=['baseline']+[f'action-{a}' for a in range(4)]
                assert [p['name'] for p in native['profiles']]==expected_names
                values=[[d['values'][0] for d in p['deals']] for p in native['profiles']]
                assert all(len(v)==16 for v in values)
                old_native=json.loads((source/'native.json').read_text())
                for old,new in zip(old_native['profiles'],native['profiles']):
                    assert old['name']==new['name']
                    for a,b in zip(old['deals'],new['deals']):
                        assert a['expected_rake']==b['expected_rake'] and a['terminal_mass']==b['terminal_mass']
                    if old['name'] in ('action-0','action-1'):assert old['deals']==new['deals']
                original_paired=json.loads((source/'paired.json').read_text())
                assert original_paired['response_sha256']==sha(response_path)
                assert original_paired['series']==registration['comparisons']
                for i,c in enumerate(summary['classes']):
                    baseline=values[0][i];actions=[values[a+1][i] for a in range(4)];mix=summary['root_probabilities'][i]
                    err=abs(sum(p*v for p,v in zip(mix,actions))-baseline);max_mix=max(max_mix,err);assert err<1e-9
                    chosen=response['actions'][c]
                    differences=[actions[chosen]-baseline if chosen>=0 else 0.]+[v-baseline for v in actions]
                    oldbase=summary['baseline_values'][i];oldactions=summary['action_values'][i]
                    olddiff=[oldactions[chosen]-oldbase if chosen>=0 else 0.]+[v-oldbase for v in oldactions]
                    assert max(abs(a-b) for a,b in zip(olddiff,original_paired['differences'][i]))<1e-10
                    all_rows.append(dict(index=offset+i,hand_class=c,original=olddiff,conditional=differences))
                max_forward=max(max_forward,native['maximum_forward_cashflow_error'])
                for p in (bp,pp,native_path):evaluation_artifacts[str(p)]=sha(p);store_bytes+=p.stat().st_size
                assert store_bytes<registration['maximum_new_store_bytes']
                completed_deals+=16;status()
                if offset%1024==0:print(json.dumps(dict(stage=stage,deals=completed_deals)),flush=True)
        assert len(all_rows)==16384
        # No new confidence interval: original test outcomes were already seen.
        before=np.asarray([r['original'] for r in all_rows]);after=np.asarray([r['conditional'] for r in all_rows])
        diagnostics=[]
        for i,name in enumerate(registration['comparisons']):
            original_variance=float(before[:,i].var(ddof=1));new_variance=float(after[:,i].var(ddof=1))
            assert abs(float(before[:,i].mean())-source_result['intervals'][name]['mean'])<1e-9
            assert abs(original_variance-source_result['intervals'][name]['sample_variance'])<1e-7
            diagnostics.append(dict(comparison=name,original_mean=float(before[:,i].mean()),
                conditional_mean=float(after[:,i].mean()),original_variance=original_variance,
                conditional_variance=new_variance,variance_ratio=new_variance/original_variance))
        rp=STORE/'paired-rows.json';save(rp,all_rows)
        for p,h in registration['inputs'].items():assert sha(p)==h,p
        for p,h in source_batches.items():assert sha(p)==h,p
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(regpath),
            source_test_deals=16384,cache_artifact=str(cachepath),cache_sha256=sha(cachepath),
            cache_artifacts=cache_artifacts,evaluation_artifacts=evaluation_artifacts,
            paired_rows=str(rp),paired_rows_sha256=sha(rp),diagnostics=diagnostics,
            new_equity_keys=len(missing),reused_equity_keys=len(keys)-len(missing),
            native_equity_seconds=native_seconds,cache_phase_seconds=cache_seconds,
            maximum_root_mixture_error_bb=max_mix,maximum_forward_cashflow_error_bb=max_forward,
            seconds=time.monotonic()-started,scope=registration['scope'],production_modified=False))
        stage='complete';print(json.dumps(dict(stage=stage,diagnostics=diagnostics)),flush=True)
    except Exception as exc:
        error=str(exc);stage='stopped';raise
    finally:
        if child is not None and child.poll() is None:child.terminate();child.wait(timeout=20)
        status()


if __name__=='__main__':main()
