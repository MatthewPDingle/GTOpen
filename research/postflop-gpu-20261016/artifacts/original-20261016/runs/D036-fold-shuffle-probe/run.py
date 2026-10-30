"""D036 one-shot standalone build/numerical probe; root executes in serialized slot."""
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
    spec=importlib.util.spec_from_file_location('d036_runner_primitives',HERE/'runner-primitives-source.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.REPO=REPO
    commands=[]
    def heartbeat(stage,elapsed=0):
        with runner.exclusive_lock(STATUS.with_suffix('.lock'),timeout=3):
            state=json.loads(STATUS.read_text(encoding='utf-8-sig'))
            state['updated_at']=runner.now()
            state['stage']='D036 standalone fold-kernel diagnostic'
            state['activity']=f'D036 {stage}; {elapsed:.0f}s elapsed. Exact kernel/corpus diagnostic only; accepted E015 and deployment status unchanged.'
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
            save('execution-manifest.json',{'id':'D036','prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
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
            rows=[json.loads(line[len('D036_PROBE '):]) for line in (HERE/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if line.startswith('D036_PROBE ')]
            assert len([r for r in rows if r['stage']=='complete'])==1 and rows[-1]['stage']=='complete'
            assert not any(r['stage']=='invalid' for r in rows)
            complete=rows[-1]
            assert complete['required_exact'] and complete['all_observed_gpu_bits_exact']
            assert complete['kernel_launches']==370 and complete['full_case_pairs']==180
            assert complete['required_raw_case_pairs']==1040 and complete['all_raw_case_pairs']==1120
            assert len([r for r in rows if r['stage']=='resource'])==8
            assert len([r for r in rows if r['stage']=='raw_total_exact'])==5
            assert len([r for r in rows if r['stage']=='full_fold_exact'])==180
            assert all(r.get('optional_bit_mismatches',0)==0 for r in rows)
            ptx={v:(HERE/(v+'.ptx')).read_text(encoding='utf-8') for v in ['baseline','candidate','raw-baseline','raw-candidate']}
            summaries={}
            for variant in ptx:
                name='raw_total' if variant.startswith('raw-') else 'up_fold'
                code=entry(ptx[variant],name)
                bytes_new(variant+'-'+name+'.ptx',(code+'\n').encode())
                summaries[variant]={'opcodes_static_only':opcodes(code),'entry_sha256':hashlib.sha256(code.encode()).hexdigest()}
            names={v:re.findall(r'\.visible\s+\.entry\s+(\w+)\(',ptx[v]) for v in ['baseline','candidate']}
            assert names['baseline']==names['candidate']
            unchanged={name:entry(ptx['baseline'],name)==entry(ptx['candidate'],name) for name in names['baseline'] if name!='up_fold'}
            report={'id':'D036','status':'completed_standalone_exact_kernel_probe','prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
                'complete':complete,'records':rows,'ptx':summaries,'other_entry_ptx_byte_equality':unchanged,'commands':commands,
                'telemetry_after':telemetry_after,'input_sha256_after':{n:sha(HERE/n) for n in prepared['artifact_sha256']},
                'binary_sha256':sha(HERE/'probe.exe'),'raw_results_sha256':sha(HERE/'raw-results.jsonl'),
                'performance_measurement':False,'solver_executions':0,'candidate_accepted':False,
                'limits':['Only the frozen constructed cases were executed; no solver lifecycle or end-to-end claim.',
                    'All observed GPU bits include overflow outputs. No claim for NaN/Inf input payloads or all possible finite inputs.',
                    'CPU same-tree oracle applies to finite-domain raw totals only; full compiled baseline is authoritative for CFVs.',
                    'PTX static opcode counts and occupancy are not timings or dynamic barrier measurements.',
                    'Compiler/probe process duration is audit metadata, never solver performance.']}
            save('report.json',report)
            heartbeat('complete; independent result audit pending',0)
            print(json.dumps({'id':'D036','complete':complete,'report':str(HERE/'report.json')},indent=2))
    except BaseException as error:
        save('failure.json',{'at':now(),'error':repr(error),'commands':commands,'instruction':'Preserve failure; no retry/overwrite in this directory.'})
        try:heartbeat('invalid; evidence retained',0)
        except BaseException:pass
        raise

if __name__=='__main__':main()
