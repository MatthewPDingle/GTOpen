"""Software controls only: synthetic policies/payoffs, no scientific model run."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace

import numpy as np

TOOLS = Path(r'T:\Dev\GTOpen\tools\research')
sys.path.append(str(TOOLS))
from stack_context_preflop_expected_components_v2 import PreflopExpectedComponents
from stack_context_board_components_v1 import exact_terms, board_terms

PAIRS = np.asarray(list(itertools.combinations(range(52), 2)), dtype=np.int64)
CLASSES = np.asarray([max(a//4, b//4)*13+min(a//4, b//4)
    if a % 4 == b % 4 or a//4 == b//4 else min(a//4, b//4)*13+max(a//4, b//4)
    for a, b in PAIRS])


def compatible(h, o):
    return ((h[:, None, 0] != o[None, :, 0]) & (h[:, None, 0] != o[None, :, 1])
          & (h[:, None, 1] != o[None, :, 0]) & (h[:, None, 1] != o[None, :, 1]))


def fixture(context):
    weights = np.asarray([1 + CLASSES / 200, .1 + CLASSES / 100])
    weights[1, CLASSES == 1] = 0
    joint = compatible(PAIRS, PAIRS) * weights[0, :, None] * weights[1, None, :]
    total = float(joint.sum())
    joint /= total
    pair_class = CLASSES[:, None]*169 + CLASSES[None, :]
    def group(x):
        return np.bincount(pair_class.ravel(), weights=x.ravel(), minlength=169**2).reshape(169, 169)
    mass = group(joint)
    called = context['nodes'][context['nodes'][context['nodes'][0]['children'][3]]['children'][1]]
    rake = min(called['pot']*context['rake_fraction'], context['rake_cap'])
    score = PAIRS.sum(1)
    share = (score[:, None] > score[None, :]) + .5*(score[:, None] == score[None, :])
    payoff = [-(called['invested'][0])+(called['pot']-rake)*share,
              -(called['invested'][1])+(called['pot']-rake)*(1-share)]
    matrix = SimpleNamespace(mass=mass, bb=group(joint*payoff[0]), btn=group(joint*payoff[1]),
                             bb_mass=mass.sum(1), btn_mass=mass.sum(0))
    pre = {}
    for i, n in enumerate(context['nodes']):
        if n['children']:
            a = len(n['children'])
            raw = 1 + ((np.arange(169)[:, None]*3 + np.arange(a)[None, :]*7 + i) % 11)
            pre[i] = raw / raw.sum(1)[:, None]
    return matrix, pre, weights, total, joint, payoff


def board_fixture(context, weights):
    board = [0, 5, 10, 15, 20]
    ids = np.asarray([i for i, p in enumerate(PAIRS) if not any(c in board for c in p)])
    hands = PAIRS[ids]
    score = (hands.sum(1)*7 + (hands[:, 1]-hands[:, 0]) % 5).astype(np.int64)
    tree = dict(format=1, board=board, hands=[hands.tolist(), hands.tolist()],
                ranks=[score.tolist(), score.tolist()], branches=[])
    post = []
    for i, n in enumerate(context['nodes']):
        if n['leaf'] and n['leaf']['type'] == 'postflop':
            m = min(n['invested'])
            payouts = [m+2, -m-2, 0]
            nodes = [dict(kind=0, actor=0, children=[1, 4]),
                     dict(kind=1, children=[2]),
                     dict(kind=0, actor=1, children=[3, 5]),
                     dict(kind=3, actor=0, children=[], payouts=payouts),
                     dict(kind=0, actor=1, children=[6, 7]),
                     dict(kind=0, actor=0, children=[8, 9]),
                     dict(kind=2, actor=1, children=[], payouts=payouts),
                     dict(kind=3, actor=0, children=[], payouts=payouts),
                     dict(kind=2, actor=0, children=[], payouts=payouts),
                     dict(kind=3, actor=0, children=[], payouts=payouts)]
            tree['branches'].append(dict(branch=i, nodes=nodes,
                offsets=n['leaf']['value_offsets'], starting_pot=n['leaf']['starting_pot']))
            policy = {}
            for j in (0, 2, 4, 5):
                first = .1 + ((CLASSES[ids]+i+j) % 7)/10
                policy[j] = np.column_stack([first, 1-first])
            post.append(policy)
    return tree, post, [w[ids] for w in weights], [CLASSES[ids], CLASSES[ids]], ids


def dense_post(tree, branch, policy):
    """Independent forward enumeration of terminal pair matrices."""
    hands = [np.asarray(h) for h in tree['hands']]
    ranks = [np.asarray(r) for r in tree['ranks']]
    allowed = compatible(*hands)
    out = [np.zeros(allowed.shape), np.zeros(allowed.shape)]
    todo = [(0, allowed.astype(float))]
    while todo:
        i, probability = todo.pop()
        node = branch['nodes'][i]
        if node['kind'] == 0:
            for a, child in enumerate(node['children']):
                p = policy[i][:, a]
                todo.append((child, probability*(p[:, None] if node['actor'] == 0 else p[None, :])))
        elif node['kind'] == 1:
            todo.append((node['children'][0], probability))
        else:
            for hero in (0, 1):
                v = node['payouts']
                if node['kind'] == 2:
                    payoff = v[1 if node['actor'] == hero else 0]
                else:
                    sign = ranks[0][:, None]-ranks[1][None, :]
                    if hero == 1: sign = -sign
                    payoff = np.where(sign > 0, v[0], np.where(sign < 0, v[1], v[2]))
                out[hero] += probability*(payoff+branch['offsets'][hero])
    return out


def reference(context, matrix, pre, joint, showdown, board_data, total):
    """Force one action; enumerate future leaves, excluding only own past."""
    tree, post, weights, classes, ids = board_data
    boards = {b['branch']:dense_post(tree, b, p) for b, p in zip(tree['branches'], post)}
    board_joint = weights[0][:, None]*weights[1][None, :]/total
    ancestors = {}
    def paths(i, path):
        if context['nodes'][i]['children']:
            ancestors[i] = path
            for a, child in enumerate(context['nodes'][i]['children']):
                paths(child, path+[(i, a)])
    paths(0, [])
    factor = (52*51*50/(48*47*46)) * (49*48/(45*44))
    result = {}
    for i, path in ancestors.items():
        hero = context['nodes'][i]['actor']
        other = 1-hero
        mass = matrix.bb_mass if hero == 0 else matrix.btn_mass
        past = np.ones(169)
        for j, a in path:
            if context['nodes'][j]['actor'] == other:
                past *= pre[j][:, a]
        exact = np.zeros((169, len(context['nodes'][i]['children'])))
        board = np.zeros_like(exact)
        for a, child in enumerate(context['nodes'][i]['children']):
            future = [np.ones(169), np.ones(169)]
            future[other] = past.copy()
            todo = [(child, future)]
            while todo:
                j, reach = todo.pop()
                node = context['nodes'][j]
                if node['children']:
                    for b, nxt in enumerate(node['children']):
                        r = [x.copy() for x in reach]
                        r[node['actor']] *= pre[j][:, b]
                        todo.append((nxt, r))
                    continue
                kind = node['leaf']['type']
                if kind == 'postflop':
                    pair = (board_joint * reach[0][CLASSES[ids]][:, None]
                            * reach[1][CLASSES[ids]][None, :] * boards[j][hero])
                    marginal = pair.sum(1 if hero == 0 else 0)
                    numerator = np.bincount(CLASSES[ids], weights=marginal, minlength=169)*factor
                    board[:, a] += np.divide(numerator, mass, out=np.zeros(169), where=mass > 0)
                else:
                    payoff = node['leaf']['utilities'][hero] if kind == 'fold' else showdown[hero]
                    pair = joint * reach[0][CLASSES][:, None]*reach[1][CLASSES][None, :]*payoff
                    marginal = pair.sum(1 if hero == 0 else 0)
                    numerator = np.bincount(CLASSES, weights=marginal, minlength=169)
                    exact[:, a] += np.divide(numerator, mass, out=np.zeros(169), where=mass > 0)
        result[i] = exact, board
    return result


def main():
    began = time.monotonic()
    inputs = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (
        Path(__file__), Path(__file__).with_name('stack_context_preflop_expected_components_v2.py'),
        TOOLS/'stack_context_board_components_v1.py', TOOLS/'board_fixed_policy_values_v1.py',
        TOOLS/'board_sorted_terminal_v1.py', TOOLS/'board_sorted_terminal_v2.py')}
    cases = []
    max_reference = 0.
    max_root = 0.
    final = None
    for stack in (20, 40, 100, 200, 400):
        path = Path(r'S:\GTOpen-research\stack-context-population-v1')/f'stack-{stack}'/'context.json'
        inputs[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        context = json.loads(path.read_bytes())
        matrix, pre, w, total, joint, showdown = fixture(context)
        data = board_fixture(context, w)
        obj = PreflopExpectedComponents(context, matrix, pre)
        exact = obj.exact()
        board = obj.board(*data[:4], total)
        independent = reference(context, matrix, pre, joint, showdown, data, total)
        error = max(float(np.max(abs(got[i]['q']-expected[k])))
            for i, expected in independent.items() for k, got in enumerate((exact, board)))
        assert error < 1e-9, (stack, error)
        max_reference = max(max_reference, error)
        e_old = exact_terms(context, matrix, pre)
        b_old = board_terms(context, data[0], data[1], pre, data[2], data[3], total, matrix.bb_mass)
        root_error = max(float(np.max(abs(e_old-exact[0]['q']))),
                         float(np.max(abs(b_old-board[0]['q']))))
        assert root_error < 1e-9
        max_root = max(max_root, root_error)
        for records in (exact, board):
            for i, row in records.items():
                assert np.max(abs((row['advantages']*pre[i]).sum(1))) < 1e-10
                if row['actor'] == 1:
                    assert not row['incoming_class_supported'][1]
                    assert np.all(row['q'][1] == 0)
        cases.append(dict(stack=stack, nodes=len(exact),
            physical_board_holdings=len(data[4]), maximum_forward_error=error,
            maximum_original_root_error=root_error))
        if stack == 400:
            final = context, matrix, pre, data, total, exact, board

    context, matrix, pre, data, total, exact, board = final
    q = {i:p.copy() for i, p in pre.items()}
    q[0][:, 2] = 0
    q[0] /= q[0].sum(1)[:, None]
    blocked_own = PreflopExpectedComponents(context, matrix, q)
    own_e, own_b = blocked_own.exact(), blocked_own.board(*data[:4], total)
    assert np.array_equal(own_e[6]['q'], exact[6]['q'])
    assert np.array_equal(own_b[6]['q'], board[6]['q'])
    assert np.all(own_e[6]['own_history_probability'] == 0)
    assert np.all(own_e[6]['counterfactual_supported'])
    q = {i:p.copy() for i, p in pre.items()}
    q[3][:, 2] = 0
    q[3] /= q[3].sum(1)[:, None]
    blocked_other = PreflopExpectedComponents(context, matrix, q)
    for record in (blocked_other.exact()[6], blocked_other.board(*data[:4], total)[6]):
        assert not np.any(record['counterfactual_supported'])
        assert np.all(record['q'] == 0)
    scaling = []
    for fraction in (1., .25):
        q = {i:p.copy() for i, p in pre.items()}
        q[3][:] = 0
        q[3][:, 2] = fraction
        q[3][:, 0] = 1-fraction
        obj = PreflopExpectedComponents(context, matrix, q)
        scaling.append(obj.exact()[6]['q']+obj.board(*data[:4], total)[6]['q'])
    assert np.max(abs(scaling[1]-.25*scaling[0])) < 1e-11
    snapshot = {i:p.copy() for i, p in pre.items()}
    frozen = PreflopExpectedComponents(context, matrix, snapshot)
    snapshot[0][:] = .25
    assert np.array_equal(frozen.preflop[0], pre[0])
    rejected = []
    def refuse(name, f):
        try: f()
        except (ValueError, KeyError, IndexError, TypeError): rejected.append(name)
        else: raise AssertionError('Accepted malformed '+name)
    for name, change in [('missing-policy', lambda p:p.pop(6)),
                         ('extra-policy', lambda p:p.update({999:np.ones((169, 2))*.5})),
                         ('negative-policy', lambda p:p[6].__setitem__((0, 0), -1)),
                         ('nonfinite-policy', lambda p:p[6].__setitem__((0, 0), np.nan)),
                         ('wrong-arity', lambda p:p.update({6:np.ones((169, 3))/3})),
                         ('unnormalized-policy', lambda p:p[6].__setitem__((0, 0), .123))]:
        p = {i:x.copy() for i, x in pre.items()}; change(p)
        refuse(name, lambda p=p:PreflopExpectedComponents(context, matrix, p))
    for name, change in [('duplicate-board', lambda t:t['board'].__setitem__(4, 0)),
                         ('missing-physical-hand', lambda t:t['hands'][0].pop()),
                         ('missing-branch', lambda t:t['branches'].pop()),
                         ('duplicate-branch', lambda t:t['branches'][1].update(branch=t['branches'][0]['branch']))]:
        t = copy.deepcopy(data[0]); change(t)
        refuse(name, lambda t=t:frozen.board(t, *data[1:4], total))
    c = [x.copy() for x in data[3]]; c[0][0] = (c[0][0]+1) % 169
    refuse('wrong-physical-class', lambda:frozen.board(data[0], data[1], data[2], c, total))
    w = [x.copy() for x in data[2]]; w[0][0] = np.inf
    refuse('nonfinite-entry-weight', lambda:frozen.board(data[0], data[1], w, data[3], total))
    refuse('wrong-pair-normalizer', lambda:frozen.board(*data[:4], 0.))
    for name, change in [('postflop-cycle', lambda t:t['branches'][0]['nodes'][1].update(children=[0])),
                         ('wrong-offset', lambda t:t['branches'][0]['offsets'].__setitem__(0, 77.)),
                         ('wrong-starting-pot', lambda t:t['branches'][0].update(starting_pot=77.)),
                         ('extra-unreachable-post-node', lambda t:t['branches'][0]['nodes'].append(
                             dict(kind=3, actor=0, children=[], payouts=[1, -1, 0]))),
                         ('nonfinite-terminal', lambda t:t['branches'][0]['nodes'][3]['payouts'].__setitem__(0, np.inf)),
                         ('bad-terminal-actor', lambda t:t['branches'][0]['nodes'][3].update(actor=2)),
                         ('missing-chance-child', lambda t:t['branches'][0]['nodes'][1].update(children=[]))]:
        t = copy.deepcopy(data[0]); change(t)
        refuse(name, lambda t=t:frozen.board(t, *data[1:4], total))
    for name, change in [('missing-post-policy', lambda p:p[0].pop(2)),
                         ('extra-post-policy', lambda p:p[0].update({999:p[0][2]})),
                         ('unnormalized-post-policy', lambda p:p[0][2].__setitem__((0, 0), .123)),
                         ('nonfinite-post-policy', lambda p:p[0][2].__setitem__((0, 0), np.nan))]:
        p = [{i:x.copy() for i, x in item.items()} for item in data[1]]; change(p)
        refuse(name, lambda p=p:frozen.board(data[0], p, *data[2:4], total))
    m = copy.deepcopy(matrix); m.bb[0, 0] += .5
    refuse('unconserved-allin', lambda:PreflopExpectedComponents(context, m, pre))
    m = copy.deepcopy(matrix); m.bb[0, 0] = 1000.; m.btn[0, 0] -= 1000.-matrix.bb[0, 0]
    refuse('out-of-bound-allin', lambda:PreflopExpectedComponents(context, m, pre))
    w = [x.copy() for x in data[2]]; w[1][np.flatnonzero(data[3][1] == 1)[0]] = .5
    refuse('mass-on-absent-entry-class', lambda:frozen.board(data[0], data[1], w, data[3], total))
    native_like = copy.deepcopy(data[0])
    for b in native_like['branches']:
        for n in b['nodes']:
            if n['kind'] >= 2: n.pop('children')
    native_rows = frozen.board(native_like, *data[1:4], total)
    assert all(np.array_equal(native_rows[i]['q'], board[i]['q']) for i in board)
    # Node IDs carry no ordering assumption: child pointers define topology.
    permutation = [0, *range(len(context['nodes'])-1, 0, -1)]
    inverse = {old:new for new, old in enumerate(permutation)}
    c = copy.deepcopy(context)
    c['nodes'] = [copy.deepcopy(context['nodes'][old]) for old in permutation]
    for n in c['nodes']: n['children'] = [inverse[j] for j in n['children']]
    p = {inverse[i]:x.copy() for i, x in pre.items()}
    t = copy.deepcopy(data[0])
    for b in t['branches']: b['branch'] = inverse[b['branch']]
    remapped = PreflopExpectedComponents(c, matrix, p)
    remapped_e, remapped_b = remapped.exact(), remapped.board(t, *data[1:4], total)
    assert all(np.array_equal(remapped_e[inverse[i]]['q'], exact[i]['q'])
               and np.array_equal(remapped_b[inverse[i]]['q'], board[i]['q']) for i in exact)
    result = dict(passed=True, cases=cases, maximum_independent_forward_error=max_reference,
        maximum_original_root_error=max_root, excluded_own_past_reach=True,
        preserved_opponent_past_reach_scale=True, zero_incoming_class_mask_checked=True,
        source_policy_snapshot_checked=True, rejected_cases=rejected,
        native_terminal_schema_checked=True, nonsequential_node_ids_checked=True,
        seconds=time.monotonic()-began, inputs=inputs, synthetic_policies_and_payoffs=True,
        native_execution=False, model_inference=False, gpu_used=False, training=False,
        new_scientific_deals=False, accuracy_qualified=False, production_modified=False)
    destination = Path(r'T:\Dev\GTOpen\research\preflop-evolution\blind-defense-20260922')/'stack-context-preflop-expected-components-check-v2-result.json'
    with destination.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, allow_nan=False)
    print(json.dumps({k:v for k, v in result.items() if k != 'inputs'}, indent=2))


if __name__ == '__main__':
    main()
