"""One-shot byte-exact retained-export and pre-write boundary qualification."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',PYTHONDONTWRITEBYTECODE='1')
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import threading
import time
import traceback
import psutil
import ntfs_expected_retention_v2 as ntfs
import preflop_expected_native_execution_v2 as execution

STAGE=Path(__file__).resolve().parent
REPO=Path(r'T:\Dev\GTOpen')
BUILD=Path(r'S:\GTOpen-research\native-bounded-export-build-v1')
STORE=Path(r'S:\GTOpen-research\native-bounded-export-controls-v1')
REVIEW=STAGE/'native-bounded-export-review-v1/representative-controls.json'
SOURCE_REVIEW=STAGE/'native-bounded-export-review-v1/source-review-publication-v2/result.json'
STOP=threading.Event()
CHECK_LOCK=threading.Lock()
LAST_PRODUCTION_CHECK=0.
MAX_LOGICAL=1_000_000_000
sys.path.append(str(REPO/'tools/research'))
from bounded_parallel_evaluation_archive_v2 import production_available
def sha(path):return execution.sha(path)
def read(path):return json.loads(Path(path).read_bytes())
def write(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as file:
        file.write(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n')
        file.flush();os.fsync(file.fileno())
def guard():
    global LAST_PRODUCTION_CHECK
    if STOP.is_set():raise InterruptedError('Another independent control failed; preserve evidence')
    if psutil.virtual_memory().available<24_000_000_000:raise ValueError('Native-control free RAM reserve')
    if psutil.disk_usage('S:\\').free<20_000_000_000:raise ValueError('Native-control volume reserve')
    with CHECK_LOCK:
        if time.monotonic()-LAST_PRODUCTION_CHECK>2:
            if not production_available():raise InterruptedError('Yielding to active production solve')
            LAST_PRODUCTION_CHECK=time.monotonic()
def pins_for(exe,reference):
    pins={str(exe):sha(exe),str(Path(__file__).resolve()):sha(__file__),str(STAGE/'preflop_expected_native_execution_v2.py'):sha(STAGE/'preflop_expected_native_execution_v2.py')}
    pins.update({row['new']:row['new_sha256'] for row in read(STAGE/'native-bounded-export-sources-v2/publication.json')['sources']})
    helper=REPO/'crates/solver/examples/research_sampled/research_bounded_output_v1.rs';pins[str(helper)]=sha(helper)
    for item in reference.get('request_inputs',[]):pins[item['path']]=item['sha256']
    if reference.get('stdin'):pins[reference['stdin']['path']]=reference['stdin']['sha256']
    return pins
def invoke(exe,args,folder,label,pins,cap,stdin=None,direct=(),expect_success=True):
    folder.mkdir(parents=True,exist_ok=False)
    try:
        result=execution.run_native(str(exe),list(args),folder=folder,label=label,
            expected_identities=pins,guard=guard,timeout=120,max_output_bytes=cap,
            stdin_path=stdin,direct_outputs=direct)
    except BaseException as error:
        receipt_path=folder/(label+'-receipt.json')
        if not receipt_path.is_file():raise
        receipt=read(receipt_path)
        if expect_success:raise
        if (receipt['outcome']!='failed' or receipt['returncode'] not in (1,101)
                or receipt['stdout']['bytes']!=0 or receipt['stderr']['bytes'] not in (25,27)
                or any(item['exists'] for item in receipt['direct_output_artifacts'])):
            raise AssertionError('Expected pre-write refusal was partial, unbounded or incorrectly terminated') from error
        expected_message=b'Research exporter failed\n' if receipt['returncode']==1 else b'Research exporter panicked\n'
        if Path(receipt['stderr']['path']).read_bytes()!=expected_message:raise AssertionError('Nonfixed failure diagnostic')
        return dict(passed=True,expected_refusal=True,exception=dict(type=type(error).__name__,message=str(error)),receipt_path=str(receipt_path),receipt_sha256=sha(receipt_path),receipt=receipt)
    if not expect_success:raise AssertionError('An over-budget or invalid output was accepted')
    execution.verify_native(result,executable=str(exe),arguments=list(args),expected_identities=pins,
        timeout=120,max_output_bytes=cap,stdin_path=stdin,direct_outputs=direct)
    return dict(passed=True,result=result)
def compare(path,expected):
    if Path(path).stat().st_size!=expected['bytes'] or sha(path)!=expected['sha256']:
        raise AssertionError('Byte-exact retained native payload mismatch: '+str(path))
def primary_case(index,reference,binaries):
    group=reference['group'];name=f'{index:02d}-{group}';root=STORE/name;root.mkdir()
    role='bridge' if group.startswith('bridge') else ('river' if group.startswith('river') else group)
    exe=Path(binaries[role]['path']);pins=pins_for(exe,reference)
    direct_index=5 if role=='bridge' else (4 if role=='trace' else None)
    threshold=reference['expected_stdout']['bytes']+reference['expected_stderr']['bytes']+256
    if direct_index is not None:threshold+=reference['expected_payload']['bytes']
    out=[]
    try:
        for label,cap,success in [('inclusive',threshold,True),('one-extra',threshold+1,True),('one-short',threshold-1,False)]:
            folder=root/label;args=reference['original_argv'][1:].copy();direct=[]
            if direct_index is not None:
                output=folder/'payload.json';args[direct_index-1]=str(output)
                direct=[dict(path=str(output),argument_index=direct_index)]
            args.append('--output-byte-limit='+str(cap))
            result=invoke(exe,args,folder,'native',pins,cap,
                stdin=reference['stdin']['path'] if reference['stdin'] else None,direct=direct,expect_success=success)
            if success:
                receipt=result['result']['receipt']
                compare(receipt['stdout']['path'],reference['expected_stdout']);compare(receipt['stderr']['path'],reference['expected_stderr'])
                payload=receipt['direct_output_artifacts'][0]['path'] if direct_index is not None else receipt['stdout']['path']
                compare(payload,reference['expected_payload'])
            out.append(dict(label=label,limit=cap,**result))
        result=dict(passed=True,role=role,group=group,reference=reference,threshold=threshold,invocations=out)
        write(root/'result.json',result);return result
    except BaseException:
        STOP.set();write(root/'failure.json',dict(passed=False,traceback=traceback.format_exc(),completed=out));raise
def helper_controls():
    folder=STORE/'serialization-helper';folder.mkdir()
    source=STAGE/'research_bounded_output_control_v1.rs';exe=folder/'bounded-output-control.exe'
    args=[r'C:\Users\there\.cargo\bin\rustc.exe',str(source),'--edition=2021','-C','panic=unwind','-C','opt-level=2','-o',str(exe)]
    compiled=subprocess.run(args,stdin=subprocess.DEVNULL,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    (folder/'compile-stdout.bin').write_bytes(compiled.stdout);(folder/'compile-stderr.bin').write_bytes(compiled.stderr)
    if compiled.returncode:raise RuntimeError('Shared output helper compilation failed')
    write(folder/'build.json',dict(argv=args,returncode=compiled.returncode,source_sha256=sha(source),helper_sha256=sha(STAGE/'research_bounded_output_v1.rs'),binary_sha256=sha(exe)))
    raw=b'{"array":[true,false,null,1,-2,0.125],"nested":{"\\u00e9":"line\\n\\t","unicode":"'+ '♠é'.encode() + b'"}}'
    fixture=folder/'fixture.json';fixture.write_bytes(raw)
    pins={str(exe):sha(exe),str(source):sha(source),str(fixture):sha(fixture),str(STAGE/'research_bounded_output_v1.rs'):sha(STAGE/'research_bounded_output_v1.rs')}
    results=[];threshold=len(raw)+9+256
    cases=[('inclusive','bytes',threshold,True),('one-extra','bytes',threshold+1,True),('one-short','bytes',threshold-1,False),
        ('empty','empty',256,True),('large-error','large-error',256,False),('large-panic','large-panic',256,False),
        ('invalid-zero','bytes',256,False),('above-ceiling','bytes',2048,False),('invalid-text','bytes',256,False),
        ('default-cap','bytes',2048,True),('stdio-only','stdio',len(raw)+5+256,True)]
    for label,mode,cap,success in cases:
        destination=folder/label/'direct.bin';cli=[mode,str(fixture),str(destination)]
        if label!='default-cap':
            requested={'invalid-zero':'0','above-ceiling':'2049','invalid-text':'x'}.get(label,str(cap));cli.append('--output-byte-limit='+requested)
        direct=[dict(path=str(destination),argument_index=3)] if mode in ('bytes','empty') and success else []
        # Failed helper cases declare a new direct path too, so its absence is witnessed.
        if mode=='bytes' and not success:direct=[dict(path=str(destination),argument_index=3)]
        r=invoke(exe,cli,folder/label,'helper',pins,cap,direct=direct,expect_success=success)
        if success:
            record=r['result']['receipt']
            if mode=='bytes':
                if destination.read_bytes()!=raw or Path(record['stdout']['path']).read_bytes()!=b'out\n' or Path(record['stderr']['path']).read_bytes()!=b'note\n':raise AssertionError('Helper changed serialized bytes')
            elif mode=='stdio' and Path(record['stdout']['path']).read_bytes()!=raw:raise AssertionError('Helper changed stdout bytes')
            elif mode=='empty' and destination.read_bytes()!=b'':raise AssertionError('Empty output changed')
        results.append(dict(label=label,**r))
    for label,directory in [('existing-file',False),('existing-directory',True)]:
        case=folder/label;case.mkdir();target=case/'sentinel'
        if directory:target.mkdir()
        else:target.write_bytes(b'owned-new-sentinel\n')
        before=ntfs.file_identity(target);digest=None if directory else sha(target)
        extra=dict(pins)
        if not directory:extra[str(target)]=digest
        r=invoke(exe,['bytes',str(fixture),str(target),'--output-byte-limit='+str(threshold)],case/'capture','helper',extra,threshold,expect_success=False)
        after=ntfs.file_identity(target)
        if before!=after or (not directory and sha(target)!=digest):raise AssertionError('Existing output was modified')
        results.append(dict(label=label,sentinel_preserved=True,**r))
    write(folder/'result.json',dict(passed=True,cases=results,scope='Raw serialized-byte sink controls; native serializer parity tested separately.'))
    return results
def river_input_controls(reference,binary):
    root=STORE/'river-input-limits';root.mkdir();exe=Path(binary['path']);results=[]
    context=Path(reference['original_argv'][1]).read_bytes();request=Path(reference['stdin']['path']).read_bytes()
    for label,kind,length,success in [('context-at-limit','context',16*1024*1024,True),('context-over-limit','context',16*1024*1024+1,False),
        ('request-at-limit','request',64*1024,True),('request-over-limit','request',64*1024+1,False),('malformed-request','malformed',1,False)]:
        source=root/(label+'.json');original=context if kind=='context' else request
        source.write_bytes(b'{' if kind=='malformed' else original+b' '*(length-len(original)))
        args=[str(source) if kind=='context' else reference['original_argv'][1],'--output-byte-limit=64000000']
        stdin=reference['stdin']['path'] if kind=='context' else str(source)
        pins=pins_for(exe,reference);pins[str(source)]=sha(source)
        r=invoke(exe,args,root/label,'river',pins,64_000_000,stdin=stdin,expect_success=success)
        if success:
            payload=read(r['result']['stdout_path']);saved=read(reference['expected_payload']['path'])
            if payload['targets']!=saved['targets'] or payload['total_nodes']!=saved['total_nodes']:raise AssertionError('Whitespace-only input changed native calculation')
            if payload['context_source']!=Path(args[0]).read_text() or payload['request_source']!=Path(stdin).read_text():raise AssertionError('Input admission altered source bytes')
        results.append(dict(label=label,**r))
    write(root/'result.json',dict(passed=True,cases=results));return results
def main():
    if STORE.exists():raise FileExistsError('Never retry this started qualification namespace')
    build=read(BUILD/'result.json')
    if build.get('passed') is not True or read(SOURCE_REVIEW).get('source_review_passed') is not True:raise ValueError('Required build and source review not passed')
    if not production_available():raise ValueError('Production solve active; no control admitted')
    if time.time()-read(BUILD/'inventory.json')['observed_unix']>3600:raise ValueError('Fresh complete global allocation snapshot required')
    snapshot=read(BUILD/'inventory.json')
    if snapshot['allocated_total_bytes']+5_000_000_000+1_500_000_000>800_000_000_000:raise ValueError('Global qualified-build plus control reserve exceeded')
    artifacts={k:v for record in build['builds'] for k,v in record['artifacts'].items()}
    names={'board':'hu_fixed_board_tree_bounded_v2','bridge':'hu_sampled_allin_history_bridge_bounded_v2','trace':'hu_sampled_action_trace_bounded_v3','river':'hu_river_two_stage_stream_bounded_v2'}
    binaries={role:artifacts[name] for role,name in names.items()};references=read(REVIEW)['primary']
    pins={str(Path(__file__).resolve()):sha(__file__),str(REVIEW):sha(REVIEW),str(SOURCE_REVIEW):sha(SOURCE_REVIEW),str(BUILD/'result.json'):sha(BUILD/'result.json'),
        str(STAGE/'preflop_expected_native_execution_v2.py'):sha(STAGE/'preflop_expected_native_execution_v2.py'),str(STAGE/'ntfs_expected_retention_v2.py'):sha(STAGE/'ntfs_expected_retention_v2.py'),
        str(STAGE/'research_bounded_output_control_v1.rs'):sha(STAGE/'research_bounded_output_control_v1.rs'),str(STAGE/'research_bounded_output_v1.rs'):sha(STAGE/'research_bounded_output_v1.rs')}
    pins.update(build['source_identities'])
    for binary in binaries.values():pins[binary['path']]=binary['sha256']
    for reference in references:
        for item in [*reference['request_inputs'],reference['original_executable'],reference['original_receipt'],reference['expected_payload'],reference['expected_stdout'],reference['expected_stderr'],*([reference['stdin']] if reference['stdin'] else [])]:pins[item['path']]=item['sha256']
    for path,digest in pins.items():
        if sha(path)!=digest:raise ValueError('Qualification source/reference changed: '+path)
    ntfs.create_new_store(STORE)
    registration=dict(format=1,name=STORE.name,created_unix=time.time(),source_identities=pins,references=references,binaries=binaries,
        maximum_parallel_native_children=6,maximum_logical_control_files=MAX_LOGICAL,control_and_metadata_reserve=1_500_000_000,
        boundary='T=direct+stdout+stderr+256; pass T and T+1, reject T-1 before any payload write',
        additional_cases='13 raw-byte helper cases and5 existing river-input boundary/malformed cases',
        scope='One-shot retained-request software qualification; no new deals, policy inference, model fitting, scientific attempt, production change or accuracy claim.')
    write(STORE/'registration.json',registration);began=time.monotonic()
    try:
        helper=helper_controls()
        with ThreadPoolExecutor(6) as pool:primary=list(pool.map(lambda item:primary_case(*item,binaries),enumerate(references)))
        river=river_input_controls(references[5],binaries['river'])
        for path,digest in pins.items():
            if sha(path)!=digest:raise ValueError('Original or qualified source changed during controls')
        measurement=ntfs.measure_tree(STORE,guard)
        if measurement['logical_bytes']>MAX_LOGICAL:raise ValueError('Control logical storage envelope exceeded')
        result=dict(passed=True,seconds=time.monotonic()-began,primary=primary,helper=helper,river_input=river,
            native_control_invocations=21+len(helper)+len(river),source_identities=pins,measurement=measurement,
            registered_budget_sha256=sha(STORE/'registration.json'),accuracy_proven=False,originals_preserved=True)
        write(STORE/'result.json',result)
        print(json.dumps(dict(passed=True,seconds=result['seconds'],invocations=result['native_control_invocations'],measurement=measurement,store=str(STORE))),flush=True)
    except BaseException:
        STOP.set();write(STORE/'failure.json',dict(passed=False,seconds=time.monotonic()-began,traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
