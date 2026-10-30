"""Generate the approved finite D051 corpus once; host-only, no native/CUDA calls."""
from pathlib import Path
from itertools import combinations
from collections import Counter
import bisect,hashlib,json,struct
HERE=Path(__file__).resolve().parent
GUARD=0x4b123456;SENTINEL=0xffffffff
COUNTS=[0,1,127,128,129,255,256,257,1081]
PROFILES=['all_zero','sparse_rounding_witness','seeded_ordinary','subnormal_mixed_scales']
def card(s):return '23456789TJQKA'.index(s[0])*4+'cdhs'.index(s[1])
def parse(s):return [card(s[i:i+2]) for i in range(0,len(s),2)]
def fb(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def xorshift(x):
 x^=(x<<13)&0xffffffff;x^=x>>17;x^=(x<<5)&0xffffffff;return x&0xffffffff
def shuffled(seq,seed):
 seq=list(seq)
 for i in range(len(seq)-1,0,-1):seed=xorshift(seed);j=seed%(i+1);seq[i],seq[j]=seq[j],seq[i]
 return seq
def eval5(cs):
 ranks=sorted((c>>2 for c in cs),reverse=True);groups=sorted(((n,r) for r,n in Counter(ranks).items()),reverse=True)
 unique=sorted(set(ranks),reverse=True);flush=len({c&3 for c in cs})==1
 high=(unique[0] if len(unique)==5 and unique[0]-unique[4]==4 else 3 if unique==[12,3,2,1,0] else None)
 if flush and high is not None:cat,rs=8,[high]
 elif groups[0][0]==4:cat,rs=7,[groups[0][1],groups[1][1]]
 elif groups[0][0]==3 and groups[1][0]==2:cat,rs=6,[groups[0][1],groups[1][1]]
 elif flush:cat,rs=5,ranks
 elif high is not None:cat,rs=4,[high]
 elif groups[0][0]==3:cat,rs=3,[r for n,r in groups]
 elif groups[0][0]==2 and groups[1][0]==2:cat,rs=2,[r for n,r in groups]
 elif groups[0][0]==2:cat,rs=1,[r for n,r in groups]
 else:cat,rs=0,ranks
 v=cat
 for i in range(5):v=(v<<4)|(rs[i] if i<len(rs) else 0)
 return v
def rank7(cs):return max(eval5(c) for c in combinations(cs,5))
def geometry(boardtext,m,p):
 board=parse(boardtext);flop=set(board[:3]);final=set(board)
 root=[h for h in combinations(range(52),2) if not(set(h)&flop)]
 valid=[h for h in root if not(set(h)&final)];blocked=[h for h in root if set(h)&final]
 assert len(root)==1176 and len(valid)==1081 and len(blocked)==95
 rank={h:rank7(board+list(h)) for h in valid}
 order=shuffled(valid,0xD0511234)
 small=order[:m]+blocked[:95 if m==1081 else 17]
 other=order[:257]+blocked[:17]
 ranges=[shuffled(other,0x31791234),shuffled(small,0x91531abc)]
 hp,ho=ranges[p],ranges[1-p]
 sp=sorted((rank[h],i) for i,h in enumerate(hp) if h in rank);so=sorted((rank[h],i) for i,h in enumerate(ho) if h in rank)
 assert sorted([len(sp),len(so)])==sorted([m,257])
 nhp,nho=len(hp),len(ho);nhmax=max(nhp,nho)+11
 strength_o=[r for r,i in so];lower=[bisect.bisect_left(strength_o,r) for r,i in sp];upper=[bisect.bisect_right(strength_o,r) for r,i in sp]
 bycard=[[pos for pos,(r,i) in enumerate(so) if c in ho[i]] for c in range(52)]
 cpos=[GUARD]*11;coff=[0]*53
 for c in range(52):coff.append(len(cpos));cpos+=bycard[c]
 coff.append(len(cpos));assert coff[106-1]-coff[53]==2*len(so);cpos +=[GUARD]*7
 same=[ho.index(h) if h in ho else SENTINEL for h in hp]
 nodes=[SENTINEL,SENTINEL,2,5,SENTINEL,SENTINEL]
 cfvslot=[0]*7;cfvslot[2]=3;cfvslot[5]=1
 rsrc=[0]*7;rsrc[2]=2;rsrc[5]=4
 active=[False]*(6*nhmax+13)
 for n in [2,5]:
  for i in range(nhp):active[cfvslot[n]*nhmax+i]=True
 arrays={'nodes':nodes,'node_twin':[fb(0)]*7,'node_tlose':[fb(0)]*7,'node_ttie':[fb(0)]*7,'node_river_slot':[0,0,1,0,0,1,0],'rsrc_o':rsrc,
 'p_off':[0,5],'p_cnt':[0,len(sp)],'p_idx':[SENTINEL]*5+[i for r,i in sp]+[SENTINEL]*3,
 'p_lower':[SENTINEL]*5+lower+[SENTINEL]*3,'p_upper':[SENTINEL]*5+upper+[SENTINEL]*3,
 'o_off':[0,7],'o_cnt':[0,len(so)],'o_idx':[SENTINEL]*7+[i for r,i in so]+[SENTINEL]*3,
 'o_card_off':coff,'o_card_pos':cpos,'same_p':same+[SENTINEL]*3,'pc1':[h[0] for h in hp]+[SENTINEL]*3,'pc2':[h[1] for h in hp]+[SENTINEL]*3,'cfv_slot':cfvslot}
 for n,win,tie in [(2,5,0),(5,4.5,-.25)]:arrays['node_twin'][n]=fb(win);arrays['node_tlose'][n]=fb(-5);arrays['node_ttie'][n]=fb(tie)
 # Coverage observations are integer facts about this actual board/range, not GPU results.
 flags={'same_present':sum(v!=SENTINEL for v in same),'same_absent':sum(v==SENTINEL for v in same),'positive_lower':sum(x>0 for x in lower),'nonempty_higher':sum(x<len(so) for x in upper),'tie_boundaries':sum(a<b for a,b in zip(lower,upper)),'blocked_own':nhp-len(sp),'blocked_opponent':nho-len(so)}
 first4={c for r,i in so[:4] for c in ho[i]}
 witness=next((i for r,i in sp if not(set(hp[i])&first4)),None)
 if boardtext=='AsKsQsJsTs' and m==257:assert witness is not None
 return {'id':f'{boardtext}-m{m}-p{p}','board':board,'board_text':boardtext,'target_m':m,'player':p,'hands_p':hp,'hands_o':ho,'strengths_p':[rank.get(h,SENTINEL) for h in hp],'strengths_o':[rank.get(h,SENTINEL) for h in ho],'nh_p':nhp,'nh_o':nho,'nh_max':nhmax,'m_p':len(sp),'m_o':len(so),'start':2,'count':2,'grid_blocks':4,'dynamic_shared_bytes':4*nho+16*len(so),'arrays':arrays,'output_initial':[GUARD]*len(active),'output_active':active,'coverage':flags,'rounding_witness_own_index':witness}
def case(g,profile):
 so=g['arrays']['o_idx'][7:7+g['m_o']];row=[fb(0 if profile=='all_zero' else .25)]*g['nh_o'];seed=0xD0515eed
 for k,i in enumerate(so):
  seed=xorshift(seed)
  if profile=='all_zero':v=0
  elif profile=='sparse_rounding_witness':v=[fb(1),fb(2**-24),fb(2**-24),fb(2**-24)][k] if k<4 else 0
  elif profile=='seeded_ordinary':v=fb((seed&4095)/4096) if k%11 else 0
  else:v=[fb(.5),0,0x80000000,1,0x007fffff,0x00800000,fb(2**-24),fb(.125),fb(1),fb(1-2**-24)][k%10]
  row[i]=v
 reach=[GUARD]*(6*g['nh_o']+7)
 for slot in [2,4]:reach[slot*g['nh_o']:(slot+1)*g['nh_o']]=row
 return {'id':g['id']+'-'+profile,'geometry':g['id'],'profile':profile,'count':2,'reach_o_bits':reach}
def main():
 geometries=[];cases=[]
 for board in ['Ks7h2dQhTc','AsKsQsJsTs']:
  for m in COUNTS:
   for p in [0,1]:
    g=geometry(board,m,p);geometries.append(g)
    for profile in PROFILES:cases.append(case(g,profile))
 for board in ['Ks7h2dQhTc','AsKsQsJsTs']:
  for p in [0,1]:
   g=next(g for g in geometries if g['board_text']==board and g['target_m']==257 and g['player']==p)
   c=case(g,'seeded_ordinary');c['count']=0;c['id']+='-count0';cases.append(c)
 assert len(geometries)==36 and len(cases)==148
 counts={k:sum(g['coverage'][k] for g in geometries) for k in geometries[0]['coverage']};assert all(v>0 for v in counts.values())
 data={'id':'D051','seed':'deterministic xorshift32; seeds in generator source','rank_oracle':'independent best-of21 five-card evaluator; actual accepted Rust evaluate7 rechecks every frozen root-hand rank before CUDA context creation','guard':GUARD,'geometries':geometries,'cases':cases}
 payload=(json.dumps(data,separators=(',',':'),allow_nan=False)+'\n').encode()
 with (HERE/'corpus.json').open('xb') as f:f.write(payload)
 summary={'id':'D051-corpus','geometry_count':36,'comparison_pairs':148,'kernel_launches':296,'regular_pairs':144,'zero_count_pairs':4,'corpus_sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload),'coverage_integer_counts':counts,'required_device_input_buffers_per_variant':21,'required_active_words_per_pair':sum(sum(g['output_active']) if c['count'] else 0 for c in cases for g in geometries if g['id']==c['geometry']),'required_output_guard_checks_across_both_variants':2*sum(len(g['output_active'])-(sum(g['output_active']) if c['count'] else 0) for c in cases for g in geometries if g['id']==c['geometry']),'max_valid_river_hands':1081,'native_execution':False}
 with (HERE/'corpus-summary.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(summary,f,indent=2);f.write('\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
