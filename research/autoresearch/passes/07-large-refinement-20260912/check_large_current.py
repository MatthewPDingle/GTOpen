"""Summarize current reach without confusing it with average-policy reach."""
import json
import math
from check_joint import HERE, RAW, read, require


def verify():
    process = read('large-normalized-current-v1-exit.json')
    require(process['returncode'] == 0 and process['reason'] is None, 'Incomplete diagnostic')
    current = read('large-normalized-current-v1.json')['nodes']
    audit = read('large-normalized-quality-v1-audit.json')['rows']
    paths = json.loads((HERE/'broad-paths.json').read_text())
    require([n['path'] for n in current] == paths, 'Wrong current path coverage')
    require([n['candidate']['path'] for n in audit] == paths, 'Wrong audit path coverage')
    rows = []
    for n, q in zip(current, audit):
        c = q['candidate']
        require(n['iteration'] == 1500 and not n['forced'] and not n['frozen'], 'Wrong final policy')
        masses = n['current_prefix_mass_by_seat']
        require(len(masses) == 8 and all(math.isfinite(m) and m >= 0 for m in masses), 'Invalid masses')
        mass = math.prod(m for i, m in enumerate(masses) if i != n['actor'])
        require(abs(mass-n['current_counterfactual_prefix_mass']) < 1e-12, 'Wrong current product')
        require([h['class_index'] for h in n['hands']] == list(range(169)), 'Missing hands')
        relevant = [h for h in c['hands'] if h['conditional_hand_mass'] >= .0025]
        worst = max(relevant, key=lambda h: h['probability_on_actions_losing_over_0_1bb'])
        hand = n['hands'][worst['class_index']]
        rows.append(dict(path=n['path'], passed=c['passes_local_tail_gate'],
            average_mass=n['average_counterfactual_prefix_mass'], current_mass=mass,
            worst_hand=hand['hand'], worst_bad_probability=worst['probability_on_actions_losing_over_0_1bb'],
            current_hand_mass=hand['current_conditional_hand_mass'], uniform=hand['current_uniform_fallback']))
    return dict(nodes=rows, zero_current_opponent_mass=sum(n['current_mass'] == 0 for n in rows),
                failed=sum(not n['passed'] for n in rows),
                all_current_masses_above_floor=all(n['current_mass'] > 1e-12 for n in rows),
                scope='Current prefix diagnostic versus independently audited average policy; zero current reach does not qualify an average-policy failure')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
