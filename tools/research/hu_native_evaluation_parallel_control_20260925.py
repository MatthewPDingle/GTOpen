"""Bounded CPU throughput control on authenticated, previously evaluated batches.

No sampling, inference, fitting, GPU access, production changes, or live-source
changes. Repeated batches measure implementation throughput, not more evidence.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle

PREFIX = 'native-evaluation-parallel-control-v1'
STORE = Path('T:/GTOpen-research')/PREFIX
OLD = Path('T:/GTOpen-research/root-retained-wider-study-v1/evaluation')


def main():
    start = time.monotonic()
    assert not STORE.exists() and idle()
    def guard():
        assert time.monotonic()-start < 600, 'Control deadline'
        assert psutil.virtual_memory().available > 20_000_000_000
        assert psutil.disk_usage('T:/').free > 40_000_000_000
    guard()
    context = OUT/'bb-context-candidate.json'
    executable = ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    outer = OUT/'root-retained-wider-study-v1-evaluation.json'
    detail_path = OLD/'result.json'
    detail = read(detail_path)
    assert read(outer)['result_sha256'] == sha(detail_path)
    sources = []
    paths = [Path(__file__).resolve(), context, executable, outer, detail_path,
             ROOT/'tools/research/sampled_physical_root_evaluation_v1.py',
             ROOT/'tools/research/reboot_research_idle_v1.py']
    for name in ('train-000000', 'train-010752'):
        folder = OLD/name
        summary_path = folder/'summary.json'
        assert sha(summary_path) == detail['batch_summary_hashes'][name]
        summary = read(summary_path)
        for filename in ('conditional-batch.json', 'profiles.json', 'native.json'):
            assert sha(folder/filename) == summary['artifacts'][filename]
            paths.append(folder/filename)
        paths.append(summary_path)
        batch, profiles = read(folder/'conditional-batch.json'), read(folder/'profiles.json')
        assert len(batch['deals']) == 64 and len(profiles['profiles']) == 5
        assert profiles['context_source'] == context.read_text()
        assert profiles['batch_source'] == (folder/'conditional-batch.json').read_text()
        sources.append(folder)
    inputs = {str(p):sha(p) for p in paths}
    registration = OUT/f'{PREFIX}-registration.json'
    save(registration, dict(inputs=inputs, source_batches=list(map(str,sources)),
        concurrency_order=[1,2,4,4,2,1], jobs_per_stage=16, jobs_alternate_batches=True,
        maximum_seconds=600, maximum_output_bytes=50_000_000,
        maximum_owned_native_workers=4, cpu_only=True, fresh_holdout=False,
        scope='Repeated native evaluation of two frozen 64-deal, five-profile batches. Exact native output hashes must match prior evaluation. Concurrent GPU training remains unchanged; no study-strength claim.'))
    STORE.mkdir()
    rows = []
    error = None
    try:
        for stage, concurrency in enumerate((1,2,4,4,2,1)):
            guard(); assert idle(), 'Production busy'
            directory = STORE/f'stage-{stage:02d}-workers-{concurrency}'
            directory.mkdir()
            def job(index):
                guard()
                source = sources[index%2]
                output = directory/f'job-{index:02d}.json'
                before = time.monotonic()
                process = subprocess.run([str(executable), str(context),
                    str(source/'conditional-batch.json'), str(source/'profiles.json'), str(output)],
                    capture_output=True, text=True, timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW)
                elapsed = time.monotonic()-before
                assert process.returncode == 0, process.stderr[-2000:]
                assert sha(output) == inputs[str(source/'native.json')], 'Native output changed'
                guard()
                return dict(job=index, source=source.name, seconds=elapsed, sha256=sha(output))
            before = time.monotonic()
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                jobs = list(pool.map(job,range(16)))
            elapsed = time.monotonic()-before
            assert idle(), 'Production became busy'
            row = dict(stage=stage,workers=concurrency,jobs=jobs,
                       elapsed_seconds=elapsed,jobs_per_second=16/elapsed)
            rows.append(row)
            print(json.dumps({k:v for k,v in row.items() if k!='jobs'}), flush=True)
        for p,h in inputs.items(): guard(); assert sha(p) == h,p
        size = sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())
        assert size < 50_000_000
        totals = {n:sum(r['elapsed_seconds'] for r in rows if r['workers']==n) for n in (1,2,4)}
        result = dict(passed=True,registration_sha256=sha(registration),stages=rows,
            combined_seconds_by_workers=totals,speedup_over_serial={n:totals[1]/totals[n] for n in (1,2,4)},
            native_outputs_byte_identical=True,logical_bytes=size,seconds=time.monotonic()-start,
            gpu_used=False,production_modified=False,live_trial_modified=False,accuracy_qualified=False,
            scope='Native evaluator throughput on repeated saved batches under concurrent training. No full-pipeline speedup or extra independent poker samples.')
        save(OUT/f'{PREFIX}-result.json',result)
        print(json.dumps({k:v for k,v in result.items() if k!='stages'}), flush=True)
    except BaseException as exc:
        error = repr(exc)
        raise
    finally:
        save(OUT/f'{PREFIX}-status.json',dict(state='failed' if error else 'complete',error=error,
             completed_stages=len(rows),seconds=time.monotonic()-start,production_modified=False))


if __name__ == '__main__':
    main()
