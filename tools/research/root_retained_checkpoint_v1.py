"""Version-5 research envelope: exact BTN plus all sampled BB root regrets.

The nested v4 checkpoint retains its original reservoirs and tables for audit.
Only readers of this new envelope apply the separately typed root override.
"""
import hashlib
import json
from sampled_root_regret_accumulator_v1 import SampledRootRegrets
from sampled_root_policy_table_v1 import SampledRootTable, document as root_document
import exact_initial_hybrid_checkpoint_v1 as exact
import sampled_visible_hybrid_checkpoint_v1 as base

POLICY_TYPE = 'visible-hybrid-exact-btn-all-sampled-bb-root-v1'
CONFIG_KEY = 'root_regret_policy'


def require_config(config):
    exact.require_config(config)
    if config.get(CONFIG_KEY) != POLICY_TYPE:
        raise ValueError('Explicit all-sampled root policy configuration required')


def validate_model(value, context_source, catalog_source, matrix_sha256, entry_mass):
    if value.get('format') != 5 or value.get('policy_type') != POLICY_TYPE:
        raise ValueError('Explicit version-5 root-retained model required')
    if value.get('context_sha256') != base.digest(context_source):
        raise ValueError('Root-retained context changed')
    exact.validate_model(value['exact_model'],context_source,catalog_source,matrix_sha256,entry_mass)
    if type(value['generation']) is not int or value['generation'] != value['exact_model']['generation']:
        raise ValueError('Nested model generation mismatch')
    table = SampledRootTable(value['sampled_root'],context_source,catalog_source,matrix_sha256=matrix_sha256)
    if table.completed_updates != value['generation']:
        raise ValueError('One root accumulation per completed generation required')
    return table


def write_model(directory, exact_document, root_state, *, context_source,
                catalog_source, matrix_sha256, entry_mass):
    value = dict(format=5,policy_type=POLICY_TYPE,context_sha256=base.digest(context_source),
        generation=exact_document['generation'],exact_model=exact_document,
        sampled_root=root_document(root_state,context_source=context_source,catalog_source=catalog_source))
    validate_model(value,context_source,catalog_source,matrix_sha256,entry_mass)
    ref = base.publish(directory,'rootmodel',base.encoded(value))
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
        total = sum(d['sampled_root']['state']['sample_counts'])
        if total != d['generation']*config['subbatches_per_iteration']*config['deals_per_subbatch']:
            raise ValueError('Root sample count differs from completed generation budget')
        ref = base.publish(directory,'exactmodel',base.encoded(d['exact_model']))
        refs.append(dict(ref,generation=d['generation']))
    inner = exact.save_checkpoint(directory,completed=completed,config=config,sampler=sampler,
        action_rng=action_rng,reservoirs=reservoirs,bank=refs[:-1],current=refs[-1],**args)
    value = dict(format=5,policy_type=POLICY_TYPE,completed_iterations=completed,
        context_sha256=base.digest(context_source),catalog_sha256=base.digest(catalog_source),
        matrix_sha256=matrix_sha256,config_sha256=hashlib.sha256(base.encoded(config)).hexdigest(),
        exact_checkpoint=inner,played_bank=bank,next_model=current,
        root_state_location='next_model.sampled_root.state; all corrected root samples exactly once',
        averaging='Complete ordered played generations only; final unplayed model excluded')
    return base.publish(directory,'rootcheckpoint',base.encoded(value))


def restore_checkpoint(directory, reference, *, context_source, config,
                       catalog_source, matrix_sha256, entry_mass, manifest_source=None):
    require_config(config)
    value = json.loads(base.read_object(directory,reference))
    if (value.get('format') != 5 or value.get('policy_type') != POLICY_TYPE
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
        if sum(d['sampled_root']['state']['sample_counts']) != d['generation']*config['subbatches_per_iteration']*config['deals_per_subbatch']:
            raise ValueError('Restored root count differs from generation budget')
    root = SampledRootRegrets.restore(docs[-1]['sampled_root']['state'],
        context_sha256=base.digest(context_source),matrix_sha256=matrix_sha256)
    restored.update(played_bank=value['played_bank'],next_model=value['next_model'],
        next_model_document=docs[-1],root_regret_state=root)
    return restored
