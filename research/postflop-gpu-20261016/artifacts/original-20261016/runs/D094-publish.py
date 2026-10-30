"""Publish a prospective materiality clarification without reopening old trials."""
import json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D094-resource-materiality';r=old.read(H/'report.json');tests=old.read(H/'test-report.json')
assert r['status']=='pass_same_allocation_quantum_and_driver_occupancy' and r['sdk_allocation_rows']==20480 and r['retained_driver_matches']==60 and tests['status']=='pass' and tests['tests']==7
helper=old.REPO/'tools/postflop_resource_admission.py';old.pin(helper,tests['helper_sha256'])
old.pin(H/'execution/probe.stdout.log',r['raw_stdout_sha256'])
for label,folder in [('cl','build'),('probe','execution'),('unit','admission-tests')]:
    receipt=old.read(H/folder/(label+'.exit.json'));assert receipt['returncode']==0 and receipt['error'] is None and receipt['cleanup'] is None
policy=old.REPO/'research/postflop-gpu-20261016/resource-admission-policy-20261017.md';assert not policy.exists()
text=f'''# Prospective resource admission: allocated registers

Effective after D094 publication on 17 October 2026. The user's unchanged acceptance rule remains at least **1% complete-cycle improvement with no material tradeoffs**, exactness, fixed sampling and strict fixture nonregression. This clarifies a preliminary compiler/resource filter; it grants no performance or adoption decision.

For future independently scoped candidates, reported registers per thread may increase **only when the verified target-device allocation model proves that allocated registers per warp and block do not increase**. Keep the raw reported counts visible. Require the same fixed driver occupancy observations and no decrease in occupancy or maximum threads. Preserve the existing no-increase checks for local spill bytes and static/dynamic shared memory. Validate the declared ABI/caller changes and intended changed entry bodies; unchanged entries must remain exact. All actual host/global-device payload, capacity, behavior, compatibility, F32/save/resume/continuation and complete-cycle performance gates still apply.

If allocation granularity is not verified for the actual target device/compiler/runtime context, a nominal register increase cannot pass this exception. The checked helper currently supports compute12.0 with32thread warps and256register per-warp allocation units, pinned to D094's NVIDIA CUDA12.9.79 header and calibrated driver evidence. Other hardware requires its own verified evidence. Instrumentation, launch preferences and spill/shared/global costs cannot be waived by an allocation calculation.

The [NVIDIA occupancy guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#calculating-occupancy) distinguishes reported registers from rounded allocation. D094 compiled the official standalone CUDA occupancy header with live RTX5090 properties. Its20,480 rows cover10resource geometries, nominal counts38/40 and every1..1024thread count. All pairs have identical modeled allocated registers/shared memory, occupancy, feasibility and limiting factors. A separate integer replay passes30,780checks; all60 retained actual driver occupancy queries at64/128/256threads match. At128threads both counts allocate5,120registers per block in this model. Allocation counts are NVIDIA SDK model outputs, not hardware allocation-counter measurements or proof of runtime speed.

Seven helper tests cover all10retained geometries, quantum boundaries32->33and40->41, allocation reduction, spill/shared/occupancy/limit regressions, missing proof, malformed attributes and incomplete/misaligned driver observations. Crossing to the next allocation quantum is rejected even when sampled occupancy remains unchanged. The helper admits numerical controls only; it never accepts a candidate.

Historical protocols, samples and decisions remain frozen. E057 retains its rejection under its original no-nominal-register-increase rule; this audit does not reopen E057, E050 or any other closed hypothesis, nor permit variants or additional samples. Future protocols must freeze this policy and the helper/proof hashes before candidate execution. Performance thresholds, exactness, stopping/storage/workload settings, fixture guards, fresh16confirmation and broader/holdout/fresh-original qualification are unchanged.

- [D094 frozen audit protocol](evidence/D094-resource-materiality/protocol.json)
- [Allocation and driver-calibration report](evidence/D094-resource-materiality/report.json)
- [Helper tests](evidence/D094-resource-materiality/test-report.json)
- [Prospective admission helper](evidence/D094-resource-materiality/postflop_resource_admission.py)
- [Unchanged primary qualification policy](qualification-policy-20261017.md)

SDK header SHA256: {r['sdk_header_sha256']}. Helper SHA256: {old.sha(helper)}. Audit report SHA256: {old.sha(H/'report.json')}. Root review/replay is not an external independent audit. No solver source or live executable changed; no new performance gain is claimed.
'''
policy.write_text(text,encoding='utf-8',newline='\r\n')
published=[]
def put(path,prefix=None):
    key=('evidence/'+prefix+'/'+path.name) if prefix else path.name
    target=old.ar.DASHBOARD/key;target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert target.read_bytes()==path.read_bytes(),target
    else:shutil.copyfile(path,target)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==path.read_bytes()
    published.append({'path':str(path),'url':key,'sha256':old.sha(path)})
for folder,prefix in [(H,H.name),(H/'build',H.name+'-build'),(H/'execution',H.name+'-native'),(H/'admission-tests',H.name+'-tests')]:
    for path in folder.iterdir():
        if path.is_file() and path.suffix in ['.json','.cpp','.py','.log']:put(path,prefix)
