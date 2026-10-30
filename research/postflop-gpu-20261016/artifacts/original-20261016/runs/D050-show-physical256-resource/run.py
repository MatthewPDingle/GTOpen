"""D050 one-shot standalone compiler/resource probe; root executes in serialized slot."""
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
        for name,h in prepared['protected_checkout_sha256'].items():assert sha(REPO/name)==h,('Accepted E020 source must be restored before D050',name)
        assert sha(HERE/'prepared-manifest.json')==args.prepared_manifest_sha256
        for name,info in prepared['references'].items():assert sha(info['path'])==info['sha256'],('Reference changed',name)
        audit=json.loads(Path(prepared['references']['D049_terminal_review']['path']).read_text(encoding='utf-8'))
        assert audit['verdict']=='CONFIRMED_RESOURCE_PREREQUISITE_REJECTION'
        proposal=json.loads(Path(prepared['references']['D047_source_manifest']['path']).read_text(encoding='utf-8'))
        assert proposal['verdict']=='GO_SOURCE_FEASIBILITY_ONLY_FOR_PHYSICAL256_FIXED_LOGICAL128; NO_GO_LAUNCH_ONLY'
    verify()
    save('execution-started.json',{'at':now(),'prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
        'operator_obligation':'Root owns serialized build/GPU slot; no concurrent unrelated build/GPU job',
        'per_stage_timeout_seconds':STAGE_TIMEOUT_SECONDS})
    spec=importlib.util.spec_from_file_location('d050_runner_primitives',HERE/'runner-primitives-source.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.REPO=REPO
    commands=[]
    def heartbeat(stage,elapsed=0):
        with runner.exclusive_lock(STATUS.with_suffix('.lock'),timeout=3):
            state=json.loads(STATUS.read_text(encoding='utf-8-sig'))
            state['updated_at']=runner.now()
            state['stage']='D050 standalone fixed-logical128 physical256 showdown resource diagnostic'
            state['activity']=f'D050 {stage}; {elapsed:.0f}s elapsed. Compiler/resources only; no kernel launches; accepted E020 and deployment status unchanged.'
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
            assert runner.source_identity()['source_sha256']==prepared['protected_checkout_sha256'],'Accepted162-source map must be exact'
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
            save('execution-manifest.json',{'id':'D050','prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
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
            assert runner.source_identity()['source_sha256']==prepared['protected_checkout_sha256'],'Checkout changed during probe'
            telemetry_after=runner.telemetry()
            rows=[json.loads(line[len('D050_RESOURCE '):]) for line in (HERE/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if line.startswith('D050_RESOURCE ')]
            assert len(rows)==10 and rows[0]['stage']=='device' and rows[-1]['stage']=='complete'
            resource=[row for row in rows if row['stage']=='resource']
            assert len(resource)==8 and rows[-1]['resource_rows']==8 and rows[-1]['source_variants']==2
            protocol=json.loads((HERE/'protocol.json').read_text(encoding='utf-8'))
            shapes=protocol['resource_cases']
            assert [(v['source_variant'],v['kernel'],v['case_id']) for v in resource]==[
                (variant,'up_show',shape['id']) for variant in ['baseline','candidate'] for shape in shapes]
            assert rows[0]['device']=='NVIDIA GeForce RTX 5090' and rows[0]['architecture']=='compute_120'
            assert rows[0]['nvrtc_major']>0 and rows[0]['nvrtc_minor']>=0
            for row in rows:
                assert row['kernel_launches']==0 and row['performance_measurement'] is False
            for row in resource:
                expected=prepared['source_variants'][row['source_variant']]
                assert row['source_fnv1a64']==expected['fnv1a64'] and row['source_bytes']==expected['bytes']
                shape=next(v for v in shapes if v['id']==row['case_id'])
                threads=128 if row['source_variant']=='baseline' else 256
                assert row['block_threads']==threads and row['dynamic_shared_bytes']==shape['dynamic_shared_bytes']
                assert row['registers']>0 and row['max_threads_per_block']>0 and row['static_shared_bytes']>=0
                assert row['local_bytes_per_thread']>=0 and row['occupancy_blocks_per_sm']>=0
                assert row['occupancy_warps_per_sm']==row['occupancy_blocks_per_sm']*(threads//32)
                fits=(row['static_shared_bytes']+row['dynamic_shared_bytes']<=rows[0]['max_shared_bytes_per_block_default']
                    and row['max_threads_per_block']>=threads and rows[0]['max_threads_per_block']>=threads)
                assert row['fits_queried_default_shared_and_thread_limits'] is fits
            ptx={v:(HERE/(v+'.ptx')).read_text(encoding='utf-8') for v in ['baseline','candidate']}
            summaries={}
            for variant in ['baseline','candidate']:
                code=entry(ptx[variant],'up_show')
                bytes_new(variant+'-up_show.ptx',(code+'\n').encode())
                summaries[variant]={'opcodes_static_only':opcodes(code),'entry_sha256':hashlib.sha256(code.encode()).hexdigest()}
            names={v:re.findall(r'\.visible\s+\.entry\s+(\w+)\(',ptx[v]) for v in ['baseline','candidate']}
            assert names['candidate']==names['baseline'] and len(names['baseline'])==9
            unchanged={name:entry(ptx['baseline'],name)==entry(ptx['candidate'],name) for name in names['baseline'] if name!='up_show'}
            before_entry=entry(ptx['baseline'],'up_show');after_entry=entry(ptx['candidate'],'up_show')
            signature_unchanged=before_entry.split('{',1)[0]==after_entry.split('{',1)[0]
            assert signature_unchanged,'Showdown ABI changed'
            import difflib
            bytes_new('up_show-ptx.diff',''.join(difflib.unified_diff(before_entry.splitlines(True),after_entry.splitlines(True),fromfile='baseline-up_show.ptx',tofile='candidate-up_show.ptx')).encode())
            arithmetic={}
            for variant,code in [('baseline',before_entry),('candidate',after_entry)]:
                counts=opcodes(code)
                arithmetic[variant]={
                    'local_declarations':[line.strip() for line in code.splitlines() if re.search(r'\.local\b',line)],
                    'floating_typed_opcodes_static_only':{k:v for k,v in counts.items() if re.search(r'\.f(?:32|64)(?:\.|$)',k)},
                    'ftz_opcodes_static_only':{k:v for k,v in counts.items() if '.ftz.' in k},
                    'barrier_opcodes_static_only':{k:v for k,v in counts.items() if k.startswith('bar.')},
                }
            save('ptx-inspection.json',{'entry_names':names,'other_entry_ptx_byte_equality':unchanged,
                'up_show_signature_unchanged':signature_unchanged,'entries':summaries,'arithmetic_inspection':arithmetic,
                'source_ptx_review_status':'Pending independent scan/guard/float-dependency inspection; static counts alone cannot prove exactness.',
                'required_review':'Physical256 must use the same128 logical chunks, +0 accumulators,128 chunk writes, full128 left-to-right recurrence and per-chunk base addition as accepted physical128. Every physical thread reaches all barriers; upper128 scan threads access no uninitialized chunk_sum. Other valid1D widths retain original geometry.'})
            assert len(unchanged)==8 and all(unchanged.values()),'Other accepted entry PTX changed; retain invalid evidence'
            gate={row['source_variant']+'/'+row['case_id']:
                row['fits_queried_default_shared_and_thread_limits'] and row['occupancy_blocks_per_sm']>0
                for row in resource}
            trades=[]
            for shape in shapes:
                before=next(v for v in resource if v['source_variant']=='baseline' and v['case_id']==shape['id'])
                after=next(v for v in resource if v['source_variant']=='candidate' and v['case_id']==shape['id'])
                trades.append({'case_id':shape['id'],'dynamic_shared_bytes':shape['dynamic_shared_bytes'],
                    'baseline':{k:before[k] for k in ['block_threads','registers','local_bytes_per_thread','static_shared_bytes','occupancy_blocks_per_sm','occupancy_warps_per_sm']},
                    'candidate':{k:after[k] for k in ['block_threads','registers','local_bytes_per_thread','static_shared_bytes','occupancy_blocks_per_sm','occupancy_warps_per_sm']}})
            report={'id':'D050','status':'completed_compiler_resource_diagnostic','prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
                'protocol_sha256':prepared['protocol_sha256'],'complete':rows[-1],'records':rows,'ptx':summaries,
                'other_entry_ptx_byte_equality':unchanged,'up_show_signature_unchanged':signature_unchanged,
                'arithmetic_inspection':arithmetic,'source_ptx_review_status':'pending independent scan/guard/float-dependency review',
                'capacity_prerequisite_checks':gate,'capacity_prerequisite_pass':all(gate.values()),
                'source_ptx_prerequisite_pass':None,'eligible_for_native_candidate':False,
                'resource_trades':trades,'resource_nonregression_gate':False,'commands':commands,'telemetry_after':telemetry_after,
                'input_sha256_after':{n:sha(HERE/n) for n in prepared['artifact_sha256']},'binary_sha256':sha(HERE/'probe.exe'),
                'kernel_launches':0,'solver_executions':0,'numerical_validation':'not executed','performance_measurement':False,
                'candidate_accepted':False,'deployment_changed':False,
                'limits':['One baseline128/candidate256 compiler comparison; no kernel/solver launch or numerical comparison.',
                    'Registers/local bytes/blocks/warps are reported tradeoffs, not arbitrary performance gates or measured speed.',
                    'Thread/shared capacity, unchanged ABI/eight other entries and independent exact scan source/PTX review are prerequisites only.',
                    'D045 selected launch intervals are event-perturbed samples, not full solve or family shares.',
                    'Both future training/evaluation up_show host sites would need256 threads; host code is deliberately unimplemented here.',
                    'A later authorized native differential and full exactness/complete-cycle controls remain necessary. No automatic rescue or adoption.']}
            save('report.json',report)
            heartbeat('complete; independent result audit pending',0)
            print(json.dumps({'id':'D050','complete':rows[-1],'report':str(HERE/'report.json')},indent=2))
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
