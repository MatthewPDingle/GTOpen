"""Freeze E070 four-entry resource prerequisites; no application kernel launch."""
from pathlib import Path
import array,json,re,shutil,struct,subprocess,sys,urllib.request
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>67*1024**3
D=ROOT/'runs/D114-node-metadata';dr=old.read(D/'report.json');assert dr['status']=='pass_byte_domain_and_retained_node_encoding';S=ROOT/'runs/E070-source';H=ROOT/'runs/E070-resource';H.mkdir()
for p,h in old.read(D/'protocol.json')['input_sha256'].items():old.pin(p,h)
raw=(D/'all-byte-pairs.bin').read_bytes();assert raw[:16]==b'D114-U8PAIR-V1\0\0' and len(raw)==16+65536*4
checks=0
for i,(p,a,v) in enumerate(struct.iter_unpack('<BBH',raw[16:])):assert (p,a)==divmod(i,256) and v==(p<<8)|a and v>>8==p and v&255==a;checks+=1
for c in dr['retained_node_cases']:
 path=D/f'case-{c["id"]:02d}-packed.bin';old.pin(path,c['packed_raw_sha256']);raw=path.read_bytes();assert raw[:16]==b'D114-NODE-PACK1\0' and struct.unpack('<IQ',raw[16:28])==(c['id'],c['nodes']) and len(raw)==28+4*c['nodes'];n=0
 for p,a,v in struct.iter_unpack('<BBH',raw[28:]):assert v==(p<<8)|a and v>>8==p and v&255==a;n+=1
 assert n==c['nodes'];checks+=n
