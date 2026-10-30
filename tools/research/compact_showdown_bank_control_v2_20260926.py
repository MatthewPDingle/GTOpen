"""CPU-only admission and averaging control using the real audited eight-update prefix."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
import numpy as np
from compact_showdown_bank_v2 import load_bank, validated_document
from archived_checkpoint_objects_v1 import ReadOnlyCheckpointObjects
from showdown_root_checkpoint_v1 import model_document as original_corrected_document
from action_integrated_policy_v1 import ActionIntegratedCpuBank64
from hu_action_integrated_exact_20260925 import bank_args
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle


def main():
    start = time.monotonic()
    def guard():
        assert idle() and time.monotonic() - start < 240
    guard()
    prefix = 'compact-showdown-bank-control-v2'
    registration = OUT / f'{prefix}-registration.json'
    destination = OUT / f'{prefix}-result.json'
    assert not registration.exists() and not destination.exists()
    sources = [Path(__file__).resolve(), ROOT / 'tools/research/compact_showdown_bank_v2.py',
        ROOT / 'tools/research/action_integrated_policy_v1.py',
        OUT / 'showdown-training-readback-v2-9266201-baseline-0008-result.json',
        OUT / 'archived-checkpoint-objects-control-v1-result.json',
        ROOT / 'tools/research/archived_checkpoint_objects_v1.py']
    inputs = {str(p): sha(p) for p in sources}
    save(registration, dict(inputs=inputs, purpose='implementation-control',
        arm='9266201-baseline', completed=8, gpu_used=False, maximum_seconds=240))
    try:
        args = bank_args((OUT / 'bb-context-candidate.json').read_text())
        models, weights, identity = load_bank(OUT, '9266201-baseline', completed=8,
            purpose='implementation-control', bank_args=args, guard=guard)
        assert not identity['evaluation_qualified'] and identity['excluded_generation'] == 8
        assert [d['generation'] for d in models] == list(range(8))
        catalog = json.loads(args['catalog_source'])['native_observations']
        query = dict(context_source=args['context_source'], observations=[r['observation'] for r in catalog])
        assert all(o['own_history'] == [] for o in query['observations'])
        bank = ActionIntegratedCpuBank64(models, completed_iterations=8,
            weights_by_player=weights, **args)
        actual, reach = bank.average(query, guard=guard)
        expected = np.zeros_like(actual)
        case = Path('S:/GTOpen-research/showdown-matched-training-v1/9266201-baseline')
        # Independent reference: the already-audited policies actually played
        # before each update, not a second invocation of bank averaging.
        policy_sources = {}
        for generation in range(8):
            path = case / f'iteration-{generation+1:04d}' / 'current-initial-policy.json'
            policy_sources[str(path)] = sha(path)
            frozen = read(path)
            for i, row in enumerate(catalog):
                h = row['hand_class']
                p = frozen['root'][h] if row['player'] == 0 else [1-frozen['calls'][h], frozen['calls'][h], 0, 0]
                expected[i] += (generation + 1) * np.asarray(p) / 36
        error = float(np.max(abs(actual - expected)))
        assert error < 1e-10 and np.array_equal(reach, np.full(len(catalog), 36.))
        rejections = []
        for name, label, purpose, n in [
            ('partial evaluation', '9266201-baseline', 'evaluation', 8),
            ('unknown purpose', '9266201-baseline', 'preview', 8),
            ('unknown arm', 'missing-arm', 'implementation-control', 8),
            ('boolean update count', '9266201-baseline', 'implementation-control', True),
        ]:
            try:
                load_bank(OUT, label, completed=n, purpose=purpose, bank_args=args, guard=guard)
            except ValueError:
                rejections.append(name)
            else:
                raise AssertionError('Accepted ' + name)
        for p, h in {**inputs, **policy_sources}.items():
            assert sha(p) == h
        # Authenticate the already-qualified archive and compare the actual reader
        # used by v2 against the original corrected model validator.
        archive_result = read(OUT / 'archived-checkpoint-objects-control-v1-result.json')
        assert archive_result['passed']
        for p, h in archive_result['artifacts'].items():
            guard(); assert sha(p) == h
        archive_objects = ReadOnlyCheckpointObjects(Path(archive_result['store']) / 'case/objects', guard=guard)
        source = read(OUT / 'showdown-training-integration-control-v1-result.json')
        checkpoint = json.loads(archive_objects.read(source['final_checkpoint']))
        archived_generations = []
        for ref in [*checkpoint['played_bank'], checkpoint['next_model']]:
            actual_doc = validated_document(archive_objects, ref, treatment=True, bank_args=args)
            expected_doc = original_corrected_document(Path(source['store']) / 'objects', ref, **args)
            assert actual_doc == expected_doc
            archived_generations.append(actual_doc['generation'])
        assert archived_generations == [0, 1, 2]
        ref = checkpoint['played_bank'][0]
        for name, changed, treatment in [
            ('archived wrong generation', dict(ref, generation=7), True),
            ('corrected relabelled baseline', ref, False),
        ]:
            try:
                validated_document(archive_objects, changed, treatment=treatment, bank_args=args)
            except ValueError:
                rejections.append(name)
            else:
                raise AssertionError('Accepted ' + name)
        for p, h in inputs.items(): assert sha(p) == h
        result = dict(passed=True, registration_sha256=sha(registration), bank_identity=identity,
            observations=len(catalog), maximum_root_policy_error=error,
            archived_corrected_generations=archived_generations,
            archive_retention_sha256=archive_objects.retention_sha256,
            saved_policy_hashes=policy_sources, rejections=rejections, seconds=time.monotonic()-start,
            gpu_used=False, production_modified=False, accuracy_qualified=False,
            full_arm_qualified=False, corrected_arm_qualified=False,
            scope='Real audited baseline prefix admission and CPU average against independently saved played root policies. Archived corrected control documents match original validated documents exactly; full bank admission remains pending.')
        save(destination, result)
        print(json.dumps({k: v for k, v in result.items() if k not in ('bank_identity', 'saved_policy_hashes')}))
    except BaseException as exc:
        save(destination, dict(passed=False, error=repr(exc), registration_sha256=sha(registration),
            seconds=time.monotonic()-start, gpu_used=False, production_modified=False))
        raise


if __name__ == '__main__':
    main()
