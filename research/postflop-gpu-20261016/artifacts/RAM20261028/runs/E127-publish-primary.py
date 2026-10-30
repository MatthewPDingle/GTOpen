"""Publish retained E127 controls and primary screen, preserving accepted/live custody."""
import json,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
Q=ROOT/'comparisons/E127-three-pair-comparison/report.json';A=ROOT/'comparisons/E127-root-crosscheck/report.json';P=ROOT/'runs/E127-primary-plan/protocol.json'
q,a,plan=h.read(Q),h.read(A),h.read(P);perf=q['performance'];passed=perf['primary_timing_pass']
assert a['aggregate_gain_pct']==perf['observed_gain_pct']and a['status']==('pass_initial_timing_only'if passed else'pass_rejected')
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}and q['ordinary_units_passed']==86 and q['ordinary_units_ignored']==4
assert not q['excluded_samples']and q['extension_runs']==q['historical_timing_samples_used']==q['RAM_baseline_samples_scored']==0
assert h.read(ROOT/'runs/E127-primary-wrapper/complete.json')['all_owned_children_terminal']
S=ROOT/'runs/E127-host-source';manifest=h.read(S/'manifest.json')
for value in manifest['owned'].values():
    if value['base']is not None:h.pin(value['base'],value['base_sha256'])
    h.pin(value['candidate'],value['candidate_sha256'])
for name in['E127-native/control-protocol.json','E127-host-control/protocol.json','E127-direct/protocol.json','E127-build-plan/protocol.json','E127-primary-plan/protocol.json']:
    for path,digest in h.read(ROOT/'runs'/name)['input_sha256'].items():h.pin(path,digest)
native=ROOT/'runs/E127-native/control-report.json';host=ROOT/'runs/E127-host-control/report.json';direct=ROOT/'runs/E127-direct/report.json'
n,c,d=h.read(native),h.read(host),h.read(direct)
assert n['status']=='pass_scoped_two_phase_control_and_captured_parameter_contract'
assert c['status']=='pass_real_compiled_CPU_builder_all6_original_plans_and_types'
assert d['status']=='pass_all2457_original_and_derived_whole_physical_cases'and d['counts']['cases']==2457 and d['kernel_launches']==7914
repair=h.read(ROOT/'runs/E127-direct/reader-repair.json');h.pin(ROOT/'runs/E127-read-direct.py',repair['original_reader_sha256']);h.pin(ROOT/'runs/E127-read-direct-v2.py',repair['replacement_reader_sha256'])
receipts=[];repairs=[]
folders=['E127-native/execution','E127-host-control/execution','E127-direct/execution','E127-final-build','E127-primary-execution','E127-primary-wrapper']
for folder in folders:
    for path in(ROOT/'runs'/folder).rglob('*.exit.json'):
        receipt=h.read(path);record={'path':str(path),'sha256':h.sha(path),'returncode':receipt['returncode']}
        if path==ROOT/'runs/E127-direct/execution/reader.exit.json':
            assert receipt['returncode']==1 and receipt['error']is receipt['cleanup']is None
            assert "KeyError: 'immutable_words_both_arms'"in(path.parent/'reader.stderr.log').read_text(encoding='utf-8')
            repairs.append(record)
        else:
            assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None;receipts.append(record)
