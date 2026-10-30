import sys,json,statistics,shutil,subprocess,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not (ROOT/'gpu-run.lock').exists() and not (ROOT/'epoch-sequence.lock').exists()
N=ROOT/'runs/D159-outcome-checkpoint';N.mkdir(exist_ok=False)
reports={};pins={};terminal=[]
for name in ['D157-actual-resources','D158-cold-main-acquisition','D159-vectorization-resource','D159R2-vectorization-resource']:
    folder=ROOT/'runs'/name;p=h.read(folder/'protocol.json')
    for path,digest in p['input_sha256'].items():h.pin(path,digest);pins[path]=digest
    pins[str(folder/'protocol.json')]=h.sha(folder/'protocol.json')
    for f in (folder/'execution').glob('*.exit.json'):
        receipt=h.read(f);expected=101 if name=='D159-vectorization-resource' and f.name=='probe.exit.json' else 0
        assert receipt['returncode']==expected,(f,receipt)
        terminal.append({'path':str(f),'sha256':h.sha(f),'exit':expected})
    if name!='D159-vectorization-resource':reports[name]=h.read(ROOT/'comparisons'/name/'report.json')
P=h.read(ROOT/'runs/D157-actual-resources/protocol.json');R=reports['D157-actual-resources'];raw={};anchor=h.read(ROOT/'epoch/exact-anchor.json');exact=checks=0
excluded={'build_ms','fingerprint_ms_excluded','full_cycle_ms','init_ms','readback_ms','solve_ms'}
for item in P['sequence']:
    ident=item['id'];out=ROOT/'runs/D157-actual-resources/execution';r=h.read(out/(ident+'.resource.json'));raw[ident]=r
    times=r['terminal_process_times'];assert times['lifetime_ms']==(times['exit_FILETIME']-times['creation_FILETIME'])/10000
    assert times['CPU_ms']==(times['kernel_100ns']+times['user_100ns'])/10000
    assert r['parent_wall_ms']>=times['lifetime_ms'] and r['parent_wall_ms']<times['lifetime_ms']+2000
    assert r['sample_count']==len(r['samples'])
    for key,field in [('reported_working_set_high_water_bytes','PeakWorkingSetSize'),('reported_commit_high_water_bytes','PeakPagefileUsage')]:
        assert r[key]==max(x['process_memory'][field] for x in r['samples'] if x['process_memory'])
    assert r['sampled_global_GPU_used_max_bytes']==max(x['NVML_global']['used'] for x in r['samples'])
    text=(out/(ident+'.stdout.log')).read_text(encoding='utf-8')
    results=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_RESULT ' in x]
    stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_STAGE ' in x]
    conv=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for x in stages if x.get('stage')=='convergence_check']
    assert [[{k:v for k,v in x.items() if k not in excluded} for x in results],conv]==anchor
    exact+=len(results);checks+=len(conv)
b=[raw[x['id']]['terminal_process_times']['lifetime_ms'] for x in P['sequence'] if x['arm']=='baseline'];c=[raw[x['id']]['terminal_process_times']['lifetime_ms'] for x in P['sequence'] if x['arm']=='candidate']
regression=(statistics.median(c)/statistics.median(b)-1)*100
assert regression==R['resource_summary']['process_lifetime_ms']['median_regression_pct']
assert R['failed_gates']==['process_lifetime_ms:median_within_fixed_allowance'] and regression>1
D158=reports['D158-cold-main-acquisition'];p=h.read(ROOT/'runs/D158-cold-main-acquisition/protocol.json');cold=[]
for ident in p['native_sequence']:
    out=ROOT/'runs/D158-cold-main-acquisition/execution';lines=(out/(ident+'.stdout.log')).read_text(encoding='utf-8').splitlines()
    rows=[json.loads(x.split('D158_COLD ',1)[1]) for x in lines if x.startswith('D158_COLD ')]
    assert len(rows)==1 and rows[0]['explicit_GPU_context_or_kernel_calls']==0
    cold.append(rows[0]['cold_acquisition_ns']/1e6)
    assert (out/(ident+'.ptx')).read_bytes()==(ROOT/'runs/D158-cold-main-acquisition/reference-main-compute120.ptx').read_bytes()
