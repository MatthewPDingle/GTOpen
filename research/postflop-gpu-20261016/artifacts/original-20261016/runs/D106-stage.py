"""Stage a distinct exact-layout betting-subtree replication candidate, no native work."""
import difflib,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();old.ar.refuse_active(old.ar.live_status());assert not (ROOT/'gpu-run.lock').exists();assert shutil.disk_usage(ROOT).free>=66*1024**3
assert old.read(ROOT/'runs/E064-closure/decision.json')['candidate_accepted'] is False
H=ROOT/'runs/D106-subtree-replication';S=ROOT/'runs/E065-source';assert not H.exists() and not S.exists();H.mkdir();S.mkdir()
base=(old.REPO/'crates/solver/src/tree.rs').read_bytes();text=base.decode('utf-8').replace('\r\n','\n')
descriptor='''// A completed, board-independent betting subtree. These are indices/counts
// into the existing output vectors, not a second retained copy or a cache.
#[derive(Clone, Copy)]
struct SubtreeTemplate {
    nodes_start: usize,
    nodes_len: usize,
    children_start: usize,
    children_len: usize,
    actions_start: usize,
    actions_len: usize,
    data_start: [u64; 2],
    data_len: [u64; 2],
}

'''
assert text.count('struct BuildState {')==1;text=text.replace('struct BuildState {',descriptor+'struct BuildState {')
helper='''    // Replay a completed subtree at the current append positions. Decline
    // before mutation if a budget/integer boundary needs the original path.
    fn try_clone_subtree(&mut self, t: &SubtreeTemplate) -> Option<u32> {
        let node_start = self.nodes.len();
        let child_start = self.children.len();
        let action_start = self.actions.len();
        let node_end = node_start.checked_add(t.nodes_len)?;
        let child_end = child_start.checked_add(t.children_len)?;
        let action_end = action_start.checked_add(t.actions_len)?;
        if node_end > u32::MAX as usize || child_end > u32::MAX as usize
            || action_end > u32::MAX as usize
            || self.max_nodes.is_some_and(|cap| node_end > cap)
        {
            return None;
        }
        let node_delta = u32::try_from(node_start.checked_sub(t.nodes_start)?).ok()?;
        let child_delta = u32::try_from(child_start.checked_sub(t.children_start)?).ok()?;
        let action_delta = u32::try_from(action_start.checked_sub(t.actions_start)?).ok()?;
        let data_delta = [
            self.data_size[0].checked_sub(t.data_start[0])?,
            self.data_size[1].checked_sub(t.data_start[1])?,
        ];
        let data_end = [
            self.data_size[0].checked_add(t.data_len[0])?,
            self.data_size[1].checked_add(t.data_len[1])?,
        ];

        // Each complete template range is already in these same vectors.
        // Repeated children have identical BuildState and static board_mask;
        // the chance card is deliberately absent from the betting state.
        self.nodes.extend_from_within(t.nodes_start..t.nodes_start + t.nodes_len);
        self.children.extend_from_within(t.children_start..t.children_start + t.children_len);
        self.actions.extend_from_within(t.actions_start..t.actions_start + t.actions_len);
        for node in &mut self.nodes[node_start..node_end] {
            if node.kind == KIND_ACTION || node.kind == KIND_CHANCE {
                node.children_start += child_delta;
            }
            if node.kind == KIND_ACTION {
                node.actions_start += action_delta;
                node.data_offset += data_delta[node.player as usize];
            }
        }
        for child in &mut self.children[child_start..child_end] {
            if *child != SENTINEL {
                *child += node_delta;
            }
        }
        self.data_size = data_end;
        Some(node_start as u32)
    }

'''
assert text.count('    fn push_node(')==1;text=text.replace('    fn push_node(',helper+'    fn push_node(')
a=text.index('        // Known waste, kept deliberately:');b=text.index('    fn runout_chance(',a);body=text[a:b]
needle='        let mut child_indices = vec![SENTINEL; 52];';assert body.count(needle)==1;body=body.replace(needle,needle+'\n        let mut template: Option<SubtreeTemplate> = None;')
needle='            let child = self.action_node(child_state)?;';assert body.count(needle)==1
replacement='''            let child = if let Some(t) = &template {
                if let Some(root) = self.try_clone_subtree(t) {
                    root
                } else {
                    // Preserve original node-budget errors and partial-build
                    // behavior when the whole template would not fit.
                    self.action_node(child_state)?
                }
            } else {
                let nodes_start = self.nodes.len();
                let children_start = self.children.len();
                let actions_start = self.actions.len();
                let data_start = self.data_size;
                let root = self.action_node(child_state)?;
                debug_assert_eq!(root as usize, nodes_start);
                template = Some(SubtreeTemplate {
                    nodes_start,
                    nodes_len: self.nodes.len() - nodes_start,
                    children_start,
                    children_len: self.children.len() - children_start,
                    actions_start,
                    actions_len: self.actions.len() - actions_start,
                    data_start,
                    data_len: [self.data_size[0] - data_start[0], self.data_size[1] - data_start[1]],
                });
                root
            };'''
