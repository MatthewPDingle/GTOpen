"""One-shot E020 acceptance publication. Prepared only; root reviews and executes.
Does not run a compiler, test, GPU job, server or deployment. Frozen evidence is read-only.
"""
import hashlib,json,math,shutil,subprocess,sys
from pathlib import Path
PINS = {'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-three-pair-comparison\\report.json': '2ce4a2cd59c29ea4635227fadb265038e7332d295a478d6d8fd36cdac7b025f2', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-cumulative-comparison\\report.json': '573f33d970e11e3a49ec3b386600e7638caf330a874a8878f76dd4659f0badbe', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-broader-qualification\\report.json': 'b3ef310d7d69ae5d05b2d5644e49cc561571d7585aae4d3175d3b6429bcb880b', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-controls-comparison\\report.json': '69fd25c3fe6f28d12120451d00cea7c57ef23a405930b6506292e106d864054c', 'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\E020-wide-turn-holdout-implementation-r2\\cohort\\report.json': '97061633cd79146984c66494d5119aaf628078c47488e2486122dd1d92ee25f4', 'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\E020-main-integration\\report.json': '1c09d01fd4b01122a39b5cc297370c0ddb4b69bae9bf17099682441adf6457c8', 'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\E020-qualification-plan-r3\\qualification-ready.json': '526c3e5d8b5c0b07277acfec09f3f09062c451640462212f015fe9dcce5dbfdb', 'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\E020-qualification-plan-r3\\all-builds-ready.json': '4c53c85b4d7e83915ce31ec93d13a0dc916d8aca5c722441152e10886a6fdda0', 'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\E020-qualification-plan-r3\\authorization.json': 'e935a6b3f29f4de2b44cb7724adc6499119b68afa1934265e218dd76f559c76f', 'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\E020-qualification-plan-r3\\protocol.json': '51f48a84a7dce494eae9d6f06f75a4e78dff654c424a8ac3482d02d551686bb9', 'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\E020-primary-plan\\pre-primary-holdout-freeze.json': '4c9039a562b2ee990f70d2d089ee9bc7e81fed8ac288978ae7fe842970ac8b72', 'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\E020-wide-turn-holdout-plan\\protocol.json': '33d4a047f67d1b23bd125cbfc8c31b564b6cf6a8417da768023beb8389c71510', 'S:\\GTOpen-research\\postflop-gpu-20261016\\binaries\\E020-postflop_autoresearch.exe': 'c4c2c6295c34915ca780dc2ffa3aff400914119bb578d3fc4eaf30ccff409882', 'S:\\GTOpen-research\\postflop-gpu-20261016\\binaries\\E020-postflop_autoresearch.manifest.json': '37bb96c45ecaae02dab11ddfb43d8e46e842dacaed7df8edbad2264b31cb3768', 'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\V020-unit\\stdout.log': 'a3c0c0e74c9565a57b31d4412ea629de149c496373227009dfa4173d1d6c8293', 'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\V020-gpu\\stdout.log': '8089c73a01f6df22f3a7d04960301cc88a6a8c4c4dda73751c8019686491a875', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\D037-independent-review\\validation.json': '15fe1e55029d8f0acf476d73879c8ed41d8800d4bde42002f1b8b1e763a0b825', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\D037-independent-review\\summary.md': '43f77bfa6fa2f5106dc456f97af91f9d3090f0a695411240518d35ddb78f7e10', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\D037-candidate-source-review\\manifest.json': 'd3a2601a509e8c6a1be338ea88aec49779bdb21d275cfb85a85f9ef0782cc3d5', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\D037-candidate-source-review\\review.md': 'e71ba50de427ed136612e977f091cbc7e23098865ae3d5ae2acbfb8936af19dc', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-build-readiness-review\\readiness-r1-invalid.json': '77de1620eeea94bb4221661bdec677c5c7d1bce798bbe52aa314315c4cd79369', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-build-readiness-review\\readiness-r1-invalid.md': '54832648cf5035f59691f588edb053d463e6bd9f88c4e27ddfed34d23277700f', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-build-readiness-review\\readiness-r2-validation.json': '505a129c4a3996aa4bd3ae790cb286448374f2f530e543c6e62b16f1d720b5a8', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-build-readiness-review\\readiness-r2-summary.md': 'd35790c57d7ccc6fc5a263ac1f7d87819ee7e22f2ee417320d46a7fe580c8476', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-build-readiness-review\\primary-and-broader-embedded-cuda.json': 'f6945e25ca7176b7634a8120ad2dd8dc5952961f95de62c4b1ba31fd8384ed6b', 'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\E020-source\\candidate-kernels.cu': '075651690d59ede225c17ff9674662e040d40460a5e2b5436fd6fa7d4f5d663b', 'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\E020-source\\candidate-mod.rs': 'ce71fa3bfb797baade1efe50beba68e971b88c7da1c9547d306e0b6e9245ee8d', 'S:\\GTOpen-research\\postflop-gpu-20261016\\runs\\E020-source\\candidate.patch': 'f0e4e936379b30faf8c743874529f0814902459b719a0c322ad88ceab795e4f6', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-independent-review\\validation.json': 'ee2992d1066faeaf782f5276f7558521990f40a5cfbeece91cade970464fd438', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-independent-review\\summary.md': '174e9859c23f4b7d6a869810593cb75a19bce876e9d4bb5d93208fad09178a66', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-independent-review\\manifest.json': '764ddfd51fc33450f1d179a7933b5380397bd6faa1a6baafe007891d446bb5cc', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-broader-independent-review\\validation.json': '7b5613f4e8871453689ace399246662e8258a257691c91b482e26349dd2c60bd', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-broader-independent-review\\summary.md': 'd0b7539ef867e11fd52d59ee4610a6f803430b0b422927ab8394deb6a7d4c173', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-broader-independent-review\\manifest.json': '467a30f4f38f08983713a2762af461b3f473ffe817d7d67698c77722f9bba17e', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-cumulative-independent-review\\validation.json': '03ec6b6d3ed064ec50f009193d9b28e66078dd6a92507b7122d2fccbdafc8117', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-cumulative-independent-review\\summary.md': 'b32cb9a78c7be66eae256aa97f0746cd36ecad64c330bf97236ad94fe0b8f33c', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-cumulative-independent-review\\manifest.json': 'c84e53a8643e9707e1b71bd9a2191c1b327a29e988c02e580baba711fd3ff12d', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-holdout-independent-review\\validation.json': 'c2d029eacabaf16209cc871a22442ab0460716c5a52c07db9cdbd8ad8530711b', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-holdout-independent-review\\review.md': 'a7a357c9cebfbdc92774f9a88b40ff64b04421c95784ef3f3a8b982e1c36d84a', 'S:\\GTOpen-research\\postflop-gpu-20261016\\comparisons\\E020-holdout-independent-review\\manifest.json': '9d7201571cfc3e82fc73c44f2af044b2fdeac1e33e2a8d41ea313488bff4b413', 'X:\\Dev\\GTOpen-gpu-research-20261016\\tools\\postflop_autoresearch.py': 'd6943a80d80d1cd515e1b83bb9109f5d27d78ce5c9dfc2ce21b16e0e1d188b70'}
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
APP=Path(r'X:\Dev\GTOpen')
OUT=ROOT/'comparisons/E020-qualification'
EXPECTED_COMMITS={'research':'7bac2ac1c2fa8f919dd975e801b2269c25bcd1ff','main':'ae823c8bd6d723c75e096da139fd638d7dd397eb'}
SOURCE={'crates/solver/src/gpu/kernels.cu':'075651690d59ede225c17ff9674662e040d40460a5e2b5436fd6fa7d4f5d663b','crates/solver/src/gpu/mod.rs':'ce71fa3bfb797baade1efe50beba68e971b88c7da1c9547d306e0b6e9245ee8d'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def artifact(p):return {'path':str(p),'sha256':sha(p)}
def check_pins():
 for p,h in PINS.items():assert sha(p)==h,('pinned input changed',p)
def near(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-8)
check_pins()
sys.path.insert(0,str(REPO/'tools'))
import postflop_autoresearch as ar
assert ar.RESEARCH==ROOT and ar.REPO==REPO and ar.APP==APP
primary=read(ROOT/'comparisons/E020-three-pair-comparison/report.json')
cumulative=read(ROOT/'comparisons/E020-cumulative-comparison/report.json')
pr=read(ROOT/'comparisons/E020-independent-review/validation.json')
cr=read(ROOT/'comparisons/E020-cumulative-independent-review/validation.json')
br=read(ROOT/'comparisons/E020-broader-independent-review/validation.json')
hr=read(ROOT/'comparisons/E020-holdout-independent-review/validation.json')
broader=read(ROOT/'comparisons/E020-broader-qualification/report.json')
controls=read(ROOT/'comparisons/E020-controls-comparison/report.json')
holdout=read(ROOT/'runs/E020-wide-turn-holdout-implementation-r2/cohort/report.json')
ready=read(ROOT/'runs/E020-qualification-plan-r3/qualification-ready.json')
integration=read(ROOT/'runs/E020-main-integration/report.json')
manifest=read(ROOT/'binaries/E020-postflop_autoresearch.manifest.json')
full_source=manifest['source_sha256'];assert len(full_source)==162
compiled_shared={k:v for k,v in full_source.items() if k.startswith('crates/solver/src/') or k in ('Cargo.toml','Cargo.lock','crates/solver/Cargo.toml')}
def source_custody():
 commits={}
 for name,root in [('research',REPO),('main',APP)]:
  commits[name]=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
  assert commits[name]==EXPECTED_COMMITS[name],('unexpected commit',name,commits[name])
  for rel,h in compiled_shared.items():assert sha(root/rel)==h,('compiled source changed',name,rel)
  for rel,h in SOURCE.items():
   assert sha(root/rel)==h
   assert hashlib.sha256(subprocess.check_output(['git','show','HEAD:'+rel],cwd=root)).hexdigest()==h,('candidate not committed',name,rel)
 assert integration['research_commit']==commits['research'] and integration['main_after']==commits['main'] and not integration['live_deployment']
 return commits
commits=source_custody()
assert {k:full_source[k] for k in SOURCE}==SOURCE
assert manifest['binary_sha256']==sha(ROOT/'binaries/E020-postflop_autoresearch.exe')=='c4c2c6295c34915ca780dc2ffa3aff400914119bb578d3fc4eaf30ccff409882'
for report in (primary,cumulative):
 perf=report['performance'];assert report['decision']=='qualifying' and not report['accepted'] and not report['deployed']
 assert perf['aggregate_gate_met'] and perf['required_gain_pct']==2 and perf['observed_gain_pct']>=2
 assert not perf['fixture_regression_guard']['failed'] and not report['excluded_runs'] and len(report['pairs'])==3
 assert [f['fixture_id'] for f in report['fixtures']]==['rainbow','two-tone','river']
 assert all(f['exact_screen']['status']=='pass' for f in report['fixtures'])
 assert not perf['statistical_significance_established']
assert primary['cohorts']['baseline']['run_ids']==['B062','B063','B064'] and primary['cohorts']['candidate']['run_ids']==['E020R1','E020R2','E020R3']
assert cumulative['cohorts']['baseline']['run_ids']==['B065','B066','B067'] and cumulative['cohorts']['candidate']['run_ids']==['E020C1','E020C2','E020C3']
assert pr['verdict']=='CONFIRMED_PROVISIONAL_QUALIFYING' and pr['all18_complete_non_timing_results_exact'] and pr['all_convergence_trajectories_exact']
assert cr['verdict']=='PASS_REGISTERED_CUMULATIVE_GATE' and cr['complete_results_exact']==18 and cr['convergence_records_exact']==138 and cr['all_raw_stages_exact']==222 and cr['aggregate_gate'] and not cr['fixture_guard_failed']
assert near(cr['gain_pct'],10.379845449201355) and near(cr['gain_pct'],cumulative['performance']['observed_gain_pct'])
assert near(primary['performance']['observed_gain_pct'],2.2141234232789055)
assert br['verdict']=='PASS_SCOPED_BROADER_CORRECTNESS' and br['nine_runs_terminal_and_fixed_order'] and br['original_snapshots_each']==160 and br['F32_fixtures']==3 and br['F32_all_nontiming_and_stage_trajectories_exact']
assert len(br['GPU_test_names'])==6 and br['continuation']['selected_tests']==3 and br['continuation']['paging_sweeps']==160 and br['continuation']['stored_full_state_passes']==720
assert broader['status']=='pass' and broader['error'] is None and (broader['original_snapshots'],broader['f32_fixtures'],broader['gpu_tests'],broader['continuation_tests'])==(160,3,6,3)
assert controls['status']=='pass' and controls['total_snapshots_each']==160
assert hr['verdict']=='PASS_HOLDOUT_NONREGRESSION_ONLY' and hr['resource_feasible'] and hr['all_six_raw_files_byte_equal_to_B1'] and hr['all_six_complete_non_timing_results_exact'] and hr['all_six_convergence_trajectories_exact'] and not hr['repeatable_regression']
assert holdout['status']=='pass' and not holdout['repeatable_regression'] and not holdout['candidate_accepted'] and not holdout['deployment_changed']
assert all(ready[k] for k in ('broader_pass','holdout_pass','independent_broader_review_pass','independent_holdout_review_pass'))
for p,h in ready['evidence_sha256'].items():assert sha(p)==h
assert read(ROOT/'comparisons/D037-independent-review/validation.json')['resource_probe_pass']
assert read(ROOT/'comparisons/D037-candidate-source-review/manifest.json')['verdict']=='PASS_SOURCE_ONLY'
assert read(ROOT/'comparisons/E020-build-readiness-review/readiness-r2-validation.json')['verdict']=='PASS_BUILD_AND_SOURCE_IDENTITY_ONLY'
assert '84 passed; 0 failed; 4 ignored' in (ROOT/'runs/V020-unit/stdout.log').read_text()
assert '6 passed; 0 failed; 0 ignored' in (ROOT/'runs/V020-gpu/stdout.log').read_text()
river=next(f for f in cumulative['performance']['fixture_regression_guard']['fixtures'] if f['fixture_id']=='river')
assert near(river['median_regression_pct'],0.7128343556410366) and river['repetitions_above_3pct']==1 and river['paired_repetitions']==3 and not river['repeatable_material_regression']
scope=('Registered three-fixture compressed postflop suite on RTX 5090; three alternating fresh-original/candidate pairs, sum of fixture medians. '
       'Tree construction, GPU initialization including runtime NVRTC/JIT, fixed-quality solve/checks and full readback are included. '
       'Cargo compilation, fingerprinting, final destruction, API/browser latency and disk saving are excluded. '
       'Warm-cache observations do not qualify cold-start behavior; no significance, universal tree/range/device or F32-speed claim. '
       'Cumulative gain includes retained E004/E015 plus E020; the separately measured E020 increment is not added to prior percentages.')
links=[('Accepted qualification and tested scope','comparisons/E020-qualification/report.json'),
 ('Fresh original cumulative comparison','comparisons/E020-cumulative-comparison/report.json'),
 ('Incremental comparison against E015','comparisons/E020-three-pair-comparison/report.json'),
 ('Independent cumulative audit','comparisons/E020-cumulative-independent-review/summary.md'),
 ('Independent primary audit','comparisons/E020-independent-review/summary.md'),
 ('Independent broader correctness audit','comparisons/E020-broader-independent-review/summary.md'),
 ('160 original state/menu/resume snapshots','comparisons/E020-controls-comparison/report.json'),
 ('Broader correctness qualification','comparisons/E020-broader-qualification/report.json'),
 ('Independent full-range turn holdout audit','comparisons/E020-holdout-independent-review/review.md'),
 ('Holdout raw-result and non-regression audit','comparisons/E020-holdout-independent-review/validation.json'),
 ('Exact candidate source review','comparisons/D037-candidate-source-review/review.md'),
 ('Resource feasibility audit','comparisons/D037-independent-review/summary.md'),
 ('Preserved invalid R1 holdout build (no native runs)','comparisons/E020-build-readiness-review/readiness-r1-invalid.md'),
 ('Corrected isolated-arm build-readiness audit','comparisons/E020-build-readiness-review/readiness-r2-summary.md'),
 ('84 solver unit tests','runs/V020-unit/stdout.log'),('Six GPU integration tests','runs/V020-gpu/stdout.log')]
def public_path(rel):return 'evidence/'+rel.split('/',1)[1]
evidence=[{'label':label,'url':public_path(rel)} for label,rel in links]
def merge(existing,added):
 # Keep original links/details; the separate acceptance record supersedes their provisional status.
 seen={e['url'] for e in existing};return existing+[e for e in added if e['url'] not in seen]
# Preflight publication paths without writing any evidence or status.
assert not OUT.exists(),('one-shot output exists',str(OUT))
publish={}
for label,rel in links[1:]:publish[ROOT/rel]=ar.DASHBOARD/public_path(rel)
for folder in ['E020-independent-review','E020-cumulative-independent-review','E020-broader-independent-review','E020-holdout-independent-review']:
 for name in ['validation.json','manifest.json']:publish[ROOT/'comparisons'/folder/name]=ar.DASHBOARD/'evidence'/folder/name
for src,dst in publish.items():
 assert str(src) in PINS
 if dst.exists():assert sha(dst)==sha(src),('published evidence differs',str(dst))
assert not (ar.DASHBOARD/'evidence/E020-qualification/report.json').exists()
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 check_pins();assert source_custody()==commits
 status=read(ar.STATUS);assert status['accepted_complete_run']['candidate_id']=='E015'
 assert not any(h['candidate_id']=='E020' for h in status['accepted_history'])
 assert status['deployment']['status']=='blocked' and status.get('active_experiment') is None
 rows=[e for e in status['experiments'] if e['id']=='E020'];assert len(rows)==1 and rows[0]['status']=='qualifying'
 assert {f['id'] for f in status['fixtures']}=={'rainbow','two-tone','river'}
 previous_deployment=status['deployment'];performance=cumulative['performance'];measured=cumulative['created_at'];at=ar.now()
 report={'id':'E020','accepted_at':at,'status':'validated','scope':scope,
  'source_sha256':SOURCE,'binary_source_sha256':full_source,'compiled_shared_source_sha256':compiled_shared,
  'source_map_scope':{'source_sha256':'Exactly two E020 production files; working bytes and committed HEAD blobs verified at research and main.','binary_source_sha256':'Historical immutable primary solver build map of 162 research inputs; research-only tests/docs are not asserted present in main.','compiled_shared_source_sha256':'Cargo manifests/lock and solver src subset verified at both roots. Server files belong to the later server build manifest.'},
  'research_commit':commits['research'],'main_commit':commits['main'],'binary_sha256':manifest['binary_sha256'],
  'performance':performance,'incremental_performance':primary['performance'],'fixtures':cumulative['fixtures'],
  'pairs':cumulative['pairs'],'incremental_pairs':primary['pairs'],'baseline_run_ids':['B065','B066','B067'],'candidate_run_ids':['E020C1','E020C2','E020C3'],
  'correctness':{'status':'pass','primary_complete_results_exact':18,'cumulative_complete_results_exact':18,'cumulative_convergence_checks_exact':138,'original_snapshots_each':160,'f32_fixtures_exact':3,'unit_tests_passed':84,'unit_tests_ignored':4,'gpu_integration_tests_passed':6,'continuation_tests_passed':3,'paging_sweeps':160,'stored_full_state_passes':720},
  'holdout':{'status':'pass','scope':'Prospectively frozen full-range turn holdout, three paired runs; full raw stores/scales and complete non-timing results exact. No primary-score merge.','median_slowdown_pct':hr['median_slowdown_pct'],'paired_slowdown_pct':hr['paired_slowdown_pct'],'repeatable_regression':False,'raw_bytes_per_run':hr['raw_bytes_per_run'],'theoretical_blocks_per_sm':hr['theoretical_blocks_per_sm']},
  'supersedes_provisional_placeholders':{'record_type':'Separate final qualification; frozen primary/cumulative reports remain unchanged.','broader_validation':'pass','f32_storage':'pass','reason':'Their comparison-helper pending/not-run fields describe isolated screens; completed separately pinned qualification gates are authoritative here.'},
  'preserved_failure':{'record':artifact(ROOT/'comparisons/E020-build-readiness-review/readiness-r1-invalid.json'),'summary':'R1 shared Cargo cache produced a wrong-arm holdout binary; refusal occurred before any native holdout execution. Original outputs/readiness preserved invalid; corrected R2 used separate targets and direct linked-CUDA checks. No timing sample was replaced.'},
  'evidence':evidence,'inputs':[{'path':p,'sha256':h} for p,h in PINS.items()],
  'acceptance_script':artifact(Path(__file__)),
  'interpretation':['10.379845% is measured against the original implementation in this fresh cohort; 2.214123% is the separate E020 increment versus E015. Percentages are not added.','River median is 0.712834% slower; only 1 of 3 pairs exceeds 3%, so the unchanged repeated-material-regression guard passes.','Fixed controls and one wide-turn holdout do not establish universal solver accuracy/performance; no significance or cold-start claim.','Continuation tests share candidate kernels internally; immutable original state/F32 comparisons supply the separate original-kernel oracle. Stored testing used unlimited RAM, not forced SSD spill.'],
  'deployed':False,'deployment_status':'blocked','deployment':'Live executable replacement/restart remains blocked by the prior automatic approval review (blocked by policy; no further reason). No live service action is performed by this script.',
  'previous_deployment_record':previous_deployment,'server_validation':{'status':'pending','candidate_id':'E020','summary':'E020 native server build/tests and isolated API smoke remain pending; prior E015 server validation is not an E020 validation.'}}
 accepted={'status':'validated','scope':'complete_run','candidate_id':'E020','baseline_ms':performance['baseline_full_cycle_ms'],'best_ms':performance['candidate_full_cycle_ms'],'observed_gain_pct':performance['observed_gain_pct'],'correctness':'pass','measured_at':measured,'method':scope}
 # Make the complete next status in memory before publishing the new qualification.
 before=json.loads(json.dumps(status))
 status['baseline']={'id':'B065 / B066 / B067','commit':'bad4779b','measured_at':measured,'full_cycle_definition':scope}
 status['accepted_complete_run']=accepted;status['accepted_history'].append({**accepted,'at':at})
 status['validation']={'status':'pass','candidate_id':'E020','summary':'Both compressed cohorts exact; 160 original state/menu/resume snapshots, 3 F32 fixtures, 84 unit tests, 6 GPU tests and 3 continuation tests passed. Full-range turn holdout raw states exact and non-regression guard passed. E020 server validation pending.'}
 status['deployment']={'status':'blocked','candidate_id':'E020','commit':commits['main'],'summary':'Automatic approval review previously rejected live executable replacement/restart: blocked by policy (no further reason). E020 main source is integrated; E020 server build/tests and isolated API validation pending. No live deployment performed.'}
 status['server_validation']=report['server_validation']
 for fixture in status['fixtures']:
  item=next(f for f in cumulative['fixtures'] if f['fixture_id']==fixture['id']);guard=next(f for f in performance['fixture_regression_guard']['fixtures'] if f['fixture_id']==fixture['id']);fp=item['exact_screen']['fingerprint']
  fixture['baseline']={'full_cycle_ms':item['baseline']['full_cycle_ms']['median_ms'],'solve_ms':item['baseline']['solve_ms']['median_ms'],'fingerprint':fp,'repetitions':3,'provisional':False}
  fixture['best']={'status':'accepted','candidate_id':'E020','full_cycle_ms':item['candidate']['full_cycle_ms']['median_ms'],'solve_ms':item['candidate']['solve_ms']['median_ms'],'fingerprint':fp,'median_regression_pct':guard['median_regression_pct'],'guard_passed':not guard['repeatable_material_regression']}
  fixture['correctness']={'status':'pass','details':'Complete non-timing states/settings/stops exact; separate original F32/state controls and full-range turn holdout passed. '+guard['reason']}
  fixture['evidence']=merge(fixture['evidence'],evidence[:10])
 row=rows[0];row.update(status='accepted',correctness='pass',stage='Accepted for registered corpus; E020 server validation pending',updated_at=at,full_cycle_ms=performance['candidate_full_cycle_ms'],baseline_full_cycle_ms=performance['baseline_full_cycle_ms'],solve_ms=sum(f['candidate']['solve_ms']['median_ms'] for f in cumulative['fixtures']),timing_aggregation='Fresh-original three-pair sum of per-fixture medians; all fixed samples retained',reason='Accepted 2.2141% incremental gain versus E015; fresh-original cumulative 10.3798% complete-cycle reduction. All accuracy/holdout gates passed. River median 0.7128% slower, repeated-regression guard passes. Main source integrated; E020 server validation pending and live deployment blocked.')
 row['details']='Registered compressed corpus on RTX 5090: 10.3798% aggregate reduction; no universal or cold-start claim. Separate wide-turn holdout passed; no score merging. River slowdown retained and disclosed.'
 row['qualification_summary']={'id':'E020-qualification','status':'validated','performance':performance,'incremental_performance':primary['performance'],'broader_validation':'pass','f32_storage':'pass','controls_snapshots_each':160,'wide_turn_holdout':'pass','server_validation':'pending','deployment':'blocked'}
 row['evidence']=merge(row['evidence'],evidence);status['evidence']=merge(status['evidence'],evidence)
 status['state']='running';status['stage']='E020 accepted; isolated server validation pending';status['activity']='Accepted 10.3798% lower complete-cycle time on the registered corpus, with exact tested-state results. Preparing E020 server validation; live deployment remains blocked.';status['updated_at']=at
 OUT.mkdir(exist_ok=False)
 ar.atomic_json(OUT/'status-before.json',before);ar.atomic_json(OUT/'report.json',report)
 for src,dst in publish.items():
  dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists():shutil.copyfile(src,dst)
  assert sha(dst)==sha(src)
 target=ar.DASHBOARD/'evidence/E020-qualification/report.json';target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();shutil.copyfile(OUT/'report.json',target)
 ar.atomic_json(ar.STATUS,status);ar.atomic_json(OUT/'status-after.json',status)
 ar.atomic_json(OUT/'publication.json',{'at':ar.now(),'status':'complete','qualification':artifact(OUT/'report.json'),'dashboard_qualification':artifact(target),'status_after':artifact(OUT/'status-after.json'),'frozen_reports_unchanged':all(sha(p)==h for p,h in PINS.items()),'deployed':False})
print(json.dumps({'accepted':'E020','cumulative_gain_pct':performance['observed_gain_pct'],'incremental_gain_pct':primary['performance']['observed_gain_pct'],'qualification_sha256':sha(OUT/'report.json'),'server_validation':'pending','deployment':'blocked'}))
