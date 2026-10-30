import sys,json,math,statistics
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
rows=[];gates={}
reference=(H/'reference-main-compute120.ptx').read_bytes()
for ident in P['native_sequence']:
    receipt=h.read(H/'execution'/(ident+'.exit.json'));assert receipt['returncode']==0
    log=(H/'execution'/(ident+'.stdout.log')).read_text(encoding='utf-8');markers=[json.loads(x.split('D158_COLD ',1)[1]) for x in log.splitlines() if x.startswith('D158_COLD ')];assert len(markers)==1
    row=markers[0];gates[ident+':accepted_PTX_exact']=(H/'execution'/(ident+'.ptx')).read_bytes()==reference
    gates[ident+':valid_actual_clock']=isinstance(row['cold_acquisition_ns'],int) and row['cold_acquisition_ns']>0
    gates[ident+':original_arch_no_GPU_calls']=row['architecture']=='compute_120' and row['explicit_GPU_context_or_kernel_calls']==0 and row['PTX_bytes']==len(reference)
    rows.append({'id':ident,**row,'PTX_sha256':h.sha(H/'execution'/(ident+'.ptx'))})
values=[x['cold_acquisition_ns']/1e6 for x in rows];required=P['minimum_proxy_rule_baseline_ms']*P['required_proxy_pct']/100
proxy=min(values);identity=all(gates.values());admit=identity and proxy>=required
h.custody();D=ROOT/'comparisons/D158-cold-main-acquisition';D.mkdir(exist_ok=False)
report={'id':'D158','at':h.now(),'status':'admit_actual_overlap_diagnostic_only' if admit else 'declined_standalone_cold_acquisition_proxy','protocol_sha256':h.sha(H/'protocol.json'),'gates':gates,'all_emitted_PTX_exact':all(v for k,v in gates.items() if k.endswith('accepted_PTX_exact')),'cold_acquisition_ms':values,'minimum_cold_proxy_ms':proxy,'median_cold_ms':statistics.median(values),'required_proxy_ms':required,'proxy_admitted':admit,'native_records':rows,'solver_or_explicit_GPU_context_kernel_calls':0,'new_optimization_source_or_E093_created':False,'all_children_terminal':True,'source_main_live_PTX_custody_pass':True,'performance_qualification_samples':0,'candidate_accepted':False,'scope':'Three standalone first-process NVRTC acquisitions,not the solver critical path. Minimum raw duration compared prospectively to1% current suite baseline as a conservative effort-selection heuristic,not causal/removable time or rigorous bound. Existing cache remains process-local; concurrent zero scans,context/library scheduling and cache hits may reduce or change any benefit. Identity failure or below-proxy result declines this investigation without source/arch/sample rescue. An admission requires actual overlap evidence before any prebuilt-main candidate.'}
h.save(D/'report.json',report);print(json.dumps({k:report[k] for k in ['status','all_emitted_PTX_exact','cold_acquisition_ms','minimum_cold_proxy_ms','required_proxy_ms','proxy_admitted']}),flush=True)
