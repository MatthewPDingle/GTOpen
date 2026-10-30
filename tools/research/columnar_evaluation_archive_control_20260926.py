"""Durable publication/retirement and original scalar-reader control on owned copies."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import hashlib
import json
from pathlib import Path
import time
import psutil
from sampled_evidence_archive_gzip6_v1 import read_artifact
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read, load_complete_cache
from reboot_research_idle_v1 import idle
from owned_columnar_evaluation_archive_v1 import OwnedColumnarEvaluationArchive, ColumnarEvaluationReader, restore
from hu_later_action_compact_evaluation_review_20260925 import verify_batch


PREFIX = 'columnar-evaluation-archive-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX


def main():
    started=time.monotonic()
    def guard():
        assert idle() and time.monotonic()-started < 600 and psutil.virtual_memory().available > 20_000_000_000
        if STORE.exists():
            assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) < 60_000_000
    guard()
    registration,destination=(OUT/f'{PREFIX}-{k}.json' for k in ('registration','result'))
    assert not registration.exists() and not destination.exists() and not STORE.exists()
    old_result=OUT/'later-action-compact-evaluation-study-v1-result.json';result=read(old_result)
    original=Path(result['store'])/'test-000000';mp=original/'manifest.json'
    assert result['passed'] and sha(mp)==result['archive_manifest_hashes']['test-000000']
    dependencies=[Path(__file__).resolve(),old_result,mp,
        OUT/'evaluation-lossless-columnar-probe-v2-result.json',
        *[ROOT/'tools/research'/n for n in ('owned_columnar_evaluation_archive_v1.py',
            'crossed_profile_columnar_v1.py','crossed_profile_columnar_v2.py',
            'hu_later_action_compact_evaluation_review_20260925.py')],
        *original.glob('*.gz')]
    inputs={str(p):sha(p) for p in dependencies}
    assert read(OUT/'evaluation-lossless-columnar-probe-v2-result.json')['passed']
    save(registration,dict(inputs=inputs,store=str(STORE),maximum_output_bytes=60_000_000,
        maximum_seconds=600,gpu_used=False,production_modified=False,
        scope='CPU control; archive only new owned copies of one previously evaluated batch.'))
    rejected=[]
    def reject(label,action):
        try:action()
        except (ValueError,FileNotFoundError):rejected.append(label)
        else:raise AssertionError('Accepted '+label)
    try:
        old=read(mp);parts={n:read_artifact(original,old,n,guard=guard) for n in old['artifacts']}
        writer=OwnedColumnarEvaluationArchive.create(STORE,guard=guard)
        name='test-000000';folder=writer.begin(name);folder.mkdir()
        for n,raw in parts.items():
            with (folder/n).open('xb') as f:f.write(raw)
        reject('no durable receipt',lambda:writer.release(name))
        assert {p.name for p in folder.iterdir()}==set(parts)
        identity=writer.publish(name)
        manifest=read(STORE/(name+'.manifest.json'));archive=STORE/(name+'.xz')
        assert restore(archive,manifest,guard=guard)==parts
        reject('wrong owner',lambda:OwnedColumnarEvaluationArchive(STORE,'0'*64,guard=guard))
        reject('parent traversal',lambda:writer.release('../test-000000'))
        changed=folder/'query-batch.json';changed.write_bytes(parts[changed.name]+b' ')
        reject('changed original before retirement',lambda:writer.release(name))
        assert {p.name for p in folder.iterdir()}==set(parts)
        changed.write_bytes(parts[changed.name])
        reader=ColumnarEvaluationReader(STORE,{name:identity},guard=guard)
        assert reader.read_bytes(STORE/name/'profiles.json')==parts['profiles.json']
        packed=archive.read_bytes();mutated=bytearray(packed);mutated[-8]^=1;archive.write_bytes(mutated)
        reject('changed compressed data blocks retirement',lambda:writer.release(name))
        reject('changed compressed data invalidates reader cache',lambda:reader.read_bytes(STORE/name/'profiles.json'))
        assert {p.name for p in folder.iterdir()}==set(parts)
        archive.write_bytes(packed)
        reject('unregistered virtual batch',lambda:reader.read_bytes(STORE/'test-000032'/'profiles.json'))
        reject('unregistered scratch path',lambda:reader.read_bytes(folder/'profiles.json'))
        virtual=STORE/name;virtual.mkdir();plain=virtual/'profiles.json';plain.write_bytes(parts['profiles.json'])
        reject('ambiguous plain and archived file',lambda:reader.read_bytes(plain))
        assert plain.resolve().parent==virtual.resolve() and plain.resolve().is_relative_to(STORE.resolve())
        assert plain.read_bytes()==restore(archive,manifest,guard=guard)['profiles.json']
        plain.unlink();virtual.rmdir()
        # Simulate interrupted retirement of one already verified, owned copy.
        target=folder/'summary.json'
        assert target.resolve().parent==folder.resolve() and target.resolve().is_relative_to(STORE.resolve())
        assert target.read_bytes()==restore(archive,manifest,guard=guard)['summary.json']
        target.unlink()
        assert writer.release(name)==identity and not folder.exists()
        assert writer.release(name)==identity  # Safe retry after completion.
        for n,raw in parts.items():assert reader.read_bytes(STORE/name/n)==raw
        expected=json.loads(parts['query-batch.json']);context=json.loads(parts['queries.json'])['context_source']
        values,observations,summary_hash=verify_batch(reader,STORE/name,expected,context,load_complete_cache())
        assert summary_hash==hashlib.sha256(parts['summary.json']).hexdigest()
        assert len(values)==32 and observations>0
        for p,h in inputs.items():guard();assert sha(p)==h,p
        output=dict(passed=True,registration_sha256=sha(registration),store=str(STORE),
            raw_bytes=sum(map(len,parts.values())),packed_bytes=manifest['packed_bytes'],
            manifest_sha256=identity,owner_sha256=writer.owner_sha256,rejections=rejected,
            original_members_verified=len(parts),scalar_reader_deals=len(values),
            scalar_reader_observations=observations,original_summary_sha256=summary_hash,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
            interrupted_retirement_recovered=True,legacy_files_unchanged=True,
            seconds=time.monotonic()-started,gpu_used=False,production_modified=False,
            scope='Durable lossless archive, guarded new-copy retirement and existing scalar evaluation-reader compatibility. No new evaluation or poker-strength result.')
        save(destination,output);print(json.dumps({k:v for k,v in output.items() if k!='artifacts'}),flush=True)
    except BaseException as exc:
        save(destination,dict(passed=False,error=repr(exc),registration_sha256=sha(registration),
            seconds=time.monotonic()-started,gpu_used=False,production_modified=False))
        raise


if __name__=='__main__':main()
