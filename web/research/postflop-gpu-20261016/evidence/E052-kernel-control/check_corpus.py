"""Host-only corpus anti-vacuity check; not a GPU exactness oracle or a case pass."""
from pathlib import Path
import json,struct,hashlib
P=Path(__file__).resolve().parent
j=json.loads((P/'corpus.json').read_text(encoding='utf-8'))
def f(v):return struct.unpack('<f',struct.pack('<I',v))[0]
def r(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def bits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
rows=[]
for c in j['cases']:
 g=next(g for g in j['geometries'] if g['id']==c['geometry']);a=g['arrays'];m=g['m_o'];mp=g['m_p']
 if not c['count']:continue
 ro=list(map(f,c['reach_o_bits'][2*g['nh_o']:3*g['nh_o']]))
 reach=[ro[i] for i in a['o_idx'][7:7+m]];prefix=[0.]*m;chunk=(m+127)//128;cs=[0.]*129
 for lane in range(128):
  acc=0.
  for k in range(lane*chunk,min((lane+1)*chunk,m)):acc=r(acc+reach[k]);prefix[k]=acc
  cs[lane+1]=acc
 for k in range(1,129):cs[k]=r(cs[k]+cs[k-1])
 for lane in range(128):
  for k in range(lane*chunk,min((lane+1)*chunk,m)):prefix[k]=r(prefix[k]+cs[lane])
 total=prefix[-1] if m else 0.;outs=[]
 for node in [2,5]:
  win,lose,tie=[f(a[k][node]) for k in ['node_twin','node_tlose','node_ttie']]
  for k in range(mp):
   i=a['p_idx'][5+k];lb=a['p_lower'][5+k];ub=a['p_upper'][5+k];lower=prefix[lb-1] if lb else 0.;higher=r(total-(prefix[ub-1] if ub else 0.));tc=lc=hc=0.
   for card in [a['pc1'][i],a['pc2'][i]]:
    for t in range(a['o_card_off'][53+card],a['o_card_off'][54+card]):
     pos=a['o_card_pos'][t];v=reach[pos];tc=r(tc+v)
     if pos<lb:lc=r(lc+v)
     elif pos>=ub:hc=r(hc+v)
   sc=a['same_p'][i];same=ro[sc] if sc!=0xffffffff else 0.;valid=r(r(total-tc)+same);lower=r(lower-lc);higher=r(higher-hc);tied=r(r(valid-lower)-higher)
   out=r(r(r(win*lower)+r(lose*higher))+r(tie*tied));outs.append((node,i,bits(out)))
 nz=sum((v&0x7fffffff)!=0 for node,i,v in outs)
 if g['target_m']>=127 and c['profile']!='all_zero':assert nz>0,c['id']
 if g['board_text']=='AsKsQsJsTs' and g['target_m']==257 and c['profile']=='sparse_rounding_witness':assert next(v for node,i,v in outs if node==5 and i==g['rounding_witness_own_index'])==bits(-.25)
 rows.append({'case_id':c['id'],'nonzero_host_reference_words':nz})
report={'id':'D051-host-anti-vacuity','status':'pass','scope':'Host binary32 model used only to verify corpus has nonzero outputs and intended sparse witness, not a GPU comparison or numerical case pass; no FTZ/FMA claim.','corpus_sha256':hashlib.sha256((P/'corpus.json').read_bytes()).hexdigest(),'regular_cases':len(rows),'all_nonzero_expected_profiles_have_nonzero_output':True,'sparse_witness_own_cfv_minus_quarter':True,'rows':rows,'native_execution':False}
with (P/'host-anti-vacuity.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
