import json, shutil, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D190-inline-tree-control'
assert len(sys.argv)==2;h.pin(H/'protocol.json',sys.argv[1]);P=h.read(H/'protocol.json')
for p,digest in P['input_sha256'].items():h.pin(p,digest)
OUT=H/'execution'
def child(command,label,timeout):
    proc=None;error=None;cleanup=None;start=h.now();clock=time.monotonic();announced=0
    h.save(OUT/(label+'.invocation.json'),{'at':start,'command':command,'cwd':str(OUT)})
    print('Starting',label,flush=True)
    try:
        with (OUT/(label+'.stdout.log')).open('xb') as stdout,(OUT/(label+'.stderr.log')).open('xb') as stderr:
            proc=subprocess.Popen(command,cwd=OUT,env=h.env(),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            while True:
                try:proc.wait(timeout=10);break
                except subprocess.TimeoutExpired:
                    elapsed=time.monotonic()-clock
                    if elapsed>timeout:raise TimeoutError(label)
                    if elapsed-announced>=30:print(label,'running',int(elapsed),'seconds; PID',proc.pid,flush=True);announced=elapsed
    except BaseException as e:error=repr(e);cleanup=h.ar.cleanup_child(proc);raise
    finally:h.save(OUT/(label+'.exit.json'),{'started_at':start,'finished_at':h.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup})
    assert proc.returncode==0,(label,(OUT/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-4000:])

with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.custody();h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['storage_admission_GiB']*1024**3
    OUT.mkdir(exist_ok=False)
    child(P['smallvec_command'],'smallvec-rustc',180)
    child(P['rustc_command'],'rustc',180)
    h.save(OUT/'build-complete.json',{'at':h.now(),'probe_sha256':h.sha(H/'probe.exe'),'smallvec_rlib_sha256':h.sha(H/'libsmallvec.rlib'),'native_executions':0})
    canonical=[];controls=[];sizes=[]
    for label,args in P['sequence']:
        child([str(H/'probe.exe'),*args],label,600);h.custody()
        markers=[json.loads(x.split('D190_TREE ',1)[1]) for x in (OUT/(label+'.stdout.log')).read_text(encoding='utf-8').splitlines() if x.startswith('D190_TREE ')]
        assert markers[-1]['stage']=='complete' and markers[-1]['all_exact']
        canonical.extend(m for m in markers if m['stage']=='canonical')
        controls.extend(m['result'] for m in markers if m['stage']=='control')
        sizes.extend(m for m in markers if m['stage']=='temporary_container_sizes')
    assert len(canonical)==3 and [x['id'] for x in canonical]==[0,1,2]
    assert len(controls)==15+P['extra_control_cases'] and len(sizes)==4 and all(x==sizes[0] for x in sizes)
    raw_records=[]
    for row in canonical+controls:
        if 'raw_file' not in row:continue
        p=OUT/row['raw_file'];assert p.is_file()
        raw_records.append({'path':str(p),'sha256':h.sha(p),'bytes':p.stat().st_size,'label':row.get('label','canonical-'+str(row.get('id'))),'checks':row['checks'],'metadata':row['metadata'],'hands':row['hands']})
    saving=sum(x['saving_ms'] for x in canonical)
    guards=[{'id':x['id'],'positive_median_slowdown':x['positive_median_slowdown'],'slower_pairs':x['slower_pairs'],'failed':x['positive_median_slowdown'] and x['slower_pairs']>=5} for x in canonical]
    passed=saving>=P['minimum_component_saving_ms'] and not any(x['failed'] for x in guards)
    h.save(H/'report.json',{'id':'D190-inline-tree-control','at':h.now(),'status':'advance_to_integrated_qualification' if passed else 'rejected_component_admission','protocol_sha256':sys.argv[1],'canonical':canonical,'controls':controls,'raw_files':raw_records,'sum_component_median_saving_ms':saving,'required_component_saving_ms':P['minimum_component_saving_ms'],'component_guards':guards,'temporary_container_sizes':sizes[0],'all_tree_fields_capacities_errors_exact':True,'measured_pairs_per_canonical':9,'warmup_pairs_per_canonical':2,'historical_timing_samples_scored':0,'exclusions':[],'extension_samples':0,'binary_sha256':h.sha(H/'probe.exe'),'all_owned_children_terminal':True,'source_activated':False,'gpu_executions':0,'full_cycle_performance_measured':False,'candidate_accepted':False,'limits':'CPU tree wrapper screen only. Full raw final/control trees retained; no full solve/CPU/RAM/material/quality/capacity qualification. Component-reference effort proxy is separate from samples. All original gates apply before adoption.'})
    h.custody()
# Reader owns its own exclusive lease, with every compiler/native child terminal.
child([sys.executable,str(H/'audit.py')],'audit',900)
h.custody()
h.save(OUT/'complete.json',{'at':h.now(),'all_owned_compilers_native_readers_terminal':True,'raw_reader_report_sha256':h.sha(ROOT/'comparisons/D190-inline-tree-root-check/report.json'),'new_GPU_processes':0,'accepted_source_main_live_PTX_unchanged':True})
print(json.dumps({'status':h.read(H/'report.json')['status'],'saving_ms':saving,'required_ms':P['minimum_component_saving_ms'],'raw_reader':'pass','owned_children':'all terminal'}),flush=True)
