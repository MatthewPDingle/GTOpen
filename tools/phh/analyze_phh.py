#!/usr/bin/env python3
"""Population / player-type statistics from the PHH dataset (Kim, U of Toronto:
doi 10.5281/zenodo.13997158, CC-BY 4.0) — the HandHQ July-2009 real-money
no-limit hold'em cash hands.

Per hand we replay the action list with a small state machine and, for every
decision a player faced, record the SITUATION (the GTOpen profile buckets:
unopened / vs limps / vs raise / squeeze / vs 3-bet+, plus whether the player
had already voluntarily invested — "cold" vs "invested"), the raise size faced
(bb, for size bands) and the ACTION (fold / call / raise). Postflop we record
c-bet opportunities (initiative, no bet faced), bet-without-initiative
opportunities, and fold / call / raise when facing a bet, per street.

Counters are kept per player id (the dataset anonymizes names but keeps them
consistent), so players can be clustered into types by VPIP/PFR and the
conditional stats pooled per type.

Usage: python analyze_phh.py <zip-or-dir> [--limit N] [--out stats.json]
"""
import sys, os, re, json, io, zipfile, argparse, collections, multiprocessing as mp

STREETS = ('flop', 'turn', 'river')

# ---------------------------------------------------------------- parsing --

def parse_hand_block(lines):
    """Parse the key = value lines of one hand into a dict (TOML subset)."""
    h = {}
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        k, _, v = ln.partition('=')
        k = k.strip(); v = v.strip()
        if v.startswith('['):
            # array of strings or numbers (single line in this dataset)
            inner = v[1:v.rfind(']')]
            if '"' in inner or "'" in inner:
                items = re.findall(r'"([^"]*)"|\'([^\']*)\'', inner)
                h[k] = [a if a else b for a, b in items]
            else:
                h[k] = [float(x) for x in inner.split(',') if x.strip()]
        elif v.startswith('"') or v.startswith("'"):
            h[k] = v[1:-1]
        elif v in ('true', 'false'):
            h[k] = v == 'true'
        else:
            try:
                h[k] = float(v)
            except ValueError:
                h[k] = v
    return h


def iter_hands_from_text(text):
    """Yield hand dicts from a .phhs (many [tables]) or .phh (one hand) text."""
    block = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith('[') and s.endswith(']') and '=' not in s:
            if block:
                yield parse_hand_block(block)
            block = []
        else:
            block.append(ln)
    if block:
        yield parse_hand_block(block)

# ---------------------------------------------------------------- stats ----

class Acc:
    """Nested counters: key -> Counter of outcomes."""
    def __init__(self):
        self.c = collections.defaultdict(collections.Counter)
    def add(self, key, outcome, n=1):
        self.c[key][outcome] += n
    def merge(self, other):
        for k, cnt in other.c.items():
            self.c[k].update(cnt)


def size_band(to_bb):
    """Raise-TO size buckets in bb (the game's typical 2.5–3x opens vs big)."""
    if to_bb <= 2.6: return 'le2.5'
    if to_bb <= 3.6: return 'le3.5'
    if to_bb <= 5.0: return 'le5'
    return 'gt5'


