"""One off-tree fold-parent source, then an immutable no-application resource trial."""
from pathlib import Path
import ast,difflib,json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
D=R/'runs/D128-fold-parent';d=old.read(D/'report.json');assert d['admit_one_source_resource_trial']and len(d['cases'])==12
S=R/'runs/E078-source';H=R/'runs/E078-resource';assert not S.exists()and not H.exists();S.mkdir();H.mkdir()
cu=(old.REPO/'crates/solver/src/gpu/kernels.cu').read_text(encoding='utf-8');a=cu.index('extern "C" __global__ void up_fold(');b=cu.index('// Up sweep, showdown terminals:',a);fold=cu[a:b];begin=fold.index('    for (int j = threadIdx.x; j < nh_o; j += blockDim.x)');end=fold.rfind('\n}');fold_body=fold[begin:end]
helper='''// Training-only fold producer. Its unique action-parent CTA owns this
// persistent terminal row; all reductions and writes retain up_fold order.
__device__ __forceinline__ void produce_fold_in_parent(
    u32 n, int p, const int* __restrict__ node_player,
    const float* __restrict__ node_twin, const float* __restrict__ node_tlose,
    const u32* __restrict__ rsrc_o, const float* __restrict__ reach_o_buf,
    const u32* __restrict__ pc1, const u32* __restrict__ pc2,
    const u32* __restrict__ card_off, const u32* __restrict__ card_idx,
    const u32* __restrict__ same_p,
    const u32* __restrict__ cfv_slot, float* cfv,
    int nh_p, int nh_o, int nh_max)
{
    __shared__ float local_reach[1326];
    __shared__ float s[52];
    __shared__ float total_parts[256];
    const float* global_reach = reach_o_buf + (u64)rsrc_o[n] * nh_o;
'''+fold_body+'''
    // All original terminal stores precede the original action consumer.
    __syncthreads();
}

'''
needle='extern "C" __global__ void up_action(\n';assert cu.count(needle)==1;candidate=cu.replace(needle,helper+needle)
start=candidate.index(needle);stop=candidate.index('// Copy the first n floats',start);wrapper=candidate[start:stop];original_wrapper=cu[cu.index(needle):cu.index('// Copy the first n floats',cu.index(needle))]
old_header='    int nh_p, int nh_max)\n{';new_header='''    int nh_p, int nh_max,
    const float* __restrict__ node_twin, const float* __restrict__ node_tlose,
    const u32* __restrict__ rsrc_o, const float* __restrict__ reach_o_buf,
    const u32* __restrict__ pc1, const u32* __restrict__ pc2,
    const u32* __restrict__ card_off, const u32* __restrict__ card_idx,
    const u32* __restrict__ same_p, int nh_o)
{'''
assert wrapper.count(old_header)==1;wrapper=wrapper.replace(old_header,new_header)
needle2='    const int na = node_na[nodes[start + blockIdx.x]];\n';prefold='''    // Only reached fold terminals have the constructor-private -1 marker.
    u32 parent = nodes[start + blockIdx.x];
    u32 first_child = node_children_start[parent];
    for (int a = 0; a < na; a++) {
        u32 child = children[first_child + a];
        if (node_na[child] == -1) {
            produce_fold_in_parent(child, p, node_player, node_twin, node_tlose,
                rsrc_o, reach_o_buf, pc1, pc2, card_off, card_idx, same_p,
                cfv_slot, cfv, nh_p, nh_o, nh_max);
        }
    }
'''
assert wrapper.count(needle2)==1;wrapper=wrapper.replace(needle2,needle2+prefold);candidate=candidate[:start]+wrapper+candidate[stop:]
reverse=candidate.replace(helper,'',1).replace(wrapper,original_wrapper,1);assert reverse==cu
assert candidate[candidate.index('template<int NA>\n__device__ __forceinline__ void up_action_impl'):candidate.index(helper)]==cu[cu.index('template<int NA>\n__device__ __forceinline__ void up_action_impl'):cu.index('extern "C" __global__ void up_action(')]
mod=(old.REPO/'crates/solver/src/gpu/mod.rs').read_text(encoding='utf-8');candidate_mod=mod
tagger='''/// Mark only constructor-owned reached fold entries in the existing upload.
/// Public GpuPlan values and all vector lengths/capacities remain unchanged.
fn mark_fold_producers(plan: &mut GpuPlan) {
    for &node in &plan.fold_nodes {
        plan.node_na[node as usize] = -1;
    }
}

'''
needle3='fn build_lock_table(solver: &Solver)';assert candidate_mod.count(needle3)==1;candidate_mod=candidate_mod.replace(needle3,tagger+needle3)
needle4='        let ctx = CudaContext::new(0).map_err(e)?;';assert candidate_mod.count(needle4)==1;candidate_mod=candidate_mod.replace(needle4,'        mark_fold_producers(&mut plan);\n'+needle4)
start=candidate_mod.index('    fn paired_sweep(');stop=candidate_mod.index('    /// Copy GPU arenas back',start);training=candidate_mod[start:stop]
lo=training.index('            let sp = self.fold_spans[l];');hi=training.index('            let sp = self.show_spans[l];',lo);removed_fold=training[lo:hi];assert removed_fold.count('.launch_builder(&self.f_up_fold)')==1
training=training[:lo]+'            // Fold producers execute inside their unique action-parent CTA.\n'+training[hi:]
lo=training.index('.launch_builder(&self.f_up_action)');hi=training.index('.launch(Self::cfg(sp.count, 0))',lo);call=training[lo:hi];needle5='                        .arg(&nh_max)\n';extra_args='''                        .arg(&self.d_node_twin)
                        .arg(&self.d_node_tlose)
                        .arg(&self.d_rsrc[1 - p])
                        .arg(&self.d_reach[1 - p])
                        .arg(&self.d_hand_c1[p])
                        .arg(&self.d_hand_c2[p])
                        .arg(&self.d_fold_card_off[1 - p])
                        .arg(&self.d_fold_card_idx[1 - p])
                        .arg(&self.d_same[p])
                        .arg(&nh_o)
''';assert call.count(needle5)==1;newcall=call.replace(needle5,needle5+extra_args);assert call.count('.arg(')==20 and newcall.count('.arg(')==30;training=training[:lo]+newcall+training[hi:];candidate_mod=candidate_mod[:start]+training+candidate_mod[stop:]
unit='''    #[test]
    fn fold_producer_markers_are_private_and_exact() {
        for board in ["KsQs2d", "Qs7h2dKh", "AsKsQsJsTs"] {
            let spot = Spot::new(SpotConfig {
                board: board.into(), range_oop: "AA,KK,QQ,JJ,AKs,AQs,AKo".into(),
                range_ip: "AA,QQ,TT,77,AQs,KQs,AQo".into(),
                tree: TreeConfig { starting_pot: 10.0, effective_stack: 20.0, ..Default::default() },
            }).unwrap();
            for iso in [false, true] { for full in [false, true] {
                let mut plan = GpuPlan::build(&spot, iso);
                if full { plan.use_full_action_arenas(&spot); }
                let original = plan.node_na.clone(); let capacity = plan.node_na.capacity();
                mark_fold_producers(&mut plan);
                let folds: std::collections::HashSet<_> = plan.fold_nodes.iter().copied().collect();
                assert!(!folds.is_empty());
                for (n, (&a, &b)) in original.iter().zip(&plan.node_na).enumerate() {
                    if folds.contains(&(n as u32)) {
                        assert_eq!(spot.tree.nodes[n].kind, crate::tree::KIND_TERM_FOLD);
                        assert_eq!(a, 0); assert_eq!(b, -1);
                    } else { assert_eq!(a, b); }
                }
                assert_eq!(plan.node_na.capacity(), capacity);
                assert_eq!(plan.node_na.len(), original.len());
                for &n in &plan.action_nodes { assert!(plan.node_na[n as usize] > 0); }
                let once = plan.node_na.clone(); mark_fold_producers(&mut plan);
                assert_eq!(plan.node_na, once);
                let mut fresh = GpuPlan::build(&spot, iso);
                if full { fresh.use_full_action_arenas(&spot); }
                assert_eq!(fresh.node_na, original);
            }}
        }
    }

''';needle6='    fn reach_reuse_solver(';assert candidate_mod.count(needle6)==1;candidate_mod=candidate_mod.replace(needle6,unit+needle6)
reverse_mod=candidate_mod.replace(unit,'',1).replace(tagger,'',1).replace('        mark_fold_producers(&mut plan);\n','',1).replace(extra_args,'',1).replace('            // Fold producers execute inside their unique action-parent CTA.\n',removed_fold,1);assert reverse_mod==mod
names=['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs'];bases=['baseline.cu','baseline-mod.rs'];cands=['candidate.cu','candidate-mod.rs'];patch=''
for name,base,cand,btext,ctext in zip(names,bases,cands,[cu,mod],[candidate,candidate_mod]):
 raw=(old.REPO/name).read_bytes();nl=b'\r\n'if b'\r\n'in raw else b'\n';assert btext.encode().replace(b'\n',nl)==raw;(S/base).write_bytes(raw);old.pin(S/base,old.BASE[name]);(S/cand).write_bytes(ctext.encode().replace(b'\n',nl));patch+=''.join(difflib.unified_diff(btext.splitlines(True),ctext.splitlines(True),fromfile=name,tofile=name))
