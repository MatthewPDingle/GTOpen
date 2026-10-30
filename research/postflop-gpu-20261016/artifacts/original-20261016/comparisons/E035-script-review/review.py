from pathlib import Path
import ast,hashlib,json
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016');REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016');PLAN=ROOT/'runs/E035-primary-plan';HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
pins={}
def pin(p,h=None):
 p=Path(p);actual=sha(p)
 if h is not None:assert actual==h,(str(p),actual,h)
 pins[str(p)]=actual
 return actual
sealhash=pin(PLAN/'scripts-manifest.json','a4b09bda1d72111f9df3444737dd76c2a1ed51890a8d0adb256148ab7ec22793')
m=read(PLAN/'scripts-manifest.json');assert m['status']=='FROZEN_PROSPECTIVE_NOT_EXECUTED'
for n,h in m['script_sha256'].items():pin(PLAN/n,h)
for n,h in m['reference_sha256'].items():pin(n,h)
p=read(PLAN/'protocol.json');source=read(ROOT/'runs/E035-design/manifest.json');source_review=read(ROOT/'comparisons/E035-source-review/report.json')
assert source_review['independent_source_review_pass'] is True
assert p['source_archive_sha256']==m['source_manifest_sha256']==source_review['source_manifest_sha256']==sha(ROOT/'runs/E035-design/manifest.json')
assert p['candidate_owned_sha256']==source['candidate_owned_sha256']
assert p['accepted_owned_sha256']==source['accepted_owned_sha256']
assert len(p['changed_accepted_sources'])==2 and p['new_sources']==[] and p['source_entry_count']==162
expected_order=['V035-unit','B110','E035R1','E035R2','B111','B112','E035R3'];assert p['order']==expected_order
assert p['pairs']==[{'baseline':'B110','candidate':'E035R1'},{'baseline':'B111','candidate':'E035R2'},{'baseline':'B112','candidate':'E035R3'}]
assert (p['expected_unit_passed'],p['expected_unit_ignored'])==(85,4)
assert p['expected_new_unit_tests']==source['new_unit_tests']
assert p['focused_unit_marker']=={'prefix':'E035_FOLD_ZERO_TEST ','expected':source['focused_unit_summary']}
assert p['expected_fixtures']==['rainbow','two-tone','river'] and p['expected_stops']=={'rainbow':200,'two-tone':200,'river':60} and p['expected_convergence_records_per_run']==23
parent=read(ROOT/'runs/E034-primary-plan/protocol.json')
for k in ['aggregate_gate','fixture_guard','exactness','exclusions','builds_before_timing','outcome_triggered_extensions','failure_policy','build_command','compile_only_commands','preexisting_target_artifacts']:assert p[k]==parent[k],k
terminal=p['incidence_prerequisite'];pin(terminal['path'],terminal['sha256']);tr=read(terminal['path'])
for k,v in terminal['required_fields'].items():assert tr[k]==v
texts={}
for name in ['compile_check.py','build.py','primary.py','assess.py']:
 text=(PLAN/name).read_text(encoding='utf-8');ast.parse(text);texts[name]=text
 assert sha(PLAN/'protocol.json') in text,name
 assert all(x not in text for x in ['PENDING','UNSEALED','V034-unit','E033_CACHE','cache_policy.rs','D064_terminal_review','E033_failure_cleanup']),name
 assert all(ord(c)>=32 or c in '\n\r\t' for c in text)
for name in ['compile_check.py','build.py']:
 text=texts[name]
 for s in ["with ar.exclusive_lock",'ar.refuse_active(ar.live_status())','assert not target.exists()','subprocess.CREATE_NO_WINDOW','compiler_override_absence',"assert set(tracked) | (set(untracked) - set(preserved)) == set(owned)","assert item['fresh'] is False",'accepted_cuda.read_bytes() not in data'] :assert s in text,(name,s)
