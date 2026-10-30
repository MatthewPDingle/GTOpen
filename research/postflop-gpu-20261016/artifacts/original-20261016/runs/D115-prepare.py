"""Freeze E071 two-branch CPU planner and exact untimed/timed CPU controls."""
from pathlib import Path
import difflib,shutil,subprocess,sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as c
c.custody();assert not(R/'gpu-run.lock').exists();assert shutil.disk_usage(R).free>=82*1024**3
c.ar.refuse_active(c.ar.live_status())
H=R/'runs/D115-parallel-plan-control';S=R/'runs/E071-source';assert not H.exists()and not S.exists();H.mkdir();S.mkdir()
st=c.read(c.ar.STATUS);assert not any(x['id']in ['D115','E071']for x in st['experiments'])
base=(c.REPO/'crates/solver/src/gpu/plan.rs').read_bytes();text=base.decode().replace('\r\n','\n')
left_marker='        // Terminal CFVs stay resident for repeated BR/average evaluations.'
middle_marker='        // --- Per-node scalar arrays'
end_marker='        GpuPlan {\n'
assert text.count(left_marker)==text.count(middle_marker)==text.count(end_marker)==1
start=text.index(left_marker);middle=text.index(middle_marker);end=text.index(end_marker)
left,right=text[start:middle],text[middle:end]
a=['num_levels','cfv_slot','cfv_blocks','action_nodes','action_spans','fold_nodes','fold_spans','show_nodes','show_spans','chance_nodes','chance_node_spans','chance_parents','chance_children','chance_cards','chance_spans','node_river_slot','num_slots','riv_off','riv_cnt','riv_sorted_idx','riv_sorted_str','riv_lower','riv_upper','riv_card_off','riv_card_pos','riv_max_cnt']
b=['node_player','node_na','node_data_off','arena_elements','node_children_start','node_twin','node_tlose','node_ttie','node_cdiv','hand_c1','hand_c2','hand_mask','hand_perm_flat','reach_slot','reach_blocks']
def indent(fragment):return ''.join('    '+line if line.strip()else line for line in fragment.splitlines(True))
def result(names):return '('+', '.join(names)+')'
wrapper='''        // These branches share immutable inputs and return disjoint owned arrays.
        // Flop/turn Spot construction has already used the global Rayon pool.
        // Keep river planning sequential, without initializing a pool here.
        let build_worklists = || {
'''+indent(left)+'            '+result(a)+'\n        };\n        let build_metadata = || {\n'+indent(right)+'            '+result(b)+'''
        };
        let (worklists, metadata) = if spot.board.len() < 5 {
            rayon::join(build_worklists, build_metadata)
        } else {
            (build_worklists(), build_metadata())
        };
        let '''+result(a)+''' = worklists;
        let '''+result(b)+''' = metadata;

'''
candidate=text[:start]+wrapper+text[end:]
# Exact extraction proves every original computational statement/loop is intact.
inner_a=candidate.split('        let build_worklists = || {\n',1)[1].split('            '+result(a)+'\n        };',1)[0]
inner_b=candidate.split('        let build_metadata = || {\n',1)[1].split('            '+result(b)+'\n        };',1)[0]
def unindent(fragment):return ''.join(line[4:]if line.startswith('    ')else line for line in fragment.splitlines(True))
assert unindent(inner_a)==left and unindent(inner_b)==right and candidate[:start]+left+right+candidate[start+len(wrapper):]==text
newline='\r\n'if b'\r\n'in base else '\n';encoded=candidate.replace('\n',newline).encode()
(S/'baseline.rs').write_bytes(base);(S/'candidate.rs').write_bytes(encoded)
(S/'candidate.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),encoded.decode().splitlines(True),fromfile='accepted-E051/plan.rs',tofile='E071/plan.rs')),encoding='utf-8',newline='')
history=subprocess.check_output(['git','log','--all','--format=%H','-G','rayon::join|build_worklists|build_metadata|parallel.*plan','--','crates/solver/src/gpu/plan.rs'],cwd=c.REPO,text=True).strip();assert history==''
rayon=Path(r'C:\Users\there\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\rayon-core-1.13.0\src\join\mod.rs');assert rayon.exists()
review={'id':'E071','at':c.now(),'status':'root_source_scope_review_not_external_audit','owned_source':'crates/solver/src/gpu/plan.rs','candidate_sha256':c.sha(S/'candidate.rs'),'mechanical_reverse_equals_accepted':True,'all_original_computational_statements_and_order_within_each_branch_exact':True,'groups':{'worklists':a,'metadata':b},'dependencies':{'outer_prefix':'Unchanged DFS creates immutable level/reached/river_key/reach_src and chance tables; n/nh/max_level are copied scalars.','worklists_reads':['spot','level','reached','river_key','max_level','n'],'worklists_consumes_only':['rep_edges'],'metadata_reads':['spot','reached','reach_src','n','nh'],'writes':'Each closure creates and mutates only its own original local vectors/counters. Join completes both before destructuring and original GpuPlan literal. No alias, unsafe, reordered within-array traversal or numeric reduction.','type_proof_pending':'Rust compiler must accept shared Spot and owned branch returns as Send/Sync.'},'scheduling':'One fixed two-closure rayon::join only for original board length3/4; original sequential left/right calls for board length5. No node threshold, local pool, new thread count setting or parameter tuning. Spot::new flop/turn river tables already use into_par_iter; river path does not.','heap_and_cost_scope':'No explicit new Vec/HashMap/clone/allocation site, no output lengths/capacities or device plan/launch changes. Existing temporary allocations can overlap differently; Rayon task execution/queue/stack and actual process peak/CPU responsiveness must be measured before adoption. Zero resource tradeoff is not assumed.','floating_scope':'Every original per-node conversion/division and river-table integer loop stays verbatim within one branch. GPU CUDA/arithmetic/launch/quality/save schema unchanged.','novelty':'Current ledger/GPU-source search and local all-ref plan.rs -G query find no implemented matching join; D110/D111 only identified the source lead. Not exhaustive remote history.','separate_from_closed_families':'Not E045parallel zero scan, E069showdown order, E070metadata encoding, E056action ordering, E063cutoff or failed D110observer. No failed D110 timing attribution is used.','rayon_source_sha256':c.sha(rayon),'source_activated':False,'compiler_or_native_runs':0,'GPU_or_performance_samples':0,'primary_acceptance':'Unchanged unrounded1%complete-solve, strict fixture guard, fixed3pairs then fresh16/broad/material/holdout/fresh-original; no rescue variants or samples.'}
c.save(S/'source-review.json',review)
ref=R/'runs/D112-showdown-order-control'
for src,dst in [(S/'baseline.rs',H/'accepted-plan.rs'),(S/'candidate.rs',H/'candidate-plan.rs')]:shutil.copyfile(src,dst)
for name in ['game.rs','field-schema.json','fixture-0.json','fixture-1.json','fixture-2.json']:shutil.copyfile(ref/name,H/name)
probe=(ref/'probe.rs').read_text(encoding='utf-8').replace('D112','D115')
assert probe.count('a.show_nodes,&b.show_nodes,true')==1;probe=probe.replace('a.show_nodes,&b.show_nodes,true','a.show_nodes,&b.show_nodes,false').replace('all52nonorder_fields_bitwise_equal','all53fields_bitwise_equal')
with(H/'probe.rs').open('x',encoding='utf-8',newline='\n')as out:out.write(probe)
oldP=c.read(ref/'protocol.json');command=[str(H/'probe.rs')if x==str(ref/'probe.rs')else('d115_probe'if x=='d112_probe'else(str(H/'build/probe.exe')if x==str(ref/'build/probe.exe')else x))for x in oldP['command']]
inputs=[Path(__file__),rayon,*[p for p in H.iterdir()if p.is_file()],*[p for p in S.iterdir()if p.is_file()],R/'runs/accepted-E051-live-20261018/protected-main.json',c.REPO/'crates/solver/src/gpu/plan.rs',c.REPO/'crates/solver/src/game.rs',c.REPO/'Cargo.lock']
pins={str(p):c.sha(p)for p in inputs}
for path,h in oldP['input_sha256'].items():
 if '\\build-e051-final-primary\\'in path:c.pin(path,h);pins[path]=h
for p in [R/'runs/D115-execute.py',R/'runs/D115-root-check.py']:assert p.exists();pins[str(p)]=c.sha(p)
P={'id':'D115','at':c.now(),'status':'frozen_before_compile_and_native','command':command,'cases':list(range(12)),'input_sha256':pins,'accepted_source':c.BASE,'candidate_owned_sha256':{'crates/solver/src/gpu/plan.rs':c.sha(S/'candidate.rs')},'warmup_pairs':2,'measured_pairs':9,'pair_order':['BC','CB','BC','CB','BC','CB','BC','CB','BC'],'untimed_raw_pairs':1,'correctness_rule':'All53full fields, f32bits, all nested capacities, struct sizes and tree bytes exactly equal accepted and independently retained D092baseline in all12cases:3fixtures x isooff/on x compact/full.','timing_scope':'Uninstrumented warmed CPU-plan component; held Spot, excludes destructor/raw encoding. Includes fixed join/scheduling cost. No GPU/complete-solve timing or D110observer attribution.','timing_admission':'Component observations descriptive only, not an acceptance proxy. No exclusions/extensions/variants/retiming rescue. Fixed complete-solve1%screen only after exactness/root/source controls pass; broader actual CPU/host+GPUpeak/capacity/responsiveness required before adoption.','minimum_free_before_bytes':82*1024**3,'minimum_free_during_bytes':66*1024**3,'expected_max_raw_bytes':6*1024**3,'peak_output_reservation_bytes':8*1024**3,'source_activation':False,'root_review_not_external':True,'live_E051_deployment_untouched':True}
c.save(H/'protocol.json',P);c.save(S/'manifest.json',{'id':'E071','at':c.now(),'accepted_source':'E051','candidate_owned_sha256':P['candidate_owned_sha256'],'cpu_control_protocol_sha256':c.sha(H/'protocol.json'),'source_activated':False,'native_solver_executions':0})
print({'protocol_sha256':c.sha(H/'protocol.json'),'candidate_sha256':c.sha(S/'candidate.rs'),'branch_outputs':[len(a),len(b)],'source_activated':False},flush=True)