body=body.replace(needle,replacement);text=text[:a]+body+text[b:]
(S/'baseline-tree.rs').write_bytes(base);(S/'candidate-tree.rs').write_bytes(text.replace('\n','\r\n' if b'\r\n' in base else '\n').encode())
(S/'candidate.patch').write_text(''.join(difflib.unified_diff(base.decode().replace('\r\n','\n').splitlines(keepends=True),text.splitlines(keepends=True),fromfile='a/crates/solver/src/tree.rs',tofile='b/crates/solver/src/tree.rs')),encoding='utf-8',newline='\n')
source_paths=[old.REPO/'crates/solver/src/tree.rs',old.REPO/'crates/solver/src/game.rs',old.REPO/'crates/solver/src/store.rs',old.REPO/'crates/solver/src/cfr.rs',old.REPO/'crates/solver/tests/postflop_autoresearch.rs',old.REPO/'research/postflop-gpu-20261016/experiments.md']
old.save(H/'source-audit.json',{'id':'D106','at':old.now(),'status':'source_audit_no_native_or_speed_evidence','source_sha256':{str(p):old.sha(p) for p in source_paths},'findings':[{'source':'tree.rs:advance_street chance construction','fact':'Every allowed card constructs the same child_state; card is explicitly unused. board_mask is static root board only. Current code intentionally builds already-dealt-card phantom subtrees for save-compatible numbering.','implication':'Full betting subtrees repeat exactly; replication can remove repeated recursive/menu/transient-vector work while preserving every output node, child slot and action.'},{'source':'game.rs:Spot::new_impl and benchmark build stage','fact':'Spot tree creation and CPU Storeallocation are inside registered full-cycle timing. River ranking and symmetry are separate unchanged work.','implication':'This targets real complete-cycle work; actual end-to-end speed must still be measured.'},{'source':'D044constructor diagnostic and following menu-cache audit','fact':'Historical tree spans sum251.54ms; menu caching alone was declined under2%gate because recursion/output growth remain. Those older spans are not current speed evidence.','implication':'Whole subtree replication is a distinct algorithm removing recursion/menu work together, not a menu-cache retry or a projected2.56%gain.'}], 'bounded_novelty_search':'rg over indexed source-review/proposal/audit/README files for subtree cloning/copying and topology/subtree reuse found no prior executed form. Not exhaustive semantic novelty proof.','excluded_directions':['E005/E014separate GPUarity entries','E009/E010GPUquantization','E012/E013CPUencoding','D099by-card scratch','E064local index narrowing'],'production_source_activated':False,'performance_measured':False,'candidate_accepted':False})
old.save(S/'source-review.json',{'id':'E065','at':old.now(),'status':'STAGED_NOT_FROZEN_FOR_NATIVE','source_scope':'tree.rs only, no CUDA/GpuPlan/Store/quality/evaluator/menu change. First successful advance_street child supplies completed output ranges. Other same-state card children append clones and translate only absolute indices/data offsets. runout_chance source unchanged.','proof_obligations':['For a fixed advance_street invocation all child BuildState values and board_mask are identical; no card value is passed into action_node. Preserve all phantom subtrees and52slot SENTINELplacement.','Inductively each completed subtree has contiguous node/child/action ranges and no external child references. All nonsentinel child IDs are shifted by node destination delta.','Only action/chance children_start fields shift; only action actions_start and player-specific data_offset shift. All terminal/unused fields and every f64 bit stay cloned exactly.','Nested first-child templates are complete before outer replay. Templates retain indices/counts only, so Vec reallocation cannot invalidate a borrowed pointer. No unsafe access introduced.','Compute all destination ends/deltas and data totals before mutation. When a whole clone cannot fit node budget/integer bounds, execute original recursive path, preserving errors rather than introducing an early different failure.','Each appended range length is no greater than current vector length. Under current Vec amortized growth, reserve by that length should cross at mostone doubling just as gradual append; require exact actual returned capacities, do not infer physical peak from this proof.','Same number/order/layout of nodes/actions/children and exact two data sizes must be proved on full raw trees, not merely root EV/fingerprint. Validate strict/lenient legacy, aggression carry, all-in/budget/error and arbitrary menu cases before production.'], 'costs_pending':'Output copying is required and retained. New local template descriptor, translation pass and allocation order need CPU/process/peak/lifetime checks. No retained hash cache or duplicate template vectors, but no materially-free assertion before measurement.','source_audit_sha256':old.sha(H/'source-audit.json'),'native_executions':0,'candidate_accepted':False})
reference=old.read(ROOT/'comparisons/E063-three-pair-comparison/report.json')['performance']['baseline_full_cycle_ms'];assert reference==10780.8471
old.save(H/'next-native-design.json',{'status':'DESIGN_NOT_EXECUTION_PROTOCOL','at':old.now(),'next_action':'Implement/review a fresh off-tree Rust original/candidate CPU TreeBuilder harness from these exact source files, then freeze its source/corpus/compiler/environment/measurement/assessment hashes before native execution. No permission question is pending.','canonical_inputs':[{'path':str(ROOT/f'runs/D099-plan-posting-scratch/fixture-{i}.json'),'sha256':old.sha(ROOT/f'runs/D099-plan-posting-scratch/fixture-{i}.json')} for i in range(3)],'fixed_component_sampling':'Three registered canonical spot configs. CPU tree construction only: fixed2unscored warmup pairs then9alternating BC/CB pairs per case, no exclusions/extensions/history timing pooling. All output checks/fingerprints outside component clock; final full raw tree and all three Vec capacities/config/rootstreet/data sizes compare exactly. Source values unchanged and GPU not used.','CPU_proxy_reference_ms':reference,'CPU_proxy_minimum_saving_ms':reference*.01,'advance_rule':'All raw typed tree fields/f64bits/child IDs/action variant+bits/order/data sizes and actual Vec capacities exact, plus budget/strict/lenient/legacy controls. Sum canonical baseline-minus-candidate tree medians>=107.808471ms and no canonical positive median slowdown with>=5/9slower pairs. This is a prospectively specified component-admission heuristic using a fixed historical E051reference, not a complete-cycle gain or bound. If it fails, close this source form without clone-scope/placement/threshold/cache/shape variants.','additional_controls':'Compare max_nodes0,1,N-1,N,N+1and actual errors/fallback; small diverse flop/turn/river, both initiative-carry modes, allin/runout, strict vs lenient dropped-size behavior, duplicate sizes and arbitrary action menus. Serialize full typed fields, not struct padding. Keep canonical valid spot normalization identical to Spot::new.','conditional_real_qualification':'If component gate passes, freeze fresh integrated GPU builds and normal84units/three paired complete cycles on acceptedE051. Then separate fresh16, full CPU/F32/save/menu/resume/continuation, processCPU/peak-memory/responsiveness, holdout and fresh-original cumulative underunchanged1%/fixture/exactness/no-material-cost policy. Persistent capacity equality does not prove transient peak equality.','source_activated':False,'native_executions':0,'performance_measured':False})
old.save(S/'manifest.json',{'id':'E065','at':old.now(),'status':'STAGED_NOT_FROZEN_FOR_NATIVE','candidate_owned_sha256':{'crates/solver/src/tree.rs':old.sha(S/'candidate-tree.rs')},'source_sha256':old.BASE|{'crates/solver/src/tree.rs':old.sha(S/'candidate-tree.rs')},'artifact_sha256':{p.name:old.sha(p) for p in S.iterdir() if p.is_file()},'native_executions':0,'source_activated':False})
published={}
for folder in [H,S]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key='evidence/'+folder.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  published[key]=old.sha(p)
old.save(H/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(e['id'] in ['D106','E065'] for e in s['experiments']);s['experiments'].extend([{'id':'D106','at':old.now(),'kind':'diagnostic','title':'Exact-layout repeated betting-subtree source audit','status':'completed','correctness':'not_run','accepted':False,'stage':'Source finding; native controls pending','reason':'Chance card is absent from betting BuildState; same-state subtrees repeat. A full-copy/index-translation proposal preserves every node/phantom/slot, distinct from old menu-cache-only direction. Source evidence only; no timing gain.','evidence':[{'label':'Source audit','url':'evidence/D106-subtree-replication/source-audit.json'},{'label':'Prospective CPU-control design','url':'evidence/D106-subtree-replication/next-native-design.json'}]},{'id':'E065','at':old.now(),'kind':'candidate','title':'Replicate identical betting subtrees with unchanged layout','status':'preparing','correctness':'pending','accepted':False,'stage':'Off-tree source staged; CPU controls not yet frozen/run','reason':'Build first identical card subtree normally, clone output ranges and translate absolute IDs/offsets for repetitions. Keep generic budget fallback, all float bits and save-compatible phantom nodes. Must prove raw full trees/capacities/errors and measurable CPU headroom before full GPU qualification.','evidence':[{'label':'Staged source obligations','url':'evidence/E065-source/source-review.json'},{'label':'Staged candidate patch','url':'evidence/E065-source/candidate.patch'}]}]);s.update(updated_at=old.now(),state='running',active_experiment='E065',stage='E065 CPU tree replication control preparation',activity='Distinct CPU construction source staged off-tree. No native protocol/execution or gain yet. Prepare exact raw tree/capacity/error and fixed component controls, then whole-cycle qualification if admitted. Accepted E05112.437227%unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'status':'distinct_tree_replication_source_staged','candidate_tree_sha256':old.sha(S/'candidate-tree.rs'),'reference_ms':reference,'component_admission_ms':reference*.01,'published':len(published),'native_executions':0,'goal_active':True}),flush=True)
