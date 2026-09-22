"""Read-only CPU geometry/occupancy screen; no solver or sampled policy training."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import subprocess
import sys
import time
import psutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
EXE = ROOT/'target/release/examples/hu_public_chance_capacity.exe'
ATTEMPT = sys.argv[1] if len(sys.argv)>1 else 'v1'
assert ATTEMPT in ['v2'], 'v1 failed; preserve it and use the reviewed v2 correction'


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def chance_oracle():
    """Exhaust all proposal outcomes for many fixed compatible private deals.

    Public sampling cannot exclude each player's private cards globally: it
    uses the 49 unseen public cards and masks private collisions per pair.
    The finite-sum identity is an estimator check, not a convergence test.
    """
    rng = random.Random(20260922)
    rows = []
    for flop in [(51,45,29), (48,46,20), (30,26,22)]:
        deck = [c for c in range(52) if c not in flop]
        outcomes = list(itertools.permutations(deck, 2))
        assert len(outcomes) == 49*48
        error = 0.0
        for _ in range(128):
            holes = set(rng.sample(deck, 4))
            legal = [(t,r) for t,r in outcomes if t not in holes and r not in holes]
            assert len(legal) == 45*44
            value = lambda t,r: ((47*t+13*r+7*t*r)%103)/17-2
            direct = math.fsum(value(t,r) for t,r in legal)/(45*44)
            sampled_expectation = math.fsum(
                value(t,r)*(49*48)/(45*44) if t not in holes and r not in holes else 0.0
                for t,r in outcomes)/(49*48)
            error = max(error, abs(direct-sampled_expectation))
            assert abs(direct-sampled_expectation) < 1e-12
        # A constant payoff exposes the tempting incorrect uncorrected mask.
        wrong_constant = (45*44)/(49*48)
        assert abs(wrong_constant-1) > 0.1
        rows.append({'flop_cards':flop,'private_deals':128,'max_error':error,
                     'uncorrected_constant_expectation':wrong_constant})
    return {'rows':rows,'corrected_constant_expectation':1.0,
            'importance_multiplier':(49*48)/(45*44),
            'scope':'Fixed-policy chance-value identity only; no regret/averaging or adaptive-policy guarantee.'}


def execute(label, manifest):
    result = OUT/(label+'-result.json')
    log = OUT/(label+'.log')
    assert not result.exists() and not log.exists()
    assert psutil.virtual_memory().available > 40*2**30
    start = time.monotonic()
    samples = []
    with log.open('wb') as stream:
        process = subprocess.Popen([str(EXE),str(OUT/'bb-context-candidate.json'),str(manifest),str(result)],
            cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        while process.poll() is None:
            free = psutil.virtual_memory().available
            samples.append({'seconds':time.monotonic()-start,'free_host_bytes':free})
            if free < 20*2**30 or time.monotonic()-start > 1200:
                process.kill(); process.wait()
                raise RuntimeError('CPU planning reserve/deadline reached; no retry')
            time.sleep(1)
    assert process.returncode == 0, log
    return json.loads(result.read_text()), {'seconds':time.monotonic()-start,
        'minimum_free_host_bytes':min(s['free_host_bytes'] for s in samples),
        'samples':len(samples),'exit_code':process.returncode}


def validate(census, old):
    previous = {(r['board'],r['preflop_leaf']):r for r in old['rows']}
    assert len(census['rows']) == len(previous)
    for row in census['rows']:
        before = previous[(row['board'],row['preflop_leaf'])]
        assert row['canonical_state_bytes'] == before['canonical_state_bytes']
        assert row['canonical_actions'] == before['canonical_actions']
        assert sum(h['state_bytes'] for h in row['histogram']) == row['reachable_state_bytes']
        assert row['reachable_state_bytes']+row['unvisited_allocation_bytes'] == row['canonical_state_bytes']
        assert sum(h['public_groups'] for h in row['histogram']) == row['public_group_count']
        for depth, denominator in enumerate([1,49,49*48]):
            hs = [h for h in row['histogram'] if h['depth'] == depth]
            assert sum(h['public_groups']*h['orbit_multiplicity'] for h in hs) == denominator
            assert all(h['physical_public_prefixes'] == denominator for h in hs)
    assert sum(r['canonical_state_bytes'] for r in census['rows']) == old['totals']['canonical_state_bytes']


def occupancy(census):
    boards = census['manifest']['boards']
    total_weight = sum(b['weight'] for b in boards)
    weights = {b['board']:b['weight']/total_weight for b in boards}
    output = []
    for scheme in ['one_board_uniform','one_board_weighted','every_board']:
        for iterations in [2000,20000,200000,2000000]:
            by_street = [0.0]*3
            for row in census['rows']:
                pb = (1/len(boards) if scheme == 'one_board_uniform' else
                      weights[row['board']] if scheme == 'one_board_weighted' else 1.0)
                for h in row['histogram']:
                    chance = pb*h['orbit_multiplicity']/h['physical_public_prefixes']
                    visited = 1.0 if chance == 1.0 else -math.expm1(iterations*math.log1p(-chance))
                    by_street[h['depth']] += h['state_bytes']*visited
            output.append({'scheme':scheme,'iterations':iterations,
                'expected_state_bytes_by_street':by_street,'expected_state_bytes':sum(by_street)})
    return output


def main():
    registration = OUT/f'public-chance-screen-{ATTEMPT}-registration.json'
    final = OUT/f'public-chance-screen-{ATTEMPT}-review.json'
    assert not registration.exists() and not final.exists()
    inputs = [EXE,Path(__file__),ROOT/'crates/solver/examples/hu_public_chance_capacity.rs',
        ROOT/'crates/solver/Cargo.toml',ROOT/'Cargo.lock']
    inputs += list((ROOT/'crates/solver/src').rglob('*.rs')) + list((ROOT/'crates/solver/src').rglob('*.cu'))
    inputs += [OUT/n for n in ['bb-context-candidate.json','capacity-texture-probe.json',
        'capacity-texture-result.json','capacity-existing112-manifest.json','capacity-existing112-result.json']]
    hashes = {str(p.relative_to(ROOT)):sha(p) for p in inputs}
    record = {'inputs':hashes,'created_at_unix':time.time(),'maximum_seconds_per_plan':1200,
        'minimum_free_ram_bytes':20*2**30,'purpose':'Full-support canonical state census and lazy allocation occupancy, not training',
        'schemes':['one_board_uniform','one_board_weighted','every_board'],
        'iteration_counts':[2000,20000,200000,2000000],
        'model':'IID public card draws with replacement across iterations; all action branches visited; retain all ever-touched state',
        'limits':'Expected state, not peak/admission or convergence. Excludes metadata, checkpoints and data structures. No deletion of prior state.',
        'oracle_cases':384,'no_automatic_retry':True,
        'previous_failure':'public-chance-screen-registration.json; first probe planner comparison failed before any complete census',
        'correction':'Track unreachable direct-DMA arena slots separately from canonical visited actions; reconcile their sum with the unchanged capacity planner.'}
    with registration.open('x') as f: json.dump(record,f,indent=2)
    oracle = chance_oracle()
    probe, probe_resources = execute(f'public-chance-{ATTEMPT}-probe',OUT/'capacity-texture-probe.json')
    validate(probe,json.loads((OUT/'capacity-texture-result.json').read_text()))
    panel, panel_resources = execute(f'public-chance-{ATTEMPT}-panel',OUT/'capacity-existing112-manifest.json')
    validate(panel,json.loads((OUT/'capacity-existing112-result.json').read_text()))
    for p,h in hashes.items(): assert sha(ROOT/p) == h,p
    result = {'passed':True,'registration_sha256':sha(registration),'source_hashes_verified':len(hashes),
        'probe_games':len(probe['rows']),'panel_games':len(panel['rows']),
        'panel_bytes':sum(r['canonical_state_bytes'] for r in panel['rows']),
        'panel_reachable_bytes':sum(r['reachable_state_bytes'] for r in panel['rows']),
        'panel_unvisited_allocation_bytes':sum(r['unvisited_allocation_bytes'] for r in panel['rows']),
        'panel_bytes_by_street':[sum(h['state_bytes'] for r in panel['rows'] for h in r['histogram'] if h['depth']==d) for d in range(3)],
        'occupancy':occupancy(panel),'chance_oracle':oracle,
        'resources':{'probe':probe_resources,'panel':panel_resources},
        'production_modified':False,'strategic_accuracy_claim':False,'full_forest_admitted':False}
    with final.open('x') as f: json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
