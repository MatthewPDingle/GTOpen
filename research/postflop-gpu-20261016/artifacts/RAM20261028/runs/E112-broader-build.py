"""Own both frozen broader builds; restore all three source files in finally."""
import json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/E112-broader-build-plan';P=h.read(H/'protocol.json');BASE=P['accepted_source_sha256'];OUT=ROOT/'runs/E112-broader-build'
def verify():
 h.pin(H/'protocol.json',sys.argv[1])
 for p,d in P['input_sha256'].items():h.pin(p,d)
def guard(arm):
 assert h.ar.source_identity()['source_sha256']==BASE|(P['candidate_owned_sha256']if arm=='candidate'else{})
 m=h.read(h.EPOCH/'protected-main.json');main=Path(m['root']);assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()==m['git_head']
 for n,d in m['source_sha256'].items():h.pin(main/n,d)
 h.pin(m['live_path'],m['live_sha256'])
 for n in m['absent_research_paths']:assert not(main/n).exists()
 t=h.read(h.EPOCH/'preexisting-target-artifacts.json')
 for n,v in t.items():h.pin(h.REPO/n,v['sha256'])
 assert set(subprocess.check_output(['git','diff','--name-only','HEAD','--','Cargo.lock','crates/solver'],cwd=h.REPO,text=True).splitlines())==(set(P['tracked_owned_paths'])if arm=='candidate'else set())
 assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','crates/solver'],cwd=h.REPO,text=True).splitlines())==set(t)
verify();h.custody();OUT.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status())
 for arm,phase in P['arms'].items():
  verify();h.custody();h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];out=OUT/arm;out.mkdir();target=Path(phase['target']);assert not target.exists();target.mkdir()
  env=h.env();forbidden={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_RUSTC','CARGO_BUILD_RUSTC_WRAPPER','CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET','CARGO_TARGET_DIR'};assert not{k:v for k,v in env.items()if k in forbidden or k.startswith('CARGO_PROFILE_RELEASE_')or(k.startswith('CARGO_TARGET_')and k.endswith('_RUSTFLAGS'))}
  io=Path(phase['io_root']);assert not io.exists();io.mkdir(parents=True);error=None
  # Exact tracked test sources contain compile-time save paths; Cargo's normal
  # CARGO_MANIFEST_DIR is the checkout. Build the library there, then separately
  # compile only the three unchanged save harnesses with the isolated path.
  try:
   if arm=='candidate':
    for n,v in P['owned'].items():shutil.copyfile(v['candidate'],h.REPO/n)
   guard(arm);h.child(phase['command'],out,'cargo',2400);verify();guard(arm)
   rec=[json.loads(x)for x in(out/'cargo.stdout.log').read_text(encoding='utf-8').splitlines()];assert any(x.get('reason')=='build-finished'and x.get('success')is True for x in rec);arts=[x for x in rec if x.get('reason')=='compiler-artifact'];deps={p:h.sha(p)for x in arts for p in x.get('filenames',[])if Path(p).is_file()and Path(p).suffix in['.rlib','.rmeta','.lib','.dll']};tests=[x for x in arts if x.get('profile',{}).get('test')and x.get('executable')and x['target']['name']in phase['outputs']];assert len(tests)==len(phase['outputs']);pins={}
   for x in arts:
    for p in x.get('filenames',[])+([x['executable']]if x.get('executable')else[]):assert Path(p).resolve().is_relative_to(target.resolve())
   libs={}
   for n in ['solver','serde_json']:
    found=[p for p in deps if Path(p).name.startswith('lib'+n+'-')and Path(p).suffix=='.rlib'];assert len(found)==1;libs[n]=found[0]
   for test in tests:
    name=test['target']['name'];assert not test['fresh']and test['features']==phase['expected_features'];src=h.REPO/('crates/solver/src/lib.rs'if name=='solver'else'crates/solver/tests/'+name+'.rs');assert Path(test['target']['src_path']).resolve()==src.resolve();binary=ROOT/'binaries'/(phase['outputs'][name]+'.exe');assert not binary.exists();command=phase['command'];log=out/'cargo.stdout.log'
    if name in ['postflop_state_perf','postflop_action_menus','postflop_resume_state']:
     command=['rustc','--edition=2021',str(src),'--crate-name','e112_'+arm+'_'+name,'--cfg','feature="gpu"','--cfg','feature="preflop-research"','--test','-C','opt-level=3','-C','lto=thin','-C','codegen-units=1']
     for n,p in libs.items():command+=['--extern',n+'='+p]
     command+=['-L','dependency='+str(Path(libs['solver']).parent),'-o',str(binary)];prior=os.environ.get('CARGO_MANIFEST_DIR');os.environ['CARGO_MANIFEST_DIR']=str(io)
     try:h.child(command,out,'rustc-'+name,1200)
     finally:
      if prior is None:os.environ.pop('CARGO_MANIFEST_DIR',None)
      else:os.environ['CARGO_MANIFEST_DIR']=prior
     log=out/('rustc-'+name+'.stdout.log')
    else:shutil.copyfile(test['executable'],binary)
    data=binary.read_bytes();cuda=h.REPO/('crates/solver/src/preflop/gpu/kernels.cu'if name=='preflop_gpu'else'crates/solver/src/gpu/kernels.cu');assert cuda.read_bytes()in data
    manifest={**h.ar.source_identity(),'candidate':'E112'if arm=='candidate'else'E080','arm':arm,'binary_sha256':h.sha(binary),'built_at':h.now(),'build_command':command,'cargo_artifact':test,'dependency_artifact_sha256':deps,'build_protocol_sha256':sys.argv[1],'build_script_sha256':h.sha(__file__),'build_log_sha256':h.sha(log),'original_Cargo_save_harness_not_executed':name in ['postflop_state_perf','postflop_action_menus','postflop_resume_state'],'isolated_compile_time_io_root':str(io),'candidate_accepted':False,'control_only':True};h.save(binary.with_suffix('.manifest.json'),manifest)
    for p in [binary,binary.with_suffix('.manifest.json')]:pins[str(p)]=h.sha(p)
   h.save(out/'complete.json',{'at':h.now(),'source_sha256':BASE|(P['candidate_owned_sha256']if arm=='candidate'else{}),'artifact_sha256':pins,'dependency_sha256':deps,'all_compilers_terminal':True,'native_executions':0})
  except BaseException as exc:error=repr(exc);h.save(out/'failure.json',{'at':h.now(),'error':error,'native_executions':0});raise
  finally:
   if arm=='candidate':
    for n,v in P['owned'].items():assert h.sha(h.REPO/n)in[v['base_sha256'],v['candidate_sha256']];shutil.copyfile(v['base'],h.REPO/n)
   h.custody();h.save(out/'restoration.json',{'at':h.now(),'accepted_source_restored':True,'main_live_protected_PTX_unchanged':True,'error':error})
  print(arm,'broader compilers terminal; accepted source restored.',flush=True)
 h.save(OUT/'complete.json',{'at':h.now(),'all_compilers_terminal':True,'native_executions':0,'protocol_sha256':sys.argv[1],'arm_complete_sha256':{a:h.sha(OUT/a/'complete.json')for a in P['arms']}})
h.custody();print('Both matched broader builds terminal; no new native tests executed.',flush=True)
