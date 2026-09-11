"""Separate averaging lag, current prefix support and numerical fallbacks."""
from run_diagnostics import CASES, HERE, PREVIOUS
from pathlib import Path
import json


def summarize():
    results = []
    for name, audit_name, q_key in CASES:
        exit_record = json.loads((HERE / 'raw' / f'{name}-learning-diagnostics-exit.json').read_text())
        if exit_record.get('returncode') != 0 or exit_record.get('reason'):
            raise RuntimeError(f'Incomplete diagnostic: {name}')
        d = json.loads((HERE / 'raw' / f'{name}-learning-diagnostics.json').read_text())
        audit = json.loads((PREVIOUS / 'raw' / f'{audit_name}-local-v3.json').read_text())
        source_path = audit['reference' if q_key == 'reference_self' else 'candidate']
        if Path(source_path).resolve() != Path(d['input']).resolve():
            raise RuntimeError('Action values and diagnostic snapshot do not match')
        lookup = {tuple(row[q_key]['path']): row[q_key] for row in audit['rows']}
        nodes = []
        for node in d['nodes']:
            values = lookup[tuple(node['path'])]
            details = []
            for hand, qrow in zip(node['hands'], values['hands']):
                if hand['class_index'] != qrow['class_index']:
                    raise RuntimeError('Hand ordering mismatch')
                if qrow['conditional_hand_mass'] < .0025:
                    continue
                q = qrow['action_values_bb']
                best = max(q)
                current = hand['current_probabilities']
                details.append(dict(hand=hand['hand'],
                    average_loss_bb=qrow['expected_action_loss_bb'],
                    current_action_loss_against_average_future_bb=sum(p*(best-v) for p,v in zip(current,q)),
                    average_bad_probability=qrow['probability_on_actions_losing_over_0_1bb'],
                    current_bad_probability_against_average_future=sum(p for p,v in zip(current,q) if best-v > .1),
                    positive_regret_sum=hand['positive_regret_sum'], strategy_sum=hand['strategy_sum'],
                    current_uniform_fallback=hand['current_uniform_fallback'],
                    average_uniform_fallback=hand['average_uniform_fallback']))
            nodes.append(dict(path=node['path'], position=node['position'], forced=node['forced'],
                average_counterfactual_prefix_mass=node['average_counterfactual_prefix_mass'],
                current_counterfactual_prefix_mass=node['current_counterfactual_prefix_mass'],
                material_hand_count=len(details),
                current_uniform_fallback_count=sum(h['current_uniform_fallback'] for h in details),
                average_uniform_fallback_count=sum(h['average_uniform_fallback'] for h in details),
                worst_average_hands=sorted(details,key=lambda h:h['average_loss_bb'],reverse=True)[:8]))
        results.append(dict(name=name,nodes=nodes))
    return dict(scope='Current action compared with fixed average continuation; this is not a current-policy best response.',trials=results)


if __name__ == '__main__':
    result = summarize()
    (HERE / 'learning-diagnostics-summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))