(S/'candidate.patch').write_text(patch,encoding='utf-8',newline='\n');(S/'mark-fold.rs').write_text(tagger,encoding='utf-8',newline='\n')
old.save(S/'manifest.json',{'id':'E078','at':old.now(),'accepted_source_sha256':old.BASE,'candidate_owned_sha256':{n:old.sha(S/c)for n,c in zip(names,cands)},'owned':{n:{'base':str(S/b),'candidate':str(S/c)}for n,b,c in zip(names,bases,cands)},'D128_report_sha256':old.sha(D/'report.json'),'scope':'Original fold producer runs in its unique action-parent CTA before byte-exact original up_action helper/dispatch. Training separate fold launches removed, evaluation fold path byte-exact. Constructor-private existing node_na marker-1 onlyfolds, no payload/layout/capacity/sizing/launchthread/quality/save changes. Static6536sharedB, dynamic0;30argABI host/candidate consistent. Final CTAbarrier preserves original foldglobalrow before consumer. Unit tests source included, not executed yet.','candidate_accepted':False})
old.save(S/'source-review.json',{'at':old.now(),'original_fold_arithmetic_suffix_copied_byte_exact':fold_body,'original_action_helper_and_dispatch_calls_exact':True,'CUDA_removal_reverse_exact':True,'host_removal_reverse_exact':True,'original8other_global_source_entries_exact':True,'additional_up_action_arguments':10,'baseline_arguments':20,'candidate_arguments':30,'host_30argument_order':'Original20then node_twin,node_tlose,rsrc_o,reach_o_buf,pc1,pc2,card_off,card_idx,same_p,nh_o','reduction':'Same per-thread reach load, card-list sums, strided partials and shared256tree; original float expressions/payout/globalfoldrow write unchanged. Static1326hand array replaces original dynamically sized local_reach pointer. Original4? block barriers are preserved exactly from copied suffix; one explicit final CTAbarrier added. No float reassociation intended; compiler/raw NaN/signedzero equivalence remains unproven.','ownership':'D128full12case unique direct action owner/persistent terminalrow proof. Complete down precedes up; both reach arrays immutable during up. Original fold producer inputs chosen as1-p and originalfold node rsrc, including opponent-action parent case. No terminalrow aliases scratch/show/fold; no otherconsumer before parent. Delayed fold row ends every sweep with same intendedstate.','continuation':'Projection/transport/copy kernels receive action-node lists only; negative marker lies outside those lists. Same GpuSolver training/eval callers and borrowed workspace slices; actual compiler/raw/broad compatibility still required.','costs':'All actionCTAs reserve6536staticshared even nofold; extra parentchildmetadata/markerbranch/finalbarrier. May reduceoccupancy/increase registers/spill or slowdown; resourcepolicy and all actualmaterial/fullcycle gates mandatory. No performance claim.'})
for name in ['baseline.cu','candidate.cu']:shutil.copyfile(S/name,H/name)
probe=(R/'runs/E075-resource/probe.rs').read_text(encoding='utf-8').replace('E075_RESOURCE','E078_RESOURCE');(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
print('E078 source prepared; resource executor/protocol still required before compiler',old.sha(S/'candidate.cu'),flush=True)
