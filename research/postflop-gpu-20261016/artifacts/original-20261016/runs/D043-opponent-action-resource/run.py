"""D043 one-shot standalone compiler/resource probe; root executes in serialized slot."""
from pathlib import Path
import argparse, collections, datetime, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, time, signal

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
DEPS=ROOT/'build/release/deps'
STATUS=Path(r'X:\Dev\GTOpen\web\research\postflop-gpu-20261016\status.json')
STAGE_TIMEOUT_SECONDS=600
RESERVE_BYTES=50*1024**3
OUTPUT_RESERVATION_BYTES=1024**3

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(name,value):
    with (HERE/name).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,indent=2,allow_nan=False); f.write('\n')
def bytes_new(name,data):
    with (HERE/name).open('xb') as f:f.write(data)
def entry(ptx,name):
    match=re.search(r'\.visible\s+\.entry\s+'+re.escape(name)+r'\(',ptx)
    assert match,name
    begin=ptx.index('{',match.start()); depth=1; end=begin+1
    while depth:
        if ptx[end]=='{':depth+=1
        elif ptx[end]=='}':depth-=1
        end+=1
    return ptx[match.start():end]
def opcodes(source):
    result=collections.Counter()
    for line in source.splitlines():
        match=re.match(r'\s*(?:@!?%\w+\s+)?([a-z]\w*(?:\.\w+)+)\s',line.split('//',1)[0])
        if match: result[match.group(1)]+=1
    return dict(sorted(result.items()))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',required=True,action='store_true')
    parser.add_argument('--prepared-manifest-sha256',required=True)
    args=parser.parse_args()
    assert sha(HERE/'prepared-manifest.json')==args.prepared_manifest_sha256,'Prepared manifest changed'
    prepared=json.loads((HERE/'prepared-manifest.json').read_text(encoding='utf-8'))
    def verify():
        for name,h in prepared['artifact_sha256'].items(): assert sha(HERE/name)==h,('Changed artifact',name)
        for name,info in prepared['dependency_rlibs'].items():assert sha(info['path'])==info['sha256'],('Changed dependency',name)
        for name,h in prepared['protected_checkout_sha256'].items():assert sha(REPO/name)==h,('Accepted E020 source must be restored before D043',name)
        assert sha(HERE/'prepared-manifest.json')==args.prepared_manifest_sha256
        for name,info in prepared['references'].items():assert sha(info['path'])==info['sha256'],('Reference changed',name)
        terminal=json.loads((HERE/'source-D042-terminal.json').read_text(encoding='utf-8'))
        assert terminal['order']==['D042B1','D042P1','D042P2','D042B2','D042B3','D042P3']
        d042=json.loads((HERE/'source-D042-report.json').read_text(encoding='utf-8'))
        assert d042['status']=='pass' and d042['all_complete_states_exact']==18 and d042['convergence_checks_exact']==138
    verify()
    save('execution-started.json',{'at':now(),'prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
        'operator_obligation':'Root owns serialized build/GPU slot; no concurrent unrelated build/GPU job',
        'per_stage_timeout_seconds':STAGE_TIMEOUT_SECONDS})
    spec=importlib.util.spec_from_file_location('d043_runner_primitives',HERE/'runner-primitives-source.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.REPO=REPO
    commands=[]
    def heartbeat(stage,elapsed=0):
        with runner.exclusive_lock(STATUS.with_suffix('.lock'),timeout=3):
            state=json.loads(STATUS.read_text(encoding='utf-8-sig'))
            state['updated_at']=runner.now()
            state['stage']='D043 standalone opponent-action resource diagnostic'
            state['activity']=f'D043 {stage}; {elapsed:.0f}s elapsed. Compiler/resources only; no kernel launches; accepted E020 and deployment status unchanged.'
            runner.atomic_json(STATUS,state)
    def execute(args,name,env=None):
        started=now(); before=time.monotonic(); proc=None; cleanup=None
        record={'args':args,'cwd':str(HERE),'started_at':started,'timeout_seconds':STAGE_TIMEOUT_SECONDS}
        try:
            with (HERE/(name+'.stdout.log')).open('xb',buffering=0) as out, (HERE/(name+'.stderr.log')).open('xb',buffering=0) as err:
                heartbeat(name)
                proc=subprocess.Popen(args,cwd=HERE,env=env,stdout=out,stderr=err,
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                last=before
                while proc.poll() is None:
                    current=time.monotonic()
                    if current-before>=STAGE_TIMEOUT_SECONDS: raise TimeoutError(f'{name} exceeded fixed {STAGE_TIMEOUT_SECONDS}s')
                    if current-last>=10:heartbeat(name,current-before);last=current
                    time.sleep(.25)
                if proc.returncode:raise RuntimeError(f'{name} exited {proc.returncode}; preserve logs')
        except BaseException as error:
            record['error']=repr(error)
            cleanup=runner.cleanup_child(proc)
            raise
        finally:
            record.update(elapsed_seconds=time.monotonic()-before,returncode=proc.returncode if proc else None,cleanup=cleanup)
            save(name+'.command.json',record);commands.append(record)
    try:
        with runner.exclusive_lock(ROOT/'gpu-run.lock'):
            verify()
            free=shutil.disk_usage(ROOT).free
            assert free>=RESERVE_BYTES+OUTPUT_RESERVATION_BYTES, 'S: reserve insufficient'
            live=runner.live_status();runner.refuse_active(live)
            save('preflight.json',{'live_status':live,'telemetry':runner.telemetry(),'free_bytes':free,
                'minimum_free_reserve_bytes':RESERVE_BYTES,'output_reservation_bytes':OUTPUT_RESERVATION_BYTES,
                'lock':str(ROOT/'gpu-run.lock')})
            deps=prepared['dependency_rlibs']
            command=['rustc','probe.rs','--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin',
                '-L','dependency='+str(DEPS),'--extern','cudarc='+deps['cudarc']['path'],
                '--extern','serde_json='+deps['serde_json']['path'],'-o','probe.exe']
            save('execution-manifest.json',{'id':'D043','prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
                'input_sha256_before':prepared['artifact_sha256'],'rustc':runner.read_command(['rustc','-Vv']),
                'compile_command':command,'nvrtc_directory':str(runner.NVRTC),
                'nvrtc_dll_sha256':{p.name:sha(p) for p in sorted(Path(runner.NVRTC).glob('*.dll'))},
                'gpu_device_ordinal':0,'expected_device':'NVIDIA GeForce RTX 5090','expected_architecture':'compute_120',
                'solver_executions':0,'performance_measurement':False,'requested_cuda_module_loading':os.environ.get('CUDA_MODULE_LOADING'),
                'rustc_executable':shutil.which('rustc'),
                'rustc_executable_sha256':sha(shutil.which('rustc')),
                'source':'Sealed outside-checkout inputs only; accepted E020 source restored'})
            assert not (HERE/'probe.exe').exists(),'Refusing existing binary'
            execute(command,'rustc')
            verify()
            env=os.environ.copy();env['PATH']=str(runner.NVRTC)+os.pathsep+env.get('PATH','');env['RAYON_NUM_THREADS']='16'
            live=runner.live_status();runner.refuse_active(live);save('launch-preflight.json',live)
            execute([str(HERE/'probe.exe')],'probe',env)
            verify()
            telemetry_after=runner.telemetry()
            rows=[json.loads(line[len('D043_RESOURCE '):]) for line in (HERE/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if line.startswith('D043_RESOURCE ')]
            assert len(rows)==5 and rows[0]['stage']=='device' and rows[-1]['stage']=='complete'
            resource=[row for row in rows if row['stage']=='resource']
            assert len(resource)==3 and rows[-1]['resource_rows']==3
            assert [(v['source_variant'],v['kernel']) for v in resource]==[
                ('baseline','up_action'),('candidate','up_action'),('candidate','up_action_opponent')]
            assert rows[0]['device']=='NVIDIA GeForce RTX 5090' and rows[0]['architecture']=='compute_120'
            assert rows[0]['nvrtc_major']>0 and rows[0]['nvrtc_minor']>=0
            for row in rows:
                assert row['kernel_launches']==0 and row['performance_measurement'] is False
            for row in resource:
                expected=prepared['source_variants'][row['source_variant']]
                assert row['source_fnv1a64']==expected['fnv1a64'] and row['source_bytes']==expected['bytes']
                assert row['block_threads']==128 and row['dynamic_shared_bytes']==0
                assert row['registers']>0 and row['max_threads_per_block']>=128 and row['static_shared_bytes']>=0
                assert row['local_bytes_per_thread']>=0 and row['occupancy_blocks_per_sm_128']>0
                assert row['fits_queried_default_shared_and_thread_limits'] is True
            original,candidate_original,opponent=resource
            fields=['registers','local_bytes_per_thread','static_shared_bytes','max_threads_per_block',
                'occupancy_blocks_per_sm_128','occupancy_warps_per_sm_128']
            assert {k:original[k] for k in fields}=={k:candidate_original[k] for k in fields},'Original entry resources changed'
            ptx={v:(HERE/(v+'.ptx')).read_text(encoding='utf-8') for v in ['baseline','candidate']}
            summaries={}
            for variant,name in [('baseline','up_action'),('candidate','up_action'),('candidate','up_action_opponent')]:
                code=entry(ptx[variant],name)
                bytes_new(variant+'-'+name+'.ptx',(code+'\n').encode())
                summaries[variant+'-'+name]={'opcodes_static_only':opcodes(code),'entry_sha256':hashlib.sha256(code.encode()).hexdigest()}
            names={v:re.findall(r'\.visible\s+\.entry\s+(\w+)\(',ptx[v]) for v in ['baseline','candidate']}
            assert names['candidate']==names['baseline']+['up_action_opponent']
            unchanged={name:entry(ptx['baseline'],name)==entry(ptx['candidate'],name) for name in names['baseline']}
            save('ptx-inspection.json',{'entry_names':names,'original_entry_ptx_byte_equality':unchanged,'entries':summaries})
            assert all(unchanged.values()),'Original entry PTX changed; retain evidence as invalid diagnostic'
            gate={
                'zero_local_bytes':opponent['local_bytes_per_thread']==0,
                'register_reduction_at_least_25pct':opponent['registers']*4<=original['registers']*3,
                'strictly_more_active_blocks_per_sm':opponent['occupancy_blocks_per_sm_128']>original['occupancy_blocks_per_sm_128'],
                'supports128threads':opponent['max_threads_per_block']>=128,
            }
            report={'id':'D043','status':'completed_compiler_resource_diagnostic','prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
                'protocol_sha256':prepared['protocol_sha256'],'complete':rows[-1],'records':rows,'ptx':summaries,
                'original_entry_ptx_byte_equality':unchanged,'resource_prerequisite_checks':gate,
                'material_resource_prerequisite_pass':all(gate.values()),
                'register_reduction_percent':100*(1-opponent['registers']/original['registers']),
                'commands':commands,'telemetry_after':telemetry_after,
                'input_sha256_after':{n:sha(HERE/n) for n in prepared['artifact_sha256']},
                'binary_sha256':sha(HERE/'probe.exe'),'kernel_launches':0,'performance_measurement':False,
                'solver_executions':0,'numerical_validation':'not executed','candidate_accepted':False,'deployment_changed':False,
                'limits':['No kernel launch, numerical comparison or solver execution occurred.',
                    'All original accepted entry PTX is required unchanged; the new entry itself has no runtime exactness proof yet.',
                    'The three resource conditions are a prerequisite for considering a later bounded candidate, not adoption or projected speed.',
                    'Prior source census predicts20 additional launches per paired flop iteration if all mixed levels split; counts are not timings.',
                    'New function loading, actor metadata and graph construction costs are outside this resource query and must enter any later full cycle.',
                    'PTX static opcode counts and theoretical occupancy do not measure latency, throughput, native shares or complete-cycle saving.',
                    'Compiler/probe process duration is audit metadata, never solver performance.']}
            save('report.json',report)
            heartbeat('complete; independent result audit pending',0)
            print(json.dumps({'id':'D043','complete':rows[-1],'report':str(HERE/'report.json')},indent=2))
    except BaseException as error:
        save('failure.json',{'at':now(),'error':repr(error),'commands':commands,'instruction':'Preserve failure; no retry/overwrite in this directory.'})
        try:heartbeat('invalid; evidence retained',0)
        except BaseException:pass
        raise

if __name__=='__main__':
    def interrupted(signum,frame):raise KeyboardInterrupt(f'Interrupted by signal {signum}')
    for name in ['SIGTERM','SIGBREAK']:
        if hasattr(signal,name):signal.signal(getattr(signal,name),interrupted)
    main()
