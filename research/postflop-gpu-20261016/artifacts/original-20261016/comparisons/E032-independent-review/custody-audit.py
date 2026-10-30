from pathlib import Path
import json,hashlib,datetime,re,subprocess
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016'); Q=Path(r'X:\Dev\GTOpen-gpu-research-20261016'); O=R/'comparisons/E032-independent-review'; pins={}; checks=[]
def ck(x,s):
 assert x,s
 checks.append(s)
def pin(p,h=None):
 p=Path(p);v=hashlib.sha256(p.read_bytes()).hexdigest()
 if h:ck(v==h,'hash '+str(p))
 pins[str(p)]=v;return v
def read(p):pin(p);return json.loads(Path(p).read_text(encoding='utf-8'))
def dt(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
D=R/'runs/E032-design';P=R/'runs/E032-primary-plan';B=R/'runs/E032-build';S=R/'runs/E032-source';E=R/'runs/E032-primary-execution'
for p,h in [(D/'manifest.json','a8118cb83b89b1cef59f45443b98345eba4b49771d0fdcc9cf6e2e7b564b1b40'),(P/'scripts-manifest.json','b3690242063acc2f8160a21e0266923ed9d04bcad4e0cf825c551126bab5940a'),(P/'authorization.json','e6a2655a8a3d396fc849f87a1885faa4853ae62475dd6f1e5b74aed23fd7792e'),(S/'activation.json','cd65adb7c3dd03902206c36f6cb714dfdd7299cf6766d3348e00ddcc6913bd84'),(S/'cleanup.json','4ac0e452c94ceb1ffb955b0dab67db4969d0f72346bdf1dd3d015e4308db2024')]:pin(p,h)
d=read(D/'manifest.json');ss=read(P/'scripts-manifest.json');a=read(P/'authorization.json');pr=read(P/'protocol.json')
for folder,m,buckets in [(D,d,['artifact_sha256']),(P,ss,['script_sha256','supporting_sha256'])]:
 for b in buckets:
  for n,h in m[b].items():pin(folder/n,h)
 for n,h in m['reference_sha256'].items():pin(n,h)
for n,h in a['evidence_sha256'].items():pin(n,h)
ck(all(a[k] is True for k in ['E020_accepted','E020_server_qualification_pass','independent_source_review_pass','independent_script_review_pass']),'authorization gates')
base=read(R/'binaries/E020-postflop_autoresearch.manifest.json')['source_sha256'];candidate=base|d['candidate_owned_sha256'];owned='crates/solver/src/gpu/mod.rs'
ck(len(base)==162 and set(d['candidate_owned_sha256'])=={owned},'162 entries sole host delta')
act=read(S/'activation.json');cl=read(S/'cleanup.json');before=read(B/'source-before.json')
ck(act['before']['source_sha256']==base and act['after']['source_sha256']==candidate and before['source_sha256']==candidate,'activation and build source custody')
ck(cl['before']['source_sha256']==candidate and cl['after']['source_sha256']==base,'cleanup source custody')
for p in [D/'candidate/mod.rs',B/'candidate-mod.rs',S/'rejected/mod.rs']:pin(p,candidate[owned])
for p in [D/'base/mod.rs',S/'base/mod.rs']:pin(p,base[owned])
for p in [S/'activated.patch',S/'rejected.patch',B/'candidate.patch',R/'runs/E032R1.patch']:pin(p,act['patch_sha256'])
for n,h in base.items():pin(Q/n,h)
ck(cl['all162_accepted_exact'] and cl['decision']=='rejected' and not cl['extra_native_runs'] and not cl['broader_or_cumulative_authorized'],'restoration/no extra authorization')
main=Path(r'X:\Dev\GTOpen');live=main/'target/desktop-runtime/release/gto-server.exe'
ck(subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()==act['main_head']==cl['main_head']=='ae823c8bd6d723c75e096da139fd638d7dd397eb','main HEAD unchanged')
pin(live,act['live_binary_sha256']);ck(cl['live_binary_sha256']==pins[str(live)]=='b7b808b8baff6b3a92c4f3cc8c54ee74ee2c0bb079a8ca68be4da9703f6b84bd','live binary unchanged')
be=read(B/'exit.json');env=read(B/'build-environment.json');ck(be['returncode']==0 and be['error'] is None and be['command']==pr['build_command'],'build terminal and command')
ck(env['target_previously_absent'] and not env['compiler_override_absence'] and env['RAYON_NUM_THREADS']=='16','fresh target/override absence');target=Path(env['target_dir']).resolve();ck(target==(R/'build-e032-primary').resolve(),'target path')
records=[json.loads(x) for x in (B/'build.jsonl').read_text(encoding='utf-8').splitlines()];pin(B/'build.jsonl');pin(B/'build.stderr.log')
ck([x['success'] for x in records if x.get('reason')=='build-finished']==[True],'one Cargo terminal success');ck(not [x for x in records if x.get('reason')=='compiler-message' and x['message']['level']=='error'],'no compiler error')
arts=[x for x in records if x.get('reason')=='compiler-artifact']
for x in arts:
 for f in x.get('filenames',[])+([x['executable']] if x.get('executable') else []):ck(Path(f).resolve().is_relative_to(target),'artifact under target')
sol=[x for x in arts if x['target']['name']=='solver' and x['target']['kind']==['lib'] and not x['profile']['test']];ck(len(sol)==1 and not sol[0]['fresh'] and sol[0]['features']==['gpu'],'fresh gpu solver')
cuda=(Q/'crates/solver/src/gpu/kernels.cu').read_bytes();binary_info={}
for name in ['E032-solver','E032-postflop_autoresearch']:
 mp=R/'binaries'/(name+'.manifest.json');m=read(mp);bp=R/'binaries'/(name+'.exe');pin(bp,m['binary_sha256'])
 ck(m['source_sha256']==candidate and m['source_matches_prebuild'],'candidate binary source '+name)
 ck(m['probe_authorization_sha256']==pins[str(P/'authorization.json')] and m['primary_protocol_sha256']==pins[str(P/'protocol.json')] and m['build_script_sha256']==pins[str(P/'build.py')] and m['build_command']==be['command'],'binary authorization/build '+name)
 x=m['cargo_artifact'];ck(m['solver_artifact']==sol[0] and x in arts and not x['fresh'] and x['features']==['gpu'],'actual fresh artifact '+name)
 ck(Path(x['target']['src_path']).resolve()==(Q/('crates/solver/src/lib.rs' if name=='E032-solver' else 'crates/solver/tests/postflop_autoresearch.rs')).resolve() and Path(x['manifest_path']).resolve()==(Q/'crates/solver/Cargo.toml').resolve(),'artifact paths '+name)
 pin(x['executable'],m['binary_sha256'])
 for key in ['build_log','build_stderr_log','patch']:pin(m[key],m['build_stderr_sha256'] if key=='build_stderr_log' else m[key+'_sha256'])
 for f,h in m['dependency_artifact_sha256'].items():pin(f,h)
 ck(cuda in bp.read_bytes() and m['accepted_cuda_present'] and m['unchanged_cuda_sha256']==pins[str(Q/'crates/solver/src/gpu/kernels.cu')],'unchanged CUDA embedded '+name)
 binary_info[name]={'binary_sha256':m['binary_sha256'],'manifest_sha256':pins[str(mp)],'features':x['features'],'fresh':x['fresh']}
ref=R/'binaries/E020-postflop_autoresearch.exe';pin(ref,pr['reference_binary_sha256']);ck(cuda in ref.read_bytes(),'baseline accepted CUDA embedded')
order=['V032-unit','B101','E032R1','E032R2','B102','B103','E032R3'];inv=read(E/'invocation.json');ck(inv['order']==pr['order']==order and inv['source_sha256']==candidate,'primary fixed order/source')
ck(dt(act['at'])<=dt(be['at'])<=dt(inv['at']),'activation/build before primary');prev=dt(inv['at']);chron=[];nr=nc=0;hits=[]
for identity in order:
 wi=read(E/(identity+'.invocation.json'));we=read(E/(identity+'.exit.json'));r=read(R/'runs'/identity/'report.json');rp=R/'runs'/identity/'stdout.log';pin(rp,r['stdout_sha256']);raw=rp.read_text(encoding='utf-8')
 ck(we['returncode']==0 and we['error'] is None and r['returncode']==0 and r['status']=='measured','terminal '+identity)
 ck(prev<=dt(wi['at'])<=dt(r['started_at'])<=dt(r['process_started_at'])<=dt(r['finished_at'])<=dt(we['at']),'chronology '+identity);prev=dt(we['at'])
 name='E032-solver' if identity=='V032-unit' else ('E020-postflop_autoresearch' if identity.startswith('B') else 'E032-postflop_autoresearch');bp=R/'binaries'/(name+'.exe');mp=R/'binaries'/(name+'.manifest.json')
 cmd=[str(bp),'--nocapture','--test-threads=1'] if identity=='V032-unit' else [str(bp),'postflop_complete_cycle','--nocapture','--test-threads=1','--ignored']
 ck(r['command']==cmd and r['binary_sha256']==pin(bp),'native executable/command '+identity)
 bm=r['binary_build_manifest'];ck(bm['path']==str(mp) and bm['sha256']==pin(mp) and bm['data']==json.loads(mp.read_text(encoding='utf-8')),'native build manifest '+identity)
 ck(r['provenance']['source_sha256']==candidate,'contemporary source '+identity)
 ck(r['environment']=={'RAYON_NUM_THREADS':'16','nvrtc_path':r'X:\Dev\GTOpen\.cuda-nvrtc\nvidia\cuda_nvrtc\bin','POSTFLOP_AUTORESEARCH_FIXTURE':None,'POSTFLOP_AUTORESEARCH_STORAGE':'compressed','POSTFLOP_AUTORESEARCH_PROFILE':'0'},'environment '+identity)
 for key in ['live_status_before','live_status_at_launch']:
  v=r[key];ck(v['/api/status']['state']=='idle' and v['/api/preflop/status']['state'] in ('','idle') and not v['/api/reports/status']['running'],'live idle '+identity+key)
 ck(r['disk_free_bytes']>=50*1024**3,'disk reserve '+identity)
 sums=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)
 ck(sums==([('85','0','4','0','0')] if identity=='V032-unit' else [('1','0','0','0','0')]),'test summary '+identity)
 if identity=='V032-unit':ck('test gpu::tests::training_terminal_consolidation_covers_lists_and_falls_back ... ok' in raw,'new test actually passed')
 else:
  rr=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in raw.splitlines() if 'AUTORESEARCH_RESULT ' in x];ck(rr==r['results'] and len(rr)==3,'raw/report result '+identity);nr+=len(rr)
  stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in raw.splitlines() if 'AUTORESEARCH_STAGE ' in x];nc+=sum(s.get('stage')=='convergence_check' for s in stages)
 for path in [rp,E/(identity+'.stdout.log'),E/(identity+'.stderr.log')]:
  pin(path);hits += [{'file':str(path),'line':x[:200]} for x in path.read_text(encoding='utf-8').splitlines() if re.search(r'Traceback|panicked at|CUDA_ERROR_|^error:',x)]
 chron.append({'id':identity,'start':r['process_started_at'],'finish':r['finished_at'],'binary_sha256':r['binary_sha256']})
