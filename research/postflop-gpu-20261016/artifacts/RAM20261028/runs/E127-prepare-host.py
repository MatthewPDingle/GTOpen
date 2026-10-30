"""Freeze one full host form after source/resource/control prerequisites, before app kernels."""
import hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
N=ROOT/'runs/E127-native';control=h.read(N/'control-report.json');assert control['status']=='pass_scoped_two_phase_control_and_captured_parameter_contract'
assert len(control['negative_corruption_controls_rejected'])==7
S=ROOT/'runs/E127-host-source';S.mkdir(exist_ok=False)
design={
 'at':h.now(),'status':'FROZEN_BEFORE_HOST_COMPILER_OR_APPLICATION_KERNEL',
 'scope':'Allnormalownedpostfloptraininganddirectresearch/symmetric/paged/storedcontinuationswhenoriginalimmutableperboardmetadataisstable; no fixture/algorithm/storage/lock/range filtering. AllsameeligibleD313groups ororiginalfallbackwhennoheads/budget/optionalallocationOOM. No separate weaker numerical gate.',
 'caller_audit':'OnlyGpUSolverconstructorcreatesaction_spans,d_action_nodes,d_cfv_slot. SearchesallgpuRSfoundnoassignmentmutatorsafterconstruction. Paged/storedtake/swaponly7mutableFPbuffers,notoriginalmetadata;newworklistcontainsIDs,notFPaddresses. EveryeagersweepbindscurrentFPslicesafteraswap. MaincapturedgraphsusedonlystableownedGPUSolver; lockupdatealreadyinvalidatestraininggraphs. Symmetricprojection/transporthappensafterwholesweep. No cachedFPpointeradded.',
 'host_schedule':'PrivatepureCPUbuilderreceivesoriginalspans/children/CFVslots/kindcallback;fixedD313whole-star/foreign-reader/deepest-first/ascendingIDmatching. PublicGpuPlanandalloldvectorsremainunchanged. OneextraIDbuffercontainsregularthenstarheadsforeachoriginalphase;ordinarythenstarkernellauncheswherecountspositive. Everyoriginalactionnodeupdatedonce;noextraFPwork/reassociation,oldunselectedworkstaysoriginalphase.',
 'storage':'GpuSolveraddsOption<Box<ActionStarGpu>>onepointer. HeapownsoneCudaSliceu32,oneCudaFunction,twoLevelSpanVecs;logicalGPUbytes4*(originalA-selectedchildren),atmost4*A;FP/CFV/learning/reach/oldmetadataunchanged. CPUworklistVecanddenseeligibilityarraysdropafterconstruction/upload. Exacttype/capacity/peak/handles/drivercostsstillmustbemeasured.',
 'prospective_bounds':'ActualGpuSolverinlinegrowth<=16bytes,newboxedtype<=256bytes,newretainedhostspanpayload16*levelsbytesplusVecheaders/Box;newGPUworklist<=4*Abytes. No claimofdriverallocation/memoryneutrality;64MiBactualmaterialthresholds andfullcapacitytestsremain. Densebuildertemp12*N+8*CFVrowsbytespluscandidate/sorted/worklistVecs,actualcapacity/peakmustbeobserved.',
 'capacity_fallback':'Originalplan/F32layoutselectionandneededbudgetadmissionunchanged. Buildskipifsparebudget<4bytes;otherwiseoptionalworklistonlywhenactualworklistbytes<=budget-needed. OriginalGPOmetadata/stateallocationscreatedfirst,thenoptionalworklist. SynchronousallocationOOMdrainsstreamandkeepsoriginalschedule;other/asyncstreamerrorspropagateexistingerrorcontract. No uninitializedbuffer/borrowedowner tricks. Fault/capacity/materialqualificationmandatorybeforeadoption.',
 'accounting':'Storedmetadataestimateaddspossibleworklistbytesviaexactsamepurebuilder;observed_metadataaddsactualbufferlen. Estimateexplicitlyupper-boundwhenbudget/OOMfallbackomitsschedule. Alloriginalcapacitynumericalfieldsremaincomputedbyoriginalformulasplusnewdeclaredmetadatafield;actualnormalpathmustmatchestimatedpayload.',
 'validation_order':'CompileandrunactualpureCPUbuilderonall6frozenD313inputs/wholeprojectionswithindependentreader;actualfullRusttypes/layout/sourcebuildandbindingsbeforefirstappkernel. Thenfreezeallnewphysicalfields/costs/fulloriginaldirectplusstarcontrolmatrix,rawengine/canonical/ordinary/completecycle>=1%strictfixture/fresh16/broad/material/capacity/holdout/freshoriginalRAMcumulative/tempappgates. No source/phase/helper/group/guard/layout/width/quality/sample rescueafter genuinefailure.'}
