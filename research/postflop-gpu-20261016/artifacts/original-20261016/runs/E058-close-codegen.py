"""Close the fixed form after exact PTX shows the intended saving is absent."""
import difflib,hashlib,json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/E058-resource';EX=H/'execution';P=old.read(H/'protocol.json');r=old.read(H/'report.json')
R=ROOT/'comparisons/E058-codegen-root-check';O=ROOT/'runs/E058-closure';assert not R.exists() and not O.exists();R.mkdir();O.mkdir();checks=0
def req(v,label):
    global checks
    assert v,label;checks+=1
for p,h in P['input_sha256'].items():old.pin(p,h);checks+=1
req(r['status']=='pass_resource_feasibility_only' and all(r['gates'].values()),'resource pass is preliminary')
for label in ['rustc','probe']:
    receipt=old.read(EX/(label+'.exit.json'));req(receipt['returncode']==0 and receipt['error'] is None and receipt['cleanup'] is None,'terminal child')
raw=(EX/'probe.stdout.log').read_text();markers=[json.loads(line.split('E058_RESOURCE ',1)[1]) for line in raw.splitlines() if line.startswith('E058_RESOURCE ')]
req(markers==r['raw_markers'] and len(markers)==4,'exact raw marker inventory')
b,c=markers[1:3]
req(b['registers']==c['registers']==40 and b['local_bytes_per_thread']==c['local_bytes_per_thread']==32,'actual reported register/local match')
req(b['occupancy_by_threads']==c['occupancy_by_threads'] and b['static_shared_bytes']==c['static_shared_bytes']==0,'same occupancy/shared')
req(r['details']['down_action']['allocation_admission']['allocated_registers_per_warp']==[1280,1280],'allocation helper applied')
def entries(path):
    text=path.read_text();out={}
    for m in re.finditer(r'\.visible \.entry\s+(\w+)\(',text):
        a=text.index('{',m.end());i=a+1;depth=1
        while depth:
            if text[i]=='{':depth+=1
            elif text[i]=='}':depth-=1
            i+=1
        out[m[1]]=text[m.start():i]
    return out
