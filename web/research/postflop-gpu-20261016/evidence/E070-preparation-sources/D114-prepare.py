"""D114: freeze a distinct lossless global node-metadata encoding; no GPU launch."""
from pathlib import Path
import array,hashlib,json,re,shutil,struct,subprocess,sys,urllib.request,difflib
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();assert shutil.disk_usage(ROOT).free>67*1024**3
H=ROOT/'runs/D114-node-metadata';S=ROOT/'runs/E070-source';assert not H.exists() and not S.exists();H.mkdir();S.mkdir()
A=ROOT/'runs/D092-action-arity-order';AR=old.read(A/'report.json');repo=old.REPO
source_paths=[repo/'crates/solver/src/gpu'/n for n in ['kernels.cu','mod.rs','plan.rs','continuation.rs','continuation_storage.rs','continuation_capacity.rs']]+[repo/'crates/solver/src/tree.rs']
raws=[A/'execution'/f'case-{i:02d}.bin' for i in range(12)]
old.save(H/'protocol.json',{'id':'D114','at':old.now(),'scope':'Source/ABI ownership audit and exact integer encoding only. No native GPU/compiler or timing in this phase.','input_sha256':{str(p):old.sha(p) for p in [Path(__file__),*source_paths,A/'report.json',*raws]},'encoding':'u16(player)<<8 | u16(num_children); low8 bits action count, high8 player. Both fields originate as u8.','fixed_cases':'All65536byte pairs plus every node in all12retained source-matched accepted E051plan cases. No extra sampling/variants.','prospective_resource_rule':'For this new immutable encoding, the intended global payload difference is8*N to2*N bytes, preserving every logical node/value and all other allocations. Public CPU GpuPlan fields and conservative budget formulas remain unchanged. D108per-kernel feasibility gates still apply: no new local/spill bytes, no dynamic reservation increase, no lower maxthreads, default limit fit and positive64/128/256occupancy. ABI/schema/caller and emitted narrow-load proof required; all other5entry bodies exact.','material_costs':'One planned2*N-byte temporary CPU packing vector may increase peak/CPU cost. Must measure actual whole-process CPU/host+GPU peaks/responsiveness/capacity and broad compatibility before adoption; reduced payload is not proof of no tradeoff or speed.','unchanged_acceptance':'Unrounded>=1%complete-solve, strict fixture guard, separately frozen fresh16, exactness/broad/material/holdout/fresh-original cumulative. No previous failures reopened.','reserve_bytes':66*1024**3,'expected_new_raw_bytes_at_most':1024**3,'candidate_accepted':False})
tree=(repo/'crates/solver/src/tree.rs').read_text(encoding='utf-8');plan=(repo/'crates/solver/src/gpu/plan.rs').read_text(encoding='utf-8');assert 'pub player: u8,' in tree and 'pub num_children: u8,' in tree;assert 'node_player[ni] = node.player as i32;' in plan and 'node_na[ni] = node.num_children as i32;' in plan
history=subprocess.run(['git','log','--all','--format=%H','-G','(node_attrs|packed_node|node_packed|action_meta|packed_actor|actor_arity)','--','crates/solver/src/gpu'],cwd=repo,text=True,capture_output=True,check=True)
old.save(H/'history.json',{'at':old.now(),'git_query':history.args,'local_all_ref_matches':history.stdout.splitlines(),'scope':'Bounded current ledger/preserved CUDA source and local all-ref postflop GPU history; not exhaustive remote novelty.','excluded_closed_families':['E003mutable noalias','E046chance-record interleaving','E048card-identity membership','E052show shared-position narrowing','E056action arity order','E069show work order']});assert not history.stdout.strip(),'review historical metadata matches before proceeding'
checks=0

def ck(value,label):
 global checks
 assert value,label;checks+=1
raw=bytearray(b'D114-U8PAIR-V1\0\0');ck(len(raw)==16,'algebra magic')
for player in range(256):
 for na in range(256):
  packed=(player<<8)|na;ck(0<=packed<=65535 and packed>>8==player and packed&255==na,'all byte pairs lossless');raw.extend(struct.pack('<BBH',player,na,packed))
(H/'all-byte-pairs.bin').write_bytes(raw)

def vector(f,read=False):
 size=struct.unpack('<Q',f.read(8))[0];ck(size<100000000,'bounded words')
 if not read:f.seek(size*8,1);return None
 v=array.array('Q');v.fromfile(f,size);ck(len(v)==size,'complete vector');return v
