import json,re,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status())
R=ROOT/'runs/D207-resident-resource';Q=h.read(R/'report.json');assert Q['status']=='pass_resident_shader_compiler_resource_prerequisites' and all(Q['gates'].values()) and h.read(R/'execution/complete.json')['all_owned_children_terminal']
H=ROOT/'runs/E104-source';S=h.read(H/'schema.json');path=h.REPO/'crates/solver/src/gpu/mod.rs';base=path.read_bytes().decode("utf-8");h.pin(path,'1621c38893757f07a9a194b84e2d42086c2eec6210c980896b8d61210c8c15b1');assert not(H/'candidate-mod-r2.rs').exists();(H/'baseline-mod-r2.rs').write_text(base,encoding='utf-8',newline='\n')
pointer_sources={
'action_nodes':'self.d_action_nodes','chance_parents':'self.d_chance_parents','chance_children':'self.d_chance_children','chance_cards':'self.d_chance_cards','chance_nodes':'self.d_chance_nodes','fold_nodes':'self.d_fold_nodes','show_nodes':'self.d_show_nodes',
'node_player':'self.d_node_player','node_na':'self.d_node_na','node_data_off':'self.d_node_data_off','node_children_start':'self.d_node_children_start','children':'self.d_children','node_twin':'self.d_node_twin','node_tlose':'self.d_node_tlose','node_ttie':'self.d_node_ttie','node_cdiv':'self.d_node_cdiv','node_river_slot':'self.d_node_river_slot',
'reach0':'self.d_reach[0]','reach1':'self.d_reach[1]','rsrc0':'self.d_rsrc[0]','rsrc1':'self.d_rsrc[1]','regrets0':'self.d_regrets[0]','regrets1':'self.d_regrets[1]','strat_p':'self.d_strat[p]','lock_off':'self.d_lock_off','lock_sigma':'self.d_lock_sigma','cfv_slot':'self.d_cfv_slot','cfv':'self.d_cfv','disc':'self.d_disc',
'mask0':'self.d_hand_mask[0]','mask1':'self.d_hand_mask[1]','hand_perm':'self.d_hand_perm[p]','pc1':'self.d_hand_c1[p]','pc2':'self.d_hand_c2[p]','same':'self.d_same[p]','fold_card_off':'self.d_fold_card_off[1-p]','fold_card_idx':'self.d_fold_card_idx[1-p]',
'p_off':'self.d_riv_off[p]','p_cnt':'self.d_riv_cnt[p]','p_idx':'self.d_riv_idx[p]','p_lower':'self.d_riv_lower[p]','p_upper':'self.d_riv_upper[p]','o_off':'self.d_riv_off[1-p]','o_cnt':'self.d_riv_cnt[1-p]','o_idx':'self.d_riv_idx[1-p]','o_card_off':'self.d_riv_card_off[1-p]','o_card_pos':'self.d_riv_card_pos[1-p]',
'cc_start':'self.d_cc_start','cc_count':'self.d_cc_count','cc_card':'self.d_cc_card','cc_child':'self.d_cc_child','cc_perm':'self.d_cc_perm'}
assert set(pointer_sources)=={x['name'] for x in S['pointer_fields']}
types='''
#[repr(C)]
#[derive(Clone, Copy)]
struct ResidentArgs {
'''+''.join('    '+x['name']+': u64,\n' for x in S['pointer_fields'])+''.join('    '+name+': i32,\n' for name in S['scalar_fields'])+'''    spans: [[[u32; 2]; 64]; 5],
    // Explicitly initialize the CUDA ABI's final four alignment bytes.
    _reserved: u32,
}
unsafe impl cudarc::driver::DeviceRepr for ResidentArgs {}

#[derive(Default)]
struct ResidentState {
    function: Option<CudaFunction>,
    blocks: u32,
    shared: u32,
}
impl ResidentState {
    fn from_plan(ctx: &Arc<CudaContext>, module: &Arc<CudaModule>, plan: &GpuPlan) -> Self {
        if plan.num_levels == 0 || plan.num_levels > 64 { return Self::default(); }
        let spans = [&plan.action_spans, &plan.chance_spans, &plan.fold_spans, &plan.show_spans, &plan.chance_node_spans];
        let largest = spans.iter().flat_map(|v| v.iter()).map(|s| s.count).max().unwrap_or(0);
        if spans.iter().flat_map(|v| v.iter()).any(|s| s.start > i32::MAX as u32 || s.count > i32::MAX as u32) { return Self::default(); }
        let sm = match ctx.attribute(sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT) { Ok(n) if n > 0 => n as u32, _ => return Self::default() };
        if largest < sm || ctx.attribute(sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_COOPERATIVE_LAUNCH).ok() != Some(1) { return Self::default(); }
        let required = (0..2).map(|p| plan.nh[p].checked_mul(4).and_then(|n| plan.riv_max_cnt[p].checked_mul(16).and_then(|m| n.checked_add(m)))).collect::<Option<Vec<_>>>();
        let Some(required) = required.and_then(|v| v.into_iter().max()) else { return Self::default(); };
        let Ok(shared) = u32::try_from(required) else { return Self::default(); };
        let Ok(f) = module.load_function("e104_train") else { return Self::default(); };
        let Ok(static_shared) = f.shared_size_bytes() else { return Self::default(); };
        let Ok(limit) = ctx.attribute(sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK) else { return Self::default(); };
        if static_shared < 0 || static_shared as u64 + shared as u64 > limit as u64 || f.local_size_bytes().ok().filter(|n| *n <= 64).is_none() || f.max_threads_per_block().ok().filter(|n| *n >= BLOCK as i32).is_none() { return Self::default(); }
        let Ok(resident) = f.occupancy_max_active_blocks_per_multiprocessor(BLOCK, shared as usize, None) else { return Self::default(); };
        let Some(blocks) = resident.checked_mul(sm).filter(|n| *n > 0) else { return Self::default(); };
        Self { function: Some(f), blocks, shared }
    }
}
'''
# No persistent plan/cache/arena allocation; the Option<Vec> above is constructor-local only.
methods='''
    fn resident_ptr<T>(&self, data: &CudaSlice<T>) -> u64 {
        use cudarc::driver::DevicePtr;
        let (pointer, record) = data.device_ptr(&self.stream);
        drop(record);
        pointer
    }

    fn resident_args(&self, p: usize, reuse: bool) -> ResidentArgs {
        // All fields are integer POD; explicit reserved word avoids undefined padding reads.
        let mut a: ResidentArgs = unsafe { std::mem::zeroed() };
'''+''.join('        a.'+x['name']+' = self.resident_ptr(&'+pointer_sources[x['name']]+');\n' for x in S['pointer_fields'])+'''        a.num_levels = self.num_levels as i32;
        a.p = p as i32;
        a.nh0 = self.nh[0];
        a.down_nh1 = if reuse { 0 } else { self.nh[1] };
        a.nh_p = self.nh[p];
        a.nh_o = self.nh[1-p];
        a.nh_max = self.nh_max;
        for l in 0..self.num_levels {
            for (kind, span) in [self.action_spans[l], self.chance_spans[l], self.fold_spans[l], self.show_spans[l], self.chance_node_spans[l]].into_iter().enumerate() {
                a.spans[kind][l] = [span.start, span.count];
            }
        }
        a
    }

    fn try_resident_sweep(&mut self, p: usize, reuse: bool) -> Result<bool, String> {
        let Some(function) = self.resident.function.as_ref() else { return Ok(false); };
        if self.num_levels == 0 || self.num_levels > 64 { return Ok(false); }
        let spans = [&self.action_spans, &self.chance_spans, &self.fold_spans, &self.show_spans, &self.chance_node_spans];
        if spans.iter().flat_map(|v| v.iter()).any(|s| s.start > i32::MAX as u32 || s.count > i32::MAX as u32) { return Ok(false); }
        let largest = spans.iter().flat_map(|v| v.iter()).map(|s| s.count).max().unwrap_or(0);
        let sm = self._ctx.attribute(sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT).map_err(e)? as u32;
        if largest < sm { return Ok(false); }
        let current = (0..2).map(|p| (self.nh[p] as usize).checked_mul(4).and_then(|n| self.riv_max_cnt[p].checked_mul(16).and_then(|m| n.checked_add(m)))).collect::<Option<Vec<_>>>();
        let Some(current) = current.and_then(|v| v.into_iter().max()) else { return Ok(false); };
        // Workspace swaps may change dimensions. Never reuse a stale shared-memory plan.
        if current != self.resident.shared as usize { return Ok(false); }
        let blocks = largest.min(self.resident.blocks);
        if blocks == 0 { return Ok(false); }
        let a = self.resident_args(p, reuse);
        let nh0 = self.nh[0];
        let down_nh1 = if reuse { 0 } else { self.nh[1] };
        {
            let [reach0, reach1] = &mut self.d_reach;
            unsafe {
                self.stream.launch_builder(&self.f_copy_root)
                    .arg(&self.d_weights[0]).arg(&self.d_weights[1])
                    .arg(&mut *reach0).arg(&mut *reach1)
                    .arg(&nh0).arg(&down_nh1)
                    .launch(Self::cfg(4, 0)).map_err(e)?;
            }
        }
        // The enclosing exclusive borrow and existing single-stream invariant retain every
        // pointer owner through launch/capture. No pointer is cached across workspace swaps.
        unsafe {
            self.stream.launch_builder(function).arg(&a)
                .launch_cooperative(Self::cfg(blocks, self.resident.shared)).map_err(e)?;
        }
        Ok(true)
    }
'''
candidate=base;changes=[]
def replace(old,new):
 global candidate
 assert candidate.count(old)==1,old;candidate=candidate.replace(old,new,1);changes.append((old,new))
