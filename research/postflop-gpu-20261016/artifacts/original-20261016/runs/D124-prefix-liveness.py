"""Retained integer demand/encoding proof for selective showdown prefix materialization."""
from pathlib import Path
import array,collections,json,re,shutil,struct,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
assert sys.byteorder=='little' and array.array('I').itemsize==4;old.custody();assert not (R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
H=R/'runs/D124-prefix-liveness';assert not H.exists();H.mkdir();A=R/'runs/D092-action-arity-order';anchor=old.read(A/'report.json')
source=old.REPO/'crates/solver/src/gpu/kernels.cu';cu=source.read_text(encoding='utf-8');body=cu[cu.index('extern "C" __global__ void up_show('):cu.index('// Up sweep, chance nodes:')]
prefix_refs=re.findall(r'prefix\[[^\]]+\]',body);assert prefix_refs==['prefix[k]','prefix[k]','prefix[m_o - 1]','prefix[lb - 1]','prefix[ub - 1]']
assert len(re.findall(r'\bo_idx\[',body))==1 and len(re.findall(r'\bp_idx\[',body))==1
mod=old.REPO/'crates/solver/src/gpu/mod.rs';mo=mod.read_text(encoding='utf-8');assert mo.count('d_riv_idx: [up32(&plan.riv_sorted_idx[0])?, up32(&plan.riv_sorted_idx[1])?],')==1
assert mo.count('.arg(&self.d_riv_idx[p])')==2 and mo.count('.arg(&self.d_riv_idx[1 - p])')==2
history=subprocess.run(['git','log','--all','--format=%H','-G','prefix_needed|needed_prefix|prefix.*FLAG|PREFIX.*FLAG|0x80000000','--','crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/plan.rs'],cwd=old.REPO,text=True,capture_output=True,check=True);assert not history.stdout.strip()
paths=[Path(__file__),A/'report.json',A/'field-schema.json',A/'accepted-plan.rs',source,mod,old.REPO/'crates/solver/src/gpu/plan.rs',old.REPO/'crates/solver/src/game.rs',R/'runs/D123-node-array-initialization/report.json',C/'common_e051_live.py',C/'protected-main.json',*[A/'execution'/f'case-{i:02d}.bin'for i in range(12)]]
P={'id':'D124','at':old.now(),'scope':'Exactly12 retained accepted E051 plan metadata files, integer source/demand/encoding analysis. No compiler, CUDA/PTX, GPU kernels, solve/timing samples, or source activation.','input_sha256':{str(p):old.sha(p)for p in paths},'source_prefix_accesses':prefix_refs,'source_consumer_inventory':'Only up_show reads p_idx/o_idx (two sites), both training/evaluation callers use d_riv_idx, one constructor uploads owned plan.riv_sorted_idx arrays. No new persistent buffer or argument is planned. Private constructor can tag its owned sorted-index vectors in place; public GpuPlan::build, CPU save/query formats and all lengths/capacities remain unchanged.','local_all_ref_query':history.args,'local_all_ref_matches':history.stdout.splitlines(),'encoding':'Bit31 marks opponent prefix positions needed by the other player: every positive lb/ub boundary minus1, plus final m_o-1 when nonempty. Low31bits preserve the exact physical hand index. All production hands are unique two-card combos, at most1326. Mask both existing p_idx/o_idx hand dereferences. Same private u32 array payload and ABI27.','numerical_scope':'Only suppress per-chunk prefix[k]=acc stores and prefix[k]+=base operations at positions never subsequently read. Original ordered local accumulator, chunk totals/serial accumulation, every barrier, total/boundary/payout and card correction recurrence remain. Dead FP additions are not observable outputs. No E022 partial-scan truncation, E062 physical bank map, E059 predicate rewrite, E073 width narrowing, E076 CFV sharing or failed form composed.','fixed_admission':'All12 field/index/flag/demand/raw checks valid, existing-array widths and payload unchanged, >=20% of weighted prefix cells unused in each canonical flop case2/6. Passing admits one exact-source resource/control prototype only. Counts are structural opportunities, not speed, traffic, resource or material measurements. CPU tagging costs and every GPU raw/broad/1%/strict-fixture/fresh16/material/holdout/cumulative gate remain.','candidate_accepted':False};old.save(H/'protocol.json',P)
def publish(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(p)}
pub=[publish(H/'protocol.json',H.name+'/protocol.json'),publish(Path(__file__),H.name+'/audit.py')];old.save(H/'pre-execution-publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'retained_cases_decoded':0,'compiler_or_GPU_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']=='D124'for x in s['experiments']);s['experiments'].append({'id':'D124','at':old.now(),'title':'Showdown prefix read-demand and in-place index tags','kind':'diagnostic','status':'running','correctness':'Retained source/integer demand model underway','fixture':'12 accepted metadata layouts','stage':'Check unused prefix cells and tag safety','reason':'Every output reads only strength-boundary prefixes plus total. Model marking those positions in the high bit of existing sorted hand indices, with unchanged payload/ABI. No compiler, source activation, GPU kernel or timing.','accepted':False,'evidence':[{'label':'Frozen prefix-demand and encoding analysis','url':'evidence/D124-prefix-liveness/protocol.json'}]});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='D124',stage='D124 showdown prefix demand analysis',activity='D123 exact CPU initialization form closed after component loss. Inspect all12 retained layouts for unused shared-prefix cells and safe in-place hand-index bit tags. No new speed claim; E051 accepted/live gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
checks=0
def ck(v,label):
 global checks
 assert v,label;checks+=1
def vector(f,read=False):
 n,=struct.unpack('<Q',f.read(8));ck(n<100000000,'bounded encoded vector')
 if not read:f.seek(n*8,1);return None
 v=array.array('Q');v.fromfile(f,n);ck(len(v)==n,'complete vector');return v
def payload(v):ck(v[0]+1==len(v),'whole Vec framing');return v[1:]
def pair(v):
 ck(v[0]==2,'two player array framing');at=1;out=[]
 for _ in range(2):
  n=v[at];at+=1;out.append(v[at:at+n]);at+=n
 ck(at==len(v),'complete paired vectors');return out
selected=[1,15,32,43,44,45,46,48,49];cases=[];FLAG=1<<31;MASK=FLAG-1
for case in range(12):
 raw=A/'execution'/f'case-{case:02d}.bin';old.pin(raw,anchor['cases'][case]['raw_sha256']);fields={}
 with raw.open('rb')as f:
  ck(f.read(16)==b'D092-PLAN-RAW1\0\0','retained raw framing');ck(struct.unpack('<II',f.read(8))==(case,53),'case/schema');f.read(16)
  for field in range(53):
   ck(struct.unpack('<I',f.read(4))[0]==field,'field id');vector(f);vector(f);v=vector(f,field in selected);vector(f)
   if v is not None:fields[field]=v
  vector(f);vector(f);ck(f.read(1)==b'','complete raw endpoint')
 nh=fields[1];ck(len(nh)==3 and nh[0]==2 and max(nh[1:])<=1326,'legal physical combo domain');nh=list(nh[1:])
 shows=payload(fields[15]);river=payload(fields[32]);slots=fields[43][0]
 off,cnt,idx,lower,upper=[pair(fields[k])for k in [44,45,46,48,49]]
 weights=collections.Counter(int(river[n])for n in shows);ck(all(0<=slot<slots for slot in weights),'all reached show slots in range')
 tagged=[array.array('I',v)for v in idx];slot_rows=[];weighted=collections.Counter()
 for opponent in range(2):
  own=1-opponent;ck(len(off[opponent])==len(cnt[opponent])==slots,'slot span lengths')
  ck(len(idx[own])==len(lower[own])==len(upper[own]),'all own boundary vectors complete')
  ck(all(i<nh[opponent]and not(i&FLAG)for i in idx[opponent]),'original hand indices in range and high bit clear')
  for slot in range(slots):
   ob=int(off[opponent][slot]);m=int(cnt[opponent][slot]);pb=int(off[own][slot]);mp=int(cnt[own][slot]);ck(ob+m<=len(idx[opponent])and pb+mp<=len(idx[own]),'source spans in bounds')
   if m:tagged[opponent][ob+m-1]|=FLAG
   for i in range(pb,pb+mp):
    lb=int(lower[own][i]);ub=int(upper[own][i]);ck(0<=lb<=ub<=m,'every boundary in opponent span')
    if lb:tagged[opponent][ob+lb-1]|=FLAG
    if ub:tagged[opponent][ob+ub-1]|=FLAG
 # Independent set-of-consumers verifier, not the OR producer's bookkeeping.
 for opponent in range(2):
  own=1-opponent
  for slot in range(slots):
   ob=int(off[opponent][slot]);m=int(cnt[opponent][slot]);pb=int(off[own][slot]);mp=int(cnt[own][slot])
   demand={int(v)-1 for bound in [lower[own],upper[own]]for v in bound[pb:pb+mp]if v>0}
   if m:demand.add(m-1)
   bits={k for k,v in enumerate(tagged[opponent][ob:ob+m])if v&FLAG};ck(bits==demand,'exact prefix consumers match encoded flags')
   for k in range(m):ck((tagged[opponent][ob+k]&MASK)==idx[opponent][ob+k],'every tagged hand index decodes exactly')
   live=len(demand);count=weights[slot];weighted['all_prefix_cells']+=m*count;weighted['required_prefix_cells']+=live*count;weighted['unused_prefix_cells']+=(m-live)*count
   slot_rows.append({'opponent':opponent,'slot':slot,'opponent_hands':m,'own_hands':mp,'required_prefix_cells':live,'unused_prefix_cells':m-live,'reached_show_nodes':count})
 output=H/f'case-{case:02d}-tags.bin'
 with output.open('xb')as f:
  magic=b'D124-TAG-RAW1\0\0\0';ck(len(magic)==16,'tag raw magic');f.write(magic);f.write(struct.pack('<II',case,2))
  for p in range(2):
   original=array.array('I',idx[p]);f.write(struct.pack('<Q',len(original)));original.tofile(f);tagged[p].tofile(f)
 # Replay the complete saved tag images, including both original and encoded words.
 with output.open('rb')as f:
  ck(f.read(16)==magic and struct.unpack('<II',f.read(8))==(case,2),'saved raw tag framing')
  for p in range(2):
   n,=struct.unpack('<Q',f.read(8));original=array.array('I');original.fromfile(f,n);encoded=array.array('I');encoded.fromfile(f,n)
   ck(list(original)==list(idx[p])and encoded==tagged[p],'saved full original/tagged vectors exact')
   ck(all((a&MASK)==b for a,b in zip(encoded,original)),'saved low31bit semantic decode exact')
  ck(f.read(1)==b'','complete raw tag endpoint')
 ck(output.stat().st_size==40+8*sum(len(v)for v in idx),'full raw tag geometry')
 unused_pct=100*weighted['unused_prefix_cells']/weighted['all_prefix_cells'] if weighted['all_prefix_cells'] else 0
 row={'case':case,'board':anchor['cases'][case]['board'],'iso_requested':anchor['cases'][case]['iso_requested'],'iso_active':anchor['cases'][case]['iso_active'],'full_arenas':anchor['cases'][case]['full_arenas'],'river_slots':slots,'physical_hands':nh,'show_nodes':len(shows),'weighted_prefix_counts':dict(weighted),'weighted_unused_prefix_pct':unused_pct,'skippable_prefix_local_stores':weighted['unused_prefix_cells'],'skippable_dead_offset_adds':weighted['unused_prefix_cells'],'skippable_offset_read_modify_writes':weighted['unused_prefix_cells'],'sorted_index_words':sum(len(v)for v in idx),'original_device_index_bytes':4*sum(len(v)for v in idx),'encoded_device_index_bytes':4*sum(len(v)for v in idx),'new_persistent_buffers':0,'global_ABI_arguments':27,'all_index_demand_raw_invariants_pass':True,'raw_tags_sha256':old.sha(output),'raw_tags_bytes':output.stat().st_size,'retained_raw_sha256':old.sha(raw),'slots':slot_rows};old.save(H/f'case-{case:02d}.json',row);cases.append(row)
 print(json.dumps({k:row[k]for k in ['case','board','iso_active','show_nodes','weighted_unused_prefix_pct','sorted_index_words']}),flush=True)
old.custody();admit=all(c['all_index_demand_raw_invariants_pass']and c['original_device_index_bytes']==c['encoded_device_index_bytes']for c in cases)and all(cases[i]['weighted_unused_prefix_pct']>=20 for i in [2,6])
report={'id':'D124','at':old.now(),'status':'admit_one_selective_prefix_resource_prototype'if admit else'decline_retained_prefix_liveness_admission','checks':checks,'cases':cases,'all12cases_completed':True,'admit_one_resource_prototype_only':admit,'compiler_or_GPU_or_solver_executions':0,'new_performance_measurements':0,'source_activated':False,'candidate_accepted':False,'source_main_live_PTX_custody_pass':True,'limits':'Exact retained integer demand/index/tag/byte-footprint model and source consumer inventory only. No newly compiled Rust tagging helper, emitted mask/dead-store/PTX proof, floating numerical/state/NaN, resource/material/CPU cost or complete-cycle gain. Counts do not prove dynamic traffic or speed. Root verifier is not an external independent audit. No unrelated failed source form is composed.'};old.save(H/'report.json',report)
for p in H.iterdir():
 if p.is_file()and p.suffix=='.json':pub.append(publish(p,H.name+'/'+p.name))
old.save(H/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'all_bulk_raw_tag_images_retained_physically_on_S':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='D124');e.update(status='measured',correctness='All12 retained demand/index/raw invariants pass',stage='One resource prototype admitted'if admit else'Closed: prefix liveness admission declined',reason='All12 layouts decoded; exact original hand indices and demanded prefix positions survive high-bit tagging with unchanged u32 payload/ABI27. Unused weighted prefix counts are structural only. No CUDA, math, resource, actual footprint or speed result.');e['evidence'].append({'label':'Full retained prefix-demand/tag result','url':'evidence/D124-prefix-liveness/report.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment=None,stage='Preparing selective-prefix resource controls'if admit else'Investigating the next GPU optimization',activity='D124 retained demand analysis completed. '+('One selective prefix-materialization prototype admitted; no new persistent buffer or ABI argument planned. 'if admit else'No prototype admitted. ')+'No new speed gain; E051 accepted/live gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();ck(b'### D124 showdown prefix demand and index tags'not in raw,'ledger entry absent')
summary=[{k:c[k]for k in ['case','iso_active','weighted_prefix_counts','weighted_unused_prefix_pct','sorted_index_words']}for c in cases]
entry=f'''

### D124 showdown prefix demand and index tags

Previous goal turn completed D123's exact53-field CPU direct-append initialization screen, declined after canonical CPU-plan saving-3.6194ms and failed paired guards; no variants/resampling. Accepted162/main163/live/protected2PTX and idle state revalidated, last primary B243. New source search found up_show writes/offset-adds every shared-prefix cell but consumers read only lower/upper strength boundaries and final total. Original two sorted hand-index dereferences are the only consumers of private d_riv_idx in CUDA; both training/evaluation callers share them, one constructor owns/uploads the arrays. Bounded all-ref query found no prefix-demand/index-tag implementation. No E022 unused chunk-total truncation, E062 bank map, E059 predicate arithmetic, E073 width or E076 CFV layout composed or reopened.

Freeze {old.sha(H/'protocol.json')} before decoding exactly12 retained accepted D092 metadata cases. For each opponent/slot, bit31 of its existing u32 sorted index marks every other-player positive lb/ub boundary minus1 and final m-1. Legal1326 physical-hand domain leaves highbit free; mask low31bits at both existing p_idx/o_idx hand dereferences. Planned host constructor tags owned local vectors in place before original uploads: no extra persistent/temporary array, buffer, argument, payload, public-plan build/schema/save or launch change. Proposed kernel keeps all ordered local/chunk recurrences/barriers, suppressing only unread prefix stores and their dead offset-add read-modify-writes. Source/integer model is not compiled numerical proof or a CPU cost claim.

All12 demand/index/whole saved-image checks pass, {report['checks']} checks. Independent set-of-consumers comparison verifies every required prefix flag and exact decoding of each original hand index; original+tagged raw vectors retained onS. Per-case {json.dumps(summary,separators=(',',':'))}. Admission fixed before data: unchanged index payload and >=20% weighted unused prefix cells in both canonical flops, plus all12 validity checks. Status {report['status']}; report SHA {old.sha(H/'report.json')}. Counts are structural opportunities, not dynamic traffic, speed, actual physical peak or allocator/resource observations. Root is not external independent audit.

No compiler, CUDA/PTX, GPU kernel, solve/timing sample or source activation. All published protocol/source/JSON HTTP byte verified; accepted162/main163/live/protected2PTX exact. No new E077 source or primary IDs yet. If admitted, exactly one original selective-materialization resource/PTX prototype, compiled host integer packing controls and full raw GPU comparisons precede fixed1%/strict-fixture timing; broad/F32/state/menu/save/resume/continuation/material/fresh16/holdout/cumulative remain before acceptance. CPU in-place tagging costs remain inside whole clocks. E051 accepted/deployed cumulative12.4372274192% and last primary B243 unchanged; goal active.
''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: prove showdown prefix demand and exact index tags','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'status':report['status'],'checks':report['checks'],'admit_one_resource_prototype':admit,'accepted_gain_unchanged':True}),flush=True)
