import sys,json,shutil,subprocess,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();assert not (ROOT/'gpu-run.lock').exists() and not (ROOT/'epoch-sequence.lock').exists()
h.ar.refuse_active(h.ar.live_status())
for ident in ['D150-CFV-liveness','D151-auxiliary-resource','D152-packet-numerics']:
    assert h.read(ROOT/'runs'/ident/'execution/complete.json')['all_owned_children_terminal']
assert h.read(ROOT/'runs/D149-CFV-liveness/execution/probe.exit.json')['returncode']==101
model=h.read(ROOT/'comparisons/D148-packet-model/report.json')
partial=h.read(ROOT/'comparisons/D149-invalid-fixture/report.json')
life=h.read(ROOT/'comparisons/D150-CFV-liveness/report.json')
resource=h.read(ROOT/'runs/D151-auxiliary-resource/report.json')
numeric=h.read(ROOT/'comparisons/D152-packet-numerics/report.json')
assert numeric['status']=='pass_scoped_actual_packet_CPU_oracle_equivalence'
assert resource['status']=='pass_scoped_auxiliary_compile_load_resources'
A=ROOT/'runs/D153-packet-integration-review';A.mkdir(exist_ok=False)
gpu=h.REPO/'crates/solver/src/gpu'
inputs=[gpu/'mod.rs',gpu/'arena.rs',gpu/'plan.rs',gpu/'continuation.rs',gpu/'continuation_storage.rs',gpu/'continuation_paging.rs',h.REPO/'crates/solver/src/store.rs',h.REPO/'crates/solver/src/save.rs',h.REPO/'crates/solver/src/cfr.rs',ROOT/'comparisons/D148-packet-model/report.json',ROOT/'comparisons/D149-invalid-fixture/report.json',ROOT/'comparisons/D149-invalid-fixture/fixture-repair-review.json',ROOT/'comparisons/D150-CFV-liveness/report.json',ROOT/'runs/D151-auxiliary-resource/report.json',ROOT/'comparisons/D152-packet-numerics/report.json',ROOT/'runs/D151-auxiliary-resource/packet.cu',ROOT/'runs/D151-auxiliary-resource/execution/packet-compute_120.ptx']
text={p.name:p.read_text(encoding='utf-8') for p in inputs[:9]}
assert 'enum State { Memory([Vec<f32>;4]), Disk(DiskState) }' in text['continuation_storage.rs']
assert 'symmetric continuation requires zero F32 arenas' in text['continuation.rs']
assert 'paged continuation requires unlocked F32 CFR+ and explicit chance' in text['continuation_paging.rs']
assert 'use_isomorphism: true,' in text['cfr.rs'] and 'algo: Algorithm::Dcfr,' in text['cfr.rs']
assert 'let mut solver = Solver::with_storage(Arc::new(spot), storage);' in text['save.rs']
assert 'solver.algo =' not in text['save.rs'] and 'solver.use_isomorphism =' not in text['save.rs']
design={
 'id':'D153','at':h.now(),'status':'integration_contract_staged_not_implemented',
 'prior_statuses_preserved':{'D148':'finite_packet_integer_model_pass_not_GPU_or_integration_proof','D149':'closed_invalid_fixture_not_regraded_or_pooled','D150':'fresh_corrected_fixture_finite_liveness_pass','D151':'auxiliary_compile_load_resource_prerequisites_pass','D152':'actual_packet_CPU_oracle_controls_pass'},
 'new_source_audit':[
  'Stored continuation Memory/Disk persist only the four learning arrays. Seven-buffer workspaces also move reach and CFV allocations for reuse; that does not make CFV contents canonical persisted state. D148 earlier wording about state operations must be read with this distinction.',
  'Symmetric and stored continuation constructors require zero F32 arrays. Paged continuation validates F32 on every sweep. A compressed-only fast path must decline these formats before optional module setup. These wrappers were source-audited, not executed by D150; no universal paging claim.',
  'Plain changing-root continuation permits compressed data but requires CfrPlus/no actual isomorphism. D150 covers32 such actual sweeps with changing reaches and scratch clobbers. Its save/load fixtures explicitly restore the intended two flags. Application save format remains unchanged.',
  'GpuSolver::sync_to_cpu and sync_strategy first synchronize; training performs an up pass and eager/queued evaluation regenerate mode0 terminals before private mode1 reuse. No optional scratch phase may run inside a captured graph or between those private modes.',
  'PinnedBuf currently owns a raw f32 pointer/len without an initialized-prefix field. A new path must initialize its entire checked used prefix as raw bytes before creating typed views, borrow it exclusively through both existing completion waits, and retain original fallback behavior. No reference or cached device pointer may escape.'
 ],
 'prospective_first_integration_form':{
  'status':'fixed_before_any_integrated_source_or_timing_not_an_accepted_candidate',
  'admission':'All selected stores must be compressed signed-regret/unsigned-strategy, actual device cc12.0, and aggregate selected active f32 source bytes at least16777216 (16MiB). Both current CFV and pinned staging lengths must hold65544 four-byte words. Validate all blocks/scale owners/host/source bounds and all checked arithmetic before optional module loading or writes. Decline whole call on unsupported conditions.',
  'size_rule_rationale':'Prospective coarse large-transfer admission to avoid paying module/packet setup on small readbacks.16MiB is a fixed implementation policy, not an empirical crossover or a proven optimal threshold. It is chosen before integration/performance observations and must not be tuned after a failed screen.',
  'packet_shape':'Exactly128 GPU threads, at most31 descriptors and at most65544 u32 words per packet, matching actual D152 data controls. Full u64 source indices and loop induction. No alternate block width, runtime NVRTC, extra explicit device output/descriptor allocations, or per-packet host heap allocation.',
  'shader':'Persisted source-bound compute120 PTX SHA '+numeric['PTX_sha256']+'; separate lazily loaded auxiliary module. Main accepted CUDA source and runtime compiler flags remain byte unchanged. Driver module JIT/loading/ownership/destruction must be included in complete-process resource/lifecycle checks.',
  'learning_and_CPU_contract':'All four device learning arrays remain read-only. Direct scatter raw signed/unsigned q bits and exact per-node scale into original host offsets. Preserve original inactive restoration and F32 path. Original iteration/symmetry publication remains exact. CFV may change only after the original entry fence and must regenerate before future reads.',
  'host_borrow':'Raw-initialize only checked prefix before new typed views; no simultaneous f32/u32 typed alias and no references beyond joined transfer completion. Descriptor/output regions disjoint. Load packet descriptor bits into the existing CFV allocation and download only packed scales/q into the initialized existing pinned owner. Current live buffer lengths/ownership validated on each call, including after workspace swaps.',
  'failure':'Unsupported setup declines before optional activity. Submission/runtime failures must drain queued work and propagate the original error, with host staging and source references alive through completion. No silent partial-result fallback after launches.',
  'cost_boundary':'Any module/cached functions, host metadata, copy/scatter work, fences and destruction costs must be measured. If ownership changes move costs outside benchmark full_cycle_ms, retain entire-process wall/lifecycle diagnostics; do not call relocation a speedup.'
 },
 'required_before_timing':[
  'Implement one isolated source-bound integration form without altering accepted application files. Pin exact fallback reversal, main CUDA hash and PTX provenance. Preserve originals and reject the form after actual numerical/resource failure.',
  'Run exact typed-view/packet planning/decline/guards tests with current actual layouts. Force the same internal packed path in finite engine controls so tiny fixtures cannot pass only through fallback; verify noiso/algorithm after load as in D150.',
  'Compare all65 other device fields, all CPU q/scales/query/save/lock/resume state, subsequent graphs/evaluation/continuation, complete physical CFV and logical regeneration with explicit expected scratch differences. Ordinary F32/small/unsupported paths must exhibit zero optional loads/allocations/launches.',
  'Measure actual module/setup/CPU/device/pinned/metadata/graph resource effects, peak memory and capacity boundaries. No claim that zero local bytes or no explicit new output buffers implies no total resource cost.'
 ],
 'qualification_after_correctness':'Only then freeze fresh complete-solve three-pair screen at>=1% unrounded aggregate with strict fixture slowdown guard. Advancing candidates need separately frozen16pair confirmation, broad/material/capacity/holdout/fresh-original qualification. No source/threshold/width/shape/sample rescue after an actual failed integrated form.',
 'new_integrated_source_created':False,'new_performance_candidate_created':False,'performance_measurements':0,'candidate_accepted':False,'source_sha256':{str(p):h.sha(p) for p in inputs}}
