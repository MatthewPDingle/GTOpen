"""Retained accepted-tree ownership census for fold computation inside its parent."""
from pathlib import Path
import array,collections,json,shutil,struct,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert sys.byteorder=='little'and not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
H=R/'runs/D128-fold-parent';assert not H.exists();H.mkdir();A=R/'runs/D092-action-arity-order';AR=old.read(A/'report.json');old.pin(A/'accepted-plan.rs',old.BASE['crates/solver/src/gpu/plan.rs'])
raws=[A/'execution'/f'case-{i:02d}.bin'for i in range(12)]
history=subprocess.run(['git','log','--all','--format=%H','-G','inline.fold|fused.fold|fold.fus|up_action_fold|action_fold|fold_child','--','crates/solver/src/gpu'],cwd=old.REPO,text=True,capture_output=True,check=True);assert not history.stdout.strip()
old.save(H/'history.json',{'at':old.now(),'query':history.args,'all_ref_matches':history.stdout.splitlines(),'scope':'Bounded local-all-ref and retained ledger search, not remote exhaustive novelty.','distinct_from_closed_forms':'D122/E076 unary CFV lifetime layout retained original kernels and is closed; this form changes no CFV layout or allocation, instead executes each original fold producer in its unique action parent block. No E035 zero predicate, E039chance fusion, E053sorted-prefix fusion, E054early-store or load/cache/helper/arity rescue.'})
paths=[Path(__file__),A/'report.json',A/'field-schema.json',A/'accepted-plan.rs',*raws,H/'history.json',C/'common_e051_live.py',C/'protected-main.json',*[old.REPO/'crates/solver/src/gpu'/n for n in ['plan.rs','mod.rs','kernels.cu','continuation.rs','continuation_storage.rs','continuation_projection.cu','continuation_storage_copy.cu']],old.REPO/'crates/solver/src/tree.rs']
P={'id':'D128','at':old.now(),'input_sha256':{str(p):old.sha(p)for p in paths},'scope':'Exactly12accepted E051retained full metadata dumps, baseline arm only, source/integer ownership analysis. No compiler/native kernel/new solver/timing/source activation.','fixed_checks':['Every reached fold has exactly one reached direct action parent, no fold root/chance parent, at most one fold child per action, child player equals parent actor and depth increases1.','Every actual fold CFV row is unique and disjoint from all reached action/chance/show outputs, every child address and both opponent reach rows bounded; no actual fold has another consumer.','All fold nodes can be privately marked node_na=-1 without marking any action/worklist/pack/transport node. Original public GpuPlan stays unchanged; constructor-owned existing upload vector only.','Record every parent/fold pair, actor/arity/level incidence and removed training-only fold launch/block inventory. No traffic/time gain inferred from counts. Evaluation fold launch retained.'],'proposed_source':'One fixed fused producer before the unchanged up_action helper. Existing ascending child loop identifies private -1 fold child, runs exact original fold arithmetic/reduction/shared copy and writes the same cached CFV row, one final CTA barrier then existing action helper/dispatch unchanged. Same128default/1..256controls and all supported hands<=1326. Static shared1326+52+256floats, dynamic0 unchanged. No extra global/CPU payload or changed learning arithmetic. Host training-only fold launches removed; evaluation path unchanged. Opponent reach fully built before up sweep and immutable until next down; original fold address/payout/CFV ownership retained.','admission':'Require every declared invariant all12cases and nonzero fold exposure in each canonical fixture; only admits one off-tree source/compiler feasibility trial. Numerical/full raw/F32/state/menu/save/resume/continuation/material/complete-cycle1%/strictfixture/fresh16/holdout/cumulative remain. Static shared/occupancy tradeoff must be visible; new local/spill or lost maxthreads/dynamic capacity fails before numerical work. No source/placement/thread/arity/marker/threshold rescue after actual failed qualification.','candidate_accepted':False};old.save(H/'protocol.json',P)
def publish(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes()
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(p)}
pub=[publish(H/n,H.name+'/'+n)for n in ['history.json','protocol.json']];pub.append(publish(Path(__file__),H.name+'/audit.py'));old.save(H/'pre-execution-publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'retained_cases_decoded':0,'compiler_or_GPU_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']=='D128'for x in s['experiments']);s['experiments'].append({'id':'D128','at':old.now(),'title':'Fold producer inside its unique action parent','kind':'diagnostic','status':'running','correctness':'Retained graph/address/ownership census underway','fixture':'12accepted metadata cases, both actors/iso/full+compact','stage':'Source and exact integer ownership model','reason':'Check moving each unchanged fold computation into its unique parent CTA while retaining cached CFV rows/evaluation and all action arithmetic. No speed or GPUaccuracy claim.','accepted':False,'evidence':[{'label':'Frozen source/ownership census','url':'evidence/D128-fold-parent/protocol.json'}]});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='D128',stage='D128 fold-parent ownership census',activity='D127closed on CPU cost. Investigating a distinct GPU launch/computation fusion; original fold arithmetic/CFV layout/action update and evaluation path retained. Accepted/live E051gain12.44%unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
checks=0
def ck(v,label):
 global checks
 assert v,label;checks+=1
def vector(f,read=False):
 raw=f.read(8);ck(len(raw)==8,'vector header');n,=struct.unpack('<Q',raw);ck(n<100000000,'bounded vector')
 if not read:f.seek(n*8,1);return None
 v=array.array('Q');v.fromfile(f,n);ck(len(v)==n,'full vector');return v
def payload(v):ck(v[0]+1==len(v),'vector framing');return v[1:]
def pair(v):
 ck(v[0]==2,'pair framing');a=v[1];x=v[2:2+a];b=v[2+a];y=v[3+a:];ck(len(y)==b,'second pair length');return[x,y]
def spanlist(v,nl):ck(v[0]==nl and len(v)==1+2*nl,'span framing');return[(int(v[1+2*i]),int(v[2+2*i]))for i in range(nl)]
def owner_contract(parent_rows,folds,foldslots,other_slots):
 counts=collections.Counter(c for _,c in parent_rows)
 return set(counts)==set(folds)and all(n==1 for n in counts.values())and len(set(foldslots))==len(folds)and not set(foldslots).intersection(other_slots)
controls=[([(0,1)],[1],[7],[0],True), ([(0,1),(2,1)],[1],[7],[0],False), ([],[1],[7],[0],False), ([(0,1),(2,3)],[1,3],[7,7],[0],False), ([(0,1)],[1],[7],[7],False), ([(0,1),(2,3)],[1],[7],[0],False)]
for rows,folds,slots,other,expected in controls:ck(owner_contract(rows,folds,slots,other)==expected,'positive/negative owner fixture')
selected=[0,1,2,3,5,6,11,12,13,14,15,16,20,23,24,27,34,35,36,37];cases=[]
for case,path in enumerate(raws):
 old.pin(path,AR['cases'][case]['raw_sha256']);fields={};startchecks=checks
 with path.open('rb')as f:
  ck(f.read(16)==b'D092-PLAN-RAW1\0\0','magic');ck(struct.unpack('<II',f.read(8))==(case,53),'case/schema');ck(len(f.read(16))==16,'struct sizes')
  for field in range(53):
   ck(struct.unpack('<I',f.read(4))[0]==field,'field identity');vector(f);vector(f);v=vector(f,field in selected);vector(f)
   if v is not None:fields[field]=v
  kinds=payload(vector(f,True));children=payload(vector(f,True));ck(f.read(1)==b'','complete endpoint')
 nl=int(fields[0][0]);n=int(fields[3][0]);nh=list(fields[1][1:]);nhmax=int(fields[2][0]);blocks=int(fields[37][0]);ck(len(nh)==2 and max(nh)==nhmax<=1326,'supported hand bound')
 families=[(payload(fields[fi]),spanlist(fields[si],nl))for fi,si in[(5,6),(11,12),(13,14),(15,16)]];actions,chance,fold,show=[x[0]for x in families]
 arity=payload(fields[24]);player=payload(fields[23]);cs=payload(fields[27]);slots=payload(fields[36]);reach=pair(fields[34]);reachblocks=list(fields[35][1:]);cc_child=payload(fields[20]);ck(len(kinds)==len(arity)==len(player)==len(cs)==len(slots)==n and all(len(x)==n for x in reach),'all node arrays')
 level=array.array('i',[-1])*n
 for kind,(nodes,spans)in enumerate(families):
  at=0
  for lev,(lo,count)in enumerate(spans):
   ck(lo==at and lo+count<=len(nodes),'contiguous bounded spans');at+=count
   for node in nodes[lo:lo+count]:ck(node<n and level[node]==-1 and kinds[node]==kind and slots[node]<blocks,'reached kind/row');level[node]=lev
  ck(at==len(nodes),'complete worklist')
 foldset=set(fold);ck(0 not in foldset and len(foldset)==len(fold),'no fold root or duplicate')
 ck(not foldset.intersection(cc_child),'no chance fold consumer')
 parent_rows=[];parent_by_fold={};fold_by_arity=collections.Counter();fold_by_actor=collections.Counter();action_levels=collections.Counter();parents_with_fold=0;all_children=0
 for parent in actions:
  ck(0<arity[parent]<=255 and player[parent]in[0,1]and cs[parent]+arity[parent]<=len(children),'action shape bounds');count=0;action_levels[level[parent]]+=1
  for child in children[cs[parent]:cs[parent]+arity[parent]]:
   ck(child<n and level[child]==level[parent]+1 and slots[child]<blocks,'child level/row');all_children+=1
   if kinds[child]!=2:continue
   ck(child in foldset and arity[child]==0 and player[child]==player[parent],'fold kind/actor/arity');count+=1;parent_rows.append((int(parent),int(child)));parent_by_fold[int(child)]=int(parent);fold_by_arity[int(arity[parent])]+=1;fold_by_actor[int(player[parent])]+=1
   for p in[0,1]:ck(reach[1-p][child]<reachblocks[1-p],'both original opponent reach addresses bounded')
  ck(count<=1,'at most one fold child');parents_with_fold+=bool(count)
 foldslots=[slots[x]for x in fold];other_slots=set(slots[x]for nodes in[actions,chance,show]for x in nodes)
 ck(owner_contract(parent_rows,fold,foldslots,other_slots),'all fold ownership and CFV writes disjoint');ck(len(parent_rows)==len(fold)>0,'complete nonzero fold exposure')
 pairs=array.array('I')
 for parent,child in parent_rows:pairs.extend([parent,child])
 rawmap=H/f'case-{case:02d}-parent-fold.bin'
 with rawmap.open('xb')as f:f.write(b'D128-FOLD-RAW1\0\0');f.write(struct.pack('<IIQ',case,2,len(parent_rows)));pairs.tofile(f)
 ck(rawmap.stat().st_size==32+8*len(parent_rows),'map framing')
 result={'case':case,'board':AR['cases'][case]['board'],'fixture_index':AR['cases'][case]['fixture_index'],'iso_requested':AR['cases'][case]['iso_requested'],'full_arenas':AR['cases'][case]['full_arenas'],'nodes':n,'nh':nh,'action_nodes':len(actions),'fold_nodes':len(fold),'fold_parents':parents_with_fold,'action_parent_incidence_pct':parents_with_fold/len(actions)*100,'original_training_fold_launches_per_sweep':sum(count>0 for _,count in families[2][1]),'original_training_fold_blocks_per_sweep':len(fold),'fold_by_parent_arity':dict(fold_by_arity),'fold_by_actor':dict(fold_by_actor),'action_levels':dict(action_levels),'all_actual_action_child_addresses_checked':all_children,'root_checks':checks-startchecks,'pair_map':str(rawmap),'pair_map_bytes':rawmap.stat().st_size,'pair_map_sha256':old.sha(rawmap),'accepted_raw_sha256':AR['cases'][case]['raw_sha256'],'every_fold_unique_parent_and_disjoint_row_pass':True,'zero_new_native_or_GPU_executions':True};old.save(H/f'case-{case:02d}.json',result);cases.append(result);print(json.dumps({k:result[k]for k in['case','board','action_nodes','fold_nodes','action_parent_incidence_pct','root_checks']}),flush=True)
admit=all(x['every_fold_unique_parent_and_disjoint_row_pass']and x['fold_nodes']>0 for x in cases)and len(cases)==12
report={'id':'D128','at':old.now(),'status':'admit_one_offtree_fold_parent_source_and_resource_trial'if admit else'decline_fold_parent_structural_prerequisite','protocol_sha256':old.sha(H/'protocol.json'),'cases':cases,'root_checks':checks,'owner_control_fixtures':len(controls),'admit_one_source_resource_trial':admit,'candidate_accepted':False,'source_activated':False,'compiler_GPU_solver_new_timing_executions':0,'limits':'Exact finite retained metadata/source ownership model, not GPU arithmetic equivalence, whole-device peak/capacity, dynamic traffic/time headroom or speed. Original fold sum tree/element order/payout/row write must remain byte-exact, then original action helper. Extra shared/global barriers and parent-side metadata/shared occupancy can erase benefit. New fixed static shared6536B per action CTA at most1326opponent hands, dynamic0, must pass compiled feasibility/no new spill/default fit before numerical work. Host/eval/continuation tagging and every actual buffer image need compiled controls. All1%/strictfixture/fresh16/exact/broad/material/holdout/cumulative gates remain.'};old.save(H/'report.json',report)
for p in H.iterdir():
 if p.is_file()and p.suffix=='.json':pub.append(publish(p,H.name+'/'+p.name))
old.custody();assert not(R/'gpu-run.lock').exists();old.save(H/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'bulk_pair_maps_retained_physically_S':True,'source_main_live_PTX_custody_pass':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='D128');e.update(status='measured',correctness='All12accepted graph/ownership models and6contract controls pass',stage='One off-tree source/resource trial admitted'if admit else'Structural prerequisite declined',reason='Every reached fold has one action parent, one disjoint cached CFV row and bounded original reach inputs; no chance/root/other consumer. Counts show structural exposure only; no GPU, numerical or speed result.');e['evidence'].append({'label':'Full12case ownership census and source obligations','url':'evidence/D128-fold-parent/report.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment=None,stage='Preparing fold-parent GPU source/resource trial'if admit else'Investigating the next GPU optimization',activity='D128retained ownership census complete; '+('one fixed parent-CTA fold producer prototype admitted. 'if admit else'no source trial admitted. ')+'No new accepted gain; E051accepted/deployed12.44% and lastprimaryB246unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D128 fold producer parent ownership census'not in raw
entry=f'''

### D128 fold producer parent ownership census

Previous goal turn completed D127 exactly6CPUprocesses/full88owned image controls, rejected despite122.9617ms component saving because both large cases increased summed CPU roughly3x. No thread/chunk/threshold/source rescue. Accepted162/main163/live/protected2PTX and idle state revalidated; lastprimaryB246. D087retained ordinary GPUtrace action-update family35.6%,fold8.5% motivates distinct source inspection, not timing headroom. D128localallref/ledger search found no parent-fold producer fusion. D122/E076changed CFVstorage only and remains closed; no unary fusion/zero predicate/chance/sorted-prefix/early-store/load/helper/arity forms composed or reopened.

Frozen source/integer census {old.sha(H/'protocol.json')} reads baseline arm only of12accepted D092full raw metadata dumps, full rawSHAchecked, no compiler/native kernel/solver/timing/source activation. All reached folds must have exactlyone direct action parent, no root/chance/other consumer, at mostonefold/action, samefoldplayer/parentactor, depth+1. All actual fold cachedCFVrows unique/disjoint from action/chance/showwrites and both original opponent-reach addresses bounded. All cases pass, {checks}checks and6positive/negative owner fixtures. Full original parent/fold u32pairs retained physicallyS, percase hashes/reports published. Case summaries {json.dumps([{k:x[k]for k in['case','board','action_nodes','fold_nodes','action_parent_incidence_pct','original_training_fold_launches_per_sweep']}for x in cases],separators=(',',':'))}. Counts are structural exposure, not dynamic traffic/time/gain.

One fixed source/resource form admitted: existing private uploaded node_na marks only reached folds-1, no public plan/schema/new payload. Before unchanged up_actionhelper/dispatch, CTAidentifies its one foldchild, executes exact original foldcopy/card/total reductions/payout/fullrowwrite, final CTAbarrier. Training-only separatefold launches removed; evaluation foldpath unchanged. Original down completes before up, reach immutable throughout, terminalCFVrows disjoint/persistent; delaying this producer1level has no otherconsumer. All other action/learning expressions/order retained. Staticshared1326+52+256floats(6536B),dynamic0; extra metadata/shared cost may erase gain. Local/spill/maxthreads/defaultfit/actualoccupancy/ABImechanism and otherentry guards precede any numerical run. Hostcompiledtag/continuation/rawGPU/fullcycle1%/strictfixture/fresh16/broad/state/F32/menu/save/resume/material/holdout/cumulative stillrequired. ReportSHA {old.sha(H/'report.json')}. No current production change/adoption/speed or no-tradeoff claim; sourceform cannot be tuned/resampled after actualfailedqualification.

All{len(pub)}JSON/codeprotocol/history/reportartifacts HTTPbyteverified; bulk maps S, no GPUlock/ownednativechild. Accepted162/main163/live/protected2PTX unchanged; accepted/deployed E051cumulative12.4372274192% unchanged. Goalactive; source/compilerresourceprototype next.
''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: prove fold-child ownership for one parent-block producer trial','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'status':report['status'],'checks':checks,'cases':len(cases),'report_sha256':old.sha(H/'report.json')}),flush=True)