h.save(S/'design.json',design)
owned={}
def write_owned(name,original,candidate):
    stem=Path(name).name;base=S/('baseline-'+stem)if original is not None else None;out=S/('candidate-'+stem)
    if base is not None:base.write_bytes(original)
    out.write_bytes(candidate)
    owned[name]={'base':str(base)if base else None,'candidate':str(out),'base_sha256':h.sha(base)if base else None,'candidate_sha256':h.sha(out)}
original=(h.REPO/'crates/solver/src/gpu/mod.rs').read_bytes();assert b'\r\n'not in original;text=original.decode();changed=text;edits=[]
def replace(before,after):
    global changed
    assert changed.count(before)==1,before[:100];changed=changed.replace(before,after,1);edits.append((before,after))
replace('mod arena;\n','mod arena;\nmod action_stars;\n')
new_type='''struct ActionStarGpu {
    nodes: CudaSlice<u32>,
    regular: Vec<LevelSpan>,
    fused: Vec<LevelSpan>,
    function: CudaFunction,
}

fn upload_action_stars(work: action_stars::StarWork, stream: &Arc<CudaStream>, module: &Arc<CudaModule>)
    -> Result<Option<Box<ActionStarGpu>>, String>
{
    // The pageable source remains alive until every queued upload is drained.
    let upload = stream.clone_htod(&work.nodes);
    stream.synchronize().map_err(e)?;
    let nodes = match upload {
        Ok(nodes) => nodes,
        Err(error) if error.0 == sys::CUresult::CUDA_ERROR_OUT_OF_MEMORY => return Ok(None),
        Err(error) => return Err(e(error)),
    };
    let function = module.load_function("up_action_star").map_err(e)?;
    Ok(Some(Box::new(ActionStarGpu { nodes, regular: work.regular, fused: work.fused, function })))
}

'''
replace('pub struct GpuSolver {\n',new_type+'pub struct GpuSolver {\n')
replace('    f_up_action_eval: CudaFunction,\n','    f_up_action_eval: CudaFunction,\n    action_stars: Option<Box<ActionStarGpu>>,\n')
anchor='''        let ctx = CudaContext::new(0).map_err(e)?;'''
planner='''        let star_work = if budget_bytes.saturating_sub(needed) >= 4 {
            action_stars::build(plan.num_nodes, plan.num_levels, plan.cfv_blocks,
                &plan.action_nodes, &plan.action_spans, &plan.node_na,
                &plan.node_children_start, &solver.spot.tree.children, &plan.cc_child,
                &plan.cfv_slot, |i| solver.spot.tree.nodes[i].kind)
                .filter(|work| work.nodes.len() as u64 * 4 <= budget_bytes - needed)
        } else { None };
'''
replace(anchor,planner+anchor)
replace('''        Ok(GpuSolver {
            f_copy_root:''','''        let mut gpu = GpuSolver {
            f_copy_root:''')
replace('''            f_up_action_eval: func("up_action_eval")?,
''','''            f_up_action_eval: func("up_action_eval")?,
            action_stars: None,
''')
end='''            _module: module,
        })
    }

    fn cfg'''
new_end='''            _module: module,
        };
        if let Some(work) = star_work {
            gpu.action_stars = upload_action_stars(work, &gpu.stream, &gpu._module)?;
        }
        Ok(gpu)
    }

    fn cfg'''
