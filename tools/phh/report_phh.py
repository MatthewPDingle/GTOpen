#!/usr/bin/env python3
"""Turn analyze_phh.py's counters into pool tables and data-grounded player
types. Prints markdown; writes types.json with every number the GTOpen
profile editor takes (so archetypes can be generated from it).

Usage: python report_phh.py phh_stats.json [--min-hands 300] [--size fr|6m]
"""
import sys, json, argparse, collections, math
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def pct(c, num, den):
    n = sum(c.get(k, 0) for k in num)
    d = sum(c.get(k, 0) for k in den)
    return (100.0 * n / d if d else float('nan')), d

def key(*parts):
    return '|'.join(map(str, parts))

# ------------------------------------------------------------ pool tables --

def pool_report(pool, size):
    out = []
    H = pool.get(key('hand', size), {})
    dealt = H.get('dealt', 0)
    out.append(f"**{ {'fr':'Full ring (7-9 dealt)','6m':'6-max (4-6 dealt)','hu':'Heads-up'}[size] }** — {dealt:,} player-hands")
    out.append(f"- VPIP {100*H.get('vpip',0)/max(dealt,1):.1f}% · PFR {100*H.get('pfr',0)/max(dealt,1):.1f}% · limp (open-limp or limp-behind) {100*H.get('limp',0)/max(dealt,1):.1f}%")
    def sit(name, sit_key, cold):
        c = pool.get(key('pre', sit_key, cold, size), {})
        d = sum(c.values())
        if not d: return
        parts = ' · '.join(f"{k} {100*v/d:.1f}%" for k, v in sorted(c.items(), key=lambda kv: -kv[1]))
        out.append(f"- {name} (n={d:,}): {parts}")
    sit('unopened (first in)', 'unopened', 'cold')
    sit('BB option (no raise)', 'bb_free', 'cold')
    sit('vs limps (cold)', 'vs_limps', 'cold')
    sit('vs raise, cold', 'vs_raise', 'cold')
    sit('vs raise after LIMPING', 'vs_raise', 'inv')
    sit('squeeze spot, cold (raise + callers in front)', 'squeeze', 'cold')
    sit('vs squeeze / raise after calling', 'squeeze', 'inv')
    sit('vs 3-bet as the RAISER', 'vs_3bet', 'inv')
    sit('vs 3-bet COLD', 'vs_3bet', 'cold')
    sit('vs 4-bet+ (invested)', 'vs_4bet_plus', 'inv')
    # size bands
    for cold, label in (('cold', 'cold'), ('inv', 'after limping')):
        rows = []
        for band in ('le2.5', 'le3.5', 'le5', 'gt5'):
            c = pool.get(key('pre_size', 'vs_raise', cold, band, size), {})
            d = sum(c.values())
            if d < 200: continue
            rows.append(f"TO {band}: fold {100*c.get('fold',0)/d:.0f}% / call {100*c.get('call',0)/d:.0f}% / raise {100*c.get('raise',0)/d:.0f}% (n={d:,})")
        if rows:
            out.append(f"- vs raise {label}, by raise size — " + '; '.join(rows))
    # postflop
    for st in ('flop', 'turn', 'river'):
        cb = pool.get(key('post', 'cbet', st, size), {}); dcb = sum(cb.values())
        stab = pool.get(key('post', 'stab', st, size), {}); dst = sum(stab.values())
        vb = pool.get(key('post', 'vs_bet', st, size), {}); dvb = sum(vb.values())
        out.append(f"- {st}: bet with initiative {100*cb.get('bet',0)/max(dcb,1):.1f}% (n={dcb:,}) · bet without initiative {100*stab.get('bet',0)/max(dst,1):.1f}% (n={dst:,}) · vs bet: fold {100*vb.get('fold',0)/max(dvb,1):.1f}% / call {100*vb.get('call',0)/max(dvb,1):.1f}% / raise {100*vb.get('raise',0)/max(dvb,1):.1f}% (n={dvb:,})")
    return '\n'.join(out)

# ------------------------------------------------------------ player types --