be=entries(EX/'baseline.ptx');ce=entries(EX/'candidate.ptx');req(set(be)==set(ce)==set(P['expected_entries']),'entry inventory')
for name in be:req((be[name]==ce[name])==(name!='down_action'),'only intended entry differs '+name)
bl=be['down_action'].splitlines();cl=ce['down_action'].splitlines();req(len(bl)==len(cl),'same full entry line count')
diff=[i for i,(x,y) in enumerate(zip(bl,cl)) if x!=y];req(len(diff)==2 and diff[1]==diff[0]+1,'exactly two adjacent changed lines')
i=diff[0];req(bl[i]==cl[i+1] and bl[i+1]==cl[i],'only an adjacent instruction swap')
division=bl[i].strip();comparison=bl[i+1].strip()
req(division.startswith('div.rn.f32') and comparison.startswith('setp.leu.f32'),'unpredicated division and independent comparison')
req('0f40400000' in division and '0f2B8CBCCC' in comparison,'three-action fallback division and threshold')
defs=lambda x:re.findall(r'%[a-z]+\d+',x)
d=defs(division);p=defs(comparison)
req(len(d)==2 and len(p)==2 and not set(d).intersection(p),'data-independent adjacent instructions')
req(sum('div.rn.f32' in x for x in bl)==sum('div.rn.f32' in x for x in cl)==18,'all scalar division sites retained')
delta=''.join(difflib.unified_diff([x+'\n' for x in bl],[x+'\n' for x in cl],fromfile='accepted-down-action.ptx',tofile='conditional-down-action.ptx'))
(R/'only-ptx-change.patch').write_text(delta,encoding='utf-8',newline='\n')
root={'id':'E058-codegen-root-check','at':old.now(),'status':'intended_division_skipping_absent','checks':checks,'resource_report_sha256':old.sha(H/'report.json'),'resource_protocol_sha256':old.sha(H/'protocol.json'),'reported_registers':[40,40],'allocated_registers_per_warp':[1280,1280],'local_bytes':[32,32],'scalar_division_sites':[18,18],'changed_full_entry_lines':diff,'baseline_changed_lines':[bl[k] for k in diff],'candidate_changed_lines':[cl[k] for k in diff],'only_independent_adjacent_compare_divide_swapped':True,'all_other_full_entry_lines_exact':True,'all_other8entries_exact':True,'abi_exact':True,'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'limits':'PTX comparison proves no skipped fallback operation in this fixed compiler form. It is not final-SASS analysis or a runtime slowdown/speed measurement. No numerical equivalence or universal mechanism claim.'}
old.save(R/'report.json',root)
old.save(O/'decision.json',{'at':old.now(),'id':'E058','decision':'closed_intended_compiled_mechanism_absent','resource_gate':'pass_under_prospective_D094_allocation_rule','reason':'Conditional source was transformed back into unconditional fallback division. Exact whole entry differs only by swapping an independent threshold comparison and pr/3 division;18division sites and all remaining instructions/CFG identical. Generic fallback path unchanged.','no_syntax_placement_arity_factor_variant_rescue':True,'direct_numerical_primary_confirmation_broad_holdout_cumulative_not_run':True,'source_activated':False,'kernel_launches':0,'solver_executions':0,'performance_measured':False,'accepted_source':'E051','candidate_accepted':False,'root_report_sha256':old.sha(R/'report.json'),'goal_active':True})
published=[]
def put(path,prefix):
    key='evidence/'+prefix+'/'+path.name;dest=old.ar.DASHBOARD/key;dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert dest.read_bytes()==path.read_bytes()
    else:shutil.copyfile(path,dest)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==path.read_bytes()
    published.append({'path':str(path),'url':key,'sha256':old.sha(path)})
for folder in [ROOT/'runs/D095-uniform-division',ROOT/'runs/E058-source',H,EX,R,O]:
    for path in folder.iterdir():
        if path.is_file() and path.suffix in ['.json','.py','.rs','.cu','.ptx','.log','.txt','.patch']:put(path,'E058-resource-native' if folder==EX else folder.name)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(e for e in s['experiments'] if e['id']=='E058');e.update(status='rejected',correctness='pending',stage='Closed: compiler retained unconditional fallback division',reason='Resource gate passes40/40nominal registers, same1,280allocated registers per warp and32local bytes. Exact PTX differs only by an independent adjacent compare/divide swap; all18division sites remain. Intended saving absent. No kernel, numerical controls, timed solve, variant or adoption.',updated_at=old.now());e['evidence'].extend([{'label':'Actual resource pass','url':'evidence/E058-resource/report.json'},{'label':'Complete codegen differential/root replay','url':'evidence/E058-codegen-root-check/report.json'},{'label':'Only two changed PTX lines','url':'evidence/E058-codegen-root-check/only-ptx-change.patch'},{'label':'No-mechanism closure','url':'evidence/E058-closure/decision.json'}]);s.update(updated_at=old.now(),state='running',active_experiment=None,stage='Next independent GPU hotspot investigation',activity='D094 corrected future resource filtering to actual allocations. E058 passes that gate but its intended division saving is absent from compiled PTX. Accepted E051/cumulative12.437227% unchanged; no new speed claim.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D095 and E058 conditional fallback division' not in raw
note=f'''

### D095 and E058 conditional fallback division -- compiled mechanism absent

After D094's prospective resource clarification, inspect accepted E051 down_action PTX: three-action pr/3 and generic pr/na are formed before their fallback conditions. E058 changes one down_action_impl expression from float uni=pr/(float)na to sum>1e-12f?0.f:pr/(float)na. If the condition holds, uni is never consumed; otherwise the exact original division is used. All stored expressions/order, thresholds, cached regret sum, locked path, addresses, dispatch/host/ABI/graph/precision/quality unchanged. This differs from closed E055discount reads/up_action stores/dispatch/probability caches. Candidate SHA256 b14b7f289e63d88d05e8c0cb1586d7e9d708e1451ecce7a5515b8b58d5a5db80 had no exact match among241retained scoped CU files. Root review is not external independence.

Frozen no-launch resource protocol {old.sha(H/'protocol.json')} pins D094 policy/helper/proof before execution. Actual down_action registers40/40, local32/32, allocated registers perwarp1,280/1,280, shared0/0, maxthreads/64/128/256occupancy,18parameterABI and other8entry bodies match; all resource gates pass. Resource report {old.sha(H/'report.json')}. No source activation or kernel launch.

Exact whole-entry PTX comparison shows equal line counts,18scalar divisions in both, and only two adjacent changed lines: an unpredicated pr/3division and data-independent sum-threshold comparison swap places. All remaining instructions/labels/control flow and generic fallback are byte-identical. Thus the intended conditional division skipping is absent; do not spend numerical/timed solver runs on this fixed form or attempt conditional syntax/placement/arity/factor variants. No final-SASS/runtime or universal claim. Root {checks}checks {old.sha(R/'report.json')}; only-PTX-change.patch retained. No direct numerical, initial3pair, fresh16, broad/F32/state/menu/save/resume/continuation/material/holdout/cumulative work or adoption follows. All{len(published)}public code/result/log/PTX artifacts HTTP-byte verified. Accepted162/main157/live/protectedPTX and E051cumulative12.4372274192%unchanged, last primary baselineB185. Goal active.
'''
newline=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+note.encode('utf-8').replace(b'\n',newline))
old.save(O/'checkpoint.json',{'at':old.now(),'previous_goal_turn':'progress: D093/E057 fixed resource rejection','current_goal_turn':'progress: D094 allocation materiality audit/calibration/7helper tests/prospective policy, then D095/E058 resource pass and compiled-mechanism closure','goal_active':True,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'last_primary_baseline':'B185','all_owned_sessions_terminal':True,'all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True,'historical_outcomes_unchanged':True,'next':'Do not retry E058 syntax/placement/arity/factor variants or old closed hypotheses. Use the committed D094 helper/policy/proof in future resource protocols. A strong next diagnostic is actual CUPTI device+phase profiling of the two-tone registered fixture using retained D087 observer/binary if its fixture selector permits, with fresh fixed BC/CB/BC and full exactness/observer clocks, since D085/D087 are rainbow-only. Inspect current sources/receipts before reusing tools.','live_deployment':'Automatic approval block remains; do not retry or ask duplicate permission.'});put(O/'checkpoint.json','E058-closure')
old.save(O/'publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True});old.custody()
print(json.dumps({'decision':'compiled_mechanism_absent','resource_gate':'pass','root_checks':checks,'scalar_division_sites':[18,18],'changed_lines':len(diff),'published':len(published),'accepted_source':'E051'}),flush=True)