def replay(h, per_player, pool, dealt_hist):
    """Replay one hand; update per-player and pool accumulators."""
    variant = h.get('variant')
    if variant != 'NT':
        return False
    stacks = h.get('starting_stacks') or []
    blinds = h.get('blinds_or_straddles') or []
    actions = h.get('actions') or []
    n = len(stacks)
    if n < 2 or len(blinds) != n or not actions:
        return False
    # the big blind is min_bet; require the normal two posts (a hand where the
    # BB sat out posts only the SB, and some sites' records carry odd posts)
    bb = float(h.get('min_bet') or 0)
    posted = [b for b in blinds if b > 0]
    if bb <= 0 or len(posted) != 2 or abs(max(posted) - bb) > 1e-9:
        return False
    seat_count = int(h.get('seat_count') or 0)
    antes = h.get('antes') or [0] * n
    names = h.get('players') or [None] * n
    if len(names) != n:
        names = [None] * n
    # seat i (0-based) = p(i+1). Blinds list marks SB/BB seats; with n>=3 the
    # button is the seat before the SB (last seat when SB is p1).
    sb_i = next((i for i, b in enumerate(blinds) if b > 0), 0)
    bb_i = next((i for i in range(sb_i + 1, n) if blinds[i] > 0), sb_i)
    btn_i = (sb_i - 1) % n if n >= 3 else sb_i
    def posname(i):
        if i == sb_i: return 'SB'
        if i == bb_i: return 'BB'
        if i == btn_i: return 'BTN'
        # seats after BB up to BTN: EP..CO by distance to the button
        d = (btn_i - i) % n  # 1 = CO, 2 = HJ ...
        return {1: 'CO', 2: 'HJ', 3: 'MP', 4: 'MP', 5: 'EP'}.get(d, 'EP')
    # table type from the table's seat count (dealt-in count varies hand to hand)
    sc = seat_count or n
    tsize = 'fr' if sc >= 7 else ('6m' if sc >= 4 else 'hu')

    # preflop state
    contrib = [float(b) for b in blinds]           # street contribution
    invested = [b > 0 for b in blinds]              # voluntary money in? (blinds don't count)
    voluntary = [False] * n
    raised_pf = [False] * n
    limped = [False] * n
    called_raise = [False] * n                      # called a raise (cold or after limp)
    folded = [False] * n
    allin = [False] * n
    cur_bet = float(bb)
    raises = 0                                      # number of raises so far (open = 1)
    limpers = 0
    callers = 0                                     # callers of the current raise level
    aggressor = None
    street = 'pre'
    st_bet = 0.0                                    # postflop: current bet on street
    st_aggr = None                                  # last bettor/raiser this street
    initiative = None                               # last aggressor (carries across streets)
    st_actors_bet = set()
    live = n
    pf_records = []                                 # (seat, situation, cold, size_band, action)
    # per-hand flags for VPIP/PFR (computed at end)
    for a in actions:
        parts = a.split()
        if parts[0] == 'd':
            if parts[1] == 'db':
                # new street
                if street == 'pre':
                    initiative = aggressor
                    street = 'flop'
                elif street == 'flop':
                    street = 'turn'
                elif street == 'turn':
                    street = 'river'
                st_bet = 0.0
                st_aggr = None
                contrib = [0.0] * n
            continue
        m = re.match(r'p(\d+)', parts[0])
        if not m:
            continue
        seat = int(m.group(1)) - 1
        if seat < 0 or seat >= n or folded[seat]:
            continue
        act = parts[1]
        if act == 'sm':
            continue
        if street == 'pre':
            facing = cur_bet - contrib[seat]
            # situation classification (GTOpen buckets)
            if raises == 0:
                sit = 'unopened' if limpers == 0 else 'vs_limps'
                if seat == bb_i and facing <= 1e-9:
                    sit = 'bb_free'   # BB option: check or raise, no fold possible
            elif raises == 1:
                sit = 'squeeze' if callers > 0 else 'vs_raise'
            else:
                sit = 'vs_3bet' if raises == 2 else 'vs_4bet_plus'
            cold = not voluntary[seat]
            band = size_band(cur_bet / bb) if raises >= 1 else None
            if act == 'f':
                out = 'fold'
                folded[seat] = True
                live -= 1
            elif act == 'cc':
                if facing <= 1e-9:
                    out = 'check'
                else:
                    out = 'call'
                    if raises == 0:
                        limped[seat] = True
                        limpers += 1
                    else:
                        called_raise[seat] = True
                        callers += 1
                    contrib[seat] = cur_bet
                    voluntary[seat] = True
            elif act == 'cbr':
                to = float(parts[2])
                out = 'raise'
                raised_pf[seat] = True
                voluntary[seat] = True
                contrib[seat] = to
                if to > cur_bet:
                    cur_bet = to
                raises += 1
                callers = 0
                aggressor = seat
                if to >= stacks[seat] - 1e-9:
                    allin[seat] = True
            else:
                continue
            pf_records.append((seat, sit, cold, band, out, posname(seat)))
        else:
            facing = st_bet - contrib[seat]
            has_init = (initiative == seat)
            if act == 'f':
                out = 'fold'; folded[seat] = True; live -= 1
            elif act == 'cc':
                out = 'check' if facing <= 1e-9 else 'call'
                if facing > 1e-9:
                    contrib[seat] = st_bet
            elif act == 'cbr':
                to = float(parts[2])
                out = 'bet' if st_bet <= 1e-9 else 'raise'
                contrib[seat] = to
                st_bet = max(st_bet, to)
                st_aggr = seat
                initiative = seat
            else:
                continue
            pid = names[seat]
            key_base = (street,)
            if facing <= 1e-9:
                # bet-or-check opportunity
                kind = 'cbet' if has_init else 'stab'
                o = 'bet' if out in ('bet', 'raise') else 'check'
                pool.add(('post', kind, street, tsize), o)
                if pid: per_player[pid].add(('post', kind, street), o)
            else:
                kind = 'vs_bet'
                pool.add(('post', kind, street, tsize), out)
                if pid: per_player[pid].add(('post', kind, street), out)

    # preflop records -> counters
    for (seat, sit, cold, band, out, pos) in pf_records:
        pid = names[seat]
        pool.add(('pre', sit, 'cold' if cold else 'inv', tsize), out)
        if band:
            pool.add(('pre_size', sit, 'cold' if cold else 'inv', band, tsize), out)
        pool.add(('pre_pos', sit, pos, tsize), out)
        if pid:
            per_player[pid].add(('pre', sit, 'cold' if cold else 'inv'), out)
            if band:
                per_player[pid].add(('pre_size', sit, 'cold' if cold else 'inv', band), out)
    # per-hand VPIP / PFR / limp per player (dealt-in hands)
    for i in range(n):
        pid = names[i]
        pool.add(('hand', tsize), 'dealt')
        pool.add(('hand', tsize), 'vpip' if voluntary[i] else 'novpip')
        if raised_pf[i]:
            pool.add(('hand', tsize), 'pfr')
        if limped[i]:
            pool.add(('hand', tsize), 'limp')
        if pid:
            per_player[pid].add(('hand',), 'dealt')
            if voluntary[i]: per_player[pid].add(('hand',), 'vpip')
            if raised_pf[i]: per_player[pid].add(('hand',), 'pfr')
            if limped[i]: per_player[pid].add(('hand',), 'limp')
            per_player[pid].add(('meta',), tsize)
    dealt_hist[tsize] += 1
    return True


