"""Prepare, but do not run, the fixed E072 primary controller during compile."""
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');reference=R/'runs/E071-freeze-run-publish.py';target=R/'runs/E072-freeze-run-publish.py';assert not target.exists()
code=reference.read_text(encoding='utf-8').replace('E071','E072').replace('e071','e072')
for a,b in [('B229','B232'),('B230','B233'),('B231','B234')]:code=code.replace(a,b)
old="control['status']=='pass_all53_CPU_fields_and_capacities'and len(control['cases'])==12 and control['all53_fields_exact']and control['all_capacities_exact']"
new="control['status']=='pass_scoped_full_fold_raw_equivalence' and control['cases']==360 and control['application_kernel_launches']==720 and control['all_owned_children_terminal'] and control['source_main_live_PTX_custody_pass']"
assert code.count(old)==1;code=code.replace(old,new)
old="control['status']=='pass_all53_CPU_fields_and_capacities' and len(control['cases'])==12 and control['all53_fields_exact'] and control['all_capacities_exact']"
assert code.count(old)==1;code=code.replace(old,new)
code=code.replace('runs/D115-parallel-plan-control/report.json','runs/E072-direct-fold/complete.json').replace('runs/D115-parallel-plan-control/protocol.json','runs/E072-direct-fold/protocol.json')
code=code.replace('cpu_control_report','direct_control_report')
old=".replace('import common_e051 as old','import common_e051_live as old')";assert code.count(old)==1;code=code.replace(old,old+".replace('cpu_control_report','direct_control_report')")
start=code.index("source_scope='One two-closure");end=code.index("')\npaths=",start)
scope="One fixed256word fold card-index prefix staged cooperatively in existing reduction scratch. One extra CTA barrier retires every integer consumer before original float reduction stores. Same private/static/dynamic bytes, global payloads, host/plan/ABI/launch/quality/save behavior and other8CUDAentries. Original float expressions/order are source-exact; D117corrects the static count proxy for16versus8unrolling, with the original failed resource report preserved and source unchanged. All360direct GPUoutput/input/guard pairs exact. Complete clocks include NVRTC/JIT, all initialization and readback. No complete-solve or broad/material/holdout/cumulative result yet."
code=code[:start]+"source_scope='"+scope+code[end:]
needle="paths=[Path(__file__),build,d,";assert code.count(needle)==1
code=code.replace(needle,"paths=[Path(__file__),build,d,R/'runs/E072-direct-fold/report.json',R/'runs/D117-fold-PTX-audit/report.json',R/'runs/E072-resource/report.json',")
code=code.replace("'CPU_control_report_sha256':old.sha(d)","'direct_control_report_sha256':old.sha(d)").replace("'CPU_all53_fields_and_capacities_exact':True","'direct_GPU_cases':360,'direct_GPU_launches':720").replace("'CPU_raw_bytes_retained':control['raw_bytes']","'direct_raw_report_sha256':old.sha(R/'runs/E072-direct-fold/report.json')")
code=code.replace('and 12 full CPU plan controls passed.','and 360 direct GPU case pairs passed.').replace('All 53 CPU fields and capacities passed.','All 360 direct GPU case pairs passed.').replace('all added scheduling and setup costs','all runtime compilation, setup and readback costs').replace('branch/threshold/scope variants','cache-width/synchronization/source-scope variants')
start=code.index("entry=f'''");end=code.index("''';nl=",start)+3
entry="""entry=f'''\n\n### E072 fold index staging complete-solve screen\n\nD116source-address and D117static-count audit already recorded. CandidateCUDA{P['candidate_owned_sha256']['crates/solver/src/gpu/kernels.cu']} unchanged from the sole resource probe and360direct GPUcase pairs/720launches; all full output/input/guard bytes exact. The original FPcount-equality failure and parser correction remain explicit; no resource rerun/source/cachewidth/barrier variant. Shared/dynamic/local byte use unchanged; registers39to36, same queried occupancy. No new host/plan/launch/quality/save behavior.\n\nTwo fresh isolated builds; source restored toE051after each. V072unit84passed/4ignored. Fixed B232/E072R1,E072R2/B233,B234/E072R3; all18full non-timing payloads and138quality records exact. Sum fixture median complete-cycle{perf['baseline_full_cycle_ms']:.10f}to{perf['candidate_full_cycle_ms']:.10f}ms, unrounded gain{perf['observed_gain_pct']:.10f}%. Strict fixture guards{json.dumps(perf['fixture_regression_guard'],separators=(',',':'))}. Root{root['checks']}raw/arithmetic checks; assessmentSHA{old.sha(qpath)}. {reason}\n\nNo exclusions,extensions,historical timing pooling or adoption. Fresh16,broadF32/state/menu/save/resume/continuation,actual material CPU/host+GPUpeak/capacity,holdout/cumulative not yet run forE072. Primary arena fingerprints exact; primary full raw arenas not independently byte-compared. All{len(published)}published files HTTP-byteverified; ownedchildren terminal, accepted source/main/live/protectedPTX unchanged. E051accepted and deployed gain12.4372274192%unchanged. LastprimaryB234; goalactive.\n'''"""
code=code[:start]+entry+code[end:]
assert "control['raw_bytes']"not in code and 'D115'in code and 'CPU_all53'not in code
# D115 appears only in the old duplicate-section assertion; make it E072-specific.
code=code.replace("b'### D115 and E072 parallel CPU planner'","b'### E072 fold index staging complete-solve screen'")
assert 'D115'not in code
compile(code,str(target),'exec')
with target.open('x',encoding='utf-8',newline='\n')as out:out.write(code)
print('Prepared E072primary controller; no builds/tests/timings executed.',flush=True)