def player_stats(p):
    """Every profile-editor number for one player (None where no sample)."""
    H = p.get(key('hand'), {}); dealt = H.get('dealt', 0)
    def frac(k, num, den, minn=25):
        c = p.get(k, {}); d = sum(c.get(x, 0) for x in den)
        if d < minn: return None, d
        return 100.0 * sum(c.get(x, 0) for x in num) / d, d
    s = {'hands': dealt,
         'vpip': 100*H.get('vpip',0)/dealt, 'pfr': 100*H.get('pfr',0)/dealt, 'limp': 100*H.get('limp',0)/dealt}
    s['open_raise'], s['n_unopened'] = frac(key('pre','unopened','cold'), ['raise'], ['fold','call','raise'])
    s['open_limp'], _ = frac(key('pre','unopened','cold'), ['call'], ['fold','call','raise'])
    s['limp_behind'], s['n_vs_limps'] = frac(key('pre','vs_limps','cold'), ['call'], ['fold','call','raise'])
    s['iso_raise'], _ = frac(key('pre','vs_limps','cold'), ['raise'], ['fold','call','raise'])
    s['threebet'], s['n_vs_raise'] = frac(key('pre','vs_raise','cold'), ['raise'], ['fold','call','raise'])
    s['fold_vs_raise_cold'], _ = frac(key('pre','vs_raise','cold'), ['fold'], ['fold','call','raise'])
    s['fold_vs_raise_limped'], s['n_limp_raised'] = frac(key('pre','vs_raise','inv'), ['fold'], ['fold','call','raise'])
    s['limp_raise'], _ = frac(key('pre','vs_raise','inv'), ['raise'], ['fold','call','raise'])
    s['squeeze'], s['n_squeeze'] = frac(key('pre','squeeze','cold'), ['raise'], ['fold','call','raise'])
    s['fold_vs_squeeze'], _ = frac(key('pre','squeeze','inv'), ['fold'], ['fold','call','raise'])
    s['fold_to_3bet'], s['n_vs_3bet'] = frac(key('pre','vs_3bet','inv'), ['fold'], ['fold','call','raise'])
    s['fourbet'], _ = frac(key('pre','vs_3bet','inv'), ['raise'], ['fold','call','raise'])
    s['fold_vs_3bet_cold'], _ = frac(key('pre','vs_3bet','cold'), ['fold'], ['fold','call','raise'])
    for band in ('le2.5','le3.5','le5','gt5'):
        s[f'fold_vs_raise_{band}'], _ = frac(key('pre_size','vs_raise','cold',band), ['fold'], ['fold','call','raise'], 15)
    for st in ('flop','turn','river'):
        s[f'cbet_{st}'], _ = frac(key('post','cbet',st), ['bet'], ['bet','check'])
        s[f'stab_{st}'], _ = frac(key('post','stab',st), ['bet'], ['bet','check'])
        s[f'fold_vs_bet_{st}'], _ = frac(key('post','vs_bet',st), ['fold'], ['fold','call','raise'])
        s[f'raise_vs_bet_{st}'], _ = frac(key('post','vs_bet',st), ['raise'], ['fold','call','raise'])
    return s

TYPES = [
    # name, predicate on (vpip, pfr)
    ('Nit / OMC',            lambda v, p: v < 14),
    ('TAG reg',              lambda v, p: 14 <= v < 24 and p >= 0.6 * v),
    ('Tight-passive',        lambda v, p: 14 <= v < 24 and p < 0.6 * v),
    ('LAG reg',              lambda v, p: 24 <= v < 34 and p >= 0.65 * v),
    ('Loose-passive (semi)', lambda v, p: 24 <= v < 34 and p < 0.65 * v),
    ('Loose-aggressive fish',lambda v, p: 34 <= v < 48 and p >= 0.55 * v),
    ('Loose-passive fish',   lambda v, p: 34 <= v < 48 and p < 0.55 * v),
    ('Whale (VPIP 48+)',     lambda v, p: v >= 48 and p < 0.5 * v),
    ('Maniac (VPIP 48+, aggressive)', lambda v, p: v >= 48 and p >= 0.5 * v),
]

def classify(v, p):
    for name, pred in TYPES:
        if pred(v, p): return name
    return 'other'

