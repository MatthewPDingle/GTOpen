import sys,ast,shutil,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=50*1024**3
RES=R/'runs/E089-resource';q=old.read(RES/'report.json')
assert q['status']=='pass_compiled_serial_card_loop_prerequisites'and all(q['gates'].values())
for label in ['rustc','probe']:
 x=old.read(RES/'execution'/(label+'.exit.json'));assert x['returncode']==0 and x['error']is x['cleanup']is None
S=R/'runs/E089-source';prior=R/'runs/E084-kernel-control';H=R/'runs/E089-kernel-control';H.mkdir(exist_ok=False)
for n in ['baseline.cu','candidate.cu']:shutil.copyfile(S/n,H/n)
for arm in ['baseline','candidate']:
 p=RES/'execution'/(arm+'-compute_120.ptx');old.pin(p,q['ptx_sha256'][arm+'-compute_120']);shutil.copyfile(p,H/(arm+'.ptx'))
for n in ['corpus.json','accepted-evaluator.rs']:shutil.copyfile(prior/n,H/n)
assert len(old.read(H/'corpus.json')['cases'])==364
for name in ['probe.rs','execute.py','audit.py']:
 t=(prior/name).read_text(encoding='utf-8').replace('E084','E089')
 t=t.replace('pass_compiled_first_card_total_prerequisites','pass_compiled_serial_card_loop_prerequisites').replace('pass_scoped_full_first_card_total_raw_equivalence','pass_scoped_full_serial_card_loop_raw_equivalence').replace('first-card-total-cache','serial-card-loop').replace('first-card-total','serial-card-loop')
 if name.endswith('.py'):ast.parse(t)
 (H/name).write_bytes(t.encode())
P0=old.read(prior/'protocol.json');deps={p:h for p,h in P0['input_sha256'].items()if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']}
files=[Path(__file__),RES/'protocol.json',RES/'report.json',RES/'execution/complete.json',C/'common_e080_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[p for folder in [S,H]for p in folder.iterdir()if p.is_file()]]
P={'id':'E089-kernel-control','at':old.now(),'status':'FROZEN_PRE_FIRST_APPLICATION_KERNEL','rustc_command':[x.replace(str(prior),str(H))for x in P0['rustc_command']],'input_sha256':deps|{str(p):old.sha(p)for p in files},'resource_report':str(RES/'report.json'),'widths':[1,32,64,128,256],'base_cases':364,'geometries':36,'expected_pairs':1820,'expected_application_launches':3640,'sealed_PTX_sha256':{a:old.sha(H/(a+'.ptx'))for a in ['baseline','candidate']},'scope':'Reuse all original364physicalshowdowncases x5widths, full21actualimmutablebuffersandwholephysicalCFV/guards. Onecompiler/one fixedGPUprocess then independentrawreader. Source/math/descriptors/order/inputs/expected/tolerancesunchanged; no NVRTC/resource rerun/sourceactivation/solve/performance. Failclosesexactcandidate; nofactor/body/helper/placement/subset/width/sourcevariant ormoreGPU samples.','candidate_accepted':False,'performance_measurement':False}
old.save(H/'protocol.json',P)
pub=[]
for folder in [RES,H]:
 for p in folder.rglob('*'):
  if not p.is_file()or p.suffix not in ['.rs','.cu','.py','.json','.log','.patch']:continue
  key=folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'protocol_sha256':old.sha(H/'protocol.json'),'application_kernel_launches':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E089')
 x.update(stage='Full raw showdown accuracy controls',correctness='resource_pass',reason='Actualshaderbody smaller120/75; registers38to40,local0/static1040/dynamic22600/128threadresidency4/max1024unchanged. Run original1820rawpairs; no speedclaim.')
 x['evidence'] += [{'label':'Compiled resource observations','url':'evidence/E089-resource/report.json'},{'label':'Frozen raw accuracy matrix','url':'evidence/E089-kernel-control/protocol.json'}]
 s.update(updated_at=old.now(),stage='E089 full raw GPU accuracy controls',activity='Compiledloopbody shrank and resource prerequisite passed. Check1820original/candidatepairs acrossfivewidths,wholeoutputs/inputs/guards. Speedunproven;E080live.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(old.sha(H/'protocol.json'),flush=True)
