"""Saved-policy/cards control of external-action noise; no fitting or GPU use."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from reboot_research_idle_v1 import idle
from ntfs_research_storage_v1 import create_compressed_directory, measure_tree
from hu_root_retained_storage_admitted_study_20260924 import measure, LIMIT, METADATA_RESERVE

PREFIX = 'root-action-integration-v1'
STORE = Path('T:/GTOpen-research')/PREFIX
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
UPDATE = ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe'
FULL = ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'


def root_values(updates, queries):
    records = updates['records']; obs = queries['observations']
    heads = [i for i,r in enumerate(records) if obs[r[0]]['phase']==0 and int(obs[r[0]]['hi'])==1]
    assert len(heads) == len(updates['roots']) == 128
    values = []
    for k,(index,root) in enumerate(zip(heads,updates['roots'])):
        assert root[:2] == list(divmod(k,2))
        r = records[index]
        if root[1] == 0:
            assert r[1:3] == [0,4]
            values.append(np.asarray(r[3])+root[2])
    values = np.asarray(values)
    assert values.shape==(64,4) and np.max(abs(values[:,0]+1)) < 1e-9
    return values


def main():
    started = time.monotonic(); last = 0.
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    def guard():
        nonlocal last
        now = time.monotonic(); assert now-started < 1800
        if now-last > 2:
            assert idle() and psutil.virtual_memory().available > 20_000_000_000
            assert psutil.disk_usage('T:/').free > 40_000_000_000
            last = now
    guard(); assert not LOCK.exists() and not OTHER.exists() and not STORE.exists()
    context = OUT/'bb-context-candidate.json'
    inputs = {str(p):sha(p) for p in [context, UPDATE, FULL, Path(__file__),
        ROOT/'tools/research/hu_root_action_integration_review_20260925.py',
        OUT/'ROOT-ACTION-INTEGRATION-CONTROL-PLAN.md']}
    for name in ('sampled_physical_root_evaluation_v1.py','later_average_support_v1.py',
                 'reboot_research_idle_v1.py','ntfs_research_storage_v1.py',
                 'hu_root_retained_storage_admitted_study_20260924.py'):
        p=ROOT/'tools/research'/name;inputs[str(p)]=sha(p)
    admitted_full=OUT/'root-retained-wider-study-v1-registration.json'
    approved=read(admitted_full)
    assert approved['inputs'][str(FULL)]==sha(FULL)
    inputs[str(admitted_full)]=sha(admitted_full)
    fixtures = []
    for prefix in ('root-retained-fresh-pilot-v1','root-retained-replication-resume-v1'):
        paths = [OUT/f'{prefix}-{s}.json' for s in ('registration','result','independent-review')]
        reg,result,audit = map(read,paths)
        assert result['passed'] and audit['passed'] and audit['completed_updates']==78
        assert result['registration_sha256']==audit['source_registration_sha256']==sha(paths[0])
        assert audit['source_result_sha256']==sha(paths[1])
        assert reg['inputs'][str(UPDATE)]==sha(UPDATE)
        inputs.update({str(p):sha(p) for p in paths})
        for iteration in (1,26,52,78):
            folder = Path(result['store'])/f'iteration-{iteration:04d}'
            mp = folder/'metrics.json'; assert sha(mp)==result['steps'][iteration-1]['metrics_sha256']
            metric = read(mp); inputs[str(mp)] = sha(mp)
            source = folder/'batch-00'
            for name in ('batch','queries','policies','updates','derived-targets'):
                p=source/f'{name}.json'
                assert sha(p)==metric['subbatches'][0]['artifacts'][name]
                inputs[str(p)]=sha(p)
            fixtures.append(dict(source=str(source), training_prefix=prefix, iteration=iteration,
                seeds=[358501+1000*len(fixtures)+r for r in range(16)]))
    inventory = measure(); allocated=sum(x['allocated_file_bytes'] for x in inventory)
    assert allocated+2_000_000_000+METADATA_RESERVE <= LIMIT
    rp=OUT/f'{PREFIX}-registration.json'; assert not rp.exists()
    save(rp,dict(inputs=inputs,fixtures=fixtures,store=str(STORE),maximum_seconds=1800,
        allocation_cap=2_000_000_000,logical_cap=4_000_000_000,
        storage_admission=dict(roots=inventory,allocated_bytes=allocated,limit_bytes=LIMIT,reserve_bytes=METADATA_RESERVE),
        scope='Conditional opponent-action variance on saved training cards/policies. No new physical data, fitting, GPU use or strength qualification.',
        production_modified=False))
    acquired=False;error=None;artifacts={};rows=[]
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True; assert not OTHER.exists(); guard();create_compressed_directory(STORE)
        def storage_check():
            value=measure_tree(STORE,guard)
            assert value['allocated_file_bytes']<=2_000_000_000 and value['logical_bytes']<=4_000_000_000
            assert value['compressed_files']==value['files']
            return value
        def invoke(exe,args):
            guard(); proc=subprocess.run([str(exe),*map(str,args)],capture_output=True,text=True,
                timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
            assert proc.returncode==0,proc.stderr[-2000:]
            guard()
        for fi,fixture in enumerate(fixtures):
            before=time.monotonic(); guard()
            source=Path(fixture['source']); folder=STORE/f'fixture-{fi:02d}';folder.mkdir()
            batch=read(source/'batch.json'); queries=read(source/'queries.json'); policies=read(source/'policies.json')
            assert len(batch['deals'])==64 and batch['format']==3
            assert queries['context_source']==policies['context_source']==context.read_text()
            assert queries['batch_source']==policies['batch_source']==(source/'batch.json').read_text()
            original=root_values(read(source/'updates.json'),queries)
            corrected=read(source/'derived-targets.json')['bb_root_corrections']
            assert np.max(abs(original[:,:3]-np.asarray([np.asarray(x['advantages'])[:3]+x['derived_root_value'] for x in corrected])))<1e-9
            profile_rows=policies['policies']
            profiles=[dict(name='baseline',policies=profile_rows)]
            root_ids=[i for i,o in enumerate(queries['observations']) if o['phase']==0 and int(o['hi'])==1]
            for action in range(4):
                changed=list(profile_rows)
                for i in root_ids:changed[i]=dict(changed[i],probabilities=np.eye(4)[action].tolist())
                profiles.append(dict(name=f'action-{action}',policies=changed))
            full_profiles=folder/'profiles.json'
            save(full_profiles,dict(format=1,context_source=policies['context_source'],batch_source=policies['batch_source'],profiles=profiles))
            full_output=folder/'full-values.json'
            a=time.monotonic();invoke(FULL,[context,source/'batch.json',full_profiles,full_output]);full_seconds=time.monotonic()-a
            full=read(full_output); assert full['maximum_forward_cashflow_error']<1e-10 and full['maximum_conservation_error']<1e-10
            assert [p['name'] for p in full['profiles']]==['baseline',*[f'action-{i}' for i in range(4)]]
            exact=np.asarray([[d['values'][0] for d in p['deals']] for p in full['profiles'][1:]]).T
            baseline=np.asarray([d['values'][0] for d in full['profiles'][0]['deals']])
            mixed=[]
            for i,x in enumerate(corrected):mixed.append(exact[i]@np.asarray(profile_rows[x['query']]['probabilities']))
            assert np.max(abs(baseline-np.asarray(mixed)))<1e-9 and np.max(abs(exact[:,0]+1))<1e-12
            draws=[];sample_seconds=[]
            for ri,seed in enumerate(fixture['seeds']):
                part=folder/f'repeat-{ri:02d}';part.mkdir()
                bp=part/'batch.json';pp=part/'policies.json';up=part/'updates.json'
                save(bp,dict(batch,seed=seed,batch_id=f'{PREFIX}-fixture-{fi}-repeat-{ri}'))
                save(pp,dict(policies,batch_source=bp.read_text()))
                a=time.monotonic();invoke(UPDATE,['verify',context,bp,pp,up]);sample_seconds.append(time.monotonic()-a)
                draws.append(root_values(read(up),queries))
                if ri%4==3:storage_check()
            draws=np.asarray(draws);e=draws[:,:,1:3]-exact[None,:,1:3]
            e=np.concatenate([e,(e[:,:,0]-e[:,:,1])[:,:,None]],axis=2)
            row=dict(fixture=fi,training_prefix=fixture['training_prefix'],iteration=fixture['iteration'],
                conditional_action_noise_variance=e.var(0,ddof=1).mean(0).tolist(),
                pooled_mean_error=e.mean((0,1)).tolist(),
                rms_per_deal_mean_error=np.sqrt(np.mean(e.mean(0)**2,axis=0)).tolist(),
                full_evaluation_seconds=full_seconds,sampling_verify_seconds=sample_seconds,
                seconds=time.monotonic()-before)
            rows.append(row);save(folder/'summary.json',row)
            storage=storage_check()
            for p in folder.rglob('*'):
                if p.is_file():artifacts[str(p)]=sha(p)
            print(json.dumps(dict(fixture=fi,iteration=fixture['iteration'],variance=row['conditional_action_noise_variance'],allocated=storage['allocated_file_bytes'])),flush=True)
        for p,h in {**inputs,**artifacts}.items():assert sha(p)==h,p
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),artifacts=artifacts,
            fixtures=rows,storage=storage_check(),seconds=time.monotonic()-started,
            contrasts=['call','raise','call minus raise'],production_modified=False,accuracy_qualified=False,
            scope='Descriptive external-action noise at fixed cards/current policies. Full action integration removes that conditional randomness, not board/private-card noise or approximation error.'))
    except BaseException as exc:error=repr(exc);raise
    finally:
        save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if error else 'complete',error=error,seconds=time.monotonic()-started))
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
