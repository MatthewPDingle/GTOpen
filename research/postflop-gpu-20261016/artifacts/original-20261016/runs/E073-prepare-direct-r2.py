"""Freeze one fresh full raw showdown corpus for two private boundary types."""
from pathlib import Path
import ast,json,re,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
RES=R/'runs/E073-resource';D=R/'runs/D119-boundary-load-audit';S=R/'runs/E073-source';P0=old.read(RES/'protocol.json');q=old.read(RES/'report.json');a=old.read(D/'report.json')
assert a['status']=='pass_corrected_same_narrow_load_prerequisite'and all(a['gates'].values())and a['criterion_unchanged']and a['new_compilers']==a['new_resource_probes']==0
assert a['original_resource_report_sha256']==old.sha(RES/'report.json')
for p,h in P0['input_sha256'].items():old.pin(p,h)
for label in ['rustc','probe']:
 e=old.read(RES/'execution'/(label+'.exit.json'));assert e['returncode']==0 and e['error']is e['cleanup']is None
H=R/'runs/E073-kernel-control-r2';prior=R/'runs/E066-kernel-control';assert not H.exists();H.mkdir()
for n in ['accepted-evaluator.rs']:(H/n).write_bytes((prior/n).read_bytes())
for n in ['baseline.cu','candidate.cu']:(H/n).write_bytes((S/n).read_bytes())
for arm in ['baseline','candidate']:
 src=RES/'execution'/(arm+'-compute_120.ptx');old.pin(src,q['ptx_sha256'][arm+'-compute_120']);shutil.copyfile(src,H/(arm+'.ptx'))
corpus=old.read(prior/'corpus.json');changes=[]
for g in corpus['geometries']:
 b=g['arrays']['p_off'][1];end=b+g['m_p']
 for key in ['p_lower','p_upper']:
  for i,value in enumerate(g['arrays'][key]):
   if value>65535:
    assert not b<=i<end,'never change a consumed rank boundary'
    changes.append({'geometry':g['id'],'array':key,'index':i,'before':value,'after':0xD15A});g['arrays'][key][i]=0xD15A
  assert all(0<=x<=g['m_o']for x in g['arrays'][key][b:end])
assert len(corpus['geometries'])==36 and len(corpus['cases'])==364
old.save(H/'corpus.json',corpus);old.save(H/'corpus-adaptation.json',{'at':old.now(),'original_corpus_sha256':old.sha(prior/'corpus.json'),'prospective_padding_only_changes':changes,'active_boundary_words_changed':0,'case_or_geometry_count_changed':False,'purpose':'Both arms use a common representable0xD15Aguard in previously unconsumed rank-boundary padding. Original corpus retained; no E073numeric launch has occurred. All active geometry/ranks/reach/output/quality/case identities exact.','not_result_driven':True})
code=(prior/'probe.rs').read_text(encoding='utf-8').replace('E066_EXACT','E073_EXACT');code='//! E073: originalu32/privateu16boundaries, same full raw controls; no timing.\n'+code.split('\n',1)[1]
def replace(before,after):
 global code
 assert code.count(before)==1,(before[:100],code.count(before));code=code.replace(before,after,1)
replace('active:&[bool])->Result<(Vec<u32>,usize,usize,Vec<Value>)>','active:&[bool],narrow:bool)->Result<(Vec<u32>,usize,usize,Vec<Value>)>')
helper='''enum Bounds { Wide(CudaSlice<u32>), Narrow(CudaSlice<u16>) }
fn upload_bounds(s:&Arc<CudaStream>,a:&Value,key:&str,narrow:bool)->Result<(Vec<u32>,Bounds)> {
 let h=words(&a[key]);
 let device=if narrow {
  let mut values=Vec::with_capacity(h.len());
  for &value in &h {values.push(u16::try_from(value).map_err(|_| "river rank boundary exceeds u16".to_string())?);}
  let device=s.clone_htod(&values)?;s.synchronize()?;Bounds::Narrow(device)
 } else {Bounds::Wide(s.clone_htod(&h)?)};
 Ok((h,device))
}
'''
replace('fn upload_u32(',helper+'fn upload_u32(')
replace('let (pl,d_pl)=upload_u32(s,a,"p_lower")?;let (pu,d_pu)=upload_u32(s,a,"p_upper")?;','let (pl,d_pl)=upload_bounds(s,a,"p_lower",narrow)?;let (pu,d_pu)=upload_bounds(s,a,"p_upper",narrow)?;')
replace(' .arg(&d_po).arg(&d_pc).arg(&d_pi).arg(&d_pl).arg(&d_pu).arg(&d_oo).arg(&d_oc).arg(&d_oi).arg(&d_co).arg(&d_cp)',
''' .arg(&d_po).arg(&d_pc).arg(&d_pi);
 match &d_pl {Bounds::Wide(d)=>{launch.arg(d);},Bounds::Narrow(d)=>{launch.arg(d);}}
 match &d_pu {Bounds::Wide(d)=>{launch.arg(d);},Bounds::Narrow(d)=>{launch.arg(d);}}
 launch.arg(&d_oo).arg(&d_oc).arg(&d_oi).arg(&d_co).arg(&d_cp)''')
