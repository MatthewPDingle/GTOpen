"""Record current final codegen and a fully measured closed component probe."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D090-wide-OR';R=ROOT/'comparisons/D090-component-root-check';q=old.read(R/'report.json');n=old.read(H/'report.json');p=old.read(R/'publication.json');c=old.read(ROOT/'runs/D089-zero-scan-codegen/assembly-review.json')
assert q['status']=='verified_closed_component_probe' and q['checks_passed']==460988 and q['raw_cases']==65840 and n['status']=='closed_component_gate_failed'
old.save(H/'execution-r2/terminal.json',{'at':old.now(),'outer_exec_session_id':4930,'outer_exec_chunk_id':'958474','returncode':0,'complete_sha256':old.sha(H/'execution-r2/complete.json'),'all_owned_children_terminal':True})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';data=ledger.read_bytes();assert b'### D089 final zero-scan codegen' not in data
text=f'''
### D089 final zero-scan codegen -- verified, compile-only

Exact measured E051 solver RLIB c55801469c43d75e329da05b1b56ad1a93865f5cae863ff78c1c7c43d97a5239and dependencies link the unmodified frozen primary evaluator with opt3/thinLTO/codegen1 and --emit=asm,link. Compiler handle27425terminated0; no native executable or GPU kernel ran.35final assembly modules and executable preserved with hashes. This is a new analysis executable, not asserted byte-identical to the historically timedE051binary; library-stage scalar assumptions remain insufficient.

The final ArenaLayout::upload function contains four inlined signed/unsigned qscan branch copies. Each main vector loop uses2x128bitloads,2independent integer-OR accumulators and16u16words/32bytes periteration. Scalar tails and original positive-zero scale checks remain. No256bitregister appears in that1500line function. Review {old.sha(ROOT/'runs/D089-zero-scan-codegen/assembly-review.json')} includes complete function and four loop bodies;44files HTTPbyteverified. Baseline is already SIMD. D019's earlier encoder result was not treated as current integer-OR evidence.

### D090 guarded wide serial OR -- component gate failed

One isolated prototype gives the exact same typed readonly i16/u16-bit OR folds an AVX2 target_feature, called only after runtime AVX2 detection. Official Rust runtime feature and target_feature safety documentation is linked in proposal.json. No manual intrinsics/pointer casting/FP arithmetic, Rayon/chunks/threshold/metadata/scan omission/readback encoder change or solver source activation. This is separate from closed E045/E049/E038variants.

The compiler merged identical signed and unsigned functions into one portable and one wide machine body, redirecting all typed call sites. The first name-only reader stopped before any native control or timing. Original failure, source/binary and complete callsite witness retained. R2only recognizes those unchanged canonical bodies; four separate control calls still pass signed/unsigned inputs and independently compare four results. Six calls per canonical body include control and benchmark paths. Portable body uses128bit vectors; AVX2body uses256bit vectors with automatic4accumulator unrolling. No helper/source/binary/ISA/gate change or recompilation followed the observer repair.

All65,840fixed controls pass: every65,536singleword bitpattern plus304vector/tail/offset/pattern cases. Full before/unsigned-after/signed-after images total{q['full_before_after_and_guard_words']}words and all4result words percase replay exactly. Complete raw file/guards retained. No GPU kernel or solve ran.

Fixed16pairs BA/AB alternate in4blocks,32independent native processes. Each creates the accepted fresh rainbow Solver with1,346,813nodes and1,386,321,040CPUarena bytes, no qpre-touch before first timer. The score includes4positive-zero scale checks+4full qscans; factory/allocator, snapshot guards, GPU and whole constructor/solve costs excluded. A separate pretouched measurement follows an explicit untimed touch in each process. No coarse component result is promoted as full-cycle speed.

Fresh medians **{q['fresh_baseline_median_ms']:.10f}to{q['fresh_avx2_median_ms']:.10f}ms**, **{q['fresh_gain_pct']:.10f}%component gain**, difference{q['fresh_median_difference_ms']:.10f}ms;12/16pairs improve. Baseline190.5185ms passes the prospective75%-125%representativeness window around D088187.8079ms. The old D088timing is used only for that separately frozen window, never pooled into current medians/gains. D090misses its fixed25%component-admission and13/16positive-pair gates. Paired/block/order medians and pretouched nonregression gates pass; pretouched medians{q['pretouched_baseline_median_ms']:.10f}to{q['pretouched_avx2_median_ms']:.10f}ms. All32observations retained, no exclusions/extensions/ISA/helper/factor/size rescue or production candidate follows. User's1%complete-solve policy remains unchanged.

460,988check root replay {old.sha(R/'report.json')} redecodes complete raw words, typed-call witness, actual32process stdout/receipts/order and every unrounded gate. {p['http_byte_verified_files']}artifacts HTTPbyteverified. Root replay is not external independent review. AcceptedE051/main/live/PTX remain exact and accepted cumulative12.4372274192%unchanged.

Source screening also declined a proposed original-order showdown reach-cache removal: E021already performed that transformation and returned0.0674%full-cycle gain. No duplicate source or native work was admitted. A distinct D091/E055hypothesis instead conditionally places the3immutableGPU discount reads in the existing action-update branch; its resource/raw work is recorded separately.
'''
nl=b'\r\n' if b'\r\n' in data else b'\n';ledger.write_bytes(data+text.encode('utf-8').replace(b'\n',nl));old.custody()
old.save(R/'checkpoint.json',{'at':old.now(),'previous_goal_turn':'progress: D087API and D088CPU constructor observers fully measured/replayed','current_goal_turn':'progress: D089final integer scan codegen; D09065840exact controls/32process fixed component rejection; E021duplicate declined; E055distinct GPU conditional-read experiment advanced','goal_active':True,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'owned_component_sessions_terminal':[27425,4930],'source_main_live_ptx_exact':True,'next':'Continue E055full solver qualification; do not reopen D090ISA/helper/size variants or old parallel/metadata/omission/showdown-cache transforms.','report_sha256':old.sha(R/'report.json')})
for src in [R/'checkpoint.json',H/'execution-r2/terminal.json',Path(__file__)]:
 key=R.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;assert not dst.exists();dst.write_bytes(src.read_bytes());assert urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15).read()==src.read_bytes()
print(json.dumps({'recorded':['D089','D090'],'ledger_sha256':old.sha(ledger)}),flush=True)