old.save(D/'root-raw-replay.json',{'at':old.now(),'status':'pass_saved_raw_encoding_replay','record_checks':checks,'source_report_sha256':old.sha(D/'report.json'),'all65536byte_pairs_and10774636retained_rows_replayed':True,'external_independent_review':False,'gpu_launches':0,'performance_measured':False})
for n in ['baseline.cu','candidate.cu']:shutil.copyfile(S/n,H/n)
probe=r'''use cudarc::{driver::{CudaContext,sys::CUdevice_attribute as Attr},nvrtc::{compile_ptx_with_opts,CompileOptions}};
use std::{fs::OpenOptions,io::Write};
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E070_RESOURCE {v}").unwrap();o.flush().unwrap();}
fn main(){
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");
 let(major,minor)=ctx.compute_capability().unwrap();assert_eq!((major,minor),(12,0));
 let actual:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
 let shared_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap();
 let block_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap();
 emit(serde_json::json!({"stage":"device","device":ctx.name().unwrap(),"architecture":actual,"shared_limit":shared_limit,"block_limit":block_limit,"kernel_launches":0}));
 for arch in [actual,"compute_75"]{
  for(variant,source) in [("baseline",include_str!("baseline.cu")),("candidate",include_str!("candidate.cu"))]{
   let ptx=compile_ptx_with_opts(source,CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
   let mut file=OpenOptions::new().create_new(true).write(true).open(format!("{variant}-{arch}.ptx")).unwrap();file.write_all(ptx.to_src().as_bytes()).unwrap();file.flush().unwrap();file.sync_all().unwrap();drop(file);
   if arch==actual{
    let module=ctx.load_module(ptx).unwrap();
    for kernel in ["down_action","up_fold","up_action","up_action_eval"]{
     let f=module.load_function(kernel).unwrap();let registers=f.num_regs().unwrap();let local=f.local_size_bytes().unwrap();let shared=f.shared_size_bytes().unwrap();let max_threads=f.max_threads_per_block().unwrap();
     let dynamic=if kernel=="up_fold"{4*1326u32}else{0};
     let occupancy:Vec<_>=[64u32,128,256].into_iter().map(|t|(t,f.occupancy_max_active_blocks_per_multiprocessor(t,dynamic as usize,None).unwrap())).collect();
     emit(serde_json::json!({"stage":"resource","variant":variant,"kernel":kernel,"shape":"same128threads_max1326hands","registers":registers,"local_bytes_per_thread":local,"static_shared_bytes":shared,"dynamic_shared_bytes":dynamic,"max_threads":max_threads,"actual_block_threads":128,"occupancy_by_threads":occupancy,"fits_default_limits":shared+dynamic as i32<=shared_limit&&max_threads>=256&&block_limit>=256,"kernel_launches":0,"performance_measurement":false}));
    }
    drop(module);ctx.check_err().unwrap();
   }
  }
 }
 ctx.check_err().unwrap();emit(serde_json::json!({"stage":"complete","resource_rows":8,"compile_variants":4,"kernel_launches":0,"solver_executions":0,"performance_measurement":false,"candidate_accepted":false}));
}
'''
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
prior=ROOT/'runs/E068-resource';prefix=(prior/'execute.py').read_text(encoding='utf-8').split("with old.ar.exclusive_lock(",1)[0].replace('E068','E070')
body=r'''with old.ar.exclusive_lock(old.ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(old.ROOT).free>=66*1024**3
 assert not OUT.exists() and not (HERE/'probe.exe').exists();OUT.mkdir()
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid'] in gpu['stdout']
 old.save(OUT/'before.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'gpu':gpu,'application_kernel_launches':0})
 env=old.env();assert not {k:v for k,v in env.items() if k in {'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER'} or k.startswith('CARGO_PROFILE_RELEASE_')}
 child(P['rustc_command'],'rustc',env,180)
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.save(OUT/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(HERE/'probe.exe'),'rustc_terminal':True,'native_executions':0})
 child([str(HERE/'probe.exe')],'probe',env,180);old.custody()
 raw=(OUT/'probe.stdout.log').read_text(encoding='utf-8');markers=[json.loads(x.split('E070_RESOURCE ',1)[1]) for x in raw.splitlines() if 'E070_RESOURCE ' in x];assert len(markers)==10 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete'
 rows={(x['variant'],x['kernel']):x for x in markers[1:-1]};assert len(rows)==8
 tables={(v,a):entries(OUT/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']}
 assert all(set(t)==set(P['expected_entries']) for t in tables.values());changed=set(P['changed_entries']);gates={};details={};abi={};mechanism={}
 for arch in ['compute_120','compute_75']:
  be,ce=tables['baseline',arch],tables['candidate',arch]
  gates[arch+':other5_entries_exact']=all(be[n]==ce[n] for n in be if n not in changed)
  gates[arch+':exact4_changed_entries']={n for n in be if be[n]!=ce[n]}==changed
  for name in P['changed_entries']:
   def sig(t):return re.findall(r'\.param\s+\.(u[0-9]+)((?:\s+\.ptr\s+\.align\s+[0-9]+)?)\s+'+re.escape(name)+r'_param_([0-9]+)',t.split('{',1)[0])
   bs,cs=sig(be[name]),sig(ce[name]);meta=P['parameter_schema'][name];assert [int(x[2]) for x in bs]==list(range(len(bs))) and [int(x[2]) for x in cs]==list(range(len(cs)))
   expected=[x for x,p in zip(bs,meta['baseline']) if p['name']!='node_na'];same=len(bs)==len(meta['baseline']) and len(cs)==len(meta['candidate'])==len(expected) and [(x[0],x[1]) for x in cs]==[(x[0],x[1]) for x in expected]
   gates[arch+':'+name+':ABI_transform']=same;abi[arch+':'+name]={'baseline':bs,'candidate':cs,'source_parameter_schema':meta}
   narrow=len(re.findall(r'\bld\.global(?:\.[a-z0-9]+)*\.(?:u8|u16)\b',ce[name]));gates[arch+':'+name+':narrow_metadata_load_emitted']=narrow>0;mechanism[arch+':'+name]={'candidate_PT X_narrow_global_load_sites'.replace('PT X','PTX'):narrow,'driver_SASS_inspected':False}
 sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_feasibility import evaluate_feasibility
 proof=old.read(P['allocation_proof']['path'])
 for name in P['changed_entries']:
  b,c=rows['baseline',name],rows['candidate',name];admission=evaluate_feasibility(b,c,proof);kg=admission['gates']|{'same_dynamic_bytes':b['dynamic_shared_bytes']==c['dynamic_shared_bytes']};details[name]={'baseline':b,'candidate':c,'feasibility':admission};gates.update({name+':'+k:v for k,v in kg.items()})
 report={'id':'E070-resource','at':old.now(),'status':'pass_resource_and_encoding_prerequisites' if all(gates.values()) else 'rejected_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'details':details,'abi':abi,'emitted_mechanism':mechanism,'raw_markers':markers,'ptx_sha256':{v+'-'+a:old.sha(OUT/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']},'entry_body_sha256':{v+'-'+a:{n:hashlib.sha256(t.encode()).hexdigest() for n,t in table.items()} for(v,a),table in tables.items()},'binary_sha256':old.sha(HERE/'probe.exe'),'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'host_integration_implemented':False,'accepted_main_live_ptx_unchanged':True,'limits':'Compiler PTX narrow loads and driver attributes/occupancy only. No driver SASS, GPU floating-result equivalence, actual integrated allocation/graph/CPU/peak/capacity or speed qualification. No source activation.'}
 old.save(HERE/'report.json',report);old.save(OUT/'complete.json',{'at':old.now(),'report_sha256':old.sha(HERE/'report.json'),'all_children_terminal':True,'application_kernel_launches':0})
 print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items() if not v],'resources':{n:{'registers':[details[n][v]['registers'] for v in ['baseline','candidate']],'local':[details[n][v]['local_bytes_per_thread'] for v in ['baseline','candidate']],'max_threads':[details[n][v]['max_threads'] for v in ['baseline','candidate']]} for n in details},'report_sha256':old.sha(HERE/'report.json')}),flush=True)
'''
(H/'execute.py').write_text(prefix+body,encoding='utf-8',newline='\n')
original=old.read(prior/'protocol.json');command=[x.replace(str(prior),str(H)) for x in original['rustc_command']]