def process_member(args):
    """Worker: parse one file (zip member or path) and return (pool, per_player, hands)."""
    src, member, limit = args
    pool = Acc()
    per_player = collections.defaultdict(Acc)
    dealt = collections.Counter()
    nh = 0
    try:
        if member is None:
            with open(src, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
        else:
            with zipfile.ZipFile(src) as z:
                text = z.read(member).decode('utf-8', errors='replace')
        for h in iter_hands_from_text(text):
            if replay(h, per_player, pool, dealt):
                nh += 1
                if limit and nh >= limit:
                    break
    except Exception as e:  # keep going on a bad file
        sys.stderr.write(f"{member or src}: {e}\n")
    # per_player Acc objects are picklable (defaultdict of Counter)
    return pool.c, {k: v.c for k, v in per_player.items()}, dealt, nh, member or src


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--filter', default='handhq', help='substring members must contain')
    ap.add_argument('--limit', type=int, default=0, help='hands per file cap (smoke tests)')
    ap.add_argument('--max-files', type=int, default=0)
    ap.add_argument('--out', default='phh_stats.json')
    ap.add_argument('--procs', type=int, default=max(1, mp.cpu_count() - 2))
    args = ap.parse_args()

    if os.path.isdir(args.src):
        jobs = []
        for root, _, files in os.walk(args.src):
            for fn in files:
                if fn.endswith(('.phh', '.phhs')) and any(x in os.path.join(root, fn) for x in args.filter.split(',')):
                    jobs.append((os.path.join(root, fn), None, args.limit))
    else:
        with zipfile.ZipFile(args.src) as z:
            pats = [x for x in args.filter.split(',') if x]
            members = [m for m in z.namelist() if m.endswith(('.phh', '.phhs')) and any(x in m for x in pats)]
        jobs = [(args.src, m, args.limit) for m in members]
    if args.max_files:
        jobs = jobs[:args.max_files]
    print(f"{len(jobs)} files", file=sys.stderr)

    pool = Acc()
    players = collections.defaultdict(Acc)
    dealt = collections.Counter()
    total = 0
    done = 0
    with mp.Pool(args.procs) as p:
        for pc, ppl, d, nh, name in p.imap_unordered(process_member, jobs, chunksize=1):
            for k, cnt in pc.items():
                pool.c[k].update(cnt)
            for pid, acc in ppl.items():
                for k, cnt in acc.items():
                    players[pid].c[k].update(cnt)
            dealt.update(d)
            total += nh
            done += 1
            if done % 20 == 0:
                print(f"  {done}/{len(jobs)} files, {total} hands", file=sys.stderr)
    print(f"{total} hands, {len(players)} players", file=sys.stderr)

    def ser(acc):
        return {'|'.join(map(str, k)): dict(v) for k, v in acc.c.items()}
    out = {
        'hands': total,
        'dealt_by_size': dict(dealt),
        'pool': ser(pool),
        'players': {pid: ser(acc) for pid, acc in players.items()
                    if acc.c.get(('hand',), {}).get('dealt', 0) >= 100},
    }
    with open(args.out, 'w') as f:
        json.dump(out, f)
    print(f"wrote {args.out}", file=sys.stderr)


if __name__ == '__main__':
    main()
