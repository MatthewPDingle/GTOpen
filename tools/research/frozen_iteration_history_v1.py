"""Explicit, contiguous locations for immutable training evidence.

Storage boundaries never change the iteration numbers or the original training
budget. Snapshot and verify all iteration files and each checkpoint's object
closure; earlier object generations may remain on their original volume.
"""
from pathlib import Path
import json
from immutable_checkpoint_copy_v1 import inspect_closure
from sampled_physical_root_evaluation_v1 import sha


def directory(value):
    path = Path(value)
    if not path.is_absolute() or not path.is_dir():
        raise ValueError('Existing absolute evidence directory required')
    for ancestor in (path, *path.parents):
        if ancestor.is_symlink() or ancestor.is_junction():
            raise ValueError('Linked evidence directories are unsupported')
    return path.resolve()


class FrozenHistory:
    def __init__(self, segments, completed):
        if type(completed) is not int or completed <= 0:
            raise ValueError('Positive completed update count required')
        self.completed = completed
        self.locations = {}
        next_iteration = 1
        for segment in segments:
            first, last = segment['first'], segment['last']
            if (type(first) is not int or type(last) is not int or
                    first != next_iteration or last < first or last > completed):
                raise ValueError('Segments must cover a contiguous nonoverlapping prefix')
            store, objects = directory(segment['store']), directory(segment['objects'])
            for iteration in range(first, last+1):
                folder = directory(store/f'iteration-{iteration:04d}')
                if folder.parent != store:
                    raise ValueError('Iteration folder escaped its evidence store')
                self.locations[iteration] = (folder, objects)
            next_iteration = last+1
        if next_iteration != completed+1:
            raise ValueError('Incomplete history coverage')

    def location(self, iteration):
        return self.locations[iteration]

    def snapshot(self, *, maximum_bytes, guard):
        files = {}
        total = 0
        def add(path):
            nonlocal total
            path = Path(path)
            if path.is_symlink() or path.is_junction() or not path.is_file():
                raise ValueError('Regular immutable evidence file required')
            name = str(path.resolve())
            if name not in files:
                guard()
                total += path.stat().st_size
                if total > maximum_bytes:
                    raise ValueError('Evidence exceeds admitted read budget')
                files[name] = sha(path)
        for iteration in range(1,self.completed+1):
            folder,objects = self.location(iteration)
            for path in sorted(folder.rglob('*')):
                if path.is_symlink() or path.is_junction():
                    raise ValueError('Linked evidence is unsupported')
                if path.is_file(): add(path)
            metrics = json.loads((folder/'metrics.json').read_text())
            if metrics['iteration'] != iteration:
                raise ValueError('Iteration identity does not match its folder')
            for ref in (metrics['checkpoint'], metrics['used_model']):
                closure = inspect_closure(objects, ref, maximum_bytes=maximum_bytes, guard=guard)
                for name in closure['objects']: add(objects/name)
        return dict(files=files,logical_bytes=total,completed_updates=self.completed)


def verify_snapshot(snapshot, guard):
    for name,digest in snapshot['files'].items():
        guard()
        if sha(name) != digest:
            raise ValueError('Historical evidence changed: '+name)
