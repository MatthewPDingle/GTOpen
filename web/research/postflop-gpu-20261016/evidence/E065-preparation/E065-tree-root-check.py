"""Replay every paired typed tree byte and independently recompute CPU admission."""
import array,json,statistics,struct,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
H=ROOT/'runs/E065-tree-control';P=old.read(H/'protocol.json');q=old.read(H/'report.json');corpus=old.read(H/'corpus.json');checks=0
def check(v):
 global checks
 assert v;checks+=1
def read_exact(f,n):
 b=f.read(n);assert len(b)==n;return b
def u64(f):return struct.unpack('<Q',read_exact(f,8))[0]
def typed(b,kind):
 a=array.array(kind);a.frombytes(b)
 if sys.byteorder!='little':a.byteswap()
 return a
def case_for(label):
 if label.startswith('canonical-'):return corpus['canonical'][int(label.split('-')[1])]
 return next(c for c in corpus['controls'] if c['name']==label)
def board_cards(text):
 ranks='23456789TJQKA';suits='cdhs';assert len(text)%2==0
 return [ranks.index(text[i])*4+suits.index(text[i+1]) for i in range(0,len(text),2)]
old.custody();assert not (ROOT/'gpu-run.lock').exists()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status())
 for p,h in P['input_sha256'].items():old.pin(p,h);checks+=1
 for label in ['rustc','canonical-0','canonical-1','canonical-2','controls']:
  e=old.read(H/'execution'/(label+'.exit.json'));check(e['returncode']==0 and e['error'] is e['cleanup'] is None)
 markers=[]
 for label in ['canonical-0','canonical-1','canonical-2','controls']:
  ms=[json.loads(x.split('E065_TREE ',1)[1]) for x in (H/'execution'/(label+'.stdout.log')).read_text(encoding='utf-8').splitlines() if x.startswith('E065_TREE ')];check(ms[-1]['stage']=='complete' and ms[-1]['all_exact']);markers.extend(ms[:-1])
 check([m for m in markers if m['stage']=='canonical']==q['canonical']);check([m['result'] for m in markers if m['stage']=='control']==q['controls'])
 total_nodes=total_children=total_actions=total_raw_bytes=total_paired_words=0;files=[];last=time.monotonic()
 for rec in q['raw_files']:
  path=Path(rec['path']);old.pin(path,rec['sha256']);check(path.stat().st_size==rec['bytes'] and path.parent==H/'execution');case=case_for(rec['label']);expected_cfg=case.get('tree',case.get('spot',{}).get('tree'));board=board_cards(case['spot']['board'] if 'spot' in case else case['board']);hands=rec['hands']
  with path.open('rb') as f:
   check(read_exact(f,16)==b'D106-TREE-RAW1\0\0');caseid,version=struct.unpack('<II',read_exact(f,8));check(caseid==case['id'] and version==1)
   a=struct.unpack('<11Q',read_exact(f,88));b=struct.unpack('<11Q',read_exact(f,88));check(list(a)==rec['metadata'] and a==b);checks+=11
   nn,nc,na,street,ds0,ds1,capn,capc,capa,nsize,asize=a;check(street==len(board)-3 and capn>=nn and capc>=nc and capa>=na and nsize==64 and asize==16)
   configs=[read_exact(f,u64(f)) for _ in range(2)];check(configs[0]==configs[1] and json.loads(configs[0])==expected_cfg);checks+=len(configs[0])
   data=[0,0];spans=[];node_types=[0,0,0,0];native_checks=11+len(configs[0])+12*nn+nc+2*na
   check(native_checks==rec['checks'])
   for base in range(0,nn,8192):
    rows=min(8192,nn-base);words=typed(read_exact(f,rows*24*8),'Q')
    for column in range(12):check(words[column::24]==words[column+12::24]);checks+=rows
    for j in range(rows):
     k=j*24;kind,player,st,count,childstart,actionstart,offset=words[k:k+7];index=base+j
     check(kind<=3 and player<=1 and st<=2);node_types[kind]+=1
     if kind==0:
      check(0<count<=250 and childstart+count<=nc and actionstart+count<=na and offset==data[player]);data[player]+=count*hands[player];spans.append((index,kind,childstart,count))
     elif kind==1:
      check(count==52 and childstart+52<=nc and actionstart==0 and offset==0);spans.append((index,kind,childstart,count))
     else:check(count==childstart==actionstart==offset==0)
   check(data==[ds0,ds1])
   paired_children=typed(read_exact(f,nc*8),'I');children=paired_children[0::2];check(children==paired_children[1::2]);checks+=nc
   # Root-board-only sentinels preserve the existing phantom-runout layout.
   blocked=set(board);edges=0
   for parent,kind,start,count in spans:
    for slot,child in enumerate(children[start:start+count]):
     if kind==1 and slot in blocked:check(child==0xffffffff)
     else:check(parent<child<nn);edges+=1
   check(edges==nn-1)
   for base in range(0,na,16384):
    rows=min(16384,na-base);words=typed(read_exact(f,rows*4*8),'Q');check(words[0::4]==words[2::4] and words[1::4]==words[3::4]);checks+=2*rows
    for j in range(rows):check(words[4*j]<=4 and (words[4*j]>1 or words[4*j+1]==0))
   check(f.read(1)==b'')
  files.append({'label':rec['label'],'nodes':nn,'children':nc,'actions':na,'raw_bytes':rec['bytes'],'node_types':node_types,'native_typed_comparisons':native_checks,'all_fields_capacities_configs_exact':True,'independent_tree_offsets_edges_sentinels_pass':True})
  total_nodes+=nn;total_children+=nc;total_actions+=na;total_raw_bytes+=rec['bytes'];total_paired_words+=12*nn+nc+2*na
  if time.monotonic()-last>=20:print('Raw tree replay:',len(files),'files,',total_nodes,'nodes checked',flush=True);last=time.monotonic()
 baseline_sum=candidate_sum=0.0;guards=[]
 for row in q['canonical']:
  av,bv=row['baseline_samples_ms'],row['candidate_samples_ms'];check(len(av)==len(bv)==9)
  am,bm=statistics.median(av),statistics.median(bv);check(am==row['baseline_median_ms'] and bm==row['candidate_median_ms'] and am-bm==row['saving_ms']);slower=sum(b>a for a,b in zip(av,bv));check(slower==row['slower_pairs']);baseline_sum+=am;candidate_sum+=bm;guards.append({'id':row['id'],'positive_median_slowdown':bm>am,'slower_pairs':slower,'failed':bm>am and slower>=5})
 saving=sum(row['baseline_median_ms']-row['candidate_median_ms'] for row in q['canonical']);check(saving==q['sum_component_median_saving_ms'] and guards==q['component_guards']);check(saving<P['minimum_component_saving_ms'] and guards[-1]['failed'] and q['status']=='rejected_component_admission')
 check(q['exclusions']==[] and q['extension_samples']==q['historical_timing_samples_scored']==0);check(len(files)==23 and len(q['controls'])==30)
 errors=[r for r in q['controls'] if r['status']=='exact_error'];check(len(errors)==10)
 R=ROOT/'comparisons/E065-tree-root-check';R.mkdir();report={'id':R.name,'at':old.now(),'status':'pass_preserved_component_rejection','checks':checks,'protocol_sha256':old.sha(H/'protocol.json'),'native_report_sha256':old.sha(H/'report.json'),'files':files,'total_raw_bytes':total_raw_bytes,'raw_nodes_compared':total_nodes,'raw_child_slots_compared':total_children,'raw_actions_compared':total_actions,'raw_typed_words_compared':total_paired_words,'native_error_equalities':len(errors),'baseline_component_median_sum_ms':baseline_sum,'candidate_component_median_sum_ms':candidate_sum,'component_saving_ms':saving,'required_component_saving_ms':P['minimum_component_saving_ms'],'component_guards':guards,'all_source_main_live_ptx_unchanged':True,'production_source_activated':False,'GPU_executions':0,'full_cycle_performance_measured':False,'candidate_accepted':False,'limits':'Root raw paired fields/capacity/config/structure and timing arithmetic replay, not external independent audit. Error equality is nativeasserted; both raw error strings were not separately saved. Per-sample full fingerprints asserted natively; all final/control successful trees retained raw. BudgetN-1success preserves original builder boundary behavior; no stricter cap assertion imposed. Timed wrapper includes same fixed TreeConfig clone/deserialization, as clarified before native. Historical complete-cycle reference is admission proxy only, not a measured full-cycle gain.'};old.save(R/'report.json',report);old.custody();print(json.dumps({k:v for k,v in report.items() if k not in ['files']},indent=2),flush=True)
