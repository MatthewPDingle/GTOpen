"""Explicit storage recovery for fixed-count wider evaluations.

Only complete contiguous batches may be reused. Replays the original core's
sampling, response fitting and residual calculations; never reads intervals
from the failed run. A controller must establish terminal source state and
freeze this manifest and every model/source identity before calling run.
"""
import json
import shutil
from pathlib import Path
from unittest.mock import patch
import wider_root_evaluation_v1 as core
from sampled_physical_root_evaluation_v1 import sha

ROOT_FILES = ('training-deals.json', 'response.json',
              'residual-preparation.json', 'test-start.json', 'training-stability.json')


def read(path):
    return json.loads(Path(path).read_text())


def capture(folder, config, guard):
    """Freeze only a complete training prefix and completed test prefix."""
    folder = Path(folder).resolve()
    assert folder.is_dir() and not folder.is_symlink()
    root = {name: sha(folder / name) for name in ROOT_FILES}
    start = read(folder / 'test-start.json')
    assert start['response_frozen_before_test']
    assert start['response_sha256'] == root['response.json']
    assert start['preparation_sha256'] == root['residual-preparation.json']
    batches = {}
    counts = {}
    for phase, total in (('train', config['per_class'] * 169), ('test', config['test_deals'])):
        complete = 0
        stopped = False
        for offset in range(0, total, config['batch_size']):
            guard()
            name = f'{phase}-{offset:06d}'
            part = folder / name
            ready = (part / 'summary.json').is_file()
            if phase == 'test':
                ready = ready and (part / 'residuals.json').is_file()
            if not ready:
                stopped = True
                continue
            assert not stopped, 'Source has a hole in completed batches'
            assert not part.is_symlink()
            summary = read(part / 'summary.json')
            artifacts = summary['artifacts']
            assert set(artifacts) == {'query-batch.json', 'conditional-batch.json',
                                       'queries.json', 'profiles.json', 'native.json'}
            batch = read(part / 'query-batch.json')
            assert batch['batch_id'] == f"{config['id']}-{name}"
            assert len(batch['deals']) == min(config['batch_size'], total - offset)
            files = dict(artifacts, **{'summary.json': sha(part / 'summary.json')})
            if phase == 'test':
                files['residuals.json'] = sha(part / 'residuals.json')
            batches[name] = files
            complete += len(batch['deals'])
        counts[phase] = complete
    assert counts['train'] == config['per_class'] * 169
    return dict(source=str(folder), config=config, root_files=root,
                batches=batches, completed_deals=counts)


def run(context_path, bank, cache, exact, config, folder, guard, manifest):
    """Run the unchanged evaluator with verified completed-batch transport."""
    assert manifest['config'] == config
    source = Path(manifest['source']).resolve()
    folder = Path(folder).resolve()
    assert source != folder and not folder.exists()
    for name, digest in manifest['root_files'].items():
        guard()
        assert sha(source / name) == digest
    original = core.batch_values
    reused = []
    computed = []
    checked_response = False

    def recovered(cp, batch, destination, check, active_bank, active_cache):
        nonlocal checked_response
        check()
        destination = Path(destination)
        name = destination.name
        assert destination.parent.resolve() == folder
        assert batch['batch_id'] == f"{config['id']}-{name}"
        if name.startswith('test-') and not checked_response:
            for root_name, digest in manifest['root_files'].items():
                assert sha(folder / root_name) == digest, f'Reconstructed {root_name} differs'
            checked_response = True
        if name not in manifest['batches']:
            computed.append(name)
            return original(cp, batch, destination, check, active_bank, active_cache)
        old = source / name
        assert read(old / 'query-batch.json') == batch, 'Chance stream or batch identity changed'
        destination.mkdir(exist_ok=False)
        for filename, digest in manifest['batches'][name].items():
            check()
            src = old / filename
            assert not src.is_symlink() and sha(src) == digest
            if filename != 'residuals.json':
                dst = destination / filename
                shutil.copy2(src, dst)
                assert sha(dst) == digest
                assert dst.stat().st_mtime_ns == src.stat().st_mtime_ns
            assert sha(src) == digest
        reused.append(name)
        return read(destination / 'summary.json')

    with patch.object(core, 'batch_values', recovered):
        result = core.run(context_path, bank, cache, exact, config, folder, guard)
    assert checked_response
    for name in reused:
        for filename, digest in manifest['batches'][name].items():
            guard()
            assert sha(folder / name / filename) == digest
    for name, digest in manifest['root_files'].items():
        assert sha(source / name) == sha(folder / name) == digest
    return result, dict(reused_batches=reused, computed_batches=computed,
        original_response_and_rng_reproduced=True, all_reused_artifact_hashes_match=True,
        original_scope_and_sample_counts_unchanged=True, final_look_only=True)
