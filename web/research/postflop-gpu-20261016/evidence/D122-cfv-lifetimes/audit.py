"""Fixed retained-data CFV lifetime/alias scout; no native, CUDA or timing."""
from pathlib import Path
import array,collections,hashlib,json,re,shutil,struct,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
assert sys.byteorder=='little';old.custody();assert not(R/'gpu-run.lock').exists();assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
H=R/'runs/D122-cfv-lifetimes';assert not H.exists();H.mkdir();A=R/'runs/D092-action-arity-order';AR=old.read(A/'report.json');old.pin(A/'accepted-plan.rs',old.BASE['crates/solver/src/gpu/plan.rs'])
raws=[A/'execution'/f'case-{i:02d}.bin'for i in range(12)]
source_paths=[old.REPO/'crates/solver/src/gpu'/n for n in ['plan.rs','mod.rs','kernels.cu']]+[old.REPO/'crates/solver/src/tree.rs']
tree=source_paths[-1].read_text(encoding='utf-8');assert all(f'pub const {name}: u8 = {value};'in tree for name,value in [('KIND_ACTION',0),('KIND_CHANCE',1),('KIND_TERM_FOLD',2),('KIND_TERM_SHOWDOWN',3)])
history=subprocess.run(['git','log','--all','--format=%H','-G','unary|alias_child|alias_parent|linear.scan|cfv.*interval|interval.*cfv|singleton','--','crates/solver/src/gpu/plan.rs'],cwd=old.REPO,text=True,capture_output=True,check=True);assert not history.stdout.strip()
old.save(H/'history.json',{'at':old.now(),'query':history.args,'local_all_ref_matches':history.stdout.splitlines(),'scope':'Bounded local all-ref CFVplanner/ledger search, not exhaustive remote novelty.','distinct_from_closed_forms':'Not E025row padding, E027reach pitch, E047arity dispatch, E054early-store scheduling or E075uniform loads. No prior source/timing composed or rescued.'})
P={'id':'D122','at':old.now(),'scope':'Exactly12retained accepted E051metadata cases, source/liveness/integer model only. No compiler, rebuilt plan, CUDA/appkernel, solver, new timing or source activation.','input_sha256':{str(p):old.sha(p)for p in [Path(__file__),A/'report.json',A/'field-schema.json',A/'accepted-plan.rs',*raws,*source_paths,C/'common_e051_live.py',C/'protected-main.json',H/'history.json']},'fixed_analysis':['Count all one-action parents by actual child kind/arity; retain concrete potential cross-CTA conflicts for naive early parent writes into existing two-parity storage.','Model only disjoint pairs: reachedone-action parent whose unique reachedchild is an action node ofarity>=2. No chain/fusion implementation.','Merge parent/child CFVintervals into one closedinterval[level(parent)-1,level(child)]. Preserve original level schedule,all float kernels/updates and terminal caches. Sharedrow would be read then overwritten by the originalone-actionparent, same hand index only.','Assign representative interval colors in descending producer level, nodeIDascending, LIFOfree colors; retire only after all consumption in a stage. Relabel the rootcolor to0. Assign distinct terminal caches after scratchcolors in original nodeIDorder.','Independently verify per-color closedinterval nonoverlap and actual action/chance graph read/write collisions: only selectedone-actionparent may read/write its selectedchild row in place. Check all other shared logical-node pairs/lifetimes and terminal/root/sentinel/geometry contracts.'],'admission':'Require all12models valid, scratch/block/payload never increases, and at leastone canonical iso-on flop has fewerCFVblocks before implementing one Rustprototype. This is storage/source feasibility only, not a measured speedup/traffic bound or no-tradeoff proof. Actual CPUtemporary/packing/capacity costs and all GPU/exact/broad/1%/strictfixture/fresh16/material/holdout/cumulative gates remain.','no_optimization_accepted':True};old.save(H/'protocol.json',P)
def publish(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes()
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(p)}
pub=[publish(H/n,H.name+'/'+n)for n in ['history.json','protocol.json']];pub.append(publish(Path(__file__),H.name+'/audit.py'));old.save(H/'pre-execution-publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'metadata_cases_decoded':0,'native_or_GPU_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']=='D122'for x in s['experiments']);s['experiments'].append({'id':'D122','at':old.now(),'title':'Single-action CFV lifetime and sharing scout','kind':'diagnostic','status':'running','correctness':'Integer/source analysis underway','fixture':'12retained accepted E051metadata cases','stage':'Exact lifetime/address model','reason':'Check naive fusion hazards and a separate original-schedule parent/child sharing layout. No compiler, GPU kernel or speed result.','accepted':False,'evidence':[{'label':'Frozen retained-data/lifetime analysis','url':'evidence/D122-cfv-lifetimes/protocol.json'}]});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='D122',stage='D122 CFV storage lifetime analysis',activity='E075closed after1.0196%gain but rainbowguard fail. Analyze all12accepted metadata cases for one-action CFVsharing and actual per-level dependencies. No new source/kernel/timing, E051accepted/deployed gain12.44%unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
checks=0
def ck(v,label):
 global checks
 assert v,label;checks+=1
def vector(f,read=False):
 n,=struct.unpack('<Q',f.read(8));ck(n<100000000,'bounded encoded vector')
 if not read:f.seek(n*8,1);return None
 v=array.array('Q');v.fromfile(f,n);ck(len(v)==n,'full vector');return v
selected=[0,1,2,3,5,6,11,12,13,14,15,16,20,24,27,36,37]
def payload(v):
 ck(v[0]+1==len(v),'complete vector payload');return v[1:]
def spans(v,nl):
 ck(v[0]==nl and len(v)==1+2*nl,'level span framing');return [(v[1+2*i],v[2+2*i])for i in range(nl)]
cases=[]
for case,path in enumerate(raws):
 old.pin(path,AR['cases'][case]['raw_sha256']);fields={}
 with path.open('rb')as f:
  ck(f.read(16)==b'D092-PLAN-RAW1\0\0','raw framing');ck(struct.unpack('<II',f.read(8))==(case,53),'case/schema');f.read(16)
  for field in range(53):
   ck(struct.unpack('<I',f.read(4))[0]==field,'field id');vector(f);vector(f);v=vector(f,field in selected);vector(f)
   if v is not None:fields[field]=v
  kinds=payload(vector(f,True));children=payload(vector(f,True));ck(f.read(1)==b'','complete raw endpoint')
 nl=fields[0][0];n=fields[3][0];nhmax=fields[2][0];oldblocks=fields[37][0];ck(len(kinds)==n,'node count')
 families=[(payload(fields[fi]),spans(fields[si],nl))for fi,si in [(5,6),(11,12),(13,14),(15,16)]]
 actions,chance,fold,show=[x[0]for x in families];arity=payload(fields[24]);cs=payload(fields[27]);oldslots=payload(fields[36]);cc=payload(fields[20]);ck(len(arity)==len(cs)==len(oldslots)==n,'complete per-node arrays')
 level=array.array('i',[-1])*n
 for expected,(nodes,ss)in enumerate(families):
  for lev,(start,count)in enumerate(ss):
   ck(start+count<=len(nodes),'work span bounds')
   for node in nodes[start:start+count]:ck(level[node]==-1 and kinds[node]==expected,'unique reached kind');level[node]=lev
 widths=[0]*nl
 for node in actions:widths[level[node]]+=1
 for node in chance:widths[level[node]]+=1
 oldscratch=max(widths[::2],default=0)+max(widths[1::2],default=0);ck(oldblocks==oldscratch+len(fold)+len(show),'original two-parity accounting')
 alias_parent=bytearray(n);alias_child=bytearray(n);pairs=[];unary=0;childkinds=collections.Counter();childarities=collections.Counter();owners=array.array('I',[0])*n
 for parent in actions:
  for child in children[cs[parent]:cs[parent]+arity[parent]]:
   ck(level[child]==level[parent]+1,'action edge level');owners[child]+=1
  if arity[parent]!=1:continue
  unary+=1;child=children[cs[parent]];childkinds[int(kinds[child])]+=1
  if kinds[child]==0:
   childarities[int(arity[child])]+=1
   if arity[child]>=2:
    ck(not alias_child[child]and not alias_parent[child],'disjoint candidate groups');alias_parent[parent]=1;alias_child[child]=1;pairs.append((int(parent),int(child)))
 pairmap={parent:child for parent,child in pairs};ck(all(owners[c]==1 for p,c in pairs),'unique action parent for every shared child');ck(not any(alias_child[c]for c in cc),'no chance orbit references to shared children')
 hazard=collections.Counter();witness=[]
 for lev in range(nl-1):
  start,count=families[0][1][lev+1];reads={}
  for consumer in actions[start:start+count]:
   for child in children[cs[consumer]:cs[consumer]+arity[consumer]]:
    if kinds[child]<2:
     slot=oldslots[child]
     if slot in reads:ck(reads[slot][1]==child,'scratch same-stage logical input ownership')
     else:reads[slot]=(int(consumer),int(child))
  for parent,child in pairs:
   if level[parent]!=lev:continue
   target=int(oldslots[parent]);hit=reads.get(target)
   if hit is None:hazard['no_other_action_input_at_original_target']+=1
   elif hit[0]==child:hazard['same_child_CTA_only']+=1
   else:
    hazard['potential_cross_CTA_read_write_conflict']+=1
    if len(witness)<8:witness.append({'parent':parent,'child_CTA':child,'parent_level':lev,'old_target_slot':target,'other_reader_CTA':hit[0],'other_input_node':hit[1],'other_input_level':int(level[hit[1]])})
 # Each group's interval is closed at both producer and final consumer stages.
 groups=[array.array('I')for _ in range(nl)]
 for node in range(n):
  if level[node]>=0 and kinds[node]<2 and not alias_parent[node]:groups[level[node]].append(node)
 slots=array.array('I',[0xffffffff])*n;expiry=[array.array('I')for _ in range(nl+4)];free=[];nextslot=0;live=0;peak=0;intervals=[];by_stage=[]
 for lev in reversed(range(nl)):
  released=expiry[lev+3];free.extend(released);live-=len(released);ck(live>=0,'live count nonnegative')
  for node in groups[lev]:
   if free:slot=free.pop()
   else:slot=nextslot;nextslot+=1
   slots[node]=slot;death=lev-(2 if alias_child[node] else 1);expiry[death+2].append(slot);intervals.append((slot,death,lev,int(node)))
  live+=len(groups[lev]);peak=max(peak,live);by_stage.append({'stage':lev,'born_groups':len(groups[lev]),'retired_groups':len(released),'live_groups':live})
 ck(nextslot==peak and nextslot<=oldscratch,'interval coloring within original capacity')
 for parent,child in pairs:slots[parent]=slots[child]
 rootcolor=int(slots[0]) if kinds[0]<2 else 0
 if kinds[0]<2:
  ck(rootcolor<nextslot,'root has a scratch group')
  for node in range(n):
   if kinds[node]<2 and level[node]>=0:
    if slots[node]==0:slots[node]=rootcolor
    elif slots[node]==rootcolor:slots[node]=0
 # Independent sorted closed-interval verification; no reliance on retire code.
 percolor=collections.defaultdict(list)
 for slot,a,b,node in intervals:percolor[slot].append((a,b,node))
 for color,interval_list in percolor.items():
  interval_list.sort()
  for previous,current in zip(interval_list,interval_list[1:]):ck(previous[1]<current[0],'no closed lifetime overlaps per physical color')
 newblocks=nextslot
 for node in range(n):
  if level[node]>=0 and kinds[node]>=2:slots[node]=newblocks;newblocks+=1
 ck(newblocks==nextslot+len(fold)+len(show)and newblocks<=oldblocks,'full cached-terminal accounting');ck(slots[0]==0,'root slot0 preserved')
 allowed=0
 for lev in range(nl):
  outputs={}
  for family in [0,1]:
   nodes,ss=families[family];start,count=ss[lev]
   for node in nodes[start:start+count]:ck(slots[node]not in outputs,'same-level outputs unique');outputs[slots[node]]=int(node)
  start,count=families[0][1][lev]
  for consumer in actions[start:start+count]:
   for child in children[cs[consumer]:cs[consumer]+arity[consumer]]:
    if slots[child]in outputs:
     ck(outputs[slots[child]]==consumer and pairmap.get(int(consumer))==child and arity[consumer]==1,'only self same-hand unary read/write may alias');allowed+=1
  # Chance children are drawn from the immutable card table, not raw52slots.
  for child in cc:
   if level[child]==lev+1:ck(slots[child]not in outputs,'chance gathers never overlap current outputs')
 ck(allowed==len(pairs),'every selected alias and no other graph collision')
 for node in range(n):
  if level[node]<0:ck(slots[node]==0xffffffff,'unvisited sentinel unchanged')
  else:ck(slots[node]<newblocks,'all reached slots in range')
 ck(len({slots[n]for n in list(fold)+list(show)})==len(fold)+len(show),'all terminal cache rows distinct')
 output=H/f'case-{case:02d}-cfv-map.bin'
 with output.open('xb')as f:
  magic=b'D122-CFV-MAP1\0\0\0';ck(len(magic)==16,'map magic');f.write(magic);f.write(struct.pack('<IQQQQQ',case,n,oldscratch,nextslot,oldblocks,newblocks));slots.tofile(f)
 ck(output.stat().st_size==60+4*n,'complete map bytes')
 row={'case':case,'board':AR['cases'][case]['board'],'iso_requested':AR['cases'][case]['iso_requested'],'iso_active':AR['cases'][case]['iso_active'],'full_arenas':AR['cases'][case]['full_arenas'],'nodes':n,'levels':nl,'single_action_nodes':unary,'single_action_child_kind_counts':dict(childkinds),'action_child_arity_counts':dict(childarities),'disjoint_share_pairs':len(pairs),'naive_early_write_analysis':dict(hazard),'naive_cross_CTA_witnesses':witness,'old_scratch_rows':oldscratch,'new_scratch_rows':nextslot,'old_CFV_rows':oldblocks,'new_CFV_rows':newblocks,'CFV_payload_bytes_saved':(oldblocks-newblocks)*nhmax*4,'nh_max':nhmax,'maximum_live_group_count':peak,'all_graph_and_lifetime_invariants_pass':True,'original_raw_sha256':old.sha(path),'proposed_map_sha256':old.sha(output),'proposed_map_bytes':output.stat().st_size,'stage_lifetime_inventory':by_stage};old.save(H/f'case-{case:02d}.json',row);cases.append(row);print(json.dumps({k:row[k]for k in ['case','board','iso_active','disjoint_share_pairs','old_scratch_rows','new_scratch_rows','CFV_payload_bytes_saved']}),flush=True)
old.custody();admit=all(c['all_graph_and_lifetime_invariants_pass']and c['new_CFV_rows']<=c['old_CFV_rows']for c in cases)and any(c['iso_requested']and not c['full_arenas']and c['case']//4<2 and c['new_CFV_rows']<c['old_CFV_rows']for c in cases)
report={'id':'D122','at':old.now(),'status':'pass_retained_lifetime_model_admit_one_Rust_prototype'if admit else'decline_no_retained_storage_admission','checks':checks,'cases':cases,'all12cases_completed':True,'admit_Rust_prototype_only':admit,'compiler_or_GPU_or_solver_executions':0,'new_performance_measurements':0,'source_activated':False,'candidate_accepted':False,'source_main_live_PTX_custody_pass':True,'limits':'Exact retained integer graph/layout feasibility and source reasoning only; no newly compiled Rustplan, GPU numeric/state/FP/sign-zero/NaN/alias proof, actual CPU/peak/capacity, cache traffic or complete-cycle performance gain. Model stage-loop time not measured/scored. Naive fusion witnesses are potential unsynchronized read/write hazards, not observed GPU failures. Proposed model retains the original kernel schedule; no fusion implemented.'};old.save(H/'report.json',report)
for p in H.iterdir():
 if p.is_file()and p.suffix=='.json':pub.append(publish(p,H.name+'/'+p.name))
old.save(H/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'all_new_bulk_maps_retained_physically_on_S':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='D122');e.update(status='measured',correctness='Retained integer lifetimes/graph model pass',stage='One Rust layout prototype admitted'if admit else'Storage-model admission declined',reason='All12metadata cases decoded and explicit lifetime/graph/alias/root/terminal invariants checked. Shared single-action intervals can use original-schedule row reuse; naive early stores have potential cross-CTA conflicts. Storage savings are payload counts, no speed or GPUaccuracy result.');e['evidence'].append({'label':'Full retained lifetime/model result','url':'evidence/D122-cfv-lifetimes/report.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment=None,stage='Preparing a CFV lifetime-sharing prototype'if admit else'Investigating the next GPU optimization',activity='D122retained-data model completed. '+('One Rustphysical-CFVlayout prototype is admitted; original float kernels/schedule stay unchanged. 'if admit else'No storage prototype admitted. ')+'No GPU/new speed gain, accepted/live E051gain12.44%unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D122 retained CFV lifetime scout'not in raw
summary=[{k:c[k]for k in ['case','iso_active','disjoint_share_pairs','old_scratch_rows','new_scratch_rows','CFV_payload_bytes_saved','naive_early_write_analysis']}for c in cases]
entry=f'''\n\n### D122 retained CFV lifetime scout\n\nPrevious goal turn completed E075full819raw controls/builds/84units/3pairs, gained1.0195745992%but rainbow0.4663446165%slower2/3, rejected withoutrescue. Accepted162/main163/live/protected2PTX/idle/current lastprimaryB240revalidated. New source/all-ref audit found no unary-parent/child CFVinterval sharing. Currentplan uses2parity scratchpools and unique persistentterminal caches; immediate earlyparentwrites can collide with otherchildCTAs still reading sameparity grandchild inputs. D122retains concretepotential race witnesses, not observed GPUfailures.\n\nFreeze{old.sha(H/'protocol.json')}before decoding exactly12accepted E051D092metadata cases, no new planbuild/compiler/GPU/solver/timing/sourceactivation. Model selects only disjointone-actionparent/actionchildarity>=2pairs, uniqueactionparent and no chanceorbit childreference. It merges parent/child into one closedlifetime, retains every original kernel/float operation/update/schedule, assigns LIFOintervalcolors, relabelsrootto0and keeps distinct terminalcaches beyond scratch. Separate sorted percolorlifetime verification and actual graph read/write checks permit only sameparent/samehand one-actioninplace update; allother source dependencies remain nonoverlapping. No na1specialization,earlystore,uniformload,padding/pitch or worklistfamily is composed. No fusion implemented.\n\nAll12cases complete, {checks}integer/schema/lifetime/graph checks; status{report['status']}. Per-case{json.dumps(summary,separators=(',',':'))}. Payload counts are exact model CFVallocation deltas, not physical process/driver footprint or speed/traffic observations. Full maps/identities onS, source reportSHA{old.sha(H/'report.json')}. CPUmodel is not a compiled Rust/GPUproof androot is not external independent audit. CandidateRustsource not created by this scout.\n\nAllpublished JSON/protocol/source artifacts HTTPbyteverified, accepted162/main163/live/protected2PTXexact. No new compiler/kernel/solve/performance sample or adoption. E051accepted/deployed cumulative12.4372274192%and lastprimaryB240unchanged,goalactive. If admitted, implement exactlyone original-schedule interval-sharing Rustprototype and full metadata/FP/GPUstate/broad/material qualification before1%completecycle/strictfixture/fresh16/holdout/cumulative adoption; include added CPUtemporary/coloring costs. No claim from storage savings alone.\n''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: verify retained CFV lifetimes before storage reuse','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'status':report['status'],'checks':checks,'cases':12,'admit_one_Rust_prototype':admit,'accepted_gain_unchanged':True}),flush=True)
