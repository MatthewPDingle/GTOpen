"""Root-only phases for the sealed E020 wide-turn holdout. Never edits checkout."""
from pathlib import Path
import argparse, ctypes, datetime, hashlib, importlib.util, json, math, os, re, shutil, signal, statistics, struct, subprocess, sys, time

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
STATUS=Path(r'X:\Dev\GTOpen\web\research\postflop-gpu-20261016\status.json')
TARGET=ROOT/'build-holdout-e020'
ORDER=['B1','C1','C2','B2','B3','C3']
TIMINGS={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
COMPILER_KEYS={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER',
 'CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_RUSTC','CARGO_BUILD_RUSTC_WRAPPER','CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET'}
def compiler_overrides(environment):
    return {key:value for key,value in environment.items() if key in COMPILER_KEYS or key.startswith('CARGO_PROFILE_RELEASE_') or (key.startswith('CARGO_TARGET_') and key.endswith('_RUSTFLAGS'))}

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def pin(record):
    path=Path(record['path']);assert sha(path)==record['sha256'],path
    return path
def binary_equal(a,b):
    if a.stat().st_size!=b.stat().st_size:return False
    with a.open('rb') as left,b.open('rb') as right:
        while True:
            x=left.read(1024*1024);y=right.read(1024*1024)
            if x!=y:return False
            if not x:return True
def raw_layout(path,result):
    # Independent structural decoder: validates all frames, lengths and EOF.
    rows=[]
    with path.open('rb') as f:
        magic=b'GTO-WIDE-RAW-v1\0'
        assert f.read(len(magic))==magic
        n=struct.unpack('<Q',f.read(8))[0];assert n<65536
        meta=json.loads(f.read(n))
        expected={k:result[k] for k in ['algorithm','iteration','use_isomorphism','exploit_bits']}
        assert meta==expected
        arenas=result['state_fingerprint']['arenas']
        assert [(a['player'],a['arena'],a['kind']) for a in arenas]==[
            (0,'regrets','i16'),(0,'strategy_sums','u16'),(1,'regrets','i16'),(1,'strategy_sums','u16')]
        for arena in arenas:
            header=f.read(19);assert len(header)==19
            player,which,kind,entries,scales=struct.unpack('<BBBQQ',header)
            assert player==arena['player']
            assert which=={'regrets':0,'strategy_sums':1}[arena['arena']]
            assert kind=={'f32':0,'i16':1,'u16':2}[arena['kind']]
            assert entries==arena['entries'] and scales==arena['scale_entries']
            payload=entries*(4 if kind==0 else 2)+scales*4
            assert f.tell()+payload<=path.stat().st_size
            f.seek(payload,1);rows.append({'player':player,'arena':which,'kind':kind,'entries':entries,'scales':scales,'payload_bytes':payload})
        assert len(rows)==4 and f.read(1)==b''
    return {'metadata':meta,'frames':rows,'bytes':path.stat().st_size,'sha256':sha(path)}
def markers(path,tag):
    rows=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        match=re.search(re.escape(tag)+r'\s+',line)
        if match:rows.append(json.loads(line[match.end():]))
    return rows
def native_pass(path,name):
    text=path.read_text(encoding='utf-8')
    assert re.search(r'test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;',text),name
    assert name in text and 'FAILED' not in text

def main():
    def interrupted(signum, _frame):raise KeyboardInterrupt(f'received signal {signum}')
    for sig in [signal.SIGTERM, getattr(signal,'SIGBREAK',None)]:
        if sig is not None:signal.signal(sig,interrupted)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['build','resource','cohort'])
    parser.add_argument('--authorization',required=True,type=Path)
    parser.add_argument('--authorization-sha256',required=True)
    args=parser.parse_args()
    assert sha(args.authorization)==args.authorization_sha256
    authorization=read(args.authorization)
    assert authorization['candidate']=='E020'
    assert authorization['primary_audit_pass'] is True and authorization['holdout_source_review_pass'] is True
    for record in authorization['required_evidence']:pin(record)
    prepared=read(HERE/'prepared-manifest.json')
    assert authorization['prepared_manifest_sha256']==sha(HERE/'prepared-manifest.json')
    primary=read(HERE/'primary-audit-validation.json')
    assert primary['verdict']=='CONFIRMED_PROVISIONAL_QUALIFYING'
    assert primary['primary']['aggregate_gate_met'] is True and primary['primary']['fixture_guard_failed'] is False
    assert primary['all18_complete_non_timing_results_exact'] is True and primary['all_convergence_trajectories_exact'] is True
    spec=importlib.util.spec_from_file_location('wide_holdout_primitives',HERE/'runner-primitives-source.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.REPO=REPO
    out=HERE/args.phase
    def verify():
        assert sha(args.authorization)==args.authorization_sha256
        for record in authorization['required_evidence']:pin(record)
        for name,h in prepared['artifact_sha256'].items():assert sha(HERE/name)==h,name
        for name,h in prepared['nvrtc_dll_sha256'].items():assert sha(Path(runner.NVRTC)/name)==h,name
        for name,h in read(HERE/'protected-checkout.json').items():assert sha(REPO/name)==h,name
        if args.phase in ('resource','cohort'):
            all_builds_ready()
        if args.phase=='cohort':
            resource_path=pin(authorization['resource_report'])
            assert resource_path.resolve()==(HERE/'resource/report.json').resolve()
            resource=read(resource_path)
            assert resource['status']=='pass' and resource['scope']=='actual holdout compiler/resource feasibility only'
            assert resource['all_builds_ready']['sha256']==authorization['all_builds_ready']['sha256']
    def heartbeat(stage,seconds=0):
        # Best effort only. Never unwind/release the GPU lock because a reader
        # briefly denies Windows atomic replacement while a child remains alive.
        try:
            with runner.exclusive_lock(STATUS.with_suffix('.lock'),timeout=3):
                status=read(STATUS)
                status.update(updated_at=runner.now(),stage='E020 wide-turn holdout',
                  activity=f'E020 holdout {stage}; {seconds:.0f}s. Additional non-regression evidence; accepted gain and deployment unchanged.')
                runner.atomic_json(STATUS,status)
        except Exception as error:
            try:
                with (out/'heartbeat-errors.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'at':now(),'error':repr(error)})+'\n')
            except Exception:pass
    def env():
        value=os.environ.copy()
        overrides=compiler_overrides(value)
        assert not overrides,('Refuse unregistered compiler overrides',overrides)
        for key in ['POSTFLOP_AUTORESEARCH_FIXTURE','POSTFLOP_AUTORESEARCH_STORAGE','POSTFLOP_AUTORESEARCH_PROFILE',
                    'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER']:
            value.pop(key,None)
        value.update(RAYON_NUM_THREADS='16',CARGO_TARGET_DIR=str(TARGET))
        value['PATH']=str(runner.NVRTC)+os.pathsep+value.get('PATH','')
        return value
    def preflight(where,gpu):
        live=runner.live_status();runner.refuse_active(live)
        disk=shutil.disk_usage(ROOT).free;assert disk>=52*1024**3,'S reserve/output admission'
        class Memory(ctypes.Structure):
            _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total_phys',ctypes.c_ulonglong),('avail_phys',ctypes.c_ulonglong),
                ('total_page',ctypes.c_ulonglong),('avail_page',ctypes.c_ulonglong),('total_virtual',ctypes.c_ulonglong),('avail_virtual',ctypes.c_ulonglong),('extended',ctypes.c_ulonglong)]
        memory=Memory();memory.length=ctypes.sizeof(memory)
        assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory))
        assert memory.avail_phys>=16*1024**3,'host free-memory admission'
        tele=runner.telemetry()
        if gpu:
            query=runner.read_command(['nvidia-smi','--query-gpu=index,name,memory.total,memory.free','--format=csv,noheader,nounits'])
            assert query.get('returncode')==0
            lines=[x.strip() for x in query['stdout'].splitlines() if x.strip()]
            first=[x.strip() for x in lines[0].split(',')]
            assert first[0]=='0' and first[1]=='NVIDIA GeForce RTX 5090'
            assert float(first[2])>=30*1024 and float(first[3])>=4*1024,'device memory admission'
        else:query=None
        save(where/'preflight.json',{'at':now(),'live':live,'disk_free_bytes':disk,'host_available_bytes':memory.avail_phys,'telemetry':tele,'device_admission':query})
    def execute(command,where,cwd,timeout,environment):
        verify();proc=None;error=None;cleanup=None;start=time.monotonic()
        save(where/'invocation.json',{'at':now(),'args':command,'cwd':str(cwd),'timeout_seconds':timeout,
            'environment':{k:environment.get(k) for k in ['RAYON_NUM_THREADS','CARGO_TARGET_DIR','RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','POSTFLOP_HOLDOUT_STATE']},
            'compiler_override_absence_check':{'keys':sorted(COMPILER_KEYS),'patterns':['CARGO_PROFILE_RELEASE_*','CARGO_TARGET_*_RUSTFLAGS'],'present':compiler_overrides(environment)}})
        try:
            with (where/'stdout.log').open('xb',buffering=0) as stdout,(where/'stderr.log').open('xb',buffering=0) as stderr:
                proc=subprocess.Popen(command,cwd=cwd,env=environment,stdout=stdout,stderr=stderr,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                last=start
                while proc.poll() is None:
                    current=time.monotonic()
                    if current-start>=timeout:raise TimeoutError(f'fixed phase timeout {timeout}s')
                    if current-last>=10:heartbeat(where.name,current-start);last=current
                    time.sleep(.25)
                assert proc.returncode==0,f'native exit {proc.returncode}, see {where}'
        except BaseException as exc:
            error=repr(exc);cleanup=runner.cleanup_child(proc);raise
        finally:
            save(where/'exit.json',{'at':now(),'returncode':proc.returncode if proc else None,'process_wall_ms':(time.monotonic()-start)*1000,'error':error,'cleanup':cleanup})
        verify()
    def built(name):
        binary=HERE/'build/binaries'/f'{name}.exe'
        manifest_path=binary.with_suffix('.manifest.json');manifest=read(manifest_path)
        assert manifest['binary_sha256']==sha(binary) and manifest['prepared_manifest_sha256']==sha(HERE/'prepared-manifest.json')
        return binary,manifest_path
    def all_builds_ready():
        path=pin(authorization['all_builds_ready'])
        ready=read(path);assert ready['all_required_builds_terminal'] is True
        assert ready['all_builds_terminal'] is True and ready['holdout_builds_terminal'] is True
        assert ready['holdout_build_source_review_pass'] is True
        listed={str(pin({'path':name,'sha256':h})) for name,h in ready['artifacts'].items()}
        for name in ['E015-holdout','E020-holdout','E015-resource']:
            binary,manifest=built(name)
            assert str(binary) in listed and str(manifest) in listed
        return {'path':str(path),'sha256':sha(path)}

    with runner.exclusive_lock(ROOT/'gpu-run.lock'):
        verify();out.mkdir(exist_ok=False)
        save(out/'started.json',{'at':now(),'phase':args.phase,'prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
            'authorization_path':str(args.authorization),'authorization_sha256':args.authorization_sha256})
        try:
            if args.phase=='build':
                preflight(out,False);(out/'binaries').mkdir()
                save(out/'toolchain.json',{'rustc':runner.read_command(['rustc','-Vv']),'cargo':runner.read_command(['cargo','-V']),
                    'nvrtc_dll_sha256':{p.name:sha(p) for p in sorted(Path(runner.NVRTC).glob('*.dll'))}})
                outputs=[]
                for role in ['E015','E020']:
                    folder=out/role;folder.mkdir()
                    workspace=HERE/'workspaces'/role
                    command=['cargo','test','--release','--locked','--offline','-p','solver','--features','gpu','--test','postflop_wide_turn_holdout']
                    wanted={'postflop_wide_turn_holdout':role+'-holdout'}
                    if role=='E015':
                        command+=['--test','postflop_wide_turn_resources'];wanted['postflop_wide_turn_resources']='E015-resource'
                    command+=['--no-run','--message-format=json']
                    execute(command,folder,workspace,1800,env())
                    logs=[json.loads(line) for line in (folder/'stdout.log').read_text(encoding='utf-8').splitlines()]
                    assert any(x.get('reason')=='build-finished' and x.get('success') is True for x in logs)
                    rows=[x for x in logs if x.get('reason')=='compiler-artifact' and x.get('executable') and x.get('profile',{}).get('test') and x['target']['name'] in wanted]
                    assert {x['target']['name'] for x in rows}==set(wanted) and len(rows)==len(wanted)
                    deps={f:sha(Path(f)) for x in logs if x.get('reason')=='compiler-artifact' for f in x.get('filenames',[]) if Path(f).is_file() and Path(f).suffix in {'.rlib','.rmeta','.lib','.dll'}}
                    for item in rows:
                        name=wanted[item['target']['name']];destination=out/'binaries'/f'{name}.exe'
                        assert not destination.exists();shutil.copyfile(item['executable'],destination)
                        manifest={'role':role,'name':name,'at':now(),'binary_sha256':sha(destination),
                            'prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),'workspace_source_map':read(HERE/'workspace-source-maps.json')[role],
                            'cargo_artifact':item,'dependency_artifact_sha256':deps,'command':command,
                            'build_stdout_sha256':sha(folder/'stdout.log'),'build_stderr_sha256':sha(folder/'stderr.log'),
                            'evaluator_sha256':sha(HERE/'evaluator.rs'),'fixture_sha256':sha(HERE/'fixture.json'),'source_verified_after_build':True}
                        save(destination.with_suffix('.manifest.json'),manifest);outputs.append({'path':str(destination),'sha256':sha(destination)})
                save(out/'report.json',{'status':'pass','scope':'compilation only','outputs':outputs,'gpu_executions':0})
            elif args.phase=='resource':
                ready=all_builds_ready();preflight(out,True)
                binary,manifest=built('E015-resource')
                run=out/'native';run.mkdir()
                execute([str(binary),'postflop_wide_turn_resources','--exact','--ignored','--nocapture','--test-threads=1'],run,out,600,env())
                native_pass(run/'stdout.log','postflop_wide_turn_resources')
                rows=markers(run/'stdout.log','WIDE_RESOURCE')
                assert len(rows)==4 and rows[0]['stage']=='device' and rows[-1]['stage']=='complete' and rows[-1]['resource_rows']==2
                resources=rows[1:3]
                assert [r['source_variant'] for r in resources]==['baseline','candidate']
                for r,dynamic,fnv in zip(resources,[13160,21808],['3f0594b037a1dda3','fd544fbd87847b9c']):
                    assert r['nh_o']==1128 and r['max_valid_opponent_hands']==1081 and r['dynamic_shared_bytes']==dynamic
                    assert r['source_fnv1a64']==fnv and r['fits_queried_default_shared_and_thread_limits'] is True
                    assert r['max_threads_per_block']>=128 and r['occupancy_blocks_per_sm_128']>=1
                    assert r['kernel_launches']==0 and r['performance_measurement'] is False
                save(out/'report.json',{'status':'pass','scope':'actual holdout compiler/resource feasibility only','records':rows,
                    'binary_sha256':sha(binary),'build_manifest_sha256':sha(manifest),'all_builds_ready':ready,
                    'kernel_launches':0,'timings':False,'telemetry_after':runner.telemetry()})
            else:
                ready=all_builds_ready();resource_report=read(HERE/'resource/report.json');assert resource_report['status']=='pass'
                records={}
                for label in ORDER:
                    run=out/label;run.mkdir();preflight(run,True)
                    binary,manifest=built(('E015' if label[0]=='B' else 'E020')+'-holdout')
                    environment=env();environment['POSTFLOP_HOLDOUT_STATE']=str(run/'state.bin')
                    execute([str(binary),'postflop_wide_turn_holdout','--exact','--ignored','--nocapture','--test-threads=1'],run,run,600,environment)
                    native_pass(run/'stdout.log','postflop_wide_turn_holdout')
                    results=markers(run/'stdout.log','AUTORESEARCH_RESULT');assert len(results)==1
                    result=results[0];stages=markers(run/'stdout.log','AUTORESEARCH_STAGE')
                    assert result['fixture_id']=='wide-turn-full169' and result['config']==read(HERE/'fixture.json')
                    assert result['storage']=='compressed' and result['target_met'] is True
                    assert result['target_pct']==0.3 and result['check_every']==20 and result['max_iterations']==400
                    assert result['use_isomorphism'] is True and result['iteration'] in range(20,401,20)
                    for key in TIMINGS:assert type(result[key]) in (int,float) and math.isfinite(result[key]) and result[key]>=0
                    checks=[s for s in stages if s['stage']=='convergence_check']
                    admissions=[s for s in stages if s['stage']=='holdout_admission']
                    assert len(admissions)==1
                    admission=admissions[0]
                    assert admission['hands']==[1128,1128] and admission['river_cards']==48 and admission['river_max']==[1081,1081]
                    assert admission['nodes']==result['nodes']<=11691 and admission['public_vram_estimate_bytes']<=2*1024**3
                    assert admission['gpu_budget_bytes']==2*1024**3 and admission['duplicate_plan_built'] is False
                    assert admission['baseline_dynamic_shared_bytes']==[13160,13160] and admission['candidate_dynamic_shared_bytes']==[21808,21808]
                    memory_rows=[s for s in stages if s['stage']=='postscore_device_memory']
                    assert len(memory_rows)==1 and memory_rows[0]['excluded_from_score'] is True
                    assert 0<=memory_rows[0]['free_bytes']<=memory_rows[0]['total_bytes']
                    assert memory_rows[0]['total_bytes']>=30*1024**3
                    assert [s['iteration'] for s in checks]==list(range(20,result['iteration']+1,20))
                    assert all(math.isfinite(s['exploit_pct_pot']) and s['exploit_pct_pot']>0.3 for s in checks[:-1])
                    assert checks[-1]['exploit_pct_pot']<=0.3 and checks[-1]['exploit_bits']==result['exploit_bits']
                    assert stages[-1]['stage']=='suite_complete' and stages[-1]['fixtures_completed']==1 and stages[-1]['primary_suite'] is False
                    raw=raw_layout(run/'state.bin',result)
                    raw_rows=[s for s in stages if s['stage']=='raw_state_complete'];assert len(raw_rows)==1 and raw_rows[0]['bytes']==raw['bytes']
                    record={'label':label,'result':result,'checks':[{k:s[k] for k in ['iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for s in checks],
                        'raw_state':raw,'admission':admission,'postscore_device_memory':memory_rows[0],'binary_sha256':sha(binary),'build_manifest_sha256':sha(manifest),
                        'process_wall_ms':read(run/'exit.json')['process_wall_ms'],'telemetry_after':runner.telemetry()}
                    save(run/'report.json',record);records[label]=record
                    if label!='B1':
                        reference=records['B1']
                        assert {k:v for k,v in result.items() if k not in TIMINGS}=={k:v for k,v in reference['result'].items() if k not in TIMINGS},'exact full-result mismatch'
                        assert record['checks']==reference['checks'],'exact convergence trajectory mismatch'
                        assert binary_equal(out/'B1/state.bin',run/'state.bin'),'exact raw state mismatch'
                baseline=[records[f'B{i}']['result']['full_cycle_ms'] for i in range(1,4)]
                candidate=[records[f'C{i}']['result']['full_cycle_ms'] for i in range(1,4)]
                assert all(x>0 for x in baseline+candidate)
                paired=[100*(c/b-1) for b,c in zip(baseline,candidate)]
                change=100*(statistics.median(candidate)/statistics.median(baseline)-1)
                rejected=change>3 and sum(x>3 for x in paired)>=2
                save(out/'report.json',{'status':'failed' if rejected else 'pass','at':now(),'scope':'one prospective broad-turn holdout, not primary score',
                    'correctness':'all6 full compressed CPU stores byte-identical and every non-timing result/check exact',
                    'baseline_full_cycle_ms':baseline,'candidate_full_cycle_ms':candidate,'baseline_median_ms':statistics.median(baseline),
                    'candidate_median_ms':statistics.median(candidate),'median_slowdown_pct':change,'paired_slowdown_pct':paired,
                    'pairs_over_3pct':sum(x>3 for x in paired),'repeatable_regression':rejected,
                    'resource_report_sha256':sha(HERE/'resource/report.json'),'all_builds_ready':ready,
                    'run_report_sha256':{label:sha(out/label/'report.json') for label in ORDER},
                    'candidate_accepted':False,'deployment_changed':False,'protocol_sha256':sha(HERE/'plan-protocol.json')})
            verify();heartbeat(args.phase+' complete; independent audit pending')
        except BaseException as error:
            save(out/'failure.json',{'at':now(),'status':'inconclusive','error':repr(error),'preserve_all_evidence':True,'retry_permitted':False})
            heartbeat(args.phase+' stopped; failure evidence retained')
            raise

if __name__=='__main__':main()
