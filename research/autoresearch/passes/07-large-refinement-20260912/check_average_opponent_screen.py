"""Independent convergence/coverage gate and exact disabled-mode replay."""
import gzip
import hashlib
from check_joint import *
from check_root_repair import checked_local
from run07 import LAB, digest
from run_average_opponent_screen import CASES, case_name


def archive(name):
    packed = (RAW/(name+'-result.json.gz')).read_bytes()
    data = gzip.decompress(packed)
    e = read(name+'-result-envelope.json')
    require(len(data) == e['original_bytes'] and hashlib.sha256(data).hexdigest() == e['original_sha256']
            and hashlib.sha256(packed).hexdigest() == e['gzip_sha256'], 'Corrupt archive')
    return json.loads(data)


def verify():
    paths = json.loads((HERE/'exploration-diagnostic-paths.json').read_text())
    cases = []
    for seed, average in CASES:
        name = case_name(seed, average)
        r = archive(name)
        for suffix in ('-exit.json', '-audit-exit.json'):
            p = read(name+suffix)
            require(p['returncode'] == 0 and p['reason'] is None, 'Incomplete process')
        require(r['nodes'] == 23038 and r['samples'] == 64 and r['seed'] == seed
                and r['normalized'] is True and r['pair'] is True
                and r['average_opponents'] is average and r['schedule'] == 'gamma15'
                and r['horizon'] == 1000 and r['limit'] == 3000
                and 0 < r['pair_extra_bytes'] <= 1024*1024*1024, 'Wrong registered configuration')
        require(r['roundtrip_exact'] is True and r['large_game_qualified'] is False, 'Wrong preservation or scope')
        require(1 <= len(r['checks']) <= 120, 'Wrong check count')
        streak = 0; checks = []
        for index, c in enumerate(r['checks']):
            require(c['iteration'] == 25*(index+1) and c['full_reference_samples'] == 1024
                    and streak < 2, 'Wrong check cadence or late stopping')
            require(len(c['gaps']) == len(c['evs']) == 6
                    and all(math.isfinite(v) and v >= 0 for v in c['gaps'])
                    and all(math.isfinite(v) for v in c['evs']), 'Invalid global evaluation')
            gap = sum(c['gaps']); require(abs(gap-c['gap']) < 1e-12, 'Wrong gap sum')
            passed = checked_local(c['rows'], paths)
            require(c['passed'] == passed, 'Wrong conditional count')
            streak = streak+1 if gap <= .005 and passed == 6 else 0
            require(c['consecutive_combined_passes'] == streak, 'Wrong combined gate')
            checks.append(dict(iteration=c['iteration'], gap=gap, passed=passed, streak=streak))
        require(r['qualified'] is (streak >= 2) and r['iteration'] == checks[-1]['iteration']
                and (r['qualified'] or r['iteration'] == 3000), 'Wrong terminal condition')
        audit = read(name+'-audit.json')
        require(checked_local(audit['rows'], paths) == checks[-1]['passed'], 'Saved count differs')
        for actual, expected in zip(audit['rows'], r['checks'][-1]['rows']):
            require(actual['candidate'] == expected['candidate'], 'Saved hand record differs')
        if not average:
            prior_name = f'normalized-pair-tail-seed{seed}-v1'
            prior = archive(prior_name)
            require(r['iteration'] == prior['iteration'] and len(r['checks']) == len(prior['checks']),
                    'Disabled mode changed stopping')
            for new, old in zip(r['checks'], prior['checks']):
                for key in ('iteration', 'gaps', 'evs', 'gap', 'rows', 'passed', 'consecutive_combined_passes'):
                    require(new[key] == old[key], 'Disabled mode changed trajectory: '+key)
            require(digest(LAB/'target/convergence'/name/'final.gtop')
                    == digest(LAB/'target/convergence'/prior_name/'final.gtop'), 'Disabled saved histories differ')
        require(math.isfinite(r['seconds']) and r['seconds'] > 0, 'Invalid complete timing')
        cases.append(dict(seed=seed, average_opponents=average, seconds=r['seconds'],
                          iteration=r['iteration'], qualified=r['qualified'], checks=checks,
                          independent_saved_audit_exact=True, disabled_replay_exact=not average))
    admitted = True
    for candidate in (c for c in cases if c['average_opponents']):
        control = next(c for c in cases if c['seed'] == candidate['seed'] and not c['average_opponents'])
        require(control['qualified'], 'Control did not qualify')
        candidate['complete_time_ratio'] = candidate['seconds']/control['seconds']
        candidate['passes_screen'] = candidate['qualified'] and candidate['complete_time_ratio'] <= 2
        admitted &= candidate['passes_screen']
    return dict(evidence_verified=True, cases=cases, exploratory_large_admitted=admitted,
                large_game_qualified=False,
                scope='Matched small-fixture accuracy and bounded overhead screen; no deployment qualification')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
