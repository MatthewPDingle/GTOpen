"""Replay complete archived river-target calculations with subset preparation.

Two fixed batches, different seeds/models. CPU only. No fresh training, model
fitting, checkpoint changes, or competing GPU work. Preserve failure evidence.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                  MKL_NUM_THREADS='1', RAYON_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import argparse
import gc
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import psutil

ROOT=Path('T:/Dev/GTOpen');TOOLS=ROOT/'tools/research'
sys.path.insert(0,str(TOOLS))
from river_policy_batch_v1 import CPUCurrentPolicy
from river_query_preflop_subset_v1 import prepare as subset_prepare
from river_training_overlay_targets_stream_v1 import generate
from weighted_deal_binding_v1 import DealWeightGeneration
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_physical_root_evaluation_v1 import save
from bounded_parallel_evaluation_archive_v2 import production_available
from global_research_inventory_v2 import measure
from board_study_storage_v1 import measure as study_measure

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-preflop-subset-targets-control-v1'
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
STORE=OUT/NAME
PILOT=Path('S:/GTOpen-research/weighted-complete-river-training-pilot-v1')
PARENT_REG=OUT/'river-matched-training-pilot-v1-registration.json'
PARENT_SHA='1dec3f979f863c8fafa18a905f897f64c824ba110a7320858795b4fae1e9924b'
CONTEXT=OUT/'bb-context-candidate.json'
CATALOG=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
MATRIX=OUT/'preflop-allin-matrix-control-v1-matrix.json'
EXE=ROOT/'target/release/examples/hu_river_two_stage_stream_v1.exe'
NATIVE_SHA='8dc03e7dd21cbcfc6ed1fd8f7c068137e0fbcb6eebfc9de329744165f79bba62'
LIMIT=32_000_000
FIXTURES=(
    ('A-river','generation-0079-bb713ca9','6dbaecaaf825f95e48a5379e74de9d2acd0efde3b37ae0220aa1158b86abcfa5'),
    ('B-river','generation-0080-0c20ee23','a27bc224ae369b2a9196807e0661b39294b1f214fd8ec4aa9c2d1d1f5a0e0630'))


def read(path):return json.loads(Path(path).read_bytes())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def size():return sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())


class CandidatePolicy(CPUCurrentPolicy):
    def prepare(self,queries):return subset_prepare(self,queries)


def specification():
    assert sha(PARENT_REG)==PARENT_SHA and sha(EXE)==NATIVE_SHA
    reg=read(PARENT_REG);source=CONTEXT.read_text()
    paths=[Path(__file__),PARENT_REG,CONTEXT,CATALOG,MATRIX,EXE]
    fixtures=[]
    for arm,directory,expected in FIXTURES:
        folder=PILOT/arm/directory;metric_path=folder/'metrics.json'
        assert sha(metric_path)==expected
        metric=read(metric_path);ref=metric['used_model'];part=folder/'batch-00'
        model_path=PILOT/arm/'objects'/ref['file'];assert sha(model_path)==ref['sha256']
        for relative,digest in metric['subbatches'][0]['artifacts'].items():
            path=part/relative;assert sha(path)==digest;paths.append(path)
        paths.extend((metric_path,model_path,folder/'source-generation.json'))
        old=read(part/'conditional/evidence.json')
        assert old['policy_id']==ref['sha256'] and old['native_sha256']==NATIVE_SHA
        assert metric['iteration']==ref['generation']+1
        fixtures.append(dict(arm=arm,folder=str(folder),model=str(model_path),
            policy_id=ref['sha256'],iteration=metric['iteration'],case_id=old['case_id'],
            root_config=reg['arms'][arm]['config']['board_root']))
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).is_relative_to(TOOLS) and Path(path).suffix=='.py':paths.append(Path(path))
    return dict(format=1,inputs={str(p):sha(p) for p in paths},fixtures=fixtures,
        maximum_seconds=600,maximum_retained_bytes=LIMIT,global_allocated_cap=800_000_000_000,
        scope='First complete conditional-target batch of A-river update 79 and B-river update 80. Candidate-only replays against saved originals.',
        required='Identical target bindings/rows, native requests/output hashes, policy arrays, posterior plans, evidence and overlay.',
        timing='Descriptive candidate replay under concurrent load; not a paired full-update benchmark.',
        gpu_used=False,training_changed=False,new_deals=0,production_modified=False)


def main(run=False):
    spec=specification()
    if not run:
        print(json.dumps(dict(ready=True,fixtures=len(spec['fixtures']),gpu_used=False)));return
    assert not any(p.exists() for p in (REG,RESULT,STORE))
    began=time.monotonic();last=0.;peak_rss=0
    def guard():
        nonlocal last,peak_rss
        now=time.monotonic();assert now-began<600
        if now-last<2:return
        assert production_available() and psutil.virtual_memory().available>32_000_000_000
        assert psutil.cpu_percent(interval=.2)<60
        peak_rss=max(peak_rss,psutil.Process().memory_info().rss)
        assert peak_rss<2_000_000_000 and size()<LIMIT
        last=time.monotonic()
    guard()
    # Measure the active study first: later allocation already present in the
    # global inventory is then conservatively counted twice, never subtracted.
    active=study_measure(Path('S:/GTOpen-research/weighted-complete-river-continuation-v1'))
    remaining=max(0,60_000_000_000-active['allocated_file_bytes'])+4_000_000_000
    inventory=measure();allocated=sum(row['allocated_file_bytes'] for row in inventory)
    assert allocated+remaining+LIMIT<800_000_000_000
    spec['admission']=dict(allocated_bytes=allocated,inventory=inventory,
        active_study_measurement=active,additional_reserved_bytes=remaining+LIMIT)
    save(REG,spec);STORE.mkdir()
    result=dict(format=1,passed=False,registration_sha256=sha(REG),started_unix=time.time(),cases=[])
    try:
        source=CONTEXT.read_text();matrix=AllinMatrix(read(MATRIX),source)
        weights=PhysicalDeals(source,mode='full_deck',seed=0).weights
        entry=[{tuple(map(int,p)):float(w) for p,w in zip(PAIRS,row)} for row in weights]
        for fixture in spec['fixtures']:
            guard();folder=Path(fixture['folder']);original=folder/'batch-00';old=original/'conditional'
            engine=CandidatePolicy(read(fixture['model']),source,catalog_source=CATALOG.read_text(),
                matrix_sha256=sha(MATRIX),entry_mass=matrix.btn_mass,root_config=fixture['root_config'])
            generation=DealWeightGeneration(read(folder/'source-generation.json'),source)
            destination=STORE/fixture['arm'];started=time.perf_counter()
            overlay,evidence=generate(read(original/'queries.json'),read(original/'updates.json'),
                read(original/'policies.json'),read(original/'action-trace.json'),generation=generation,
                start=0,iteration=fixture['iteration'],policy_id=fixture['policy_id'],case_id=fixture['case_id'],
                engine=engine,entry=entry,executable=EXE,context_path=CONTEXT,folder=destination,guard=guard,write=save)
            seconds=time.perf_counter()-started
            assert overlay==read(old/'overlay.json'),'Changed overlay or binding'
            assert evidence==read(old/'evidence.json'),'Changed target evidence or plans'
            produced={p.name for p in destination.iterdir() if p.is_file()}
            expected={p.name for p in old.iterdir() if p.is_file()}
            assert produced==expected
            for name in sorted(produced):
                assert sha(destination/name)==sha(old/name),'Changed artifact: '+name
                if name.endswith('-policies.npz'):
                    with np.load(destination/name,allow_pickle=False) as a,np.load(old/name,allow_pickle=False) as b:
                        assert set(a.files)==set(b.files)
                        for key in a.files:
                            assert a[key].dtype==b[key].dtype and a[key].shape==b[key].shape
                            assert a[key].tobytes()==b[key].tobytes()
            report=dict(arm=fixture['arm'],iteration=fixture['iteration'],model_generation=fixture['iteration']-1,
                river_rows=len(overlay['rows']),chunks=len(evidence['chunks']),artifacts=len(produced),
                all_artifact_bytes_identical=True,seconds=seconds,
                retained_bytes=sum(p.stat().st_size for p in destination.iterdir() if p.is_file()))
            result['cases'].append(report);print(json.dumps(report),flush=True)
            del engine,generation,overlay,evidence;gc.collect()
        for path,digest in spec['inputs'].items():assert sha(path)==digest,path
        guard();result.update(passed=True,gpu_used=False,training_changed=False,accuracy_claim=False,
            next_requirement='Complete update/checkpoint parity before adoption; queued separately after live study.')
    except Exception as error:
        result.update(error=str(error),traceback=traceback.format_exc())
    result.update(seconds=time.monotonic()-began,finished_unix=time.time(),
        retained_bytes=size(),boundary_sampled_rss_bytes=peak_rss)
    save(RESULT,result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('cases','traceback')}),flush=True)
    if not result['passed']:raise RuntimeError(result['error'])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true')
    main(parser.parse_args().run)
