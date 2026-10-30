"""Bounded, hash-verified byte access for future archived evaluation batches.

Original metadata stays plain; each batch is a separately authenticated gzip
archive. This reader never writes, extracts, deletes, or changes source files.
"""
import json
from pathlib import Path
import re
from sampled_evidence_archive_v1 import read_artifact, digest, MAX_ARTIFACT_BYTES


class ArchivedEvaluationReader:
    def __init__(self, root, manifest_hashes, *, external_files, guard):
        self.root = Path(root).absolute()
        self.manifest_hashes = dict(manifest_hashes)
        self.external = {Path(p).absolute() for p in external_files}
        self.guard = guard
        if not self.manifest_hashes or any(
            not re.fullmatch(r'(train|test)-[0-9]{6}', name)
            for name in self.manifest_hashes
        ):
            raise ValueError('Explicit evaluation batch identities required')

    def _plain(self, path):
        self.guard()
        if path.resolve() != path.absolute() or path.is_symlink():
            raise ValueError('Linked or aliased evidence path')
        if path.stat().st_size > MAX_ARTIFACT_BYTES:
            raise ValueError('Oversized evidence file')
        raw = path.read_bytes()
        if len(raw) > MAX_ARTIFACT_BYTES:
            raise ValueError('Evidence grew beyond size limit')
        return raw

    def read_bytes(self, path):
        path = Path(path).absolute()
        if path in self.external or path.parent == self.root:
            return self._plain(path)
        if path.parent.parent != self.root:
            raise ValueError('Evidence outside registered evaluation')
        name = path.parent.name
        if name not in self.manifest_hashes:
            raise ValueError('Unregistered batch')
        if path.exists():
            raise ValueError('Ambiguous plain and archived artifact')
        manifest_path = path.parent / 'manifest.json'
        raw = self._plain(manifest_path)
        if digest(raw) != self.manifest_hashes[name]:
            raise ValueError('Archive manifest identity changed')
        return read_artifact(path.parent, json.loads(raw), path.name, guard=self.guard)

    def read_json(self, path):
        return json.loads(self.read_bytes(path))

    def sha256(self, path):
        return digest(self.read_bytes(path))
