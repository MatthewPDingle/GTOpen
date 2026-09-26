"""Show that checkpoint cadence and compact transports leave training unchanged."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
from pathlib import Path
import sys
import time
import uuid
from hu_paired_continuation_support_20260925 import launch,guard_for,setup_cuda
from hu_action_integrated_exact_20260925 import bank_args
from later_average_support_v1 import OUT,read,load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from owned_research_archive_v1 import pack,unpack,retire
import later_action_training_v1 as baseline
import later_action_cadence_training_v1 as sparse_baseline
import showdown_cadence_training_v1 as sparse_treatment
import later_action_checkpoint_v1 as baseline_checkpoint
import showdown_root_checkpoint_v1 as treatment_checkpoint

PREFIX='training-cadence-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def worker(reg):
    setup_cuda();guard=guard_for(reg);guard();started=time.monotonic()
    source=read(OUT/'showdown-training-integration-control-v1-result.json')
    cfg=source['config'];STORE.mkdir();token=uuid.uuid4().hex
    save(STORE/'archive-owner.json',dict(format=1,token=token,purpose='new-research-scratch-v1'))
    cp=OUT/'bb-context-candidate.json';args=bank_args(cp.read_text());cache=load_complete_cache()
    step=dict(context_path=cp,catalog_source=args['catalog_source'],matrix_sha256=args['matrix_sha256'],
        matrix_source=(OUT/'preflop-allin-matrix-control-v1-matrix.json').read_text(),cache=cache,
        executable=ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe',
        integration_executable=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe',
        trace_executable=ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe',
        batch_prefix='showdown-training-integration-control-v1',guard=guard)
    results={}
    for name,module,checkpoints in [('baseline_every_update',baseline,baseline_checkpoint),
                                   ('baseline_sparse',sparse_baseline,baseline_checkpoint),
                                   ('treatment_sparse',sparse_treatment,treatment_checkpoint)]:
        case=STORE/name;case.mkdir();objects=case/'objects';objects.mkdir()
        config=dict(cfg)
        if name!='treatment_sparse':
            for k in ('showdown_root_policy','showdown_root_targets','control_coefficients_sha256'):config.pop(k)
        state=module.initialize(objects,config,**args);initial=module.save_state(objects,state,config,**args)
        archives=[];metrics=[]
        for iteration in (1,2):
            guard();kwargs=dict(step)
            if name!='baseline_every_update':kwargs['checkpoint_due']=iteration==2
            if name=='treatment_sparse':
                kwargs.update(coefficients=read(OUT/'showdown-root-control-coefficients-v1.json'),
                    score_executable=ROOT/'target/release/examples/hu_board_outcomes_v1.exe')
            folder=case/f'iteration-{iteration:04d}'
            metric=module.update(folder,objects,state,config,**kwargs);metrics.append(metric)
            if iteration==1 and name!='baseline_every_update':assert metric['checkpoint'] is None
            part=folder/'batch-00';archive=case/f'batch-{iteration:04d}.xz'
            manifest=pack(part,[p.name for p in part.iterdir() if p.is_file()],archive,root=STORE,token=token,guard=guard)
            original=unpack(archive,manifest,guard=guard)
            for key,data in original.items():assert data==(part/key).read_bytes()
            retire(part,archive,manifest,root=STORE,token=token,guard=guard)
            archives.append(dict(path=str(archive),manifest=manifest))
        restored=checkpoints.restore_checkpoint(objects,metrics[-1]['checkpoint'],config=config,**args)
        assert restored['next_model']==state['next_model'] and restored['completed_iterations']==2
        result=dict(final_checkpoint=metrics[-1]['checkpoint'],next_model=state['next_model'],
            root_state=state['root_regret_state'].document(),exact_state=state['exact_btn_state'].document(),
            archive=archives,metrics=metrics,initial_checkpoint=initial)
        if name=='baseline_sparse':
            prior=results['baseline_every_update']
            for k in ('final_checkpoint','next_model','root_state','exact_state'):assert result[k]==prior[k],k
            for a,b in zip(archives,prior['archive']):
                assert unpack(a['path'],a['manifest'],guard=guard)==unpack(b['path'],b['manifest'],guard=guard)
        if name=='treatment_sparse':
            assert result['final_checkpoint']==source['final_checkpoint']
            for iteration,a in enumerate(archives,1):
                for key,data in unpack(a['path'],a['manifest'],guard=guard).items():
                    old=Path(source['store'])/f'iteration-{iteration:04d}'/'batch-00'/key
                    assert sha(old)==source['artifacts'][str(old)] and data==old.read_bytes()
        results[name]=result
        print(name+' exact-state and archive checks passed',flush=True)
    for p,h in reg['inputs'].items():guard();assert sha(p)==h,p
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,terminal=True,
        registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),store=str(STORE),results=results,
        checkpoint_cadence_preserves_baseline_and_treatment=True,transports_byte_identical=True,
        evidence_archive_survives_raw_retirement=True,seconds=time.monotonic()-started,
        artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
        production_modified=False,accuracy_qualified=False))


if __name__=='__main__':
    if sys.argv[1:]==['--worker']:worker(read(OUT/f'{PREFIX}-registration.json'))
    else:
        assert sys.argv[1:]==['--run']
        p=OUT/'owned-research-archive-control-v1-result.json';assert read(p)['passed']
        launch(Path(__file__).resolve(),PREFIX,dict(extra_inputs=[str(p)],store=str(STORE),
            scope='Baseline and treatment save-cadence equivalence with lossless raw-transport retirement'),cap=150_000_000,seconds=1200)
