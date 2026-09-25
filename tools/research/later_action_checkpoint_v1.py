"""Version-7 envelope keeps postflop integrated targets distinct from old trials."""
import hashlib
import json
import action_integrated_checkpoint_v1 as parent
import sampled_visible_hybrid_checkpoint_v1 as base
from later_action_training_ingest_v1 import METHOD

POLICY_TYPE='visible-hybrid-exact-initial-postflop-action-integrated-v1'
CONFIG_KEY='later_action_policy'
FIT_IMPLEMENTATION='ordered-cuda-gradient-graph-v1'


def require_config(config):
    parent.require_config(config)
    if (config.get(CONFIG_KEY)!=POLICY_TYPE or config.get('postflop_learning_targets')!=METHOD
            or config.get('fit_implementation')!=FIT_IMPLEMENTATION or config.get('device')!='cuda'):
        raise ValueError('Explicit postflop target estimator and qualified CUDA fitter required')


def inner_model(value,**args):
    if (value.get('format')!=7 or value.get('policy_type')!=POLICY_TYPE
            or value.get('postflop_learning_targets')!=METHOD
            or value.get('fit_implementation')!=FIT_IMPLEMENTATION):
        raise ValueError('Explicit version-7 later-action model required')
    inner={k:v for k,v in value.items() if k not in ('postflop_learning_targets','fit_implementation')}
    inner.update(format=6,policy_type=parent.POLICY_TYPE)
    parent.validate_model(inner,**args)
    return inner


def write_model(directory,exact_document,root_state,**args):
    ref=parent.write_model(directory,exact_document,root_state,**args)
    inner=parent.model_document(directory,ref,**args)
    value=dict(inner,format=7,policy_type=POLICY_TYPE,
        postflop_learning_targets=METHOD,fit_implementation=FIT_IMPLEMENTATION)
    inner_model(value,**args)
    ref=base.publish(directory,'lateractionmodel',base.encoded(value))
    return dict(ref,generation=value['generation'])


def model_document(directory,reference,**args):
    value=json.loads(base.read_object(directory,reference));inner_model(value,**args)
    if value['generation']!=reference['generation']:raise ValueError('Later-action generation mismatch')
    return value


def convert_bank(directory,completed,bank,current,**args):
    if type(completed) is not int or completed<0 or len(bank)!=completed:
        raise ValueError('Complete played history required')
    docs=[];refs=[]
    for generation,ref in enumerate([*bank,current]):
        doc=model_document(directory,ref,**args)
        if doc['generation']!=generation:raise ValueError('Played generations out of order')
        inner=inner_model(doc,**args);docs.append(doc)
        published=base.publish(directory,'integratedrootmodel',base.encoded(inner))
        refs.append(dict(published,generation=generation))
    return docs,refs


def save_checkpoint(directory,*,completed,context_source,config,sampler,action_rng,reservoirs,
                    bank,current,catalog_source,matrix_sha256,entry_mass):
    require_config(config)
    args=dict(context_source=context_source,catalog_source=catalog_source,
        matrix_sha256=matrix_sha256,entry_mass=entry_mass)
    _,refs=convert_bank(directory,completed,bank,current,**args)
    nested=parent.save_checkpoint(directory,completed=completed,config=config,sampler=sampler,
        action_rng=action_rng,reservoirs=reservoirs,bank=refs[:-1],current=refs[-1],**args)
    value=dict(format=7,policy_type=POLICY_TYPE,completed_iterations=completed,
        context_sha256=base.digest(context_source),catalog_sha256=base.digest(catalog_source),
        matrix_sha256=matrix_sha256,config_sha256=hashlib.sha256(base.encoded(config)).hexdigest(),
        postflop_learning_targets=METHOD,fit_implementation=FIT_IMPLEMENTATION,
        action_integrated_checkpoint=nested,played_bank=bank,next_model=current)
    return base.publish(directory,'lateractioncheckpoint',base.encoded(value))


def restore_checkpoint(directory,reference,*,context_source,config,catalog_source,matrix_sha256,
                       entry_mass,manifest_source=None):
    require_config(config);value=json.loads(base.read_object(directory,reference))
    if (value.get('format')!=7 or value.get('policy_type')!=POLICY_TYPE
            or value.get('postflop_learning_targets')!=METHOD or value.get('fit_implementation')!=FIT_IMPLEMENTATION
            or value['context_sha256']!=base.digest(context_source)
            or value['catalog_sha256']!=base.digest(catalog_source) or value['matrix_sha256']!=matrix_sha256
            or value['config_sha256']!=hashlib.sha256(base.encoded(config)).hexdigest()):
        raise ValueError('Wrong later-action checkpoint identity')
    args=dict(context_source=context_source,catalog_source=catalog_source,
        matrix_sha256=matrix_sha256,entry_mass=entry_mass)
    # Restore is read-only: validate nested references without publishing objects.
    docs=[]
    if len(value['played_bank'])!=value['completed_iterations']:raise ValueError('Incomplete played bank')
    for generation,ref in enumerate([*value['played_bank'],value['next_model']]):
        doc=model_document(directory,ref,**args)
        if doc['generation']!=generation:raise ValueError('Played history order changed')
        docs.append(doc)
    state=parent.restore_checkpoint(directory,value['action_integrated_checkpoint'],
        config=config,manifest_source=manifest_source,**args)
    if state['completed_iterations']!=value['completed_iterations']:raise ValueError('Nested update count mismatch')
    for ref,doc in zip([*state['played_bank'],state['next_model']],docs):
        if base.encoded(parent.model_document(directory,ref,**args))!=base.encoded(inner_model(doc,**args)):
            raise ValueError('Nested model differs from typed later-action history')
    state.update(played_bank=value['played_bank'],next_model=value['next_model'],next_model_document=docs[-1])
    return state
