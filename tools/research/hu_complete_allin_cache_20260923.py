"""Prepare, then enumerate every private pair in the fixed BB/BTN population.

Candidate-independent equity data only. --prepare may run alongside training;
--run requires the research resource lock and an idle production server.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['OMP_NUM_THREADS'] = '2'
import json
from pathlib import Path
import shutil
import sys
import time
import psutil
from sampled_allin_protocol_v3 import AllinCache
from sampled_conditional_cache_builder_v1 import build
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from reboot_research_idle_v1 import idle

OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'complete-private-allin-cache-v1'
STORE = Path('S:/GTOpen-research') / PREFIX
REGISTRATION = OUT / f'{PREFIX}-registration.json'
LOCK = ROOT / 'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT / 'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def read(path):
    return json.loads(Path(path).read_text())


def prepare():
    assert idle() and not STORE.exists() and not REGISTRATION.exists()
    began = time.monotonic()
    population_result_path = OUT / 'allin-private-population-plan-v1-result.json'
    population_registration = OUT / 'allin-private-population-plan-v1-registration.json'
    population_result = read(population_result_path)
    assert population_result['passed'] and population_result['registration_sha256'] == sha(population_registration)
    for path, h in read(population_registration)['inputs'].items():
        assert sha(path) == h, path
    population_path = Path(population_result['artifact'])
    assert sha(population_path) == population_result['artifact_sha256']
    population = read(population_path)
    assert population['player_roles_fixed'] is True and len(population['rows']) == 47478
    base_review_path = OUT / 'sampled-physical-allin-training-cache-v1-independent-review.json'
    base = AllinCache.from_review(base_review_path)
    diagnostic_review_path = OUT / 'sampled-physical-allin-population-diagnostic-v1-independent-review.json'
    diagnostic_result_path = OUT / 'sampled-physical-allin-population-diagnostic-v1-result.json'
    diagnostic_registration = OUT / 'sampled-physical-allin-population-diagnostic-v1-registration.json'
    review, diagnostic = read(diagnostic_review_path), read(diagnostic_result_path)
    assert review['passed'] and diagnostic['passed'] and review['result_sha256'] == sha(diagnostic_result_path)
    assert review['registration_sha256'] == diagnostic['registration_sha256'] == sha(diagnostic_registration)
    assert review['reviewer_sha256'] == sha(ROOT / 'tools/research/hu_allin_population_diagnostic_review_20260923.py')
    # The admitted diagnostic review already reconstructed these integer rows
    # from all native outputs. Recheck the saved provenance before reusing them.
    for path, h in diagnostic['cache_artifacts'].items():
        assert sha(path) == h, path
    additional = AllinCache(diagnostic['cache_artifact'], diagnostic['cache_sha256'])
    combined = dict(base.rows)
    for key, row in additional.rows.items():
        if key in combined:
            assert combined[key] == row
        combined[key] = row
    keys = sorted(tuple(row['private_cards']) for row in population['rows'])
    assert len(set(keys)) == len(keys)
    missing = [k for k in keys if k not in combined]
    assert 0 < len(missing) <= 24000
    paths = [Path(__file__), ROOT / 'tools/research/hu_complete_allin_cache_review_20260923.py',
        population_result_path, population_registration, population_path, base_review_path,
        Path(read(base_review_path)['cache_artifact']), diagnostic_review_path,
        diagnostic_result_path, diagnostic_registration, Path(diagnostic['cache_artifact']),
        OUT / 'bb-context-candidate.json',
        ROOT / 'target/release/examples/hu_allin_board_reference.exe',
        *[ROOT / 'tools/research' / n for n in ('sampled_allin_protocol_v3.py',
            'sampled_conditional_cache_builder_v1.py', 'hu_sampled_physical_dense_btn_jam_diagnosis_20260923.py',
            'reboot_research_idle_v1.py', 'sampled_physical_root_evaluation_v1.py')]]
    STORE.mkdir()
    reused = STORE / 'reviewed-union-cache.json'
    save(reused, dict(format=1, player_roles_fixed=True, rows=[combined[k] for k in keys if k in combined]))
    AllinCache(reused, sha(reused))
    paths.append(reused)
    registration = dict(inputs={str(p): sha(p) for p in paths}, population=str(population_path),
        population_sha256=sha(population_path), base_union=str(reused), base_union_sha256=sha(reused),
        reviewed_base_cache=read(base_review_path)['cache_artifact'], reviewed_base_sha256=base.sha256,
        reviewed_additional_cache=diagnostic['cache_artifact'], reviewed_additional_sha256=additional.sha256,
        canonical_private_pairs=len(keys), physical_private_pairs=population['physical_pairs'],
        reused_keys=len(keys)-len(missing), new_keys=len(missing), maximum_new_keys=24000,
        maximum_seconds=4800, minimum_host_bytes=20_000_000_000, minimum_disk_bytes=40_000_000_000,
        reviewers_required=['hu_complete_allin_cache_review_20260923.py'],
        policy_candidates=[], production_modified=False,
        scope='Complete candidate-independent all-in equities for the fixed compatible private-pair population. No training, policy selection or range-quality claim.')
    save(REGISTRATION, registration)
    save(OUT / f'{PREFIX}-status.json', dict(state='prepared', launched=False, production_modified=False))
    print(json.dumps(dict(prepared=True, private_pairs=len(keys), reused_keys=registration['reused_keys'],
        new_keys=len(missing), native_seconds_estimate=len(missing)*diagnostic['native_equity_seconds']/diagnostic['new_equity_keys'],
        preparation_seconds=time.monotonic()-began)))


def run():
    reg = read(REGISTRATION)
    assert read(OUT / f'{PREFIX}-status.json')['state'] == 'prepared'
    assert idle() and not LOCK.exists() and not OTHER.exists()
    for p, h in reg['inputs'].items():
        assert sha(p) == h, p
    began = time.monotonic(); last = 0.; acquired = False; error = None
    def guard():
        nonlocal last
        now = time.monotonic()
        assert now-began < reg['maximum_seconds'], 'Execution deadline'
        if now-last >= 2:
            assert idle(), 'Production activity'
            assert psutil.virtual_memory().available >= reg['minimum_host_bytes']
            assert shutil.disk_usage(STORE.anchor).free >= reg['minimum_disk_bytes']
            last = now
    try:
        with LOCK.open('x') as f:
            f.write(str(os.getpid()))
        acquired = True; guard()
        save(OUT / f'{PREFIX}-status.json', dict(state='running', controller_pid=os.getpid(), production_modified=False))
        population = read(reg['population'])
        # The five filler board cards are only independent native scorer
        # sanity checks. Exact equity still enumerates ALL possible boards.
        deals = [r['private_cards'] + [c for c in range(52) if c not in r['private_cards']][:5] for r in population['rows']]
        base = AllinCache(reg['base_union'], reg['base_union_sha256'])
        cache, result = build(deals, base, STORE / 'enumeration', maximum_new_keys=reg['maximum_new_keys'], guard=guard)
        assert len(cache.rows) == reg['canonical_private_pairs'] and result['new_keys'] == reg['new_keys']
        assert result['reused_keys'] == reg['reused_keys']
        for p, h in reg['inputs'].items():
            assert sha(p) == h, p
        guard()
        save(OUT / f'{PREFIX}-result.json', dict(passed=True, registration_sha256=sha(REGISTRATION),
            cache_artifact=result['cache_artifact'], cache_sha256=cache.sha256,
            builder_result=str(STORE / 'enumeration/result.json'), builder_result_sha256=sha(STORE / 'enumeration/result.json'),
            canonical_private_pairs=len(cache.rows), physical_private_pairs=population['physical_pairs'],
            new_keys=result['new_keys'], reused_keys=result['reused_keys'], native_seconds=result['native_seconds'],
            seconds=time.monotonic()-began, production_modified=False, gpu_used=False,
            accuracy_qualified=False, independently_reviewed=False, scope=reg['scope']))
        print(json.dumps(dict(passed=True, new_keys=result['new_keys'], seconds=time.monotonic()-began)))
    except Exception as exc:
        error = repr(exc)
        raise
    finally:
        save(OUT / f'{PREFIX}-status.json', dict(state='stopped' if error else 'complete', error=error,
            seconds=time.monotonic()-began, production_modified=False))
        if acquired:
            assert LOCK.read_text().strip() == str(os.getpid())
            LOCK.unlink()


if __name__ == '__main__':
    if sys.argv[1:] == ['--prepare']:
        prepare()
    elif sys.argv[1:] == ['--run']:
        run()
    else:
        raise SystemExit('Use --prepare or --run')
