"""CPU native-model integration of compact evaluation, using an old fixture.

Reuses its exact two-model bank, chance streams and counts. No active trial
models, fresh validation stream, GPU work, or original-source cleanup.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import shutil
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from root_retained_wider_inputs_v1 import admitted
from root_retained_policy_v1 import RootRetainedCpuBank64
from wider_root_evaluation_v3 import run
from wider_root_readback_v3 import review
from archived_evaluation_reader_v1 import ArchivedEvaluationReader
from hu_root_retained_storage_admitted_study_20260924 import measure
from ntfs_research_storage_v1 import measure_tree
from reboot_research_idle_v1 import idle

PREFIX='archived-native-control-v1'
BASE=Path('T:/GTOpen-research')/PREFIX
STORE=BASE/'evaluation'
PRIOR='root-retained-wider-cpu-control-v1'
CAP=500_000_000


def main():
    started=time.monotonic();last_size=0.;maximum_observed=0
    def guard():
        nonlocal last_size,maximum_observed
        assert time.monotonic()-started<1200 and idle()
        assert psutil.virtual_memory().available>=20_000_000_000
        assert shutil.disk_usage('T:/').free>=40_000_000_000
        if BASE.exists() and time.monotonic()-last_size>5:
            size=sum(p.stat().st_size for p in BASE.rglob('*') if p.is_file())
            maximum_observed=max(maximum_observed,size);assert size<=CAP
            last_size=time.monotonic()
    guard();assert not BASE.exists()
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    old_reg_path=OUT/f'{PRIOR}-registration.json';old_result_path=OUT/f'{PRIOR}-result.json'
    prior,prior_result=read(old_reg_path),read(old_result_path);source=Path(prior['store'])
    assert prior_result['passed'] and prior_result['registration_sha256']==sha(old_reg_path)
    assert prior_result['result_sha256']==sha(source/'result.json')
    data=admitted(control=True);assert data['control_only'] and data['count']==2
    assert data['exact']==prior['exact'] and data['checkpoint']==prior['checkpoint']
    cfg=prior['config']
    assert cfg['per_class']==2 and cfg['test_deals']==128 and cfg['batch_size']==16
    bank=RootRetainedCpuBank64(data['models'],completed_iterations=2,
        weights_by_player=data['weights'],**data['bank_args'])
    sources={str(p):sha(p) for p in source.rglob('*') if p.is_file()}
    inputs=data['inputs']
    paths=[Path(__file__).resolve(),old_reg_path,old_result_path,
        *[ROOT/'tools/research'/n for n in ('root_retained_wider_inputs_v1.py','root_retained_policy_v1.py',
            'wider_root_evaluation_v3.py','wider_root_readback_v3.py','owned_batch_archive_v1.py',
            'sampled_evidence_archive_v1.py','archived_evaluation_reader_v1.py',
            'sampled_conditional_root_evaluation_v1.py','sampled_visible_hybrid_cpu64_v1.py')],
        ROOT/'target/release/examples/hu_sampled_bank_bridge.exe',
        ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe']
    inputs.update({str(p):sha(p) for p in paths})
    roots=measure();used=sum(r['allocated_file_bytes'] for r in roots)
    assert used+CAP+12_000_000_000+2_000_000_000<=800_000_000_000
    save(rp,dict(inputs=inputs,sources=sources,config=cfg,store=str(STORE),
        exact=data['exact'],checkpoint=data['checkpoint'],cache_sha256=data['cache'].sha256,
        storage_inventory=roots,maximum_new_bytes=CAP,reserved_queued_trial_bytes=12_000_000_000,
        maximum_seconds=1200,original_sources_unchanged=True,gpu_used=False,production_modified=False,
        scope='Repeat native CPU fixture through new compact pipeline; same old physical deals, not new validation.'))
    BASE.mkdir()
    result=run(data['context_path'],bank,data['cache'],data['exact'],cfg,STORE,guard,
        prior_response_path=data['prior_response_path'])
    reader=ArchivedEvaluationReader(STORE,result['archive_manifest_hashes'],
        external_files=[data['context_path'],data['prior_response_path']],guard=guard)
    audit=review(data['context_path'],STORE,cfg,data['exact'],data['cache'].sha256,guard,
        prior_response_path=data['prior_response_path'],read_artifact_json=reader.read_json,
        artifact_sha256=reader.sha256)
    assert audit==prior_result['independent_readback']
    old=read(source/'result.json');added={'archive_manifest_hashes','archive_owner_sha256','storage_encoding'}
    timing={'seconds','phase_timings'}
    assert {k:v for k,v in result.items() if k not in added|timing}=={k:v for k,v in old.items() if k not in timing}
    artifact_count=0
    for name in result['batch_summary_hashes']:
        for p in (source/name).iterdir():
            if p.is_file():
                assert reader.read_bytes(STORE/name/p.name)==p.read_bytes(),str(p)
                artifact_count+=1
    assert not any(p.is_dir() for p in (STORE/'.batch-work').iterdir())
    for p,h in {**inputs,**sources}.items():guard();assert sha(p)==h,p
    storage=measure_tree(BASE,guard);assert storage['logical_bytes']<=CAP
    outputs={str(p):sha(p) for p in BASE.rglob('*') if p.is_file()}
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),
        result_sha256=sha(STORE/'result.json'),independent_readback=audit,storage=storage,
        native_artifacts_byte_identical=artifact_count,unchanged_original_files=len(sources),
        maximum_observed_file_bytes=maximum_observed,output_files=outputs,seconds=time.monotonic()-started,
        gpu_used=False,production_modified=False,original_sources_unchanged=True,
        accuracy_qualified=False,scope='Native compact-pipeline integration on repeated control deals only.'))
    print(json.dumps(dict(passed=True,native_artifacts_byte_identical=artifact_count,
        storage=storage,seconds=time.monotonic()-started)),flush=True)


if __name__=='__main__':main()
