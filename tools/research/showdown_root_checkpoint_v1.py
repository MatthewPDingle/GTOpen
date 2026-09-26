"""Version-8 research envelope: exact BTN plus showdown-controlled BB root regrets.

The nested v4 checkpoint retains its original reservoirs and tables for audit.
Only readers of this new envelope apply the separately typed root override.
"""
import hashlib
import json
from showdown_root_accumulator_v1 import ShowdownRootRegrets
from showdown_root_table_v1 import ShowdownRootTable, document as root_document
import exact_initial_hybrid_checkpoint_v1 as exact
import sampled_visible_hybrid_checkpoint_v1 as base

POLICY_TYPE = 'visible-hybrid-postflop-showdown-controlled-root-v1'
CONFIG_KEY = 'showdown_root_policy'


def require_config(config):
    from later_action_checkpoint_v1 import require_config as require_later
    from action_integrated_root_accumulator_v1 import identity
    require_later(config)
    if config.get(CONFIG_KEY) != POLICY_TYPE or config.get('showdown_root_targets') != 'showdown-controlled-bb-root-targets-v1':
        raise ValueError('Explicit showdown root training configuration required')
    identity(config.get('control_coefficients_sha256'))


def validate_model(value, context_source, catalog_source, matrix_sha256, entry_mass):
    if value.get('format') != 8 or value.get('policy_type') != POLICY_TYPE:
        raise ValueError('Explicit version-8 showdown-controlled model required')
    if value.get('context_sha256') != base.digest(context_source):
        raise ValueError('Action-integrated context changed')
    exact.validate_model(value['exact_model'],context_source,catalog_source,matrix_sha256,entry_mass)
    if type(value['generation']) is not int or value['generation'] != value['exact_model']['generation']:
        raise ValueError('Nested model generation mismatch')
    table = ShowdownRootTable(value['integrated_root'],context_source,catalog_source,matrix_sha256=matrix_sha256)
    if table.completed_updates != value['generation']:
        raise ValueError('One root accumulation per completed generation required')
    return table


def write_model(directory, exact_document, root_state, *, context_source,
                catalog_source, matrix_sha256, entry_mass):
    value = dict(format=8,policy_type=POLICY_TYPE,context_sha256=base.digest(context_source),
        generation=exact_document['generation'],exact_model=exact_document,
        integrated_root=root_document(root_state,context_source=context_source,catalog_source=catalog_source))
    validate_model(value,context_source,catalog_source,matrix_sha256,entry_mass)
    ref = base.publish(directory,'showdownrootmodel',base.encoded(value))
    return dict(ref,generation=value['generation'])


def model_document(directory, reference, *, context_source, catalog_source,
                   matrix_sha256, entry_mass):
    value = json.loads(base.read_object(directory,reference))
    validate_model(value,context_source,catalog_source,matrix_sha256,entry_mass)
    if value['generation'] != reference['generation']:
        raise ValueError('Root model reference generation mismatch')
    return value


def verify_bank(directory,completed,bank,current,**args):
    if type(completed) is not int or completed < 0 or len(bank) != completed:
        raise ValueError('Complete ordered root played bank required')
    docs = []
    for generation,ref in enumerate([*bank,current]):
        if type(ref['generation']) is not int or ref['generation'] != generation:
            raise ValueError('Root played bank ordering changed')
        docs.append(model_document(directory,ref,**args))
    return docs


def save_checkpoint(directory, *, completed, context_source, config, sampler,
                    action_rng, reservoirs, bank, current, catalog_source,
                    matrix_sha256, entry_mass):
    require_config(config)
    args = dict(context_source=context_source,catalog_source=catalog_source,
                matrix_sha256=matrix_sha256,entry_mass=entry_mass)
    docs = verify_bank(directory,completed,bank,current,**args)
    refs = []
    for d in docs:
        if d['integrated_root']['coefficients_sha256'] != config['control_coefficients_sha256']:
            raise ValueError('Model coefficients differ from training configuration')
        total = sum(d['integrated_root']['state']['sample_counts'])
        if total != d['generation']*config['subbatches_per_iteration']*config['deals_per_subbatch']:
            raise ValueError('Root sample count differs from completed generation budget')
        ref = base.publish(directory,'exactmodel',base.encoded(d['exact_model']))
        refs.append(dict(ref,generation=d['generation']))
    inner = exact.save_checkpoint(directory,completed=completed,config=config,sampler=sampler,
        action_rng=action_rng,reservoirs=reservoirs,bank=refs[:-1],current=refs[-1],**args)
    value = dict(format=8,policy_type=POLICY_TYPE,completed_iterations=completed,
        context_sha256=base.digest(context_source),catalog_sha256=base.digest(catalog_source),
        matrix_sha256=matrix_sha256,config_sha256=hashlib.sha256(base.encoded(config)).hexdigest(),
        exact_checkpoint=inner,played_bank=bank,next_model=current,
        root_state_location='next_model.integrated_root.state; all integrated root samples exactly once',
        averaging='Complete ordered played generations only; final unplayed model excluded')
    return base.publish(directory,'showdownrootcheckpoint',base.encoded(value))


def restore_checkpoint(directory, reference, *, context_source, config,
                       catalog_source, matrix_sha256, entry_mass, manifest_source=None):
    require_config(config)
    value = json.loads(base.read_object(directory,reference))
    if (value.get('format') != 8 or value.get('policy_type') != POLICY_TYPE
            or value['context_sha256'] != base.digest(context_source)
            or value['catalog_sha256'] != base.digest(catalog_source)
            or value['matrix_sha256'] != matrix_sha256
            or value['config_sha256'] != hashlib.sha256(base.encoded(config)).hexdigest()):
        raise ValueError('Root checkpoint identity or configuration changed')
    args = dict(context_source=context_source,catalog_source=catalog_source,
                matrix_sha256=matrix_sha256,entry_mass=entry_mass)
    completed = value['completed_iterations']
    docs = verify_bank(directory,completed,value['played_bank'],value['next_model'],**args)
    restored = exact.restore_checkpoint(directory,value['exact_checkpoint'],config=config,
        manifest_source=manifest_source,**args)
    if restored['completed_iterations'] != completed:
        raise ValueError('Nested checkpoint iteration mismatch')
    for ref,d in zip([*restored['played_bank'],restored['next_model']],docs):
        nested = exact.model_document(directory,ref,**args)
        if base.encoded(nested) != base.encoded(d['exact_model']):
            raise ValueError('Root and nested histories differ')
        if d['integrated_root']['coefficients_sha256'] != config['control_coefficients_sha256']:
            raise ValueError('Restored model coefficients differ from configuration')
        if sum(d['integrated_root']['state']['sample_counts']) != d['generation']*config['subbatches_per_iteration']*config['deals_per_subbatch']:
            raise ValueError('Restored root count differs from generation budget')
    root = ShowdownRootRegrets.restore(docs[-1]['integrated_root']['state'],
        context_sha256=base.digest(context_source),matrix_sha256=matrix_sha256,
        coefficients_sha256=config['control_coefficients_sha256'])
    restored.update(played_bank=value['played_bank'],next_model=value['next_model'],
        next_model_document=docs[-1],root_regret_state=root)
    return restored
