"""Independent structural/accounting checks for a read-only HU context export.

No solve, fitting, GPU use, or live-server access. The candidate is a geometry
fixture, not an accepted training range or evidence of improved blind defense.
"""
import copy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def close(a, b, tol=1e-8):
    assert math.isfinite(a) and math.isfinite(b)
    assert abs(a-b) <= tol, (a, b)


def audit(d):
    cfg, nodes = d['config'], d['nodes']
    seats = d['original_seats']
    assert len(seats) == len(set(seats)) == 2
    assert d['postflop_order'] == [0, 1]
    assert d['positions'] == [cfg['positions'][p] for p in seats]
    # Independently reproduce the documented postflop ordering convention.
    if len(cfg['positions']) == 2:
        order = sorted(range(2), key=lambda p: (-cfg['posts'][p], -p))
    else:
        blinds = sorted((p for p, v in enumerate(cfg['posts']) if v > 0), key=lambda p: cfg['posts'][p])
        order = blinds + [p for p in range(len(cfg['positions'])) if p not in blinds]
    assert seats == [p for p in order if p in seats]
    assert nodes[0]['kind'] == 0
    mask = sum(1 << p for p in seats)
    assert nodes[0]['original_live'] == mask
    dead = sum(v for p, v in enumerate(nodes[0]['original_invested']) if p not in seats)
    close(d['dead_money'], dead)
    close(d['rake_fraction'], cfg['rake_pct']/100)
    close(d['rake_cap'], cfg['rake_cap'])
    assert cfg['no_flop_no_drop'] or cfg['rake_pct'] == 0 or cfg['rake_cap'] == 0
    parents = [0] * len(nodes)
    terminal_counts = {'fold': 0, 'postflop': 0, 'showdown': 0}
    for i, n in enumerate(nodes):
        assert n['kind'] in (0, 1, 2)
        assert n['original_live'] & ~mask == 0
        close(sum(n['original_invested']), n['pot'])
        assert n['invested'] == [n['original_invested'][p] for p in seats]
        assert all(0 <= v <= cfg['stack'] + cfg['ante'] + 1e-8 for v in n['original_invested'])
        for p in range(len(cfg['positions'])):
            if p not in seats:
                close(n['original_invested'][p], nodes[0]['original_invested'][p])
        close(n['pot'] - sum(n['invested']), dead)
        assert len(n['actions']) == len(n['children'])
        if n['kind'] == 0:
            assert n['leaf'] is None and n['winner'] is None
            actor = n['actor']
            assert actor in (0, 1) and seats[actor] == n['original_actor']
            assert n['original_live'] == mask
            assert len(n['strategy']) == 169*len(n['actions'])
            assert all(math.isfinite(v) and 0 <= v <= 1.000001 for v in n['strategy'])
            for h in range(169):
                close(sum(n['strategy'][a*169+h] for a in range(len(n['actions']))), 1, 2e-6)
            for a, (action, child_id) in enumerate(zip(n['actions'], n['children'])):
                assert i < child_id < len(nodes)
                parents[child_id] += 1
                child = nodes[child_id]
                assert child['path'] == n['path'] + [a]
                expected = n['original_invested'].copy()
                next_live = n['original_live']
                if action['kind'] == 'fold':
                    next_live &= ~(1 << seats[actor])
                elif action['kind'] != 'check':
                    assert action['kind'] in ('call', 'raise', 'jam')
                    expected[seats[actor]] = action['to'] + cfg['ante']
                    assert expected[seats[actor]] >= n['invested'][actor] - 1e-8
                assert child['original_live'] == next_live
                for x, y in zip(expected, child['original_invested']):
                    close(x, y)
        else:
            assert not n['children'] and not n['strategy'] and n['actor'] is None
            leaf = n['leaf']
            terminal_counts[leaf['type']] += 1
            if n['kind'] == 1:
                assert leaf['type'] == 'fold'
                assert n['winner'] in (0, 1)
                assert n['original_live'] == 1 << seats[n['winner']]
                assert n['original_winner'] == seats[n['winner']]
                for p in range(2):
                    close(leaf['utilities'][p], (n['pot'] if p == n['winner'] else 0) - n['invested'][p])
                close(sum(leaf['utilities']), dead)
            else:
                assert n['original_live'] == mask and n['winner'] is None
                close(n['invested'][0], n['invested'][1])
                remaining = cfg['stack'] + cfg['ante'] - n['invested'][0]
                assert leaf['type'] == ('postflop' if remaining > 1e-8 else 'showdown')
                close(leaf['starting_pot'], n['pot'])
                close(leaf['effective_stack'], remaining)
                for p in range(2):
                    close(leaf['value_offsets'][p], n['pot']/2 - n['invested'][p])
                # Test win, tie, and loss chip identities without any equity model.
                rake = min(n['pot']*d['rake_fraction'], d['rake_cap'])
                for equity in (0, .5, 1):
                    u0 = equity*(n['pot']-rake)-n['invested'][0]
                    u1 = (1-equity)*(n['pot']-rake)-n['invested'][1]
                    close(u0+u1+rake, dead)
    assert parents == [0] + [1]*(len(nodes)-1), 'disconnected or reused node'
    support = []
    for mass in d['incoming_class_mass']:
        assert len(mass) == 169 and all(math.isfinite(v) and v >= 0 for v in mass)
        combo_weights = [v/(6 if c//13 == c%13 else 4 if c//13 > c%13 else 12) for c, v in enumerate(mass)]
        maximum = max(combo_weights)
        assert maximum > 0
        support.append(sum(v/maximum >= 1e-5 for v in combo_weights))
    return {'nodes': len(nodes), 'terminals': terminal_counts, 'positions': d['positions'],
            'dead_money': dead, 'classes_at_current_entry_cutoff': support}


def compare_original(old, new):
    for field in ('iteration', 'config', 'root_path', 'original_seats', 'postflop_order', 'incoming_class_mass', 'class_base'):
        assert old[field] == new[field], field
    assert len(old['nodes']) == len(new['nodes'])
    for a, b in zip(old['nodes'], new['nodes']):
        for field in ('original_node', 'path', 'kind', 'original_actor', 'children', 'strategy',
                      'pot', 'invested', 'original_invested', 'original_live', 'original_winner', 'r', 'actions'):
            assert a[field] == b[field], (a['path'], field)
        if a['kind'] == 0:
            assert a['actor'] == b['actor']
        elif a['kind'] == 1:
            assert a['winner'] == b['winner']


def main():
    output = OUT/'export-audit.json'
    assert not output.exists(), 'preserve evidence'
    original_path = ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
    original = json.loads(original_path.read_text())
    paths = [OUT/'original-context-reexport.json', OUT/'bb-context-candidate.json']
    contexts = [json.loads(p.read_text()) for p in paths]
    reviews = [audit(d) for d in contexts]
    compare_original(original, contexts[0])
    bb = contexts[1]
    assert bb['positions'] == ['BB', 'BTN'] and reviews[1]['classes_at_current_entry_cutoff'][0] == 169
    assert bb['nodes'][0]['actions'][1]['to'] - bb['nodes'][0]['invested'][0] == 1
    # Rejection controls target old-context leakage and malformed topology.
    negative = []
    for name, mutate in [
        ('wrong_pot_offset', lambda d: d['nodes'][2]['leaf']['value_offsets'].__setitem__(0, 1.75)),
        ('third_live_player', lambda d: d['nodes'][0].__setitem__('original_live', 0b1100001)),
        ('swapped_postflop_order', lambda d: d.__setitem__('original_seats', list(reversed(d['original_seats'])))),
        ('percent_as_fraction', lambda d: d.__setitem__('rake_fraction', 5.)),
        ('wrong_remaining_stack', lambda d: d['nodes'][2]['leaf'].__setitem__('effective_stack', 182.)),
        ('duplicate_child', lambda d: d['nodes'][0]['children'].__setitem__(1, 1)),
        ('unmatched_call', lambda d: d['nodes'][0]['actions'][1].__setitem__('to', 3.)),
    ]:
        invalid = copy.deepcopy(bb)
        mutate(invalid)
        try:
            audit(invalid)
        except AssertionError:
            negative.append(name)
        else:
            raise AssertionError(f'failed to reject {name}')
    before = json.loads((OUT/'export-inputs-before.json').read_text())
    for p, expected in before['inputs'].items():
        assert sha(ROOT/p) == expected, p
    inputs = [*paths, original_path, OUT/'export-inputs-before.json', Path(__file__),
              ROOT/'crates/solver/examples/conditional_hu_context_export.rs',
              ROOT/'target/release/examples/conditional_hu_context_export.exe']
    report = {'passed': True, 'purpose': 'context geometry qualification only',
              'original_strategy_and_reaches_exact': True, 'source_files_unchanged': True,
              'contexts': reviews, 'rejection_controls': negative,
              'inputs': {str(p.relative_to(ROOT)): sha(p) for p in inputs},
              'ready_for_strategic_training': False, 'production_modified': False}
    with output.open('x') as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
