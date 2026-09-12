"""Independent forced-age averaging diagnostic; never a speed qualification."""
import gzip
import hashlib
from check_root_repair import checked_local
from check_joint import *
from check_large_normalized_pair import verify as verify_original


def verify():
    original = verify_original(42)
    require(not original['combined_quality_passed'], 'Original passed; wrong follow-up')
    name = 'large-averaging-dcfr-v1'
    packed = (RAW/(name+'-result.json.gz')).read_bytes()
    data = gzip.decompress(packed)
    envelope = read(name+'-result-envelope.json')
    require(len(data) == envelope['original_bytes']
            and hashlib.sha256(data).hexdigest() == envelope['original_sha256']
            and hashlib.sha256(packed).hexdigest() == envelope['gzip_sha256'], 'Corrupt evidence')
    r = json.loads(data)
    paths = json.loads((HERE/'broad-paths.json').read_text())
    limit = original['checks'][-1]['iteration']
    for suffix in ('-exit.json', '-audit-exit.json', '-compare-exit.json'):
        p = read(name+suffix)
        require(p['returncode'] == 0 and p['reason'] is None, 'Incomplete process')
    require(r['nodes'] == 1567754 and r['samples'] == 64 and r['seed'] == 42
            and r['pair'] is True and 0 < r['pair_extra_bytes'] <= 1024*1024*1024
            and r['normalized'] is True and r['schedule'] == 'dcfr'
            and r['horizon'] == 1000 and r['limit'] == limit
            and r['reference_iteration'] == limit and r['iteration'] == limit
            and r['forced_age'] is True and r['reference_regrets_exact'] is True,
            'Wrong registered experiment')
    require(r['roundtrip_exact'] is True and r['large_game_qualified'] is False,
            'Wrong roundtrip or premature qualification')
    require(len(r['checks']) == limit//50 == len(original['checks']), 'Wrong check count')
    streak = 0
    any_pass = False
    checks = []
    for index, (c, old) in enumerate(zip(r['checks'], original['checks'])):
        require(c['iteration'] == old['iteration'] == 50*(index+1)
                and c['full_reference_samples'] == 1024, 'Wrong cadence')
        require(len(c['gaps']) == len(c['evs']) == 8
                and all(math.isfinite(v) and v >= 0 for v in c['gaps'])
                and all(math.isfinite(v) for v in c['evs']), 'Invalid global check')
        gap = sum(c['gaps'])
        require(abs(gap-c['gap']) < 1e-12, 'Wrong global sum')
        passed = checked_local(c['rows'], paths)
        require(c['passed'] == passed, 'Wrong local count')
        streak = streak+1 if gap <= .005 and passed == 27 else 0
        require(c['consecutive_combined_passes'] == streak, 'Wrong combined gate')
        any_pass |= streak >= 2
        checks.append(dict(iteration=c['iteration'], gap=gap, passed=passed, streak=streak,
                           original_gap=old['gap'], original_passed=old['passed']))
    require(r['qualified'] is (streak >= 2) and r['any_combined_pass'] is any_pass,
            'Wrong terminal gate')
    audit = read(name+'-audit.json')
    require(checked_local(audit['rows'], paths) == checks[-1]['passed'], 'Saved count differs')
    for actual, expected in zip(audit['rows'], r['checks'][-1]['rows']):
        require(actual['candidate'] == expected['candidate'], 'Saved per-hand record differs')
    arenas = read(name+'-compare.json')
    require(arenas['iteration'] == limit and arenas['nodes'] == 1567754
            and arenas['regrets_bit_exact'] is True and arenas['averages_bit_exact'] is False
            and arenas['all_learning'] is True and arenas['model'] == 'coupled_deck_v1',
            'Independent arena isolation failed')
    return dict(evidence_verified=True, any_combined_pass=any_pass,
                final_combined_pass=streak >= 2, checks=checks,
                independent_saved_audit_exact=True, independent_regrets_bit_exact=True,
                large_game_qualified=False, seconds=r['seconds'],
                scope='Forced-age averaging diagnostic; no equal-quality speed claim or deployment')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
