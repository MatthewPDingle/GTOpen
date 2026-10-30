"""Read the original, unchanged twelve plans; count fixed adjacent-CTA reuse."""
import array,json,struct,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D248-cluster-metadata-census'
A=Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs\D092-action-arity-order')

def prepare():
 h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
 H.mkdir(exist_ok=False)
 prior=h.read(A.parent/'D111-showdown-order-audit/protocol.json')
 sources=[h.REPO/'crates/solver/src/gpu'/n for n in ['plan.rs','kernels.cu','mod.rs']]
 for p in sources[:2]:h.pin(p,prior['input_sha256'][str(p)])
 raw=[{'path':str(A/'execution'/f'case-{i:02d}.bin'),'sha256':prior['input_sha256'][str(A/'execution'/f'case-{i:02d}.bin')]}for i in range(12)]
 files=[Path(__file__),ROOT/'epoch/common.py',A/'field-schema.json',A/'report.json',A.parent/'D111-showdown-order-audit/protocol.json',ROOT/'comparisons/D247-cluster-controls/report.json']+sources
 h.save(H/'protocol.json',{'id':'D248','at':h.now(),'status':'FROZEN_PRE_CPU_CENSUS','input_sha256':{str(p):h.sha(p)for p in files},'raw_inputs':raw,'required_free_bytes':12*1024**3,'pairing':'Unchanged original show-node worklist, pairs (0,1),(2,3),... reset at each original launch span. Never sort or regroup; preserve odd tail. Both original player orientations.','selected_fields':['num_nodes','num_slots','show_nodes','show_spans','node_river_slot','cfv_slot','cfv_blocks','riv_cnt','riv_card_off','riv_card_pos'],'scope':'Original twelve E051 plans have byte-identical current accepted plan source and kernel source. Historical CPU metadata only, all source hashes checked. Count identical immutable card-position slices only; do not share node reach, prefix sums, output CFV or floating arithmetic. No solver candidate/compiler/GPU/speed run.','gates':['All original input hashes and complete framing/EOF.','Complete unchanged level partition; every show node and CFV owner unique and in bounds.','All slots and all original card-position offsets/indices valid for both players.','Count all fixed pairs including mismatches and odd tails; integer sums conserved.'],'selection':'Any matched pair establishes structural immutable-copy reuse only. Counts/bytes are not timing, cache misses, removable wall time, or candidate admission. A separate source/history/material-cost decision is required. No D183/D110 timing used.','semantic_history':'Additional output lanes declined as too close to closed E026 geometry and no identified eliminated work. This census instead tests omission of one duplicate immutable card-position copy in fixed adjacent CTAs, leaving both original 128-thread per-node scans/arithmetic untouched. Closed E069 sorting and D068 reach-owner sharing excluded.'})
 print(h.sha(H/'protocol.json'),flush=True)

