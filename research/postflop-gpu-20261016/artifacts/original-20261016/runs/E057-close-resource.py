"""Root replay and closure of a failed fixed no-launch resource gate."""
import hashlib,json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/E057-resource';EX=H/'execution';P=old.read(H/'protocol.json');r=old.read(H/'report.json');D=ROOT/'runs/D093-prefix-layout'
R=ROOT/'comparisons/E057-resource-root-check';O=ROOT/'runs/E057-closure';assert not R.exists() and not O.exists();R.mkdir();O.mkdir();checks=0
def req(v,label):
    global checks
    assert v,label;checks+=1
req(r['protocol_sha256']==old.sha(H/'protocol.json'),'frozen protocol')
for p,h in P['input_sha256'].items():old.pin(p,h);checks+=1
for label in ['rustc','probe']:
    exit=old.read(EX/(label+'.exit.json'));req(exit['returncode']==0 and exit['error'] is None and exit['cleanup'] is None,'terminal '+label)
raw=(EX/'probe.stdout.log').read_text();markers=[json.loads(line.split('E057_RESOURCE ',1)[1]) for line in raw.splitlines() if line.startswith('E057_RESOURCE ')]
req(markers==r['raw_markers'] and len(markers)==22,'raw complete marker inventory')
rows={(x['variant'],x['shape']):x for x in markers[1:-1]};req(len(rows)==20,'both arms ten geometries')
expected_failed=[]
for shape in P['shapes']:
    b=rows['baseline',shape];c=rows['candidate',shape]
    req(b['kernel']==c['kernel']=='up_show' and b['kernel_launches']==c['kernel_launches']==0,'resource-only scope')
    req(b['registers']==38 and c['registers']==40,'actual register regression')
    req(c['local_bytes_per_thread']==b['local_bytes_per_thread'] and c['static_shared_bytes']==b['static_shared_bytes'] and c['dynamic_shared_bytes']==b['dynamic_shared_bytes'],'other exact storage attributes')
    req(c['max_threads']==b['max_threads'] and c['occupancy_by_threads']==b['occupancy_by_threads'],'same maxthreads and query occupancy')
    req(b['fits_default_limits'] and c['fits_default_limits'],'device limits')
    expected_failed.append(shape+':registers_not_increased')
req([k for k,v in r['gates'].items() if not v]==expected_failed and r['status']=='rejected_resource_gate','unchanged fixed rejection')
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
for arch in ['compute_120','compute_75']:
    b=entries(EX/f'baseline-{arch}.ptx');c=entries(EX/f'candidate-{arch}.ptx')
    req(set(b)==set(c)==set(P['expected_entries']),'entry inventory '+arch)
    for name in b:req((b[name]==c[name])==(name!='up_show'),'only show body changes '+name)
    req(re.findall(r'\.param[^\n]+',b['up_show'].split('{')[0])==re.findall(r'\.param[^\n]+',c['up_show'].split('{')[0]),'ABI exact '+arch)
