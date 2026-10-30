"""D037 one-shot standalone compiler/resource probe; root executes in serialized slot."""
from pathlib import Path
import argparse, collections, datetime, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, time

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
    parser.parse_args()
    prepared=json.loads((HERE/'prepared-manifest.json').read_text(encoding='utf-8'))
    def verify():
        for name,h in prepared['artifact_sha256'].items(): assert sha(HERE/name)==h,('Changed artifact',name)
        for name,info in prepared['dependency_rlibs'].items():assert sha(info['path'])==info['sha256'],('Changed dependency',name)
        for name,h in prepared['protected_checkout_sha256'].items():assert sha(REPO/name)==h,('Accepted source changed',name)
    verify()
    save('execution-started.json',{'at':now(),'prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
        'operator_obligation':'Root owns serialized build/GPU slot; no concurrent unrelated build/GPU job',
        'per_stage_timeout_seconds':STAGE_TIMEOUT_SECONDS})
    spec=importlib.util.spec_from_file_location('d037_runner_primitives',HERE/'runner-primitives-source.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.REPO=REPO
    commands=[]
    def heartbeat(stage,elapsed=0):
        with runner.exclusive_lock(STATUS.with_suffix('.lock'),timeout=3):
            state=json.loads(STATUS.read_text(encoding='utf-8-sig'))
            state['updated_at']=runner.now()
            state['stage']='D037 standalone showdown-cache resource diagnostic'
            state['activity']=f'D037 {stage}; {elapsed:.0f}s elapsed. Compiler/resources only; no kernel launches; accepted E015 and deployment status unchanged.'
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
            save('execution-manifest.json',{'id':'D037','prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
                'input_sha256_before':prepared['artifact_sha256'],'rustc':runner.read_command(['rustc','-Vv']),
                'compile_command':command,'nvrtc_directory':str(runner.NVRTC),
                'nvrtc_dll_sha256':{p.name:sha(p) for p in sorted(Path(runner.NVRTC).glob('*.dll'))},
                'gpu_device_ordinal':0,'expected_device':'NVIDIA GeForce RTX 5090','expected_architecture':'compute_120',
                'solver_executions':0,'performance_measurement':False,'source':'Sealed outside-checkout inputs only'})
            assert not (HERE/'probe.exe').exists(),'Refusing existing binary'
            execute(command,'rustc')
            verify()
            env=os.environ.copy();env['PATH']=str(runner.NVRTC)+os.pathsep+env.get('PATH','');env['RAYON_NUM_THREADS']='16'
            live=runner.live_status();runner.refuse_active(live);save('launch-preflight.json',live)
            execute([str(HERE/'probe.exe')],'probe',env)
            verify()
            telemetry_after=runner.telemetry()
            rows=[json.loads(line[len('D037_RESOURCE '):]) for line in (HERE/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if line.startswith('D037_RESOURCE ')]
            assert len(rows)==16 and rows[0]['stage']=='device' and rows[-1]['stage']=='complete'
            resource=[row for row in rows if row['stage']=='resource']
            assert len(resource)==14 and rows[-1]['resource_rows']==14
            shapes=prepared['resource_shapes']
            assert [(v['source_variant'],v['shape']) for v in resource]==[(variant,s['id']) for variant in ['baseline','candidate'] for s in shapes]
            for row in rows:
                assert row['kernel_launches']==0 and row['performance_measurement'] is False
            for row in resource:
                expected=prepared['source_variants'][row['source_variant']]
                assert row['source_fnv1a64']==expected['fnv1a64'] and row['source_bytes']==expected['bytes']
                shape=next(s for s in shapes if s['id']==row['shape'])
                assert row['nh_o']==shape['nh_o'] and row['max_valid_opponent_hands']==shape['m_max']
                assert row['dynamic_shared_bytes']==shape[row['source_variant']+'_dynamic_bytes']
                assert row['max_threads_per_block']>0 and row['static_shared_bytes']>=0
            ptx={v:(HERE/(v+'.ptx')).read_text(encoding='utf-8') for v in ['baseline','candidate']}
            summaries={}
            for variant in ptx:
                code=entry(ptx[variant],'up_show')
                bytes_new(variant+'-up_show.ptx',(code+'\n').encode())
                summaries[variant]={'opcodes_static_only':opcodes(code),'entry_sha256':hashlib.sha256(code.encode()).hexdigest()}
            names={v:re.findall(r'\.visible\s+\.entry\s+(\w+)\(',ptx[v]) for v in ['baseline','candidate']}
            assert names['baseline']==names['candidate']
            unchanged={name:entry(ptx['baseline'],name)==entry(ptx['candidate'],name) for name in names['baseline'] if name!='up_show'}
            report={'id':'D037','status':'completed_compiler_resource_diagnostic','prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
                'complete':rows[-1],'records':rows,'ptx':summaries,'other_entry_ptx_byte_equality':unchanged,'commands':commands,
                'telemetry_after':telemetry_after,'input_sha256_after':{n:sha(HERE/n) for n in prepared['artifact_sha256']},
                'binary_sha256':sha(HERE/'probe.exe'),'kernel_launches':0,'performance_measurement':False,
                'solver_executions':0,'numerical_validation':'not executed','candidate_accepted':False,
                'limits':['No kernel launch, numerical comparison or solver execution occurred.',
                    'Rainbow allocations were observed; river allocation follows final-board metadata; two-tone fixture-specific occupancy was not queried.',
                    'Full1326 and empty/single valid-opponent rows are conservative/synthetic resource shapes.',
                    'PTX static opcode counts and theoretical occupancy are not timings, bandwidth savings or runtime exactness.',
                    'Compiler/probe process duration is audit metadata, never solver performance.']}
            save('report.json',report)
            heartbeat('complete; independent result audit pending',0)
            print(json.dumps({'id':'D037','complete':rows[-1],'report':str(HERE/'report.json')},indent=2))
    except BaseException as error:
        save('failure.json',{'at':now(),'error':repr(error),'commands':commands,'instruction':'Preserve failure; no retry/overwrite in this directory.'})
        try:heartbeat('invalid; evidence retained',0)
        except BaseException:pass
        raise

if __name__=='__main__':main()
