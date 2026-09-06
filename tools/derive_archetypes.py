#!/usr/bin/env python3
"""Turn report_phh.py's pooled player-type table (types.json, group 'all')
into GTOpen archetypes: cache/archetypes.json — one entry per preflop type
plus its postflop modifiers (station / folder), with every HudStats and
PostflopStats field the profile editor takes and a provenance note.

Mapping (data field -> engine field):
  vpip, pfr, threebet (3-bet % when facing a single raise, all seats)
  open_raise / open_limp = first-in raise / limp % when it is folded to him
  iso_raise / limp_behind = facing limpers with nothing invested: raise / limp %
  fold_to_3bet   = fold % as the RAISER facing a 3-bet
  squeeze        = raise % cold in a squeeze spot (raise + callers in front)
  fourbet        = raise % as the raiser facing a 3-bet
  cont_vs_raise  = 100 - fold % facing a single raise COLD
  cont_vs_raise_limped = 100 - fold % facing a raise AFTER LIMPING (the engine's
                   limp-defence policy; limpers fold far less than cold seats)
  cont_vs_raise_bands = size bands from the cold fold rates: TO <= 3.5bb vs > 5bb
  cont_squeeze   = 100 - fold % after calling/limping, facing a squeeze
  flatten        = naivete by type (not measurable from stats): fish 0.55-0.75,
                   regs 0.15-0.2, nits 0.3
  postflop.cbet[F,T,R]        = bet % with the initiative
  postflop.fold_to_bet[F,T,R] = fold % facing a bet
  postflop.raise_bet          = raise % facing a bet (streets pooled)
  postflop.donk               = bet % without initiative (streets pooled)

Usage: python tools/derive_archetypes.py path/types_micro.json
"""
import sys, json, os

ORDER = ['Nit', 'Tight-passive', 'TAG', 'Loose-passive fish', 'LAG', 'Whale', 'Maniac']
NAIVETE = {'Nit': 0.3, 'Tight-passive': 0.35, 'TAG': 0.15, 'Loose-passive fish': 0.55,
           'LAG': 0.2, 'Whale': 0.75, 'Maniac': 0.6}
BLURB = {
    'Nit': 'Nit: plays under 14% of hands, almost never limps, raises most of what he plays',
    'Tight-passive': 'Tight-passive: plays 14–24% of hands and limps or calls more than he raises',
    'TAG': 'TAG: plays 14–24% of hands, raises 60%+ of them, open-limps ~2%',
    'Loose-passive fish': 'Loose-passive fish: plays 24–48% of hands, mostly by limping and calling',
    'LAG': 'LAG: plays 24–48% of hands and raises 60%+ of them',
    'Whale': 'Whale: plays half the hands or more, mostly by limping and calling',
    'Maniac': 'Maniac: plays half the hands or more and raises most of them',
}
MOD_BLURB = {'station': 'STATION: folds to a flop bet under 45% of the time',
             'folder': 'FOLDER: folds to a flop bet over 65% of the time'}
MIN_PLAYERS = 30

def r1(x, lo=0.0, hi=100.0):
    return None if x is None else round(min(hi, max(lo, x)), 1)

def fmt(x):
    return 'n/a' if x is None else f"{x:.0f}%"

