import sys,json,shutil,subprocess,time,importlib.util,re,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
def publish(folder,names):
    for name in names:
        path=folder/name;key=folder.name+'/'+name;dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert dest.read_bytes()==path.read_bytes()
        else:shutil.copyfile(path,dest)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==path.read_bytes()
verify();O=H/'execution';O.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('times',H/'sampler.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
publish(H,['protocol.json','source-review.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);assert not any(x['id']=='D169' for x in status['experiments'])
    status['experiments'].append({'id':'D169','title':'Balanced CPU worker complete-cycle comparison','kind':'diagnostic','status':'running','accepted':False,'correctness':'D168fullrawpass_timingpending','measurement_epoch':'RAM20261028','stage':'86units/config,3warmups,9scoredbalancedfreshprocesses','reason':'SameE080solver/sameharness;actual8/16/32poolobservedafterallwork. Originalfullruntimecompile/qualityclocks,no prebuiltPTX. Unrounded1%/strictfixture/wholeprocessCPUandlifetimegates;noexclusions/extensions/adoptionfromscreen.','evidence':[{'label':'Frozenbalancedconfigurationcomparison','url':'evidence/D169-worker-comparison/protocol.json'},{'label':'Unchangedclock/bodyandpost-suiteobserver','url':'evidence/D169-worker-comparison/source-review.json'}]})
    status.update(updated_at=h.now(),active_experiment='D169',stage='CPUworker complete-cycle screen',activity='8/16/32actualpools/fullrawstatepassed. Noworiginalrealruntimecompilecompletecycleswithbalanced3/configsamplesandterminalCPU/lifetimegates. E08016stayslive,no gainadopted.');h.ar.atomic_json(h.ar.STATUS,status)
def run(row):
    directory=ROOT/'runs'/row['id'];directory.mkdir(exist_ok=False);env=h.env();env['RAYON_NUM_THREADS']=str(row['workers'])
    command=[P['unit_binary'],'--nocapture','--test-threads=1'] if row['kind']=='unit' else [str(H/'probe.exe'),'--exact','d169_worker_cycle','--ignored','--nocapture','--test-threads=1']
    started=h.now();clock=time.monotonic();proc=handle=None;error=cleanup=None;terminal=None
    h.save(directory/'invocation.json',{'at':started,'command':command,'cwd':str(h.REPO),'RAYON_NUM_THREADS':env['RAYON_NUM_THREADS'],'kind':row['kind'],'block':row.get('block'),'binary_sha256':h.sha(command[0]),'original_NVRTC_path':str(h.ar.NVRTC)})
    print('Starting',row['id'],row['workers'],'workers',row['kind'],flush=True)
    try:
        with (directory/'stdout.log').open('xb') as stdout:
            proc=subprocess.Popen(command,cwd=h.REPO,env=env,stdout=stdout,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            handle=s.KERNEL.OpenProcess(0x1000,False,proc.pid)
            if not handle:raise s.c.WinError(s.c.get_last_error())
            announced=0
            while True:
                try:proc.wait(timeout=10);break
                except subprocess.TimeoutExpired:
                    elapsed=time.monotonic()-clock
                    if elapsed>P['native_timeout_seconds']:raise TimeoutError(row['id'])
                    if elapsed-announced>=30:print(row['id'],'running',int(elapsed),'seconds;PID',proc.pid,flush=True);announced=elapsed
            terminal=s.process_times(handle,True)
        assert proc.returncode==0,(row['id'],(directory/'stdout.log').read_text(encoding='utf-8',errors='replace')[-2500:])
    except BaseException as exc:error=repr(exc);cleanup=h.ar.cleanup_child(proc);raise
    finally:
        if handle:assert s.KERNEL.CloseHandle(handle)
        h.save(directory/'exit.json',{'started_at':started,'finished_at':h.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup,'terminal_process_times':terminal,'parent_wall_ms':(time.monotonic()-clock)*1000})
    text=(directory/'stdout.log').read_text(encoding='utf-8');results=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_RESULT ' in x]
    if row['kind']=='unit':
        assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',text)==[('86','0','4','0','0')]
    else:
        pool=[json.loads(x.split('D169_POOL ',1)[1]) for x in text.splitlines() if x.startswith('D169_POOL ')]
        assert pool==[{'requested':row['workers'],'actual':row['workers'],'after_entire_suite_and_destructors':True}]
        assert text.index('D169_POOL ')>text.rindex('AUTORESEARCH_RESULT ') and 'test result: ok. 1 passed; 0 failed; 0 ignored;' in text
        assert 'postflop NVRTC13' not in text and len(results)==3 and all(x['runtime_nvrtc_jit_included'] is True for x in results)
    h.save(directory/'report.json',{'id':row['id'],'at':h.now(),'status':'measured','returncode':proc.returncode,'workers':row['workers'],'kind':row['kind'],'block':row.get('block'),'results':results,'stdout_sha256':h.sha(directory/'stdout.log'),'terminal_process_times':terminal,'protocol_sha256':sys.argv[1],'source_sha256':h.custody(),'performance_qualification_sample':row['kind']=='scored','candidate_accepted':False})
    if row['kind']!='unit':assert h.exact(row['id'])==h.read(ROOT/'epoch/exact-anchor.json')
    print('Completed',row['id'],'exact',flush=True)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    h.child(P['rustc_command'],O,'rustc',1200);verify();assert (h.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes() in(H/'probe.exe').read_bytes();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe'),'one_harness_allconfigs':True,'accepted_kernel_source_embedded':True})
    for row in P['sequence']:
        verify();h.ar.refuse_active(h.ar.live_status());run(row);verify()
    h.save(O/'native-complete.json',{'at':h.now(),'all_owned_children_terminal':True,'sequence':[x['id'] for x in P['sequence']],'units_per_config':86,'warmups_unscored':3,'scored_processes':9,'scored_full_records_exact':27,'scored_checkpoints_exact':207,'all_samples_retained':True,'no_extension_runs':True})
    h.child([sys.executable,str(H/'assess.py')],O,'assessment',1200);verify();D=ROOT/'comparisons/D169-worker-comparison';r=h.read(D/'report.json');h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(D/'report.json'),'all_owned_children_terminal':True,'new_gain_accepted':False})
publish(D,['report.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D169');item.update(status='measured',correctness='all_unique_science_and_units_pass',stage='Balancedworkerconfigurationoutcomesmeasured',reason='27scoredfullrecords/207checkpointsexact,86unitsperconfigpass,actualpoolsverifiedafterallsuite. Advancingconfigs: '+str(r['advancing_worker_counts'])+'. Smallinitialscreenonly;no liveconfigurationchange/adoption.')
    item.setdefault('evidence',[]).append({'label':'Allfixedtimingandprocesscostoutcomes','url':'evidence/D169-worker-comparison/report.json'});status.update(updated_at=h.now(),active_experiment='D169',stage='CPUworker comparison measured',activity='All9scoredobservationsretained;each8/32formgradedvsbalancedshared16controlswith1%/strictfixture/terminalCPU/lifetimegates. No newgainadopted.');h.ar.atomic_json(h.ar.STATUS,status)
verify();print(json.dumps({'status':r['status'],'outcomes':r['configuration_outcomes'],'advancing':r['advancing_worker_counts']}),flush=True)
