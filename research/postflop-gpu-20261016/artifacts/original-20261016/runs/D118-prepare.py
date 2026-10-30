"""D118: one lossless private river-boundary representation, off-tree only."""
from pathlib import Path
import array,difflib,hashlib,json,re,shutil,struct,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018'
sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
H=R/'runs/D118-river-boundaries';S=R/'runs/E073-source';assert not H.exists()and not S.exists();H.mkdir();S.mkdir()
A=R/'runs/D092-action-arity-order';AR=old.read(A/'report.json');schema=old.read(A/'field-schema.json')['fields']
assert [schema[i]['name']for i in [48,49]]==['riv_lower','riv_upper']
raws=[A/'execution'/f'case-{i:02d}.bin'for i in range(12)]
owned=['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/continuation_capacity.rs']
inputs=[Path(__file__),A/'report.json',A/'field-schema.json',*raws,*[old.REPO/p for p in owned],old.REPO/'crates/solver/src/gpu/plan.rs',old.REPO/'crates/solver/src/game.rs',old.REPO/'crates/solver/src/cards.rs',old.REPO/'crates/solver/src/range.rs',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',C/'common_e051_live.py',C/'protected-main.json']
old.save(H/'protocol.json',{'id':'D118','at':old.now(),'scope':'Source/ownership review and exact integer representation proof only. No compiler, application kernel, solve or timing sample.','input_sha256':{str(p):old.sha(p)for p in inputs},'fixed_proof':'Every u16 value0..65535 round-trips through little-endian storage and u32 promotion; every original lower/upper word in12retained accepted E051 plans, isooff/on and compact/full, is checked and retained in paired raw form.','prospective_candidate':'Only private GPU lower/upper boundary buffers become u16. CPU/public GpuPlan, ranks, list offsets, arithmetic, launch/graph, storage/save/quality and all other GPU payloads unchanged. Same buffer/element counts, half bytes for these4buffers.','host_cost':'One checked Vec<u16> per upload, explicitly synchronize before its destruction;4temporary allocations and4synchronizations inside complete clocks. At most one new temporary live at once; physical allocator/process peak/CPU/responsiveness are not assumed free.','source_family':'Not E052shared card positions, E057prefix mapping, E063per-card cutoff encoding, E070global player/arity packing or E072fold staging. None are composed or reopened. No width/packing/threshold/source variants after numerical or performance failure.','acceptance':'Same unrounded1% complete-cycle, strict fixture guard, fresh16, full exact/broad/material/capacity/holdout/cumulative qualification before adoption. Source/bytes/compiler evidence cannot accept a performance change.','reserve_bytes':66*1024**3,'expected_added_raw_bytes_at_most':1024**3,'candidate_accepted':False})

checks=0
def ck(v,label):
 global checks
 assert v,label;checks+=1

history=subprocess.run(['git','log','--all','--format=%H','-G','(riv_lower|riv_upper|p_lower|p_upper).*u16|u16.*(riv_lower|riv_upper|p_lower|p_upper)|unsigned short.*p_lower','--','crates/solver/src/gpu'],cwd=old.REPO,text=True,capture_output=True,check=True)
ck(not history.stdout.strip(),'no matching local all-ref boundary narrowing')
matches=[];scanned=0
for p in(R/'runs').rglob('*.cu'):
 if S in p.parents:continue
 t=p.read_text(encoding='utf-8',errors='strict');scanned+=1
 if re.search(r'const\s+(?:unsigned\s+short|u16|uint16_t)\s*\*[^,\n]*\bp_(?:lower|upper)\b',t):matches.append(str(p))
ck(not matches,'review any prior narrow global boundary source')
old.save(H/'history.json',{'at':old.now(),'git_query':history.args,'local_all_ref_matches':history.stdout.splitlines(),'retained_CUDA_files_scanned':scanned,'matching_boundary_pointer_sources':matches,'scope':'Bounded retained CUDA and local all-ref source history, not exhaustive remote novelty.','declined_source_leads':['Chance child-to-CFV pre-resolution overlaps E018dependent-child mapping and E039child-base cache; no candidate created.','NVRTC-only overlap lacks demonstrated1% headroom: D088first compile/module envelope53.2587ms, PTX already process-cached, not a removable global bound.','Fold copy/reduction fusion resembles closed E053copy/prefix fusion; no candidate created.']})
cards=(old.REPO/'crates/solver/src/cards.rs').read_text(encoding='utf-8');game=(old.REPO/'crates/solver/src/game.rs').read_text(encoding='utf-8');plan=(old.REPO/'crates/solver/src/gpu/plan.rs').read_text(encoding='utf-8')
ck('pub const NUM_COMBOS: usize = 1326;'in cards,'physical combo domain')
ck('for idx in 0..NUM_COMBOS {'in game and 'if hands[p].len() > u16::MAX as usize {'in game,'legal Spot construction bounds')
ck('while lower < opponent.len() && opponent[lower].0 < stren {'in plan and 'while upper < opponent.len() && opponent[upper].0 <= stren {'in plan,'original boundaries at most sorted opponent length')
for x in range(65536):ck(struct.unpack('<H',struct.pack('<H',x))[0]==x,'complete u16 round trip')

def vector(f,read=False):
 n=struct.unpack('<Q',f.read(8))[0];ck(n<100000000,'bounded encoded word count')
 if not read:f.seek(n*8,1);return None
 v=array.array('Q');v.fromfile(f,n);ck(len(v)==n,'complete word vector');return v
cases=[]
for case,path in enumerate(raws):
 old.pin(path,AR['cases'][case]['raw_sha256']);fields={}
 with path.open('rb')as f:
  ck(f.read(16)==b'D092-PLAN-RAW1\0\0','baseline framing');ck(struct.unpack('<II',f.read(8))==(case,53),'case/schema');f.read(16)
  for field in range(53):
   ck(struct.unpack('<I',f.read(4))[0]==field,'field index');vector(f);vector(f);v=vector(f,field in [1,48,49]);vector(f)
   if v is not None:fields[field]=v
  vector(f);vector(f);ck(f.read(1)==b'','complete raw endpoint')
 ck(len(fields[1])==3 and fields[1][0]==2 and max(fields[1][1:])<=1326,'two legal hand domains')
 out=H/f'case-{case:02d}-boundaries.bin';count=0;maximum=0;lengths=[]
 with out.open('xb')as f:
  f.write(b'D118-BOUNDS-V1\0\0');ck(f.tell()==16,'paired raw magic');f.write(struct.pack('<I',case))
  for field in [48,49]:
   v=fields[field];ck(v[0]==2,'two player vectors');offset=1
   for p in range(2):
    n=v[offset];offset+=1;f.write(struct.pack('<IIQ',field,p,n));chunk=bytearray();maximum=max(maximum,max(v[offset:offset+n],default=0));lengths.append(n)
    for x in v[offset:offset+n]:
     ck(x<=fields[1][2-p]and x<=1326,'every bound within opposing hand count');packed=struct.pack('<H',x);ck(struct.unpack('<H',packed)[0]==x,'every retained word lossless');chunk.extend(struct.pack('<I',x)+packed)
     if len(chunk)>=65532:f.write(chunk);chunk.clear()
    f.write(chunk);offset+=n;count+=n
   ck(offset==len(v),'full nested vector endpoint')
 ck(lengths[0]==lengths[2]and lengths[1]==lengths[3],'lower/upper geometry');ck(out.stat().st_size==84+6*count,'complete paired raw bytes')
 cases.append({'case':case,'hand_counts':list(fields[1][1:]),'four_boundary_vector_lengths':lengths,'boundary_words':count,'maximum_bound':maximum,'baseline_GPU_boundary_payload_bytes':4*count,'candidate_GPU_boundary_payload_bytes':2*count,'logical_payload_saved_bytes':2*count,'max_one_temporary_payload_bytes':2*max(lengths,default=0),'baseline_raw_sha256':old.sha(path),'paired_raw_sha256':old.sha(out),'paired_raw_bytes':out.stat().st_size})

baseline={p:(old.REPO/p).read_bytes()for p in owned};candidate={};transforms={}
for p,b in baseline.items():
 t=b.decode('utf-8').replace('\r\n','\n');edits=[]
 if p.endswith('kernels.cu'):
  before='const u32* __restrict__ p_lower, const u32* __restrict__ p_upper,';after='const unsigned short* __restrict__ p_lower, const unsigned short* __restrict__ p_upper,';edits=[(before,after)]
 elif p.endswith('mod.rs'):
  helper='''        // Rank boundaries are counts of at most 1326 physical hands. Keep
        // the public CPU plan intact and narrow only these private uploads.
        let up_bounds = |v: &Vec<u32>| -> Result<CudaSlice<u16>, String> {
            let mut values = Vec::with_capacity(v.len());
            for &value in v {
                values.push(u16::try_from(value).map_err(|_| "river rank boundary exceeds u16".to_string())?);
            }
            let device = stream.clone_htod(&values).map_err(e)?;
            // Retire every transfer before the temporary source can be freed,
            // including when later constructor work returns an error.
            stream.synchronize().map_err(e)?;
            Ok(device)
        };
'''
  edits=[('d_riv_lower: [CudaSlice<u32>; 2],','d_riv_lower: [CudaSlice<u16>; 2],'),('d_riv_upper: [CudaSlice<u32>; 2],','d_riv_upper: [CudaSlice<u16>; 2],'),('        let upf = |v: &Vec<f32>| stream.clone_htod(v).map_err(e);\n','        let upf = |v: &Vec<f32>| stream.clone_htod(v).map_err(e);\n'+helper),('d_riv_lower: [up32(&plan.riv_lower[0])?, up32(&plan.riv_lower[1])?],','d_riv_lower: [up_bounds(&plan.riv_lower[0])?, up_bounds(&plan.riv_lower[1])?],'),('d_riv_upper: [up32(&plan.riv_upper[0])?, up32(&plan.riv_upper[1])?],','d_riv_upper: [up_bounds(&plan.riv_upper[0])?, up_bounds(&plan.riv_upper[1])?],')]
 else:edits=[('d_riv_lower:u32,','d_riv_lower:u16,'),('d_riv_upper:u32,','d_riv_upper:u16,')]
 original=t
 for a,b in edits:ck(t.count(a)==1,'single owned source replacement');t=t.replace(a,b,1)
 reverse=t
 for a,b in reversed(edits):ck(reverse.count(b)==1,'single reverse source replacement');reverse=reverse.replace(b,a,1)
 ck(reverse==original,'exact source reversal');suffix=Path(p).name;nl='\r\n'if b'\r\n'in baseline[p]else'\n';encoded=t.replace('\n',nl).encode();candidate[p]=encoded;transforms[p]={'replacements':len(edits),'baseline_sha256':hashlib.sha256(baseline[p]).hexdigest(),'candidate_sha256':hashlib.sha256(encoded).hexdigest()}
 (S/('baseline-'+suffix)).write_bytes(baseline[p]);(S/('candidate-'+suffix)).write_bytes(encoded)
patch=''.join(''.join(difflib.unified_diff(baseline[p].decode().splitlines(True),candidate[p].decode().splitlines(True),fromfile='E051/'+p,tofile='E073/'+p))for p in owned);(S/'candidate.patch').write_text(patch,encoding='utf-8',newline='')
# Keep the conventional CUDA names used by standalone resource/direct probes.
(S/'baseline.cu').write_bytes(baseline[owned[0]]);(S/'candidate.cu').write_bytes(candidate[owned[0]])
manifest={'id':'E073','at':old.now(),'accepted_source':'E051','candidate_owned_sha256':{p:hashlib.sha256(candidate[p]).hexdigest()for p in owned},'candidate_files':{p:str(S/('candidate-'+Path(p).name))for p in owned},'source_activated':False,'GPU_application_launches':0,'solver_executions':0};old.save(S/'manifest.json',manifest)
report={'id':'D118','at':old.now(),'status':'pass_legal_boundary_domain_and_retained_raw_equivalence','checks':checks,'full_u16_domain_cases':65536,'retained_plan_cases':cases,'retained_boundary_words':sum(x['boundary_words']for x in cases),'raw_bytes':sum(x['paired_raw_bytes']for x in cases),'source_scope':transforms,'public_CPU_GpuPlan_exact':True,'legal_count_bound':1326,'CPU_conversion':'Checkedu32to u16, same length/order, at most one temporary live, explicit stream synchronization before drop. No truncation, bit packing or fallback threshold.','changed_CUDA_entries':['up_show'],'CUDA_change':'Only p_lower/p_upper pointee types; every original body statement, ordered floating recurrence and barrier exact. Other8entry source bytes exact by sole declaration replacement.','capacity':'Only observed private d_riv_lower/d_riv_upper accounting changes4to2bytes; generic CPU estimate remains conservatively unchanged. Logical entries and all other buffers unchanged.','reference':{'url':'https://docs.nvidia.com/cuda/archive/12.9.2/cuda-c-programming-guide/index.html#device-memory-accesses','review':'NVIDIA CUDA12.9.2 size/alignment section supports naturally aligned2byte scalar global access. Actual generated narrow loads, resources, numerical output and speed still require independent evidence.'},'limits':'Integer model and source review only. Retained metadata is source-matched accepted E051, not a newly built candidate plan. No numerical GPU, driver traffic, actual integrated host/process peak/capacity/CPU or speed proof. Root is not external independent review.','compilers':0,'application_kernel_launches':0,'solver_executions':0,'timing_samples':0,'candidate_accepted':False};old.save(H/'report.json',report)
old.save(S/'source-review.json',{'id':'E073','at':old.now(),'status':'pass_source_and_integer_representation_review','D118_report_sha256':old.sha(H/'report.json'),'source_scope':transforms,'floating_body_unchanged':True,'public_CPU_plan_unchanged':True,'private_host_temporary_and_sync_costs_included':True,'prospective_compiler_prerequisite':'Actual andcompute75PTXexact other8entries/expected27ABI; narrow global loads from boundary parameters emitted; same allocated local/static/dynamic bytes and default feasibility/positive64/128/256occupancy for10fixed shapes. Register/residency are diagnostics under D108, no adoption without all later qualification. FPstatic opcode counts are diagnostic only; source recurrence and actual full raw numeric controls are mandatory.','no_variant_rescue':True,'external_independent_review':False,'candidate_accepted':False})
old.custody();published=[]
for folder in [H,S]:
 for p in folder.iterdir():
  if p.is_file()and p.suffix in ['.json','.cu','.rs','.patch']:
   key=folder.name+'/'+p.name;dest=old.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
   with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:ck(response.read()==p.read_bytes(),'HTTPexact artifact')
   published.append(key)
old.save(H/'publication.json',{'at':old.now(),'HTTP_byte_verified_files':published,'all_raw_retained_physically_on_S':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']in['D118','E073']for x in s['experiments'])
 s['experiments'].append({'id':'D118','at':old.now(),'title':'Lossless river rank-boundary storage','kind':'diagnostic','status':'measured','correctness':'integer/source pass; GPU untested','fixture':'Fullu16domain and12accepted E051CPUplans','stage':'Source/domain proof complete','reason':f'All65536u16values and{report["retained_boundary_words"]}retained boundaries exact. Private GPU4boundary arrays become16bit; same public CPUplan and arithmetic. Temporary packing/synchronizations remain inside complete clocks. No speed claim.','accepted':False,'evidence':[{'label':'Fixed integer/source protocol','url':'evidence/D118-river-boundaries/protocol.json'},{'label':'Source and full retained-data proof','url':'evidence/D118-river-boundaries/report.json'}]})
 s['experiments'].append({'id':'E073','at':old.now(),'title':'16-bit private river rank boundaries','kind':'candidate','status':'planned','correctness':'GPU untested','fixture':'Registered complete-solve suite; not run','stage':'Compiler/resource prerequisite next','reason':'Only private rank-boundary storage narrows. Added checked host packing and4synchronizations must earn their cost under unchanged1%/fixture/exact/broad/material gates. No acceptance or speed result.','accepted':False,'evidence':[{'label':'Frozen source review','url':'evidence/E073-source/source-review.json'},{'label':'Exact three-file patch','url':'evidence/E073-source/candidate.patch'}]})
 s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E073',stage='E073 compiler/resource prerequisite',activity='E072is closed after0.0294%gain and repeatable rainbow slowdown. D118proves lossless private16bit river boundaries; E073is off-tree only. Generated code/resources and raw GPU controls next; accepted/live E051 gain12.44%unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
print(json.dumps({'status':report['status'],'checks':checks,'retained_boundary_words':report['retained_boundary_words'],'raw_bytes':report['raw_bytes'],'source_sha256':manifest['candidate_owned_sha256'],'published_files':len(published)}),flush=True)
