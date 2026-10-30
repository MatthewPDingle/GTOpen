"""Resource admission for the full BB context; no CUDA allocations or solves."""
import json
import shutil
import subprocess
import time
from pathlib import Path
import psutil
from hu_context_audit_20260922 import ROOT, OUT, audit, close, sha


def review_plan(path, context):
    d = json.loads(path.read_text())
    boards = d['manifest']['boards']
    leaves = [(i, n) for i, n in enumerate(context['nodes']) if n['leaf'] and n['leaf']['type'] == 'postflop']
    assert len(d['rows']) == len(boards)*len(leaves)
    work = [0]*11
    metadata = host = state = peak = 0
    for row, (board, (i, n)) in zip(d['rows'], ((b, leaf) for b in boards for leaf in leaves)):
        assert row['board'] == board['board'] and row['preflop_leaf'] == i
        close(row['pot'], n['pot'])
        close(row['effective_stack'], n['leaf']['effective_stack'])
        state += row['canonical_state_bytes']
        host += row['host_retained_payload_bytes']
        metadata += row['retained_gpu_payload_bytes']
        comp = row['workspace_components_bytes']
        assert len(comp) == len(work)
        peak = max(peak, metadata+sum(work)+sum(comp))
        work = [max(a, b) for a, b in zip(work, comp)]
    expected = dict(canonical_state_bytes=state, host_retained_payload_bytes=host,
                    ram_payload_total_bytes=host+state, retained_gpu_payload_bytes=metadata,
                    shared_gpu_workspace_bytes=sum(work), steady_gpu_payload_bytes=metadata+sum(work),
                    constructor_gpu_payload_upper_bytes=peak)
    assert expected == d['totals']
    assert d['device_allocated'] is False and d['strategies_evaluated'] is False
    return {'boards': len(boards), 'continuations': len(d['rows']), **expected}


def main():
    dest = OUT/'capacity-review.json'
    assert not dest.exists(), 'preserve evidence'
    context = json.loads((OUT/'bb-context-candidate.json').read_text())
    audit(context)
    paths = [OUT/'capacity-texture-result.json', OUT/'capacity-existing112-result.json']
    plans = [review_plan(p, context) for p in paths]
    prior = ROOT/'research/preflop-evolution/ssd-storage-20260920/strategic-weighted112-2000-v1-result.json'
    assert json.loads(paths[1].read_text())['manifest'] == json.loads(prior.read_text())['manifest']
    gib = 2**30
    gpu = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.total,memory.free', '--format=csv,noheader,nounits'], text=True).strip().splitlines()
    assert len(gpu) == 1
    total_mb, free_mb = map(int, gpu[0].split(','))
    ram_free = psutil.virtual_memory().available
    disk_free = shutil.disk_usage('S:/').free
    gpu_reserve, ram_reserve, disk_reserve = 3*gib, 20*gib, 32*gib
    full = plans[1]
    # Optimistic lower bound: no checkpoints, driver overhead or temporary arrays.
    minimum_spill = max(0, full['ram_payload_total_bytes'] - max(0, ram_free-ram_reserve))
    admission = {
        'constructor_payload_within_free_vram_reserve': full['constructor_gpu_payload_upper_bytes'] <= free_mb*2**20-gpu_reserve,
        'steady_payload_within_free_vram_reserve': full['steady_gpu_payload_bytes'] <= free_mb*2**20-gpu_reserve,
        'single_raw_state_spill_within_free_ssd_reserve': minimum_spill <= disk_free-disk_reserve,
    }
    inputs = [*paths, prior, OUT/'bb-context-candidate.json', OUT/'capacity-texture-probe.json',
              OUT/'capacity-existing112-manifest.json', Path(__file__),
              ROOT/'crates/solver/examples/hu_context_capacity.rs', ROOT/'crates/solver/Cargo.toml',
              ROOT/'target/release/examples/hu_context_capacity.exe']
    result = {'created_at_unix': time.time(), 'plans': plans,
              'resource_snapshot': {'total_vram_bytes': total_mb*2**20, 'free_vram_bytes': free_mb*2**20,
                                    'free_ram_bytes': ram_free, 'free_ssd_bytes': disk_free,
                                    'gpu_reserve': gpu_reserve, 'ram_reserve': ram_reserve, 'disk_reserve': disk_reserve},
              'minimum_single_state_spill_bytes': minimum_spill, 'admission_checks': admission,
              'forest_admitted': all(admission.values()), 'strategic_result': False,
              'inputs': {str(p.relative_to(ROOT)): sha(p) for p in inputs},
              'note': 'Conservative constructor bound is an admission guard, not a measured CUDA allocation. No checkpoints or transient RAM allowance in the spill lower bound. No existing evidence deleted; S and T capacities are not added together.'}
    with dest.open('x') as f:
        json.dump(result, f, indent=2)
    print(json.dumps({k: v for k, v in result.items() if k != 'inputs'}, indent=2))


if __name__ == '__main__':
    main()
