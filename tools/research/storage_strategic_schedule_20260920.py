"""Register segment resources from the completed full-size seed; never launch a solver."""
import json
import math
from pathlib import Path
import shutil
from storage_phase_run_20260920 import ROOT, OUT, EVIDENCE, read, sha


def schedule(seed, phase_rows):
    assert seed['seed_and_fresh_restore_passed'] and seed['restored_scientific_checkpoint_exact']
    iterations = [r['iteration_seconds'] for r in phase_rows if r['phase'] == 'iteration_complete']
    assert len(iterations) == 20 and all(math.isfinite(x) and x > 0 for x in iterations)
    evaluations = [phase_rows[i+1]['elapsed_seconds']-r['elapsed_seconds']
                   for i,r in enumerate(phase_rows) if r['phase'] == 'evaluation_start']
    assert len(evaluations) == 2 and all(math.isfinite(x) and x > 0 for x in evaluations)
    setup = seed['construction_and_restore_seconds']
    save = seed['save_after_final_evaluation_and_teardown_seconds']
    assert all(math.isfinite(x) and x > 0 for x in [setup,save])
    bound = 64*1024**3
    assert 0 < seed['snapshot']['bytes'] <= bound
    stages = []
    for branch, initial in [('weighted',20),('equal',0)]:
        start = initial
        for target in [500,1000,1500,2000]:
            checkpoints = sorted({t for t in [1,20,100,500,2000,5000,10000,start,target]
                                  if max(1,start) <= t <= target})
            # An admission estimate only. Actual mature training cost is still unknown.
            estimate = 2*(setup+save+(target-start)*max(iterations)+len(checkpoints)*max(evaluations))+600
            deadline = math.ceil(estimate/300)*300
            assert deadline <= 43200, 'Estimated segment exceeds the guard ceiling; register shorter segments separately'
            stages.append(dict(branch=branch,start=start,target=target,evaluation_iterations=checkpoints,
                               admission_estimate_seconds=estimate,maximum_seconds=deadline,
                               maximum_checkpoint_write_bytes=bound))
            start = target
    return dict(stages=stages,additional_checkpoint_write_budget_bytes=len(stages)*bound,
                disk_free_reserve_bytes=100_000_000_000,observed_seed_max_iteration_seconds=max(iterations),
                observed_seed_max_evaluation_seconds=max(evaluations),
                within_panel_gap_threshold_bb=.01,stop_early_for_appearance=False,
                timing_scope='Early 20-iteration cost with 2x admission margin and 600 seconds; not a mature speed guarantee.',
                accuracy_claim=False,production_ready=False)


def main():
    seed_path = OUT/'strategic-weighted112-seed-v1-review.json'
    seed = read(seed_path)
    assert read(OUT/'strategic-seed-pipeline-v1-status.json')['step'] == 'complete-seed-and-restore-qualified'
    assert read(OUT/'checkpoint-long-v1-review.json')['passed']
    for name,digest in seed['result_sha256'].items():
        assert sha(OUT/f'strategic-weighted112-seed-v1-{name}-result.json') == digest
    snapshot = Path(seed['snapshot']['path'])
    assert {p.name for p in snapshot.iterdir()} == set(seed['snapshot']['files'])
    for name,digest in seed['snapshot']['files'].items():
        assert sha(snapshot/name) == digest, name
    log_path = EVIDENCE/'strategic-weighted112-seed-v1-save.log'
    rows = [json.loads(line.split('STUDY_PHASE ',1)[1]) for line in log_path.read_text().splitlines()
            if line.startswith('STUDY_PHASE ')]
    plan = schedule(seed,rows)
    assert shutil.disk_usage(snapshot).free >= plan['disk_free_reserve_bytes']+plan['additional_checkpoint_write_budget_bytes']
    files = [Path(__file__),seed_path,log_path,OUT/'STRATEGIC-COMPARISON-PLAN.md',
             OUT/'STRATEGIC-SEED-PROTOCOL.md',OUT/'checkpoint-v1-runtime-freeze.json',
             OUT/'checkpoint-long-v1-review.json',OUT/'expansion-train-112.json',
             OUT/'expansion-train-112-chance-weight-v1.json']
    plan['inputs_sha256'] = {str(p.relative_to(ROOT)):sha(p) for p in files}
    plan['seed_checkpoint'] = seed['snapshot']
    plan['launch_authorized'] = False
    plan['next_gate'] = 'Review this resource schedule and register the continuation runner before launching.'
    with (OUT/'strategic-segments-v1-proposed-schedule.json').open('x') as f:
        json.dump(plan,f,indent=2)
    print(json.dumps({k:v for k,v in plan.items() if k not in ['inputs_sha256','seed_checkpoint']},indent=2))


if __name__ == '__main__':
    main()