h.save(A/'design-review.json',design)
folders=[ROOT/'runs/D148-packet-model',ROOT/'comparisons/D148-packet-model',ROOT/'comparisons/D149-invalid-fixture',ROOT/'runs/D150-CFV-liveness',ROOT/'comparisons/D150-CFV-liveness',ROOT/'runs/D151-auxiliary-resource',ROOT/'runs/D152-packet-numerics',ROOT/'comparisons/D152-packet-numerics',A]
pub=[]
for folder in folders:
 for p in folder.iterdir():
  if not p.is_file() or p.suffix not in ['.json','.rs','.cu','.py']:continue
  key=folder.name+'/'+p.name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  pub.append(key)
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);x=next(x for x in s['experiments'] if x['id']=='D152')
 x.update(status='measured',correctness='pass',stage='Actual packed output numerical controls passed',reason='2212cases/type x six cohorts,5208 GPU launches; every packed word/scale/descriptor/guard and complete host output matches shared Rust encoder.83328 scratch guard words,12 injected reader calibrations and62458 reader checks. No integration, speed or capacity claim.')
 x.setdefault('evidence',[]).append({'label':'Full raw CPU-oracle packet report','url':'evidence/D152-packet-numerics/report.json'})
 assert not any(x['id']=='D153' for x in s['experiments'])
 s['experiments'].append({'id':'D153','title':'Packet integration contract and admission review','kind':'diagnostic','status':'staged','accepted':False,'correctness':'source_contract_only','measurement_epoch':'RAM20261028','stage':'Fixed first integration form before code or timing','reason':'Prospective16MiB compressed/cc120 admission,65544-word current scratch/staging and31 descriptors at128 threads; preserve all original inactive/F32/small fallbacks. Pinned typed-view initialization, current-buffer ownership, exact engine state and actual resources must pass before timing. No candidate gain claimed.','evidence':[{'label':'Integration contract, source audit and remaining gates','url':'evidence/D153-packet-integration-review/design-review.json'}]})
 s.update(updated_at=h.now(),active_experiment='D153',stage='Integrate verified packet encoder under bounded runtime contract',activity='Packet address model, corrected36case scratch liveness, separate prebuilt shader resource gates and full2212case encoder corpus passed. Next one isolated integrated form; E080 remains live and current-RAM baseline stays10.4564s. No new speedup accepted.')
 h.ar.atomic_json(h.ar.STATUS,s)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
