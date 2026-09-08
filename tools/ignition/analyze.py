"""Validate anonymous Ignition histories; exclude hero from all population counts."""
import collections, hashlib, json, re, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'coinpoker'))
import analyze as cp

# When imported as `analyze` from tests, use an unambiguous module spec.
if not hasattr(cp,'replay'):
    import importlib.util
    spec=importlib.util.spec_from_file_location('coin_replay',Path(__file__).resolve().parents[1]/'coinpoker'/'analyze.py')
    cp=importlib.util.module_from_spec(spec);spec.loader.exec_module(cp)

PAIR=re.compile(r'\[([2-9TJQKA][cdhs]) ([2-9TJQKA][cdhs])\]')
def norm(s):return ' '.join(s.split())
def hand_index(cards):
    ranks='23456789TJQKA';a,b=cards
    lo,hi=sorted([ranks.index(a[0]),ranks.index(b[0])])
    return hi*13+lo if a[1]==b[1] else lo*13+hi

def convert(block):
    head=re.match(r'Ignition Hand #(\d+).* - (\d{4}-\d{2}-\d{2})',block)
    if not head or '*** SUMMARY ***' not in block or '*** HOLE CARDS ***' not in block: raise cp.Invalid('header_or_incomplete')
    pre,rest=block.split('*** HOLE CARDS ***',1)
    cards={}
    for line in rest.splitlines():
        if ': Card dealt to a spot [' in line:
            p=norm(line.split(':',1)[0]);m=PAIR.search(line)
            if not m or p in cards: raise cp.Invalid('invalid_dealt_cards')
            cards[p]=m.groups()
    allcards=[c for pair in cards.values() for c in pair]
    if len(allcards)!=len(set(allcards)): raise cp.Invalid('card_collision')
    board=set()
    for line in rest.splitlines():
        if re.match(r'^\*\*\* (?:FLOP|TURN|RIVER) \*\*\*|^Board ',line):
            board.update(re.findall(r'[2-9TJQKA][cdhs]',line))
    if board&set(allcards):raise cp.Invalid('board_hole_collision')
    seats=[(int(m[1]),norm(m[2]),m[3]) for m in map(cp.SEAT.match,pre.splitlines()) if m and norm(m[2]) in cards]
    names=[p for _,p,_ in seats]
    if not 3<=len(names)<=6:raise cp.Invalid('occupancy_outside_3_6')
    if set(names)!=set(cards):raise cp.Invalid('dealt_seat_mismatch')
    if ': Posts chip ' in pre:raise cp.Invalid('extra_post')
    sb=bb=None
    for line in pre.splitlines():
        m=re.match(r'^(.+?)\s*:\s*(Small Blind|Big blind) \$([\d.]+)',line,re.I)
        if m:
            if m[2].lower()=='small blind':sb=(norm(m[1]),m[3])
            else:bb=(norm(m[1]),m[3])
    if sb is None or bb is None or sb[0] not in names or bb[0] not in names: raise cp.Invalid('missing_blinds')
    btn=seats[(names.index(sb[0])-1)%len(seats)][0]
    explicit=re.search(r'Set dealer \[(\d+)\]',pre)
    if explicit and int(explicit[1])!=btn:raise cp.Invalid('dealer_mismatch')
    out=[f"PokerStars Hand #{head[1]}: Hold'em No Limit (${sb[1]}/${bb[1]} USD) - {head[2].replace('-','/')} 00:00:00 ET",
         f"Table 'Ignition' 6-max Seat #{btn} is the button"]
    out.extend(f'Seat {i}: {p} (${stack} in chips)' for i,p,stack in seats)
    out.extend([f'{sb[0]}: posts small blind ${sb[1]}',f'{bb[0]}: posts big blind ${bb[1]}','*** HOLE CARDS ***'])
    cur=cp.cents(bb[1]);contrib={p:0 for p in names};contrib[sb[0]]=cp.cents(sb[1]);contrib[bb[0]]=cur
    paid=contrib.copy();stacks={p:cp.cents(stack) for _,p,stack in seats}
    def money(c):return f'{c//100}.{c%100:02d}'
    for line in rest.splitlines():
        if line.startswith('*** SUMMARY ***'):break
        if line.startswith('*** '):
            out.append(line);cur=0;contrib={p:0 for p in names};continue
        ret=re.match(r'^(.+?)\s*:\s*Return uncalled portion of bet \$([\d.]+)',line)
        if ret:
            p=norm(ret[1]);amount=cp.cents(ret[2]);out.append(f'Uncalled bet (${ret[2]}) returned to {p}')
            contrib[p]-=amount;paid[p]-=amount;continue
        m=re.match(r'^(.+?)\s*:\s*(Folds|Checks|Calls|Bets|Raises|All-in(?:\(raise\))?)(?: \$([\d.]+))?(?: to \$([\d.]+))?(.*)$',line)
        if not m:continue
        p,act,amt,to,tail=m.groups();p=norm(p)
        if p not in contrib:raise cp.Invalid('unseated_actor')
        if act.startswith('All-in'):
            amount=cp.cents(amt)
            if amount!=stacks[p]-paid[p]:raise cp.Invalid('allin_stack_mismatch')
            target=contrib[p]+amount
            if to is not None and cp.cents(to)!=target:raise cp.Invalid('allin_to_mismatch')
            act='Bets' if cur==0 else 'Raises' if target>cur else 'Calls'
            if act=='Raises':to=money(target)
            tail='all-in'
        suffix=' and is all-in' if 'all-in' in tail.lower() or 'all in' in tail.lower() else ''
        if act=='Raises':
            if to is None:raise cp.Invalid('raise_missing_to')
            target=cp.cents(to)
            # Ignition's first amount is chips added, unlike PokerStars' increment.
            if cp.cents(amt)!=target-contrib[p]:raise cp.Invalid('raise_delta')
            out.append(f'{p}: raises ${money(target-cur)} to ${to}{suffix}')
            paid[p]+=target-contrib[p]
            cur=target;contrib[p]=target
        elif act in ['Calls','Bets']:
            out.append(f'{p}: {act.lower()} ${amt}{suffix}');contrib[p]+=cp.cents(amt)
            paid[p]+=cp.cents(amt)
            if act=='Bets':cur=contrib[p]
        else:out.append(f'{p}: {act.lower()}')
    total=re.search(r'Total Pot\(\$([\d.]+)\)',block)
    if not total:raise cp.Invalid('missing_total')
    out.extend(['*** SUMMARY ***',f'Total pot ${total[1]} | Rake $0'])
    return '\n'.join(out),cards

