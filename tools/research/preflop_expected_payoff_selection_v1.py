"""Read-only connection from the completed four-arm study to fixed payoff banks.

The caller supplies authenticated registration, freshly recomputed arm configs,
bounded IO, the existing complete checkpoint restorer and model reader. This
module cannot admit or run training, draw deals, or choose a favorable boundary.
"""
import copy
import hashlib
import json
from pathlib import Path
import re

from preflop_expected_payoff_bank_v1 import FixedExpectedBank, selected_documents
from preflop_expected_policy_v1 import encoded

ARMS = ('first-K2', 'first-K8', 'replication-K2', 'replication-K8')
MAX_METADATA_BYTES = 16_000_000


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(path):
    require(isinstance(path, str), 'Explicit absolute path required')
    value = Path(path)
    require(value.is_absolute() and value.resolve() == value,
            'Canonical absolute path required')
    return value


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def reference(value, *, expected_path=None):
    require(isinstance(value, dict) and set(value) == {'path', 'sha256'},
            'Exact path/hash reference required')
    path = canonical(value['path'])
    require(isinstance(value['sha256'], str)
            and re.fullmatch('[0-9a-f]{64}', value['sha256']) is not None,
            'Explicit SHA256 required')
    if expected_path is not None:
        require(path == expected_path, 'Artifact routed to a different study or arm')
    return path


def model_reference(value, generation):
    require(isinstance(value, dict)
            and set(value) == {'file', 'sha256', 'generation'}
            and type(value['generation']) is int and value['generation'] == generation
            and isinstance(value['sha256'], str)
            and re.fullmatch('[0-9a-f]{64}', value['sha256']) is not None
            and value['file'] == f"expectedstackmodel-{value['sha256']}.json",
            'Exact immutable model reference and ordered generation required')