replace('pub struct GpuSolver {',types+'\npub struct GpuSolver {')
replace('    f_up_action_eval: CudaFunction,','    f_up_action_eval: CudaFunction,\n    resident: ResidentState,')
paths=[h.read(ROOT/'runs'/f/'report.json')['include_directory'] for f in ['D203-runtime-header-bootstrap','D203-cccl-header-bootstrap']]
replace('                        arch: Some(arch),','                        arch: Some(arch),\n                        include_paths: vec!['+','.join('r#"'+p+'"#.to_string()' for p in paths)+'],')
replace('        let func = |name: &str| module.load_function(name).map_err(e);','        let func = |name: &str| module.load_function(name).map_err(e);\n        let resident = ResidentState::from_plan(&ctx, &module, &plan);')
replace('            f_up_action_eval: func("up_action_eval")?,','            f_up_action_eval: func("up_action_eval")?,\n            resident,')
replace('    fn cfg(blocks: u32, shared: u32) -> LaunchConfig {',methods+'\n    fn cfg(blocks: u32, shared: u32) -> LaunchConfig {')
replace('        debug_assert!(!reuse_player1_reach || p == 1);','        debug_assert!(!reuse_player1_reach || p == 1);\n        if prof.is_none() && self.try_resident_sweep(p, reuse_player1_reach)? { return Ok(()); }')
reverse=candidate
for old,new in reversed(changes):assert reverse.count(new)==1;reverse=reverse.replace(new,old,1)
assert reverse==base
(H/'candidate-mod-r2.rs').write_text(candidate,encoding='utf-8',newline='\n');(H/'host-methods-r2.rs.txt').write_text(methods,encoding='utf-8',newline='\n');(H/'host-types-r2.rs.txt').write_text(types,encoding='utf-8',newline='\n')
h.save(H/'host-source-review-r2.json',{'id':'E104-host','at':h.now(),'status':'OFF_TREE_COMPLETE_SOURCE_NOT_ACTIVATED_NO_CFR_KERNELS','base_sha256':h.sha(path),'candidate_host_sha256':h.sha(H/'candidate-mod-r2.rs'),'byte_normalized_text_reverse_exact':True,'pointer_sources':pointer_sources,'argument_policy':'Fresh3008Bframefromall52currentdevicebufferpointers andoriginal5spanarrays,7signedscalars;explicitreservedtailzero. ExistingexclusiveGpuSolverborrow/oneCUDAstream/disabledcross-streamtracking retainallowners. No stalepointercaching acrossworkspace swaps.','caller':'Onlypaired_sweep training dispatcheswhenprofNoneandcurrentstateeligible; profileandallotherpaths retainoriginalbody. Newpath queuesidentical4CTArootcopy once beforeonecooperativetrainingkernel. Onkernel/APIerror propagate, neverfallbackafterpartialtraining. Evaluation/discounts/graphoutercadence/iteration/save/math unchanged.','fixed_eligibility':'<=64levels,allspanssigneddomains,largestphase>=actualSM,actualcoopsupport/defaultlimits/local<=64/128positiveoccupancy. Cacheonlyfunction/gridcapacity/sharedscalar. Recomputecurrentmaxspans/nh/sharedshape beforeanynewpathwork; changedsharedshape fallsbackoriginalbeforewrites, grid=min(currentlargest,cachedresidentSMcapacity).','declared_costs':'ResidentStateOptionfunction+2u32expected24B,requireactualwrappergrowth<=32BbeforeCFRoutcome;frame3008B/align8/spanoffset444/reserved3004. Constructor+dispatch currentlycreate2elementOptionVec tocompute sharedmax; transientCPUallocation/driverSMquery/module/JIT/header/stack/graphargumentresourcesincluded inlaterclocks/material qualification, no zero-costclaim. Couldbeoptimizedonlybynewunfailedform beforefullfreeze, notaftergenuinefailure.','portability':'Prototypecompile usespinnedprivateXheadersmatchingD207;portableproductionheaderdelivery/otherGPU/CPUfallbackbehavior unqualified andmandatorybeforeadoption. Shader remains exactD207resourcepassed bytes, no flags/sourcevariant.','future':'Hostcompile/layout,andstaticalloriginalhostargrolebindingreview beforeCFRkernels. Thenfull multistage raw/exceptional/reuse/graph/lock/save/resume/paging andcanonical/ordinary/complete1%strictfixture/fresh16/broad/material/capacity/holdout/cumulative/applicationgates. Unsupportedfeaturefallback mustbemeasured;no candidateaccepted.'})
owned={}
for rel,stem in [('crates/solver/src/gpu/kernels.cu','kernels.cu'),('crates/solver/src/gpu/mod.rs','mod-r2.rs')]:
 b=H/('baseline-'+stem);c=H/('candidate-'+stem);owned[rel]={'base':str(b),'candidate':str(c),'base_sha256':h.sha(b),'candidate_sha256':h.sha(c)}
h.save(H/'manifest-r2.json',{'id':'E104','at':h.now(),'status':'COMPLETE_OFF_TREE_SOURCE_UNBUILT_NOT_ACTIVATED','owned':owned,'accepted_source_sha256':h.custody(),'candidate_owned_sha256':{k:v['candidate_sha256'] for k,v in owned.items()},'tracked_owned_paths':list(owned),'new_owned_paths':[],'shader_resource_report_sha256':h.sha(R/'report.json'),'candidate_accepted':False})
print(json.dumps({'candidate_host_sha256':h.sha(H/'candidate-mod-r2.rs'),'shader_sha256':h.sha(H/'candidate-kernels.cu'),'reverse_exact':True,'pointer_roles':len(pointer_sources),'new_CFR_kernel_launches':0,'source_activated':False}),flush=True)
