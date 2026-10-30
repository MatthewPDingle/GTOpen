"""Close successful branch removal that exceeds the fixed allocation budget."""
import hashlib,json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/D097-chance-selection';H=ROOT/'runs/E059-resource';EX=H/'execution';P=old.read(H/'protocol.json');q=old.read(H/'report.json');branch=old.read(H/'blocker-branch-proof.json')
R=ROOT/'comparisons/E059-resource-root-check';O=ROOT/'runs/E059-closure';assert not R.exists() and not O.exists();R.mkdir();O.mkdir();checks=0
def req(v,label):
    global checks
    assert v,label;checks+=1
for p,h in P['input_sha256'].items():old.pin(p,h);checks+=1
for label in ['rustc','probe']:
    receipt=old.read(EX/(label+'.exit.json'));req(receipt['returncode']==0 and receipt['error'] is None and receipt['cleanup'] is None,'terminal '+label)
raw=(EX/'probe.stdout.log').read_text();markers=[json.loads(line.split('E059_RESOURCE ',1)[1]) for line in raw.splitlines() if line.startswith('E059_RESOURCE ')]
req(markers==q['raw_markers'] and len(markers)==4,'raw complete markers')
b,c=markers[1:3];req(b['registers']==30 and c['registers']==40,'actual compiled register attributes')
req(b['local_bytes_per_thread']==c['local_bytes_per_thread']==b['static_shared_bytes']==c['static_shared_bytes']==0,'local/static storage match')
req(b['dynamic_shared_bytes']==c['dynamic_shared_bytes']==0 and b['max_threads']==c['max_threads']==1024,'dynamic/maxthreads match')
req(b['occupancy_by_threads']==c['occupancy_by_threads']==[[64,24],[128,12],[256,6]],'actual occupancy queries match')
admission=q['details']['up_chance']['allocation_admission'];before=((30*32+255)//256)*256;after=((40*32+255)//256)*256
req(admission['allocated_registers_per_warp']==[before,after]==[1024,1280],'independent allocation rounding')
for row in admission['allocated_registers_per_block']:
    req(row['baseline']==before*(row['threads']//32) and row['candidate']==after*(row['threads']//32),'all block allocation amounts')
req(admission['status']=='reject_resource_prefilter' and q['status']=='rejected_compiled_prerequisite','fixed compiled rejection')
req([k for k,v in q['gates'].items() if not v]==['up_chance:allocated_registers_not_increased'],'only increased allocation fails')
req(branch['status']=='pass_blocker_branch_removal' and all(branch['gates'].values()),'branch mechanism passes separately')
req(len(branch['baseline']['mask_dependent_branches'])==7 and len(branch['candidate']['mask_dependent_branches'])==0,'seven to zero branch witnesses')
req(branch['baseline']['fp_add_sites']==branch['candidate']['fp_add_sites']==7,'static float-add sites unchanged')
def entries(path):
    s=path.read_text();out={}
    for m in re.finditer(r'\.visible \.entry\s+(\w+)\(',s):
        a=s.index('{',m.end());i=a+1;depth=1
        while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
        out[m[1]]=s[m.start():i]
    return out
be=entries(EX/'baseline.ptx');ce=entries(EX/'candidate.ptx');req(set(be)==set(ce)==set(P['expected_entries']),'nine expected entries')
for name in be:req((be[name]==ce[name])==(name!='up_chance'),'only intended entry changes '+name)
req(be['up_chance'].split('{')[0]==ce['up_chance'].split('{')[0],'exact ABI header')
for line in branch['baseline']['mask_dependent_branches']:req(line in be['up_chance'],'baseline branch text retained')
for arm,table in [('baseline',be),('candidate',ce)]:
    for name,body in table.items():req(hashlib.sha256(body.encode()).hexdigest()==q['entry_body_sha256'][arm][name],'actual entry body hash')
address=old.read(D/'report.json');req(address['status']=='pass_source_contract_and_concrete_address_ownership' and len(address['cases'])==12 and address['root_checks']==16823188,'full prior CPU source/address control')
root={'id':'E059-resource-root-check','at':old.now(),'status':'pass_fixed_allocation_rejection','checks':checks,'resource_report_sha256':old.sha(H/'report.json'),'branch_proof_sha256':old.sha(H/'blocker-branch-proof.json'),'address_proof_sha256':old.sha(D/'report.json'),'compiled_nominal_registers':[30,40],'modeled_allocated_registers_per_warp':[1024,1280],'driver_occupancy_queries_equal':True,'blocker_branch_sites':[7,0],'static_fp_add_sites':[7,7],'same_abi_other8entries_exact':True,'source_activated':False,'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'limits':'Root raw attributes, integer allocation rounding and PTX witness/hash replay, not external independent review. Allocation is the calibrated NVIDIA SDK model, not hardware counters. No numerical or runtime performance qualification.'}
old.save(R/'report.json',root)
old.save(O/'decision.json',{'at':old.now(),'id':'E059','decision':'rejected_fixed_allocated_register_budget','reported_registers':[30,40],'modeled_allocated_registers_per_warp':[1024,1280],'blocker_branches':[7,0],'actual_occupancy_unchanged':True,'only_failed_gate':'allocated_registers_not_increased','no_mask_expression_control_placement_factor_variant_rescue':True,'direct_numerical_primary_confirmation_broad_holdout_cumulative_not_run':True,'source_activated':False,'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'accepted_source':'E051','root_report_sha256':old.sha(R/'report.json'),'goal_active':True})
published=[]
def put(path,prefix):
    key='evidence/'+prefix+'/'+path.name;dest=old.ar.DASHBOARD/key;dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert dest.read_bytes()==path.read_bytes(),dest
    else:dest.write_bytes(path.read_bytes())
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==path.read_bytes()
    published.append({'path':str(path),'url':key,'sha256':old.sha(path)})
for folder in [D,ROOT/'runs/E059-source',H,EX,R,O]:
    for path in folder.iterdir():
        if path.is_file() and path.suffix in ['.json','.py','.rs','.cu','.ptx','.log','.patch','.txt']:put(path,'E059-resource-native' if folder==EX else folder.name)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(e for e in s['experiments'] if e['id']=='E059');e.update(status='rejected',correctness='pending',stage='Closed: allocated registers increase despite branch removal',reason='Compiler removes7blocker-dependent PTX branches; all12CPU layouts/address invariants pass. Reported registers30to40 increase modeled allocation1,024to1,280perwarp, failing the fixed D094 resource gate. Occupancy/maxthreads/local/shared unchanged. No direct GPU numerical test, timed solve, variant or adoption.',updated_at=old.now());e['evidence'].extend([{'label':'Actual compiled resources and allocation rejection','url':'evidence/E059-resource/report.json'},{'label':'Seven blocker branches removed','url':'evidence/E059-resource/blocker-branch-proof.json'},{'label':'Root attributes/PTX/allocation replay','url':'evidence/E059-resource-root-check/report.json'},{'label':'No-timing rejection decision','url':'evidence/E059-closure/decision.json'}]);s.update(updated_at=old.now(),state='running',active_experiment=None,stage='Next independent GPU hotspot investigation',activity='E059 removed the intended blocker branches but exceeded the frozen allocated-register budget. No timed solver ran. Accepted E051 and cumulative12.437227% qualifying research gain remain unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D097 and E059 blocker-preserving bit selection' not in raw
note=f'''

### D097 and E059 blocker-preserving bit selection -- allocated-resource rejection

The prior turn completed freshD096two-tone device/API profiling, including rake-aware evaluation topology. D097/E059 tests one distinct chance-kernel control-flow mechanism: retain original64bit hm&cm membership, compute original child-add unconditionally, then select exact previous accumulator bits when blocked and new sum bits otherwise. No add-zero, precision, used addition order, metadata, dispatch, buffer, graph or quality change. Source SHA256479d18af23b0666278bb751df4e0169edd001f88404a0ab0ff369c119c9e5c1e. Scoped retained CU/patch/review search found no matching accumulator bit-selection; closed E039/E046metadata and E048membership candidates remain absent. NVIDIA Math API bit-reinterpretation reference retained; extra ignored arithmetic has no supported observable exception-status output.

Before CUDA work, source review proves total in-range suit-permutation tables, valid/reached orbit children at depth+1, initialized full CFV allocations, stream ordering and disjoint current-level rows. Stream complete D092raw metadata for all12canonical iso-off/on xcompact/full cases:16,823,188root node/permutation/edge/bounds/ownership checks pass. Factored total hand-address bounds cover every newly read cell regardless of blocker state; not every product address is individually enumerated. Unsupported malformed/trapping raw pointer contracts are excluded. No GPU numerical equivalence claim from CPU address data.

Resource protocol067c2281477407763f6e34866c5f4bb14312bf154dff4d5f307de445261a1f32 pins prospectiveD094allocation helper/proof and explicit mask-data PTXtaint analysis before execution. Baseline has7mask-dependent branch sites; candidate0, with7staticFP-add sites in each. Both masks sourced from unchanged parameter9; unknown calls absent, ABI15parameters and other8entry bodies exact. Driver reports registers30 ->40, local0/0, shared0/0,maxthreads1024,occupancy64/128/256=24/12/6unchanged. Calibrated256register-warp granularity yields allocated registers perwarp1,024 ->1,280; at128threads4,096 ->5,120. Thus fixed allocated-resource gate fails even though the intended PTX branch removal succeeds. Resource report {old.sha(H/'report.json')}; root {checks}attribute/rounding/PTX checks {old.sha(R/'report.json')}. These are SDK-model allocations from actual reported attributes, not hardware allocation counters, SASS, numerical or runtime slowdown/speed measurements.

No tracked source activation, CUDA kernel launch, full solver build, direct numerical test, primary3pairs, fresh16, broad/F32/state/save/resume/continuation/material/holdout/cumulative qualification, mask/control/placement/factor variant rescue or adoption. All{len(published)}source/resource/log/PTX artifacts HTTP-byte verified. Root source/replay is not external independent review. Accepted162/main157/live/protectedPTX unchanged; acceptedE051 cumulative12.4372274192%, lastprimaryB185. Goal active.
'''
newline=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+note.encode('utf-8').replace(b'\n',newline))
old.save(O/'checkpoint.json',{'at':old.now(),'previous_goal_turn':'progress: D096 exact fresh two-tone device/API profile with rake-aware source topology repair','current_goal_turn':'progress: D09712layout full address/ownership proof, E059 real blocker-branch removal and fixed allocation rejection','goal_active':True,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'last_primary_baseline':'B185','all_owned_exec_calls_terminal':True,'all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True,'next':'Do not rescue E059 with mask/control/placement/factor variants or old closed hypotheses. A promising next diagnostic is source-matched actual driver CUBIN/SASS inspection to check whether common-action div.rn operations already share denominator reciprocal work before proposing any exact reciprocal-reuse arithmetic. First inspect official CUPTI RESOURCE_MODULE_LOADED callback/module descriptor support in the retained12.9SDK; capture only an owned off-tree module/process, no counters/elevation/injection/live-server attachment. Use official pinned nvdisasm if needed, private onS. Preserve every module and scope source-matched analysis vs exact frozen benchmark bytes. Do not claim precision or speed without exact raw proofs/full unchanged qualification. If inaccessible/unsupported, record concrete evidence and choose a distinct safe mechanism.','live_deployment':'Automatic approval block remains; do not retry or ask duplicate permission.'});put(O/'checkpoint.json','E059-closure')
old.save(O/'publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True});old.custody()
print(json.dumps({'decision':'rejected_allocated_register_budget','root_checks':checks,'blocker_branches':[7,0],'allocated_registers_warp':[1024,1280],'published':len(published),'accepted_source':'E051'}),flush=True)