assert "item['features']==['gpu']" in texts['build.py']
assert "item['features']==['gpu','preflop-research']" in texts['compile_check.py']
assert 'compile_check_sha256 = verify_compile_check()' in texts['build.py']
assert texts['primary.py'].index("run('V035-unit'") < texts['primary.py'].index("for identity, candidate in [('B110'")
assert "assert records==[marker['expected']]" in texts['primary.py']
assert 'assert checks==reference_checks' in texts['assess.py'] and 'results == run[\'results\']' in texts['assess.py']
assert "excluded_timing = {'build_ms', 'init_ms', 'solve_ms', 'readback_ms', 'full_cycle_ms', 'fingerprint_ms_excluded'}" in texts['assess.py']
accepted=read(ROOT/'binaries/E020-postflop_autoresearch.manifest.json')['source_sha256'];assert len(accepted)==162
for n,h in accepted.items():pin(REPO/n,h)
for n,v in p['preexisting_target_artifacts'].items():pin(REPO/n,v['sha256']);assert (REPO/n).stat().st_size==v['bytes'] and n not in accepted
prep=read(PLAN/'preparation.json')
for path in prep['unused_paths']:assert not Path(path).exists(),path
assert read(PLAN/'draft-r1/protocol.json')['order'][0]=='V034-unit'
assert len(m['script_sha256'])==10 and len(m['reference_sha256'])==47
report={'id':'E035','verdict':'PASS_PROSPECTIVE_SCRIPT_REVIEW','independent_script_review_pass':True,'scripts_manifest_sha256':sealhash,'protocol_sha256':sha(PLAN/'protocol.json'),'source_manifest_sha256':p['source_archive_sha256'],'findings':[],
'checks':[
'All10 package artifacts and47 reference pins verify; four scripts AST-parse without importing or executing them. Current162 accepted E020 source entries are exact, both specifically named PTX exceptions retain exact bytes/size, and every declared target/output/binary/seven-run ID remains absent.',
'Both build stages bind root authorization, exact two changed files, canonical D066 terminal scope/custody audit and independent reviews. Feature lib no-run uses an unused target; separate GPU-only lib/evaluator build uses a different unused target, fresh artifact/source/features/target containment, complete candidate CUDA inclusion and full old CUDA absence. Only the original fold fragment is embedded by the unit.',
'Existing GPU lock/live-idle,54GiB reserve, compiler-environment absence, hidden process launch, bounded waits, owned-process cleanup and terminal error logs remain. No feature native workload is invoked.',
'V035-unit85/0/4/0/0 and named focused test plus exactly one26-pair/52-launch success marker precede the fixed B110/R1,R2/B111,B112/R3 sequence. First stale V034-unit draft is preserved; final order and all script literals are corrected.',
'Every retained complete result is compared in full after only the six declared timing exclusions. All138 convergence records, fixed stopping/target conditions and configurations remain exact requirements. At least2percent aggregate gain and the unchanged conjunctive greater-than3percent fixture guard govern primary qualification.',
'Cache-policy/cleanup marker gates from E034 were removed; D066 establishes incidence only. No rescue, sample replacement, outcome-triggered extension, automatic acceptance or pre-primary broader harness was introduced.'
],
'limits':['Prospective file-only review; no candidate script import, compiler, native test, CUDA or performance execution. Root must separately authorize and activate exact sources.','A passing unit or primary does not constitute adoption. Conditional original/full-state/F32/continuation/wide-turn/cumulative qualification remains mandatory only after primary passes.'],
'input_sha256':pins,'compiler_native_gpu_executed':False,'candidate_accepted':False}
with (HERE/'report.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2);f.write('\n')
manifest={'id':'E035-script-review','artifact_sha256':{n:sha(HERE/n) for n in ['review.py','report.json']},'scripts_manifest_sha256':sealhash}
with (HERE/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(manifest,f,indent=2);f.write('\n')
print(json.dumps({'report':sha(HERE/'report.json'),'manifest':sha(HERE/'manifest.json'),'pins':len(pins)}))