import ast,hashlib,json,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status())
model=ROOT/'comparisons/D206-resident-phase-model/report.json';M=h.read(model);assert M['status']=='pass_scoped_full_original_phase_ownership_model' and len(M['cases'])==6 and h.read(ROOT/'runs/D206-resident-phase-model/execution/complete.json')['all_owned_readers_terminal']
H=ROOT/'runs/E104-source';H.mkdir(exist_ok=False);baseline=h.REPO/'crates/solver/src/gpu/kernels.cu';base=baseline.read_bytes();text=base.decode();h.pin(baseline,'a926bf0bc818a2ba808c862b59a552dfb7ade453ca18f347b4307784e47d9647');(H/'baseline-kernels.cu').write_bytes(base)
PTR=[]
def pointer(names,ctype):
 for name in names.split():PTR.append({'name':name,'c_type':ctype})
pointer('action_nodes chance_parents chance_children chance_cards chance_nodes fold_nodes show_nodes','const u32*')
pointer('node_player node_na','const int*');pointer('node_data_off','const u64*');pointer('node_children_start children','const u32*');pointer('node_twin node_tlose node_ttie node_cdiv','const float*');pointer('node_river_slot','const int*')
pointer('reach0 reach1','float*');pointer('rsrc0 rsrc1','const u32*');pointer('regrets0 regrets1 strat_p','float*');pointer('lock_off','const long long*');pointer('lock_sigma','const float*');pointer('cfv_slot','const u32*');pointer('cfv','float*');pointer('disc','const float*')
pointer('mask0 mask1','const u64*');pointer('hand_perm pc1 pc2 same','const u32*');pointer('fold_card_off fold_card_idx','const u32*');pointer('p_off p_cnt p_idx p_lower p_upper o_off o_cnt o_idx o_card_off o_card_pos','const u32*');pointer('cc_start cc_count cc_card cc_child cc_perm','const u32*')
assert len(PTR)==52 and len({x['name'] for x in PTR})==52
scalars=['num_levels','p','nh0','down_nh1','nh_p','nh_o','nh_max'];span_names=['action','chance_edge','fold','show','chance_node']
frame_bytes=((len(PTR)*8+len(scalars)*4+5*64*8+7)//8)*8;assert frame_bytes==3008 and frame_bytes<=4096
types='\n#include <cooperative_groups.h>\nstruct E104Span { u32 start; u32 count; };\nstruct E104Args {\n'+''.join('    '+x['c_type']+' '+x['name']+';\n' for x in PTR)+''.join('    int '+x+';\n' for x in scalars)+'    E104Span spans[5][64];\n};\nstatic_assert(sizeof(E104Args)==3008,"fixed kernel parameter frame");\nstatic_assert(__alignof__(E104Args)==8,"fixed kernel parameter alignment");\n'
names=['down_action_impl','down_action','down_chance','up_fold','up_show','up_chance','up_action_impl','up_action'];proof=[];copies=[]
for name in names:
 decl=('template<int NA>' if name.endswith('_impl') else 'extern "C" __global__ void '+name+'(')
 if name.endswith('_impl'):
  pos=text.index('void '+name+'(');start=text.rfind('template<int NA>',0,pos);assert start>=0
 else:start=text.index(decl)
 opening=text.index('{',text.index('void '+name+'(',start));at=opening+1;depth=1
 while depth:
  if text[at]=='{':depth+=1
  elif text[at]=='}':depth-=1
  at+=1
 original=text[start:at];copy=original
 if not name.endswith('_impl'):copy=copy.replace('extern "C" __global__ void '+name+'(', '__device__ __forceinline__ void '+name+'(',1)
 for oldname in names:copy=re.sub(r'\b'+oldname+r'\b','e104_'+oldname,copy)
 copy=copy.replace('void e104_'+name+'(','void e104_'+name+'(int e104_work,',1)
 copy=re.sub(r'(e104_(?:down|up)_action_impl<\d+>\()',r'\1e104_work, ',copy)
 copy=copy.replace('blockIdx.x','e104_work');assert 'blockIdx' not in copy and 'gridDim' not in copy
 reverse=copy.replace('void e104_'+name+'(int e104_work,','void e104_'+name+'(',1);reverse=re.sub(r'(e104_(?:down|up)_action_impl<\d+>\()e104_work, ',r'\1',reverse);reverse=reverse.replace('e104_work','blockIdx.x')
 for oldname in names:reverse=re.sub(r'\be104_'+oldname+r'\b',oldname,reverse)
 if not name.endswith('_impl'):reverse=reverse.replace('__device__ __forceinline__ void '+name+'(','extern "C" __global__ void '+name+'(',1)
 assert reverse==original,('exact helper projection',name)
 copies.append(copy);proof.append({'function':name,'original_sha256':hashlib.sha256(original.encode()).hexdigest(),'device_copy_sha256':hashlib.sha256(copy.encode()).hexdigest(),'exact_reverse_projection':True,'changes':'Onlyglobal-to-deviceinline linkage,explicituniformworkindexinstead ofblockIdx,matchingtemplateindexforwarding. Originalhelperbodyexpressions/order/arity/branches/shared/barriersunchanged.'})
# Calls retain the original host launch role bindings and all formal argument order.
calls={
'down_action':['a.action_nodes','(int)sp.start','(int)sp.count','a.node_player','a.node_na','a.node_data_off','a.node_children_start','a.children','a.rsrc0','a.rsrc1','a.regrets0','a.regrets1','a.lock_off','a.lock_sigma','a.reach0','a.reach1','a.nh0','a.down_nh1'],
'down_chance':['a.chance_parents','a.chance_children','a.chance_cards','(int)sp.start','(int)sp.count','a.rsrc0','a.rsrc1','a.mask0','a.mask1','a.reach0','a.reach1','a.nh0','a.down_nh1'],
'up_fold':['a.fold_nodes','(int)sp.start','(int)sp.count','a.p','a.node_player','a.node_twin','a.node_tlose','a.rsrc0','a.rsrc1','a.reach0','a.reach1','a.pc1','a.pc2','a.fold_card_off','a.fold_card_idx','a.same','a.cfv_slot','a.cfv','a.nh_p','a.nh_o','a.nh_max'],
'up_show':['a.show_nodes','(int)sp.start','(int)sp.count','a.node_twin','a.node_tlose','a.node_ttie','a.node_river_slot','a.p == 0 ? a.rsrc1 : a.rsrc0','a.p == 0 ? a.reach1 : a.reach0','a.p_off','a.p_cnt','a.p_idx','a.p_lower','a.p_upper','a.o_off','a.o_cnt','a.o_idx','a.o_card_off','a.o_card_pos','a.same','a.pc1','a.pc2','a.cfv_slot','a.cfv','a.nh_p','a.nh_o','a.nh_max'],
'up_chance':['a.chance_nodes','(int)sp.start','(int)sp.count','a.cc_start','a.cc_count','a.cc_card','a.cc_child','a.cc_perm','a.node_cdiv','a.p == 0 ? a.mask0 : a.mask1','a.hand_perm','a.cfv_slot','a.cfv','a.nh_p','a.nh_max'],
'up_action':['a.action_nodes','(int)sp.start','(int)sp.count','a.p','a.node_player','a.node_na','a.node_data_off','a.node_children_start','a.children','a.p == 0 ? a.regrets0 : a.regrets1','a.strat_p','a.p == 0 ? a.rsrc0 : a.rsrc1','a.p == 0 ? a.reach0 : a.reach1','a.lock_off','a.lock_sigma','a.cfv_slot','a.cfv','a.disc','a.nh_p','a.nh_max']}
formal_names={}
for name in calls:
 i=text.index('extern "C" __global__ void '+name+'(');a=text.index('(',i)+1;b=text.index(')',a);header=text[a:b];header=re.sub(r'//[^\n]*','',header);header=re.sub(r'/\*.*?\*/','',header,flags=re.S);params=header.split(',');formal_names[name]=[re.search(r'([A-Za-z_]\w*)\s*$',x.strip())[1] for x in params]
 assert len(params)==len(calls[name]),('all original helper arguments',name,len(params),len(calls[name]))
entry='\nextern "C" __global__ void e104_train(const __grid_constant__ E104Args a) {\n    cooperative_groups::grid_group grid=cooperative_groups::this_grid();\n    if (!grid.is_valid()) { asm volatile("trap;"); return; }\n'
def phase(role,index):
 return '        { E104Span sp=a.spans['+str(index)+'][l]; if (sp.count>0) {\n            for (u64 work=blockIdx.x;work<sp.count;work+=gridDim.x) {\n                e104_'+role+'((int)work, '+', '.join(calls[role])+');\n                __syncthreads();\n            }\n            grid.sync();\n        }}\n'
entry+='    for (int l=0;l<a.num_levels;++l) {\n'+phase('down_action',0)+phase('down_chance',1)+'    }\n'
entry+='    for (int l=a.num_levels-1;l>=0;--l) {\n'+phase('up_fold',2)+phase('up_show',3)+phase('up_chance',4)+phase('up_action',0)+'    }\n}\n'
assert entry.count('__syncthreads();')==entry.count('grid.sync();')==6
candidate=base+b'\n\n'+(types+'\n\n'+'\n\n'.join(copies)+'\n'+entry).encode();assert candidate.startswith(base);(H/'candidate-kernels.cu').write_bytes(candidate)
schema={'pointer_fields':PTR,'scalar_fields':scalars,'span_names':span_names,'span_levels':64,'frame_bytes':frame_bytes,'frame_alignment':8,'formal_names':formal_names,'helper_calls':calls,'original_CUDA_sha256':h.sha(baseline),'candidate_CUDA_sha256':h.sha(H/'candidate-kernels.cu'),'original9sourceprefix_exact':True,'helper_copy_projections':proof}
h.save(H/'schema.json',schema)
h.save(H/'source-review.json',{'id':'E104-shader','at':h.now(),'status':'OFF_TREE_SHADER_ONLY_NOT_INTEGRATED_OR_SPEED_ADMITTED','mechanism':'Onecooperativepersistentgrid pertrainingtraverser,originalwholeworkitems reassignedbyCTAgrid-stride. Originalkernelboundaries replaced bygrid.syncaftereachoriginalnonemptyphase; CTAbarrieraftereveryworkitem modelsoriginalblockretirement/sharedscratchlifetime. All128threadsjoinwork/phasecollectives; helperreturnsonlyreturntoglobalwrapper. Originalflat-edgechanceunchanged,notE102fanout orE078foldfusion.','helper_source_projection':'All8originaldevice/globaltraininghelperbodies reverseexactly afteronlyexplicitblockworkindex/linkage/templateforwarding adaptation. Samefloat operands/order/arity/locks/p1reuse/permutation/positivezero/scans/reductions/barriers,original9CUDAentrysourceprefixbyteexact. No newCPUCFRmath/evaluation/quality/savechange. GPUbitexactnessstillunproven.','immutable_parameter_frame':'52pointerwords,7signedscalars,5x64originalLevelSpanarrays,3008B/align8. const __grid_constant__ actualCUDA12.9>=sm70 guaranteesoneimmutablegridargumentobjectratherthanthreadlocalstructcopy; no pointed-data read-onlyclaim. ExacttypedRust/CUDAframeABI/layout requiredbeforeapplicationkernels. No newdevice/pinnedpayloadallocation inproposedhost; byvaluedrivercapturedargumentstorageisa realcost.','prospective_host_costs':'Laterhostadds optionalCudaFunction plusgrid/sharedu32state (expected24B,require<=32B); publicwrappermetadata mustreportexpectedgrowth,notwaivedafterobservation. Actualhostbinarysizeof/capacity/graphresourcesnotyetproved. Argument3008Btransientstack/frame andmodule/headercompile/JIT/register/staticshared/local costsreported. OriginalE102wrappergatefailure remainsclosed;no numericfieldexceptions.','fixed_host_eligibility_design':'128threads,<=64levels,supportedcooperativelaunch,actualentrypositiveoccupancy/defaultlimits. Largestoriginalphasecount>=SMcount;grid=min(largestphase,actualoccupancy*SM). Unsupported/small/deeperplans retainoriginalpathbeforefunction/kernelwork;profilingretainsoriginalperkernelpath. Freezeexacthostsourcebeforefirstappkernel; nothreshold/grid/arity/phase/helper/flag variantaftergenuinefailure.','resource_gate':'OneRustmodule-onlyhelper,2candidateNVRTC12.9compiletargets120/75 withfrozenvendorheaders,originalbaselinePTXreused. Original9entries/ABIsmustnormalizedexactandactualresourceequal. Newentryone3008Bparam,128supported,localbytes<=64(originalmaxtraininglocal),static+worst26520dynamicfitdefault,contextstackunchanged,positive128occupancy; reportlowerresidency/higherregs/sharedrisk,notmaterialneutrality. No appkernels orordinaryoptimizeradmittedfrompass.','future':'Fullrawmultiphase/scratchpoison/FPexceptional/reuse/locks/graph/continuation/paging/canonical/ordinary/build/complete1%strictfixture/fresh16/broad/material/capacity/holdout/cumulative/applicationgatesremain. Portablelicensed/reproducibleheaderdeliveryandallruntimecompilecostsmustbequalifiedbeforeadoption.','primary_parameter_doc':'https://docs.nvidia.com/cuda/archive/12.9.2/cuda-c-programming-guide/index.html#grid-constant','source_activated':False,'candidate_accepted':False})
print(json.dumps({'shader_sha256':h.sha(H/'candidate-kernels.cu'),'helper_projections':len(proof),'pointer_fields':len(PTR),'parameter_frame_bytes':frame_bytes,'source_activated':False}),flush=True)
