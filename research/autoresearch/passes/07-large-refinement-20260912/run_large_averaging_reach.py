"""Read-only discriminator after the forced-age averaging comparison ends."""
import json
from run07 import LAB, RAW, run
from check_joint import require, read
from check_large_current import verify as verify_current
from check_large_averaging import verify as verify_averaging


def main():
    result = verify_averaging()
    age = result['checks'][-1]['iteration']
    exe = LAB/'target/release/examples/convergence_diagnostics.exe'
    equity = LAB/'cache/preflop_eq169.bin'
    names = ('large-normalized-pair-seed42-v1', 'large-averaging-dcfr-v1')
    summaries = []
    details = []
    for case in names:
        name = case+'-current'
        source = LAB/'target/convergence'/case/'final.gtop'
        audit = RAW/(case+'-audit.json')
        out = RAW/(name+'.json')
        run(name, [exe, source, audit, out], 300, [exe, source, audit, equity])
        summaries.append(verify_current(name, case+'-audit.json', age))
        details.append(read(name+'.json')['nodes'])
    # Identical learned histories must also produce identical current policy,
    # current prefix mass, and hand reach at every preregistered path.
    for left, right in zip(*details):
        for key in ('path', 'actor', 'actions', 'current_prefix_mass_by_seat',
                    'current_counterfactual_prefix_mass'):
            require(left[key] == right[key], 'Current node differs between averages')
        for lh, rh in zip(left['hands'], right['hands']):
            for key in ('class_index', 'regrets', 'positive_regret_sum', 'current_probabilities',
                        'current_conditional_hand_mass', 'current_uniform_fallback'):
                require(lh[key] == rh[key], 'Current hand differs between averages')
    (RAW/'large-averaging-reach-verified.json').write_text(json.dumps(dict(
        current_policies_and_reaches_exact=True, iteration=age,
        original=summaries[0], averaging=summaries[1],
        scope='Separate current learning coverage from average-policy response quality; no new learning'),
        indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
