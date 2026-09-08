"""Validated, opportunity-based HHDealer CoinPoker text replay (not PHH).

Run: python tools/coinpoker/analyze.py --source "T:/Dev/Poker Data/hhdealer/CoinPoker" --out output/coinpoker
Raw histories and player identifiers stay local. Only aggregate models are published.
"""
from __future__ import annotations
import argparse, collections, concurrent.futures, datetime, hashlib, json, re, time
from pathlib import Path

HEADER = re.compile(r'^PokerStars Hand #(\d+): Hold\x27em No Limit \(\$([\d.]+)/\$([\d.]+) USD\) - (\d{4}/\d{2}/\d{2})')
SPLIT = re.compile(r'(?=^PokerStars Hand #)', re.M)
SEAT = re.compile(r'^Seat (\d+): (.+) \(\$([\d.]+) in chips\)(.*)$')
ACTION = re.compile(r'^(.+?): (folds|checks|calls|bets|raises)(?: \$([\d.]+))?(?: to \$([\d.]+))?(.*)$')
POST = re.compile(r'^(.+?): posts (small blind|big blind|the ante) \$([\d.]+)(.*)$')
RETURN = re.compile(r'^Uncalled bet \(\$([\d.]+)\) returned to (.+)$')
TOTAL = re.compile(r'^Total pot \$([\d.]+)')
STAKE_BB = {'NL10':10, 'NL25':25, 'NL50':50, 'NL100':100}
SCHEMA = 2

def read_histories(path):
    # HHDealer occasionally repeats the site prefix. Normalize before splitting;
    # otherwise many valid hands become one rejected multi-board block.
    text = path.read_text(encoding='utf-8-sig', errors='replace')
    return re.sub(r'^(?:PokerStars ){2,}Hand #', 'PokerStars Hand #', text, flags=re.M)

class Invalid(ValueError): pass

def cents(s):
    if s is None: raise Invalid('missing_amount')
    a, _, b = s.partition('.')
    if len(b)>2 and int(b[2:]): raise Invalid('fractional_cent')
    return int(a)*100 + int((b+'00')[:2])

def band(x):
    return '2.5' if x<=2.5+1e-8 else '3.5' if x<=3.5+1e-8 else '5' if x<=5+1e-8 else '999'

