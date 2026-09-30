"""Exhaustive private-hand split and retained visible-query routing controls.

Synthetic contracts only. No new scientific samples, native calls or fitting.
"""
import copy
import hashlib
import itertools
import json
import os
from pathlib import Path
import time
import traceback
import psutil
import stack_context_private_hand_holdout_v1 as holdout
import stack_context_flop_partition_v1 as flops
from stack_context_teacher_path_v1 import visible_cards
from storage_strategic_common_prior_20260920 import PAIRS, CLASSES, COUNTS

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'stack-context-private-hand-holdout-check-v1'


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream, 'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def save(path, value):
    with Path(path).open('xb') as stream:
        stream.write(flops.encoded(value));stream.flush();os.fsync(stream.fileno())
def source_id(name):return hashlib.sha256(name.encode()).hexdigest()


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    attempt, result, failure = (OUT/(NAME+s+'.json') for s in ('-attempt', '-result', '-failure'))
    assert not any(p.exists() for p in (attempt, result, failure))
    fixtures = [Path(f'S:/GTOpen-research/stack-context-matched-evaluation-integration-check-v1/{d}-cached/queries.json')
        for d in (20, 60)]
    paths = [Path(__file__).resolve(), Path(holdout.__file__).resolve(), Path(flops.__file__).resolve(),
        ROOT/'tools/research/stack_context_teacher_path_v1.py',
        ROOT/'tools/research/storage_strategic_common_prior_20260920.py',
        OUT/'STACK-CONTEXT-PREDICTION-DIAGNOSTIC-DESIGN.md', *fixtures]
    inputs = {str(p):sha(p) for p in paths}
    cfg = holdout.config(namespace='qualification-private-hand-only-v1', buckets=7, test_buckets=[0, 3])
    fcfg = flops.config(namespace='qualification-visible-flop-only-v1', buckets=5, test_buckets=[1])
    sources = holdout.source_config(fit_source_identity=source_id('qualification-fit-source'),
        test_source_identity=source_id('qualification-evaluation-source'))
    save(attempt, dict(inputs=inputs, synthetic_hand_contract=cfg, synthetic_flop_contract=fcfg,
        synthetic_sources_contract=sources, qualification_only=True, scientific_samples=0,
        native_calls=0, fits=0, gpu=False, actual_diagnostic_registered=False))
    began = time.monotonic();negatives = []
    def reject(name, action):
        try:action()
        except (ValueError, KeyError, TypeError):negatives.append(name)
        else:raise AssertionError('Accepted '+name)
    try:
        catalogue = holdout.catalogue(cfg);suit_order_checks = 0
        assert catalogue['combo_multiplicities'] == {4:78, 6:13, 12:78}
        assert sum(catalogue['physical_combos_by_split'].values()) == 1326
        independent_counts = [0]*169
        independent_sides = {'fit':0, 'test':0}
        for i, pair in enumerate(PAIRS.tolist()):
            assert holdout.own_class(pair) == int(CLASSES[i])
            c = int(CLASSES[i]);independent_counts[c] += 1
            raw = hashlib.sha256(flops.encoded([holdout.TYPE, cfg['sha256'], c])).digest()
            expected = 'test' if int.from_bytes(raw, 'big') % 7 in (0, 3) else 'fit'
            assert holdout.assignment(pair, cfg) == expected;independent_sides[expected] += 1
            for suits in itertools.permutations(range(4)):
                mapped = [4*(v//4)+suits[v%4] for v in pair]
                for ordered in (mapped, mapped[::-1]):
                    assert holdout.own_class(ordered) == c and holdout.assignment(ordered, cfg) == expected
                    suit_order_checks += 1
        assert independent_counts == COUNTS.astype(int).tolist()
        assert independent_sides == catalogue['physical_combos_by_split']
        assert len(PAIRS) == 1326 and suit_order_checks == 1326*24*2
        assert cfg == holdout.config(namespace=cfg['namespace'], buckets=7, test_buckets=[3, 0])
        representatives = {s:next(r['representative'] for r in catalogue['rows'] if r['split'] == s)
            for s in ('fit', 'test')}
        controls = [];descendant_checks = 0;visible_suit_checks = 0
        # Independent source identities, not a per-row class flag alone, keep
        # every evaluation parent out of fitting (including its other actor).
        for own_side, hand in representatives.items():
            free = [v for v in range(52) if v not in hand];boards = {}
            for flop in itertools.combinations(free, 3):
                side = flops.visible_partition(flop, phase=1, document=fcfg)
                boards.setdefault(side, list(flop))
                if len(boards) == 2:break
            assert set(boards) == {'fit', 'test'}
            for depth, actor, source in itertools.product(('fit', 'heldout'), (0, 1), ('fit', 'test')):
                base = dict(hand=hand, actor=actor, depth_split=depth, hand_document=cfg,
                    flop_document=fcfg, sources_document=sources, source_side=source, draw_index=37)
                pre = holdout.route(**base, board=[], phase=0)
                expected = (['depth'] if depth == 'heldout' else [])+(['own-hand'] if own_side == 'test' else [])
                assert pre['holdout_axes'] == expected and pre['public_flop_split'] is None
                assert 'canonical_public_flop' not in pre and not pre['preflop_future_board_used']
                assert pre['label_generation_allowed'] == (source == ('test' if expected else 'fit'))
                controls.append(dict(hand=hand, board=[], phase=0, actor=actor, depth_split=depth,
                    source_side=source, draw_index=37, expected=pre))
                for flop_side, flop in boards.items():
                    rest = [v for v in free if v not in flop]
                    expected = (['depth'] if depth == 'heldout' else [])+(['own-hand'] if own_side == 'test' else [])
                    expected += ['public-flop'] if flop_side == 'test' else []
                    for phase, board in ((1, flop), (2, [*flop, rest[0]]), (3, [*flop, rest[0], rest[-1]])):
                        row = holdout.route(**base, board=board, phase=phase)
                        assert row['holdout_axes'] == expected and row['own_hand_split'] == own_side
                        assert row['public_flop_split'] == flop_side and row['source_cluster_identity'] == pre['source_cluster_identity']
                        assert row['label_generation_allowed'] == (source == ('test' if expected else 'fit'))
                        assert row['partition_is_metadata_not_model_input'] and not row['opponent_cards_used']
                        controls.append(dict(hand=hand, board=board, phase=phase, actor=actor, depth_split=depth,
                            source_side=source, draw_index=37, expected=row));descendant_checks += 1
                        for suits in itertools.permutations(range(4)):
                            mh = [4*(v//4)+suits[v%4] for v in hand]
                            mb = [4*(v//4)+suits[v%4] for v in board]
                            mapped = holdout.route(**(base|{'hand':mh[::-1]}), board=mb, phase=phase)
                            assert mapped == row;visible_suit_checks += 1
                        permuted = holdout.route(**base, board=[*board[:3][::-1], *board[3:]], phase=phase)
                        assert permuted == row
        assert descendant_checks == 96 and len(controls) == 112 and visible_suit_checks == 2304
        assert holdout.cluster_identity(sources['fit_source_identity'], 37) != holdout.cluster_identity(sources['test_source_identity'], 37)
        # Route retained canonical native keys. Decoding independently checks
        # that preflop padding never becomes a hidden future-flop test flag.
        native_summary = [];native_controls = []
        for depth, path in zip((20, 60), fixtures):
            doc = read(path);phases = [0]*4;actors = [0]*2;allowed = {'fit':0, 'test':0}
            for index, obs in enumerate(doc['observations']):
                hand, board = visible_cards(obs);phases[obs['phase']] += 1;actors[obs['actor']] += 1
                for source in ('fit', 'test'):
                    args = dict(hand=hand, board=board, phase=obs['phase'], actor=obs['actor'],
                        depth_split='fit' if depth == 20 else 'heldout', hand_document=cfg,
                        flop_document=fcfg, sources_document=sources, source_side=source, draw_index=index)
                    row = holdout.route(**args);allowed[source] += int(row['label_generation_allowed'])
                    assert row['label_side'] == ('test' if row['holdout_axes'] else 'fit')
                    if depth == 60:assert not row['label_generation_allowed'] if source == 'fit' else row['label_generation_allowed']
                    if not obs['phase']:assert row['public_flop_split'] is None and 'canonical_public_flop' not in row
                    native_controls.append(dict(fixture_depth=depth, observation_index=index,
                        source_side=source, expected=row))
            assert all(phases) and all(actors)
            native_summary.append(dict(depth=depth, observations=len(doc['observations']), phases=phases,
                actors=actors, routed_rows=2*len(doc['observations']), allowed_by_source=allowed))
        assert sum(r['observations'] for r in native_summary) == 918
        valid = dict(hand=representatives['fit'], board=[], phase=0, actor=0, depth_split='fit',
            hand_document=cfg, flop_document=fcfg, sources_document=sources, source_side='fit', draw_index=37)
        for name, pair in (('missing private card',[0]),('duplicate private card',[0,0]),
            ('invalid private card',[0,52]),('boolean private card',[False,4]),('floating private card',[0,4.])):
            reject(name, lambda pair=pair:holdout.own_class(pair))
        changed = copy.deepcopy(cfg);changed['namespace'] = 'substituted'
        reject('substituted hand split', lambda:holdout.validate(changed))
        changed = copy.deepcopy(cfg);changed['extra'] = True
        reject('unknown hand contract field', lambda:holdout.validate(changed))
        reject('non-document hand contract', lambda:holdout.validate([]))
        for name, buckets in (('empty test',[ ]),('duplicate test',[0,0]),('all test',list(range(7))),('invalid test',[7])):
            reject(name, lambda buckets=buckets:holdout.config(namespace='x', buckets=7, test_buckets=buckets))
        reject('implicit hand namespace', lambda:holdout.config(namespace='', buckets=7, test_buckets=[0]))
        reject('same parent source', lambda:holdout.source_config(fit_source_identity=sources['fit_source_identity'],
            test_source_identity=sources['fit_source_identity']))
        reject('bad source SHA', lambda:holdout.cluster_identity('not-a-SHA',37))
        for name, index in (('negative parent index',-1),('boolean parent index',True),('overflow parent index',2**63)):
            reject(name, lambda index=index:holdout.cluster_identity(sources['fit_source_identity'],index))
        changed = copy.deepcopy(sources);changed['rule'] = 'reuse test parents'
        reject('changed source rule', lambda:holdout.validate_sources(changed))
        reject('non-document source contract', lambda:holdout.validate_sources([]))
        for name, patch in (('future flop in preflop',{'board':[4,8,12]}),
            ('incomplete flop',{'phase':1,'board':[4,8]}),('future river in flop',{'phase':1,'board':[4,8,12,16,20]}),
            ('own board collision',{'phase':1,'board':[representatives['fit'][0],8,12]}),
            ('boolean actor',{'actor':True}),('unknown actor',{'actor':2}),('unknown phase',{'phase':4}),
            ('implicit depth',{'depth_split':'auto'}),('implicit source',{'source_side':'auto'})):
            reject(name, lambda patch=patch:holdout.route(**(valid|patch)))
        reject('opponent cards used for routing', lambda:holdout.route(**valid, opponent_hand=[48,49]))
        reject('future deal used for routing', lambda:holdout.route(**valid, full_deal=list(range(9))))
        for p, h in inputs.items():assert sha(p) == h
        answer = dict(complete=True, passed=True, seconds=time.monotonic()-began, inputs=inputs,
            synthetic_hand_contract=cfg, synthetic_flop_contract=fcfg, synthetic_sources_contract=sources,
            catalogue=catalogue, independent_physical_counts=independent_counts, suit_order_checks=suit_order_checks,
            controls=controls, descendants_checked=descendant_checks, visible_suit_checks=visible_suit_checks,
            retained_native_summary=native_summary, retained_native_controls=native_controls,
            corruption_rejections=negatives, qualification_only=True, scientific_samples=0, native_calls=0,
            fits=0, gpu=False, production_modified=False, actual_diagnostic_registered=False,
            actual_diagnostic_complete=False, scientific_accuracy_evidence=False,
            unseen_own_classes_globally_excluded=True, preflop_future_board_never_used=True,
            source_independence_is_registration_requirement=True)
        save(result, answer)
        print(json.dumps({k:answer[k] for k in ('passed','seconds','suit_order_checks','descendants_checked','visible_suit_checks')}))
    except BaseException as error:
        save(failure, dict(complete=False, passed=False, error=repr(error), traceback=traceback.format_exc(),
            preserve_evidence=True, automatic_retry_allowed=False));raise


if __name__ == '__main__':main()
