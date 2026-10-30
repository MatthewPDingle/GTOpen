"""Archive only new owned scratch batches, then release verified copies.

No recursive deletion. Completed receipts authenticate durable archives;
interrupted cleanup can be resumed with the original owner identity.
"""
import json
import os
from pathlib import Path
import re
import uuid
from sampled_evidence_archive_v1 import archive, read_artifact, digest


ARTIFACTS = {'query-batch.json', 'conditional-batch.json', 'queries.json',
             'profiles.json', 'native.json', 'summary.json'}


def durable_json(path, value):
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':'))+'\n').encode()
    with path.open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return digest(raw)


class OwnedBatchArchive:
    def __init__(self, root, owner_sha256, *, guard):
        self.root = Path(root).absolute()
        self.work = self.root / '.batch-work'
        self.owner_sha256 = owner_sha256
        self.guard = guard
        self._owner()

    @classmethod
    def create(cls, root, *, guard):
        root = Path(root).absolute(); guard()
        if root.resolve() != root or not root.is_dir():
            raise ValueError('Existing unlinked evaluation root required')
        work = root / '.batch-work'
        work.mkdir(exist_ok=False)
        identity = durable_json(work/'owner.json', dict(format=1,
            id=uuid.uuid4().hex, root=str(root), purpose='new-evaluation-scratch-only'))
        return cls(root, identity, guard=guard)

    def _owner(self):
        self.guard()
        if self.root.resolve() != self.root or self.work.resolve() != self.work:
            raise ValueError('Linked or aliased scratch root')
        path = self.work/'owner.json'
        if path.is_symlink() or digest(path.read_bytes()) != self.owner_sha256:
            raise ValueError('Scratch owner identity changed')
        doc = json.loads(path.read_bytes())
        if doc['format'] != 1 or doc['root'] != str(self.root):
            raise ValueError('Scratch owner context mismatch')

    def _paths(self, name):
        self._owner()
        if not re.fullmatch(r'(train|test)-[0-9]{6}', name):
            raise ValueError('Invalid batch name')
        path = self.work/name
        if path.resolve() != path or path.parent != self.work:
            raise ValueError('Scratch path escapes owned root')
        paths = (path, self.root/name, self.work/(name+'.claim.json'), self.work/(name+'.receipt.json'))
        if any(p.resolve() != p or p.is_symlink() for p in paths):
            raise ValueError('Linked or aliased batch path')
        return paths

    def begin(self, name):
        path, target, claim, receipt = self._paths(name)
        if path.exists() or target.exists() or claim.exists() or receipt.exists():
            raise ValueError('Preserve existing batch or attempt')
        durable_json(claim, dict(owner_sha256=self.owner_sha256, name=name))
        # Native batch generation creates this directory itself.
        return path

    def _claim(self, name, claim):
        if claim.is_symlink() or json.loads(claim.read_bytes()) != dict(
                owner_sha256=self.owner_sha256, name=name):
            raise ValueError('Batch ownership mismatch')

    def publish(self, name):
        path, target, claim, receipt = self._paths(name)
        self._claim(name, claim)
        expected = ARTIFACTS | ({'residuals.json'} if name.startswith('test-') else set())
        if {p.name for p in path.iterdir()} != expected:
            raise ValueError('Incomplete or unexpected scratch artifacts')
        manifest = archive(path, expected, target, guard=self.guard)
        # Flush all new archive bytes before publishing permission to release
        # scratch. A partial archive without a receipt never permits cleanup.
        for member in [*(target/v['file'] for v in manifest['artifacts'].values()), target/'manifest.json']:
            with member.open('ab') as stream:
                stream.flush(); os.fsync(stream.fileno())
        for filename in expected:
            if read_artifact(target, manifest, filename, guard=self.guard) != (path/filename).read_bytes():
                raise ValueError('Archive changed before publication')
        identity = digest((target/'manifest.json').read_bytes())
        durable_json(receipt, dict(owner_sha256=self.owner_sha256, name=name,
            manifest_sha256=identity, artifacts=sorted(expected)))
        return identity

    def release(self, name):
        path, target, claim, receipt = self._paths(name)
        self._claim(name, claim)
        if receipt.is_symlink():
            raise ValueError('Linked cleanup receipt')
        entry = json.loads(receipt.read_bytes())
        if entry['owner_sha256'] != self.owner_sha256 or entry['name'] != name:
            raise ValueError('Cleanup receipt owner mismatch')
        if target.resolve() != target:
            raise ValueError('Linked archive directory')
        if (target/'manifest.json').is_symlink():
            raise ValueError('Linked archive manifest')
        raw = (target/'manifest.json').read_bytes()
        if digest(raw) != entry['manifest_sha256']:
            raise ValueError('Archive manifest changed; keep scratch')
        manifest = json.loads(raw)
        expected = ARTIFACTS | ({'residuals.json'} if name.startswith('test-') else set())
        if set(manifest['artifacts']) != expected or set(entry['artifacts']) != expected:
            raise ValueError('Cleanup artifact set mismatch')
        # Authenticate every archived member, even if an earlier interrupted
        # release already removed its scratch copy.
        for filename in sorted(expected):
            read_artifact(target, manifest, filename, guard=self.guard)
        if not path.exists():
            return entry['manifest_sha256']
        remaining = {p.name for p in path.iterdir()}
        if not remaining <= expected:
            raise ValueError('Unexpected scratch file; keep all remaining files')
        for filename in sorted(remaining):
            self.guard()
            current = path/filename
            if current.resolve() != current or not current.is_file():
                raise ValueError('Linked scratch file; keep it')
            if digest(current.read_bytes()) != manifest['artifacts'][filename]['raw_sha256']:
                raise ValueError('Scratch changed; keep it')
        for filename in sorted(remaining):
            self.guard(); self._owner()
            current = path/filename
            # Resolve each exact target again immediately before removal.
            if current.resolve() != current or current.parent != path or path.parent != self.work:
                raise ValueError('Unsafe cleanup target')
            if digest(current.read_bytes()) != manifest['artifacts'][filename]['raw_sha256']:
                raise ValueError('Scratch changed during cleanup')
            current.unlink()
        path.rmdir()  # Empty owned batch only; never recursive.
        return entry['manifest_sha256']
