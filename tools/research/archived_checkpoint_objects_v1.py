"""Read immutable checkpoint objects from originals or an authenticated archive.

No extraction, rewriting, deletion or model adaptation. A completed retention
receipt is required before the archived object path becomes authoritative.
"""
import hashlib
import json
from pathlib import Path
import re
from sampled_visible_hybrid_checkpoint_v1 import read_object
from owned_research_archive_v1 import unpack
from owned_columnar_evaluation_archive_v1 import unlinked, read_bounded


def check(condition, message):
    if not condition:
        raise ValueError(message)


class ReadOnlyCheckpointObjects:
    def __init__(self, directory, *, guard):
        self.directory=unlinked(directory);self.guard=guard;self.members=None;self.retention_sha256=None
        receipt=self.directory.parent/'objects-retention.json'
        if receipt.exists():
            raw=read_bounded(receipt,1024*1024)
            self.retention_sha256=hashlib.sha256(raw).hexdigest()
            value=json.loads(raw)
            check(value.get('format')==1 and value.get('purpose')=='completed-owned-checkpoint-retention-v1'
                  and value.get('passed') is True and value.get('originals_retired') is True
                  and value['objects_directory']==str(self.directory), 'Completed object retention required')
            check(value['archive']=='objects.xz', 'Unexpected object archive path')
            archive=unlinked(self.directory.parent/value['archive'])
            manifest_raw=read_bounded(archive.with_suffix('.xz.json'),1024*1024)
            check(hashlib.sha256(manifest_raw).hexdigest()==value['manifest_sha256'], 'Object manifest changed')
            manifest=json.loads(manifest_raw)
            self.members=unpack(archive,manifest,guard=guard)
            check(set(self.members)==set(value['original_hashes']), 'Archived object set changed')
            for name,data in self.members.items():
                check(hashlib.sha256(data).hexdigest()==value['original_hashes'][name], 'Original object changed')
                check(re.fullmatch(r'[a-z]+-[0-9a-f]{64}\.(json|npz)',name), 'Invalid stored object name')
                # A later explicit restoration may coexist, but it must agree.
                path=self.directory/name
                if path.exists():
                    check(read_bounded(path,512*1024**2)==data, 'Plain/archive object conflict')

    def read(self, reference):
        self.guard();name=reference['file'];expected=reference['sha256']
        check(isinstance(name,str) and re.fullmatch(r'[a-z]+-[0-9a-f]{64}\.(json|npz)',name),
              'Invalid immutable object reference')
        if self.members is None:
            unlinked(self.directory/name)
            return read_object(self.directory,reference)
        check(name in self.members, 'Reference absent from archived checkpoint')
        raw=self.members[name]
        check(hashlib.sha256(raw).hexdigest()==expected, 'Archived object reference hash mismatch')
        return raw
