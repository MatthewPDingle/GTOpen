"""Freeze original-node-helper action-star CUDA and resource prerequisites, off tree only."""
import ast,hashlib,json,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
D=ROOT/'runs/D313-action-star-ownership';model=h.read(D/'report.json');root=h.read(D/'root-report.json')
assert len(model['cases'])==len(root['cases'])==6 and len(root['negative_corruption_controls_rejected'])==4
assert all(x['all_physical_last_writers_unchanged']and x['same_phase_writes_disjoint']and x['all_learning_update_intervals_disjoint']for x in root['cases'])
for label in['model','root']:assert h.read(D/'execution'/(label+'.exit.json'))['returncode']==0
pattern=r'action_star|up_action_star|two.level.{0,30}action|up_action_pair|up_action_fused'
run=subprocess.run(['rg','-l','-i',pattern,str(ROOT/'runs'),r'S:\GTOpen-research\postflop-gpu-20261016\runs','-g','*.rs','-g','*.cu'],text=True,capture_output=True)
assert run.returncode in[0,1]and not run.stderr
hits=[]
for line in run.stdout.splitlines():
    path=Path(line)
    if path==ROOT/'runs/E127-resource-probe.rs':continue  # This turn's owned new draft is not historical evidence.
    text=path.read_text(encoding='utf-8-sig');matches=[v for v in text.splitlines()if re.search(pattern,v,re.I)]
    if matches and all('pair2'in v for v in matches):classification='E099adjacentHANDfloat2up_action_pair2,notdifferentactionnodes/levels;closed/notcomposed.'
    elif path.name=='candidate-tree.rs' and matches and all('action_start'in v for v in matches):classification='E065treecopyaction_start variable matched action_star prefix; no action-nodefusion.'
    else:raise AssertionError((path,matches))
    hits.append({'path':str(path),'sha256':h.sha(path),'matching_lines':matches,'classification':classification})
h.save(D/'history.json',{'at':h.now(),'bounded_retained_literal_hits':hits,'recognized_action_star_form':False,
    'scope':'RetainedX/Srs/cu literalstar/twolevel/actionpair/fusedactionmarkers pluscurrentledger/source review. HitsclassifiedasE099handpair2orE065action_startprefix. Notexhaustivesemantic/helper/remote noveltyproof.',
    'closed_counterevidence':'E078foldterminalproducerfusion addssharedfoldscratch; E104persistentallphasescooperativegridbarriers; E076unaryCFVcoloringchangeslayout. Newaction-onlydisjointstars,originalCFVmap/noextrashared/noallgridbarrier; nonecomposed/reopened.'})