assert len(repairs)==1 and len(receipts)>=20
direction=f"{abs(perf['observed_gain_pct']):.6f}% {'faster'if perf['observed_gain_pct']>=0 else'slower'}"
reason=f"Three-fixture sum of medians: {perf['baseline_full_cycle_ms']:.4f} to {perf['candidate_full_cycle_ms']:.4f} ms; {direction}. "+('The initial screen passed; independent confirmation and full state, compatibility, memory, capacity, holdout and application checks remain before adoption.'if passed else'The fixed action-group form failed the initial speed screen and is closed. No extra samples or source variants.')+' All 2,457 direct cases, 86 ordinary tests, 18 scientific results and 138 convergence checkpoints matched. E080 remains qualified and live.'
H=ROOT/'runs/E127-primary-checkpoint';H.mkdir(exist_ok=False)
h.save(H/'report.json',{'id':'E127-primary-checkpoint','at':h.now(),'status':'INITIAL_SPEED_PASS_FULL_QUALIFICATION_PENDING'if passed else'REJECTED_CLOSED_ACTION_STAR_FORM',
    'measurement_epoch':'RAM20261028','source_manifest_sha256':h.sha(S/'manifest.json'),
    'change':'Fixed D313 deepest-first nonoverlapping action-only stars. Original child actions then parent within one CTA with one barrier; original nine kernels and action arithmetic unchanged. Original CFV scratch map retained. Foreign readers excluded by physical ownership rule. CPU planner plus one new u32 worklist and two phase span lists; normal owned, symmetric, paged/stored all use the same ownership contract, original path on no groups/budget/optional allocation OOM.',
    'control_scope':'Whole PTX finite control-flow and captured native count/barrier/parameter witnesses, source helper inverse and actual unchanged resource contract. CPU-compiled real planner matches all six retained original plans. These are scoped finite controls, not universal GPU/race/IEEE or complete supported-path proofs.',
    'cost_scope':'Actual GpuSolver +8 bytes (4456), boxed ActionStarGpu 120 bytes. Extra worklist logical payload 1644276/1001040/28 bytes on primary fixtures, both constructors. Planning, additional shader JIT/module, graph creation, worklist upload and all normal setup/solve/readback included in full_cycle_ms. Full physical driver/heap/peak/material/capacity/fallback costs still unqualified; not called cost-free.',
    'native_control_report_sha256':h.sha(native),'CPU_host_report_sha256':h.sha(host),'direct_report_sha256':h.sha(direct),'direct_counts':d['counts'],'direct_kernel_launches':d['kernel_launches'],
    'reader_repair':'Original independent direct reader passed all2457 whole-buffer comparisons then failed an aggregate dictionary key lookup. Additive V2 maps immutable_words_both_arms to immutable_post_words_both_arms. Original source/protocol/failed receipt retained. No compiler, GPU module, native case or scientific source rerun/change; both full readers retained.',
    'primary_performance':perf,'fixtures':q['fixtures'],'pairs':q['pairs'],'primary_exactness':q['exactness'],'ordinary_units_passed':86,'ordinary_units_ignored':4,
    'primary_protocol_sha256':h.sha(P),'root_crosscheck_sha256':h.sha(A),'decision':reason,'all_owned_children_terminal':True,'terminal0_receipts':receipts,'preserved_reader_failure_receipts':repairs,
    'candidate_adopted':False,'qualified_live_config':'E080/GPU/compressed/Rayon16/defaultaffinity','RAM_reference_sum_threefixture_medians_ms':10456.4109,'RAM_reference_not_scored_or_pooled':True,
    'all_adoption_gates_still_pending':plan['adoption_requirements'],'full_rawengine_canonical_newphysicalworklist_broad_capacity_material_not_yet_qualified':True,
    'last_primary_baseline':'B383','next_unused_primary_baseline':'B384','active_candidate':'E127'if passed else None,'next_unused_candidate':'E128',
    'accepted_main_live_protected_PTX_D304_HTML_unchanged':True,'all_new_bulk_X_S_readonly_no_T':True,'goal_active':True})
files=[]
for folder in['E127-native','E127-host-source','E127-host-control','E127-direct','E127-build-plan','E127-final-build','E127-primary-plan','E127-primary-execution','E127-primary-wrapper','E127-primary-checkpoint']:
    files += [p for p in(ROOT/'runs'/folder).rglob('*')if p.is_file()and p.suffix.lower()in['.json','.rs','.cu','.log','.txt','.py']and '__pycache__'not in p.parts]
