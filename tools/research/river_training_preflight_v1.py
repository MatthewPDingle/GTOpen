"""Read-only source-boundary validation for the next matched river-target pilot."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import ast,copy,gc,hashlib,json,sys,time
from pathlib import Path
import psutil
import board_training_checkpoint_v1 as checkpoint
from preflop_allin_matrix_v1 import AllinMatrix
from river_weighted_overlay_ingest_v1 import METHOD
from bounded_parallel_evaluation_archive_v2 import production_available
from sampled_physical_root_evaluation_v1 import save

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
DEST=OUT/'river-training-preflight-v1.json'
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pipeline_diff():
    original=(ROOT/'tools/research/board_training_pipeline_v1.py').read_text()
    candidate=(ROOT/'tools/research/river_training_pipeline_v1.py').read_text()
    # Reverse the explicit plumbing changes; the rest of the AST must be identical.
    candidate=candidate.replace('"""Research river overlay with unchanged joint board-root checkpoint semantics."""','"""Transactional board-root pipeline; GPU integration control still required."""')
    candidate=candidate.replace('from river_training_workers_v1 import pool,complete,commit\nfrom river_weighted_overlay_ingest_v1 import METHOD','from weighted_training_workers_v1 import pool,complete,commit')
    candidate=candidate.replace('physical_catalog_source,board_executable,board_workers,river_executable,on_stage=lambda stage:None):','physical_catalog_source,board_executable,on_stage=lambda stage:None):')
    candidate=candidate.replace('physical_catalog_source,board_executable,on_stage=lambda stage:None):','physical_catalog_source,board_executable,board_workers,on_stage=lambda stage:None):')
    candidate=candidate.replace("    if config.get('river_targets')!={'method':METHOD,'K':64}:\n        raise ValueError('Explicit posterior64 research configuration required')\n",'')
    candidate=candidate.replace("    river_payload=dict(model_source=storage.read_object(objects,used).decode(),policy_id=used['sha256'],\n                       model_args={k:v for k,v in args.items() if k!='context_source'})\n",'')
    candidate=candidate.replace('ordered_insertion=0.,river_targets=0.)','ordered_insertion=0.)')
    candidate=candidate.replace("subbatches.append(dict(chunk=chunk,counts=result['counts'],coverage=cov,artifacts=result['artifacts'],river=result['river']))","subbatches.append(dict(chunk=chunk,counts=result['counts'],coverage=cov,artifacts=result['artifacts']))")
    candidate=candidate.replace('executable=executable,trace_executable=trace_executable,integration_executable=integration_executable,\n                  river_payload=river_payload,river_executable=river_executable) as executor:','executable=executable,trace_executable=trace_executable,integration_executable=integration_executable) as executor:')
    candidate=candidate.replace("fit_runtime='ordered-weighted-cuda-gradient-graph-v2',river_targets=config['river_targets'],","fit_runtime='ordered-weighted-cuda-gradient-graph-v2',")
    assert ast.dump(ast.parse(candidate))==ast.dump(ast.parse(original)),'Unexpected pipeline change'

def main():
    assert not DEST.exists();began=time.monotonic();assert production_available()
    assert psutil.virtual_memory().available>24_000_000_000
    pipeline_diff()
    training=OUT/'board-root-matched-continuation-v1-registration.json';terminal=OUT/'board-root-matched-continuation-v1-result.json'
    auditpath=OUT/'board-matched-complete-readback-v1-result.json';auditreg=OUT/'board-matched-complete-readback-v1-registration.json'
    reg,end,audit=read(training),read(terminal),read(auditpath)
    assert end['passed'] and end['training_complete'] and end['registration_sha256']==sha(training)
    assert audit['passed'] and audit['complete_training'] and audit['registration_sha256']==sha(auditreg)
    assert audit['source_result_sha256']==sha(terminal)
    check=OUT/'river-training-workers-control-v1-result.json';checkreg=OUT/'river-training-workers-control-v1-registration.json'
    done=read(check);assert done['passed'] and done['registration_sha256']==sha(checkreg)
    for p,h in read(checkreg)['inputs'].items():assert sha(p)==h,p
    for case in done['cases']:
        folder=OUT/'river-training-workers-control-v1'/case['case']
        assert read(folder/'result.json')==case
        for p,h in case['artifacts'].items():assert sha(folder/p)==h,p
    context=OUT/'bb-context-candidate.json';matrixpath=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    catpath=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    source=context.read_text();matrix=AllinMatrix(read(matrixpath),source)
    paths=[Path(__file__),training,terminal,auditpath,auditreg,check,checkreg,context,matrixpath,catpath,
           ROOT/'tools/research/river_training_workers_v1.py',ROOT/'tools/research/river_training_pipeline_v1.py']
    records=[]
    for arm,ending,checked in zip(reg['arms'],end['arms'],audit['arms']):
        assert production_available();folder=Path(reg['store'])/arm['name'];objects=folder/'objects';cfg=arm['config']
        assert arm['name']==ending['arm']==checked['arm'] and checked['generations']==ending['completed']==78
        assert checked['final_checkpoint']==ending['checkpoint']
        pp=Path(ending['progress_path']);assert sha(pp)==ending['progress_sha256'];progress=read(pp)
        ref=progress['checkpoint'];assert ref==ending['checkpoint']
        cp=objects/ref['file'];assert sha(cp)==ref['sha256'];doc=read(cp)
        args=dict(context_source=source,catalog_source=catpath.read_text(),matrix_sha256=sha(matrixpath),entry_mass=matrix.btn_mass,root_config=cfg['board_root'])
        state=checkpoint.restore_checkpoint(objects,ref,cfg,**args)
        assert state['completed_iterations']==78 and state['next_model']['generation']==78 and state['played_bank'][-1]['generation']==77
        candidate_cfg=dict(cfg,river_targets=dict(method=METHOD,K=64))
        assert {k for k in set(candidate_cfg)|set(cfg) if candidate_cfg.get(k)!=cfg.get(k)}=={'river_targets'}
        checkpoint.validate_state(objects,state,candidate_cfg,**args)
        required=[cp,*[objects[r['file']] for r in [*doc['played_bank'],doc['next_model'],*doc['reservoirs']]]
        paths.extend([pp,*required]);size=sum(p.stat().st_size for p in required)
        records.append(dict(arm=arm['name'],objects=str(objects),source_checkpoint=ref,completed=78,last_played=77,next_model=state['next_model'],
                            configuration_sha256=doc['config_sha256'],candidate_config=candidate_cfg,required_copy_bytes_per_arm=size,
                            reservoirs=[r.summary() for r in state['reservoirs']],sampler=state['sampler'].checkpoint(),
                            state_restored=True,full_played_bank_validated=True,candidate_config_validated=True))
        del state;gc.collect()
    inputs={str(p):sha(p) for p in paths}
    save(DEST,dict(passed=True,read_only=True,arms=records,inputs=inputs,worker_result_sha256=sha(check),
                  unchanged_core_pipeline_ast=True,seconds=time.monotonic()-began,gpu_used=False,training_started=False,
                  scope='Verified source boundary and integration only. Matched GPU training, restart replay and fresh policy evaluation remain pending.'))
    print(json.dumps(dict(passed=True,arms=2,completed_boundary=78,copy_bytes_four_arms=2*sum(r['required_copy_bytes_per_arm'] for r in records),seconds=time.monotonic()-began)),flush=True)
if __name__=='__main__':main()