cases=[]
for i,path in enumerate(raws):
 old.pin(path,AR['cases'][i]['raw_sha256']);fields={}
 with path.open('rb') as f:
  ck(f.read(16)==b'D092-PLAN-RAW1\0\0','baseline framing');ck(struct.unpack('<II',f.read(8))==(i,53),'case/schema');f.read(16)
  for field in range(53):
   ck(struct.unpack('<I',f.read(4))[0]==field,'field id');vector(f);vector(f);v=vector(f,field in [3,23,24]);vector(f)
   if v is not None:fields[field]=v
  vector(f);vector(f);ck(f.read(1)==b'','raw full endpoint')
 n=fields[3][0];player=fields[23];na=fields[24];ck(player[0]==na[0]==n and len(player)==len(na)==n+1,'full node field geometry')
 out=H/f'case-{i:02d}-packed.bin';ck(len(b'D114-NODE-PACK1\0')==16,'node magic')
 with out.open('xb') as f:
  f.write(b'D114-NODE-PACK1\0');f.write(struct.pack('<IQ',i,n));chunk=bytearray()
  for p,a in zip(player[1:],na[1:]):
   ck(p<=255 and a<=255,'all retained values fit byte source types');v=(p<<8)|a;ck(v>>8==p and v&255==a,'exact retained decode');chunk.extend(struct.pack('<BBH',p,a,v))
   if len(chunk)>=65536:f.write(chunk);chunk.clear()
  f.write(chunk)
 ck(out.stat().st_size==28+4*n,'full raw node count')
 cases.append({'id':i,'nodes':n,'baseline_metadata_payload_bytes':8*n,'candidate_metadata_payload_bytes':2*n,'payload_bytes_saved':6*n,'temporary_host_pack_bytes':2*n,'raw_source_sha256':old.sha(path),'packed_raw_sha256':old.sha(out),'packed_raw_bytes':out.stat().st_size})
base=(repo/'crates/solver/src/gpu/kernels.cu').read_bytes();text=base.decode().replace('\r\n','\n');candidate=text;edits=[]

def fragment(source,name):
 m=re.search(r'\bvoid\s+'+re.escape(name)+r'\s*\(',source);assert m;start=source.rfind('\n',0,m.start())+1;left=source.index('{',m.end());depth=1;end=left+1
 while depth:
  if source[end]=='{':depth+=1
  elif source[end]=='}':depth-=1
  end+=1
 return source[start:end]
for name in ['down_action_impl','down_action','up_fold','up_action_impl','up_action','up_action_eval']:
 before=fragment(candidate,name);after=before
 after,n=re.subn(r'const int\* __restrict__ node_player,\s*const int\* __restrict__ node_na,','const unsigned short* __restrict__ node_attrs,',after);ck(n==(0 if name=='up_fold' else 1),'one metadata parameter pair')
 if name=='up_fold':after=after.replace('const int* __restrict__ node_player,','const unsigned short* __restrict__ node_attrs,')
 after=after.replace('node_player, node_na,','node_attrs,').replace('node_na[nodes[start + blockIdx.x]]','(int)(node_attrs[nodes[start + blockIdx.x]] & 0xFFu)').replace('node_na[n]','(int)(node_attrs[n] & 0xFFu)').replace('node_player[n]','(int)(node_attrs[n] >> 8)')
 ck('node_player' not in after and 'node_na' not in after and before!=after,'all changed reads mapped')
 ck(candidate.count(before)==1,'unique function fragment');candidate=candidate.replace(before,after,1);edits.append((name,before,after))
