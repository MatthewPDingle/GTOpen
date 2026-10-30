"""E030_DIRECT one-shot complete-fold card-task-order exact-kernel probe; root executes in serialized slot."""
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
        for name,h in prepared['protected_checkout_sha256'].items():assert sha(REPO/name)==h,('Accepted E020 source must be restored before E030_DIRECT',name)
        assert sha(HERE/'prepared-manifest.json')==args.prepared_manifest_sha256
        for name,info in prepared['references'].items():assert sha(info['path'])==info['sha256'],('Reference changed',name)
        source_review=json.loads(Path(prepared['references']['E030_source_review']['path']).read_text(encoding='utf-8'))
        assert source_review['independent_source_review_pass'] is True
    verify()
    save('execution-started.json',{'at':now(),'prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
        'operator_obligation':'Root owns serialized build/GPU slot; no concurrent unrelated build/GPU job',
        'per_stage_timeout_seconds':STAGE_TIMEOUT_SECONDS})
    spec=importlib.util.spec_from_file_location('e030_direct_runner_primitives',HERE/'runner-primitives-source.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.REPO=REPO
    commands=[]
    def heartbeat(stage,elapsed=0):
        with runner.exclusive_lock(STATUS.with_suffix('.lock'),timeout=3):
            state=json.loads(STATUS.read_text(encoding='utf-8-sig'))
            state['updated_at']=runner.now()
            state['stage']='E030_DIRECT standalone fold card-task-order exact diagnostic'
            state['activity']=f'E030_DIRECT {stage}; {elapsed:.0f}s elapsed. Fixed180 complete-kernel comparisons only; no performance claim; accepted E020 and deployment status unchanged.'
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
            save('execution-manifest.json',{'id':'E030-direct','prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
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
            rows=[json.loads(line[len('E030_DIRECT_EXACT '):]) for line in (HERE/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if line.startswith('E030_DIRECT_EXACT ')]
            assert [r['stage'] for r in rows]==['harness_checks','device']+['full_fold_exact']*180+['complete']
            hc=rows[0];assert hc['metadata_validated'] is True and hc['full_scenarios']==17
            assert hc['baseline_offset_words']==53 and hc['candidate_offset_words']==105
            assert hc['expected_bit_injection_rejected'] is True and hc['guard_injection_rejected'] is True and hc['counts_as_gpu_numerical_case'] is False
            device=rows[1];assert device['device']=='NVIDIA GeForce RTX 5090' and device['architecture']=='compute_120'
            assert device['production_block']==128 and device['tested_blocks']==[128,16,32,64,256]
            assert device['max_threads_per_block']>=256 and device['performance_measurement'] is False
            assert [r['variant'] for r in device['resources']]==['baseline','candidate']
            for resource in device['resources']:
                variant=resource['variant'];assert resource['source_fnv1a64']==prepared['source_variants'][variant]['fnv1a64']
                assert resource['source_bytes']==prepared['source_variants'][variant]['bytes'] and resource['max_threads_per_block']>=256
                assert resource['static_shared_bytes']+1326*4<=device['max_shared_bytes_per_block_default']
            corpus=json.loads((HERE/'corpus.json').read_text(encoding='utf-8'))
            summary=json.loads((HERE/'corpus-summary.json').read_text(encoding='utf-8'))
            scenarios={r['id']:r for r in corpus['full_scenarios']};cases=summary['fixed_pair_order']
            assert len(cases)==180 and len(scenarios)==17
            raw=[json.loads(line) for line in (HERE/'raw-results.jsonl').read_text(encoding='utf-8').splitlines()]
            assert len(raw)==360
            def fnv_bytes(data):
                h=0xcbf29ce484222325
                for byte in data:h=((h^byte)*0x100000001b3)&0xffffffffffffffff
                return f'{h:016x}'
            def words_hash(v):return fnv_bytes(byte for word in v for byte in word.to_bytes(4,'little'))
            assert hc['corpus_fnv1a64']==fnv_bytes((HERE/'corpus.json').read_bytes())
            def finite(v):return v&0x7f800000!=0x7f800000
            def nf(v):return {'count':sum(not finite(w) for w in v),'first_16':[{'index':i,'bits':f'{w:08x}'} for i,w in enumerate(v) if not finite(w)][:16]}
            def padded(v):return v or [corpus['guard_bits']]
            def inputs(sc,variant):
                return {'nodes':sc['nodes'],'owner':[v['owner'] for v in sc['node_meta']],
                    'twin':[v['twin_bits'] for v in sc['node_meta']],'tlose':[v['tlose_bits'] for v in sc['node_meta']],
                    'rsrc0':sc['rsrc0'],'rsrc1':sc['rsrc1'],'reach0':sc['reach0_bits'],'reach1':sc['reach1_bits'],
                    'pc1':padded(sc['pc1']),'pc2':padded(sc['pc2']),
                    'card_off':sc['card_off'] if variant=='baseline' else sc['candidate_card_off'],
                    'card_idx':padded(sc['card_idx']),'same_p':padded(sc['same_p']),'cfv_slot':sc['cfv_slot']}
            totals={'comparison_pairs':180,'kernel_launches':360,'active_words_per_arm':0,'required_finite_words_per_arm':0,
                'required_nonzero_words':0,'output_guard_checks_both_arms':0,'input_buffer_checks_both_arms':0,'input_word_checks_both_arms':0}
            nonfinite_words=0
            for number,(case,row) in enumerate(zip(cases,rows[2:-1])):
                sc=scenarios[case['scenario']];active={};a,b=raw[2*number:2*number+2]
                for key in ['scenario','block','p','count']:assert row[key]==a[key]==b[key]==case[key]
                assert a['variant']=='baseline' and b['variant']=='candidate' and a['scope']==b['scope']=='full_up_fold'
                for node in sc['nodes'][sc['start']:sc['start']+case['count']]:
                    for hand in range(sc['nh_p']):
                        i=sc['cfv_slot'][node]*sc['nh_max']+hand
                        assert i not in active and 0<=i<sc['cfv_words'];active[i]=sc['node_meta'][node]['required']
                before=a['output_bits'];after=b['output_bits'];assert len(before)==len(after)==sc['cfv_words'] and before==after
                assert all(type(v) is int and 0<=v<=0xffffffff for v in before+after)
                assert all(v==corpus['guard_bits'] for i,v in enumerate(before) if i not in active)
                required=[before[i] for i,req in active.items() if req];overflow=[before[i] for i,req in sorted(active.items()) if not req]
                assert all(finite(v) for v in required)
                changed=sum(v!=corpus['guard_bits'] for v in required);nonzero=sum(v!=corpus['guard_bits'] and v&0x7fffffff!=0 for v in required)
                if required:assert changed>0
                assert row['nh_p']==sc['nh_p'] and row['nh_o']==sc['nh_o'] and row['dynamic_shared_bytes']==4*sc['nh_o']
                assert row['required_words']==len(required)==case['required_words'] and row['active_words']==len(active)==case['active_words']
                assert row['required_nonzero_words_excluding_stale_guard']==nonzero and row['required_changed_words']==changed
                assert row['optional_bit_mismatches']==0 and row['optional_baseline_nonfinite']==row['optional_candidate_nonfinite']==nf(overflow)
                assert row['guard_words_checked_per_variant']==case['guard_words_per_arm']==sc['cfv_words']-len(active)
                assert row['baseline_hash']==words_hash(before) and row['candidate_hash']==words_hash(after)
                assert row['all_input_buffers_bitwise_immutable'] is True and row['performance_measurement'] is False and row['device_input_buffer_checks']==28
                pair_words=0
                for image in [a,b]:
                    expected=inputs(sc,image['variant']);observed=image['input_readbacks']
                    assert len(expected)==len(observed)==14 and [r['name'] for r in observed]==list(expected)
                    for rec,(name,values) in zip(observed,expected.items()):
                        assert rec['words']==len(values) and rec['expected_fnv1a64']==rec['actual_fnv1a64']==words_hash(values)
                        pair_words+=len(values)
                assert pair_words==case['input_words_both_arms']
                totals['active_words_per_arm']+=len(active);totals['required_finite_words_per_arm']+=len(required);totals['required_nonzero_words']+=nonzero
                totals['output_guard_checks_both_arms']+=2*(sc['cfv_words']-len(active));totals['input_buffer_checks_both_arms']+=28;totals['input_word_checks_both_arms']+=pair_words
                nonfinite_words+=sum(not finite(v) for v in overflow)
            complete=rows[-1];assert complete['totals']==totals
            assert totals['required_nonzero_words']>0
            for k,v in summary['totals'].items():
                if k!='output_words_per_arm':assert totals[k]==v
            assert complete['required_exact'] is True and complete['all_observed_gpu_bits_exact'] is True
            assert complete['input_immutability'] is True and complete['output_guards'] is True and complete['overflow_reported_separately'] is True
            assert complete['nan_input_payload_guarantee'] is False and complete['raw_kernel_launches']==0
            assert complete['production_block']==128 and complete['supplementary_blocks']==[16,32,64,256]
            assert complete['solver_executions']==0 and complete['performance_measurement'] is False and complete['candidate_accepted'] is False
            ptx={v:(HERE/(v+'.ptx')).read_text(encoding='utf-8') for v in ['baseline','candidate']}
            names={v:re.findall(r'\.visible\s+\.entry\s+(\w+)\(',ptx[v]) for v in ptx}
            assert names['baseline']==names['candidate'] and len(names['baseline'])==9
            abi={name:entry(ptx['baseline'],name).split('{',1)[0]==entry(ptx['candidate'],name).split('{',1)[0] for name in names['baseline']}
            assert all(abi.values())
            unchanged={name:entry(ptx['baseline'],name)==entry(ptx['candidate'],name) for name in names['baseline'] if name!='up_fold'}
            assert len(unchanged)==8 and all(unchanged.values())
            for variant in ['baseline','candidate']:bytes_new(variant+'-up_fold.ptx',(entry(ptx[variant],'up_fold')+'\n').encode())
            report={'id':'E030-direct','status':'completed_exact_complete_up_fold_comparison','verdict':'PASS_EXACT_COMPLETE_UP_FOLD_COMPARISON',
                'exactness_pass':True,'numerical_validation':'executed','prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
                'protocol_sha256':prepared['protocol_sha256'],'corpus_sha256':sha(HERE/'corpus.json'),
                'baseline_cuda_sha256':prepared['source_variants']['baseline']['sha256'],'candidate_cuda_sha256':prepared['source_variants']['candidate']['sha256'],
                'production_threads':128,'block_shapes':[128,16,32,64,256],'each_pair_same_block_shape':True,'comparison_pairs':180,'kernel_launches':360,
                'complete':complete,'records':rows,'nonfinite_overflow_words_per_arm':nonfinite_words,'other_eight_entry_ptx_exact':unchanged,'all_entry_abi_exact':abi,
                'commands':commands,'telemetry_after':telemetry_after,'binary_sha256':sha(HERE/'probe.exe'),'raw_results_sha256':sha(HERE/'raw-results.jsonl'),
                'input_sha256_after':{name:sha(HERE/name) for name in prepared['artifact_sha256']},
                'solver_executions':0,'performance_measurement':False,'candidate_accepted':False,'deployment_changed':False,
                'limits':['All fixed observed output bits including finite-overflow-derived nonfinite values must match; no NaN-input/payload generalization.',
                    '128 is the production shape.16/32/64/256 are supplemental same-shape controls, with no cross-shape numerical equality assertion.',
                    'This direct float-kernel corpus does not validate host sorting/accounting or full solver/continuation lifecycle and complete-cycle performance.',
                    'No timing/resource nonregression gate or performance acceptance. Independent terminal audit is required before root may authorize E030 activation.']}
            save('report.json',report)
            heartbeat('complete; independent numerical audit pending',0)
            print(json.dumps({'id':'E030-direct','complete':complete,'report':str(HERE/'report.json')},indent=2))
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