class CompletedStudySelection:
    """Fixed final metadata, followed by actual complete checkpoint restoration."""
    def __init__(self, *, registration_reference, result_reference,
                 release_reference, selection_reference, expected_scope,
                 expected_configs, registry_sha256, read_bytes,
                 same_process_live, guard):
        self._read_bytes, self._guard = read_bytes, guard
        self.witnesses = []

        def read(ref, path=None):
            value = self._read(ref, path)
            return value

        reg = read(registration_reference)
        require(reg.get('scope') == expected_scope
                and expected_scope.get('cycles') == 32
                and expected_scope.get('board_counts') == [2, 8]
                and expected_scope.get('independent_training_seeds') == 2
                and expected_scope.get('fit_depths') == [20, 40, 100, 200, 400]
                and expected_scope.get('heldout_depths') == [60, 150]
                and expected_scope.get('classes') == 169
                and expected_scope.get('fitted_decisions') == 24
                and reg.get('arm_order') == list(ARMS)
                and set(reg.get('arms', {})) == set(ARMS)
                and set(expected_configs) == set(ARMS),
                'Complete unchanged scientific scope and all four arms required')
        root = canonical(reg['coordinator_store'])
        cas = canonical(reg['cas_store'])
        require(root.parent == Path(r'S:\GTOpen-research')
                and cas.parent == root.parent and root != cas,
                'Registered canonical S stores required')
        result = read(result_reference, root/'result.json')
        release = read(release_reference, root/'released.json')
        selection = read(selection_reference, root/'fixed-complete-bank-selection.json')
        require(result.get('training_stability_complete') is True
                and result.get('payoff_evaluation_complete') is False
                and type(result.get('cycles_per_arm')) is int
                and result['cycles_per_arm'] == 32
                and result.get('all169_all24') is True
                and result.get('full_checkpoint_restore_each_cycle') is True
                and result.get('selection_sha256') == selection_reference['sha256'],
                'Completed full training result with exact final selection required')
        require(release.get('success') is True and release.get('errors') == []
                and release.get('global_lock_removed') is True
                and release.get('failure_preserved') is False
                and type(result.get('pid')) is int and result['pid'] > 0
                and type(result.get('creation_time')) in (int, float)
                and result['creation_time'] > 0
                and (release.get('pid'), release.get('creation_time'))
                    == (result['pid'], result['creation_time']),
                'Successful terminal release from the same observed process required')
        guard()
        live = same_process_live(result['pid'], result['creation_time'])
        require(type(live) is bool and not live,
                'Training process must be authoritatively terminal before evaluation')
        require(type(selection.get('format')) is int and selection['format'] == 1
                and selection.get('method') == reg['method']
                and type(selection.get('completed_cycles')) is int
                and selection['completed_cycles'] == 32
                and type(selection.get('selected_boundary')) is int
                and selection['selected_boundary'] == 32
                and selection.get('selection_reason')
                    == 'fixed registered final budget; no favorable boundary selection'
                and set(selection.get('arms', {})) == set(ARMS),
                'Only the predeclared final32 boundary is eligible')
        rounds = result.get('arms')
        require(isinstance(rounds, list) and len(rounds) == 128,
                'Every complete cycle of every arm required')
        for index, item in enumerate(rounds):
            cycle, arm = index//4 + 1, ARMS[index % 4]
            arm_root = canonical(reg['arms'][arm]['store'])
            require(arm_root.parent == root.parent
                    and item.get('arm') == arm and type(item.get('cycle')) is int
                    and item['cycle'] == cycle, 'Incomplete or reordered study schedule')
            reference(item['pointer'], expected_path=arm_root/f'checkpoint-{cycle:04d}.json')
        self.arms, self.registry_sha256 = {}, registry_sha256
        for index, arm in enumerate(ARMS):
            entry = selection['arms'][arm]
            arm_root = canonical(reg['arms'][arm]['store'])
            namespace = cas/'namespaces'/arm/'objects'
            require(canonical(entry['root']) == arm_root
                    and canonical(entry['objects_namespace']) == namespace
                    and entry['checkpoint'] == rounds[-4 + index]['pointer']
                    and entry.get('own_history_weights_by_player') == [[1.]*32, [1.]*32],
                    'Selected bank routed to another arm or changed weights')
            pointer = read(entry['checkpoint'], arm_root/'checkpoint-0032.json')
            require(pointer.get('arm') == arm
                    and type(pointer.get('completed_cycles')) is int
                    and pointer['completed_cycles'] == 32
                    and pointer.get('full_restore_verified') is True
                    and canonical(pointer['objects_namespace']) == namespace
                    and pointer.get('played_bank') == entry.get('played_bank')
                    and pointer.get('excluded_unplayed_next_model') == entry.get('excluded_unplayed_model'),
                    'Final pointer and selected complete bank disagree')
            bank = entry['played_bank']
            require(isinstance(bank, list) and len(bank) == 32,
                    'Every actual played generation0..31 required')
            for generation, ref in enumerate(bank):
                model_reference(ref, generation)
            model_reference(entry['excluded_unplayed_model'], 32)
            config_ref_path = arm_root/'arm-config.json'
            # This config is bound to the content-addressed checkpoint by the
            # original restorer, and independently recomputed from registration.
            raw = read_bytes(config_ref_path, max_bytes=MAX_METADATA_BYTES)
            require(isinstance(raw, bytes) and len(raw) <= MAX_METADATA_BYTES,
                    'Bounded actual configuration bytes required')
            config_doc = json.loads(raw)
            require(config_doc.get('config') == expected_configs[arm]
                    and config_doc['config'].get('registry_sha256') == registry_sha256,
                    'Actual arm config differs from recomputed registered config')
            self.witnesses.append(dict(path=str(config_ref_path), sha256=digest(raw)))
            self.arms[arm] = dict(namespace=str(namespace), config=copy.deepcopy(config_doc['config']),
                checkpoint=copy.deepcopy(pointer['checkpoint']), played=copy.deepcopy(bank),
                excluded=copy.deepcopy(entry['excluded_unplayed_model']))
        self.registration_reference = copy.deepcopy(registration_reference)
        self.selection_reference = copy.deepcopy(selection_reference)
        self.documents = None

    def _read(self, ref, path=None):
        actual = reference(ref, expected_path=path)
        self._guard()
        raw = self._read_bytes(actual, max_bytes=MAX_METADATA_BYTES)
        require(isinstance(raw, bytes) and len(raw) <= MAX_METADATA_BYTES
                and digest(raw) == ref['sha256'], 'Actual metadata differs from pinned bytes')
        self.witnesses.append(copy.deepcopy(ref))
        return json.loads(raw)

    def restore_documents(self, *, restore_state, read_model, guard):
        """Callbacks must use the existing qualified CAS/restorer/model reader."""
        require(self.documents is None, 'Complete bank already restored')
        documents = {}
        for arm in ARMS:
            value = self.arms[arm]; guard()
            state = restore_state(arm, value['namespace'], copy.deepcopy(value['checkpoint']),
                                  copy.deepcopy(value['config']))
            require(type(state.get('completed_cycles')) is int and state['completed_cycles'] == 32
                    and state.get('played_bank') == value['played']
                    and state.get('next_model') == value['excluded'],
                    'Restored complete checkpoint differs from selected arm')
            rows = []
            for ref in value['played']:
                guard(); document = read_model(arm, value['namespace'], copy.deepcopy(ref))
                require(digest(encoded(document)) == ref['sha256'],
                        'Consumed model document differs from immutable reference')
                rows.append(document)
            documents[arm] = selected_documents(rows, completed_cycles=32, next_generation=32)
        self.documents = documents
        return dict(played_generations=list(range(32)), excluded_generation=32,
                    arm_order=list(ARMS), metadata=copy.deepcopy(self.witnesses),
                    model_identities={a:[v['sha256'] for v in self.arms[a]['played']] for a in ARMS})

    def banks(self, *, registry, resources_by_arm, context_sha256, device, guard):
        require(self.documents is not None and registry.sha256 == self.registry_sha256
                and set(resources_by_arm) == set(ARMS),
                'Restored complete banks and matching registered context resources required')
        for arm in ARMS:
            require(len(self.documents[arm]) == 32, 'Restored bank length changed')
            for document, ref in zip(self.documents[arm], self.arms[arm]['played']):
                guard()
                require(digest(encoded(document)) == ref['sha256'],
                        'Restored immutable bank changed before context construction')
        return tuple(FixedExpectedBank(self.documents[arm], registry, resources_by_arm[arm],
            context_sha256=context_sha256, completed_cycles=32, next_generation=32,
            device=device, guard=guard) for arm in ARMS)
