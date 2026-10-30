from pathlib import Path
import json,hashlib,re,datetime
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
D=R/'runs/D057-evaluation-envelope-diagnostic';OUT=R/'comparisons/D057-independent-review'
checks=[];pins={}
def ok(value,label):
    assert value,label
    checks.append(label)
def pin(path,expected=None):
    p=Path(path);v=hashlib.sha256(p.read_bytes()).hexdigest()
    if expected is not None:ok(v==expected,'hash '+str(p))
    pins[str(p)]=v;return v
def read(path):
    pin(path);return json.loads(Path(path).read_text(encoding='utf-8'))
def dt(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def main():
    auth=read(D/'authorization.json');pin(D/'authorization.json','1dd1e554430ea2efc09b2602d214a15374bfa260e8ef40a86887fc98c50db62e')
    seal=read(D/'scripts-manifest.json');pin(D/'scripts-manifest.json','13cde2af0e067cdee23cecd2579212335bffc6168b83907457c5ac21f5470c87')
    for k,v in seal['script_sha256'].items():pin(D/k,v)
    for k,v in seal['reference_sha256'].items():pin(k,v)
    for k,v in auth['evidence_sha256'].items():pin(k,v)
    for v in auth['candidate_sources'].values():pin(v['path'],v['sha256'])
    ok(auth['candidate']=='D057' and auth['source_archive']=='source/r2' and auth['actual_native_invocations']==1 and auth['no_extension'] is True,'root fixed single diagnostic authorization')
    accepted=read(R/'binaries/E020-postflop_autoresearch.manifest.json')
    bm=read(R/'binaries/D057-solver.manifest.json');src=bm['source_sha256']
    pre=read(R/'runs/D057-build/source-before.json');inv=read(R/'runs/D057-execution/invocation.json')
    native=read(R/'runs/D057R1/report.json');report=read(R/'comparisons/D057-evaluation-envelope-diagnostic/report.json')
    pin(R/'comparisons/D057-evaluation-envelope-diagnostic/report.json','ac6f63332bb3d0c512a7096cb3c1c8fee8de138e6a0c5129c9e90e9c241be350')
    activation=read(R/'runs/D057-root-decisions/activation.json');start=read(R/'runs/D057-root-decisions/pre-execution-state.json')
    cleanup=read(R/'runs/D057-source/cleanup.json');pin(R/'runs/D057-source/cleanup.json','2b1c5cd223d3244e8066a52d8cdfcb35b3045ab2c190ac26dee6fda887e1827f')
    ok(len(src)==163 and src==pre['source_sha256']==inv['source_sha256']==native['provenance']['source_sha256']==cleanup['candidate_source_sha256'],'163 source maps identical before/build/invocation/native/custody')
    owned=set(auth['candidate_sources']);expected=dict(accepted['source_sha256']);expected.update({k:v['sha256'] for k,v in auth['candidate_sources'].items()})
    ok(src==expected and len(owned)==2,'only two authorized test paths differ from accepted162')
    for k in owned:
        v=bm['source_copies'][k];pin(v['path'],src[k]);pin(bm['candidate_sources'][k]['path'],src[k]);pin(R/'runs/D057-source'/Path(k).name,src[k])
    pin(bm['patch'],bm['patch_sha256']);pin(R/'runs/D057-source/candidate.patch',bm['patch_sha256'])
    ok(bm['source_matches_prebuild'] is True and bm['test_only_append_verified'] is True,'build source equality and append-only declaration recorded')
    for k,v in accepted['source_sha256'].items():pin(REPO/k,v)
    ok(cleanup['source_sha256']==accepted['source_sha256'] and cleanup['source_entries_restored']==162 and cleanup['accepted_source_exact'] is True,'cleanup accepted162 map exact')
    ok(not (REPO/'crates/solver/src/gpu/evaluation_device_events.rs').exists() and cleanup['owned_helper_removed'] and cleanup['only_owned_paths_restored'],'temporary helper removed; only owned restoration')
    ok(cleanup['main_head']==start['main_head'],'recorded main HEAD unchanged')
    ok(cleanup['live_executable']==start['live_executable'] and cleanup['live_executable_sha256']==start['live_executable_sha256']=='b7b808b8baff6b3a92c4f3cc8c54ee74ee2c0bb079a8ca68be4da9703f6b84bd','exact desktop live path and hash unchanged')
    pin(cleanup['live_executable'],cleanup['live_executable_sha256'])
    env=read(R/'runs/D057-build/build-environment.json');be=read(R/'runs/D057-build/exit.json');ne=read(R/'runs/D057-execution/exit.json');done=read(R/'runs/D057-execution/complete.json')
    ok(env['target_previously_absent'] is True and env['compiler_override_absence']=={} and env['RAYON_NUM_THREADS']=='16','fresh target and absent compiler overrides recorded')
    ok(be['returncode']==ne['returncode']==native['returncode']==0 and be['error'] is None and ne['error'] is None,'build and sole native runner terminal zero')
    ok(be['cleanup'] is None and ne['cleanup'] is None and done['native_test_pass'] is True,'no process-error cleanup and selected test completed')
    cmd=['cargo','test','--release','--locked','--offline','-p','solver','--features','gpu','--lib','--no-run','--message-format=json']
    ok(bm['build_command']==be['command']==cmd,'exact locked offline GPU-only compile command')
    pin(bm['build_log'],bm['build_log_sha256']);pin(bm['build_stderr_log'],bm['build_stderr_sha256'])
    records=[json.loads(l) for l in Path(bm['build_log']).read_text(encoding='utf-8').splitlines() if l.strip()]
    artifacts=[x for x in records if x.get('reason')=='compiler-artifact'];target=Path(bm['target_dir']).resolve()
    for x in artifacts:
        for f in x.get('filenames',[]):ok(Path(f).resolve().is_relative_to(target),'Cargo target-contained '+Path(f).name)
    units=[x for x in artifacts if x.get('profile',{}).get('test') and x.get('executable') and x['target']['name']=='solver']
    ok(len(units)==1 and units[0]==bm['cargo_artifact'] and units[0]['fresh'] is False and units[0]['features']==['gpu'],'one freshly compiled solver GPU-only unit executable')
    ok(units[0]['manifest_path']==str(REPO/'crates/solver/Cargo.toml') and units[0]['target']['src_path']==str(REPO/'crates/solver/src/lib.rs'),'actual Cargo package/source paths')
    ok(records[-1]=={'reason':'build-finished','success':True},'Cargo terminal success record')
    ok(not any(x.get('reason')=='compiler-message' and x.get('message',{}).get('level')=='error' for x in records),'no compiler error records')
    for k,v in bm['dependency_artifact_sha256'].items():pin(k,v)
    binary=R/'binaries/D057-solver.exe';bh=pin(binary,'608d6436ef39596a10ca2c2e1f2eaa51809f25ec2472bfab82026351ce8eac77');pin(units[0]['executable'],bh)
    blob=binary.read_bytes();cuda=(REPO/'crates/solver/src/gpu/kernels.cu').read_bytes()
    ok(blob.count(cuda)==1 and b'D057_EVAL_DIAGNOSTIC' in blob,'binary contains exact accepted CUDA once and D057 marker')
    ok(native['binary_sha256']==inv['binary_sha256']==bm['binary_sha256']==report['binary_sha256']==bh,'binary identity all records')
    ok(native['binary_build_manifest']['data']==bm and native['binary_build_manifest']['binary_hash_verified'] is True,'native embedded build manifest exact and binary verified')
    pin(native['binary_build_manifest']['path'],native['binary_build_manifest']['sha256']);ok(inv['build_manifest_sha256']==native['binary_build_manifest']['sha256'],'invocation/native manifest identity')
    ok(bm['probe_authorization_sha256']==inv['authorization_sha256']==pins[str(D/'authorization.json')],'authorization bound at build and invocation')
    ok(bm['primary_protocol_sha256']==inv['protocol_sha256']==report['protocol_sha256']==seal['protocol_sha256'],'fixed protocol bound through assessment')
    ok(bm['build_script_sha256']==seal['script_sha256']['build.py'] and inv['script_sha256']==seal['script_sha256']['run.py'],'executed script hashes match sealed scripts')
    ok(dt(auth['at'])<dt(activation['at'])<dt(bm['built_at'])<=dt(inv['at'])<=dt(native['process_started_at'])<=dt(native['finished_at'])<dt(report['created_at'])<dt(cleanup['at']),'authorization activation build native assessment restoration chronology')
    ok(native['id']==inv['actual_run']==done['actual_run']=='D057R1' and native['kind']=='diagnostic' and native['fixture']=='two-tone','one registered D057R1 two-tone diagnostic')
    ok(native['command']==[str(binary),'gpu::evaluation_device_events::captured_evaluation_envelope_diagnostic','--nocapture','--test-threads=1','--ignored'],'exact selected ignored test command')
    ok(native['environment']=={'RAYON_NUM_THREADS':'16','nvrtc_path':r'X:\Dev\GTOpen\.cuda-nvrtc\nvidia\cuda_nvrtc\bin','POSTFLOP_AUTORESEARCH_FIXTURE':'two-tone','POSTFLOP_AUTORESEARCH_STORAGE':'compressed','POSTFLOP_AUTORESEARCH_PROFILE':'0'},'fixed native environment')
    for k in ['live_status_before','live_status_at_launch']:
        v=native[k];ok(v['/api/status']['state']=='idle' and v['/api/preflop/status']['state'] in ['', 'idle'] and v['/api/reports/status']['running'] is False,'recorded live idle '+k)
    ok(native['disk_free_bytes']>=54*1024**3,'native disk reserve')
    rawpath=R/'runs/D057R1/stdout.log';pin(rawpath,native['stdout_sha256']);raw=rawpath.read_text(encoding='utf-8')
    summaries=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)
    ok(summaries==[('1','0','0','0','88')] and native['test_pass_count']==1,'single native selected-test summary 1/0/0/0/88')
    markers=[json.loads(l.split('D057_EVAL_DIAGNOSTIC ',1)[1]) for l in raw.splitlines() if 'D057_EVAL_DIAGNOSTIC ' in l]
    ok(len(markers)==22 and markers[-1]['stage']=='complete' and markers[-1]['checked_cleanup'] is True,'22 markers and checked-cleanup terminal marker')
    for rel in ['runs/D057R1/stdout.log','runs/D057-execution/stdout.log','runs/D057-execution/stderr.log','runs/D057-build/build.stderr.log']:
        p=R/rel;pin(p);t=p.read_text(encoding='utf-8')
        ok(not any(x in t for x in ['panicked at','D057_EVENT_CLEANUP_ERROR','D057_SOLVER_CLEANUP_ERROR','test result: FAILED']),'no panic/test/cleanup failure in '+rel)
    ok((R/'runs/D057-execution/stderr.log').stat().st_size==0,'orchestration stderr empty; native stderr merged in hashed stdout by sealed runner')
    am=read(R/'comparisons/D057-evaluation-envelope-diagnostic/manifest.json')
    for k,v in am['files'].items():pin(R/'comparisons/D057-evaluation-envelope-diagnostic'/k,v)
    ok(am['files']['assessor.py']==seal['script_sha256']['assess.py'],'actual copied assessor equals reviewed script')
    ok(report['candidate_accepted'] is False and report['deployment_changed'] is False and report['accepted_performance_claim'] is False and report['extension_allowed'] is False,'diagnostic scope/no performance acceptance/deployment/extension')
    result={'id':'D057','verdict':'PASS_SOURCE_BUILD_RUN_AND_RESTORATION_CUSTODY','custody_pass':True,'source_entries_built':163,'source_entries_restored':162,'native_invocations_observed':1,'native_test_counts':{'passed':1,'failed':0,'ignored':0,'measured':0,'filtered':88},'binary_sha256':bh,'assessment_sha256':pins[str(R/'comparisons/D057-evaluation-envelope-diagnostic/report.json')],'cleanup_sha256':pins[str(R/'runs/D057-source/cleanup.json')],'current_candidate_pre_restore_observation':'Reviewer verified all163 active source hashes and both exact build/archive copies before notifying root restoration could proceed. This script independently verifies retained maps/copies after restoration.','numerical_audit':'Separately assigned; this custody report does not recompute numerical anchors or timing usefulness.','no_performance_claim':True,'candidate_accepted':False,'deployment_changed':False,'reviewer_native_or_gpu_execution':False,'reviewer_failures':[],'checks_passed':checks,'input_sha256':pins,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    pin(__file__);result['input_sha256']=pins
    out=OUT/'custody-validation.json'
    with out.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'verdict':result['verdict'],'checks':len(checks),'pins':len(pins),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
