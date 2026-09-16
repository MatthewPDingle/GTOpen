"""N27: same frozen model in two genuinely heads-up preflop fixtures."""
import datetime as dt
import math
from pathlib import Path
import sys
import continuation_chance_control as control

study = control.study
OUT = control.BASE/'heads-up-settling-20260916'
SEED_BIN = study.ROOT/'target/learned-interface-filtered/release/examples/continuation_hu_seed.exe'
ARMS = ['original', 'balanced', 'candidate']


def validate(s, cfg, model, iteration):
    assert s['config'] == cfg and s['model'] == model
    assert s['iteration'] == iteration and s['start_iteration'] == (0 if iteration == 500 else 500)
    assert s['warmup_iterations'] == 0 and len(s['gaps']) == len(s['evs']) == 2
    assert all(math.isfinite(x) for x in s['gaps']+s['evs'])
    assert min(s['gaps']) >= -1e-6 and abs(sum(s['evs'])) < .0002
    if model != 'original':
        assert s['plan']['contexts'] == 1 and s['plan']['entries'] == [0]
        assert s['plan']['seats'] == [1, 0]


def prepare():
    fixtures = study.read(OUT/'seeds/fixtures.json')['fixtures']
    assert [r['config']['stack'] for r in fixtures] == [40., 100.]
    assert all(r['nodes'] == 40 and r['iteration'] == 0 and r['postflop_order'] == [1, 0] for r in fixtures)
    paths = [Path(__file__), OUT/'README.md', OUT/'seeds/fixtures.json', SEED_BIN,
             study.ROOT/'crates/solver/examples/continuation_hu_seed.rs',
             control.transfer.original.runtime.BIN, control.KERNEL,
             study.ROOT/'cache/realization_fit.json', study.ROOT/'cache/preflop_eq169.bin']
    paths += [OUT/'seeds'/f['file'] for f in fixtures]
    inputs = dict(study.read(control.FULL/'manifest.json')['files'])
    inputs.update({str(p.resolve().relative_to(study.ROOT)).replace('\\', '/'): study.pilot.sha(p) for p in paths})
    for path, expected in inputs.items():
        assert study.pilot.sha(study.ROOT/path) == expected, path
    freeze = OUT/'protocol-freeze.json'
    if freeze.exists():
        assert study.read(freeze)['inputs'] == inputs
    else:
        study.freeze(freeze, dict(registered_at=study.night.now(), inputs=inputs,
                                 checkpoints=[500, 1500], production_enabled=False))
    return fixtures


def report():
    fixtures = prepare(); rows = []; hashes = {}
    for f in fixtures:
        stack = int(f['config']['stack'])
        for arm in ARMS:
            for iteration in [500, 1500]:
                path = OUT/str(stack)/arm/str(iteration)/f'iteration-{iteration}.json'
                s = study.read(path); validate(s, f['config'], arm, iteration)
                hashes[str(path.relative_to(study.ROOT)).replace('\\', '/')] = study.pilot.sha(path)
                rows.append(dict(stack=stack, arm=arm, iteration=iteration,
                                 gap_total_bb=sum(s['gaps']), evs=s['evs'],
                                 learning_seconds=s['learning_seconds']))
    result = dict(checked_at=study.night.now(), rows=rows, snapshots=hashes,
                  production_enabled=False,
                  caveat='Two fixed small heads-up fixtures; separate approximate continuation games. Not full-postflop exploitability, runtime benchmarking or deployment qualification.')
    study.freeze(OUT/'result.json', result)
    lines = ['# Heads-up settling diagnostic', '', result['caveat'], '',
             '| Stack (bb) | Path | Iterations | Frozen-value gap (bb) |', '|---|---|---:|---:|']
    for r in rows:
        lines.append(f"| {r['stack']} | {r['arm']} | {r['iteration']} | {r['gap_total_bb']:.6f} |")
    (OUT/'RESULTS.md').write_text('\n'.join(lines)+'\n', encoding='utf-8', newline='\n')
    print('\n'.join(lines), flush=True)


def run():
    control.idle(); fixtures = prepare()
    assert not (OUT/'result.json').exists(), 'Already complete; inspect results'
    assert (control.transfer.original.bridge.DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds() >= 1200
    for iteration in [500, 1500]:
        order = ARMS if iteration == 500 else ARMS[::-1]
        for f in fixtures:
            stack = int(f['config']['stack'])
            for arm in order:
                folder = OUT/str(stack)/arm/str(iteration); folder.mkdir(parents=True, exist_ok=True)
                target = folder/f'iteration-{iteration}.json'
                if not target.exists():
                    control.idle()
                    source = OUT/'seeds'/f['file'] if iteration == 500 else folder.parent/'500/policy.gtop'
                    args = ['solve', source, folder, arm, 500 if iteration == 500 else 1000, control.KERNEL]
                    if iteration == 1500: args.append('resume')
                    control.transfer.original.runtime.command(args, folder/'run.log', optimized=True, warm=0)
                validate(study.read(target), f['config'], arm, iteration)
    report()


if __name__ == '__main__':
    {'prepare': prepare, 'run': run, 'report': report}[sys.argv[1]]()
