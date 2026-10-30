"""Commit-ready measured profiler checkpoint, with no optimization claim."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D087-cupti-driver-profile';R=ROOT/'comparisons/D087-driver-phase-root-check';q=old.read(R/'report.json');c=old.read(H/'cohort-report.json');p=old.read(R/'publication.json')
assert q['status']=='pass_scoped_driver_phase_diagnostic' and q['checks_passed']==185 and q['observer_usefulness_pass'] and c['all6full_results_60checkpoints_exact']
old.save(H/'cohort-execution/terminal.json',{'at':old.now(),'outer_exec_session_id':46779,'outer_exec_chunk_id':'3022d8','returncode':0,'complete_sha256':old.sha(H/'cohort-execution/complete.json'),'all_owned_children_terminal':True})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';data=ledger.read_bytes();assert b'### D087 driver API and phase timeline' not in data
text=f'''
### D087 driver API and phase timeline -- measured diagnostic

Retained D085 raw device-gap census finds407.393486/415.234229/407.901279ms uncovered within the observed activity span, but only12.571379/12.898318/12.555041ms uncovered by device activity between first and last kernels. This cannot cover CPU time before first or after last device event. It motivates explicit host/API phase observations rather than a graph/discount-upload optimizer assumption.

D087 reuses the official local CUDA12.9.79 CUPTI SDK and adds only Driver API activity plus six explicit CUPTI timestamp markers around init/solve/readback. Existing176byte rows retain cbid,process,thread,unique correlationId and returnValue; callback names decode offline from matching SDK header. No counters/injection/admin/system or driver settings/global installation. Explicit start/flush/stop while CUDA context lives. All original13kernel/257word/2guard ability checks pass, plus exact4graph-launch and4kernel-launch API records; everykernel joins its launch or replay.60records comprise13kernels,2copies and45APIs.

An inherited build-r3path in protocol hashing stopped the first evaluator preparation before any compiler/native work. Script/evaluator/patch/error are preserved in diagnostic-draft-r1. R2 only fixes the path and adds provenance; evaluator R1/R2 bytes equal. Diagnostic harness links the immutable acceptedE051solver RLIB; no production source/evaluator change. Fresh native handle6995terminated0; matched handle46779terminated0.

Fixed six-process D087B1/D087T1,D087T2/D087B2,D087B3/D087T3rainbow cohort retains identical6full states/60checkpoints. Each trace26,230kernels,407successfulGraphLaunchAPIrecords, all graph-node repeats9/199/199and kernel/API correlation joins valid, six ordered phase timestamps,0drops/errors/bad timestamps/outstanding buffers. Preset +/-10%everypair complete/native/outer observer screen passes. Complete-cycle changes -0.1957803477%,+0.6782951280%,+0.4707065113%; native0/+0.4481792718/+0.8579465542%; outer+0.3757575758/+0.7666098809/+1.5180957009%. No exclusions/extensions/pooling or optimization acceptance.

Median diagnostic phase spans: init657.1493ms,solve4492.7859ms,readback346.4193ms. Device unions14.646995/4479.399985/102.523152ms respectively. Observed uncovered-by-device-or-API spans417.487525/0.573330/243.874900ms; device-uncovered solve span12.852313ms. Median components are not additive complete-cycle partitions. Solve DtoH API union4443.6827ms overlaps4432.672266ms of device activity: long CPU API duration includes waiting for GPU work, not standalone copy time. Graph launch union41.5991ms overlaps40.747978ms of device activity;200discount HtoD API calls total2.045ms and overlap1.435301ms. These observations do not justify reviving E044pinned discounts or treating API waits as removable delay.

Init APIs include primary-context retain81.6195ms,pinned host allocation50.7220ms,5stream synchronizations49.3012ms and57HtoDAPIcalls31.7769ms. These are instrumented observations, not candidate gains or universal bias bounds. Large CPU intervals outside API/device records motivate finer constructor CPU-stage profiling before editing initialization algorithms. Prior D012/D019/E049counterevidence remains applicable; no context/encoder/zero-metadata rescue is admitted by aggregate gaps alone.

185check root replay {old.sha(R/'report.json')} redecodes all raw intervals, perAPI overlap/count/returns, graph joins, full states/checkpoints and three observer clocks. Cohort report {old.sha(H/'cohort-report.json')};{p['http_byte_verified_files']}files HTTPbyteverified including full traces/source/failure evidence. Root replay is not external independent review. Scope is this rainbow workload and warm-driver protocol; API/device times overlap and are not removable headroom or full-cycle gains. AcceptedE051/main/live/PTX and accepted cumulative12.4372274192%remain unchanged; goal active.
'''
nl=b'\r\n' if b'\r\n' in data else b'\n';ledger.write_bytes(data+text.encode('utf-8').replace(b'\n',nl));old.custody()
old.save(R/'checkpoint.json',{'at':old.now(),'previous_goal_turn':'progress: E054 full resource/raw/primary rejection preserved and committed','current_goal_turn':'progress: D087 retained-gap analysis and new low-overhead driver/phase diagnostic fully measured and replayed','goal_active':True,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'owned_sessions_terminal':[6995,46779],'all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True,'next':'Measure CPU constructor stage contributions on accepted E051 before selecting a new optimization. No graph/discount/context/encoder/metadata variant rescue from aggregate intervals alone.','report_sha256':old.sha(R/'report.json')})
for src in [R/'checkpoint.json',H/'cohort-execution/terminal.json',Path(__file__)]:
 key=R.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;assert not dst.exists();dst.write_bytes(src.read_bytes());assert urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15).read()==src.read_bytes()
print(json.dumps({'ledger_sha256':old.sha(ledger),'root_report_sha256':old.sha(R/'report.json'),'owned_children_active':False}),flush=True)