S=ROOT/'runs/E127-source';S.mkdir(exist_ok=False)
original=(h.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();assert original.count(b'\n')==original.count(b'\r\n');text=original.decode('utf-8')
def function_at(start):
    opening=text.index('{',start);at=opening+1;depth=1
    while depth:depth+=(text[at]=='{')-(text[at]=='}');at+=1
    return text[start:at]
helper_start=text.index('template<int NA>\r\n__device__ __forceinline__ void up_action_impl(')
helper=function_at(helper_start)
global_start=text.index('extern "C" __global__ void up_action(');global_function=function_at(global_start)
parameter='const u32* __restrict__ nodes, int start, int count, int p,'
binding='    int b = blockIdx.x;\r\n    if (b >= count) return;\r\n    u32 n = nodes[start + b];\r\n'
assert helper.count(parameter)==helper.count(binding)==1
node_helper=helper.replace('void up_action_impl(','void star_action_impl(',1).replace(parameter,'u32 n, int p,',1).replace(binding,'',1)
assert node_helper.replace('void star_action_impl(','void up_action_impl(',1).replace('u32 n, int p,',parameter,1).replace('    const int na = NA == 0 ? node_na[n] : NA;',binding+'    const int na = NA == 0 ? node_na[n] : NA;',1)==helper
# The original helper reads discounts before its block binding. Reinsert at the exact original position above.
device_dispatch=global_function.replace('extern "C" __global__ void up_action(','__device__ __forceinline__ void star_action_dispatch(',1)
assert device_dispatch.count(parameter)==1
device_dispatch=device_dispatch.replace(parameter,'u32 n, int p,',1)
guard='    if (blockIdx.x >= (u32)count) return;\r\n'
selector='    const int na = node_na[nodes[start + blockIdx.x]];'
assert device_dispatch.count(guard)==device_dispatch.count(selector)==1
device_dispatch=device_dispatch.replace(guard,'',1).replace(selector,'    const int na = node_na[n];',1)
device_dispatch=device_dispatch.replace('up_action_impl<','star_action_impl<').replace('(nodes, start, count, p,','(n, p,')
back=device_dispatch.replace('__device__ __forceinline__ void star_action_dispatch(','extern "C" __global__ void up_action(',1).replace('u32 n, int p,',parameter,1).replace('    const int na = node_na[n];',guard+selector,1).replace('star_action_impl<','up_action_impl<').replace('(n, p,','(nodes, start, count, p,')
assert back==global_function
signature=global_function[:global_function.index('{')].replace('void up_action(','void up_action_star(',1)
args='p, node_player, node_na, node_data_off, node_children_start, children, regrets_p, strat_p, rsrc_p, reach_p_buf, lock_off, lock_sigma, cfv_slot, cfv, disc, nh_p, nh_max'
body='''{
    u32 b = blockIdx.x;
    if (b >= (u32)count) return;
    u32 n = nodes[start + b];
    u32 first = node_children_start[n];
    int na = node_na[n];
    // The host admits whole stars without chance children or foreign CFV readers.
    for (int a = 0; a < na; a++) {
        u32 child = children[first + a];
        if (node_na[child] > 0) {
            star_action_dispatch(child, @ARGS@);
        }
    }
    // Every original child helper completes before any parent helper begins.
    __syncthreads();
    star_action_dispatch(n, @ARGS@);
}
'''.replace('@ARGS@',args).replace('\n','\r\n')
suffix='\r\n// Action-only two-level stars. Original entry points remain above byte-exact.\r\n'+node_helper+'\r\n\r\n'+device_dispatch+'\r\n\r\n'+signature+body
candidate=original+suffix.encode();(S/'baseline.cu').write_bytes(original);(S/'candidate.cu').write_bytes(candidate)
(S/'original-helper.cu.txt').write_bytes(helper.encode());(S/'explicit-node-helper.cu.txt').write_bytes(node_helper.encode())
(S/'original-dispatch.cu.txt').write_bytes(global_function.encode());(S/'explicit-node-dispatch.cu.txt').write_bytes(device_dispatch.encode())
h.save(S/'manifest.json',{'id':'E127','at':h.now(),'status':'FROZEN_OFFTREE_SHADER_ONLY_PRE_COMPILER',
    'baseline_sha256':h.sha(S/'baseline.cu'),'candidate_sha256':h.sha(S/'candidate.cu'),'original9kernel_source_prefix_byteexact':True,
    'original_helper_inverse_exact':True,'original_dispatch_inverse_exact':True,
    'source_contract':'Newup_action_starhasoriginal20pointer/scalararguments. Explicitnnodehelpercopiesoriginalup_action_implbody,removesonlyblocklistbinding/countguard,originalpernodeFP/math/loops/arity/locked/opponent paths byteinverseexact. Device dispatchoriginal2/3/4/genericbyteinverseexact. EachCTAiteratesoriginalparentchildrenascendinga,executesactionchildren(node_na>0;nochancebyhostcontract),onewholeCTAbarrier,thenparent. Actualmetadataworklistnotimplementedyet.',
    'selection_contract_sha256':h.sha(D/'protocol.json'),'model_report_sha256':h.sha(D/'report.json'),'root_report_sha256':h.sha(D/'root-report.json'),
    'unchanged':'Original9globalentries/sourceprefix,allCPUpublicplan/CFVmap/data/metadata/storage/precision/quality/down/eval/terminal/chance semantics. No hostsourcecandidate,CUDAarrayallocation/applicationkernellaunch orspeedtest admitted yet.',
    'synchronization_reference':'https://docs.nvidia.com/cuda/archive/12.9.0/cuda-c-programming-guide/index.html#synchronization-functions',
    'synchronization_contract':'syncthreads orderspriorglobal/sharedaccessesforwholeCTA. Allhelpersreturnintowrapper,notkernelreturn; loops/childkinddecisionsuniformCTAmetadata,barrieroutsideallhelperbranches. ForeignreadersoutsideCTAexcludedbyhoststructuralcontract; no cross-blocksynchronizationassumption.',
    'risks':'SerializingseveralnodesperCTAcanloseparallelism/increaseregs/local/JIT/CFVtraffic/driverwork. Newhostworklist/eligibility/graphs/handle/allocation/constructioncostsnotimplementedormeasured. 21%structuralCTAcountnot21%time/no-costclaim.',
    'failure':'Closefixedoriginalmap/disjointstar/deepest-firstmatching/childthenparent/oneCTAbarrier/128threadsourceform atgenuinefailure. No phase/helper/guard/group/scope/order/layout/CFV/width/arity/flags/source/quality/sample rescue.'})
H=ROOT/'runs/E127-resource';H.mkdir(exist_ok=False)
parent=ROOT/'runs/E125-resource';old=h.read(parent/'protocol.json')
shutil.copyfile(S/'candidate.cu',H/'candidate.cu')
for arch in['compute_120','compute_75']:shutil.copyfile(parent/('baseline-'+arch+'.ptx'),H/('baseline-'+arch+'.ptx'))
shutil.copyfile(ROOT/'runs/E127-resource-probe.rs',H/'probe.rs')
inputs={k:v for k,v in old['input_sha256'].items()if str(ROOT/'reference/accepted-e080-deps')in k}
files=[Path(__file__),ROOT/'runs/E127-resource-probe.rs',ROOT/'runs/E127-resource-execute.py',ROOT/'epoch/common.py',D/'protocol.json',D/'report.json',D/'root-protocol.json',D/'root-report.json',D/'history.json']
files += [ROOT/'runs/E127-prepare-star-resource.py',ROOT/'runs/E127-prepare-star-resource-v2.py',D/'E127-preparation-repair.json',D/'E127-preparation-repair-v2.json']
files += [p for folder in[S,H]for p in folder.iterdir()if p.is_file()]
inputs.update({str(p):h.sha(p)for p in files})
h.save(H/'protocol.json',{'id':'E127-resource','at':h.now(),'status':'FROZEN_PRE_SHADER_COMPILER_MODULE_RESOURCE_PROCESS',
    'rustc_command':[x.replace('E125-resource','E127-resource')for x in old['rustc_command']],'input_sha256':inputs,
    'GPU_uuid':old['GPU_uuid'],'original_entries':old['original_entries'],'new_entry':'up_action_star','required_free_bytes':16*1024**3,
    'gates':'Both120/75original9headers/bodiesalphaexact;newentryoriginalup_action20paramABIsamenametransform,onebar.sync/noextra shared. Actualall9originalresourcesexact. Newentryvsoriginalup_action local<=64,constant/static/dynamic<=original0,stack<=originaldefault1024,maxthreads>=original1024,no defaultlimitloss andpositive64/128/256occupancy. Register/residencycostwarningsretained;no actualmaterialproof.',
    'pre_application_mechanism':'ActualPTX/nativewrapperchilditeration/original2/3/4/generichelperdispatch/finalbarrier/parentconsumers/returnuniformitymustbeaccounted. OriginalsourceinverseproofandfiniteownershipmodelnotactualGPUfloatproof. No appnumericalruns ifhardresourcefailure.',
    'pre_application_host_obligations':'Onlyaftershaderresourcepassmayonefullhostformbecreated. Freezeactualnewworklists/spans/handle/heap/wrapper/module/payload/CPUeligibility/capacity/lifecycle/fallback costs beforefirstapplicationkernel; accountfulloriginalandnewphysicalwords. No maximumstructuralbenefitclaim. Allsource/owner/graph/direct/canonical/broad/ordinary/fullcycle1%strictfixture/fresh16/material/capacity/holdout/freshoriginal/tempappgatesremain.',
    'failure':'ClosefixedD313selection+128threadoneCTAstar/onebarrier/helperform,no width/scope/phase/group/helper/order/layout/flags/source/quality/sample rescue. NewbulkX/Sreadonly/noT;no productionactivation.'})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);scout=next(x for x in status['experiments']if x['id']=='D313')
    scout.update(at=h.now(),status='complete',stage='Six retained plans and all selected groups replayed',correctness='pass_finite_ownership_model',reason='Original scratch layout retained. The model schedules about 21% fewer action blocks on each flop fixture and 42% fewer on river, with every action update retained. These are structural counts, not speed gains. All original CFV writer classes and learning intervals were checked.')
    assert not any(x['id']=='E127'for x in status['experiments'])
    status['experiments'].append({'id':'E127','at':h.now(),'title':'Two-level action groups in one block','kind':'candidate','status':'staged','accepted':False,'stage':'Frozen compiler and resource gate','correctness':'no_device_numerical_trials','reason':'Original action arithmetic is copied into an explicit-node helper. Each safe group computes action children, reaches one block barrier, then computes its parent. Register/local-memory costs may prevent admission. Host worklists and full numerical tests are still pending.','evidence':[]})
    status.update(updated_at=h.now(),active_experiment='E127',stage='Action groups: compiler and actual resource gate',activity='Finite ownership model passed. No GPU numerical or speed result yet; E080 remains live and unchanged.')
    h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'source_sha256':h.sha(S/'candidate.cu'),'protocol_sha256':h.sha(H/'protocol.json'),'shader_only':True}),flush=True)
