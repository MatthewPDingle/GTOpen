"""Canonical card comparisons: freeze one two-entry, no-launch resource probe."""
import difflib,json,struct,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
A=ROOT/'runs/D078-card-membership-source';R=old.read(A/'report.json')
for p,h in R['source_sha256'].items():old.pin(p,h)
old.pin(A/'algebra.bin',R['algebra']['raw_sha256']);raw=(A/'algebra.bin').read_bytes();assert raw[:8]==b'D078ALG1' and len(raw)==703048
for i in range(140608):
 c1,c2,d,b,c=raw[8+5*i:13+5*i];assert (c1,c2,d)==(i//(52*52),(i//52)%52,i%52)
 assert bool(b)==bool(((1<<c1)|(1<<c2))&(1<<d))==bool(c)==(d==c1 or d==c2)
D=ROOT/'runs/E048-design';D.mkdir();rel='crates/solver/src/gpu/kernels.cu';base=(ar.REPO/rel).read_bytes().decode('utf-8');nl='\r\n' if '\r\n' in base else '\n';candidate=base;changes=[]
start=base.index('extern "C" __global__ void down_chance(');end=base.index('// Up sweep, fold terminals:',start);part=base[start:end]
new=part.replace('    const u64* __restrict__ mask0, const u64* __restrict__ mask1,','    const u32* __restrict__ card1_0, const u32* __restrict__ card2_0,'+nl+'    const u32* __restrict__ card1_1, const u32* __restrict__ card2_1,')
new=new.replace('    u64 cm = 1ull << cards[start + e];','    u32 card = cards[start + e];').replace('(mask0[i] & cm)','(card1_0[i] == card || card2_0[i] == card)').replace('(mask1[j] & cm)','(card1_1[j] == card || card2_1[j] == card)')
assert part!=new and 'mask0' not in new and 'mask1' not in new;candidate=candidate.replace(part,new,1);changes.append((part,new))
start=base.index('extern "C" __global__ void up_chance(');end=base.index('// Up sweep, action nodes:',start);part=base[start:end]
new=part.replace('    const u64* __restrict__ mask_p,','    const u32* __restrict__ card1_p, const u32* __restrict__ card2_p,').replace('        u64 hm = mask_p[i];','        u32 c1 = card1_p[i], c2 = card2_p[i];').replace('            u64 cm = 1ull << cc_card[t];'+nl+'            if (hm & cm) continue;','            u32 card = cc_card[t];'+nl+'            if (c1 == card || c2 == card) continue;')
assert part!=new and 'mask_p' not in new and 'u64 cm' not in new;candidate=candidate.replace(part,new,1);changes.append((part,new))
reverse=candidate
for before,after in changes:assert reverse.count(after)==1;reverse=reverse.replace(after,before,1)
assert reverse==base
(D/'baseline.cu').write_bytes(base.encode('utf-8'));(D/'candidate.cu').write_bytes(candidate.encode('utf-8'))
(D/'candidate.patch').write_text(''.join(difflib.unified_diff(base.splitlines(keepends=True),candidate.splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel)),encoding='utf-8')
files=subprocess.check_output(['rg','--files','-g','*.cu',str(ROOT/'runs')],text=True).splitlines();prior={p:old.sha(p) for p in files if not Path(p).is_relative_to(D)};assert old.sha(D/'candidate.cu') not in prior.values()
old.save(A/'caller-and-domain-review.json',{'at':old.now(),'status':'pass_to_one_frozen_two_entry_resource_probe','root_review_only':True,'algebra_sha256':old.sha(A/'algebra.bin'),'raw_algebra_records_independently_decoded':140608,'source_report_sha256':old.sha(A/'report.json'),'supported_domain':'Canonical card IDs and masks produced by the sole HandInfo factory in game.rs184-194; save.rs175 rebuilds through Spot::new_lenient. In-engine source search found no alternative HandInfo factory or mask mutation. Public manually inconsistent Rust structs remain outside this domain.','all_mask_uses_reviewed':'Only constructor, four training/evaluation chance launch sites, the full-down unit reference and feature capacity accounting. No continuation mask replacement; continuation uses the same GpuSolver methods.','future_host_integration':'Reuse d_hand_c1/d_hand_c2 in all5 caller sites, remove2 private mask allocations, retain CPU plan fields, remove original mask bytes from expected/observed GPU metadata accounting without changing component-vector indices. No host packing or added GPU buffers. Not implemented yet.','byte_exact_cuda_reversal':True,'changed_entries':['down_chance','up_chance'],'float_statement_order':'Reach-copy/zero, CFV additions, card order/permutation, inverse multiplication and all other expressions unchanged.','novelty_unique_against_preserved_cuda_files':len(prior),'candidate_source_activated':False,'compiler_gpu_solver_runs':0,'limits':'Boolean/source/caller reasoning, not compiled equivalence, speed or material-cost proof.'})
old.save(D/'manifest.json',{'id':'E048-cuda-source','at':old.now(),'accepted_cuda_sha256':old.sha(D/'baseline.cu'),'candidate_cuda_sha256':old.sha(D/'candidate.cu'),'patch_sha256':old.sha(D/'candidate.patch'),'exact_reversal':True,'changed_entries':['down_chance','up_chance'],'caller_domain_review_sha256':old.sha(A/'caller-and-domain-review.json'),'source_activated':False})
HERE=ROOT/'runs/E048-resource';HERE.mkdir()
for n in ['baseline.cu','candidate.cu']:(HERE/n).write_bytes((D/n).read_bytes())
probe='''//! E048 compile/load/resource inspection only. No kernel or solve launch.
use cudarc::{driver::{CudaContext,sys::CUdevice_attribute as Attr},nvrtc::{compile_ptx_with_opts,CompileOptions}};
use std::{fs::OpenOptions,io::Write};
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E048_RESOURCE {v}").unwrap();o.flush().unwrap();}
fn main(){
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");
 let (major,minor)=ctx.compute_capability().unwrap();assert_eq!((major,minor),(12,0));
 let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
 let shared_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap();
 let block_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap();
 emit(serde_json::json!({"stage":"device","device":ctx.name().unwrap(),"architecture":arch,"shared_limit":shared_limit,"block_limit":block_limit,"kernel_launches":0}));
 for (variant,source) in [("baseline",include_str!("baseline.cu")),("candidate",include_str!("candidate.cu"))]{
  let ptx=compile_ptx_with_opts(source,CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
  let mut f=OpenOptions::new().create_new(true).write(true).open(format!("{variant}.ptx")).unwrap();f.write_all(ptx.to_src().as_bytes()).unwrap();f.flush().unwrap();f.sync_all().unwrap();drop(f);
  let module=ctx.load_module(ptx).unwrap();
  for kernel in ["down_chance","up_chance"]{
   let f=module.load_function(kernel).unwrap();let registers=f.num_regs().unwrap();let local=f.local_size_bytes().unwrap();let shared=f.shared_size_bytes().unwrap();let max_threads=f.max_threads_per_block().unwrap();
   let occupancy:Vec<_>=[64u32,128,256].into_iter().map(|threads|(threads,f.occupancy_max_active_blocks_per_multiprocessor(threads,0,None).unwrap())).collect();
   emit(serde_json::json!({"stage":"resource","variant":variant,"kernel":kernel,"registers":registers,"local_bytes_per_thread":local,"static_shared_bytes":shared,"dynamic_shared_bytes":0,"max_threads":max_threads,"actual_block_threads":128,"occupancy_by_threads":occupancy,"fits_default_limits":shared<=shared_limit&&max_threads>=128&&block_limit>=128,"kernel_launches":0,"performance_measurement":false}));drop(f);
  }
  drop(module);ctx.check_err().unwrap();
 }
 ctx.check_err().unwrap();emit(serde_json::json!({"stage":"complete","kernel_launches":0,"solver_executions":0,"performance_measurement":false,"candidate_accepted":false}));
}
'''
(HERE/'probe.rs').write_text(probe,encoding='utf-8')
template=(ROOT/'runs/E047-resource/execute.py').read_text(encoding='utf-8');pre=template[:template.index('with old.ar.exclusive_lock')].replace('E047','E048').replace('import hashlib,json,shutil','import hashlib,json,re,shutil')
body='''with old.ar.exclusive_lock(old.ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(old.ROOT).free>=54*1024**3
 assert not OUT.exists() and not (HERE/'probe.exe').exists();OUT.mkdir()
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid'] in gpu['stdout']
 old.save(OUT/'before.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'input_sha256':P['input_sha256'],'gpu':gpu,'accepted162_unchanged':True})
 env=old.env();assert not {k:v for k,v in env.items() if k in {'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER'} or k.startswith('CARGO_PROFILE_RELEASE_')}
 child(P['rustc_command'],'rustc',env,180);old.custody()
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.save(OUT/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(HERE/'probe.exe'),'native_executions':0,'rustc_terminal':True})
 child([str(HERE/'probe.exe')],'probe',env,180);old.custody()
 raw=(OUT/'probe.stdout.log').read_text(encoding='utf-8');markers=[json.loads(x.split('E048_RESOURCE ',1)[1]) for x in raw.splitlines() if 'E048_RESOURCE ' in x]
 assert len(markers)==6 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete'
 rows={(x['variant'],x['kernel']):x for x in markers[1:-1]};assert set(rows)=={(v,k) for v in ['baseline','candidate'] for k in P['changed_entries']}
 be,ce=entries(OUT/'baseline.ptx'),entries(OUT/'candidate.ptx');assert set(be)==set(ce)==set(P['expected_entries'])
 unchanged=[k for k in be if be[k]==ce[k]];gates={'other7_entries_exact':set(unchanged)==set(be)-set(P['changed_entries'])};details={};abi={}
 for k in P['changed_entries']:
  b,c=rows['baseline',k],rows['candidate',k]
  assert all(r['kernel_launches']==0 and r['performance_measurement'] is False for r in [b,c])
  kg={'changed_body':be[k]!=ce[k],'registers_not_increased':c['registers']<=b['registers'],'local_not_increased':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],'shared_not_increased':c['static_shared_bytes']<=b['static_shared_bytes'],'max_threads_not_reduced':c['max_threads']>=b['max_threads'],'fits_default_limits':b['fits_default_limits'] and c['fits_default_limits'],'occupancy_not_reduced':all(bt==ct and cn>=bn for (bt,bn),(ct,cn) in zip(b['occupancy_by_threads'],c['occupancy_by_threads'])) and len(c['occupancy_by_threads'])==3}
  abi[k]={}
  for variant,table in [('baseline',be),('candidate',ce)]:
   header=table[k].split('{',1)[0]
   params=re.findall(r'\\.param\\s+\\.(u[0-9]+)((?:\\s+\\.ptr\\s+\\.align\\s+[0-9]+)?)\\s+'+k+r'_param_([0-9]+)',header)
   observed=[{'type':t,'pointer':bool(ptr),'index':int(idx)} for t,ptr,idx in params];abi[k][variant]=observed
   expected=P['expected_abi'][k][variant]
   kg[variant+'_abi_exact']=[x['type'] for x in observed]==expected and [x['index'] for x in observed]==list(range(len(expected))) and all(x['pointer']==(x['type']=='u64') for x in observed)
  details[k]={'baseline':b,'candidate':c,'gates':kg};gates.update({k+':'+name:value for name,value in kg.items()})
 report={'id':'E048-resource','at':old.now(),'status':'pass_resource_feasibility_only' if all(gates.values()) else 'rejected_resource_gate','protocol_sha256':sys.argv[1],'source_manifest_sha256':P['source_manifest_sha256'],'raw_markers':markers,'details':details,'abi':abi,'gates':gates,'ptx_sha256':{v:old.sha(OUT/(v+'.ptx')) for v in ['baseline','candidate']},'entry_body_sha256':{v:{n:hashlib.sha256(t.encode()).hexdigest() for n,t in table.items()} for v,table in [('baseline',be),('candidate',ce)]},'binary_sha256':old.sha(HERE/'probe.exe'),'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'stderr_sha256':old.sha(OUT/'probe.stderr.log'),'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'accepted162_main_live_ptx_unchanged':True,'limits':'Actual compiled attributes and theoretical occupancy only. No numerical, runtime utilization, capacity or speed qualification.'}
 old.save(HERE/'report.json',report);old.save(OUT/'complete.json',{'at':old.now(),'report_sha256':old.sha(HERE/'report.json'),'all_children_terminal':True,'kernel_launches':0,'solver_executions':0,'accepted162_main_live_ptx_unchanged':True})
 print(json.dumps({'status':report['status'],'details':details,'gates':gates,'report_sha256':old.sha(HERE/'report.json')},indent=2),flush=True)
'''
(HERE/'execute.py').write_text(pre+body,encoding='utf-8')
p=old.read(ROOT/'runs/E047-resource/protocol.json');p.update(id='E048-resource',at=old.now(),source_manifest_sha256=old.sha(D/'manifest.json'),changed_entries=['down_chance','up_chance'])
p['rustc_command']=[x.replace('E047-resource','E048-resource') for x in p['rustc_command']]
p['expected_abi']={'down_chance':{'baseline':['u64']*3+['u32']*2+['u64']*6+['u32']*2,'candidate':['u64']*3+['u32']*2+['u64']*8+['u32']*2},'up_chance':{'baseline':['u64','u32','u32']+['u64']*10+['u32']*2,'candidate':['u64','u32','u32']+['u64']*11+['u32']*2}}
deps={n:h for n,h in p['input_sha256'].items() if '/build/' in n.replace('\\','/')};refs=[HERE/'baseline.cu',HERE/'candidate.cu',HERE/'probe.rs',HERE/'execute.py',D/'manifest.json',A/'report.json',A/'algebra.bin',A/'caller-and-domain-review.json',ar.REPO/'tools/postflop_autoresearch.py',ROOT/'runs/small-gain-confirmation-plan/common.py'];p['input_sha256']=deps|{str(x):old.sha(x) for x in refs}
p['resource_gates']=['Only down_chance/up_chance bodies differ; other7 entry bodies exact.','Per-kernel original/new ABI indices/types/pointer qualifiers exact.','No per-kernel increased registers/local/staticshared, lower maxthreads or64/128/256 theoretical occupancy; default limits fit.','No kernel/solver launch or timing. One fixed representation, no packing/partial-kernel/factor rescue after outcome.'];old.save(HERE/'protocol.json',p)
published={}
for directory in [D,HERE]:
 for src in directory.iterdir():
  if not src.is_file():continue
  key=directory.name+'/'+src.name;dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();data=src.read_bytes();dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==data
  published[key]=old.sha(src)
src=A/'caller-and-domain-review.json';key=A.name+'/'+src.name;dst=ar.DASHBOARD/'evidence'/key;assert not dst.exists();dst.write_bytes(src.read_bytes())
with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
published[key]=old.sha(src);old.save(HERE/'pre-execution-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'kernel_launches':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(ar.STATUS);assert not any(e['id']=='E048' for e in s['experiments']);s['experiments'].append({'id':'E048','at':old.now(),'title':'Reuse card IDs for chance blocker tests','kind':'candidate','status':'preparing','correctness':'pending','stage':'Frozen two-kernel no-launch resource probe','reason':'Canonical card comparison is algebraically exact; unchanged CPU plan and existing card buffers. ABI/resources/numerical GPU behavior and speed unproven.','evidence':[{'label':'E048 fixed two-entry resource protocol','url':'evidence/E048-resource/protocol.json'},{'label':'D078 caller/domain review','url':'evidence/D078-card-membership-source/caller-and-domain-review.json'}]});s.update(state='running',stage='E048 compiler/resource probe',activity='Check both chance kernels and changed ABI before any numerical launch or host implementation.',updated_at=ar.now());ar.atomic_json(ar.STATUS,s)
print(json.dumps({'protocol_sha256':old.sha(HERE/'protocol.json'),'source_manifest_sha256':old.sha(D/'manifest.json'),'candidate_sha256':old.sha(D/'candidate.cu'),'prior_cuda_files':len(prior)}),flush=True)
