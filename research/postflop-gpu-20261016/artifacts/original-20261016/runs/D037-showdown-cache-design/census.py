"""Host-only combinatorial lookup census. No solver, compiler, GPU or timings."""
from pathlib import Path
import hashlib,itertools,json,statistics
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
RANKS='23456789TJQKA';SUITS='cdhs'
def card(s):return RANKS.index(s[0])*4+SUITS.index(s[1])
def cls(s):return max(RANKS.index(s[0]),RANKS.index(s[1])),min(RANKS.index(s[0]),RANKS.index(s[1])),s[2:] or None
def combos(h,l,m):
    if h==l:
        assert m is None
        return {(h*4+a,h*4+b) for a in range(4) for b in range(a)}
    return {tuple(sorted((h*4+a,l*4+b))) for a in range(4) for b in range(4)
            if m is None or (m=='s' and a==b) or (m=='o' and a!=b)}
def expand(token):
    if '-' in token:
        a,b=token.split('-');h,l,m=cls(a);hh,ll,mm=cls(b);assert m==mm
        if h==l and hh==ll:return set().union(*(combos(r,r,m) for r in range(min(h,hh),max(h,hh)+1)))
        if h==hh:return set().union(*(combos(h,r,m) for r in range(min(l,ll),max(l,ll)+1) if r!=h))
        assert h-l==hh-ll
        return set().union(*(combos(r,r-(h-l),m) for r in range(min(h,hh),max(h,hh)+1)))
    if token.endswith('+'):
        h,l,m=cls(token[:-1])
        if h==l:return set().union(*(combos(r,r,m) for r in range(h,13)))
        return set().union(*(combos(h,r,m) for r in range(l,h)))
    return combos(*cls(token))
def save(name,v):
    with (HERE/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
anchor_path=ROOT/'runs/D033-oracle-anchors/anchors.json'
anchor=json.loads(anchor_path.read_text(encoding='utf-8'))['fixtures'][0]
config=anchor['config'];flop={card(config['board'][i:i+2]) for i in range(0,6,2)}
hands=[]
for name in ['range_oop','range_ip']:
    parsed=set().union(*(expand(token) for token in config[name].split(',')))
    hands.append(sorted(h for h in parsed if not flop.intersection(h)))
assert [len(h) for h in hands]==anchor['hands']==[257,319]
rows=[]
for turn,river in itertools.combinations([c for c in range(52) if c not in flop],2):
    valid=[[h for h in group if turn not in h and river not in h] for group in hands]
    for p in [0,1]:
        own=valid[p];opp=valid[1-p];degrees=[0]*52
        for a,b in opp:degrees[a]+=1;degrees[b]+=1
        direct=sum(degrees[a]+degrees[b] for a,b in own)
        cache=2*len(opp)
        rows.append({'turn':turn,'river':river,'p':p,'m_p':len(own),'m_o':len(opp),
            'direct_position_words':direct,'cache_copy_words':cache,
            'direct_to_copy_ratio':direct/cache if cache else None,
            'old_dynamic_bytes':4*len(hands[1-p])+8*len(opp),
            'proposed_local_layout_bytes':4*len(hands[1-p])+16*len(opp)})
summary={'scope':'Unweighted all unordered rainbow runouts; not canonical GpuPlan visitation or dynamic timing',
    'method':'Hand-class expansion follows copied range.rs, exact card exclusions only; no hand-strength evaluator needed for card-list lengths',
    'source_anchor_sha256':hashlib.sha256(anchor_path.read_bytes()).hexdigest(),
    'config':config,'base_hands':[len(h) for h in hands],'runout_count':len(rows)//2,'rows':len(rows),
    'performance_measurement':False,'players':[]}
for p in [0,1]:
    group=[x for x in rows if x['p']==p]
    def span(k):
        values=[x[k] for x in group]
        return {'min':min(values),'median':statistics.median(values),'max':max(values)}
    summary['players'].append({'p':p,**{k:span(k) for k in ['m_p','m_o','direct_position_words','cache_copy_words','direct_to_copy_ratio']},
        'inferred_global_launch_max_old_dynamic_bytes':max(x['old_dynamic_bytes'] for x in group),
        'inferred_global_launch_max_candidate_dynamic_bytes':max(x['proposed_local_layout_bytes'] for x in group)})
save('rainbow-unweighted-census.json',rows)
save('census-summary.json',summary)
print(json.dumps(summary,indent=2))
