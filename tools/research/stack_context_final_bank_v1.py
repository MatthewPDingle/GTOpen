"""Select the prospectively fixed complete played banks, without fitting.

This verifies terminal metadata and selection. The loader then authenticates
every actual model and its local context state using the existing model reader.
Neither function samples deals or chooses a model using evaluation results.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
from stack_context_inputs_v1 import encoded
from stack_context_full_policy_v1 import read_model
from stack_context_training_checkpoint_v1 import TYPE

CYCLES = 64
BANK_ORDER = ('A-baseline','A-relative','B-baseline','B-relative')
DEPTHS = (20,40,60,100,150,200,400)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha_value(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def reference(value, kind, generation=None):
    required = {'file','sha256'} | ({'generation'} if generation is not None else set())
    require(isinstance(value,dict) and set(value) == required, 'Unexpected model/checkpoint reference fields')
    identity = value['sha256']
    require(isinstance(identity,str) and re.fullmatch(r'[0-9a-f]{64}',identity), 'Invalid immutable object digest')
    require(value['file'] == kind+'-'+identity+'.json', 'Immutable filename and identity differ')
    if generation is not None:
        require(type(value['generation']) is int and value['generation'] == generation,
                'Missing, reordered or unplayed model generation')


def select(arm, progress, checkpoint, spec, *, training_registration_sha256):
    require(arm in BANK_ORDER and spec['cycles'] == CYCLES
            and spec['final_bank_generations'] == list(range(CYCLES)) and spec['unplayed_excluded'] == CYCLES,
            'Changed prospective model boundary')
    cfg = spec['arms'][arm]['config']
    width = 387 if arm.endswith('relative') else 362
    require(spec['arms'][arm]['representation'] == width
            and spec['arms'][arm]['replication'] == (0 if arm.startswith('A-') else 1), 'Arm identity differs')
    require(progress['registration_sha256'] == training_registration_sha256
            and type(progress['completed_cycles']) is int and progress['completed_cycles'] == CYCLES,
            'Training arm has not reached its fixed complete boundary')
    reference(progress['checkpoint'],'jointcontextcheckpoint')
    require(sha_value(checkpoint) == progress['checkpoint']['sha256'], 'Checkpoint content does not match the completed reference')
    updates = progress['updates']
    require(len(updates) == CYCLES and [r['cycle'] for r in updates] == list(range(1,CYCLES+1)),
            'Missing complete-cycle evidence')
    for row in updates:
        reference(row['checkpoint'],'jointcontextcheckpoint')
        require(row['paired_sources'] and all(isinstance(v,str) and re.fullmatch(r'[0-9a-f]{64}',v)
                                             for v in row['paired_sources'].values()), 'Missing matched-stream identities')
    require(len({row['checkpoint']['sha256'] for row in updates}) == CYCLES
            and updates[-1]['checkpoint'] == progress['checkpoint'], 'Final checkpoint or trajectory differs')
    require(checkpoint['format'] == 1 and checkpoint['checkpoint_type'] == TYPE
            and checkpoint['completed_cycles'] == CYCLES and checkpoint['config'] == cfg
            and checkpoint['config_sha256'] == sha_value(cfg), 'Wrong complete checkpoint configuration')
    registry = checkpoint['registry']
    require(checkpoint['registry_sha256'] == cfg['registry_sha256'] == sha_value(registry)
            and registry['representation'] == cfg['representation']
            and registry['representation']['input_width'] == width, 'Changed input representation or registry')
    contexts = registry['contexts']
    require(len(contexts) == 7 and sorted(row['starting_stack'] for row in contexts) == list(DEPTHS)
            and all(row['split'] == ('heldout' if row['starting_stack'] in (60,150) else 'fit') for row in contexts),
            'Changed fitting/held-out depth partition')
    fitting = {row['context_sha256'] for row in contexts if row['split'] == 'fit'}
    require(set(checkpoint['contexts']) == set(cfg['contexts']) == fitting,
            'Fitted local state does not match the five training depths')
    played = checkpoint['played_bank']
    require(len(played) == CYCLES, 'Complete played bank required')
    for generation, item in enumerate(played):
        reference(item,'fullstackmodel',generation)
    reference(checkpoint['next_model'],'fullstackmodel',CYCLES)
    identities = [r['sha256'] for r in [*played,checkpoint['next_model']]]
    require(len(set(identities)) == CYCLES+1, 'Duplicated or substituted model identity')
    return dict(arm=arm,input_width=width,completed_cycles=CYCLES,checkpoint=copy.deepcopy(progress['checkpoint']),
        registry_sha256=cfg['registry_sha256'],played=copy.deepcopy(played),
        excluded_unplayed=copy.deepcopy(checkpoint['next_model']),
        weights_by_player=[list(range(1,CYCLES+1)) for _ in (0,1)],
        matched_streams_by_cycle=[copy.deepcopy(row['paired_sources']) for row in updates],
        selection='All played generations 0..63; linear weights 1..64 for each actor; no test-based selection')


def select_terminal(result, checkpoints, spec, *, training_registration_sha256):
    require(result.get('training_complete') is True and result.get('registration_sha256') == training_registration_sha256
            and result.get('production_modified') is False, 'Successful unchanged training outcome required')
    require(set(result['arms']) == set(checkpoints) == set(BANK_ORDER), 'All four complete arms required')
    selected = {arm:select(arm,result['arms'][arm],checkpoints[arm],spec,
                          training_registration_sha256=training_registration_sha256) for arm in BANK_ORDER}
    for seed in ('A','B'):
        require(selected[seed+'-baseline']['matched_streams_by_cycle'] ==
                selected[seed+'-relative']['matched_streams_by_cycle'], 'Paired physical/action/board sources differ')
    return dict(format=1,bank_order=list(BANK_ORDER),arms=selected,
                training_registration_sha256=training_registration_sha256,selection_uses_test_results=False)


def load_documents(objects, selected, registry, resources, *, guard):
    """Read immutable model files; no reservoir mutation or training resumption."""
    require(selected['completed_cycles'] == CYCLES and selected['registry_sha256'] == registry.sha256
            and selected['weights_by_player'] == [list(range(1,CYCLES+1)) for _ in (0,1)], 'Changed selected bank')
    documents = []
    require(len(selected['played']) == CYCLES, 'Missing selected model')
    for generation, item in enumerate(selected['played']):
        guard()
        reference(item,'fullstackmodel',generation)
        value = read_model(Path(objects),item,registry,resources)
        require(value['generation'] == generation, 'Model file generation differs')
        documents.append(value)
    # Validate the excluded identity as well, without including its policy in
    # the played average or using its result to choose another checkpoint.
    guard()
    reference(selected['excluded_unplayed'],'fullstackmodel',CYCLES)
    read_model(Path(objects),selected['excluded_unplayed'],registry,resources)
    return documents
