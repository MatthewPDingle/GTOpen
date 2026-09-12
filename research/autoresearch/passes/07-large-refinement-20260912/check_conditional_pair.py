"""Recompute paired decision-level variance and promotion gates from raw draws."""
import gzip
import hashlib
import json
from check_conditional_sampling import verify_result
from check_joint import HERE, RAW, read, require

BLINDS = [[2, 0, 0, 1], [2, 0, 0, 1, 1]]


def load(name):
    process = read(name+'-exit.json')
    require(process['returncode'] == 0 and process['reason'] is None, 'Incomplete diagnostic')
    packed = (RAW/(name+'-result.json.gz')).read_bytes()
    data = gzip.decompress(packed)
    envelope = read(name+'-result-envelope.json')
    require(len(data) == envelope['original_bytes']
            and hashlib.sha256(data).hexdigest() == envelope['original_sha256']
            and hashlib.sha256(packed).hexdigest() == envelope['gzip_sha256'], 'Archive mismatch')
    return json.loads(data), process


def compare(base, corrected, paths):
    require(not base.get('pair_control', False) and corrected['pair_control'] is True, 'Wrong correction modes')
    require(0 < corrected['pair_extra_bytes'] <= 1024*1024*1024, 'Pair memory cap')
    require(base['source_iteration'] == corrected['source_iteration'], 'Different source age')
    require(len(base['rows']) == len(corrected['rows']) == len(paths), 'Missing rows')
    for a, b in zip(base['rows'], corrected['rows']):
        for key in ('path', 'source', 'cpu_reference', 'gpu_prefix_mass_by_seat',
                    'normalized_regret_denominator_f32', 'zero_opponent_reach',
                    'current_sigma_action_major', 'full_action_values_raw_action_major'):
            require(a[key] == b[key], 'Different frozen comparison: '+key)
    moments = [verify_result(r, paths) for r in (base, corrected)]
    rows = []
    for a, b in zip(moments[0]['rows'], moments[1]['rows']):
        scores = []
        for row in (a, b):
            require(not row['zero_opponent_reach'], 'Unreachable diagnostic gate')
            hands = [h for h in row['hands'] if h['current_hand_mass'] >= .0025]
            scores.append(dict(
                variance=sum(h['current_hand_mass']*sum(h['regret_variance']) for h in hands),
                promotion=sum(h['current_hand_mass']*h['probability_strictly_promoting_inferior_action'] for h in hands),
                worst=max(h['probability_strictly_promoting_inferior_action'] for h in hands),
                maximum_absolute_bias=max(abs(v) for h in row['hands'] for v in h['regret_bias'])))
        x, y = scores
        rows.append(dict(path=a['path'], baseline=x, corrected=y,
            variance_ratio=y['variance']/x['variance'] if x['variance'] > 0 else None,
            blind_gate=(y['variance'] <= x['variance'] and y['promotion'] <= .8*x['promotion']
                        and y['worst'] <= x['worst']+.02) if a['path'] in BLINDS else None))
    base_variance = sum(r['baseline']['variance'] for r in rows)
    pair_variance = sum(r['corrected']['variance'] for r in rows)
    require(base_variance > 0, 'Degenerate variance screen')
    ratio = pair_variance/base_variance
    require(sum(r['path'] in BLINDS for r in rows) == 2, 'Missing blind paths')
    return dict(evidence_verified=True, rows=rows, weighted_variance_ratio=ratio,
        screen_passed=ratio <= .75 and all(r['blind_gate'] for r in rows if r['path'] in BLINDS),
        scope='Fixed-policy decision noise only; no learning, convergence or speed qualification')


def main():
    paths = json.loads((HERE/'exploration-diagnostic-paths.json').read_text())
    cases = []
    for samples, seed in ((64, 42), (64, 314159), (1024, 42)):
        base, bp = load(f'conditional-sampling-s{samples}-seed{seed}-v1')
        corrected, cp = load(f'conditional-pair-s{samples}-seed{seed}-v1')
        require(base['nodes'] == corrected['nodes'] == 23038, 'Wrong fixture')
        source = f'particle-quality-s{samples}-seed{seed}-norm1-v1'
        bh = [h for p, h in bp['inputs'].items() if source in p and p.endswith('final.gtop')]
        ch = [h for p, h in cp['inputs'].items() if source in p and p.endswith('final.gtop')]
        require(len(bh) == len(ch) == 1 and bh == ch, 'Different immutable saved inputs')
        r = compare(base, corrected, paths)
        r.update(source_samples=samples, source_seed=seed, source_iteration=base['source_iteration'])
        cases.append(r)
    return dict(evidence_verified=True, screen_passed=all(c['screen_passed'] for c in cases), cases=cases)


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
