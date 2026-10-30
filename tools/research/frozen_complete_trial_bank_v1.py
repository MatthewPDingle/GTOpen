"""Load an independently audited, complete played history for evaluation.

The version-7 adapter changes representation only. Never include the unplayed
last model, choose a checkpoint by its ranges, or accept incomplete training.
"""
import json
from pathlib import Path
import numpy as np
from sampled_physical_root_evaluation_v1 import sha
from action_integrated_checkpoint_v1 import restore_checkpoint as restore_old, model_document as old_document
from later_action_checkpoint_v1 import restore_checkpoint as restore_new, model_document as new_document, inner_model


def load_completed_trial(out, prefix, *, expected_updates, bank_args, guard):
    if type(expected_updates) is not int or expected_updates < 1:
        raise ValueError('Explicit complete training count required')
    out=Path(out)
    paths={key:out/f'{prefix}-{key}.json' for key in ('registration','result','independent-review','readback-registration')}
    docs={key:json.loads(path.read_text()) for key,path in paths.items()}
    reg,result,audit,readback=(docs[k] for k in paths)
    if not (result['passed'] and result['terminal'] and audit['passed']
            and result['completed_iterations']==audit['completed_updates']==expected_updates
            and result['registration_sha256']==audit['source_registration_sha256']==sha(paths['registration'])
            and audit['source_result_sha256']==sha(paths['result'])
            and audit['readback_registration_sha256']==sha(paths['readback-registration'])):
        raise ValueError('Completed trial and independent readback identities required')
    if not all(result['config'][k]==v for k,v in reg['config'].items()):
        raise ValueError('Training configuration changed')
    if result['config']['max_iterations']!=expected_updates or result['store']!=reg['store']:
        raise ValueError('Count or store mismatch')
    # Freeze code identities as well as training metadata. Object readers below
    # independently authenticate the referenced checkpoint, tensors and models.
    dependencies=dict(reg['inputs'])
    dependencies.update({p:h for p,h in readback['inputs'].items()
                         if Path(p).suffix in ('.py','.rs','.exe')})
    # Raw training batches already have an authenticated audit and are not
    # consumed for inference. Do not reread tens of GB of them for each bank.
    for path,digest in dependencies.items():
        guard()
        if sha(path)!=digest: raise ValueError('Frozen dependency changed: '+path)
    objects=Path(reg['store'])/'objects'
    newer='later_action_policy' in result['config']
    restore,document=(restore_new,new_document) if newer else (restore_old,old_document)
    guard(); state=restore(objects,result['final_checkpoint'],config=result['config'],**bank_args)
    if state['completed_iterations']!=expected_updates or len(state['played_bank'])!=expected_updates:
        raise ValueError('Complete played history missing')
    models=[]
    for generation,reference in enumerate(state['played_bank']):
        guard(); model=document(objects,reference,**bank_args)
        if model['generation']!=generation: raise ValueError('Played generation order changed')
        models.append(inner_model(model,**bank_args) if newer else model)
    next_model=document(objects,state['next_model'],**bank_args)
    if next_model['generation']!=expected_updates: raise ValueError('Unplayed generation mismatch')
    weights=np.tile(np.arange(1,expected_updates+1,dtype=np.float64),(2,1))
    identity=dict(prefix=prefix,checkpoint=result['final_checkpoint'],
        registration_sha256=sha(paths['registration']),result_sha256=sha(paths['result']),
        audit_sha256=sha(paths['independent-review']),played_generations=list(range(expected_updates)),
        excluded_generation=expected_updates,weights=weights.tolist(),
        version7_adaptation=newer,production_modified=False)
    return models,weights,identity