def entry(tname, t, mod=None):
    vpip = r1(t['vpip']); pfr = r1(t['pfr'])
    threebet = r1(t.get('threebet') or 0.0)
    f3b = r1(t.get('fold_to_3bet') if t.get('fold_to_3bet') is not None else 55.0)
    squeeze = r1(t.get('squeeze') if t.get('squeeze') is not None else max(0.5, threebet * 0.6))
    fourbet = t.get('fourbet')
    fc = t.get('fold_vs_raise_cold'); fl = t.get('fold_vs_raise_limped')
    fold_vr = fc if fc is not None else fl
    cont_vs_raise = None if fold_vr is None else r1(max(threebet, 100.0 - fold_vr))
    cont_vs_raise_limped = None if fl is None else r1(100.0 - fl)
    bands = None
    small = t.get('fold_vs_raise_le3.5'); big = t.get('fold_vs_raise_gt5')
    if small is not None and big is not None and big > small + 2:
        bands = [[3.5, r1(max(threebet, 100 - small))], [999.0, r1(max(threebet, 100 - big))]]
    fsq = t.get('fold_vs_squeeze')
    cont_squeeze = None if fsq is None else r1(max(squeeze, 100.0 - fsq))
    stats = {
        'vpip': vpip, 'pfr': pfr, 'threebet': threebet, 'fold_to_3bet': f3b, 'squeeze': squeeze,
        'fourbet': r1(fourbet) if fourbet is not None else None,
        'flatten': NAIVETE.get(tname, 0.4),
        'raise_size': 'max' if tname == 'Nit' else 'min',
        'cont_vs_raise': cont_vs_raise, 'cont_vs_raise_bands': bands, 'cont_squeeze': cont_squeeze,
        'cont_vs_raise_limped': cont_vs_raise_limped,
        'open_raise': r1(t.get('open_raise')), 'open_limp': r1(t.get('open_limp')),
        'iso_raise': r1(t.get('iso_raise')), 'limp_behind': r1(t.get('limp_behind')),
    }
    def g(k, d):
        v = t.get(k); return r1(v) if v is not None else d
    pf = {
        'cbet': [g('cbet_flop', 60), g('cbet_turn', 50), g('cbet_river', 45)],
        'fold_to_bet': [g('fold_vs_bet_flop', 45), g('fold_vs_bet_turn', 45), g('fold_vs_bet_river', 48)],
        'raise_bet': r1(sum(t.get(f'raise_vs_bet_{s}') or 0 for s in ('flop', 'turn', 'river')) / 3.0),
        'donk': r1(sum(t.get(f'stab_{s}') or 0 for s in ('flop', 'turn', 'river')) / 3.0),
        'bet_size': 'min',
    }
    name = f"Data · {tname}" + (f" · {mod}" if mod else "")
    note = (f"{BLURB[tname]}" + (f"; {MOD_BLURB[mod]}" if mod else "") +
            f". Measured from {t['players']:,} real players / {t['hands']:,} hands of 25–50NL online cash, all table sizes "
            f"(HandHQ July 2009 via the U of Toronto PHH dataset). "
            f"First-in: raises {fmt(t.get('open_raise'))} / limps {fmt(t.get('open_limp'))}; vs limpers: iso-raises {fmt(t.get('iso_raise'))} / limps behind {fmt(t.get('limp_behind'))}; "
            f"folds to a raise {fmt(fc)} cold / {fmt(fl)} after limping; folds to a 3-bet as the raiser {fmt(f3b)}; "
            f"c-bets the flop {fmt(t.get('cbet_flop'))} and folds to a flop bet {fmt(t.get('fold_vs_bet_flop'))}.")
    return {'name': name, 'stats': stats, 'postflop': pf, 'note': note,
            'source': {'group': 'micro', 'type': tname, 'mod': mod, 'players': t['players'], 'hands': t['hands']}}

def main():
    types = json.load(open(sys.argv[1], encoding='utf-8'))
    rows = types.get('all') or types.get('fr')
    out = []
    for tname in ORDER:
        t = rows.get(tname)
        if not t or t['players'] < MIN_PLAYERS:
            continue
        out.append(entry(tname, t))
        for mod, sub in (t.get('mods') or {}).items():
            if sub['players'] >= MIN_PLAYERS:
                out.append(entry(tname, sub, mod))
    os.makedirs('cache', exist_ok=True)
    with open('cache/archetypes.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(f"wrote cache/archetypes.json with {len(out)} archetypes")
    for a in out:
        s = a['stats']; p = a['postflop']
        print(f"- {a['name'].encode('ascii', 'replace').decode()}: {s['vpip']}/{s['pfr']}/{s['threebet']} first-in {s['open_raise']}/{s['open_limp']} "
              f"vs limps {s['iso_raise']}/{s['limp_behind']} f3b {s['fold_to_3bet']} cvr {s['cont_vs_raise']} limped {s['cont_vs_raise_limped']} "
              f"| cbet {p['cbet']} f2b {p['fold_to_bet']} rvb {p['raise_bet']} donk {p['donk']} ({a['source']['players']} players)")

if __name__ == '__main__':
    main()
