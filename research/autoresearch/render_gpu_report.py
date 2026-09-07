"""Write the final GPU pass report from audited measurement records."""
import collections
import json
import re
from pathlib import Path
import lab

config = json.loads((lab.HERE / 'run.json').read_text())
end_time = config.get('pass_completed_utc', config['pass_deadline_utc'])[11:16]
validation = json.loads((lab.HERE / 'gpu-validation.json').read_text())
rows = {r['id']: r for r in lab.rows()}
current = [r for r in rows.values() if r['utc'] >= config['pass_started_utc']]
families = {re.match(r'E\d+', r['id'])[0] for r in current
            if r['status'] == 'keep' and r['id'].startswith('E')}

def table(items):
    out = ['| Workload / metric | Before | Final | Reduction | Evidence |',
           '|---|---:|---:|---:|---|']
    for label, before, after, metric, unit in items:
        a, b = rows[before]['metrics'][metric], rows[after]['metrics'][metric]
        out.append(f'| {label} | {a:,.3f} {unit} | {b:,.3f} {unit} | {(1-b/a)*100:.1f}% | [{before}](raw/{before}.log) / [{after}](raw/{after}.log) |')
    return '\n'.join(out)

targets = table([
    ('Preflop, six seats', 'B034', 'G001', 'preflop.6.target_seconds', 's'),
    ('Preflop, eight seats', 'B034', 'G001', 'preflop.8.target_seconds', 's'),
    ('Postflop, rainbow flop', 'B034', 'G002', 'postflop.Ks7h2d.target_seconds', 's'),
    ('Postflop, two-tone flop', 'B034', 'G002', 'postflop.Ks7s2d.target_seconds', 's'),
])
steps = table([
    *[(f'Preflop, {s} seats', 'B034', 'G001', f'preflop.{s}.iteration_ms', 'ms') for s in [6,8,9]],
    ('Postflop, rainbow flop', 'B035', 'G005', 'postflop.Ks7h2d.iteration_ms', 'ms'),
    ('Postflop, two-tone flop', 'B035', 'G005', 'postflop.Ks7s2d.iteration_ms', 'ms'),
])
memory = table([
    *[(f'Preflop {s} seats: GPU allocation', 'B034', 'G003', f'preflop.{s}.allocated_vram_mb', 'MB') for s in [6,8]],
    ('Two-tone compressed: GPU allocation', 'B035', 'G005', 'postflop.memory.cold.compressed.allocated_vram_mb', 'MB'),
    ('Rainbow compressed: GPU allocation', 'B035', 'G005', 'postflop.memory.rainbow.cold.compressed.allocated_vram_mb', 'MB'),
    ('Two-tone compressed: cold live host RAM', 'B035', 'G005', 'postflop.memory.cold.compressed.host_live_mb', 'MB'),
    ('Two-tone compressed: warm live host RAM', 'B035', 'G005', 'postflop.memory.warm.compressed.host_live_mb', 'MB'),
])
transfers = table([
    ('Two-tone compressed: cold initialization', 'B035', 'G005', 'postflop.memory.cold.compressed.init_ms', 'ms'),
    ('Two-tone compressed: warm initialization', 'B035', 'G005', 'postflop.memory.warm.compressed.init_ms', 'ms'),
    ('Two-tone compressed: warm full download', 'B035', 'G005', 'postflop.memory.warm.compressed.sync_ms', 'ms'),
    ('Rainbow compressed: cold initialization', 'B035', 'G005', 'postflop.memory.rainbow.cold.compressed.init_ms', 'ms'),
    ('Rainbow compressed: warm full download', 'B035', 'G005', 'postflop.memory.rainbow.warm.compressed.sync_ms', 'ms'),
])
evaluations = table([
    ('Two-seat preflop: first check', 'B035', 'G005', 'preflop.2.first_check_ms', 'ms'),
    ('Two-seat preflop: steady checks', 'B035', 'G005', 'preflop.2.steady_check_ms', 'ms'),
    ('River postflop: first check', 'B035', 'G005', 'postflop.Ks7h2dQhTc.first_check_ms', 'ms'),
    ('River postflop: steady checks', 'B035', 'G005', 'postflop.Ks7h2dQhTc.steady_check_ms', 'ms'),
])