complete=read(E/'complete.json');ai=read(R/'runs/E032-assessment/invocation.json');ae=read(R/'runs/E032-assessment/exit.json')
ck(complete['order']==order and prev<=dt(complete['at'])<=dt(ai['at'])<=dt(ae['at'])<=dt(cl['at']) and ae['returncode']==0,'complete/assessment/cleanup chronology')
ck('--reject' in ai['command'] and nr==18 and nc==138 and not hits,'reject/retained18and138/error scans')
comp=read(R/'comparisons/E032-three-pair-comparison/report.json');ck(comp['decision']=='rejected' and not comp['accepted'] and not comp['deployed'] and comp['excluded_runs']==[],'no acceptance/exclusion/deployment')
for p in (R/'runs/E032-assessment').iterdir():
 if p.is_file():pin(p)
ck(not (R/'gpu-run.lock').exists(),'terminal lock absent')
result={'id':'E032-source-custody','verdict':'PASS_SOURCE_BUILD_CUSTODY_AND_RESTORATION','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks_passed':len(checks),'input_sha256':pins,'candidate_owned_sha256':d['candidate_owned_sha256'],'binary_custody':binary_info,'chronology':chron,'raw_results_retained':nr,'raw_convergence_checks_retained':nc,'unit_summary':[85,0,4,0,0],'accepted_source_entries_restored':162,'unchanged_cuda':True,'main_head_unchanged':True,'live_binary_unchanged':True,'failure_scan_hits':hits,'scope':'File-only custody audit; numerical equality/gates separately reviewed. Baseline runs correctly recorded candidate working source but retained immutable E020 binary/manifests. No feature/direct/resource prerequisite for this host-only experiment.','reviewer_notes':['Exploratory read looked for nonexistent runs/B101/invocation.json; actual records are E032-primary-execution/*.invocation.json. Corrected, no mutation.','First attempt to save this auditor failed because its output directory did not yet exist; created only the authorized review directory and saved the auditor. No evidence was overwritten.'],'reviewer_correction_artifact':'custody-reviewer-correction.json','native_or_compiler_execution_by_auditor':False,'production_or_status_changed_by_auditor':False,'candidate_accepted':False,'deployment_changed':False}
p=O/'source-custody.json'
with p.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'verdict':result['verdict'],'checks':len(checks),'pins':len(pins),'report_sha256':pin(p)},indent=2))
