"""Restore the original checkpoint implementation from authenticated archives.

No extraction, mutation, fitting, or training launch. Call in a dedicated process:
the scoped adapters change only that process's object and reservoir byte readers.
The original validators and state reconstruction remain in use.
"""
import hashlib
import io
import json
from pathlib import Path
import threading
from unittest.mock import patch
from archived_checkpoint_objects_v1 import ReadOnlyCheckpointObjects
from owned_research_archive_v1 import unpack
from owned_columnar_evaluation_archive_v1 import unlinked, read_bounded
import sampled_visible_hybrid_checkpoint_v1 as base
from sampled_physical_reservoir_v1 import PhysicalReservoir
import later_action_checkpoint_v1 as baseline
import showdown_root_checkpoint_v1 as corrected

_RESTORE_LOCK = threading.Lock()


def check(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def restore(case, completed, *, treatment, config, bank_args, guard):
    check(type(completed) is int and 0 < completed <= 78
          and (completed % 8 == 0 or completed == 78), 'Complete recovery boundary required')
    check(treatment in ('baseline', 'corrected'), 'Explicit treatment required')
    check(_RESTORE_LOCK.acquire(blocking=False), 'Concurrent restoration is not supported')
    try:
        guard(); case = unlinked(case); objects = unlinked(case / 'objects')
        metadata = {}
        def document(path):
            raw = read_bounded(unlinked(path), 8*1024**2)
            metadata[str(path)] = digest(raw)
            return json.loads(raw)
        snapshot = document(case / f'checkpoint-{completed:04d}.json')
        marker = document(case / f'retention-{completed:04d}.json')
        metrics_path = case / f'iteration-{completed:04d}' / 'metrics.json'
        metrics = document(metrics_path)
        check(marker['iteration'] == metrics['iteration'] == snapshot['completed_iterations'] == completed,
              'Snapshot update identity differs')
        check(marker['metrics_sha256'] == metadata[str(metrics_path)], 'Snapshot metric changed')
        reference = snapshot['checkpoint']
        check(reference == marker['checkpoint'] == metrics['checkpoint'], 'Checkpoint references differ')
        pointer = snapshot['reservoir_archive']
        archive = unlinked(Path(pointer['path']))
        check(archive == case / f'checkpoint-reservoirs-{completed:04d}.xz'
              and pointer['iteration'] == completed, 'Wrong reservoir archive')
        manifest_path = archive.with_suffix('.xz.json')
        manifest = document(manifest_path)
        check(metadata[str(manifest_path)] == pointer['manifest_sha256'], 'Reservoir manifest changed')
        reservoirs = unpack(archive, manifest, guard=guard)
        check(len(reservoirs) == 2 and all(n.endswith('.npz') for n in reservoirs),
              'Two archived reservoir objects required')
        reader = ReadOnlyCheckpointObjects(objects, guard=guard)
        reads = {}
        def read_object(directory, ref):
            guard(); check(Path(directory).resolve() == objects, 'Unexpected object directory')
            filename = ref['file']
            if filename in reservoirs:
                raw = reservoirs[filename]
                check(digest(raw) == ref['sha256'], 'Archived reservoir reference changed')
            else:
                raw = reader.read(ref)
            check(filename not in reads or reads[filename] == ref['sha256'], 'Conflicting reference')
            reads[filename] = ref['sha256']
            return raw
        native_load = PhysicalReservoir.load
        def load_reservoir(path, context_source):
            p = Path(path)
            check(p.parent.resolve() == objects and p.name in reservoirs, 'Unexpected reservoir load')
            check(p.name in reads, 'Reservoir must first pass object authentication')
            return native_load(io.BytesIO(reservoirs[p.name]), context_source)
        module = baseline if treatment == 'baseline' else corrected
        with patch.object(base, 'read_object', read_object), patch.object(PhysicalReservoir, 'load', load_reservoir):
            state = module.restore_checkpoint(objects, reference, config=config, **bank_args)
        check(state['completed_iterations'] == completed and len(state['played_bank']) == completed,
              'Restored update count differs')
        check(state['next_model']['generation'] == state['exact_btn_state'].steps == completed,
              'Restored model or exact-response generation differs')
        check(int(state['root_regret_state'].counts.sum()) ==
              completed * config['subbatches_per_iteration'] * config['deals_per_subbatch'],
              'Restored root sample count differs')
        for path, expected in metadata.items():
            guard(); check(digest(Path(path).read_bytes()) == expected, 'Snapshot metadata changed during restore')
        return state, dict(completed_iterations=completed, treatment=treatment,
            checkpoint=reference, metadata_sha256=metadata, read_objects=reads,
            reservoir_archive_sha256=manifest['packed_sha256'],
            object_retention_sha256=reader.retention_sha256,
            files_extracted=0, original_reconstruction_used=True)
    finally:
        _RESTORE_LOCK.release()
