"""Prospective changed-policy checks, only for independently qualified models."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import collections
import datetime as dt
import hashlib
import importlib.util
import json
import msvcrt
import sys
from types import SimpleNamespace
import numpy as np
import continuation_bridge_run as bridge
import continuation_interface_reuse as runtime
import continuation_night_queue as queue

study=bridge.study
OUT=study.ROOT/'research/preflop-evolution/continuation/policy-transfer-20260916'
BASE=OUT.parent


def selection(name):
    assert name in ['N09','N15']
    folder='recalibrated-priors' if name=='N09' else 'shrunk-residual'
    model_dir=BASE/(folder+'-20260916');gpu=BASE/(folder+'-gpu-20260916')
    accuracy=study.read(model_dir/'evaluation.json');timing=study.read(gpu/'timing.json')
    assert accuracy['accuracy_screen_passed'] and timing['within_runtime_target']
    assert study.read(gpu/'oracle-check.json')['passed']
    assert study.pilot.sha(model_dir/'candidate.json')==accuracy['candidate_sha256']
    manifest=study.read(gpu/'manifest.json')
    for path,sha in manifest['files'].items():assert study.pilot.sha(study.ROOT/path)==sha,path
    arm='candidate' if name=='N09' else min(['serial','warp'],key=lambda v:timing['median_seconds_per_iteration'][v])
    kernel=gpu/'interface.cu' if name=='N09' else gpu/arm/'interface.cu'
    return model_dir,gpu,arm,kernel


def require_idle():
    assert not bridge.other_research(),'Another GPU child or research controller is active'
    tokens=['continuation_night_queue.py','continuation_shrunk_queue.py','continuation_policy_transfer.py run',
        'continuation_prior_evaluation.py run','continuation_shrunk_evaluation.py run',
        'continuation_prior_gpu.py oracle','continuation_prior_gpu.py benchmark',
        'continuation_shrunk_gpu.py oracle','continuation_shrunk_gpu.py benchmark',
        'continuation_shrunk_mixed_gpu.py oracle','continuation_shrunk_mixed_gpu.py benchmark',
        'continuation_warp_summary.py oracle','continuation_warp_summary.py benchmark']
    for p in queue.processes():
        if p['ProcessId']==os.getpid():continue
        if p['Name'].lower() in ['python.exe','pythonw.exe']:
            assert not any(t in (p['CommandLine'] or '').lower() for t in tokens),'Another sequencing controller is active'
    assert not study.night.live_busy(),'Live app is busy'


def adapter(directory):
    spec=importlib.util.spec_from_file_location('_policy_transfer_reference',bridge.__file__)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.OUT=directory
    module.other_research=lambda:(require_idle() or [])
    return module


def board_sample(fixtures,excluded,seed):
    groups=collections.defaultdict(list)
    for board,iso in fixtures:
        if board in excluded:continue
        cards=[board[i:i+2] for i in range(0,6,2)]
        key=('paired' if len({c[0] for c in cards})<3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))+'suits'
        groups[key].append((board,iso))
    assert len(groups)==5
    boards=[]
    for key,rows in sorted(groups.items()):
        assert len(rows)>=10,'Insufficient unused boards; do not silently reuse previous data'
        rows.sort(key=lambda b:hashlib.sha256((seed+b[0]).encode()).digest())
        boards.extend(dict(board=b,iso_weight=i,stratum=key,inclusion_probability=10/len(rows)) for b,i in rows[:10])
    assert len(boards)==50 and len({b['board'] for b in boards})==50
    return boards


def validate_snapshot(snapshot):
    assert snapshot['iteration']==500 and snapshot['start_iteration']==150 and snapshot['warmup_iterations']==0
    assert np.isfinite(snapshot['evs']).all() and np.isfinite(snapshot['gaps']).all()
    assert len(snapshot['leaves'])==2
    for leaf in snapshot['leaves']:
        w=np.array(leaf['weights']);assert w.shape==(2,169) and np.isfinite(w).all() and (w>=0).all()
        assert (w.sum(axis=1)>0).all() and 1<=leaf['stack']/leaf['pot']<=20
    for item in snapshot['views']:
        v=item['view'];n=len(v['actions']);s=np.array(v['strategy'])
        if not n:continue
        assert s.size==169*n and np.isfinite(s).all() and (s>=-1e-7).all() and (s<=1+1e-7).all()
        np.testing.assert_allclose(s.reshape(n,169).sum(axis=0),1,atol=2e-5,rtol=0)


def prepare(name):
    model_dir,gpu,arm,kernel=selection(name);directory=OUT/name;directory.mkdir(parents=True,exist_ok=True)
    sources={a:gpu/'repeat-0'/('original' if a=='original' else arm)/'policy.gtop' for a in ['original','candidate']}
    files=[OUT/'README.md',study.ROOT/'tools/research/continuation_policy_transfer.py',
        study.ROOT/'tools/research/continuation_bridge_run.py',model_dir/'candidate.json',model_dir/'evaluation.json',
        gpu/'timing.json',gpu/'oracle-check.json',gpu/'manifest.json',runtime.BIN,kernel,*sources.values()]
    hashes={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in files}
    hashes.update(study.read(gpu/'manifest.json')['files'])
    study.freeze(directory/'protocol-freeze.json',dict(files=hashes,model=name,variant=arm,production_enabled=False))
    for action in ['original','candidate']:
        target=directory/action;target.mkdir(exist_ok=True)
        if not (target/'iteration-500.json').exists():
            require_idle()
            runtime.command(['solve',sources[action],target,action,350,kernel,'resume'],target/'run.log',optimized=action=='candidate',warm=0)
        validate_snapshot(study.read(target/'iteration-500.json'))
    snapshots={a:study.read(directory/a/'iteration-500.json') for a in ['original','candidate']}
    assert snapshots['original']['config']==snapshots['candidate']['config']
    assert [v['path'] for v in snapshots['original']['views']]==[v['path'] for v in snapshots['candidate']['views']]
    assert [(v['path'],v['positions']) for v in snapshots['original']['leaves']]==[(v['path'],v['positions']) for v in snapshots['candidate']['leaves']]
    comparisons=[]
    for left,right in zip(snapshots['original']['views'],snapshots['candidate']['views']):
        a=left['view'];b=right['view'];labels=[v['label'] for v in a['actions']]
        assert labels==[v['label'] for v in b['actions']] and a['actor_pos']==b['actor_pos']
        sa=np.array(a['strategy']).reshape(len(labels),169);sb=np.array(b['strategy']).reshape(len(labels),169)
        comparisons.append(dict(path=left['path'],actor=a['actor_pos'],actions=labels,
            original_frequencies=[v['freq'] for v in a['actions']],candidate_frequencies=[v['freq'] for v in b['actions']],
            probes={h:dict(original=sa[:,study.pilot.INDEX[h]].tolist(),candidate=sb[:,study.pilot.INDEX[h]].tolist()) for h in study.night.PROBES}))
    study.freeze(directory/'strategy-comparison.json',dict(iterations=500,nodes=comparisons,production_enabled=False,
        caveat='Descriptive strategy changes at fixed work; neither convergence nor agreement with an independent preflop solution is established.'))
    if (directory/'prospective/manifest.json').exists():return adapter(directory).checked('prospective')
    cases=[]
    for action,snapshot in snapshots.items():
        for leaf in snapshot['leaves']:
            w,removed,added=study.night.clean_weights(leaf['weights'])
            text=lambda p:','.join(f'{study.pilot.LABELS[h]}:{v:.9f}' for h,v in enumerate(w[p]) if v>0)
            cases.append(dict(leaf,id=action+'-'+leaf['id'],family='changed-policy-'+action,partition='test',
                weights=w.tolist(),range_oop=text(0),range_ip=text(1),removed_mass_fraction=removed,
                probe_added_mass_fraction=added,source_policy=action,source_sha256=study.pilot.sha(directory/action/'iteration-500.json')))
    excluded=set();manifests=list(BASE.rglob('manifest.json'))
    manifests += [study.pilot.OUT/'manifest.json',study.pilot.AUDIT/'manifest.json',study.pilot.AUDIT/'extension/manifest.json']
    for path in sorted(set(manifests)):
        m=study.read(path)
        excluded.update(b['board'] for b in m.get('boards',[]) if isinstance(b,dict) and 'board' in b)
        excluded.update(j['board'] for j in m.get('jobs',[]) if 'board' in j)
        hashes[str(path.relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(path)
    fixtures=study.pilot.AUDIT/'fixtures.json'
    hashes[str(fixtures.relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(fixtures)
    boards=board_sample(study.read(fixtures)['canonical_flops'],excluded,'policy-transfer-20260916-'+name)
    jobs=[]
    for c in cases:
        for b in boards:
            size={'bet':[{'PotPct':50}],'raise':[{'PotPct':100}],'donk':[{'PotPct':50}]}
            cfg=dict(board=b['board'],range_oop=c['range_oop'],range_ip=c['range_ip'],tree=dict(starting_pot=c['pot'],
                effective_stack=c['stack'],rake_pct=0,rake_cap=0,oop=[size]*3,ip=[size]*3,max_raises=1,add_allin=False,allin_threshold=.85))
            jobs.append(dict(**b,case=c['id'],id=c['id']+'-'+b['board'],config=cfg))
    original=study.night.checked_manifest()
    frozen_path=directory/'protocol-freeze.json'
    hashes[str(frozen_path.relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(frozen_path)
    for a in snapshots:
        for filename in ['iteration-500.json','policy.gtop']:
            path=directory/a/filename;hashes[str(path.relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(path)
    hashes[original['binary_path']]=original['binary_sha256']
    manifest=study.signed(dict(cases=cases,boards=boards,jobs=jobs,partition='prospective',inputs=hashes,
        binary_path=original['binary_path'],binary_sha256=original['binary_sha256'],target_gap_pct=.1,max_iterations=2000,
        protocol='Fixed 500-iteration policy transfer; four cases each require >=15% improvement vs Balanced and <=10% regression vs previous predictor.'))
    study.freeze(directory/'prospective/manifest.json',manifest)
    study.freeze(directory/'candidate.json',study.read(model_dir/'candidate.json'))
    study.freeze(directory/'candidate-freeze.json',dict(sha256=study.pilot.sha(directory/'candidate.json'),
        frozen_at=study.night.now(),evaluation_manifest_id=manifest['id'],references_at_freeze=0))
    return manifest


def case_gate(cases):
    assert len(cases)==4 and len({c['case'] for c in cases})==4
    return all(np.isfinite([r['mae_pct_pot']['candidate'],r['mae_pct_pot']['balanced'],r['regression_vs_previous']]).all()
        and r['mae_pct_pot']['candidate']<=.85*r['mae_pct_pot']['balanced'] and r['regression_vs_previous']<=.1 for r in cases)


def evaluate(name):
    directory=OUT/name;module=adapter(directory);contexts=module.contexts('prospective')
    module.contexts=lambda partition:contexts
    module.study=SimpleNamespace(**study.__dict__);module.study.fit=SimpleNamespace(**study.fit.__dict__)
    original_predict=study.fit.predict
    candidate=study.read(directory/'candidate.json')
    if name=='N09':
        import continuation_recalibrated_priors as predictor
        assert candidate['chance']=='compatible_pair' and len(candidate['class_base'])==169
    else:
        import continuation_nonlinear_residual as predictor
        assert candidate['kind']=='shrunk_nonlinear_residual'
    module.study.fit.predict=lambda c,m:predictor.predict(c,m) if m==candidate else original_predict(c,m)
    module.study.night=SimpleNamespace(**study.night.__dict__)
    def write_result(path,value):
        if path.name=='evaluation.json':
            value['accuracy_screen_passed']=case_gate(value['cases'])
            value['caveat']='Fresh boards on ranges produced by fixed 500-iteration policies in a familiar scenario. Not untouched-context generalization or full-game convergence. No model fitting. Restricted postflop tree and approximate card removal remain.'
        study.night.dump(path,value)
    module.study.night.dump=write_result
    return module.evaluate()


def run(name):
    directory=OUT/name;directory.mkdir(parents=True,exist_ok=True)
    with (OUT/'run.lock').open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        try:
            require_idle()
            if not (directory/'protocol-freeze.json').exists():
                assert (bridge.DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()>=3600,'Too late to start a new study'
            prepare(name);adapter(directory).run_partition('prospective');result=evaluate(name)
            study.night.dump(directory/'status.json',dict(stage='complete',accuracy_screen_passed=result['accuracy_screen_passed'],
                production_enabled=False,updated=study.night.now()))
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)


if __name__=='__main__':{'run':run,'evaluate':evaluate}[sys.argv[1]](sys.argv[2])
