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
import numpy as np
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


def restore(case, completed, *, treatment, config, bank_args, guard, predecessor=None):
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
        check((len(reservoirs) == 2 or completed == 8 and len(reservoirs) == 4)
              and all(n.endswith('.npz') for n in reservoirs),
              'Two checkpoint reservoirs, optionally two startup reservoirs at update 8, required')
        reader = ReadOnlyCheckpointObjects(objects, guard=guard)
        previous = None
        if predecessor is not None:
            check(isinstance(predecessor, dict)
                  and set(predecessor) == {'directory', 'retention_sha256'},
                  'Explicit predecessor directory and retention identity required')
            previous_path = unlinked(Path(predecessor['directory']))
            check(previous_path != objects and not previous_path.is_relative_to(case),
                  'Predecessor must be outside continuation case')
            previous = ReadOnlyCheckpointObjects(previous_path, guard=guard)
            check(previous.retention_sha256 == predecessor['retention_sha256'],
                  'Predecessor retention identity changed')
        reads = {}; locations = {}
        def contains(source, name):
            return name in source.members if source.members is not None else (source.directory/name).exists()
        def read_object(directory, ref):
            guard(); check(Path(directory).resolve() == objects, 'Unexpected object directory')
            filename = ref['file']
            if filename in reservoirs:
                raw = reservoirs[filename]
                check(digest(raw) == ref['sha256'], 'Archived reservoir reference changed')
                locations[filename] = 'reservoir_archive'
                if contains(reader, filename):
                    check(raw == reader.read(ref), 'Local reservoir conflicts with archive')
                if previous is not None and contains(previous, filename):
                    check(raw == previous.read(ref), 'Predecessor reservoir conflicts with archive')
            else:
                if contains(reader, filename):
                    raw = reader.read(ref); locations[filename] = 'local'
                    if previous is not None and contains(previous, filename):
                        check(raw == previous.read(ref), 'Local/predecessor object conflict')
                else:
                    check(previous is not None, 'Missing local object and no predecessor')
                    raw = previous.read(ref); locations[filename] = 'predecessor'
            check(filename not in reads or reads[filename] == ref['sha256'], 'Conflicting reference')
            reads[filename] = ref['sha256']
            return raw
        native_load = PhysicalReservoir.load
        loaded = set()
        def load_reservoir(path, context_source):
            p = Path(path)
            check(p.parent.resolve() == objects and p.name in reservoirs, 'Unexpected reservoir load')
            check(p.name in reads, 'Reservoir must first pass object authentication')
            loaded.add(p.name)
            return native_load(io.BytesIO(reservoirs[p.name]), context_source)
        module = baseline if treatment == 'baseline' else corrected
        with patch.object(base, 'read_object', read_object), patch.object(PhysicalReservoir, 'load', load_reservoir):
            state = module.restore_checkpoint(objects, reference, config=config, **bank_args)
        check(len(loaded) == 2, 'Exactly two referenced checkpoint reservoirs must be loaded')
        # The first cadence archive also contains the initialization checkpoint's
        # empty objects. They must not become restored training reservoirs.
        extras = set(reservoirs)-loaded; initial_players = set()
        for name in extras:
            initial = native_load(io.BytesIO(reservoirs[name]), bank_args['context_source'])
            check(initial.size == initial.seen == 0 and initial.capacity == config['reservoir_capacity'],
                  'Unreferenced reservoir is not empty startup state')
            check(initial.player in (0, 1) and initial.player not in initial_players,
                  'Startup reservoir players differ')
            check(initial.rng.bit_generator.state == np.random.PCG64(config['reservoir_seeds'][initial.player]).state,
                  'Startup reservoir random state differs')
            initial_players.add(initial.player)
            del initial
        check(not extras or initial_players == {0, 1}, 'Both startup reservoirs required')
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
            loaded_reservoir_objects=sorted(loaded), validated_startup_objects=sorted(extras),
            object_retention_sha256=reader.retention_sha256,
            predecessor=predecessor, object_locations=locations,
            files_extracted=0, original_reconstruction_used=True)
    finally:
        _RESTORE_LOCK.release()
