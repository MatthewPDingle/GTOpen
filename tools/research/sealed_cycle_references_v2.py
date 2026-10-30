"""Explicit original-reference readers for the streaming format-3 archive.

Existing native receipt paths, byte counts and hashes remain authoritative.
No global file API patch, alternate raw fallback, scientific operation or
retirement occurs here. A collection can name several disjoint sealed archives.
"""
import json
import os
from pathlib import Path

from sealed_cycle_archive_v3 import Archive, MAGIC


def original_key(path):
    value = Path(path)
    if not value.is_absolute():
        raise ValueError('Original reference must be absolute')
    return os.path.normcase(str(value.resolve()))


class SealedReferences:
    def __init__(self, archive_root, manifest_sha256, *, guard=lambda: None,
                 charge=lambda amount, operation: None):
        root = Path(archive_root).resolve()
        guard()
        # Metadata observations do not read payloads. Precharge the actual
        # closed containers before the constructor authenticates their bytes.
        charge(sum((root / n).stat().st_size for n in
                   ('manifest.json', 'payload.gta', 'verified.json')) + len(MAGIC),
               'sealed-reference-container-read')
        self.archive = Archive(root, manifest_sha256, check=guard)
        self.manifest_sha256 = manifest_sha256
        self.original_root = Path(self.archive.manifest['source_root']).resolve()
        self.guard, self.charge = guard, charge
        self.originals = {}
        for name in self.archive.files:
            path = self.original_root.joinpath(*name.split('/'))
            key = original_key(path)
            if key in self.originals:
                raise ValueError('Case-aliased original archive members')
            self.originals[key] = name

    def member(self, reference):
        if not isinstance(reference, dict) or not {'path', 'sha256'} <= reference.keys():
            raise ValueError('Original absolute path/hash reference required')
        name = self.originals.get(original_key(reference['path']))
        if name is None:
            raise ValueError('Reference is absent from this sealed namespace')
        item = self.archive.files[name]
        if reference['sha256'] != item['sha256']:
            raise ValueError('Original hash differs from archive')
        if 'bytes' in reference and reference['bytes'] != item['bytes']:
            raise ValueError('Original byte count differs from archive')
        return name

    def open(self, reference):
        name = self.member(reference)
        self.guard()
        # Consumers can seek/reread; this opening charges one complete raw
        # traversal only. Repeated-read consumers must declare extra work.
        item = self.archive.files[name]
        self.charge(max(item['bytes'], item['stored_bytes']), 'sealed-reference-member-read')
        return self.archive.open(name, reference['sha256'])

    def verify(self, reference):
        name = self.member(reference)
        self.guard()
        item = self.archive.files[name]
        self.charge(max(item['bytes'], item['stored_bytes']), 'sealed-reference-member-verify')
        return self.archive.verify(name, check=self.guard)

    def read_json(self, reference):
        with self.open(reference) as stream:
            return json.load(stream)

    def location(self, reference):
        return dict(original_reference=dict(reference), member=self.member(reference),
                    archive=str(self.archive.root), manifest_sha256=self.manifest_sha256,
                    payload_sha256=self.archive.manifest['payload_sha256'],
                    qualifier='Lossless archived bytes; original file identity is historical')


class SealedReferenceSet:
    def __init__(self, bindings, *, guard=lambda: None,
                 charge=lambda amount, operation: None):
        self.readers, self.by_original = [], {}
        for binding in bindings:
            if not isinstance(binding, dict) or set(binding) != {'root', 'manifest_sha256'}:
                raise ValueError('Explicit archive root and manifest hash required')
            reader = SealedReferences(binding['root'], binding['manifest_sha256'],
                                      guard=guard, charge=charge)
            self.readers.append(reader)
            for key in reader.originals:
                if key in self.by_original:
                    raise ValueError('Original appears in multiple archives')
                self.by_original[key] = reader

    def contains(self, reference):
        return original_key(reference['path']) in self.by_original

    def reader(self, reference):
        value = self.by_original.get(original_key(reference['path']))
        if value is None:
            raise ValueError('No explicitly registered archive for original')
        value.member(reference)
        return value

    def verify(self, reference):
        return self.reader(reference).verify(reference)

    def open(self, reference):
        return self.reader(reference).open(reference)

    def location(self, reference):
        return self.reader(reference).location(reference)
