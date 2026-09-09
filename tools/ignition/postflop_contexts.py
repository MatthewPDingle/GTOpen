"""Retrospective, heads-up postflop opportunity audit; never modifies live models.

One process, standard library only. Full canonical validation precedes extraction.
Published output contains aggregates only (no cards, player IDs, or raw histories).
"""
import argparse
import collections
import hashlib
import importlib.util
import json
import math
import random
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_FROM = '2025-11-03'  # Existing, already inspected historical period.
KINDS = ('donk', 'stab', 'lead', 'probe')


def adapter():
    spec = importlib.util.spec_from_file_location('ignition_post_adapter', Path(__file__).with_name('analyze.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def classify(street, actor, oop, initiative, prior_aggressor, checked):
    """Mutually exclusive no-initiative contexts, before the first street bet."""
    if actor == initiative:
        return 'initiative'
    if initiative in checked:
        return 'stab'
    if actor == oop and initiative is not None:
        if street == 0:
            return 'donk'
        return 'lead' if prior_aggressor is not None else 'probe'
    return 'no_initiative_other'


def extract(canonical, cp):
    """Only call after cp.replay succeeds. Track amounts, checks and initiative.

    Retain every observed zero-price decision in audit counters, but only emit
    population observations when exactly two players reached the flop and both
    can still act. Never synthesize checks during an all-in runout.
    """
    pre, rest = canonical.split('*** HOLE CARDS ***', 1)
    seats = [m for line in pre.splitlines() if (m := cp.SEAT.match(line))]
    names = [m[2] for m in seats]
    stack = {m[2]: cp.cents(m[3]) for m in seats}
    paid = dict.fromkeys(names, 0)
    contrib = dict.fromkeys(names, 0)
    btn = int(re.search(r'Seat #(\d+) is the button', pre)[1])
    btn_index = [int(m[1]) for m in seats].index(btn)
    order = names[btn_index+1:] + names[:btn_index+1]
    for line in pre.splitlines():
        if m := cp.POST.match(line):
            paid[m[1]] += cp.cents(m[3])
            if m[2] != 'the ante':
                contrib[m[1]] += cp.cents(m[3])
    cur = max(contrib.values())
    active = set(names)
    street, raises = -1, 0
    initiative = prior_aggressor = street_aggressor = None
    checked = set()
    hu_flop, oop = False, None
    events, audit = [], collections.Counter()
    for line in rest.splitlines():
        if line.startswith('*** SUMMARY ***'):
            break
        if any(line.startswith('*** '+s+' ***') for s in ('FLOP', 'TURN', 'RIVER')):
            street += 1
            prior_aggressor = street_aggressor
            if street_aggressor is not None:
                initiative = street_aggressor
            street_aggressor = None
            checked = set()
            contrib = dict.fromkeys(names, 0)
            cur = 0
            if street == 0:
                hu_flop = len(active) == 2
                oop = next((p for p in order if p in active), None)
            continue
        if m := cp.RETURN.match(line):
            amount, player = cp.cents(m[1]), m[2]
            contrib[player] -= amount
            paid[player] -= amount
            continue
        m = cp.ACTION.match(line)
        if not m:
            continue
        player, action, amount, to, _ = m.groups()
        if street >= 0 and cur == contrib[player] and '[ME]' not in player:
            broad = 'initiative' if initiative == player else 'no_initiative'
            audit[f'post/{("flop", "turn", "river")[street]}/{broad}|{action[:-1] if action != "checks" else "check"}'] += 1
            if hu_flop and len(active) == 2 and all(paid[p] < stack[p] for p in active):
                kind = classify(street, player, oop, initiative, prior_aggressor, checked)
                pot = sum(paid.values())
                bet = action == 'bets'
                events.append(dict(street=street, kind=kind,
                    pot_type='limped' if raises == 0 else 'single_raised' if raises == 1 else 'three_bet_plus',
                    bet=bet, jam=bool(bet and cp.cents(amount) == stack[player]-paid[player]),
                    size_pot=cp.cents(amount)/pot if bet else None))
        if action == 'folds':
            active.remove(player)
        elif action == 'checks':
            checked.add(player)
        elif action == 'calls':
            delta = cp.cents(amount)
            paid[player] += delta
            contrib[player] += delta
        elif action in ('bets', 'raises'):
            target = cp.cents(to if action == 'raises' else amount)
            paid[player] += target-contrib[player]
            contrib[player] = cur = target
            street_aggressor = player
            if street < 0:
                raises += 1
    return events, audit


def aggregate(events):
    result = {}
    for event in events:
        key = (event['street'], event['kind'], event['pot_type'])
        row = result.setdefault(key, dict(street=key[0], kind=key[1], pot_type=key[2], opportunities=0, bets=0,
                                         allin_bets=0, ordinary_sizes=collections.Counter()))
        row['opportunities'] += 1
        row['bets'] += int(event['bet'])
        row['allin_bets'] += int(event['jam'])
        if event['bet'] and not event['jam']:
            # Evidence only, never projected into a tree by this collector.
            band = 'up_to_33' if event['size_pot'] <= .335 else 'up_to_50' if event['size_pot'] <= .505 else 'up_to_75' if event['size_pot'] <= .755 else 'up_to_100' if event['size_pot'] <= 1.005 else 'over_100'
            row['ordinary_sizes'][band] += 1
    return [result[k] for k in sorted(result)]


def validation(sessions):
    """Predeclared fixed shrinkage, not tuned on reused evaluation dates."""
    train_sessions = [s for s in sessions if max(e['date'] for e in s['events']) < TEST_FROM]
    test_sessions = [s for s in sessions if min(e['date'] for e in s['events']) >= TEST_FROM]
    train = [e for s in train_sessions for e in s['events']]
    test = [e for s in test_sessions for e in s['events']]
    train_rows = {(r['street'], r['kind'], r['pot_type']): r for r in aggregate(train)}
    relevant = [e for e in train if e['kind'] in KINDS]
    broad = (sum(e['bet'] for e in relevant)+.5)/(len(relevant)+1)
    results = []
    for row in aggregate(test):
        if row['kind'] not in KINDS:
            continue
        key = (row['street'], row['kind'], row['pot_type'])
        tr = train_rows.get(key, dict(opportunities=0, bets=0))
        predicted = (tr['bets']+20*broad)/(tr['opportunities']+20)
        n, b = row['opportunities'], row['bets']
        loss = lambda p: -(b*math.log(p)+(n-b)*math.log1p(-p))/n
        results.append(dict(street=key[0], kind=key[1], pot_type=key[2], train_opportunities=tr['opportunities'],
            test_opportunities=n, test_bets=b, predicted=predicted, observed=b/n,
            broad_predicted=broad, broad_log_loss=loss(broad), context_log_loss=loss(predicted)))
    total = sum(r['test_opportunities'] for r in results)
    session_scores = []
    for session in test_sessions:
        gain, n = 0., 0
        for event in session['events']:
            if event['kind'] not in KINDS:
                continue
            tr = train_rows.get((event['street'], event['kind'], event['pot_type']), dict(opportunities=0, bets=0))
            predicted = (tr['bets']+20*broad)/(tr['opportunities']+20)
            loss = lambda prob: -math.log(prob if event['bet'] else 1-prob)
            gain += loss(broad)-loss(predicted)
            n += 1
        if n:
            session_scores.append((gain, n))
    interval = None
    if len(session_scores) >= 2:
        rng = random.Random(20260910)
        samples = []
        for _ in range(1000):
            chosen = rng.choices(session_scores, k=len(session_scores))
            samples.append(sum(x[0] for x in chosen)/sum(x[1] for x in chosen))
        samples.sort()
        interval = [samples[25], samples[974]]
    return dict(test_from=TEST_FROM, retrospective=True, prior_strength=20, fresh_holdout=False,
                note='Existing historical evaluation period already inspected; descriptive calibration only. No release gate or board/hand-specific evidence.',
                train_sessions=len(train_sessions), test_sessions=len(test_sessions),
                excluded_boundary_sessions=len(sessions)-len(train_sessions)-len(test_sessions),
                scoring_sessions=len(session_scores), gain_95_session_bootstrap=interval,
                bootstrap='1000 paired session resamples, seed 20260910; descriptive historical interval, not fresh validation.',
                evaluated_opportunities=total,
                broad_log_loss=sum(r['test_opportunities']*r['broad_log_loss'] for r in results)/total if total else None,
                context_log_loss=sum(r['test_opportunities']*r['context_log_loss'] for r in results)/total if total else None, rows=results)


def run(source, out, stake=10, zone=False, pause_ms=20):
    a = adapter()
    seen, sessions, audit, manifest = {}, [], collections.Counter(), []
    for i, path in enumerate(a.source_paths(source, stake, zone)):
        raw = path.read_bytes()
        manifest.append(hashlib.sha256(raw).hexdigest())
        events = []
        for block in re.split(r'(?=^Ignition Hand #)', raw.decode('utf-8-sig', errors='replace'), flags=re.M):
            match = re.match(r'Ignition Hand #(\d+)', block)
            if not match:
                continue
            audit['raw'] += 1
            digest = hashlib.sha256(block.strip().encode()).hexdigest()
            if match[1] in seen:
                audit['duplicates'] += 1
                audit['duplicate_variants'] += int(seen[match[1]] != digest)
                continue
            seen[match[1]] = digest
            try:
                canonical, _ = a.convert(block)
                meta, counters = a.cp.replay(canonical, stake, variant='ignition')
            except (a.cp.Invalid, ValueError, KeyError, TypeError) as error:
                audit['excluded/'+str(error)] += 1
                continue
            rows, replayed = extract(canonical, a.cp)
            expected = collections.Counter()
            for player, counts in counters.items():
                if '[ME]' in player:
                    continue
                for key, count in counts.items():
                    if key.startswith(('post/flop/', 'post/turn/', 'post/river/')) and ('/initiative|' in key or '/no_initiative|' in key):
                        expected[key] += count
            if replayed != expected:
                raise ValueError('Independent postflop extraction disagrees with canonical opportunity counters')
            audit['accepted'] += 1
            for row in rows:
                row['date'] = meta['date']
            events.extend(rows)
        if events:
            sessions.append(dict(events=events))
        if i % 100 == 0:
            print(f'{i} files; {audit["accepted"]} valid hands', flush=True)
        time.sleep(pause_ms/1000)
    all_events = [e for s in sessions for e in s['events']]
    rows = aggregate(all_events)
    result = dict(schema=1, site='Ignition', stake=f'NL{stake} {"Zone" if zone else "regular"}',
        audit=dict(audit), source_files=len(manifest), sessions_with_eligible_decisions=len(sessions),
        source_content_sha256=hashlib.sha256('\n'.join(manifest).encode()).hexdigest(),
        dependencies={str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__), Path(__file__).with_name('analyze.py'), ROOT/'tools/coinpoker/analyze.py']},
        contextual_bets=[{k:r[k] for k in ('street','kind','pot_type','opportunities','bets')} for r in rows if r['kind'] in KINDS],
        all_contexts=rows, validation=validation(sessions),
        definitions=dict(donk='Flop OOP lead without initiative before the preflop aggressor acts.',
            lead='Turn/river OOP lead into the prior street aggressor before that player acts.',
            probe='Turn/river OOP lead without carried initiative after the preceding street checked through.',
            stab='Bet without carried initiative after its holder has checked this street.',
            no_initiative_other='No carried aggressor or unmatched no-initiative situation; not exported as evidence.'),
        limitations=['Exactly two players at flop; excludes multiway flops even if subsequently heads-up.',
            'Both players must still have chips. All-in bets count as bets; all-in runout checks are never invented.',
            'Hero excluded; opponent actions retained against hero. Anonymous pooled opponents, not individual player profiles.',
            'Pot type is preflop raise count. No position, board, stack, hand-strength, or bet-size conditional prediction.',
            'Counts are correlated within hands/sessions; opportunity counts are not independent effective sample sizes.',
            'Historical short-raise, incomplete and other canonical exclusions remain unchanged. No direct fresh-period validation.'])
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes((json.dumps(result, indent=2, allow_nan=False)+'\n').encode('utf-8'))
    print(json.dumps(dict(audit=audit, contexts=result['contextual_bets'], validation={k:v for k,v in result['validation'].items() if k != 'rows'}), indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default='T:/Dev/Poker Data/Ignition')
    parser.add_argument('--out', default=str(ROOT/'research/ignition-postflop-contexts/evidence.json'))
    parser.add_argument('--stake', type=int, default=10)
    parser.add_argument('--zone', action='store_true')
    parser.add_argument('--pause-ms', type=int, default=20)
    args = parser.parse_args()
    run(args.source, args.out, args.stake, args.zone, args.pause_ms)