FIELDS = ['vpip','pfr','limp','open_raise','open_limp','limp_behind','iso_raise','threebet',
          'fold_vs_raise_cold','fold_vs_raise_limped','limp_raise','squeeze','fold_vs_squeeze',
          'fold_to_3bet','fourbet','fold_vs_3bet_cold',
          'fold_vs_raise_le2.5','fold_vs_raise_le3.5','fold_vs_raise_le5','fold_vs_raise_gt5',
          'cbet_flop','cbet_turn','cbet_river','stab_flop','stab_turn','stab_river',
          'fold_vs_bet_flop','fold_vs_bet_turn','fold_vs_bet_river',
          'raise_vs_bet_flop','raise_vs_bet_turn','raise_vs_bet_river']

def type_tables(players, min_hands, size):
    groups = collections.defaultdict(list)
    for pid, p in players.items():
        meta = p.get(key('meta'), {})
        # a player's table size = where most of its hands were
        if size and meta.get(size, 0) < 0.6 * max(sum(meta.values()), 1):
            continue
        s = player_stats(p)
        if s['hands'] < min_hands: continue
        groups[classify(s['vpip'], s['pfr'])].append(s)
    rows = {}
    for name, members in groups.items():
        agg = {'players': len(members), 'hands': sum(m['hands'] for m in members)}
        for f in FIELDS:
            vals = [(m[f], m['hands']) for m in members if m.get(f) is not None and not (isinstance(m[f], float) and math.isnan(m[f]))]
            if not vals: agg[f] = None; continue
            w = sum(h for _, h in vals)
            agg[f] = sum(v * h for v, h in vals) / w
        rows[name] = agg
    return rows

def md_types(rows):
    order = [t[0] for t in TYPES] + ['other']
    cols = [('players','n'),('hands','hands'),('vpip','VPIP'),('pfr','PFR'),('open_limp','open-limp'),('limp_behind','limp-behind'),('iso_raise','iso'),
            ('threebet','3-bet'),('fold_vs_raise_cold','fold v raise (cold)'),('fold_vs_raise_limped','fold v raise (limped)'),('limp_raise','limp-raise'),
            ('squeeze','squeeze'),('fold_vs_squeeze','fold v squeeze'),('fold_to_3bet','fold to 3-bet'),('fourbet','4-bet'),('fold_vs_3bet_cold','fold v 3-bet cold'),
            ('fold_vs_raise_le2.5','fold v ≤2.5x'),('fold_vs_raise_le3.5','fold v ≤3.5x'),('fold_vs_raise_gt5','fold v >5x'),
            ('cbet_flop','c-bet F'),('cbet_turn','barrel T'),('cbet_river','barrel R'),('fold_vs_bet_flop','fold v bet F'),('fold_vs_bet_turn','T'),('fold_vs_bet_river','R'),
            ('raise_vs_bet_flop','raise v bet F'),('stab_flop','stab F')]
    out = ['| type | ' + ' | '.join(c[1] for c in cols) + ' |', '|---|' + '---|' * len(cols)]
    for name in order:
        if name not in rows: continue
        r = rows[name]
        cells = []
        for k, _ in cols:
            v = r.get(k)
            cells.append('–' if v is None else (f"{v:,}" if k in ('players','hands') else f"{v:.0f}"))
        out.append(f"| {name} | " + ' | '.join(cells) + ' |')
    return '\n'.join(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('stats')
    ap.add_argument('--min-hands', type=int, default=300)
    ap.add_argument('--out', default='types.json')
    args = ap.parse_args()
    data = json.load(open(args.stats))
    pool = data['pool']; players = data['players']
    print(f"hands: {data['hands']:,} · dealt by size: {data['dealt_by_size']} · players with ≥100 hands: {len(players):,}\n")
    for size in ('fr', '6m'):
        if key('hand', size) in pool:
            print(pool_report(pool, size)); print()
    types = {}
    for size in ('fr', '6m'):
        rows = type_tables(players, args.min_hands, size)
        if not rows: continue
        print(f"### Player types — {'full ring' if size=='fr' else '6-max'} (players with ≥{args.min_hands} hands, weighted by hands)\n")
        print(md_types(rows)); print()
        types[size] = rows
    json.dump(types, open(args.out, 'w'), indent=1)
    print(f"wrote {args.out}", file=sys.stderr)

if __name__ == '__main__':
    main()
