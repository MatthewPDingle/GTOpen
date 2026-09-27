"""Read-only snapshot of an immutable completed prefix of the live evaluation.

Replays the exact chance stream and sequential accumulator without producing
intervals or printing poker outcomes. Never stops or modifies the live worker.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import hashlib
import json
from pathlib import Path
import sys
import time
from concurrent.futures import ThreadPoolExecutor
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from sampled_physical_deals_v1 import PhysicalDeals
from crossed_complete_policy_comparison_v1 import CompletePolicyComparison
import owned_columnar_evaluation_archive_v1 as archive
from crossed_profile_decoder_fast_candidate_20260927 import decode
from reboot_research_idle_v1 import idle

OLD = 'showdown-composite-evaluation-study-v1'
PREFIX = 'showdown-evaluation-resume-snapshot-v1'


def restore_batch(entry):
    name, expected = entry
    store = Path('S:/GTOpen-research')/OLD
    mp = store/(name+'.manifest.json')
    assert sha(mp) == expected
    manifest = read(mp)
    raw = archive.restore(store/(name+'.xz'), manifest, guard=lambda: None)
    summary = json.loads(raw['summary.json'])
    assert set(summary['artifacts']) == set(raw)-{'summary.json'}
    for member, h in summary['artifacts'].items():
        assert hashlib.sha256(raw[member]).hexdigest() == h
    return name, json.loads(raw['query-batch.json']), summary, hashlib.sha256(raw['summary.json']).hexdigest(), manifest['packed_sha256']


def main():
    rp = OUT/f'{PREFIX}-registration.json'; result_path = OUT/f'{PREFIX}-result.json'
    assert not rp.exists() and not result_path.exists()
    admission = read(OUT/f'{OLD}-admission.json')
    process = psutil.Process(admission['worker_pid'])
    assert process.is_running() and '--worker' in process.cmdline()
    assert any(Path(a).name == 'hu_showdown_composite_evaluation_v1_20260927.py' for a in process.cmdline())
    original_rp = OUT/f'{OLD}-registration.json'; reg = read(original_rp)
    assert sha(original_rp) == admission['registration_sha256']
    for path, h in reg['inputs'].items():assert sha(path) == h
    store = Path(reg['store'])
    # Stay two batches behind the latest published manifest, avoiding any live
    # publication/release boundary. New suffix batches cannot alter this prefix.
    available = sorted(store.glob('test-*.manifest.json'))
    selected = available[:-2]
    assert len(selected) >= 2
    names = [f'test-{i*32:06d}' for i in range(len(selected))]
    assert [p.name for p in selected] == [n+'.manifest.json' for n in names]
    manifests = {name:sha(p) for name,p in zip(names,selected)}
    inputs = {str(p):sha(p) for p in (Path(__file__),
        ROOT/'tools/research/crossed_profile_decoder_fast_candidate_20260927.py',original_rp)}
    registration = dict(inputs=inputs,original_registration_sha256=sha(original_rp),
        completed_deals=len(names)*32,manifests=manifests,maximum_seconds=1800,
        snapshot_only=True,production_modified=False,interim_analysis_allowed=False)
    save(rp,registration)
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        assert time.monotonic()-started < 1800
        if time.monotonic()-last>2:
            assert idle() and psutil.virtual_memory().available>20_000_000_000
            last=time.monotonic()
    source=(OUT/'bb-context-candidate.json').read_text();context=json.loads(source)
    sampler=PhysicalDeals(source,mode='full_deck',seed=9267201)
    assert sampler.checkpoint()==read(store/'sampler-initial.json')
    comparison=CompletePolicyComparison(stack=context['config']['stack'],dead_money=context['dead_money'],deals=65536)
    summaries={};packed_hashes={}
    # Candidate decoder only in this isolated process; exact archive byte/hash
    # validation remains the original implementation. The final review uses
    # the independently frozen old decoder across every batch.
    archive.decode_profiles=decode
    with ThreadPoolExecutor(max_workers=2) as pool:
        for i,(name,batch,summary,digest,packed) in enumerate(pool.map(restore_batch,manifests.items())):
            guard();assert name==names[i]
            expected=dict(format=2,batch_id=f'{OLD}-{name}',seed=0,query_limit=100000,deals=sampler.sample(32)['deals'])
            assert batch==expected and summary['deals']==32
            comparison.add(summary['values'])
            summaries[name]=digest;packed_hashes[name]=packed
            if i%64==0:print(json.dumps(dict(verified_prefix_deals=(i+1)*32,total=len(names)*32)),flush=True)
    for p,h in inputs.items():assert sha(p)==h
    for name,h in manifests.items():assert sha(store/(name+'.manifest.json'))==h
    checkpoint=dict(sampler=sampler.checkpoint(),series=[dict(series=s.series,count=s.count,mean=s.mean,m2=s.m2) for s in comparison.series])
    checkpoint_path=OUT/f'{PREFIX}-checkpoint.json';save(checkpoint_path,checkpoint)
    save(result_path,dict(passed=True,registration_sha256=sha(rp),checkpoint_sha256=sha(checkpoint_path),
        completed_deals=len(names)*32,batch_summary_hashes=summaries,packed_sha256=packed_hashes,
        seconds=time.monotonic()-started,production_modified=False,live_worker_modified=False,
        scope='Immutable prefix, chance replay and sequential accumulator checkpoint; no interim interval or accuracy claim.'))


if __name__=='__main__':
    assert sys.argv[1:]==['--run'];main()
