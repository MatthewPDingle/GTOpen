"""Admit only the complete independently audited played board-root histories."""
from pathlib import Path
import numpy as np
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import sha
import board_training_checkpoint_v1 as checkpoint


def load_bank(label,*,bank_args,guard):
    registration=OUT/'board-root-matched-continuation-v1-registration.json'
    result_path=OUT/'board-root-matched-continuation-v1-result.json'
    audit_path=OUT/'board-matched-complete-readback-v1-result.json'
    audit_reg_path=OUT/'board-matched-complete-readback-v1-registration.json'
    reg=read(registration);result=read(result_path);audit=read(audit_path);audit_reg=read(audit_reg_path)
    if (not result['passed'] or not result['training_complete'] or result['registration_sha256']!=sha(registration)
            or reg['generations_per_arm']!=78 or result['generations_per_arm']!=78
            or reg['store']!=str(Path('S:/GTOpen-research/board-root-matched-prefix-v1'))):
        raise ValueError('Complete registered 78-generation board-root training required')
    if (not audit['passed'] or not audit['complete_training'] or audit['registration_sha256']!=sha(audit_reg_path)
            or audit['source_result_sha256']!=sha(result_path)):
        raise ValueError('Matching complete independent readback required')
    for p,h in reg['inputs'].items():
        guard()
        if sha(p)!=h:raise ValueError('Registered training source changed: '+p)
    # Raw native evidence was checked by the complete audit. Recheck its code,
    # actual played models and metric chain here, not every old raw batch again.
    for p,h in audit_reg['inputs'].items():
        if Path(p).suffix=='.py':
            guard()
            if sha(p)!=h:raise ValueError('Audited implementation changed: '+p)
    def one(rows,key):
        found=[r for r in rows if r[key]==label]
        if len(found)!=1:raise ValueError('Unknown or duplicate board-root arm')
        return found[0]
    arm=one(reg['arms'],'name');endpoint=one(result['arms'],'arm')
    checked=one(audit['arms'],'arm');job=one(audit_reg['jobs'],'name')
    folder=Path(reg['store'])/label;objects=folder/'objects';pp=Path(endpoint['progress_path'])
    if (pp!=folder/'continuation-progress.json' or sha(pp)!=endpoint['progress_sha256']
            or audit_reg['inputs'][str(pp)]!=sha(pp) or job['objects']!=str(objects)
            or job['cfg']!=arm['config'] or checked['generations']!=78
            or checked['boards_checked']!=312 or checked['physical_roots_checked']!=39936
            or checked['final_checkpoint']!=endpoint['checkpoint']):
        raise ValueError('Endpoint differs from independently audited arm')
    progress=read(pp)
    if (progress['registration_sha256']!=sha(registration) or progress['completed']!=78
            or endpoint['completed']!=78 or progress['generations']!=job['generations']
            or len(progress['generations'])!=78 or progress['checkpoint']!=endpoint['checkpoint']):
        raise ValueError('Incomplete or changed played history')
    references=[];previous=None
    for generation,row in enumerate(progress['generations']):
        guard();path=Path(row['path'])
        if (path.resolve()!=path or path.parent.parent!=folder or path.name!='metrics.json'
                or sha(path)!=row['sha256'] or audit_reg['inputs'][str(path)]!=row['sha256']):
            raise ValueError('Audited metrics changed')
        metric=read(path)
        if (metric['iteration']!=generation+1 or metric['used_model']['generation']!=generation
                or metric['next_model']['generation']!=generation+1
                or (previous is not None and previous!=metric['used_model'])):
            raise ValueError('Played model chain changed')
        references.append(metric['used_model']);previous=metric['next_model']
    if metric['checkpoint']!=endpoint['checkpoint']:raise ValueError('Final checkpoint differs from history')
    args=dict(bank_args,root_config=arm['config']['board_root'])
    state=checkpoint.restore_checkpoint(objects,endpoint['checkpoint'],arm['config'],**args)
    if state['completed_iterations']!=78 or state['played_bank']!=references or state['next_model']!=previous:
        raise ValueError('Checkpoint and played model history differ')
    documents=[]
    for generation,reference in enumerate(references):
        guard();model=checkpoint.model_document(objects,reference,**args)
        if model['generation']!=generation or model['board_root_state']['board_draws']!=4*generation:
            raise ValueError('Wrong board-root model generation')
        documents.append(model)
    weights=np.tile(np.arange(1.,79.),(2,1))
    identity=dict(arm=label,completed_iterations=78,model_references=references,checkpoint=endpoint['checkpoint'],
        unplayed_excluded=previous,root_config=arm['config']['board_root'],
        training_registration_sha256=sha(registration),training_result_sha256=sha(result_path),
        independent_audit_sha256=sha(audit_path),independent_registration_sha256=sha(audit_reg_path),
        averaging='played generations 0-77; weights 1-78; own-action reach',purpose='evaluation',accuracy_qualified=False)
    return documents,weights,identity
