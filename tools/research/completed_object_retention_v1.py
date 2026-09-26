"""Crash-resumable retirement of immutable objects in explicitly owned scratch.

The caller must establish completion and exclusive quiescence. A durable intent
binds that evidence before compression; every original byte remains recoverable.
"""
import hashlib
import json
import os
from pathlib import Path
import re
from owned_research_archive_v1 import owner, pack, unpack, encoded, MAX_RAW
from owned_columnar_evaluation_archive_v1 import unlinked, read_bounded
from archived_checkpoint_objects_v1 import ReadOnlyCheckpointObjects


def check(value, message):
    if not value:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def publish(path, value):
    with path.open('xb') as stream:
        stream.write(encoded(value)); stream.flush(); os.fsync(stream.fileno())


def retain(case, *, root, token, eligibility, guard, after_retire=None):
    """Never operate on a live arm; eligibility must keep asserting that fact.

    after_retire is a qualification-only interruption hook. No directory removal.
    Existing incomplete archives are preserved and refused, never overwritten.
    """
    root = owner(root, token)
    case = unlinked(case)
    check(case.parent == root, 'Exact owned arm directory required')
    objects = unlinked(case / 'objects')
    archive = case / 'objects.xz'
    manifest_path = case / 'objects.xz.json'
    intent_path = case / 'objects-retention-intent.json'
    receipt_path = case / 'objects-retention.json'
    guard(); evidence = eligibility()
    check(isinstance(evidence, dict) and evidence, 'Completed audit evidence required')
    if intent_path.exists():
        intent = json.loads(read_bounded(intent_path, 1024**2))
        check(intent['format'] == 1 and intent['evidence'] == evidence
              and intent['objects_directory'] == str(objects), 'Retention identity changed')
    else:
        check(not archive.exists() and not manifest_path.exists() and not receipt_path.exists(),
              'Unowned archive or receipt already exists')
        entries = sorted(objects.iterdir())
        check(entries and all(p.is_file() for p in entries), 'Only immutable files expected')
        check(sum(p.stat().st_size for p in entries) <= MAX_RAW, 'Bounded object bundle required')
        original_hashes = {}
        for path in entries:
            guard(); unlinked(path)
            check(re.fullmatch(r'[a-z]+-[0-9a-f]{64}\.(json|npz)', path.name), 'Invalid immutable name')
            original_hashes[path.name] = digest(read_bounded(path, MAX_RAW))
            check(original_hashes[path.name] == path.stem.split('-')[1], 'Content-addressed object changed')
        intent = dict(format=1, evidence=evidence, objects_directory=str(objects), original_hashes=original_hashes)
        publish(intent_path, intent)
    hashes = intent['original_hashes']
    if not manifest_path.exists():
        check(not archive.exists(), 'Incomplete archive preserved; explicit recovery required')
        check({p.name for p in objects.iterdir()} == set(hashes), 'Object set changed before packing')
        for name, expected in hashes.items():
            check(digest(read_bounded(objects / name, MAX_RAW)) == expected, 'Original changed before packing')
        pack(objects, list(hashes), archive, root=root, token=token, guard=guard)
    manifest_raw = read_bounded(manifest_path, 1024**2)
    manifest = json.loads(manifest_raw)
    restored = unpack(unlinked(archive), manifest, guard=guard)
    check({n: digest(b) for n, b in restored.items()} == hashes, 'Archive differs from durable intent')
    remaining = list(objects.iterdir())
    check(all(p.is_file() and p.name in hashes for p in remaining), 'Unexpected object appeared')
    # Verify every remaining original before deleting any, including on resume.
    for path in remaining:
        check(read_bounded(path, MAX_RAW) == restored[path.name], 'Raw/archive conflict')
    guard(); check(eligibility() == evidence, 'Completion evidence changed')
    for path in remaining:
        guard(); unlinked(path)
        check(path.resolve().parent == objects and path.resolve().is_relative_to(root), 'Redirected deletion')
        check(read_bounded(path, MAX_RAW) == restored[path.name], 'Original changed during retirement')
        path.unlink()
        if after_retire is not None:
            after_retire(path)
    receipt = dict(format=1, purpose='completed-owned-checkpoint-retention-v1', passed=True,
        originals_retired=True, objects_directory=str(objects), archive=archive.name,
        manifest_sha256=digest(manifest_raw), original_hashes=hashes, evidence=evidence,
        intent_sha256=digest(read_bounded(intent_path, 1024**2)))
    if receipt_path.exists():
        check(json.loads(read_bounded(receipt_path, 1024**2)) == receipt, 'Completed receipt changed')
    else:
        publish(receipt_path, receipt)
    reader = ReadOnlyCheckpointObjects(objects, guard=guard)
    for name, expected in hashes.items():
        check(digest(reader.read(dict(file=name, sha256=expected))) == expected, 'Final archived read failed')
    return dict(objects=len(hashes), raw_bytes=sum(map(len, restored.values())),
                packed_bytes=manifest['packed_bytes'], receipt_sha256=digest(read_bounded(receipt_path, 1024**2)))