def schema(text,name):
 m=re.search(r'\bvoid\s+'+name+r'\s*\(',text);assert m;end=text.index(')',m.end());params=re.sub(r'//[^\n]*','',text[m.end():end]).split(',');out=[]
 for p in params:
  p=p.strip();match=re.search(r'(\w+)\s*$',p);assert match;out.append({'name':match.group(1),'type':' '.join(p[:match.start()].split())})
 return out
changed=['down_action','up_fold','up_action','up_action_eval'];schemas={}
for n in changed:
 bs=schema((H/'baseline.cu').read_text(encoding='utf-8'),n);cs=schema((H/'candidate.cu').read_text(encoding='utf-8'),n);expected=[{'name':'node_attrs','type':'const unsigned short* __restrict__'} if p['name']=='node_player' else p for p in bs if p['name']!='node_na'];assert cs==expected;schemas[n]={'baseline':bs,'candidate':cs}
paths=[Path(__file__),*S.iterdir(),H/'baseline.cu',H/'candidate.cu',H/'execute.py',H/'probe.rs',D/'protocol.json',D/'report.json',D/'root-raw-replay.json',D/'history.json',Path(original['allocation_proof']['path']),old.REPO/'tools/postflop_resource_feasibility.py',old.REPO/'tools/postflop_resource_admission.py',old.REPO/'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
inputs={str(p):old.sha(p) for p in paths if p.is_file()}
for p,h in original['input_sha256'].items():
 if '\\build\\release\\deps\\' in p:old.pin(p,h);inputs[p]=h
old.save(H/'protocol.json',{'id':'E070-resource','at':old.now(),'status':'FROZEN_PRE_COMPILER','source_manifest_sha256':old.sha(S/'manifest.json'),'changed_entries':changed,'expected_entries':original['expected_entries'],'gpu_uuid':original['gpu_uuid'],'rustc_command':command,'input_sha256':inputs,'allocation_proof':original['allocation_proof'],'parameter_schema':schemas,'fixed_gates':'D114prospective lower immutable metadata representation, D108per-kernel feasibility; exact4ABI changes and other5PTXentries; emitted u8/u16metadata loads on compute120and75. No local/spill increase, maxthread reduction or dynamic-shared increase. Actual driver occupancy/defaultlimits fit. All downstream exactness/1%/fixture/fresh16/broad/material/holdout/cumulative unchanged.','kernel_launches':0,'performance_measurement':False,'host_integration_implemented':False,'no_variants_or_retry_after_prerequisite_failure':True})
print('E070 resource protocol',old.sha(H/'protocol.json'),flush=True)
old.child([sys.executable,str(H/'execute.py'),old.sha(H/'protocol.json')],H,'manager',old.env(),500)
q=old.read(H/'report.json');passed=q['status']=='pass_resource_and_encoding_prerequisites';published=[]
for folder in [H,D]:
 for p in folder.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix in ['.json','.py','.rs','.ptx','.log']:
   key=folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
   if dst.exists():assert dst.read_bytes()==p.read_bytes()
   else:shutil.copyfile(p,dst)
   with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==p.read_bytes()
   published.append(key)
old.save(H/'publication.json',{'at':old.now(),'http_byte_verified_files':published,'all_owned_children_terminal':True,'source_unchanged':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert not any(x['id']=='E070' for x in st['experiments']);st['experiments'].append({'id':'E070','at':old.now(),'title':'Pack byte player and arity into global u16 metadata','kind':'candidate','status':'prepared' if passed else 'rejected','correctness':'CPU encoding pass; GPU numerical untested','fixture':'Four CUDAentries and12CPUplan cases','stage':'Direct numerical/host ABI preparation next' if passed else 'Closed: compiled prerequisite failed','reason':q['status']+'; no application kernel, solver timing or adoption. '+('Full host/caller integration and direct GPUcontrols remain required.' if passed else 'No width/packing/key/ABI/resource variant rescue.'),'accepted':False,'evidence':[{'label':'Prospective resource protocol','url':'evidence/E070-resource/protocol.json'},{'label':'Driver resources and PTX ABI/mechanism report','url':'evidence/E070-resource/report.json'},{'label':'CPU raw encoding replay','url':'evidence/D114-node-metadata/root-raw-replay.json'}]});st.update(updated_at=old.now(),state='running',goal_status='active',active_experiment=None,stage='E070 direct control and host ABI design' if passed else 'Next independent GPU mechanism investigation',activity='D114lossless byte encoding proof complete. E070'+('passed' if passed else 'failed')+'its frozen four-entry resource/ABI prerequisite. No new speed result or accepted gain.');old.ar.atomic_json(old.ar.STATUS,st)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D114 and E070 global node encoding' not in raw
note=f'''\n\n### D114 and E070 global node encoding\n\nPrevious goal turn completed D112/E069and resolved native execution through on-request approvals; E069failed its fixed three-pair speed/fixture gates and remains closed. Goal nowactive. D114audits a distinct immutable device encoding: current Node.player and num_children areu8, copied into two public i32CPUplan vectors and private device arrays. Proposed privateu16attributes retain high8player/low8arity and reduce this logical metadata payload8*Nto2*Nbytes, with a planned2*Ntemporary host packing vector. Public CPUplan and conservative budget formula stay unchanged. This is not E003alias/E046chance-record interleaving/E048card identity/E052shared show positions/E056orE069ordering rescue. Bounded preserved-source/current-ledger/local all-ref searches found no prior matching encoding; no exhaustive remote novelty claim.\n\nFrozen before proof:65536byte pairs plus all10774636nodes across12retained accepted E051cases. Source typing, exact decode and raw full-file replay pass;{dr['checks']}source/corpus checks and{checks}saved-record root checks;43,098,880node-raw bytes retained physicallyS. CPU/source report{old.sha(D/'report.json')}; CUDAcandidate{old.sha(S/'candidate.cu')}. Only off-tree CUDAexists; mod.rs, continuation, stored down-action ABI and actual device-capacity accounting integration are still pending. No public/save schema change planned.\n\nResourceprotocol{old.sha(H/'protocol.json')}froze exact4changed entries, both compute120/75compilation, other5PTXentries exact and typed parameter reduction/rename, narrow metadata load sites, D108per-kernel local/dynamic/maxthreads/driver-occupancy/default-limit feasibility. The smaller immutable encoding is the explicit prospective payload change, not loss of supported logical capacity; material CPU/host+GPUpeak/capacity/responsiveness requires actual qualification. Resource outcome **{q['status']}**; failed gates{json.dumps([k for k,v in q['gates'].items() if not v])}. Report{old.sha(H/'report.json')}. One no-application-kernel resource process, no production activation or solver timing. RawPTX and receipts preserved;{len(published)}artifacts HTTP-byte verified. Compiler PTX and driver attributes do not establish driverSASS, numerical equivalence, actual integrated resources or speed. All unrounded1%/strictfixture/fresh16/broad/material/holdout/cumulative gates remain unchanged; no adoption or new gain. Accepted E051/main/live/PTXunchanged, lastprimaryB225. {'Proceed to explicit four-kernel raw controls and complete host ABI design.' if passed else 'Close the exact form with no packing-width/guard/ABI/resource rescue.'}\n'''
nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+note.encode('utf-8').replace(b'\n',nl));old.custody()
subprocess.run(['git','commit','--only','-m','research: audit lossless node metadata encoding','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
old.save(H/'commit.json',{'at':old.now(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=old.REPO,text=True).strip(),'research_ledger_only':True});old.custody();print(json.dumps({'resource_status':q['status'],'report_sha256':old.sha(H/'report.json'),'published':len(published),'goal_active':True,'new_speed_gain':False}),flush=True)