macro=''' macro_rules! check_bounds {($h:ident,$d:ident)=>{{
  let(got,raw,width):(Vec<u32>,Vec<u8>,u32)=match &$d {
   Bounds::Wide(d)=>{let v=s.clone_dtoh(d)?;let raw=v.iter().flat_map(|x|x.to_le_bytes()).collect();(v,raw,32)},
   Bounds::Narrow(d)=>{let v=s.clone_dtoh(d)?;let raw=v.iter().flat_map(|x|x.to_le_bytes()).collect();(v.into_iter().map(u32::from).collect(),raw,16)}
  };
  exact(&$h,&got,stringify!($h))?;snapshots.push(json!({"buffer":stringify!($h),"actual_device_words":got,"actual_storage_bits":width,"actual_device_bytes":raw}));checks+=1;input_words+=$h.len();
 }}}
'''
replace(' check_u!(nodes,d_nodes);',macro+' check_u!(nodes,d_nodes);')
replace('check_u!(pl,d_pl);check_u!(pu,d_pu);','check_bounds!(pl,d_pl);check_bounds!(pu,d_pu);')
replace('run_variant(&s,&bf,g,c,128,&active)?','run_variant(&s,&bf,g,c,128,&active,false)?');replace('run_variant(&s,&cf,g,c,128,&active)?','run_variant(&s,&cf,g,c,128,&active,true)?')
left=code.index(' let compile=|src:&str,name:&str|');right=code.index(' let shared_limit=',left)
code=code[:left]+''' let load_ptx=|src:&str,name:&str|->Result<_>{let mut out=OpenOptions::new().write(true).create_new(true).open(format!("{name}.ptx"))?;out.write_all(src.as_bytes())?;out.flush()?;Ok(ctx.load_module(cudarc::nvrtc::Ptx::from_src(src))?)};
 let bm=load_ptx(include_str!("baseline.ptx"),"baseline")?;let cm=load_ptx(include_str!("candidate.ptx"),"candidate")?;let bf=bm.load_function("up_show")?;let cf=cm.load_function("up_show")?;
'''+code[right:]
replace('"compile_options":"arch only, all other production defaults"','"compile_options":"No NVRTC rerun: same sealedcompute120PTX from the sole resource probe, originally arch-only production defaults"')
(H/'probe.rs').write_text(code,encoding='utf-8',newline='\n')
runner=(prior/'execute.py').read_text(encoding='utf-8').replace('E066','E073').replace("ROOT/'runs/accepted-E051'","ROOT/'runs/accepted-E051-live-20261018'").replace('import common_e051 as old','import common_e051_live as old')
runner=runner.replace('import json,re,shutil,subprocess,sys,time','import json,re,shutil,struct,subprocess,sys,time').replace('card-offset cache control','private16bit boundary control').replace('>=54*1024**3','>=66*1024**3')
before="expected={n:g['arrays'][key] for n,key in names.items()}|{'reach':case['reach_o_bits']};assert {v['buffer']:v['actual_device_words'] for v in snapshot}==expected"
after=before+'''
    for snap in snapshot:
     if snap['buffer'] in ['pl','pu']:
      width=32 if arm=='baseline'else 16;assert snap['actual_storage_bits']==width
      fmt='<I'if width==32 else'<H';assert bytes(snap['actual_device_bytes'])==b''.join(struct.pack(fmt,x)for x in expected[snap['buffer']])
''';assert runner.count(before)==1;runner=runner.replace(before,after)
before='assert snapshots[0]==snapshots[1];';after="assert [v for v in snapshots[0]if v['buffer']not in ['pl','pu']]==[v for v in snapshots[1]if v['buffer']not in ['pl','pu']];";assert runner.count(before)==1;runner=runner.replace(before,after)
needle="complete=markers[-1];";assert runner.count(needle)==1;runner=runner.replace(needle,"for arm in ['baseline','candidate']:old.pin(OUT/(arm+'.ptx'),P['sealed_PTX_sha256'][arm])\n "+needle)
needle="'all_actual_device_inputs_exact':True,";assert runner.count(needle)==1;runner=runner.replace(needle,needle+"'both_boundary_physical_byte_images_exact':True,'other19input_images_identical':True,'input_word_counter_means_logical_elements':True,'NVRTC_recompiles':0,'limits':'All full raw outputs/guards and every actual input. pl/pu physical storage differs32vs16bits; full raw bytes checked against little-endian encoding plus promoted logical words. Other19inputs identical. Same sealed resource PTX, no GPU speed/state/material/capacity claim.',")
ast.parse(runner);(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
oldP=old.read(prior/'execution-plan.json');command=[x.replace(str(prior),str(H))for x in oldP['rustc_command']]
paths=[Path(__file__),R/'runs/E073-run-direct-r2.py',*H.iterdir(),*S.iterdir(),RES/'protocol.json',RES/'report.json',D/'protocol.json',D/'report.json',D/'corrected-pointer-decoder.py',R/'runs/D118-river-boundaries/report.json',C/'common_e051_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
P={'id':'E073-kernel-control-r2','at':old.now(),'status':'FROZEN_PRE_FIRST_NUMERICAL_LAUNCH','cases':364,'kernel_launches':728,'rustc_command':command,'input_sha256':{str(p):old.sha(p)for p in paths if p.is_file()}|{p:h for p,h in oldP['input_sha256'].items()if Path(p).suffix in ['.rlib','.lib']},'source_manifest_sha256':old.sha(S/'manifest.json'),'resource_original_failure_sha256':old.sha(RES/'report.json'),'resource_corrected_same_criterion_sha256':old.sha(D/'report.json'),'sealed_PTX_sha256':{arm:old.sha(H/(arm+'.ptx'))for arm in ['baseline','candidate']},'scope':'Exactly364fresh pairs/728up_showlaunches from retained36physical geometries, both players, zeros/signedzero/subnormal/nonfinite/sNaN/rounding witnesses/countzero/tails/excess grid and immutable/guard images. Both arms128threads, same source floating recurrence. Only prospective nonconsumed boundary padding normalized to representable0xD15Ainbotharms; no active/case/reach/output change. Same sealed PTX, no NVRTC rerun, no performance result.','typed_input_contract':'Baseline2u32 boundary buffers, candidate2u16, same logical values. Actual post-device byte images of both checked independently using Pythonstruct plus promoted values;19other input images and all output/guards exact.','host_source_contract':'Direct helper mirrors production checked conversion and explicit synchronization; integrated source still requires fresh builds, whole-state/broad tests, material CPU/host+GPUpeak/capacity and full timing.','no_retries_extensions_or_source_variants':True,'performance_measured':False,'candidate_accepted':False};old.save(H/'execution-plan.json',P)
def publish(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes()
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(p)}
pub=[publish(p,H.name+'/'+p.name)for p in H.iterdir()if p.is_file()];pub.append(publish(Path(__file__),H.name+'/prepare.py'));old.save(H/'pre-execution-publication.json',{'at':old.now(),'execution_plan_sha256':old.sha(H/'execution-plan.json'),'HTTP_byte_verified_files':pub,'numeric_kernel_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E073');e.update(stage='Full raw showdown numerical controls',reason='D119corrects only cvta pointer tracing; same original32to16load criterion/resources pass. Fixed364fresh pairs compare every output/input/guard, including actual32/16bit boundary byte images. Original padding is prospectively normalized only outside consumed spans inbotharms. No solve or speed result.');e['evidence'].append({'label':'Frozen full raw typed-input control','url':'evidence/E073-kernel-control-r2/execution-plan.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E073',stage='E073 full raw numerical control',activity='Testing364original/candidate showdown pairs using the same sealed PTX. All actual immutable buffers/output/guards checked. E051accepted/deployed gain12.44%unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'execution-plan.json'),'cases':364,'launches':728,'padding_only_changes':len(changes),'active_boundaries_changed':0,'application_kernel_executions':0}),flush=True)