report = f'''# GPU research pass 2

Approximately three-hour pass: 7 September 2026, 03:57–{end_time} UTC. The retained changes are
in the shared checkout. This pass found **{len(families)} retained improvement
families** across preflop CUDA, postflop CUDA, and GPU memory/transfers.
No precision, solver model, bet menu, target, or learning algorithm was changed.

[Tracking webpage](index.html) · [All measurements](results.tsv) ·
[Validation evidence](gpu-validation.json) · [Retained source patch](patches/gpu-pass-retained.patch) ·
[Earlier progress notes](gpu-pass-milestones.md) · [Next-pass handoff](gpu-pass-handoff.md) · [Pass 1 report](report.md)

![Measured progress](gpu-pass-progress.png)

## Time to the same accuracy

These are fresh comparisons with the implementation at the start of this pass,
commit `{config['pass_baseline_commit'][:8]}`, rebuilt using the same frozen workloads.
Preflop still stops at exactly **175 / 125 iterations**, with identical complete
arena, gap, and EV fingerprints. Postflop still stops at **200 / 200 / 60 iterations**
and the same final exploitability values, using the unchanged 0.3%-pot target.

{targets}

The time-to-target workload excludes initial tree construction and GPU upload.
Lifecycle costs are measured separately below. Timings vary with machine state;
the report uses fresh controls, and the ledger retains earlier repetitions.

## Iteration throughput

The fixed workload uses five warm-up iterations followed by three measured
20-iteration batches. Entries are the median batch time per iteration.

{steps}

The nine-seat workload contains 1,825,426 nodes. Two- and three-seat trees are
also checked: the adaptive launch policy keeps larger blocks for narrow levels,
so the large-tree improvement does not impose the rejected universal-64-thread
policy's small-tree latency cost.

## GPU and host memory

{memory}

MB are decimal. GPU allocation is measured through device free-memory deltas.
Live host RAM is the Windows process working set after the specified lifecycle;
it includes driver and allocator behavior and is distinct from GPU VRAM.
The default application uses compressed CPU stores. F32 stores retain direct
full action arenas when the VRAM budget permits; a tight budget can use the exact
compact representation. Trees with less than 5% action-storage savings skip packing.

## Initialization and readback

{transfers}

Independent repeat G003 covers the same final lifecycle. Retained transfer
changes reuse a pinned staging allocation and encode independent node blocks
in parallel on download. Parallel chunk decoding on upload was rejected after
it made every measured compressed initialization case slower.

The fixed report-adaptation workload also retained its exact 80-iteration result:
{rows['B028']['metrics']['reports.adaptation_seconds']:.3f}s in B028 to
{rows['G004']['metrics']['reports.adaptation_seconds']:.3f}s in G004. B028 is an
earlier within-pass control, not the fresh pass-start comparison used above.

## Repeated evaluation

{evaluations}

Steady checks are the median after the first eager check and graph-capture check.
First-check timings are listed separately; short startup measurements are noisier
and graph reuse benefits repeated checks most. Large-flop checks are also recorded
in the tracker, without claiming the small-river percentage applies to them.

## What changed

| Research path | Retained implementation families |
|---|---|
| Preflop CUDA | Separate terminal entry points for common seat counts; common-action specialization; reusable evaluation graphs and batched root downloads; block-shared terminal uniforms for generic seat counts; an exact 128-thread reach-mass reduction; adaptive 256/64-thread non-reduction launches. |
| Postflop CUDA | Common-action specialization in both sweeps; reusable evaluation graphs, with the original eager first-check path and invalidation when lock buffers change. |
| GPU memory and transfers | Remove the preflop sigma arena; reuse preflop action-value scratch across levels; pack visited postflop action arenas while preserving inactive state; reuse postflop action/chance CFV scratch; reuse pinned staging and parallelize compressed readback. |

E021–E038 cover 18 hypothesis families. Four were rejected entirely: universal
shared terminal uniforms, postflop card-run loops, explicit equity-loop unrolling,
and parallel upload decoding. Additional refinements were rejected when a better
variant won. All measurements, including failures, remain in the ledger.

## Accuracy and regression validation

The final combined source passed **124 CPU tests, 42 GPU tests, and the server
continuation test** in the actual shared checkout. The separate final report run
also passed its benchmark and continuation test. Source hashes attest which code
the suites compiled; all frozen workload hashes are checked in both checkouts.

The combined research runs reproduce:

- Seven complete preflop arena/gap/EV fingerprints at 2/3/5/6/7/8/9 seats.
- 48 preflop variants covering seat counts, menus, frozen players, hero and locks.
- Exact normal-versus-tight-cache preflop results and unchanged target stopping states.
- 24 original postflop saved-state fingerprints and 24 action-menu/algorithm/lock cases.
- 112 resume snapshots across cold/warm, F32/compressed and isomorphism on/off cases,
  including save bytes, CPU query materialization, lock updates, and resumed EVs.
- Exact large lifecycle evaluation bits and repeated first/capture/steady evaluation results.
- Focused scratch-lifetime and signed-zero tests, plus the original CUDA/CPU equivalence suites.

The audit records **{len(validation['checks'])} successful source/numerical/suite checks**
across retained and final runs. This demonstrates unchanged results on the tested
coverage; performance percentages are specific to these workloads and hardware.

## Measurement record and limits

Hardware: RTX 3090 24 GB, Ryzen 5950X, 64 GB RAM, 16 solver threads, Windows.
GPU benchmarks ran serially. Fresh original-code controls B034/B035 bracket the
final validation phase; G001–G005 run the combined retained implementation.
Repeated-check graphs improve steady evaluation, especially small river solves;
first-check and capture timings are recorded separately and remain noisier.

One initial E026 measurement reused an older Cargo artifact after a copy preserved
its timestamp. That measurement is explicitly invalidated and excluded from plots.
The runner now hashes compiler inputs and refreshes changed input timestamps.
E026A and later runs are rebuilt measurements. E038's commit attribution was
corrected in an append-only audit event; its source bytes were unchanged during
the run, and the experiment was rejected on performance grounds.

This pass recorded **{len(current)} runs**; the cumulative tracker contains
**{validation['metrics']} metric graphs**, with individual histories and per-chart
run-to-experiment tables. Gray points are controls or metrics collected alongside
another target; blue points are retained targeted results; crosses are rejected
or failed trials; green is the best eligible observation, not an average.

The source is ready for the normal application rebuild/restart. The existing live
application and its saved/current sessions were left running unchanged. Changes
remain reviewable in the shared working tree; nothing was pushed.
'''
(lab.HERE / 'gpu-pass.md').write_text(report, encoding='utf-8', newline='\n')
print('Wrote final GPU report from validated measurements')
