"""Independent combined-quality acceptance and matched full-control timing."""
import gzip
import hashlib
from check_root_repair import checked_local
from check_joint import *
from run_normalized_pair import CASES


def verify():
    paths = json.loads((HERE/'exploration-diagnostic-paths.json').read_text())
    cases = []
    for samples, seed in CASES:
        name = f'normalized-pair-quality-s{samples}-seed{seed}-v1'
        packed = (RAW/(name+'-result.json.gz')).read_bytes()
        data = gzip.decompress(packed); envelope = read(name+'-result-envelope.json')
        require(len(data) == envelope['original_bytes'] and hashlib.sha256(data).hexdigest() == envelope['original_sha256']
                and hashlib.sha256(packed).hexdigest() == envelope['gzip_sha256'], 'Archive mismatch')
        r = json.loads(data)
        for suffix in ('-exit.json', '-audit-exit.json'):
            p = read(name+suffix)
            require(p['returncode'] == 0 and p['reason'] is None, 'Incomplete guarded process')
        require(r['nodes'] == 23038 and r['samples'] == samples and r['seed'] == seed
                and r['normalized'] is True and r['pair'] is (samples != 1024)
                and r['schedule'] == 'gamma15' and r['horizon'] == r['limit'] == 1000, 'Wrong configuration')
        require(r['roundtrip_exact'] and r['large_game_qualified'] is False, 'Wrong preservation or scope')
        require((0 < r['pair_extra_bytes'] <= 1024*1024*1024) if r['pair'] else r['pair_extra_bytes'] == 0, 'Wrong pair budget')
        require(1 <= len(r['checks']) <= 40, 'Wrong check count')
        checks = []; streak = 0
        for index, c in enumerate(r['checks']):
            require(c['iteration'] == 25*(index+1) and c['full_reference_samples'] == 1024 and streak < 2, 'Wrong cadence or stopping')
            require(len(c['gaps']) == len(c['evs']) == 6
                    and all(math.isfinite(v) and v >= 0 for v in c['gaps'])
                    and all(math.isfinite(v) for v in c['evs']), 'Invalid full global check')
            gap = sum(c['gaps']); require(abs(gap-c['gap']) < 1e-12, 'Wrong gap sum')
            passed = checked_local(c['rows'], paths)
            require(passed == c['passed'], 'Wrong conditional count')
            streak = streak+1 if gap <= .005 and passed == 6 else 0
            require(c['consecutive_combined_passes'] == streak, 'Wrong combined streak')
            checks.append(dict(iteration=c['iteration'], gap=gap, passed=passed, streak=streak))
        require(r['qualified'] is (streak >= 2) and r['iteration'] == checks[-1]['iteration']
                and (r['qualified'] or r['iteration'] == 1000), 'Wrong terminal condition')
        audit = read(name+'-audit.json')
        require(checked_local(audit['rows'], paths) == checks[-1]['passed'], 'Saved count differs')
        for a, b in zip(audit['rows'], r['checks'][-1]['rows']):
            require(a['candidate'] == b['candidate'], 'Saved per-hand audit differs')
        replay = None
        if samples == 1024:
            lab = HERE.parents[3]
            old = lab/'target/convergence/particle-quality-s1024-seed42-norm1-v1/final.gtop'
            new = lab/'target/convergence'/name/'final.gtop'
            replay = hashlib.sha256(new.read_bytes()).hexdigest()
            require(replay == hashlib.sha256(old.read_bytes()).hexdigest(), 'Full-control histories changed')
        require(math.isfinite(r['seconds']) and r['seconds'] > 0, 'Invalid timing')
        cases.append(dict(samples=samples, seed=seed, seconds=r['seconds'], solve_seconds=r['solve_seconds'],
            iteration=r['iteration'], qualified=r['qualified'], checks=checks,
            independent_saved_audit_exact=True, full_control_replay_sha256=replay))
    rankings = []
    for samples in (64, 256):
        seeds = []
        for seed in (42, 314159):
            candidate = next(c for c in cases if c['samples'] == samples and c['seed'] == seed)
            control = next(c for c in cases if c['samples'] == 1024 and c['seed'] == seed)
            ratio = control['seconds']/candidate['seconds'] if candidate['qualified'] and control['qualified'] else None
            seeds.append(dict(seed=seed, qualified_speedup=ratio, passed=ratio is not None and ratio >= 1.25))
        rankings.append(dict(samples=samples, seeds=seeds, small_fixture_qualified=all(s['passed'] for s in seeds)))
    return dict(evidence_verified=True, cases=cases, rankings=rankings, large_game_qualified=False,
                scope='Combined-quality small-fixture GPU screen; no large-game or deployment qualification')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
