"""Four fixed-budget fresh-seed training arms with compact lossless evidence.

No performance selection or range-quality claim. Final evaluation is separate.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
import psutil
from later_average_support_v1 import OUT,read,load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from hu_action_integrated_exact_20260925 import bank_args
from hu_paired_continuation_support_20260925 import setup_cuda,LOCK,OTHER
from hu_root_retained_storage_admitted_study_20260924 import measure,LIMIT,METADATA_RESERVE
from reboot_research_idle_v1 import idle
from owned_research_archive_v1 import pack,unpack,retire
import later_action_cadence_training_v1 as baseline
import showdown_cadence_training_v1 as treatment
import later_action_checkpoint_v1 as baseline_checkpoint
import showdown_root_checkpoint_v1 as treatment_checkpoint

PREFIX='showdown-matched-training-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
CAP=4_250_000_000
SECONDS=14*3600


def output(suffix):return OUT/f'{PREFIX}-{suffix}.json'
def status(value):
    path=output('status');temporary=path.with_suffix('.tmp');save(temporary,value);temporary.replace(path)


def worker(reg):
    import torch
    setup_cuda();start=time.monotonic();last=last_size=0.
    def guard():
        nonlocal last,last_size
        now=time.monotonic()
        assert now-start<SECONDS
        if now-last>=2:
            assert idle() and not OTHER.exists()
            assert psutil.virtual_memory().available>=20_000_000_000
            assert shutil.disk_usage('S:/').free>=40_000_000_000
            assert torch.cuda.mem_get_info()[0]>=3_000_000_000
            last=now
        if now-last_size>=10:
            assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())<=CAP
            last_size=now
    guard()
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    STORE.mkdir();token=uuid.uuid4().hex
    save(STORE/'archive-owner.json',dict(format=1,token=token,purpose='new-research-scratch-v1'))
    cp=OUT/'bb-context-candidate.json';args=bank_args(cp.read_text());cache=load_complete_cache()
    step=dict(context_path=cp,catalog_source=args['catalog_source'],matrix_sha256=args['matrix_sha256'],
        matrix_source=(OUT/'preflop-allin-matrix-control-v1-matrix.json').read_text(),cache=cache,
        executable=ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe',
        integration_executable=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe',
        trace_executable=ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe',guard=guard)
    results=[]
    for arm in reg['arms']:
        guard();label=arm['name'];cfg=arm['config'];case=STORE/label;case.mkdir();objects=case/'objects';objects.mkdir()
        assert cfg['torch_version']==torch.__version__ and cfg['numpy_version']==__import__('numpy').__version__
        assert cfg['device_name']==torch.cuda.get_device_name()
        module=baseline if arm['treatment']=='baseline' else treatment
        checkpoint=baseline_checkpoint if arm['treatment']=='baseline' else treatment_checkpoint
        kwargs=dict(step,batch_prefix=PREFIX+'-'+str(arm['seed']))  # Identical card/action labels within each pair.
        if arm['treatment']!='baseline':kwargs.update(coefficients=read(OUT/'showdown-root-control-coefficients-v1.json'),
            score_executable=ROOT/'target/release/examples/hu_board_outcomes_v1.exe')
        state=module.initialize(objects,cfg,**args);initial=module.save_state(objects,state,cfg,**args)
        metrics=[];checkpoint_archives=[];arm_started=time.monotonic()
        for iteration in range(1,79):
            guard();began=time.monotonic();folder=case/f'iteration-{iteration:04d}'
            due=iteration%8==0 or iteration==78
            metric=module.update(folder,objects,state,cfg,checkpoint_due=due,**kwargs)
            archives=[]
            for chunk in range(8):
                part=folder/f'batch-{chunk:02d}';destination=case/f'iteration-{iteration:04d}-batch-{chunk:02d}.xz'
                manifest=pack(part,[p.name for p in part.iterdir() if p.is_file()],destination,root=STORE,token=token,guard=guard)
                retire(part,destination,manifest,root=STORE,token=token,guard=guard)
                archives.append(dict(path=str(destination),manifest_sha256=sha(destination.with_suffix('.xz.json')),
                    packed_bytes=manifest['packed_bytes']))
            if due:
                destination=case/f'checkpoint-reservoirs-{iteration:04d}.xz'
                names=[p.name for p in objects.glob('*.npz')]
                manifest=pack(objects,names,destination,root=STORE,token=token,guard=guard)
                retire(objects,destination,manifest,root=STORE,token=token,guard=guard)
                checkpoint_archives.append(dict(iteration=iteration,path=str(destination),
                    manifest_sha256=sha(destination.with_suffix('.xz.json'))))
                save(case/f'checkpoint-{iteration:04d}.json',dict(checkpoint=metric['checkpoint'],
                    reservoir_archive=checkpoint_archives[-1],completed_iterations=iteration))
            row=dict(iteration=iteration,metrics_sha256=sha(folder/'metrics.json'),checkpoint=metric['checkpoint'],
                archives=archives,seconds=time.monotonic()-began)
            metrics.append(row);save(case/f'retention-{iteration:04d}.json',row)
            progress=dict(state='running',worker_pid=os.getpid(),arm=label,completed_iterations=iteration,
                latest_recovery_iteration=(iteration if due else iteration//8*8),seconds=time.monotonic()-start,
                production_modified=False)
            status(progress);print(json.dumps(progress),flush=True)
        # Restore only the final reservoir bundle. Historical checkpoints retain their own archive pointers.
        final_archive=Path(checkpoint_archives[-1]['path'])
        manifest=read(final_archive.with_suffix('.xz.json'))
        for name,data in unpack(final_archive,manifest,guard=guard).items():
            with (objects/name).open('xb') as f:f.write(data)
        restored=checkpoint.restore_checkpoint(objects,metrics[-1]['checkpoint'],config=cfg,**args)
        assert restored['next_model']==state['next_model'] and restored['played_bank']==state['played_bank']
        assert restored['root_regret_state'].document()==state['root_regret_state'].document()
        assert restored['exact_btn_state'].document()==state['exact_btn_state'].document()
        assert restored['sampler'].checkpoint()==state['sampler'].checkpoint()
        assert restored['action_rng'].bit_generator.state==state['action_rng'].bit_generator.state
        assert state['root_regret_state'].counts.sum()==39936
        result=dict(name=label,config=cfg,store=str(case),initial_checkpoint=initial,
            final_checkpoint=metrics[-1]['checkpoint'],played_bank=state['played_bank'],
            completed_iterations=78,training_deals=39936,steps=metrics,checkpoint_archives=checkpoint_archives,
            final_restore_verified=True,seconds=time.monotonic()-arm_started)
        save(case/'result.json',result);results.append(result)
        del state,restored
    for p,h in reg['inputs'].items():guard();assert sha(p)==h,p
    save(output('result'),dict(passed=True,terminal=True,registration_sha256=sha(output('registration')),
        arms=results,store=str(STORE),seconds=time.monotonic()-start,
        logical_bytes=sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()),
        production_modified=False,accuracy_qualified=False,evaluation_complete=False,
        scope='Four fixed training arms; unseen payoff evaluation and independent training readback still required.'))


def main():
    assert idle() and not LOCK.exists() and not OTHER.exists() and not STORE.exists() and not output('registration').exists()
    controls=['showdown-training-integration-control-v1','owned-research-archive-control-v1','training-cadence-control-v1']
    for prefix in controls:assert read(OUT/f'{prefix}-result.json')['passed'] and read(OUT/f'{prefix}-status.json')['state']=='complete'
    source=read(OUT/'showdown-training-integration-control-v1-result.json');arms=[]
    for seed in (9266201,9266301):
        for mode in ('baseline','corrected'):
            cfg=dict(source['config'],max_iterations=78,deals_per_iteration=512,subbatches_per_iteration=8,
                sampler_seed=seed,action_seed=seed+1,reservoir_seeds=[seed+2,seed+3],fit_seed_base=seed+4)
            if mode=='baseline':
                for key in ('showdown_root_policy','showdown_root_targets','control_coefficients_sha256'):cfg.pop(key)
            arms.append(dict(name=f'{seed}-{mode}',seed=seed,treatment=mode,config=cfg))
    inventory=measure();assert sum(r['allocated_file_bytes'] for r in inventory)+CAP+METADATA_RESERVE<=LIMIT
    inputs={str(p):sha(p) for p in (ROOT/'tools/research').glob('*.py')}
    for prefix in controls:inputs[str(OUT/f'{prefix}-result.json')]=sha(OUT/f'{prefix}-result.json')
    for p in [OUT/'showdown-root-control-coefficients-v1.json',OUT/'SHOWDOWN-MATCHED-TRAINING-PLAN.md',
              OUT/'bb-context-candidate.json',OUT/'preflop-allin-matrix-control-v1-matrix.json',
              Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')]:inputs[str(p)]=sha(p)
    for name in ('hu_sampled_allin_bridge_v3','hu_sampled_profile_allin_evaluation_v1','hu_sampled_action_trace_v2','hu_board_outcomes_v1'):
        p=ROOT/f'target/release/examples/{name}.exe';inputs[str(p)]=sha(p)
    reg=dict(inputs=inputs,arms=arms,store=str(STORE),maximum_output_bytes=CAP,maximum_seconds=SECONDS,
        storage_inventory=inventory,checkpoint_interval=8,production_modified=False,
        stopping='78 updates per arm regardless of intermediate policies; guards may stop for resource/user activity. No outcome-based selection.')
    save(output('registration'),reg)
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    child=None;error=None;start=time.monotonic()
    try:
        with (OUT/f'{PREFIX}.log').open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker'],cwd=ROOT,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                assert idle() and time.monotonic()-start<SECONDS+120
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:pass
        assert child.returncode==0,'Training stopped; preserve partial evidence and last durable checkpoint'
        assert read(output('result'))['passed']
    except BaseException as exc:error=repr(exc);raise
    finally:
        if child is not None and child.poll() is None:child.terminate();child.wait(timeout=15)
        assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()
        status(dict(state='failed' if error else 'complete',error=error,exit_code=child.returncode if child else None,
            seconds=time.monotonic()-start,production_modified=False))


if __name__=='__main__':
    if sys.argv[1:]==['--worker']:worker(read(output('registration')))
    else:
        assert sys.argv[1:]==['--run'];main()