def execute(identity):
 h.pin(H/'protocol.json',identity);P=h.read(H/'protocol.json')
 for p,d in P['input_sha256'].items():h.pin(p,d)
 schema=h.read(A/'field-schema.json')['fields'];anchors=h.read(A/'report.json')['cases'];checks=0
 def ck(v,label):
  nonlocal checks
  assert v,label;checks+=1
 def words(f,selected=False):
  raw=f.read(8);ck(len(raw)==8,'whole word-count framing');n,=struct.unpack('<Q',raw);ck(n<100000000,'bounded word count')
  if not selected:f.seek(n*8,1);return None
  v=array.array('Q');v.fromfile(f,n);ck(len(v)==n,'whole selected words');return v
 def vec(v):ck(len(v)>0 and v[0]+1==len(v),'whole vector');return v[1:]
 def pair(v):
  ck(v[0]==2,'two-player array');at=1;out=[]
  for p in range(2):n=v[at];out.append(v[at+1:at+1+n]);ck(len(out[-1])==n,'whole player vector');at+=n+1
  ck(at==len(v),'whole nested player array');return out
 results=[]
 with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
  h.custody();h.ar.refuse_active(h.ar.live_status());ck(shutil.disk_usage(ROOT).free>=P['required_free_bytes'],'X free reservation')
  for i,item in enumerate(P['raw_inputs']):
   path=Path(item['path']);print('Hash/read original plan',i,flush=True);h.pin(path,item['sha256']);D={}
   with path.open('rb')as f:
    ck(f.read(16)==b'D092-PLAN-RAW1\0\0','raw magic');ck(struct.unpack('<II',f.read(8))==(i,53),'identity/schema');ck(len(f.read(16))==16,'original clocks ignored')
    for ix,desc in enumerate(schema):
     ck(struct.unpack('<I',f.read(4))[0]==ix,'field sequence');words(f);words(f);v=words(f,desc['name']in P['selected_fields']);words(f)
     if v is not None:D[desc['name']]=v
    words(f);words(f);ck(f.read(1)==b'','complete EOF')
   nn=D['num_nodes'][0];ns=D['num_slots'][0];nb=D['cfv_blocks'][0];nodes=vec(D['show_nodes']);slots=vec(D['node_river_slot']);cfv=vec(D['cfv_slot']);span=D['show_spans'];cnt=pair(D['riv_cnt']);off=pair(D['riv_card_off']);pos=pair(D['riv_card_pos'])
   ck(len(slots)==len(cfv)==nn and len(span)==1+span[0]*2,'node/span shape');ck(len(set(nodes))==len(nodes),'all show owners unique');ck(all(n<nn and slots[n]<ns and cfv[n]<nb for n in nodes),'all original show bounds');ck(len({cfv[n]for n in nodes})==len(nodes),'all persistent CFV outputs disjoint')
   for p in range(2):
    ck(len(cnt[p])==ns and len(off[p])==ns*53,'all slot/card geometry');last=0
    for s in range(ns):
     offsets=off[p][s*53:(s+1)*53];ck(offsets[0]==last and offsets[-1]-last==2*cnt[p][s]and offsets[-1]<=len(pos[p]),'whole two-card copy slice');ck(all(a<=b for a,b in zip(offsets,offsets[1:])),'monotone card spans');ck(all(x<cnt[p][s]for x in pos[p][last:offsets[-1]]),'all immutable sorted positions in bounds');last=offsets[-1]
    ck(last==len(pos[p]),'whole card-position allocation covered')
   end=0;rows=[];matched_total=pair_total=tail_total=0;original=[0,0];omitted=[0,0]
   for level in range(span[0]):
    start,n=span[1+level*2:3+level*2];ck(start==end and start+n<=len(nodes),'whole original launch partition');end=start+n;row=nodes[start:end];pairs=n//2;matched=[]
    for j in range(0,n-1,2):
     if slots[row[j]]==slots[row[j+1]]:matched.append(slots[row[j]])
    copy=[sum(2*cnt[1-p][slots[node]]for node in row)for p in range(2)];skip=[sum(2*cnt[1-p][s]for s in matched)for p in range(2)]
    ck(all(0<=skip[p]*2<=copy[p]for p in range(2)),'copy omission conservation bound');matched_total+=len(matched);pair_total+=pairs;tail_total+=n%2
    for p in range(2):original[p]+=copy[p];omitted[p]+=skip[p]
    rows.append({'level':level,'nodes':n,'pairs':pairs,'matched_slot_pairs':len(matched),'mismatched_pairs':pairs-len(matched),'odd_tail':n%2,'original_card_copy_words_by_player':copy,'omittable_card_copy_words_by_player':skip})
   ck(end==len(nodes) and 2*pair_total+tail_total==len(nodes),'all launch work covered')
   result={'id':i,'board':anchors[i]['board'],'iso_requested':anchors[i]['iso_requested'],'full_arenas':anchors[i]['full_arenas'],'show_nodes':len(nodes),'fixed_pairs':pair_total,'matched_slot_pairs':matched_total,'mismatched_slot_pairs':pair_total-matched_total,'odd_tails':tail_total,'matched_pair_pct':100*matched_total/pair_total if pair_total else 0,'original_card_copy_words_by_player':original,'omittable_card_copy_words_by_player':omitted,'omittable_copy_pct_by_player':[100*omitted[p]/original[p]if original[p]else 0 for p in range(2)],'levels':rows,'raw_input_sha256':item['sha256']};results.append(result)
   print(json.dumps({k:v for k,v in result.items()if k not in ['levels','raw_input_sha256']}),flush=True)
  h.custody()
 report={'id':'D248','at':h.now(),'status':'pass_structural_adjacent_immutable_copy_census','protocol_sha256':identity,'checks':checks,'cases':results,'structural_reuse_present':any(x['matched_slot_pairs']for x in results),'new_compilers_native_GPU_solver_or_speed_samples':0,'optimizer_or_gain_accepted':False,'limits':P['selection'],'source_and_live_unchanged':True}
 h.save(H/'report.json',report);print('D248 complete',checks,flush=True)

if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 else:execute(sys.argv[2])
