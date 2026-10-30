"""CPU-only archival control on existing, audited numerical fixtures."""
import copy
import gzip
import json
from pathlib import Path
import time
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_evidence_archive_v1 import archive,read_artifact,MAX_ARTIFACT_BYTES

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-evidence-archive-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
PRIOR='sampled-physical-allin-precision-control-v1'


def main():
    began=time.monotonic()
    def guard():
        assert idle() and time.monotonic()-began<300
        assert psutil.virtual_memory().available>=20_000_000_000
        assert psutil.disk_usage(str(STORE.parent)).free>=40_000_000_000
    guard(); assert not STORE.exists()
    reviewpath=OUT/f'{PRIOR}-independent-review.json'
    review=json.loads(reviewpath.read_text());assert review['passed'] and review['complete_deals']==256
    for p,h in review['inputs'].items():assert sha(p)==h,p
    names=('batch.json','queries.json','profiles.json','native.json','summary.json')
    sources={}
    for offset in range(0,256,32):
        folder=STORE.parent/PRIOR/f'gpu-{offset}'
        for name in names:
            p=folder/name;expected=review['artifacts'][str(p)]
            assert sha(p)==expected,p;sources[str(p)]=expected
    paths=[Path(__file__),reviewpath,ROOT/'tools/research/sampled_evidence_archive_v1.py']
    registration=dict(inputs={str(p):sha(p) for p in paths},source_artifacts=sources,
        scope='Lossless transport control on eight existing audited batches. No new chance draws, GPU work, model changes or source deletion.',production_modified=False)
    regpath=OUT/f'{PREFIX}-registration.json';save(regpath,registration);STORE.mkdir()
    records=[];hashes={};raw_total=packed_total=0
    for offset in range(0,256,32):
        guard();source=STORE.parent/PRIOR/f'gpu-{offset}';target=STORE/f'batch-{offset}'
        manifest=archive(source,names,target,guard=guard)
        manifestpath=target/'manifest.json';hashes[str(manifestpath)]=sha(manifestpath)
        assert manifest==json.loads(manifestpath.read_text())
        for name,item in manifest['artifacts'].items():
            original=(source/name).read_bytes();p=target/item['file'];compressed=p.read_bytes()
            # Separate direct standard-library decoder checks the transport.
            independent=gzip.decompress(compressed)
            assert independent==original==read_artifact(target,manifest,name,guard=guard)
            assert json.loads(independent)==json.loads(original)
            assert sha(source/name)==sources[str(source/name)]==item['raw_sha256']
            assert sha(p)==item['compressed_sha256'];hashes[str(p)]=sha(p)
            raw_total+=len(original);packed_total+=len(compressed)
        records.append(dict(offset=offset,manifest=str(manifestpath),sha256=sha(manifestpath)))
    # Adversarial manifest/read cases never modify the successful archives.
    folder=STORE/'batch-0';original=json.loads((folder/'manifest.json').read_text())
    rejected=[]
    def rejects(name,fn):
        try:fn()
        except (ValueError,KeyError,OSError):rejected.append(name)
        else:raise AssertionError('Invalid case accepted: '+name)
    for label,key,value in [('member-path','file','../outside.gz'),
            ('compressed-hash','compressed_sha256','0'*64),
            ('raw-hash','raw_sha256','0'*64),('packed-size','compressed_bytes',1),
            ('decompressed-size','raw_bytes',1),('oversized','raw_bytes',MAX_ARTIFACT_BYTES+1)]:
        bad=copy.deepcopy(original);bad['artifacts']['batch.json'][key]=value
        rejects(label,lambda:read_artifact(folder,bad,'batch.json',guard=guard))
    bad=copy.deepcopy(original);bad['format']=2
    rejects('wrong-format',lambda:read_artifact(folder,bad,'batch.json',guard=guard))
    rejects('path-traversal',lambda:read_artifact(folder,original,'../batch.json',guard=guard))
    source=STORE.parent/PRIOR/'gpu-0'
    rejects('duplicate-members',lambda:archive(source,['batch.json','batch.json'],STORE/'invalid-duplicate',guard=guard))
    rejects('source-alias',lambda:archive(source,['batch.json'],source,guard=guard))
    rejects('existing-archive',lambda:archive(source,names,folder,guard=guard))
    assert len(rejected)==11
    for p,h in {**registration['inputs'],**sources,**hashes}.items():assert sha(p)==h,p
    guard();result=dict(passed=True,registration_sha256=sha(regpath),batches=8,deals=128,
        source_files_verified=40,raw_bytes=raw_total,compressed_bytes=packed_total,
        compressed_fraction=packed_total/raw_total,records=records,artifacts=hashes,
        rejected_cases=rejected,seconds=time.monotonic()-began,production_modified=False,
        scope=registration['scope'])
    save(OUT/f'{PREFIX}-result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('records','artifacts')}))


if __name__=='__main__':main()