old=ledger.read_bytes();assert b'### D148 packet model through D152 exact packet output controls' not in old
entry=f'''

### D148 packet model through D152 exact packet output controls

Continue the X-only current-RAM epoch without changing accepted solver/application code, main CUDA source, protected PTX, benchmark/stopping rules or live server. D148 frozen CPU integer packet model passed144 physical cases,288 capacity declines,19 invalid/overflow/ownership declines,72 symbolic high-u64-source cases,288 injected output corruptions and6644 checks. This checks address/layout/scatter only; no native high-offset allocation or quantization was inferred.

D149 original control protocol remains unchanged and closed INVALID. Compiler0; native101. Save/load resets experimental algorithm/iso controls to DCFR/true; the fixture incorrectly assumed they persisted. After case8 resume the original plain continuation eligibility guard rejected before any continuation sweep. A separate retained-only reader checks848 raw frames and180 completed ordinary phase pairs, with all65 other device fields and completed CPU/query/save results exact. It does not complete the declared36case cohort or establish the planned resumed-CFR+ matrix. Preserve every original source/protocol/raw observation, failed exit and absent full metadata/audit; do not pool or regrade this as a pass.

A prospective fixture-repair review distinguishes this invalid request setup from a failed numerical equivalence or performance assertion. Separately named D150 explicitly restores the two originally declared fixture settings on both loaded CPU solvers and asserts actual device algorithms and noiso status. All36 original cases/752 clobbers/gates remain; no application source, shader, data corpus or performance gate changes. This is a fresh whole correctness cohort with no D149 partial pooling. D150 protocol {life['protocol_sha256']}: one compiler/one native process/independent raw reader terminal0. All752 scratch replacements,608 regenerated logical CFV pairs,144 intentionally retained scratch readback pairs,324 EV pairs and32 changing-range plain continuation roots pass. All66 constructor images match CPU references, all65 other actual device arrays and host scalars match, all CPU q/scales/query/save/resume files exact.3528 total raw frames including3008 GPU frames;575879 reader checks;1,140,455,990 represented words. Full physical CFV retained, current-player logical rows checked after regeneration; padding/raw scratch equality between arms is intentionally not claimed. No actual paged/stored wrapper or universal liveness proof.

D151 distinct isolated packet shader is not integrated into GpuSolver. Source SHA {resource['source_sha256']}; source-only helper compiles compute120/75 PTX, terminates, then a separate fresh driver process loads only persisted120 PTX. No NVRTC in that load process and no kernel launch. Two Rust compilers and both helper processes terminal0. Both entries have exact3parameter ABI/64bit addressing,38 registers,0local/dynamic shared bytes,512static shared bytes,128-thread theoretical occupancy12, legal default limits and unchanged stack1024/heap8388608. Main CUDA source/runtime compiler untouched. This proves bounded compilation/loading/resource prerequisites only; module resources/JIT/load/destruction are not free and integrated peak/capacity/performance remain unproven.

D152 frozen protocol {numeric['protocol_sha256']} executes the D151 artifact SHA {numeric['PTX_sha256']} without runtime NVRTC. Original source-bound2212case generator and accepted shared Rust encode_i16/u16 oracle, signed/unsigned x max1/7/31 descriptors with65544-word capacity: six cohorts and5208 actual GPU launches. Exactly1,964,131 encoded values/type include signed zeros, ties/adjacent values, NaN/Inf, subnormals, overflow, saturation, empty/odd and long blocks. Whole initial/expected/actual packet images, descriptor/scales/packed output, every scratch/host guard and direct host scatter match. Full source words exact before/after each cohort (not after every individual packet).67,599,373 represented raw words,83,328 packet guard words,7,674 odd and246 empty block occurrences,12 injected reader corruption calibrations,62,458 checks. Compiler/native/full retained reader terminal0. No application integration, performance score or acceptance.

D153 stages one integration contract before integrated code/timing. Fixed prospective compressed/cc12.0/aggregate16MiB admission, current CFV+pinned capacity65544words, max31 descriptors,128threads; unsupported or any checked-bounds failure declines before optional work.16MiB is a coarse pre-observation implementation policy, not a measured crossover and not tunable after a failed screen. Lazy separate prebuilt artifact, read-only learning arrays, direct exact q/scale scatter, original inactive restoration/F32/small fallback and unchanged publication. Must initialize checked pinned prefix before typed views, preserve exclusive borrows/fences/error lifetimes, and never cache swapped device pointers. All metadata/module/setup/destruction and actual memory/capacity effects must be qualified. No integrated optimization source or E092 timing candidate exists yet.

Source audit clarifies D148: Stored Memory/Disk persist four learning arrays; seven-buffer workspaces also move reach/CFV allocations but do not make CFV canonical content. Symmetric/stored/paged wrappers require F32 and must remain on original paths; their execution remains unproven here. Forced internal-path engine controls must prevent tiny fixtures passing only through fallback. After exact/compiled/actual-resource gates, freeze fresh complete-cycle screen, strict fixture guard and then16pair/broad/material/holdout/fresh-original qualification as required; no rescue of a real failed candidate. E009/E010 remain closed with their old counterevidence intact.

Current five-run E080 baseline remains10.4564109s (rainbow6.1265299, two-tone4.2093584, river0.1205226); no current-RAM gain adopted. Historical14.741418835370924% belongs to prior RAM/hardware comparison. All new data physically X; old archive read-only, no T access. Tracker evidence HTTP byte-verified. All research children terminal, sequence locks absent; accepted/main/live/protected PTX custody passes. No push or live binary replacement; goal active.
'''
nl=b'\r\n' if b'\r\n' in old else b'\n';ledger.write_bytes(old+entry.encode().replace(b'\n',nl))
subprocess.run(['git','-c','gc.auto=0','commit','--only','-m','research: verify scratch lifetime and exact packed encoder output','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
h.custody();assert not (ROOT/'gpu-run.lock').exists() and not (ROOT/'epoch-sequence.lock').exists()
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20) as response:served=json.load(response)
assert served['active_experiment']=='D153' and served['current_hardware_baseline']['aggregate_ms']==10456.4109
O=ROOT/'runs/D152-checkpoint';O.mkdir(exist_ok=False)
h.save(O/'report.json',{'at':h.now(),'research_git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip(),'HTTP_verified_artifacts':pub,'D153_design_sha256':h.sha(A/'design-review.json'),'current_E080_baseline_ms':10456.4109,'new_performance_gain_accepted':False,'all_research_children_terminal':True,'research_locks_absent':True,'source_main_live_PTX_custody_pass':True,'all_new_artifacts_physical_X':True,'current_X_free_bytes':shutil.disk_usage(ROOT).free,'goal_status':'active'})
print(json.dumps({'D149':'invalid_fixture_preserved','D150':'36case_liveness_pass','D151':'compile_load_resources_pass','D152':'5208_actual_packet_launches_exact','D153':'integration_contract_staged','HTTP_artifacts':len(pub),'baseline_ms':10456.4109,'all_research_children_terminal':True}),flush=True)
