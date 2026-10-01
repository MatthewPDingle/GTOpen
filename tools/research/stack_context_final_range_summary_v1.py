"""Descriptive reading of the 28 completed, independently verified range exports.

No poker inference, sampling, fitting, checkpoint selection or statistical gate.
The default is a synthetic arithmetic check; --summarize requires terminal audit
success and the separately rendered qualified final report.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'stack-context-final-range-summary-v1'
RANKS = '23456789TJQKA'
WEIGHT_TOTAL = 2080
ARMS = ('A-baseline', 'A-relative', 'B-baseline', 'B-relative')
EXAMPLES = ('AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55',
            '44', '33', '22', 'AKo', 'AQo', 'KQo', 'AKs', 'AQs', 'AJs',
            'ATs', 'KQs', 'KJs', 'QJs', 'JTs', 'T9s', '98s', '87s', '76s',
            '65s', '54s', 'A5s', 'A4s', 'A3s', 'A2s')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hand_name(index):
    row, col = divmod(index, 13)
    if row == col:
        return RANKS[row]*2
    return RANKS[max(row, col)]+RANKS[min(row, col)]+('s' if row > col else 'o')


def action_text(action, invested):
    if action['kind'] == 'fold':
        return 'Fold'
    more = float(action['to'])-float(invested)
    require(more >= -1e-10, 'Action takes back an existing investment')
    verb = {'call': 'Call', 'raise': 'Raise', 'jam': 'Jam'}[action['kind']]
    return f'{verb} to {action["to"]:g}bb ({max(0., more):g}bb more)'


def describe_node(context, row):
    tree = context['nodes'][row['node']]
    require(row['actor'] == tree['actor'] and row['actions'] == tree['actions'],
            'Export and public decision geometry differ')
    history = []
    for ancestor, action_index in row['path']:
        parent = context['nodes'][ancestor]
        history.append(dict(player=('BB', 'BTN')[parent['actor']],
                            action=parent['actions'][action_index]))
    reach = float(row['probability_of_reaching_node'])
    marginal = row['entry_mass_by_class']
    policies = row['action_probabilities_by_class']
    own = row['own_history_weighted_model_support_by_class']
    require(len(marginal) == len(policies) == len(own) == 169,
            'Every class is required, including unsupported classes')
    require(math.isfinite(reach) and reach >= 0 and abs(sum(marginal)-reach) < 1e-10,
            'Invalid joint node reach or class marginal')
    arity = len(row['actions'])
    require(all(math.isfinite(m) and m >= 0 for m in marginal)
            and all(len(p) == arity and all(math.isfinite(x) and x >= 0 for x in p)
                    and abs(sum(p)-1) < 1e-10 for p in policies)
            and all(math.isfinite(x) and 0 <= x <= WEIGHT_TOTAL+1e-8 for x in own),
            'Invalid policy or own-history mixture support')
    if reach:
        weighted = [sum(m*p[a] for m, p in zip(marginal, policies))/reach for a in range(arity)]
        require(row['conditional_action_frequencies'] is not None
                and len(row['conditional_action_frequencies']) == arity
                and max(abs(a-b) for a, b in zip(weighted, row['conditional_action_frequencies'])) < 1e-10,
                'Frequencies do not use the actual arriving class marginal')
        require(row['conditional_range_by_class'] is not None
                and len(row['conditional_range_by_class']) == 169
                and max(abs(m/reach-c) for m, c in zip(marginal, row['conditional_range_by_class'])) < 1e-10,
                'Invalid conditional arriving range')
    else:
        weighted = None
        require(row['conditional_action_frequencies'] is None
                and row['conditional_range_by_class'] is None, 'Zero-reach mix must remain absent')
    classes = []
    for index in range(169):
        require(row['in_arriving_range'][index] == (marginal[index] > 0), 'Incorrect arrival marker')
        classes.append(dict(hand=hand_name(index), entry_mass=marginal[index],
            conditional_arriving_share=marginal[index]/reach if reach else None,
            own_history_weighted_support=own[index], own_history_support_fraction=own[index]/WEIGHT_TOTAL,
            in_arriving_range=marginal[index] > 0,
            conditional_hand_action_policy=policies[index]))
    return dict(node=row['node'], player=('BB', 'BTN')[row['actor']], history=history,
        actions=[dict(action, display=action_text(action, tree['invested'][row['actor']])) for action in row['actions']],
        joint_node_reach=reach, conditional_action_frequencies=weighted,
        classes=classes, zero_node_reach=reach == 0)


def synthetic_check():
    # Unequal physical arrival weights: 75% of this history holds AA and 25%
    # holds KK. Equal weighting of the 169 classes would give a wrong answer.
    actions = [dict(kind='fold', label='Fold', to=0.), dict(kind='call', label='Call 2', to=2.)]
    context = dict(nodes=[dict(actor=0, actions=actions, invested=[1., 2.])])
    marginal = [0.]*169; marginal[168] = .15; marginal[154] = .05
    policy = [[.5, .5] for _ in range(169)]; policy[168] = [0., 1.]; policy[154] = [.8, .2]
    row = dict(node=0, actor=0, actions=actions, path=[], probability_of_reaching_node=.2,
        entry_mass_by_class=marginal, action_probabilities_by_class=policy,
        own_history_weighted_model_support_by_class=[WEIGHT_TOTAL]*169,
        conditional_range_by_class=[m/.2 for m in marginal], conditional_action_frequencies=[.2, .8],
        in_arriving_range=[m > 0 for m in marginal])
    answer = describe_node(context, row)
    require(abs(answer['conditional_action_frequencies'][1]-.8) < 1e-12,
            'Synthetic compatible-arrival calculation failed')
    require(answer['actions'][1]['display'] == 'Call to 2bb (1bb more)', 'Total versus incremental call confused')
    names = [hand_name(i) for i in range(169)]
    require(len(set(names)) == 169 and names[168] == 'AA' and names[154] == 'KK'
            and names[167] == 'AKs' and names[155] == 'AKo', 'Hand-class mapping differs')
    row.update(probability_of_reaching_node=0., entry_mass_by_class=[0.]*169,
               conditional_action_frequencies=None, conditional_range_by_class=None,
               in_arriving_range=[False]*169)
    zero = describe_node(context, row)
    require(zero['conditional_action_frequencies'] is None and zero['zero_node_reach'],
            'Unsupported fallback became a recommendation')
    print(json.dumps(dict(synthetic_only=True, passed=True, scientific_values_read=False)))


def summarize():
    paths = {key: OUT/(NAME+suffix) for key, suffix in
             (('full', '.json'), ('nodes', '-nodes.csv'), ('hands', '-example-hands.csv'), ('receipt', '-receipt.json'))}
    require(not any(p.exists() for p in paths.values()), 'Preserve any existing descriptive analysis')
    receipt_path = OUT/'stack-context-final-report-v3-receipt.json'
    require(receipt_path.is_file(), 'Qualified final report must have completed first')
    receipt = read(receipt_path)
    require(receipt['complete'] is True and receipt['independent_readback_complete'] is True
            and receipt['comparison_count'] == 56 and receipt['pooled_comparison_count'] == 8,
            'Incomplete final report')
    sys.path.insert(0, str(ROOT/'tools/research'))
    import stack_context_final_report_v3 as report
    terminal, reader, inputs = report.terminal_evidence()
    require(all(sha(p) == digest for p, digest in receipt['inputs'].items())
            and all(sha(p) == digest for p, digest in receipt['outputs'].items()),
            'Final report sources or products changed')
    inputs[str(receipt_path)] = sha(receipt_path)
    prepared_path = OUT/'stack-context-population-v1-result.json'
    prepared = read(prepared_path); inputs[str(prepared_path)] = sha(prepared_path)
    descriptions = []
    for depth in report.base.DEPTHS:
        record = next(r for r in prepared['contexts'].values() if r['depth'] == depth)
        context_path = Path(record['context_path']); context = read(context_path)
        inputs[str(context_path)] = sha(context_path)
        for arm in ARMS:
            matches = [Path(p) for p in terminal['range_exports']
                       if Path(p).parent.name == f'stack-{depth}' and Path(p).name == arm+'-preflop-ranges.json']
            require(len(matches) == 1, 'Missing or duplicated stack/arm export')
            path = matches[0]; inputs[str(path)] = sha(path)
            require(inputs[str(path)] == terminal['range_exports'][str(path)], 'Changed verified export')
            value = read(path)
            require(value['context_sha256'] == record['context_sha256'] and value['arm'] == arm,
                    'Range belongs to a different context or arm')
            descriptions.append(dict(depth=depth, split='heldout' if depth in (60, 150) else 'fit', arm=arm,
                export_path=str(path), nodes=[describe_node(context, row) for row in value['range_export']['nodes']]))
    require(len(descriptions) == 28, 'Every stack/arm is required')
    payload = dict(complete=True, descriptions=descriptions, own_weight_total=WEIGHT_TOTAL,
        interpretation='Each export uses the same arm for BOTH players; arrivals are not fixed-opponent payoff contrasts.',
        support_interpretation='Own support / 2080 is own-history reach, not an observed hand count or joint node reach.',
        no_support_cutoff=True, external_accuracy_qualified=False, production_ready=False)
    paths['full'].write_text(json.dumps(payload, allow_nan=False, separators=(',', ':'), sort_keys=True), encoding='utf-8')
    fields = ['depth', 'split', 'arm', 'node', 'player', 'history', 'joint_node_reach', 'action', 'conditional_frequency']
    with paths['nodes'].open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fields); writer.writeheader()
        for desc in descriptions:
            for node in desc['nodes']:
                history = json.dumps(node['history'], separators=(',', ':'))
                for index, action in enumerate(node['actions']):
                    writer.writerow({**{k: desc[k] for k in ('depth', 'split', 'arm')},
                        **{k: node[k] for k in ('node', 'player', 'joint_node_reach')}, 'history': history,
                        'action': action['display'], 'conditional_frequency': None if node['zero_node_reach'] else node['conditional_action_frequencies'][index]})
    fields += ['hand', 'entry_mass', 'conditional_arriving_share', 'own_history_weighted_support',
               'own_history_support_fraction', 'in_arriving_range', 'conditional_hand_action_policy']
    with paths['hands'].open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fields); writer.writeheader()
        for desc in descriptions:
            for node in desc['nodes']:
                hands = {row['hand']: row for row in node['classes']}
                for hand in EXAMPLES:
                    row = hands[hand]
                    for index, action in enumerate(node['actions']):
                        writer.writerow({**{k: desc[k] for k in ('depth', 'split', 'arm')},
                            **{k: node[k] for k in ('node', 'player', 'joint_node_reach')},
                            **{k: row[k] for k in fields if k in row and k != 'conditional_hand_action_policy'},
                            'history': json.dumps(node['history'], separators=(',', ':')), 'action': action['display'],
                            'conditional_frequency': None if node['zero_node_reach'] else node['conditional_action_frequencies'][index],
                            'conditional_hand_action_policy': row['conditional_hand_action_policy'][index]})
    inputs[str(Path(__file__).resolve())] = sha(__file__)
    require(all(sha(p) == digest for p, digest in inputs.items()), 'Evidence changed during descriptive reading')
    paths['receipt'].write_text(json.dumps(dict(complete=True, unix=time.time(), inputs=inputs,
        outputs={str(p): sha(p) for key, p in paths.items() if key != 'receipt'}, exports=28,
        classes_per_node=169, example_hands=list(EXAMPLES), descriptive_only=True,
        statistical_gate_changed=False, new_scientific_work=False, production_modified=False),
        allow_nan=False, sort_keys=True, separators=(',', ':')), encoding='utf-8')
    print(json.dumps(dict(complete=True, exports=28, nodes=sum(len(d['nodes']) for d in descriptions),
                         outputs={key: str(p) for key, p in paths.items()})))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--summarize', action='store_true')
    if parser.parse_args().summarize:
        summarize()
    else:
        synthetic_check()