req(old.read(EX/'complete.json')['all_children_terminal'] and old.read(EX/'complete.json')['report_sha256']==old.sha(H/'report.json'),'final child receipt')
model=old.read(D/'report-r2.json');req(model['status']=='admit_no_launch_resource_probe' and all(model['gates'].values()),'prior CPU-only model does not override resource failure')
root={'id':'E057-resource-root-check','at':old.now(),'status':'pass_rejected_resource_gate','checks':checks,'resource_report_sha256':old.sha(H/'report.json'),'resource_protocol_sha256':old.sha(H/'protocol.json'),'registers':[38,40],'occupancy_queries_unchanged':True,'local_shared_dynamic_abi_other8entries_unchanged':True,'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'source_main_live_ptx_unchanged':True,'limits':'Root raw-marker/PTX arithmetic replay, not an external independent review. Driver attributes are not numerical or performance qualification; candidate failed its predeclared register gate.'}
old.save(R/'report.json',root)
old.save(O/'decision.json',{'at':old.now(),'id':'E057','decision':'rejected_fixed_resource_gate','registers':[38,40],'failed_gate':'No register count increase','all_other_resource_gates_passed':True,'kernel_launches':0,'solver_executions':0,'direct_numerical_primary_confirmation_broad_holdout_cumulative_not_run':True,'no_guard_map_width_block_schedule_variant_rescue':True,'accepted_source':'E051','source_activated':False,'candidate_accepted':False,'resource_report_sha256':old.sha(H/'report.json'),'root_report_sha256':old.sha(R/'report.json'),'goal_active':True})
published=[]
def put(path,prefix):
    key='evidence/'+prefix+'/'+path.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():req(dst.read_bytes()==path.read_bytes(),'existing immutable public bytes')
    else:shutil.copyfile(path,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:req(response.read()==path.read_bytes(),'HTTP byte replay')
    published.append({'path':str(path),'url':key,'sha256':old.sha(path)})
for folder in [D,ROOT/'runs/E057-source',H,EX,R,O]:
    for path in folder.iterdir():
        if path.is_file() and path.suffix in ['.json','.py','.rs','.cu','.patch','.txt','.log','.ptx']:put(path,folder.parent.name+'-'+folder.name if folder==EX else folder.name)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E057');e.update(status='rejected',correctness='pending',stage='Closed: register count38 to40 fails fixed prerequisite',reason='Fixed no-launch resource gate failed: up_show registers38 to40. Local/shared/dynamic bytes, maxthreads, same-shape occupancy queries, ABI and other8entry bodies match. No kernels, numerical controls, timed solves, variants or adoption. Accepted E051 retained.',updated_at=old.now());e['evidence'].extend([{'label':'Actual compiled-resource report','url':'evidence/E057-resource/report.json'},{'label':'Root raw-resource and PTX replay','url':'evidence/E057-resource-root-check/report.json'},{'label':'Resource rejection decision','url':'evidence/E057-closure/decision.json'}]);st.update(updated_at=old.now(),state='running',active_experiment=None,stage='Next independent GPU hotspot investigation',activity='E057 prefix-index permutation failed its fixed register prerequisite38 to40; no timed solver ran. Accepted E051 and cumulative12.437227% qualifying gain remain unchanged.');old.ar.atomic_json(old.ar.STATUS,st)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D093 and E057 prefix-buffer address permutation' not in raw
note=f'''

### D093 and E057 prefix-buffer address permutation -- resource rejection

The prior goal turn completed D092 CPU controls and E056 fixed initial screen/rejection; current turn makes progress with a distinct shared-prefix physical index mechanism. Scoped postflop retained CU/patch/review and ledger searches found no prior prefix swizzle; E008/E022/E031/E050/E052/E053 remain absent/closed. Accepted up_show PTX has scalar shared f32 prefix instructions, but PTX is not a hardware bank counter or final SASS. NVIDIA32bank mapping reference is retained in D093 protocol.

One fixed CUDA-only candidate b9c1b260895debf954def29b28804d3cd1cc0b431a668c698d72dda55693cec3 maps full32word tiles by k XOR ((k>>5)&31), final partial tile identity. Enable only for power-of-two chunk lengths>1; no outcome-driven guard/key/block sweep. All five prefix accesses use that bounded involution; all original float expressions/order, scan recurrence, reach/card buffers, barriers, allocation, ABI/host/graph/quality remain unchanged. Off-tree CPU proof passes2,654 m/flag cases,1,759,602 index words and339,712 block geometries. Model consumes complete D092 canonical metadata cases3/7/11. Initial per-block total-read count was corrected additively to four warp broadcasts; original report and repair script preserved, source/gates/differences unchanged. Corrected modeled prefix request units: rainbow60,859,182 ->52,082,316; two-tone36,759,483 ->31,717,197; river1,353 ->1,133. This excludes other shared traffic, issue/SASS, arithmetic/barriers, actual solver iteration weighting and time; no speed percentage or no-tradeoff claim.

Frozen resource protocol {old.sha(H/'protocol.json')} compiled/loaded both arms oncompute120 and compile-onlycompute75. Actual up_show registers38 ->40 fails the prospective no-register-increase prerequisite on all10geometries. Local/static/dynamic bytes, maxthreads,64/128/256 occupancy queries,27parameter ABI and other8entry bodies match. Rejected without source activation, any kernel launch, direct GPU numerical test, full solver build, initial timing, fresh16, broader/F32/save/resume/continuation/material/holdout/cumulative qualification or guard/map/width/block/schedule variant rescue. Resource report {old.sha(H/'report.json')} and root replay {old.sha(R/'report.json')} preserve all results; root review is not external independence. All{len(published)} source/result/log/PTX artifacts HTTP-byte verified. Accepted162/main157/live/protectedPTX unchanged, acceptedE051 cumulative12.4372274192%, last primary baselineB185. Goal active.
'''
newline=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+note.encode('utf-8').replace(b'\n',newline))
old.save(O/'checkpoint.json',{'at':old.now(),'previous_goal_turn':'progress: D092 CPU exact metadata and E056 initial complete-cycle rejection','current_goal_turn':'progress: D093 bounded index proof/canonical bank model and E057 actual resource rejection','goal_active':True,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'last_primary_baseline':'B185','all_owned_children_terminal':True,'all_owned_command_calls_terminal':True,'source_main_live_ptx_unchanged':True,'next':'Review a distinct measured bottleneck or broaden the actual CUPTI profile to two-tone before another source candidate. D085/D087 device/phase observer is rainbow-only; eager two-tone summaries are not equivalent. Do not revive E057 map/guard/width/schedule variants. Keep all prior closed hypotheses closed.','live_deployment':'Continuing automatic review block remains; do not retry or ask duplicate permission.'});put(O/'checkpoint.json','E057-closure')
old.save(O/'publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True});old.custody()
print(json.dumps({'status':'rejected_and_published','registers':[38,40],'root_checks_before_publication':root['checks'],'published':len(published),'gpu_kernel_launches':0,'accepted_source':'E051'}),flush=True)
