"""Independent fresh four-seed tail gate; original quality thresholds unchanged."""
import gzip
import hashlib
from check_root_repair import checked_local
from check_joint import *
from run_normalized_pair_tail import CASES


def verify():
    paths = json.loads((HERE/'exploration-diagnostic-paths.json').read_text())
    cases = []
    for tag, samples, seed in CASES:
        name = f'normalized-pair-tail-{tag}-v1'
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
                and r['schedule'] == 'gamma15' and r['horizon'] == 1000 and r['limit'] == 3000, 'Wrong configuration')
        require(r['roundtrip_exact'] and r['large_game_qualified'] is False, 'Wrong preservation or scope')
        require((0 < r['pair_extra_bytes'] <= 1024*1024*1024) if r['pair'] else r['pair_extra_bytes'] == 0, 'Wrong pair budget')
        require(1 <= len(r['checks']) <= 120, 'Wrong check count')
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
                and (r['qualified'] or r['iteration'] == 3000), 'Wrong terminal condition')
        audit = read(name+'-audit.json')
        require(checked_local(audit['rows'], paths) == checks[-1]['passed'], 'Saved count differs')
        for a, b in zip(audit['rows'], r['checks'][-1]['rows']):
            require(a['candidate'] == b['candidate'], 'Saved per-hand audit differs')
        prior_prefix_exact = None
        if samples == 64 and seed in (42, 314159):
            prior = json.loads(gzip.decompress((RAW/f'normalized-pair-quality-s64-seed{seed}-v1-result.json.gz').read_bytes()))
            require(len(r['checks']) >= len(prior['checks']), 'Different early stopping trajectory')
            for old, new in zip(prior['checks'], r['checks']):
                for key in ('iteration', 'gaps', 'evs', 'gap', 'rows', 'passed', 'consecutive_combined_passes'):
                    require(old[key] == new[key], 'Fresh replay changed prior prefix: '+key)
            prior_prefix_exact = True
        replay = None
        if samples == 1024:
            lab = HERE.parents[3]
            old = lab/'target/convergence/particle-quality-s1024-seed42-norm1-v1/final.gtop'
            new = lab/'target/convergence'/name/'final.gtop'
            replay = hashlib.sha256(new.read_bytes()).hexdigest()
            require(replay == hashlib.sha256(old.read_bytes()).hexdigest(), 'Full-control histories changed')
        require(math.isfinite(r['seconds']) and r['seconds'] > 0, 'Invalid timing')
        cases.append(dict(tag=tag, samples=samples, seed=seed, seconds=r['seconds'], solve_seconds=r['solve_seconds'],
            iteration=r['iteration'], qualified=r['qualified'], checks=checks,
            independent_saved_audit_exact=True, full_control_replay_sha256=replay,
            prior_screen_prefix_exact=prior_prefix_exact))
    controls = [c for c in cases if c['samples'] == 1024]
    require(len(controls) == 2 and all(c['qualified'] for c in controls), 'Controls did not qualify')
    target_seconds = min(c['seconds'] for c in controls)/1.25
    candidates = [c for c in cases if c['samples'] == 64]
    require([c['seed'] for c in candidates] == [42,271828,314159,1618033], 'Wrong seed coverage')
    for c in candidates:
        c['qualified_speedup'] = min(x['seconds'] for x in controls)/c['seconds'] if c['qualified'] else None
        c['passes_time_gate'] = c['qualified'] and c['seconds'] <= target_seconds
    return dict(evidence_verified=True, cases=cases, target_seconds=target_seconds,
                small_fixture_qualified=all(c['passes_time_gate'] for c in candidates),
                large_game_qualified=False,
                scope='Fresh four-seed small-fixture combined-quality speed screen; not large-game qualification')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
