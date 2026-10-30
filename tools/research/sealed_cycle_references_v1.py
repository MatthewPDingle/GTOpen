"""Explicit readback of original hash references from a verified sealed cycle.

Callers opt in. This never replaces global Path/open/NumPy bindings, reads a
different raw source as fallback, changes a receipt, or retires a working file.
Existing {path,sha256} references remain the data identity.
"""
import json
from pathlib import Path

from sealed_cycle_archive_v2 import Archive


class SealedReferences:
    def __init__(self, archive_root, manifest_sha256):
        self.archive = Archive(archive_root, manifest_sha256)
        self.manifest_sha256 = manifest_sha256
        self.original_root = Path(self.archive.manifest['source_root']).resolve()

    def member(self, reference):
        if not isinstance(reference, dict) or not {'path','sha256'} <= reference.keys():
            raise ValueError('Original absolute path/hash reference required')
        original = Path(reference['path'])
        if not original.is_absolute():
            raise ValueError('Original reference is not absolute')
        original = original.resolve()
        if not original.is_relative_to(self.original_root):
            raise ValueError('Reference escapes original sealed namespace')
        name = original.relative_to(self.original_root).as_posix()
        item = self.archive.files.get(name)
        if item is None or item['sha256'] != reference['sha256']:
            raise ValueError('Reference is absent or has a different raw hash')
        if 'bytes' in reference and reference['bytes'] != item['bytes']:
            raise ValueError('Original byte count differs from archive')
        return name

    def open(self, reference):
        return self.archive.open(self.member(reference),reference['sha256'])

    def read_json(self, reference):
        with self.open(reference) as stream:
            return json.load(stream)

    def location(self, reference):
        return dict(original_reference=dict(reference),
                    member=self.member(reference),archive=str(self.archive.root),
                    manifest_sha256=self.manifest_sha256,
                    payload_sha256=self.archive.manifest['payload_sha256'],
                    qualifier='Lossless archived bytes; original file identity is historical')