assert cold==D158['cold_acquisition_ms'] and min(cold)<D158['required_proxy_ms'] and not D158['proxy_admitted']
first=ROOT/'runs/D159-vectorization-resource/execution';second=ROOT/'runs/D159R2-vectorization-resource/execution';D159=reports['D159R2-vectorization-resource']
assert not (first/'candidate-compute_120.ptx').exists()
assert (first/'baseline-compute_120.ptx').read_bytes()==(second/'baseline-compute_120.ptx').read_bytes()
for arch in ['compute_120','compute_75']:
    assert (second/('baseline-'+arch+'.ptx')).read_bytes()==(second/('candidate-'+arch+'.ptx')).read_bytes()
rows=[json.loads(x.split('D159_RESOURCE ',1)[1]) for x in (second/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if x.startswith('D159_RESOURCE ')]
resource=[x for x in rows if 'kernel' in x];assert len(resource)==18 and all(x['kernel_launches']==0 for x in resource)
assert D159['failed_gates']==['intended_changed_body','intended_vector_instruction_increase'] and not D159['changed_compute120_entries']
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';old=ledger.read_bytes();snapshot=N/'history-at-D159-freeze.txt';snapshot.write_bytes(old)
assert h.sha(snapshot)==pins[str(ledger)]
entry=f'''

### D157 closes E092; D158 and D159 compiler investigations

D157 fixed actual-resource prerequisite protocol {h.sha(ROOT/'runs/D157-actual-resources/protocol.json')} completed original B1/C1/C2/B2 workload history with all12 complete scientific records and92 convergence checkpoints exact. Original Win32 terminal FILETIME arithmetic replayed independently: median process lifetime12,282.05965ms baseline versus16,788.40595ms candidate, +{regression}% against prospectively fixed<=1% allowance. CPU median -2.4289642529789157%, reported WS/commit peaks slightly lower, sampled global GPU median +31.625MiB within64MiB limit. Explicit learning/CFV/pinned payload and default stack/heap unchanged; actual two host metadata capacities total25,165,824bytes on rainbow and wrapper+32bytes. Late transient/host sampling/global WDDM limitations remain. Only process-lifetime gate failed. E092 is REJECTED and CLOSED without source,capacity,threshold,shader,fixture or resampling rescue. No fresh performance qualification or source adoption. D155 original partial activation failure remains failed.

D158 standalone accepted-main process-local PTX cold acquisition protocol {h.sha(ROOT/'runs/D158-cold-main-acquisition/protocol.json')}: three fresh CPU-only NVRTC processes measured{cold}ms, all emitted PTX byte-exact. Minimum77.8061ms below prospective104.564109ms effort-selection proxy. Declined standalone cold-main acquisition/prebuilt-main direction; these are not solver critical-path measurements, rigorous removable bounds or performance samples. No E093, source or context/kernel created. Existing cache unchanged.

D159 one --extra-device-vectorization option on exact accepted CUDA source. Original frozen probe incorrectly named obsolete up_action_opponent in hardcoded list despite protocol's correct copy_span. Rust compiler0/native101 after baseline compile/load and7resource rows, before any candidate compilation or application kernel. Original files/status stay INVALID. D159R2 is a mechanical pre-candidate symbol repair only, reusing original baseline120PTX exactly, requerying all7prior rows and compiling only3remaining originally declared variants. No source/option/architecture/gate tuning. Across R1/R2 exactly4NVRTC program variants, plus disclosed repaired Rust compile and read-only baseline module resource queries.

D159R2 protocol {h.sha(ROOT/'runs/D159R2-vectorization-resource/protocol.json')}: all9 compute120 entries and whole PTX byte-identical; emitted vector sites0->0. Fallback compute75 wholePTX exact.18resource rows pass original ABI/default-limit/local/maxthread/feasibility checks. Intended changed-body and vector-instruction-increase gates fail. Decline no-effect compiler mechanism without application kernels,solver runs,performance samples or optimizer implementation. No flag combination or repeated candidate rescue.

Root retained replay checks all protocol inputs before this append, exact scientific anchors, original process lifetime/CPU/sample maxima and raw cold/PTX identities. The frozen ledger input is preserved byte-for-byte in the X checkpoint history snapshot; append-only history transition records old/new digests without modifying original protocols. Primary Windows/NVIDIA API docs explain instrument meanings, not user speed results.

Current-RAM E080 baseline10.4564109s unchanged; no new accepted gain. Prior-RAM14.741418835370924% remains historical. All owned children terminal, locks absent, accepted162/main/live/protectedPTX custody passes. No push, application activation or server replacement. All new artifacts on X; no T access or historical archive mutation. Goal active; next source-bound scout considers numeric arena allocation lifecycle only after screening old zero-constructor and first-touch evidence.
'''
nl=b'\r\n' if b'\r\n' in old else b'\n';ledger.write_bytes(old+entry.encode().replace(b'\n',nl))
subprocess.run(['git','-c','gc.auto=0','commit','--only','-m','research: close packet resource regression and no-effect compiler scouts','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
h.save(N/'history-transition.json',{'at':h.now(),'original_path':str(ledger),'original_sha256':h.sha(snapshot),'immutable_snapshot':str(snapshot),'appended_current_sha256':h.sha(ledger),'original_protocols_unchanged':True,'purpose':'Append-only ledger publication after verifying all frozen protocol inputs. Resolve original ledger pins through exact retained snapshot.'})
h.save(N/'report.json',{'at':h.now(),'status':'pass_retained_outcome_replay','exact_D157_full_records':exact,'exact_D157_checkpoints':checks,'D157_baseline_lifetime_median_ms':statistics.median(b),'D157_candidate_lifetime_median_ms':statistics.median(c),'D157_lifetime_regression_pct':regression,'E092_rejected_and_closed':True,'D158_cold_ms':cold,'D158_proxy_declined':True,'D159_original_invalid_preserved':True,'D159R2_whole_PTX_both_architectures_identical':True,'D159R2_resource_rows':len(resource),'D159R2_declined_no_codegen_mechanism':True,'all_child_exit_receipts':terminal,'protocol_inputs_verified_before_history_append':True,'history_transition_sha256':h.sha(N/'history-transition.json'),'research_git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip(),'new_speed_gain_accepted':False,'current_baseline_ms':10456.4109})
pub=[]
for folder in [ROOT/'comparisons'/name for name in reports]+[N]:
    for path in folder.iterdir():
        if path.suffix!='.json':continue
        key=folder.name+'/'+path.name;dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(exist_ok=True,parents=True)
        if dest.exists():assert dest.read_bytes()==path.read_bytes()
        else:shutil.copyfile(path,dest)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==path.read_bytes()
        pub.append(key)
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D159R2')
    item.update(status='measured',correctness='no_codegen_change',stage='Declined: compiler option emits identical GPU code',reason='All9 main entries and wholePTX byte-identical on compute120;fallback75 exact.18 resource rows pass. Mechanism gates fail,so no solver or speed samples. Original D159 symbol setup failure remains invalid.')
    item.setdefault('evidence',[]).extend([{'label':'Compiler mechanism outcome','url':'evidence/D159R2-vectorization-resource/report.json'},{'label':'Raw outcome replay and preserved failures','url':'evidence/D159-outcome-checkpoint/report.json'}])
    status.update(updated_at=h.now(),active_experiment=None,stage='Source scout: CPU numeric arena allocation lifecycle',activity='E092 exact but rejected for36.7% longer whole-process lifetime. Cold-main proxy declined; compiler-vectorization flag emits identical code. E080 current-RAM10.4564s unchanged. Checking distinct allocation backend and complete touch/free cost before implementation.')
    h.ar.atomic_json(h.ar.STATUS,status)
h.custody();assert not (ROOT/'gpu-run.lock').exists()
print(json.dumps({'status':'outcomes_published','HTTP_artifacts':len(pub),'records':exact,'checkpoints':checks,'E092_lifetime_regression_pct':regression,'D159R2':'no_effect_declined','research_git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip()}),flush=True)