def replay(block, expected_bb=None, *, variant='coinpoker'):
    """Return metadata and per-seat flat counters. Commit only after full validation.

    Default: standard 7-max ante games with 5-7 active players. The Ignition
    adapter explicitly selects 6-max/no-ante with 3-6 active players.
    Other formats are counted as exclusions, never silently mixed into a pool.
    """
    lines = block.strip().splitlines()
    m = HEADER.match(lines[0]) if lines else None
    if not m: raise Invalid('header')
    hid, sb_text, bb_text, date = m.groups()
    bb = cents(bb_text)
    if expected_bb and bb != expected_bb: raise Invalid('stake_mismatch')
    tm = re.search(r"^Table '(.+)' (\d+)-max Seat #(\d+) is the button$", block, re.M)
    if not tm: raise Invalid('table')
    if int(tm[2]) != (7 if variant=='coinpoker' else 6): raise Invalid('not_7max' if variant=='coinpoker' else 'not_6max')
    if any(block.count('*** '+s+' ***')>1 for s in ['FLOP','TURN','RIVER']) or 'FIRST FLOP' in block or 'SECOND FLOP' in block: raise Invalid('multiple_boards')
    if '*** SUMMARY ***' not in block: raise Invalid('incomplete')
    if '*** HOLE CARDS ***' not in block: raise Invalid('no_hole_marker')
    preamble, rest = block.split('*** HOLE CARDS ***', 1)
    records = [SEAT.match(l) for l in preamble.splitlines()]
    records = [s for s in records if s]
    records = [s for s in records if not any(x in s[4].lower() for x in ['sitting out','out of hand'])]
    lo,hi=(5,7) if variant=='coinpoker' else (3,6)
    if not lo <= len(records) <= hi: raise Invalid(f'occupancy_outside_{lo}_{hi}')
    names = [s[2] for s in records]
    if len(set(names)) != len(names): raise Invalid('duplicate_seat_name')
    seat_ids = [int(s[1]) for s in records]
    stacks = {s[2]:cents(s[3]) for s in records}
    contrib = {p:0 for p in names}
    paid = {p:0 for p in names}
    antes = {}
    sbp = bbp = None
    for line in preamble.splitlines():
        p = POST.match(line)
        if ': posts ' in line and not p: raise Invalid('unusual_post')
        if not p: continue
        name, kind, amount, tail = p.groups()
        if name not in stacks: raise Invalid('unknown_poster')
        amount = cents(amount)
        paid[name] += amount
        if kind == 'the ante':
            if name in antes: raise Invalid('duplicate_ante')
            antes[name] = amount
        else:
            contrib[name] += amount
            if kind == 'small blind':
                if sbp is not None or amount != cents(sb_text): raise Invalid('unusual_blinds')
                sbp = name
            else:
                if bbp is not None or amount != bb: raise Invalid('unusual_blinds')
                bbp = name
    if sbp is None or bbp is None or sbp == bbp: raise Invalid('unusual_blinds')
    if variant=='coinpoker':
        if len(antes)!=len(names) or len(set(antes.values()))!=1 or min(antes.values())<=0: raise Invalid('nonuniform_or_no_ante')
    elif antes: raise Invalid('unexpected_ante')
    if any(paid[p]>=stacks[p] for p in names): raise Invalid('allin_post')
    btn_id = int(tm[3])
    if btn_id not in seat_ids: raise Invalid('dead_button')
    btn_index = seat_ids.index(btn_id)
    if names[(btn_index+1)%len(names)] != sbp or names[(btn_index+2)%len(names)] != bbp: raise Invalid('button_blind_order')
    positions = {}
    for i,p in enumerate(names):
        d = (btn_index-i)%len(names)
        positions[p] = 'SB' if p==sbp else 'BB' if p==bbp else 'BTN' if d==0 else {1:'CO',2:'HJ',3:'LJ',4:'UTG'}[d]
    counts = {p:collections.Counter() for p in names}
    def add(p,key,out): counts[p][key+'|'+out] += 1
    voluntary, raisers, limped, folded = set(), set(), set(), set()
    active = set(names)
    cur, raises, limpers, callers = bb, 0, 0, 0
    min_raise = bb
    street = 'pre'
    initiative = None
    previous_aggressor = None
    actor_seen = set()
    pending = set(active)
    # Action order validation catches missing/converted actions before they enter stats.
    next_index = (names.index(bbp)+1)%len(names)
    pot = sum(paid.values())
    for line in rest.splitlines():
        if line.startswith('*** SUMMARY ***'): break
        marker = next((st for st in ('FLOP','TURN','RIVER') if line.startswith('*** '+st+' ***')),None)
        if marker:
            if marker != {'pre':'FLOP','flop':'TURN','turn':'RIVER'}.get(street): raise Invalid('street_sequence')
            if pending: raise Invalid('missing_action_before_street')
            street = marker.lower()
            if previous_aggressor is not None: initiative = previous_aggressor
            previous_aggressor = None
            contrib = {p:0 for p in names}
            cur = 0
            min_raise = bb
            pending = {p for p in active if paid[p]<stacks[p]}
            if len(pending)<2: pending.clear()
            next_index = (btn_index+1)%len(names)
            continue
        ret = RETURN.match(line)
        if ret:
            amount,p = cents(ret[1]),ret[2]
            if p not in stacks or amount>contrib[p]: raise Invalid('invalid_return')
            contrib[p]-=amount; paid[p]-=amount; pot-=amount
            continue
        a = ACTION.match(line)
        if not a: continue
        p, act, amount, to, tail = a.groups()
        if p not in active or paid[p]>=stacks[p]: raise Invalid('inactive_actor')
        if p not in pending: raise Invalid('unexpected_action')
        for _ in names:
            expected = names[next_index]
            if expected in pending: break
            next_index = (next_index+1)%len(names)
        if p != expected: raise Invalid('action_order')
        next_index = (next_index+1)%len(names)
        actor_seen.add(p)
        facing = cur-contrib[p]
        if act == 'checks' and facing>0: raise Invalid('check_facing_bet')
        out = {'folds':'fold','checks':'check','calls':'call','bets':'bet','raises':'raise'}[act]
        implicit_allin = act=='raises' and to is None
        if implicit_allin:
            if 'all-in' not in tail or cents(amount)!=stacks[p]-paid[p]: raise Invalid('ambiguous_raise')
            target_cents=contrib[p]+cents(amount)
            to=f'{target_cents//100}.{target_cents%100:02d}'
        if street == 'pre':
            if raises == 0:
                sit = 'free' if facing==0 else ('limps' if limpers else 'open')
            elif raises==1:
                sit = ('limped_raise' if p in limped else 'repeat_raise') if p in voluntary else ('squeeze' if callers else 'raise')
            elif raises==2:
                sit = '3bet_raiser' if p in raisers else '3bet_other'
            else: sit = '4bet_plus'
            add(p,'pre/'+sit,out)
            add(p,'pos/'+positions[p]+'/'+sit,out)
            if sit in ('open','limps'):
                add(p,f'context/{len(names)}/{positions[p]}/{sit}',out)
            if variant == 'ignition':
                # Match the engine's decision buckets, including whether the
                # actor already entered. Never count forced posts as choices.
                bucket = ('limps' if sit=='free' else sit) if raises==0 else (
                    ('limp_defense' if p in voluntary else ('squeeze' if callers else 'raise')) if raises==1
                    else ('reraise' if p in voluntary else 'cold_reraise'))
                action = 'call' if out=='check' else out
                add(p,f'policy/{len(names)}/{positions[p]}/{bucket}',action)
                if bucket=='raise':
                    add(p,f'policy/{len(names)}/{positions[p]}/raise_{band(cur/bb)}',action)
            if sit in ('raise','limped_raise'): add(p,'size/'+sit+'/'+band(cur/bb),out)
            if act=='calls':
                if raises==0: limped.add(p); limpers+=1
                else: callers+=1
                voluntary.add(p)
            elif act in ('raises','bets'):
                if act=='bets': raise Invalid('preflop_bet')
                if raises==0: add(p,'open_size',band(cents(to)/bb))
                voluntary.add(p); raisers.add(p)
                raises+=1; callers=0
        else:
            if facing>0:
                add(p,'post/'+street+'/facing',out)
                add(p,'post/all/facing',out)
                frac = facing/max(1,pot-facing)
                add(p,'post_size/'+street+'/'+('small' if frac<=.5 else 'medium' if frac<=1 else 'overbet'),out)
            else:
                kind = 'initiative' if initiative==p else 'no_initiative'
                add(p,'post/'+street+'/'+kind,out)
                add(p,'post/all/'+kind,out)
                if act=='bets': add(p,'bet_size','small' if cents(amount)/max(pot,1)<=.6 else 'large')
        pending.discard(p)
        if act=='folds':
            folded.add(p); active.remove(p)
        elif act=='calls':
            delta = cents(amount)
            if delta != min(facing,stacks[p]-paid[p]) or delta<=0: raise Invalid('call_amount')
            contrib[p]+=delta; paid[p]+=delta; pot+=delta
        elif act in ('bets','raises'):
            target = cents(to if act=='raises' else amount)
            if target<=cur or (act=='bets' and cur): raise Invalid('raise_amount')
            # Short raises change reopening rights; exclude them from this first
            # population fit rather than pretending they are ordinary 3-bets.
            if target-cur < min_raise: raise Invalid('short_raise')
            min_raise = target-cur
            if act=='raises' and not implicit_allin and cents(amount)!=target-cur: raise Invalid('raise_increment')
            delta = target-contrib[p]
            if delta<=0 or delta>stacks[p]-paid[p]: raise Invalid('stack_overrun')
            contrib[p]=target; paid[p]+=delta; pot+=delta; cur=target
            previous_aggressor = p
            pending = {q for q in active if q!=p and paid[q]<stacks[q]}
        if len(active)==1: pending.clear()
        if len([q for q in active if paid[q]<stacks[q]])==1:
            # A lone non-all-in player still must answer an outstanding bet.
            pending = {q for q in pending if contrib[q]<cur}
    if pending: raise Invalid('incomplete_betting')
    total = next((TOTAL.match(l) for l in lines if TOTAL.match(l)),None)
    if total is None or cents(total[1]) != pot: raise Invalid('pot_mismatch')
    if set(names)-actor_seen-active: raise Invalid('missing_preflop_actor')
    for p in names:
        add(p,'vpip','yes' if p in voluntary else 'no')
        add(p,'pfr','yes' if p in raisers else 'no')
        add(p,'position',positions[p])
        add(p,'occupancy',str(len(names)))
        add(p,'stack','short' if stacks[p]/bb<50 else 'standard' if stacks[p]/bb<=150 else 'deep')
    return {'id':hid,'date':date.replace('/','-'),'ante_bb':next(iter(antes.values()),0)/bb,'n':len(names)}, counts