files +=[Q,A];published=[]
for path in files:
    relative=path.relative_to(ROOT/'runs')if path.is_relative_to(ROOT/'runs')else path.relative_to(ROOT/'comparisons')
    dst=h.ar.DASHBOARD/'evidence'/relative;dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():assert dst.read_bytes()==path.read_bytes()
    else:shutil.copyfile(path,dst)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+relative.as_posix(),timeout=20)as response:assert response.read()==path.read_bytes()
    published.append({'url':relative.as_posix(),'sha256':h.sha(path)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);row=next(x for x in status['experiments']if x['id']=='E127')
    row.update(at=h.now(),accepted=False,status='running'if passed else'rejected',stage='Initial timing passed; full qualification pending'if passed else'Closed: complete-solve speed screen failed',correctness='pass_scoped_correctness_checks',reason=reason,performance=perf,baseline_full_cycle_ms=perf['baseline_full_cycle_ms'],candidate_full_cycle_ms=perf['candidate_full_cycle_ms'],full_cycle_ms=perf['candidate_full_cycle_ms'],fixture='Three-fixture sum of medians (3 matched pairs)',gain_pct=perf['observed_gain_pct'])
    row['evidence']=[{'label':label,'url':'evidence/'+path}for label,path in[('Fixed source and declared costs','E127-host-source/manifest.json'),('Native barrier and control checks','E127-native/control-report.json'),('Actual CPU planner and Rust types','E127-host-control/report.json'),('Every direct physical buffer','E127-direct/report.json'),('Frozen complete-cycle protocol','E127-primary-plan/protocol.json'),('Retained full-cycle timing','E127-three-pair-comparison/report.json'),('Independent science and arithmetic replay','E127-root-crosscheck/report.json'),('Checkpoint and remaining gates','E127-primary-checkpoint/report.json')]]
    status.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E127',stage='Action groups: confirmation pending'if passed else'Action groups rejected; performance search continues',activity=reason+' No new gain adopted. Last baseline B383; next B384.')
    h.ar.atomic_json(h.ar.STATUS,status)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';old=ledger.read_bytes();assert b'\n## E127 action-only groups - native, host, direct and initial timing'not in old
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
entry=f'''

## E127 action-only groups - native, host, direct and initial timing {'pass; adoption pending'if passed else'closed'}

Continues the frozen D313/E127 source form from ledger b7b79143e3d3dde8e80c7a665ff175fed8e9bd12. The 21.481740406%/21.440724255%/41.666666667% reductions in modeled scheduled action CTAs were counts, never measured gains. No E078 fold fusion, E104 persistent cooperative grid, E076 CFV recolouring, E099 adjacent hand pairing or closed equivalent form reopened.

Additive native reader pins existing PTX/captured ELF/SASS, checks whole finite PTX control graphs on 120/75, valid-CTA barrier postdominance/no parent-to-child edge, actual root/list/child table/arity/loop/parent bindings, all20 captured argument offsets/widths, uniform native count guard/only early EXIT/one barrier and original CUDA math slowpaths. Seven corruption controls reject. Scope is structured control and captured native witnesses, not full SASS FP/address/race proof. No new NVRTC/module/capture/GPU-query repeat. Report {h.sha(native)}.

One full four-file host form frozen before first application kernel: pure CPU D313 planner, original public plans/CFV map/old buffers unchanged, one optional boxed worklist plus two span lists. Uniform ownership-based eligibility, no fixture/algorithm/storage/lock/range narrowing. No groups/spare budget/optional synchronous allocation OOM retain original path. Graph stable ownership and all eager post-swap bindings audited, all original capacity arithmetic retained plus declared new metadata. Real compiled CPU-only control matches complete IDs/spans/counts of all six original initial/resumed plans; foreign reader and unsupported-shape controls reject. Real GpuSolver4456(+8)/ActionStarGpu120/StarWork88/OptionBox8/LevelSpan8align4. Worklist logical payload rainbow1644276/two-tone1001040/river28B. Host peak/driver/material/capacity/fallback still require actual qualification. Report {h.sha(host)}.

Direct protocol {h.sha(ROOT/'runs/E127-direct/protocol.json')} froze all819 original unencoded parent cases and two819-case derivatives (unlocked/locked first+last action children, own-grandchild CFV alias read before parent overwrite). All original arities/roles/algorithms/discounts/hand and thread tails/count0/NaN/Inf/signed-zero/subnormal controls retained. One compiler and one7914-launch native process; accepted original child kernels then parent versus one fused candidate. Entire12 immutable inputs and3 physical mutable buffers both arms, seeds independently regenerated and every unowned guard checked; all15 actual allocations pairwise disjoint. Counts {json.dumps(d['counts'],separators=(',',':'))};5 raw files596225166B retained X. Original reader reached final aggregate then KeyError on differently named immutable count key; V2 maps that key only. Original reader/protocol/failure retained, no compiler/native/source/outcome repeats. Report {h.sha(direct)}.

Two fresh ordinary locked/offline feature/primary Cargo builds, exact accepted restoration after each, new owned module removed only after hash verification. V127-unit86 passed/4 ignored. Frozen B381/E127R1,E127R2/B382,B383/E127R3; all18 full scientific result records including arena fingerprints and138 convergence checkpoints exact original anchor. Real new CPU planner/worklist upload/module JIT/graphs/constructor costs included in normal complete-cycle timing. Sum of per-fixture medians {perf['baseline_full_cycle_ms']:.10f} to {perf['candidate_full_cycle_ms']:.10f}ms, unrounded gain {perf['observed_gain_pct']:.12f}%; strict fixture guards {json.dumps(perf['fixture_regression_guard'],separators=(',',':'))}. {reason} Independent raw-log/science/sorted-median arithmetic replay {h.sha(A)}. No sample exclusions/extensions/old RAM or historical pooling/significance/adoption claim.

Full original CPU plan/raw-engine/canonical including the new immutable list/spans, broad F32/menu/locks/save/resume/symmetric/paged/stored/fallback, actual CPU/GPU/process/heap/driver/peak/graph/material/capacity/responsiveness, separately frozen fresh16/holdout/fresh-original current-RAM cumulative/real temporary app remain mandatory before adoption. A genuine failure closes this fixed matching/group/helper/barrier/phase/guard/layout/width/source/quality/sample form; no rescue. All{len(receipts)} managed successful receipts terminal0; one reader failure and its mechanical repair retained. All{len(published)} nonbulk HTTP artifacts byte verified; checkpoint {h.sha(H/'report.json')}. E080/GPU/compressed/Rayon16/default affinity still qualified/live; RAM10456.4109ms reference separate. Accepted/main/live/protected2PTX/D304HTML unchanged, server idle/locks absent. Last B383/next B384; next unused E128. New bulk X/S read-only/no T, ledger prefix byte exact/local ledger-only commit/no push/no prune; goal active.
'''
ledger.write_bytes(old+entry.encode());assert ledger.read_bytes()[:len(old)]==old;h.custody()
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
assert subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).splitlines()==['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git','-c','gc.auto=0','commit','-m','research: qualify action-star direct controls and initial full solve screen'],cwd=h.REPO,check=True)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip();h.save(H/'publication.json',{'at':h.now(),'local_commit':head,'HTTP_artifacts':published,'report_sha256':h.sha(H/'report.json'),'goal_active':True})
h.custody();h.ar.refuse_active(h.ar.live_status());h.pin(h.ar.DASHBOARD/'index.html',h.read(ROOT/'runs/D304-tracker-display-metadata/layout-fix.json')['after_sha256'])
for path,url in[(h.ar.STATUS,'status.json'),(h.ar.DASHBOARD/'index.html','index.html'),(H/'report.json','evidence/'+H.name+'/report.json')]:
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/'+url,timeout=20)as response:assert response.read()==path.read_bytes()
assert not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=h.REPO,text=True).strip()and not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
process=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter 'ProcessId = 26528' | Select-Object ProcessId,ExecutablePath | ConvertTo-Json -Compress"],text=True))
assert process['ExecutablePath'].lower()==r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe'.lower()
h.save(H/'terminal-audit.json',{'at':h.now(),'status':'E127_INITIAL_SCREEN_COMPLETE_ALL_OWNED_WORK_TERMINAL','initial_speed_pass':passed,'candidate_adopted':False,'successful_receipts_terminal0':len(receipts),'preserved_reader_failures':1,'local_ledger_commit':head,'accepted_main_live_protected_PTX_D304_HTML_exact':True,'server_idle':True,'live_pid':26528,'locks_absent':True,'research_tracked_clean':True,'HTTP_status_index_report_exact':True,'last_primary_baseline':'B383','next_unused_primary_baseline':'B384','next_unused_candidate':'E128','X_free_bytes':shutil.disk_usage(ROOT).free,'all_new_bulk_X_S_readonly_no_T':True,'goal_active':True})
print(json.dumps(h.read(H/'terminal-audit.json')),flush=True)