replace(end,new_end)
# Exactly the training up-action launch; down and average/BR evaluation keep original lists/functions.
start=text.index('            let sp = self.action_spans[l];',text.index('let sp = self.chance_node_spans[l];',text.index('fn paired_sweep')))
# paired_sweep contains down and up sections; select the unique final occurrence of its training up launch.
target=text.rfind('            let sp = self.action_spans[l];',0,text.index('    pub fn sync_to_cpu'))
opening=text.index('            if sp.count > 0 {',target);at=text.index('{',opening)+1;depth=1
while depth:depth+=(text[at]=='{')-(text[at]=='}');at+=1
old_block=text[target:at];assert '.launch_builder(&self.f_up_action)'in old_block and '.arg(&mut self.d_regrets[p])'in old_block
loop='''            for fused in [false, true] {
                let sp = if let Some(stars) = &self.action_stars {
                    if fused { stars.fused[l] } else { stars.regular[l] }
                } else if fused { LevelSpan { start: 0, count: 0 } } else { self.action_spans[l] };
                if sp.count == 0 { continue; }
                let (nodes, function) = if let Some(stars) = &self.action_stars {
                    (&stars.nodes, if fused { &stars.function } else { &self.f_up_action })
                } else { (&self.d_action_nodes, &self.f_up_action) };
'''
body=old_block[old_block.index('                let start = sp.start as i32;'):old_block.rfind('            }')]
body=body.replace('.launch_builder(&self.f_up_action)','.launch_builder(function)').replace('.arg(&self.d_action_nodes)','.arg(nodes)')
replace(old_block,loop+body+'            }')
reversed_text=changed
for before,after in reversed(edits):assert reversed_text.count(after)==1;reversed_text=reversed_text.replace(after,before,1)
assert reversed_text==text
write_owned('crates/solver/src/gpu/mod.rs',original,changed.encode())
new=(ROOT/'runs/E127-action-stars.rs').read_bytes();assert b'\r\n'not in new
write_owned('crates/solver/src/gpu/action_stars.rs',None,new)
cuda=ROOT/'runs/E127-source/candidate.cu';h.pin(cuda,h.read(ROOT/'runs/E127-source/manifest.json')['candidate_sha256'])
write_owned('crates/solver/src/gpu/kernels.cu',(h.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes(),cuda.read_bytes())
name='crates/solver/src/gpu/continuation_capacity.rs';base=(h.REPO/name).read_bytes();assert b'\r\n'not in base;source=base.decode()
old='''    n+(p.num_nodes*8) as u64+4+12+(4*p.nh_max*4) as u64 // unlocked table, sigma, discounts, eval roots'''
addition='''    let stars = super::action_stars::build(p.num_nodes, p.num_levels, p.cfv_blocks,
        &p.action_nodes, &p.action_spans, &p.node_na, &p.node_children_start,
        &s.tree.children, &p.cc_child, &p.cfv_slot, |i| s.tree.nodes[i].kind)
        .map_or(0, |work| work.nodes.len() as u64 * 4);
    n+stars+(p.num_nodes*8) as u64+4+12+(4*p.nh_max*4) as u64 // unlocked table, sigma, discounts, eval roots'''
assert source.count(old)==1;after=source.replace(old,addition,1)
assert after.count('    n\n}\n\npub fn stored_capacity_plan')==1
after=after.replace('    n\n}\n\npub fn stored_capacity_plan','    n+g.action_stars.as_ref().map_or(0, |stars| stars.nodes.len() as u64 * 4)\n}\n\npub fn stored_capacity_plan',1)
old_limit='"limitations":"Payload accounting; excludes CUDA context/modules,'
new_limit='"limitations":"Optional action-star worklist is an upper bound when budget/OOM fallback omits it. Payload accounting; excludes CUDA context/modules,'
assert after.count(old_limit)==1;after=after.replace(old_limit,new_limit,1)
inverse=after.replace(addition,old,1).replace('    n+g.action_stars.as_ref().map_or(0, |stars| stars.nodes.len() as u64 * 4)\n}\n\npub fn stored_capacity_plan','    n\n}\n\npub fn stored_capacity_plan',1).replace(new_limit,old_limit,1)
assert inverse==source
write_owned(name,base,after.encode())
h.save(S/'manifest.json',{'id':'E127-host','at':h.now(),'status':'FROZEN_FULL_HOST_SOURCE_PRE_COMPILER_APPKERNEL',
    'owned':owned,'tracked_owned_paths':[n for n,v in owned.items()if v['base']is not None],'new_owned_paths':[n for n,v in owned.items()if v['base']is None],
    'all_original_host_files_inverse_exact':True,'new_shader_bytes_identical_to_resource_control':True,'new_CPU_builder_sha256':h.sha(ROOT/'runs/E127-action-stars.rs'),
    'design_sha256':h.sha(S/'design.json'),'native_control_report_sha256':h.sha(N/'control-report.json'),
    'original_CPU_plan_source_unchanged':True,'old_GPU_arrays_and_CFV_map_unchanged':True,
    'new_source_without_new_compilers_or_appkernels':True,'raw_metadata_CPU_typecheck_direct_engine_canonical_and_all_adoption_gates_pending':True,
    'failure':'Fixed4filehost+shaderform/D313matching/onebuffer/twophaseLaunchs/oneCTAbarrier. No source/helper/phase/guard/group/layout/width/quality/sample rescue after genuinefailure.'})
print(json.dumps({'host_manifest_sha256':h.sha(S/'manifest.json'),'owned':list(owned),'new_owned_paths':[n for n,v in owned.items()if v['base']is None]}),flush=True)