put(helper,H.name);put(policy)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);assert s['research_policy']['minimum_aggregate_gain_pct']==1
    assert next(e for e in s['experiments'] if e['id']=='E057')['status']=='rejected'
    e=next(e for e in s['experiments'] if e['id']=='D094');e.update(status='measured',correctness='pass',stage='Allocation-model and driver-calibration audit passed',reason='All20,480 SDK model rows and30,780 root checks pass;60 retained driver occupancy observations match.38/40nominal registers allocate the same5,120registers per128thread block. Seven prospective helper tests pass. Future filtering uses allocated resource units; historical rejections and1%/accuracy/material-cost gates remain unchanged. No kernel or solve executed and no speed claim.',updated_at=old.now());e['evidence'].extend([{'label':'Complete SDK allocation audit and driver calibration','url':'evidence/D094-resource-materiality/report.json'},{'label':'Seven admission-helper tests','url':'evidence/D094-resource-materiality/test-report.json'},{'label':'Prospective resource admission policy','url':policy.name}])
    s['research_policy']['resource_admission']={'status':'Prospective D094 allocation-based clarification; historical decisions frozen','policy_url':policy.name,'policy_sha256':old.sha(policy),'helper_sha256':old.sha(helper),'proof_url':'evidence/D094-resource-materiality/report.json','historical_reopening':False}
    s['evidence'].append({'label':'Prospective resource filter: actual allocation units','url':policy.name,'detail':'D094 validated compute12.0 register rounding and driver occupancy. No historical reopening or weaker accuracy/performance/material-cost gate.'})
    s.update(updated_at=old.now(),state='running',active_experiment=None,stage='Next independent GPU hotspot investigation',activity='D094 confirmed nominal register increases can fit identical allocation units. Future independent candidates use the allocation-based prefilter; prior rejections and accepted E051/cumulative12.437227% remain unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D094 resource materiality audit' not in raw
entry=f'''

### D094 resource materiality audit -- prospective filter clarified

The prior turn completed D093/E057resource rejection. D094 tests whether nominal38->40registers necessarily violates the user's no-material-tradeoff requirement. NVIDIA official CUDA12.9.79 cuda_occupancy.h explicitly handles compute12.x with256register per-warp rounding, header SHA256 {r['sdk_header_sha256']}; SDK package provenance is the frozen D085official download manifest. New off-tree CPU C++ probe queries live GPUproperties through system nvcuda and uses the unmodified occupancy header. No CUDA context creation, kernel launch, solver execution, candidate source, changed launch preferences, privilege/global environment modification or performance observation.

Frozen protocol {old.sha(H/'protocol.json')} produced all20,480 model rows:10geometries x38/40nominal counts x1..1024threads. Root formula/pair replay passes30,780checks; all60 retained actual driver occupancy queries match. All paired model allocations/shared/limit/feasibility fields match. Rounded register allocation perblock:64threads2,560;128threads5,120;256threads10,240in both arms. These are official SDK model outputs calibrated to driver occupancy, not hardware allocation counters or runtime/accuracy evidence. Seven prospective helper tests pass: all10real geometries, quantum boundaries32->33/40->41, reduction, other resource costs, occupancy/limit regressions and malformed/missing proof/observations. Helper SHA256 {old.sha(helper)}. No production tests required because solver source unchanged; the research decision logic received focused tests.

Added resource-admission-policy-20261017.md (SHA256 {old.sha(policy)}) and tools/postflop_resource_admission.py for future independently scoped protocols. Allow a nominal count increase only inside a verified nonincreasing allocation quantum, with existing actual occupancy/maxthread/local/shared and all numerical/performance/material/capacity/compatibility gates retained. Unknown target-device granularity has no exception. Primary user1%threshold, frozen quality/settings, strict fixture guard, separately frozen16pairs and all broad/F32/save/resume/continuation/holdout/fresh-original gates unchanged. E057/E050/allprior outcomes and frozen scripts remain unchanged; no reopening, variant or retiming is authorized by this audit. All{len(published)}public source/result/log/policy artifacts HTTP-byte verified. Root is not external independent review. Accepted162/main157/live/protectedPTX and E051cumulative12.4372274192%unchanged; last primary baselineB185. Goal active.
'''
newline=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+entry.encode('utf-8').replace(b'\n',newline))
old.save(H/'checkpoint.json',{'at':old.now(),'previous_goal_turn':'progress: D093/E057 bounded prefix mapping and fixed resource rejection','current_goal_turn':'progress: D094 native SDK allocation audit,60driver calibration,7focused helper tests and prospective materiality clarification','goal_active':True,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'last_primary_baseline':'B185','owned_native_session':98771,'all_owned_sessions_terminal':True,'all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True,'historical_decisions_unchanged':True,'next':'Use allocation-based resource admission only for new independent candidate protocols. Do not revive closed hypotheses. A concrete next measurement is extending D085/D087 actual CUPTI device/phase observation to the two-tone primary fixture, whose existing eager profile is not graph-time evidence. Keep the evaluator/accuracy/sampling/material gates fixed.','live_deployment':'Prior automatic approval block remains; do not retry or ask duplicate permission.'});put(H/'checkpoint.json',H.name)
old.save(H/'publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'no_new_speed_gain':True})
old.custody();print(json.dumps({'status':'published_prospective_allocation_filter','published':len(published),'helper_tests':7,'historical_outcomes_unchanged':True,'accepted_source':'E051'}),flush=True)