def run(source,out):
    sessions=[];seen={};audit=collections.Counter()
    paths=[p for p in sorted(Path(source).rglob('*.txt')) if 'ZONE' not in p.name and ' - $0.05-$0.10 - ' in p.name]
    for path in paths:
        counts=collections.Counter();cells=collections.Counter();policy_cells=collections.Counter();dates=[]
        for block in re.split(r'(?=^Ignition Hand #)',path.read_text(encoding='utf-8-sig',errors='replace'),flags=re.M):
            m=re.match(r'Ignition Hand #(\d+)',block)
            if not m:continue
            audit['raw']+=1;digest=hashlib.sha256(block.strip().encode()).hexdigest()
            if m[1] in seen:
                audit['duplicates']+=1
                if seen[m[1]]!=digest:audit['duplicate_variants']+=1
                continue
            seen[m[1]]=digest
            try:
                canonical,cards=convert(block)
                meta,cs=cp.replay(canonical,10,variant='ignition')
            except (cp.Invalid,ValueError,KeyError,TypeError) as e:
                audit['excluded/'+str(e)]+=1;continue
            audit['accepted']+=1;dates.append(meta['date'])
            for player,c in cs.items():
                if '[ME]' in player:continue
                counts.update(c)
                for k,v in c.items():
                    if k.startswith('context/') and '/open|' in k:
                        prefix,a=k.split('|');_,n,pos,_=prefix.split('/')
                        cells[f'{n}/{pos}/{hand_index(cards[player])}|{a}']+=v
                    if k.startswith('policy/'):
                        prefix,a=k.split('|');_,n,pos,bucket=prefix.split('/')
                        policy_cells[f'{bucket}/{n}/{pos}/{hand_index(cards[player])}|{a}']+=v
        if dates:sessions.append(dict(id=hashlib.sha256(path.name.encode()).hexdigest()[:16],first=min(dates),last=max(dates),counts=counts,cells=cells,policy_cells=policy_cells))
    result=dict(schema=2,site='Ignition',stake='NL10 regular',audit=audit,sessions=sessions)
    Path(out).mkdir(parents=True,exist_ok=True)
    (Path(out)/'analysis.json').write_text(json.dumps(result),encoding='utf-8')
    print(json.dumps(dict(audit=audit,sessions=len(sessions)),indent=2))

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    run(a.source,a.out)
