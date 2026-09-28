"""Read back finished scheduling evidence; no training or poker inference."""
import hashlib
import json
from pathlib import Path
import time
import psutil
from board_prefix_publication_v1 import atomic_json

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='two-arm-training-throughput-control-v1';STORE=Path('S:/GTOpen-research')/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
REVIEW=OUT/(NAME+'-readback-v1.json');REPORT=OUT/'TWO-ARM-TRAINING-THROUGHPUT-FINDINGS.md'


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not REVIEW.exists() and not REPORT.exists(),'Preserve earlier readback'
    start=time.monotonic();reg=read(REG);result=read(RESULT);parent=reg['parent']
    try:assert psutil.Process(parent['pid']).create_time()!=parent['created'],'Wait for coordinator exit'
    except psutil.NoSuchProcess:pass
    assert result['passed'] and result['complete'] and result['registration_sha256']==sha(REG)
    assert result['job_final']['active_processes']==0 and not result['production_modified']
    assert not result['learning_bank_modified'] and result['new_evaluation_deals']==0
    for path,digest in reg['inputs'].items():assert sha(path)==digest,path
    cases=result['cases'];assert len(cases)==4 and {r['case'] for r in cases}==set(reg['cases'])
    artifacts=0
    for row in cases:
        folder=STORE/row['case'];proof=read(folder/'complete.json');timed=read(folder/'timed.json')
        assert proof==row and row['registration_sha256']==sha(REG)
        assert sha(folder/'timed.json')==row['timed_sha256']
        for k,v in timed.items():assert row[k]==v
        assert sha(row['metrics'])==row['metrics_sha256']
        metric=read(row['metrics']);oracle=read(reg['oracles'][row['arm']]['metrics'])
        assert row['checkpoint']==metric['checkpoint']==oracle['checkpoint']
        for field in ('used_model','next_model','subbatches','exact_btn_delta','reservoirs'):
            assert metric[field]==oracle[field],field
        assert row['exact_saved_state'] and row['exact_numeric_fit_metrics'] and row['exact_artifacts']
        for ref in (row['checkpoint'],metric['next_model']):
            assert sha(folder/'objects'/ref['file'])==ref['sha256'];artifacts+=1
        for sub in metric['subbatches']:
            for name,digest in sub['artifacts'].items():
                assert sha(Path(row['metrics']).parent/f"batch-{sub['chunk']:02d}"/name)==digest
                artifacts+=1
        assert row['external_update_seconds']==(row['end_ns']-row['start_ns'])/1e9
        assert row['peak_cuda_reserved_bytes']<=reg['cuda_budget_bytes_per_arm']
    serial=[r for r in cases if r['case'].startswith('serial-')]
    parallel=[r for r in cases if r['case'].startswith('concurrent-')]
    total=sum(r['external_update_seconds'] for r in serial)
    span=(max(r['end_ns'] for r in parallel)-min(r['start_ns'] for r in parallel))/1e9
    summary=result['comparison']
    assert summary['serial_sum_seconds']==total and summary['concurrent_makespan_seconds']==span
    assert summary['serial_over_concurrent']==total/span
    assert summary['percent_less_elapsed']==100*(1-span/total)
    # Verification barrier must follow both timed calls.
    for group in reg['groups']:
        rows=[r for r in cases if r['case'] in group]
        end=max(r['end_ns'] for r in rows)
        assert all(read(STORE/r['case']/'verify.json')['release_ns']>=end for r in rows)
    admission=read(STORE/'admission.json')
    assert admission['allocated_bytes']+admission['reserved_bytes']<=reg['global_allocated_cap']
    assert sum(r['allocated_file_bytes'] for r in result['global_final'])<=reg['global_allocated_cap']
    review=dict(passed=True,source_result_sha256=sha(RESULT),registration_sha256=sha(REG),
        readback_source_sha256=sha(__file__),cases=4,artifact_hashes_checked=artifacts,
        timing_arithmetic_recomputed=True,verification_barriers_checked=True,
        coordinator_exited=True,final_owned_job_active_processes=0,
        seconds=time.monotonic()-start,poker_inference_repeated=False,gpu_used=False)
    atomic_json(REVIEW,review)
    rows='\n'.join(f"| {r['case']} | {r['external_update_seconds']:.3f} | {r['pipeline_seconds']:.3f} | {r['gpu_guard_wait_seconds']:.3f} |" for r in cases)
    decision=('The concurrent pair was faster on this fixture. Retain this bounded scheduler as an option for a future prospectively specified study; this single pair does not establish a universal speedup.'
              if span<total else 'The concurrent pair was not faster on this fixture. Retain serial scheduling; do not adopt concurrency merely to raise utilization.')
    report=f'''# Two independent training updates: serial versus concurrent

All four cases reproduced their original archived update-79 results exactly.
The fresh serial pair took **{total:.3f} seconds** in the measured update calls;
the concurrent pair finished in **{span:.3f} seconds**: **{summary['percent_less_elapsed']:.2f}% less elapsed time**
({summary['serial_over_concurrent']:.3f} times throughput for this pair).

{decision}

| Case | External update seconds | Pipeline seconds | Recorded GPU guard wait seconds |
|---|---:|---:|---:|
{rows}

Concurrent starts differed by {summary['concurrent_start_skew_seconds']:.6f} seconds.
The call intervals overlapped for {summary['concurrent_overlap_seconds']:.3f} seconds.
These externally timed calls include the same initial update guard and final CUDA
synchronization. Setup and readback are excluded from both comparisons. The
readback barrier was verified to follow both concurrent updates.

Whole invocation took {result['seconds']:.1f} seconds, including admission,
storage scans, source loading, all four updates and their verification. This is
not a production-solve benchmark. Serial-first order, OS caching, guard checks
and other system load can affect timing. There is one pair, not repeated trials.
GPU guards can observe the other owned child, so their wait is not classified
as external-only contention. A slower individual concurrent update can coexist
with a shorter overall pair makespan.

## Correctness and resource evidence

Each child checked full checkpoint/restored-state identity, fitted networks and
numeric fitting results, ordered reservoirs, played-model membership, source
deals/action streams and subbatch artifacts against the original saved oracle.
The independent artifact readback checked {artifacts} referenced artifact hashes
and recomputed timing arithmetic. It did not independently rerun poker inference.

At most two coordinators ran, each with eight physical and four board workers.
Each had a 2GB CUDA allocation/reservation cap. Maximum reported per-child CUDA
reservation was {max(r['peak_cuda_reserved_bytes'] for r in cases)/1e9:.3f} GB.
The existing light-desktop sharing checks and production priority were retained.
The coordinator has exited; its final owned-job active-process count was zero.

Retained new evidence: {result['storage']['logical_bytes']/1e9:.3f} GB logical,
{result['storage']['allocated_file_bytes']/1e9:.3f} GB allocated. Final global
research allocation: {sum(r['allocated_file_bytes'] for r in result['global_final'])/1e9:.3f} GB,
within the 800GB cap. Historical and failed evidence was preserved.

## Next research step

Return to evaluation precision before another large training run. The proposed
reach-weighted design passed exact-rational finite-domain checks, but its poker
adapter and floating error bounds are still unqualified. Reuse the existing
6,630-row native preflop holding catalog; it covers every preflop decision in
this context, unlike the smaller first-action catalog. Reconstruct and verify
own-action histories before extracting all complete-bank preflop policies.

This scheduling result supplies no evidence of more accurate ranges, stronger
play, cross-stack transfer or multiway accuracy. No production changes,
deployment or GitHub push were made.

Result SHA256: {sha(RESULT)}.
Registration SHA256: {sha(REG)}.
Readback: {REVIEW.name}.
'''
    with REPORT.open('x',encoding='utf-8',newline='\n') as f:f.write(report)
    print(json.dumps(review),flush=True)


if __name__=='__main__':main()