def analyze_stake(source, out, stake, holdout_days=14, limit=0):
    paths = sorted((Path(source)/stake).rglob('*.txt'))
    # Latest date comes from actual headers, not filenames or modification times.
    last = None
    for path in paths:
        text = read_histories(path)
        dates = re.findall(r'^PokerStars Hand #[^\n]+ - (\d{4}/\d{2}/\d{2})',text,re.M)
        if dates: last=max(last or dates[0],max(dates))
    cutoff = (datetime.date.fromisoformat(last.replace('/','-'))-datetime.timedelta(days=holdout_days-1)).isoformat()
    seen = {}
    audit = collections.Counter()
    dates, antes, occupancy = collections.Counter(), collections.Counter(), collections.Counter()
    examples = {}
    pseudonyms = {}
    players = collections.defaultdict(lambda: [collections.Counter(),collections.Counter()])
    pool = [collections.Counter(),collections.Counter()]
    started = time.time()
    for fi,path in enumerate(paths):
        text=read_histories(path)
        for block in SPLIT.split(text):
            if not block.strip(): continue
            m=HEADER.match(block)
            if not m: audit['bad_header']+=1; continue
            audit['raw']+=1
            hid=m[1]
            # Duplicate exports can shift the recorded clock time. Timestamp
            # variations are not a second hand; compare the substantive record.
            canonical=re.sub(r' - \d{4}/\d{2}/\d{2}[^\n]*','',block.strip().replace('\r',''),count=1)
            # Some copies disagree about showdown winners; neither winners nor
            # revealed cards are used in these action-frequency models.
            canonical=canonical.split('*** SHOW DOWN ***')[0].split('*** SUMMARY ***')[0].strip()
            total_line=re.search(r'^Total pot [^\n]+',block,re.M)
            canonical+='\n'+(total_line[0] if total_line else '')
            digest=hashlib.blake2b(canonical.encode(),digest_size=12).digest()
            if hid in seen:
                audit['duplicate']+=1
                if digest!=seen[hid]:
                    audit['duplicate_variant']+=1
                    examples.setdefault('duplicate_variant',dict(file=path.name,hand=hid))
                continue
            seen[hid]=digest
            try: meta, counters=replay(block,STAKE_BB[stake])
            except (Invalid, ValueError, KeyError, TypeError) as e:
                reason=str(e) if isinstance(e,Invalid) else 'parse_'+type(e).__name__
                audit['excluded/'+reason]+=1
                examples.setdefault(reason,dict(file=path.name,hand=hid))
                continue
            split=int(meta['date']>=cutoff)
            for name,c in counters.items():
                # Stable pseudonyms allow temporal validation without publishing names.
                if name not in pseudonyms: pseudonyms[name]=hashlib.sha256(('CoinPoker:'+name).encode()).hexdigest()[:24]
                pid=pseudonyms[name]
                players[pid][split].update(c)
                pool[split].update(c)
            audit['accepted']+=1
            audit['holdout' if split else 'train']+=1
            dates[meta['date']]+=1
            antes[str(meta['ante_bb'])]+=1
            occupancy[str(meta['n'])]+=1
            if limit and audit['accepted']>=limit: break
        if fi%100==0: print(f'{stake}: {fi}/{len(paths)} files, {audit["accepted"]:,} accepted, {time.time()-started:.0f}s',flush=True)
        if limit and audit['accepted']>=limit: break
    result=dict(schema=SCHEMA,stake=stake,cutoff=cutoff,audit=dict(audit),dates=dict(dates),antes=dict(antes),occupancy=dict(occupancy),excluded_examples=examples,pool=pool,players=dict(players))
    dest=Path(out); dest.mkdir(parents=True,exist_ok=True)
    (dest/f'{stake}.json').write_text(json.dumps(result,separators=(',',':')))
    print(f'{stake} complete: {dict(audit)}',flush=True)
    return dict(stake=stake,audit=dict(audit))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True); ap.add_argument('--out',required=True)
    ap.add_argument('--stakes',nargs='+',default=list(STAKE_BB))
    ap.add_argument('--workers',type=int,default=4); ap.add_argument('--limit',type=int,default=0)
    args=ap.parse_args()
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as ex:
        jobs=[ex.submit(analyze_stake,args.source,args.out,s,14,args.limit) for s in args.stakes]
        for job in concurrent.futures.as_completed(jobs): print(json.dumps(job.result()),flush=True)

if __name__=='__main__': main()
