"""Record the successful scoped profiler and its preserved failures/limits."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D085-cupti-activity';R=ROOT/'comparisons/D085-activity-root-check'
q=old.read(R/'report.json');p=old.read(R/'publication.json');c=old.read(H/'cohort-report.json')
assert q['status']=='pass_scoped_activity_diagnostic' and q['checks_passed']==81 and q['parent_elevated'] is False
assert c['all6full_results_60checkpoints_exact'] and c['observer_usefulness_pass'] and c['excluded_samples']==[] and c['extension_runs']==0 and c['historical_timing_samples_used']==0
assert p['http_byte_verified_files']==122
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';data=ledger.read_bytes();assert b'### D085 explicit CUPTI activity profiling' not in data
text=f'''
### D085 explicit CUPTI activity profiling -- measured diagnostic, no optimization

Refreshed D032: no installed nsys/ncu/nvdisasm/cuobjdump, current Windows token not elevated, current official Nsight Systems guide still requires administrator for Windows CLI. No install, elevation, driver/security/counter change or global environment change. Official CUDA12.9.1 redistributable manifest/checksums downloaded locally: CUPTI12.9.79, cudart12.9.79, nvcc12.9.86 headers only. Archives/licenses retained privately under S:; exact official URLs and archive hashes in bootstrap records.

Built a private MSVC collector around CUPTI Activity API CONCURRENT_KERNEL/MEMCPY/MEMSET. Explicit Start/Flush/Stop while CUDA context remains alive; no injection, detours, exit hooks, PC sampling or hardware counters. Two failed build preparations retained: CMD quoting then absent compiler CRT header; R3 completes without source change. The13-kernel eager+graph ability control verifies13kernels,3graphnodes each4replays, full257word exact output and2guards. Collector drops/errors/bad timestamps/outstanding buffers all0.

The separate copied diagnostic evaluator changes only explicit collector lifecycle hooks (Start inside existing GPU-init clock) and include relocation. Exact immutable E051 solver RLIB linked. Frozen3pairs D085B1/D085T1,D085T2/D085B2,D085B3/D085T3 compare accepted E051 against instrumented rainbow-only solve, compressed/profile0,200iterations/10checks. All6full non-timing results/60checkpoints exact. Each trace contains26,230kernel records, identical family counts and three expected graph groups:63nodes x199,63nodes x199,103nodes x9. No dropped/incomplete/error records.

Predeclared usefulness gate is +/-10%in everypair for complete cycle, native-process and whole-runner walltime. All pass. Complete-cycle changes +0.4474689286%,+0.6672225055%,+1.1588666527%; native process -0.2230897935%,-0.2096143097%,+1.5332676890%; runner -0.5554884676%,-1.8698309959%,+0.2049180327%. All observations retained, no extensions/exclusions/historical timing pooling. This observer-only test grants no optimization acceptance or universal overhead bound.

Median summed traced kernel-time shares: up_action35.6178808310% (5200calls),up_show29.6917218129% (2520),down_action17.1967169751% (5330). Ranking applies to the observed rainbow corpus. Kernel-duration sums may overlap; they are not complete-cycle walltime, removable speed headroom, or a per-family-bias guarantee. This successful activity channel is distinct from the previously rejected high-overhead D033 event observer.

81check root replay {old.sha(R/'report.json')} validates full raw state/clocks/traces/graph counts, collector status and non-elevated execution; cohort report {old.sha(H/'cohort-report.json')}.122evidence files HTTPbyteverified. SDK archives/binaries stay local, with official acquisition/checksum records and collector/build sources available; full custom raw traces published. Root replay is not external independent review. Accepted E051 source/main/live/PTX and cumulative12.4372274192%gain unchanged.

New ranking does not reopen E006/E007 launch-bound/register-cap experiments. Official __maxnreg__ perfunction syntax was checked, but register-cap variants remain closed and no maxnreg prototype or timing was admitted. E054 separately investigates earlier parent-CFV store scheduling under an explicit parent/child nonaliasing contract; it has no accepted performance result at this checkpoint.
'''
nl=b'\r\n' if b'\r\n' in data else b'\n';ledger.write_bytes(data+text.encode('utf-8').replace(b'\n',nl));old.custody()
print(json.dumps({'recorded':'D085','ledger_sha256':old.sha(ledger),'root_report_sha256':old.sha(R/'report.json')}),flush=True)