reverse=candidate
for name,before,after in reversed(edits):ck(reverse.count(after)==1,'unique reverse fragment');reverse=reverse.replace(after,before,1)
ck(reverse==text,'mechanical reverse exactly accepted source')
entries=['copy_root','down_action','down_chance','up_fold','up_show','up_chance','up_action','copy_span','up_action_eval'];changed=['down_action','up_fold','up_action','up_action_eval'];ck(all(fragment(text,n)==fragment(candidate,n) for n in entries if n not in changed),'all5other source entries exact')
encoded=candidate.replace('\n','\r\n' if b'\r\n' in base else '\n').encode();(S/'baseline.cu').write_bytes(base);(S/'candidate.cu').write_bytes(encoded);(S/'candidate.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),encoded.decode().splitlines(True),fromfile='E051/kernels.cu',tofile='E070/kernels.cu')),encoding='utf-8',newline='')
callers=[]
for p in source_paths:
 if p.suffix!='.rs':continue
 for i,line in enumerate(p.read_text(encoding='utf-8').splitlines()):
  if 'd_node_player' in line or 'd_node_na' in line:callers.append({'path':str(p.relative_to(repo)),'line':i+1,'text':line.strip()})
old.save(S/'manifest.json',{'id':'E070','at':old.now(),'source_stage':'CUDAoff-tree only; host integration not yet implemented','accepted_source':'E051','candidate_owned_sha256':{'crates/solver/src/gpu/kernels.cu':old.sha(S/'candidate.cu')},'changed_entries':changed,'other5source_entries_exact':True,'mechanical_reverse_pass':True,'source_activated':False,'gpu_application_launches':0,'solver_executions':0})
old.save(H/'report.json',{'id':'D114','at':old.now(),'status':'pass_byte_domain_and_retained_node_encoding','checks':checks,'byte_pair_cases':65536,'retained_node_cases':cases,'total_retained_nodes':sum(c['nodes'] for c in cases),'packed_raw_bytes':sum(c['packed_raw_bytes'] for c in cases),'algebra_raw_sha256':old.sha(H/'all-byte-pairs.bin'),'source_node_types':'player:u8,num_children:u8; plan fields copy these exactly into i32','encoding':'u16(player)<<8 | u16(num_children)','public_CPU_plan_unchanged':True,'planned_device_representation':'Replace private d_node_player:i32 and d_node_na:i32 by one d_node_attrs:u16. Kernel low8bits decode arity; high8bits decode player. All256values preserved for both.','remaining_integrated_files':['gpu/mod.rs','gpu/continuation.rs','gpu/continuation_storage.rs','gpu/continuation_capacity.rs'],'host_caller_inventory':callers,'remaining_host_contract':'All eager/training/evaluation/reference/continuation/stored-state down_action callers must replace the pair in-order by the packed buffer; fold replaces only player pointer. Update actual metadata-capacity accounting to2*N, retain conservative public budget formula and logical array lengths. Verify CUDA/RustABI before any integrated native launch. No disk/save schema changes.','prospective_resource_scope':'Only this deliberately smaller immutable representation is exempt from byte-identical payload; supported logical capacity and all other buffers/shapes must match. No extra local/spill, dynamic shared increase or reduced maxthreads. All5other PTXentry bodies and expected4ABI transforms must pass. Existing exactness/performance/material gates unchanged.','candidate_cuda_sha256':old.sha(S/'candidate.cu'),'all_source_and_main_live_ptx_unchanged':True,'new_GPU_processes':0,'new_compilers':0,'new_timing_samples':0,'optimization_accepted':False,'limits':'Integer/source proofs only, not GPU numerical equality, cache transactions, process peak/CPU cost, supported runtime capacity or speed. Root review is not external independent review.'})
old.save(S/'source-review.json',{'at':old.now(),'id':'E070','status':'CUDA_source_transform_and_integer_encoding_review_pass','report_sha256':old.sha(H/'report.json'),'per_function_changes':[{'function':n,'baseline_sha256':hashlib.sha256(a.encode()).hexdigest(),'candidate_sha256':hashlib.sha256(b.encode()).hexdigest()} for n,a,b in edits],'float_source_order_unchanged':'Only metadata pointer parameters, call forwarding and integer field decoding change. All float expressions/reduction order, barriers, spans/launch widths remain source-identical. Actual compiled numerical behavior still requires raw controls.','resource_risks':'narrow loads and shifts may alter registers/occupancy/instruction scheduling; packing adds CPUwork and temporary2*Nbytes. Default2^8byte source bounds, no truncation/threshold variants.','not_prior_variants':'Global player/arity encoding differs from old noalias, chance-record AoS, shared showdown index narrowing and work ordering; none are composed/reopened.','external_independent_review':False,'candidate_accepted':False})
old.custody();published=[]
for folder in [H,S]:
 for p in folder.iterdir():
  if p.is_file() and p.suffix in ['.json','.cu','.patch']:
   key=folder.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
   with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:ck(response.read()==p.read_bytes(),'served artifact bytes')
   published.append(key)
old.save(H/'publication.json',{'at':old.now(),'http_byte_verified_files':published,'all_raw_preserved_on_S':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert not any(x['id']=='D114' for x in st['experiments']);st['experiments'].append({'id':'D114','at':old.now(),'title':'Lossless global node metadata encoding','kind':'diagnostic','status':'measured','correctness':'integer proof pass; GPU untested','fixture':'Full byte domain and12retained CPU plan cases','stage':'CPU/source proof complete; resource compile next','reason':f'65536byte pairs and{sum(c["nodes"] for c in cases)}retained nodes losslessly packed. Proposed metadata payload8*N to2*N bytes, not a measured speedup. All GPU/host/material qualification remains.','accepted':False,'evidence':[{'label':'Frozen proof/resource scope','url':'evidence/D114-node-metadata/protocol.json'},{'label':'Exact integer and caller audit','url':'evidence/D114-node-metadata/report.json'},{'label':'Off-tree CUDA patch','url':'evidence/E070-source/candidate.patch'}]});st.update(updated_at=old.now(),state='running',goal_status='active',active_experiment=None,stage='E070 metadata encoding compiler prerequisite',activity='Goal resumed. D114byte-domain and retained-node proofs pass. E070is a distinct off-tree metadata encoding; no compiler or GPUtrial yet, no new accepted gain.');old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'status':'proof_complete','root_checks':checks,'retained_nodes':sum(c['nodes'] for c in cases),'candidate_cuda_sha256':old.sha(S/'candidate.cu'),'report_sha256':old.sha(H/'report.json'),'free_GiB':shutil.disk_usage(ROOT).free/1024**3}),flush=True)