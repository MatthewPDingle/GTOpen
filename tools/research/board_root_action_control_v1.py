"""Two predetermined archived batches; qualify root decomposition before replay."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import argparse
import json
from pathlib import Path
import time
import psutil
from board_root_action_decomposition_v1 import (require, digest, encoded, publish, restore_batch,
    validate_original, force_root, validate_forced, tamper_controls, invoke, compare)
from global_research_inventory_v2 import measure
from weighted_evaluation_readback_v1 import worker_guard

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'board-root-action-control-v1'
STORE = Path('S:/GTOpen-research') / PREFIX
NAMES = ('test-000000', 'test-032768')
EXPECTED = {
    'weighted-complete-board-root-study-v1-registration.json': '127088852b6bd3bd4c900b076872b449385c5c693803eb3e276f239b513a4497',
    'weighted-complete-board-root-study-v1-result.json': '2cd6c1d2d9b9ea362ff8f104376b06d8a97982ecce0a494ed570ea05b87fa092',
    'weighted-complete-board-root-study-v1-independent-review.json': '82d0d242489bb6bffcd4582592285f9804ce8eccb0e8f2748d952f924a5174f1'}


def sha(path):
    return digest(Path(path).read_bytes())


def main(run):
    if not run:
        print(json.dumps(dict(batches=NAMES, new_deals=0, gpu_used=False, control_not_run=True)))
        return
    began = time.monotonic()
    last = 0.
    def guard():
        nonlocal last
        require(time.monotonic()-began < 1800, 'Control deadline')
        if time.monotonic()-last > 2:
            worker_guard()
            require(psutil.disk_usage('S:/').free > 10_000_000_000, 'Keep free disk reserve')
            last = time.monotonic()
    guard()
    require(psutil.cpu_percent(interval=1) < 60, 'Yield to heavy CPU activity')
    for name, expected in EXPECTED.items():
        require(sha(OUT/name) == expected, 'Changed completed study evidence: '+name)
    reg, result, review = [json.loads((OUT/name).read_text()) for name in EXPECTED]
    require(result['passed'] and result['complete'] and review['passed']
        and result['deals'] == 65536 and review['deals'] == 65536, 'Complete audited source required')
    old_store = Path(result['store'])
    cp = old_store / result['checkpoint']['file']
    require(sha(cp) == result['checkpoint']['sha256'], 'Changed source checkpoint')
    checkpoint = json.loads(cp.read_text())
    require(checkpoint['routes'] == result['routes'] and checkpoint['completed_deals'] == 65536
        and checkpoint['registration_sha256'] == sha(OUT/next(iter(EXPECTED))), 'Changed routed prefix')
    executable = ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    context = OUT/'bb-context-candidate.json'
    for p in (executable, context):
        require(sha(p) == reg['inputs'][str(p)], 'Changed frozen evaluator or context')
    source = context.read_bytes().decode()
    require(not STORE.exists(), 'Preserve existing control store')
    require(not (OUT/(PREFIX+'-registration.json')).exists(), 'Preserve registered attempt')
    inventory = measure()
    require(sum(r['allocated_file_bytes'] for r in inventory)+1_000_000_000 < 800_000_000_000,
        'Control exceeds global allocated storage limit')
    paths = [OUT/name for name in EXPECTED] + [cp, executable, context,
        OUT/'BOARD-ROOT-ACTION-DECOMPOSITION-PLAN.md', Path(__file__),
        Path(__file__).with_name('board_root_action_decomposition_v1.py')]
    paths += [ROOT/'tools/research'/name for name in ('owned_columnar_evaluation_archive_v1.py',
        'crossed_profile_columnar_v1.py', 'crossed_profile_columnar_v2.py', 'global_research_inventory_v2.py')]
    inputs = {str(p):sha(p) for p in paths}
    registration = dict(format=1, inputs=inputs, batches=NAMES, routes={n:result['routes'][n] for n in NAMES},
        inventory=inventory, storage_ceiling_bytes=1_000_000_000, maximum_seconds=1800,
        max_native_seconds=120, workers=1, gpu_used=False, new_deals=0,
        tolerance=1e-10, source_study_unchanged=True, exploratory=True)
    rp = OUT/(PREFIX+'-registration.json')
    publish(rp, encoded(registration))
    STORE.mkdir()
    publish(STORE/'control-owner.json', encoded(dict(root=str(STORE), registration_sha256=sha(rp))))
    controls = []
    try:
        for name in NAMES:
            start = time.monotonic(); guard()
            members = restore_batch(old_store, name, result['routes'][name], guard)
            original, roots, deal_rows, deals = validate_original(members, source)
            rejected = tamper_controls(original, roots)
            forced = force_root(original, roots)
            validate_forced(original, forced, roots)
            folder = STORE/name; folder.mkdir()
            for member in ('conditional-batch.json', 'profiles.json'):
                publish(folder/member, members[member])
            publish(folder/'forced-profiles.json', encoded(forced))
            repeat_seconds = invoke(executable, context, folder/'conditional-batch.json',
                folder/'profiles.json', folder/'replayed-native.json', guard)
            forced_seconds = invoke(executable, context, folder/'conditional-batch.json',
                folder/'forced-profiles.json', folder/'forced-native.json', guard)
            values = compare(json.loads(members['native.json']),
                json.loads((folder/'replayed-native.json').read_text()),
                json.loads((folder/'forced-native.json').read_text()), original, deal_rows, deals,
                json.loads(source)['dead_money'])
            publish(folder/'action-values.json', encoded(values))
            row = dict(name=name, deals=len(deals), root_rows=len(roots), tamper_rejections=rejected,
                maximum_replay_error=values['maximum_replay_error'], maximum_mixture_error=values['maximum_mixture_error'],
                repeat_seconds=repeat_seconds, forced_seconds=forced_seconds, seconds=time.monotonic()-start,
                original_artifacts={n:digest(raw) for n,raw in members.items()},
                new_artifacts={str(p):sha(p) for p in folder.iterdir()},
                retained_bytes=sum(p.stat().st_size for p in folder.iterdir()))
            controls.append(row)
            print(json.dumps({k:v for k,v in row.items() if k not in ('original_artifacts','new_artifacts')}),flush=True)
        for p,h in inputs.items(): require(sha(p) == h, 'Registered input changed')
        output = dict(passed=True, registration_sha256=sha(rp), batches=controls,
            seconds=time.monotonic()-began, fresh_deals=0, gpu_used=False, production_modified=False,
            root_only_deviation=True, later_behavior_fixed=True, accuracy_qualified=False,
            full_replay_launched=False, independent_readback_pending=True)
        publish(OUT/(PREFIX+'-result.json'), encoded(output))
        print(json.dumps({k:v for k,v in output.items() if k != 'batches'}),flush=True)
    except BaseException as error:
        publish(OUT/(PREFIX+'-failure.json'), encoded(dict(passed=False,error=repr(error),
            registration_sha256=sha(rp), completed_batches=[r['name'] for r in controls])))
        raise


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true')
    main(parser.parse_args().run)
