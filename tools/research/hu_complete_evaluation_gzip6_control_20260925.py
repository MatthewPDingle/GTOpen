"""Rearchive the completed 64-deal control; no new deals or model inference."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import shutil
import sys
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read,load_complete_cache
from sampled_evidence_archive_v1 import read_artifact
from owned_batch_archive_gzip6_v1 import OwnedBatchArchive
from archived_evaluation_reader_v1 import ArchivedEvaluationReader
from hu_later_action_recovered_evaluation_review_20260925 import verify_batch
from new_volume_research_store_v1 import measure_store
from reboot_research_idle_v1 import idle
from hu_paired_continuation_support_20260925 import LOCK,OTHER

PREFIX='complete-evaluation-gzip6-control-v1'
SOURCE='later-action-recovered-evaluation-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    assert sys.argv[1:]==['--run'] and idle() and not LOCK.exists() and not OTHER.exists()
    stopped=read(OUT/'later-action-recovered-pipeline-v1-status.json')
    assert stopped['state']=='stopped' and stopped['stage']=='evaluation-study'
    assert not psutil.pid_exists(stopped['controller_pid'])
    assert not (OUT/'later-action-recovered-evaluation-study-v1-registration.json').exists()
    assert not Path('S:/GTOpen-research/later-action-recovered-evaluation-study-v1').exists()
    assert not STORE.exists()
    start=time.monotonic()
    def guard():
        assert time.monotonic()-start<600 and idle()
        assert psutil.virtual_memory().available>20_000_000_000
        assert shutil.disk_usage('S:/').free>40_000_000_000
    guard()
    rp,pp,ap=[OUT/f'{SOURCE}-{s}.json' for s in ('registration','result','independent-review')]
    result,audit=read(pp),read(ap)
    assert result['passed'] and result['complete'] and result['deals']==64 and result['mode']=='control'
    assert audit['passed'] and audit['source_result_sha256']==sha(pp)
    assert result['registration_sha256']==audit['source_registration_sha256']==sha(rp)
    source=Path(result['store']);paths=[rp,pp,ap,Path(__file__).resolve()]
    paths+=list(p for p in source.rglob('*') if p.is_file())
    paths+=[ROOT/'tools/research'/name for name in (
        'sampled_evidence_archive_gzip6_v1.py','owned_batch_archive_gzip6_v1.py',
        'sampled_evidence_archive_v1.py','archived_evaluation_reader_v1.py',
        'hu_later_action_recovered_evaluation_review_20260925.py')]
    inputs={str(p):sha(p) for p in paths}
    registration=OUT/f'{PREFIX}-registration.json'
    save(registration,dict(inputs=inputs,source_control=SOURCE,store=str(STORE),
        source_result_sha256=sha(pp),source_review_sha256=sha(ap),compression_level=6,
        maximum_seconds=600,maximum_output_bytes=20_000_000,gpu_used=False,fresh_deals=0,
        projection='Preserve original whole-control scaling by 65536/64 with 50 percent margin plus 20 MB.',
        production_modified=False))
    STORE.mkdir();owner=OwnedBatchArchive.create(STORE,guard=guard)
    for name in ('analysis.json','bank-identities.json','root-stability.json'):
        with (STORE/name).open('xb') as stream:stream.write((source/name).read_bytes())
    manifests={};expected_batches={};raw_count=0
    for name,identity in result['archive_manifest_hashes'].items():
        guard();old=source/name;assert sha(old/'manifest.json')==identity
        manifest=read(old/'manifest.json');scratch=owner.begin(name);scratch.mkdir()
        for filename in manifest['artifacts']:
            raw=read_artifact(old,manifest,filename,guard=guard)
            with (scratch/filename).open('xb') as stream:stream.write(raw)
        manifests[name]=owner.publish(name)
        new=read(STORE/name/'manifest.json')
        assert new['compression_level']==6
        for filename in manifest['artifacts']:
            assert read_artifact(STORE/name,new,filename,guard=guard)==read_artifact(old,manifest,filename,guard=guard)
            raw_count+=1
        expected_batches[name]=json.loads(read_artifact(old,manifest,'query-batch.json',guard=guard))
        assert owner.release(name)==manifests[name]
    reader=ArchivedEvaluationReader(STORE,manifests,external_files=[],guard=guard)
    cache=load_complete_cache();source_context=(OUT/'bb-context-candidate.json').read_text()
    roots=read(STORE/'root-stability.json')['root_probabilities'];observations=deals=0
    for name,batch in expected_batches.items():
        values,n,h=verify_batch(reader,STORE/name,batch,source_context,cache,roots)
        assert h==result['batch_summary_hashes'][name]
        observations+=n;deals+=len(values)
    assert deals==64 and raw_count==14 and observations==audit['observations']
    storage=measure_store(STORE,guard);assert storage['logical_bytes']<20_000_000
    projection=int(storage['logical_bytes']*65536/64*1.5)+20_000_000
    assert projection<=12_000_000_000
    for path,h in inputs.items():guard();assert sha(path)==h,path
    output=dict(passed=True,registration_sha256=sha(registration),source_result_sha256=sha(pp),
        source_review_sha256=sha(ap),store=str(STORE),archive_manifest_hashes=manifests,
        decoded_artifacts_identical=raw_count,deals_reused=deals,observations=observations,
        storage=storage,projection_with_50pct_margin=projection,seconds=time.monotonic()-start,
        fresh_deals=0,gpu_used=False,production_modified=False,accuracy_qualified=False)
    save(OUT/f'{PREFIX}-result.json',output);print(json.dumps(output),flush=True)


if __name__=='__main__':main()
