"""Exact recovery helpers for the fixed fourth-arm continuation.

No changes to training arithmetic. Helpers use existing authenticated readers,
require matching original artifacts, and archive only newly owned duplicates.
"""
import json
from pathlib import Path
from sampled_physical_root_evaluation_v1 import sha, save
from owned_research_archive_v1 import pack, unpack, retire
from compact_checkpoint_fit_replay_20260926 import compare, require
import sampled_visible_hybrid_checkpoint_v1 as base


def equal_states(a, b):
    import numpy as np
    for key in ('completed_iterations', 'played_bank', 'next_model'):
        require(a[key] == b[key], 'Restored state differs: '+key)
    require(a['sampler'].checkpoint() == b['sampler'].checkpoint(), 'Sampler state differs')
    require(a['action_rng'].bit_generator.state == b['action_rng'].bit_generator.state, 'Action RNG differs')
    for key in ('root_regret_state', 'exact_btn_state'):
        require(a[key].document() == b[key].document(), 'Accumulated state differs: '+key)
    require(len(a['reservoirs']) == len(b['reservoirs']) == 2, 'Two reservoirs required')
    for x, y in zip(a['reservoirs'], b['reservoirs']):
        require(x.summary() == y.summary() and x.rng.bit_generator.state == y.rng.bit_generator.state,
                'Reservoir metadata/RNG differs')
        for key in ('keys', 'active', 'arity', 'values', 'iterations'):
            require(np.array_equal(getattr(x, key)[:x.size], getattr(y, key)[:y.size]),
                    'Reservoir array differs: '+key)


def compare_update(source, folder, metric, *, completed, guard):
    """Retained updates require a marker; partial 56 remains explicitly partial."""
    n = metric['iteration']
    original_folder = source/f'iteration-{n:04d}'
    original = json.loads((original_folder/'metrics.json').read_text())
    if completed:
        marker = json.loads((source/f'retention-{n:04d}.json').read_text())
        require(marker['metrics_sha256'] == sha(original_folder/'metrics.json'), 'Original metric changed')
    else:
        require(n == 56 and not (source/f'retention-{n:04d}.json').exists(), 'Only preserved partial 56 allowed')
    for value, path in ((original, original_folder), (metric, folder)):
        require(value['initial_policy_sha256'] == sha(path/'current-initial-policy.json'), 'Initial policy changed')
    compare(original, metric, json.loads((original_folder/'current-initial-policy.json').read_text()),
            json.loads((folder/'current-initial-policy.json').read_text()))
    for chunk in range(8):
        guard()
        archive = source/f'iteration-{n:04d}-batch-{chunk:02d}.xz'
        manifest = archive.with_suffix('.xz.json')
        old_part = original_folder/f'batch-{chunk:02d}'
        if manifest.exists():
            if completed:
                ptr = marker['archives'][chunk]
                require(Path(ptr['path']) == archive and ptr['manifest_sha256'] == sha(manifest),
                        'Original batch pointer differs')
            members = unpack(archive, json.loads(manifest.read_text()), guard=guard)
        else:
            require(not completed and not archive.exists(), 'Incomplete original archive requires explicit recovery')
            members = {p.name:p.read_bytes() for p in old_part.iterdir() if p.is_file()}
        part = folder/f'batch-{chunk:02d}'
        require(set(members) == {p.name for p in part.iterdir() if p.is_file()}, 'Replay member set changed')
        for name, raw in members.items():
            require(raw == (part/name).read_bytes(), 'Replay bytes differ: '+name)
    return dict(iteration=n, original_completed=completed, exact_model=True,
        exact_scientific_metrics=True, exact_native_artifacts=True,
        original_metrics_sha256=sha(original_folder/'metrics.json'))


def reservoir_references(objects, checkpoint):
    outer = json.loads(base.read_object(objects, checkpoint))
    require(outer['format'] == 8, 'Corrected checkpoint envelope required')
    exact = json.loads(base.read_object(objects, outer['exact_checkpoint']))
    require(exact['format'] == 4, 'Exact checkpoint envelope required')
    inner = json.loads(base.read_object(objects, exact['base_checkpoint']))
    require(inner['format'] == 3, 'Visible checkpoint envelope required')
    refs = inner['reservoirs']
    require(len(refs) == 2 and len({r['file'] for r in refs}) == 2, 'Two distinct reservoirs required')
    require(inner['completed_iterations'] == exact['completed_iterations'] == outer['completed_iterations'],
            'Nested checkpoint generation mismatch')
    return refs


def retain_update(case, objects, metric, *, root, token, guard):
    """Call inside the authenticated predecessor overlay, after exact comparisons."""
    n = metric['iteration']
    folder = case/f'iteration-{n:04d}'
    archives = []
    for chunk in range(8):
        part = folder/f'batch-{chunk:02d}'
        dest = case/f'iteration-{n:04d}-batch-{chunk:02d}.xz'
        manifest = pack(part, [p.name for p in part.iterdir() if p.is_file()], dest,
                        root=root, token=token, guard=guard)
        retire(part, dest, manifest, root=root, token=token, guard=guard)
        archives.append(dict(path=str(dest), manifest_sha256=sha(dest.with_suffix('.xz.json')),
                             packed_bytes=manifest['packed_bytes']))
    if metric['checkpoint'] is not None:
        refs = reservoir_references(objects, metric['checkpoint'])
        # Partial original 56 can own the exact replayed reservoirs already.
        # Copy only those two authenticated byte streams to the NEW owned
        # directory so the unchanged archive/retire primitive can handle them.
        for ref in refs:
            raw = base.read_object(objects, ref)
            target = objects/ref['file']
            require(target.resolve().parent == objects.resolve(), 'Reservoir path escaped new ownership')
            if not target.exists():
                with target.open('xb') as stream:
                    stream.write(raw)
            else:
                require(target.read_bytes() == raw, 'Conflicting local reservoir')
        names = [r['file'] for r in refs]
        require(set(names) == {p.name for p in objects.glob('*.npz')}, 'Unexpected current reservoir objects')
        dest = case/f'checkpoint-reservoirs-{n:04d}.xz'
        manifest = pack(objects, names, dest, root=root, token=token, guard=guard)
        retire(objects, dest, manifest, root=root, token=token, guard=guard)
        pointer = dict(iteration=n, path=str(dest), manifest_sha256=sha(dest.with_suffix('.xz.json')))
        save(case/f'checkpoint-{n:04d}.json', dict(checkpoint=metric['checkpoint'],
            reservoir_archive=pointer, completed_iterations=n))
    marker = dict(iteration=n, metrics_sha256=sha(folder/'metrics.json'),
                  checkpoint=metric['checkpoint'], archives=archives)
    save(case/f'retention-{n:04d}.json', marker)
    return marker
