"""Version-4 model/checkpoint envelope with separately typed exact BTN state.

The nested version-3 policy still describes the retained-sample/network base.
Its first-response probabilities must be overridden before use or averaging.
Older readers reject the envelope rather than silently ignoring the override.
"""
import json
import hashlib
from pathlib import Path
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from exact_btn_policy_table_v1 import ExactBtnTable, document as table_document
import sampled_visible_hybrid_checkpoint_v1 as base

POLICY_TYPE = 'visible-hybrid-with-exact-initial-btn-response-v1'
CONFIG_KEY = 'exact_initial_response_policy'


def validate_model(value, context_source, catalog_source, matrix_sha256, entry_mass):
    if value.get('format') != 4 or value.get('policy_type') != POLICY_TYPE:
        raise ValueError('Explicit exact-initial hybrid model required')
    if value.get('context_sha256') != base.digest(context_source):
        raise ValueError('Exact-initial model context changed')
    inner = value['base_model']
    base.validate_model(inner, context_source)
    if type(value['generation']) is not int or value['generation'] != inner['generation']:
        raise ValueError('Base and exact model generations differ')
    table = ExactBtnTable(value['exact_btn'], context_source, catalog_source,
                         matrix_sha256=matrix_sha256, entry_mass=entry_mass)
    if table.completed_updates != value['generation']:
        raise ValueError('One exact update per completed generation required')
    return table


def write_model(directory, base_document, exact_state, *, context_source,
                catalog_source, matrix_sha256, entry_mass):
    value = dict(format=4, policy_type=POLICY_TYPE,
        context_sha256=base.digest(context_source), generation=base_document['generation'],
        base_model=base_document,
        exact_btn=table_document(exact_state, context_source=context_source,
            catalog_source=catalog_source, matrix_sha256=matrix_sha256))
    validate_model(value, context_source, catalog_source, matrix_sha256, entry_mass)
    reference = base.publish(directory, 'exactmodel', base.encoded(value))
    return dict(reference, generation=value['generation'])


def model_document(directory, reference, *, context_source, catalog_source,
                   matrix_sha256, entry_mass):
    value = json.loads(base.read_object(directory, reference))
    validate_model(value, context_source, catalog_source, matrix_sha256, entry_mass)
    if value['generation'] != reference['generation']:
        raise ValueError('Exact model reference generation mismatch')
    return value


def verify_bank(directory, completed, bank, current, *, context_source,
                catalog_source, matrix_sha256, entry_mass):
    if type(completed) is not int or completed < 0 or len(bank) != completed:
        raise ValueError('Complete ordered exact played bank required')
    documents = []
    for generation, ref in enumerate([*bank, current]):
        if type(ref['generation']) is not int or ref['generation'] != generation:
            raise ValueError('Exact played bank or next-generation order changed')
        documents.append(model_document(directory, ref, context_source=context_source,
            catalog_source=catalog_source, matrix_sha256=matrix_sha256, entry_mass=entry_mass))
    return documents


def require_config(config):
    base.validate_config(config)
    if config.get(CONFIG_KEY) != POLICY_TYPE:
        raise ValueError('Training configuration must explicitly declare exact response state')


def save_checkpoint(directory, *, completed, context_source, config, sampler,
                    action_rng, reservoirs, bank, current, catalog_source,
                    matrix_sha256, entry_mass):
    require_config(config)
    documents = verify_bank(directory, completed, bank, current,
        context_source=context_source, catalog_source=catalog_source,
        matrix_sha256=matrix_sha256, entry_mass=entry_mass)
    # The old checkpoint remains an explicitly nested base-state checkpoint.
    # It verifies reservoirs, sampled-table reconstruction and both RNGs. It
    # is never returned as the complete policy checkpoint to a caller.
    refs = []
    for d in documents:
        ref = base.publish(directory, 'visiblemodel', base.encoded(d['base_model']))
        refs.append(dict(ref, generation=d['generation']))
    inner = base.save_checkpoint(directory, completed=completed, context_source=context_source,
        config=config, sampler=sampler, action_rng=action_rng, reservoirs=reservoirs,
        bank=refs[:-1], current=refs[-1])
    value = dict(format=4, policy_type=POLICY_TYPE, completed_iterations=completed,
        context_sha256=base.digest(context_source), catalog_sha256=base.digest(catalog_source),
        matrix_sha256=matrix_sha256, config_sha256=hashlib.sha256(base.encoded(config)).hexdigest(),
        base_checkpoint=inner, played_bank=bank, next_model=current,
        exact_state_location='next_model.exact_btn.state; one update per played generation',
        averaging='Only ordered played generations; output weights are selected explicitly by a registered evaluator')
    return base.publish(directory, 'exactcheckpoint', base.encoded(value))


def restore_checkpoint(directory, reference, *, context_source, config,
                       catalog_source, matrix_sha256, entry_mass, manifest_source=None):
    require_config(config)
    value = json.loads(base.read_object(directory, reference))
    if (value.get('format') != 4 or value.get('policy_type') != POLICY_TYPE
            or value['context_sha256'] != base.digest(context_source)
            or value['catalog_sha256'] != base.digest(catalog_source)
            or value['matrix_sha256'] != matrix_sha256
            or value['config_sha256'] != hashlib.sha256(base.encoded(config)).hexdigest()):
        raise ValueError('Exact checkpoint identity or configuration changed')
    completed = value['completed_iterations']
    documents = verify_bank(directory, completed, value['played_bank'], value['next_model'],
        context_source=context_source, catalog_source=catalog_source,
        matrix_sha256=matrix_sha256, entry_mass=entry_mass)
    restored = base.restore_checkpoint(directory, value['base_checkpoint'],
        context_source=context_source, config=config, manifest_source=manifest_source)
    if restored['completed_iterations'] != completed:
        raise ValueError('Base and exact checkpoint iteration differ')
    for ref, exact_doc in zip([*restored['played_bank'], restored['next_model']], documents):
        old_doc = base.model_document(directory, ref, context_source=context_source)
        if base.encoded(old_doc) != base.encoded(exact_doc['base_model']):
            raise ValueError('Base and exact played histories differ')
    state = ExactBtnRegrets.restore(documents[-1]['exact_btn']['state'],
        context_sha256=base.digest(context_source), entry_mass=entry_mass)
    return dict(completed_iterations=completed, sampler=restored['sampler'],
        action_rng=restored['action_rng'], reservoirs=restored['reservoirs'],
        played_bank=value['played_bank'], next_model=value['next_model'],
        next_model_document=documents[-1], exact_btn_state=state)
