#!/usr/bin/env python3
"""Turn report_phh.py's player-type tables (types.json per stake group) into
GTOpen archetypes: cache/archetypes.json, one entry per (stake group, table
size, type) with every HudStats / PostflopStats field the profile editor
takes, plus a provenance note.

Mapping (data field -> engine field):
  vpip, pfr, threebet (3-bet % when facing a single raise, all seats)
  fold_to_3bet   = fold % as the RAISER facing a 3-bet
  squeeze        = raise % cold in a squeeze spot (raise + callers in front)
  fourbet        = raise % as the raiser facing a 3-bet
  cont_vs_raise  = 100 - fold % facing a single raise (cold and after limping,
                   pooled the way the engine's VS RAISE bucket is)
  cont_vs_raise_bands = size bands from the cold fold rates: TO <= 3.5bb vs > 5bb
  cont_squeeze   = 100 - fold % after calling/limping, facing a squeeze
  flatten        = naivete by type (not measurable from stats): fish 0.6-0.75,
                   semi-loose 0.45, regs 0.15-0.25, nits 0.3
  postflop.cbet[F,T,R]        = bet % with the initiative
  postflop.fold_to_bet[F,T,R] = fold % facing a bet
  postflop.raise_bet          = raise % facing a bet (streets pooled)
  postflop.donk               = bet % without initiative (streets pooled)

Usage: python tools/derive_archetypes.py micro=path/types_micro.json low=path/types_low.json ...
"""
import sys, json, os

NAIVETE = {
    'Nit / OMC': 0.3, 'TAG reg': 0.15, 'Tight-passive': 0.35, 'LAG reg': 0.2,
    'Loose-passive (semi)': 0.45, 'Loose-aggressive fish': 0.55, 'Loose-passive fish': 0.65,
    'Whale (VPIP 48+)': 0.75, 'Maniac (VPIP 48+, aggressive)': 0.6,
}
SHORT = {
    'Nit / OMC': 'Nit', 'TAG reg': 'TAG', 'Tight-passive': 'Tight-passive', 'LAG reg': 'LAG',
    'Loose-passive (semi)': 'Loose-passive', 'Loose-aggressive fish': 'Aggro fish',
    'Loose-passive fish': 'Passive fish', 'Whale (VPIP 48+)': 'Whale', 'Maniac (VPIP 48+, aggressive)': 'Maniac',
}
GROUP_LABEL = {'micro': '25–50NL', 'low': '100–200NL', 'mid': '400–1000NL'}
SIZE_LABEL = {'fr': 'full ring', '6m': '6-max'}

def r1(x, lo=0.0, hi=100.0):
    return None if x is None else round(min(hi, max(lo, x)), 1)

def entry(group, size, tname, t):
    vpip = r1(t['vpip']); pfr = r1(t['pfr'])
    threebet = r1(t.get('threebet') or 0.0)
    f3b = r1(t.get('fold_to_3bet') if t.get('fold_to_3bet') is not None else 55.0)
    squeeze = r1(t.get('squeeze') if t.get('squeeze') is not None else max(0.5, threebet * 0.6))
    fourbet = t.get('fourbet')
    # continue vs raise: pool cold and after-limping fold rates by their sample
    fc = t.get('fold_vs_raise_cold'); fl = t.get('fold_vs_raise_limped')
    if fc is not None and fl is not None:
        fold_vr = 0.85 * fc + 0.15 * fl   # cold decisions dominate the bucket mass
    else:
        fold_vr = fc if fc is not None else fl
    cont_vs_raise = None if fold_vr is None else r1(max(threebet, 100.0 - fold_vr))
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
        'raise_size': 'max' if tname.startswith('Nit') else 'min',
        'cont_vs_raise': cont_vs_raise, 'cont_vs_raise_bands': bands, 'cont_squeeze': cont_squeeze,
    }
    def g(k, d):
        v = t.get(k); return r1(v) if v is not None else d
    pf = {
        'cbet': [g('cbet_flop', 60), g('cbet_turn', 50), g('cbet_river', 45)],
        'fold_to_bet': [g('fold_vs_bet_flop', 45), g('fold_vs_bet_turn', 45), g('fold_vs_bet_river', 48)],
        'raise_bet': r1(sum(t.get(f'raise_vs_bet_{s}') or 0 for s in ('flop','turn','river')) / 3.0),
        'donk': r1(sum(t.get(f'stab_{s}') or 0 for s in ('flop','turn','river')) / 3.0),
        'bet_size': 'min',
    }
    name = f"Data · {SHORT[tname]} ({SIZE_LABEL[size]} {GROUP_LABEL[group]})"
    note = (f"Measured from {t['players']:,} real players / {t['hands']:,} hands, {SIZE_LABEL[size]} {GROUP_LABEL[group]} "
            f"online cash (HandHQ July 2009 via the U of Toronto PHH dataset). Type = VPIP/PFR cluster. "
            f"Folds to a raise {fold_vr:.0f}% (cold {fc if fc is not None else float('nan'):.0f}%, after limping {fl if fl is not None else float('nan'):.0f}%), "
            f"to a 3-bet as raiser {f3b:.0f}%, opens by limping {t.get('open_limp') or 0:.0f}% / raising {t.get('open_raise') or 0:.0f}%.")
    return {'name': name, 'stats': stats, 'postflop': pf, 'note': note,
            'source': {'group': group, 'size': size, 'type': tname, 'players': t['players'], 'hands': t['hands']}}

def main():
    # Only the micro group ships as archetypes (the looser 2009 25-50NL pools
    # are the closest public analogue to live low stakes); the other groups
    # stay in the research tables. Clusters under 30 players are too thin.
    out = []
    for arg in sys.argv[1:]:
        group, path = arg.split('=', 1)
        if group != 'micro':
            continue
        types = json.load(open(path))
        for size in ('fr', '6m'):
            for tname, t in types.get(size, {}).items():
                if tname == 'other' or t['players'] < 30:
                    continue
                out.append(entry(group, size, tname, t))
    order = ['Whale', 'Passive fish', 'Aggro fish', 'Maniac', 'Loose-passive', 'LAG', 'TAG', 'Tight-passive', 'Nit']
    out.sort(key=lambda a: (a['source']['group'] != 'micro', a['source']['size'] != 'fr',
                            order.index(SHORT[a['source']['type']])))
    os.makedirs('cache', exist_ok=True)
    with open('cache/archetypes.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(f"wrote cache/archetypes.json with {len(out)} archetypes")
    for a in out:
        s = a['stats']; p = a['postflop']
        print(f"- {a['name']}: {s['vpip']}/{s['pfr']}/{s['threebet']} f3b {s['fold_to_3bet']} sq {s['squeeze']} cvr {s['cont_vs_raise']} bands {s['cont_vs_raise_bands']} csq {s['cont_squeeze']} | cbet {p['cbet']} f2b {p['fold_to_bet']} rvb {p['raise_bet']} donk {p['donk']}")

if __name__ == '__main__':
    main()
