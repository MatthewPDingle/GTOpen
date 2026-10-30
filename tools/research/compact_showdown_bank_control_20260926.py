"""CPU-only admission and averaging control using the real audited eight-update prefix."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
import numpy as np
from compact_showdown_bank_v1 import load_bank
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
    prefix = 'compact-showdown-bank-control-v1'
    registration = OUT / f'{prefix}-registration.json'
    destination = OUT / f'{prefix}-result.json'
    assert not registration.exists() and not destination.exists()
    sources = [Path(__file__).resolve(), ROOT / 'tools/research/compact_showdown_bank_v1.py',
        ROOT / 'tools/research/action_integrated_policy_v1.py',
        OUT / 'showdown-training-readback-v2-9266201-baseline-0008-result.json']
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
        result = dict(passed=True, registration_sha256=sha(registration), bank_identity=identity,
            observations=len(catalog), maximum_root_policy_error=error,
            saved_policy_hashes=policy_sources, rejections=rejections, seconds=time.monotonic()-start,
            gpu_used=False, production_modified=False, accuracy_qualified=False,
            full_arm_qualified=False, corrected_arm_qualified=False,
            scope='Real audited baseline prefix admission and CPU average against independently saved played root policies. Full and corrected bank admission remain pending.')
        save(destination, result)
        print(json.dumps({k: v for k, v in result.items() if k not in ('bank_identity', 'saved_policy_hashes')}))
    except BaseException as exc:
        save(destination, dict(passed=False, error=repr(exc), registration_sha256=sha(registration),
            seconds=time.monotonic()-start, gpu_used=False, production_modified=False))
        raise


if __name__ == '__main__':
    main()
