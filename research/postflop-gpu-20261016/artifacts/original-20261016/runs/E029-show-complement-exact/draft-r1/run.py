"""E029_DIRECT one-shot complete-showdown exact-kernel probe; root executes in serialized slot."""
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
        for name,h in prepared['protected_checkout_sha256'].items():assert sha(REPO/name)==h,('Accepted E020 source must be restored before E029_DIRECT',name)
        assert sha(HERE/'prepared-manifest.json')==args.prepared_manifest_sha256
        for name,info in prepared['references'].items():assert sha(info['path'])==info['sha256'],('Reference changed',name)
    verify()
    save('execution-started.json',{'at':now(),'prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
        'operator_obligation':'Root owns serialized build/GPU slot; no concurrent unrelated build/GPU job',
        'per_stage_timeout_seconds':STAGE_TIMEOUT_SECONDS})
    spec=importlib.util.spec_from_file_location('e029_direct_runner_primitives',HERE/'runner-primitives-source.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.REPO=REPO
    commands=[]
    def heartbeat(stage,elapsed=0):
        with runner.exclusive_lock(STATUS.with_suffix('.lock'),timeout=3):
            state=json.loads(STATUS.read_text(encoding='utf-8-sig'))
            state['updated_at']=runner.now()
            state['stage']='E029_DIRECT standalone complement-only showdown exact diagnostic'
            state['activity']=f'E029_DIRECT {stage}; {elapsed:.0f}s elapsed. Fixed152 complete-kernel comparisons only; no performance claim; accepted E020 and deployment status unchanged.'
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
            save('execution-manifest.json',{'id':'E029_DIRECT','prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
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
            rows=[json.loads(line[len('E029_DIRECT_EXACT '):]) for line in (HERE/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if line.startswith('E029_DIRECT_EXACT ')]
            assert [r['stage'] for r in rows]==['corpus_validated','device']+['full_show_exact']*152+['complete']
            assert rows[0]['geometries']==40 and rows[0]['comparison_pairs']==152 and rows[0]['accepted_rank_oracle'] is True
            assert rows[0]['host_verifier_injections_rejected']==2 and rows[0]['host_injections_are_gpu_cases'] is False
            device=rows[1];assert device['device']=='NVIDIA GeForce RTX 5090' and device['architecture']=='compute_120'
            assert device['baseline_physical_threads']==128 and device['candidate_physical_threads']==128 and device['logical_scan_threads']==128
            for variant in ['baseline','candidate']:assert device[variant+'_source_fnv1a64']==prepared['source_variants'][variant]['fnv1a64']
            corpus=json.loads((HERE/'corpus.json').read_text(encoding='utf-8'));cases=corpus['cases'];geometries={g['id']:g for g in corpus['geometries']}
            raw=[json.loads(line) for line in (HERE/'raw-results.jsonl').read_text(encoding='utf-8').splitlines()]
            assert len(raw)==152 and [r['case_id'] for r in rows[2:-1]]==[c['id'] for c in cases]
            totals={'active_words':0,'guard_word_checks':0,'device_input_buffer_checks':0,'device_input_word_checks':0,'active_overwritten_words':0,'nonzero_active_words':0}
            def words_hash(v):
                h=0xcbf29ce484222325
                for word in v:
                    for byte in word.to_bytes(4,'little'):h=((h^byte)*0x100000001b3)&0xffffffffffffffff
                return f'{h:016x}'
            nonfinite=0
            for case,row,full in zip(cases,rows[2:-1],raw):
                assert full['record']==row
                g=geometries[case['geometry']];active=[bool(case['count'] and v) for v in g['output_active']]
                before=full['baseline_output_bits'];after=full['candidate_output_bits'];initial=g['output_initial']
                assert len(before)==len(after)==len(initial) and before==after
                assert all(type(x) is int and 0<=x<=0xffffffff for x in before+after)
                assert all(before[i]==initial[i] and after[i]==initial[i] for i,a in enumerate(active) if not a)
                ac=sum(active);gc=2*(len(active)-ac)
                assert row['count']==case['count'] and row['geometry']==g['id'] and row['profile']==case['profile']
                for key in ['m_p','m_o','nh_p','nh_o','dynamic_shared_bytes','target_m','player']:assert row[key]==g[key]
                assert row['active_words']==ac and row['guard_word_checks']==gc and row['device_input_buffer_checks']==43
                iw=2*(sum(len(v) for k,v in g['arrays'].items() if k!='p_missing_idx')+len(case['reach_o_bits']))+len(g['arrays']['p_missing_idx'])
                assert row['device_input_word_checks']==iw and row['all_output_bits_exact'] is True and row['input_bits_unchanged'] is True
                selected=[v for v,a in zip(before,active) if a]
                assert row['active_overwritten_words']==sum(v!=corpus['guard'] for v in selected)==ac
                assert row['nonzero_active_words']==sum(v!=corpus['guard'] and v&0x7fffffff!=0 for v in selected)
                if case['count'] and g['target_m']>=127 and case['profile']!='all_zero':assert row['nonzero_active_words']>0
                if case['profile']=='all_zero' or g['m_p']==0 or g['m_o']==0:assert all(v==0 for v in selected)
                nf=[{'index':i,'bits':v} for i,v in enumerate(selected) if v&0x7f800000==0x7f800000]
                assert row['nonfinite_active']=={'count':len(nf),'words':nf};nonfinite+=len(nf)
                assert row['baseline_output_fnv1a64']==words_hash(before) and row['candidate_output_fnv1a64']==words_hash(after)
                for key in totals:totals[key]+=row[key]
            complete=rows[-1]
            assert complete['comparison_pairs']==152 and complete['kernel_launches']==304 and complete['rounding_witness_checks']==2
            assert complete['active_words_compared']==totals['active_words']==80952
            assert complete['output_guard_word_checks']==totals['guard_word_checks']==535072
            assert complete['device_input_buffer_checks']==totals['device_input_buffer_checks']==6536
            for key in ['device_input_word_checks','active_overwritten_words','nonzero_active_words']:assert complete[key]==totals[key]
            assert complete['device_input_word_checks']==1512984
            assert complete['nonfinite_active_words']==nonfinite
            assert complete['all_output_bits_exact'] is True and complete['all_inputs_unchanged'] is True
            assert complete['performance_measurement'] is False and complete['solver_executions']==0 and complete['candidate_accepted'] is False
            ptx={v:(HERE/(v+'.ptx')).read_text(encoding='utf-8') for v in ['baseline','candidate']}
            names={v:re.findall(r'\.visible\s+\.entry\s+(\w+)\(',ptx[v]) for v in ptx}
            assert names['baseline']==names['candidate'] and len(names['baseline'])==9
            unchanged={name:entry(ptx['baseline'],name)==entry(ptx['candidate'],name) for name in names['baseline'] if name!='up_show'}
            assert len(unchanged)==8 and all(unchanged.values())
            for v in ['baseline','candidate']:
                bytes_new(v+'-up_show.ptx',(entry(ptx[v],'up_show')+'\n').encode())
            report={'id':'E029_DIRECT','status':'completed_exact_complete_up_show_comparison','verdict':'PASS_EXACT_COMPLETE_UP_SHOW_COMPARISON',
                'exactness_pass':True,'numerical_validation':'executed','prepared_manifest_sha256':sha(HERE/'prepared-manifest.json'),
                'protocol_sha256':prepared['protocol_sha256'],'corpus_sha256':sha(HERE/'corpus.json'),
                'baseline_cuda_sha256':prepared['source_variants']['baseline']['sha256'],'candidate_cuda_sha256':prepared['source_variants']['candidate']['sha256'],
                'baseline_physical_threads':128,'candidate_physical_threads':128,'logical_scan_threads':128,'comparison_pairs':152,'kernel_launches':304,
                'complete':complete,'records':rows,'other_eight_entry_ptx_exact':unchanged,
                'commands':commands,'telemetry_after':telemetry_after,'binary_sha256':sha(HERE/'probe.exe'),'raw_results_sha256':sha(HERE/'raw-results.jsonl'),
                'input_sha256_after':{name:sha(HERE/name) for name in prepared['artifact_sha256']},
                'solver_executions':0,'performance_measurement':False,'candidate_accepted':False,'deployment_changed':False,
                'limits':['Fixed finite corpus only, all observed output bits required; no NaN-input/payload generalization.',
                    'Reversed ranges exercise target counts as opponent for p0 and own for p1, not a full cross of every count with both orientations.',
                    'Direct float kernel is storage-independent; full F32/compressed/training/evaluation lifecycle and complete-cycle gates remain.',
                    'No timing or performance acceptance. Independent terminal audit is required before E029 activation.']}
            save('report.json',report)
            heartbeat('complete; independent numerical audit pending',0)
            print(json.dumps({'id':'E029_DIRECT','complete':complete,'report':str(HERE/'report.json')},indent=2))
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
