import ast,hashlib,json,pathlib
B=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016'); H=B/'runs/D066-fold-zero-census'; R=pathlib.Path(r'X:\Dev\GTOpen-gpu-research-20261016'); O=B/'comparisons/D066-script-review'
pins={}; checks=[]
def ck(v,n):
    assert v,n
    checks.append(n)
def pin(p,h=None):
    p=pathlib.Path(p);v=hashlib.sha256(p.read_bytes()).hexdigest()
    if h is not None:ck(v==h,'sha '+str(p))
    pins[str(p)]=v;return v
def read(p):return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
pin(H/'scripts-manifest.json','f7bf21efd733c81061fed48b2627e643bb19173cedd05fe9f931cb4bf84834fa'); m=read(H/'scripts-manifest.json')
ck(m['status']=='FROZEN_PROSPECTIVE_NOT_EXECUTED','unexecuted prospective seal')
for n,h in m['script_sha256'].items():pin(H/n,h)
for n,h in m['reference_sha256'].items():pin(n,h)
p=read(H/'protocol.json');s=read(H/'source/output-schema.json');sm=read(H/'source/source-manifest.json')
for n in ['build.py','run.py','assess.py']:
    t=(H/n).read_text(encoding='utf-8');ast.parse(t);ck(pins[str(H/'protocol.json')] in t,n+' final protocol literal');ck('PENDING' not in t and 'UNSEALED' not in t,n+' no unresolved placeholders')
ck(p['expected_stage_order']==s['expected_stage_order'] and p['expected_files']==s['expected_files'],'schema order and15files exact')
ck(p['expected_native_summary']==s['native_summary']==dict(passed=1,failed=0,ignored=0,measured=0,filtered_out=88),'exact native summary')
ck(p['candidate_owned_sha256']==sm['candidate_sha256'] and p['source_archive_sha256']==pins[str(H/'source/source-manifest.json')],'candidate source mapping exact')
ck(p['expected_fixtures']==['rainbow','two-tone','river'] and p['expected_stops']==dict(rainbow=200,**{'two-tone':200},river=60),'all fixed fixtures/stops')
ck(p['expected_checkpoint_records']==23 and p['expected_snapshots']==6 and p['expected_reach_array_snapshots']==12 and p['expected_final_full_state_checks']==3,'fixed controls/counts')
ck(p['performance_measurement'] is False and p['performance_acceptance'] is False and p['usefulness_threshold'] is None and p['incidence_threshold'] is None and not p['outcome_triggered_extensions'] and p['exclusions']==[],'incidence only no thresholds/extensions')
for name in ['build_target_root','build_directory','binary','execution_directory','assessment_directory']:ck(not pathlib.Path(p[name]).exists(),'unused '+name)
ck(not (B/'runs/D066R1').exists(),'D066R1 unused')
ck(not (H/'authorization.json').exists(),'separate root authorization not yet issued')
accepted=read(B/'binaries/E020-postflop_autoresearch.manifest.json')['source_sha256'];ck(len(accepted)==162,'accepted162')
for n,h in accepted.items():pin(R/n,h)
for n,v in p['preexisting_target_artifacts'].items():pin(R/n,v['sha256']);ck((R/n).stat().st_size==v['bytes'] and n not in accepted,'exact outside-map PTX '+n)
ck(len(p['preexisting_target_artifacts'])==2,'only two preserved generated artifacts')
source_review=read(B/'comparisons/D066-source-review/report.json');ck(source_review['independent_source_review_pass'] is True and source_review['source_manifest_sha256']==p['source_archive_sha256'],'final independent source review bound')
report={'id':'D066','verdict':'PASS_PROSPECTIVE_DIAGNOSTIC_SCRIPT_REVIEW','independent_script_review_pass':True,'scripts_manifest_sha256':pins[str(H/'scripts-manifest.json')],'protocol_sha256':pins[str(H/'protocol.json')],'source_review_sha256':pins[str(B/'comparisons/D066-source-review/report.json')],'findings':[],
'flow_review':[
'Root authorization must pin accepted/server qualification and independent source/script reports, final script seal and exact two candidate files. Build checks all163 source identities, accepted161 unowned entries, exact test-only append and two specifically pinned generated PTX exceptions.',
'Fresh absent GPU-only Cargo target, compiler-override refusal, serialized live-idle lock, disk bound, bounded child lifetime and owned-child cleanup remain. Fresh solver test artifact features exactly gpu, source/manifest paths and all Cargo artifacts belong to fresh target. Frozen executable contains exact accepted CUDA plus diagnostic marker.',
'One D066R1 ignored-test invocation only, fixed1pass/88filtered. Build must be terminal first; binary/build/source hashes are rechecked before/after. Existing runner supplies GPU lock/live-idle and heartbeat; fixed900second wrapper timeout; failures retain partials. Environment/output directory are explicit and isolated.',
'Assessor pins raw/report/binary/build/patch/activation source provenance and chronology. It requires39 ordered records and exactly15 created files, all23 original/E020 convergence anchors, three complete final fingerprints and native full-store equality flags.',
'Each little-endian20byte mapping record is bounds checked; physical row flags allow all0..7 values and independent category overlap. Opponent q=1-p selection and selected amount exponent bits recompute every CTA and every level without slot-uniqueness assumptions. Word totals remain separate from CTA incidence.',
'Native all-positive-zero/full-pair comparisons, verified actual uploaded metadata and complete-store checks remain source-pinned assertions; compact evidence only replays mapping/row-class incidence. No timing, useful-incidence threshold, speedup claim, retry, extra fixture or production acceptance.'],
'preservation':'Builder draft-r1 AST bracket failure and source draft-r1 context cleanup correction remain sealed. Source reviewer extraction failures are preserved in separate source review. Two exploratory reviewer reads used unavailable draft/old check filenames; no script execution, candidate modification or evidence change occurred.',
'limits':['Read-only source/AST/hash review only; no package script imported or executed, no compiler/native/GPU work.','One-shot runtime correctness and compatibility remain unexecuted and require separate root authorization.','Assessor intentionally requires active163 candidate identities; root restoration follows terminal assessment/custody, not before assessment.','Exact raw float and complete CPU payloads are not retained; FNV is not independently replayable bytewise proof.'],
'checks':checks,'input_sha256':pins,'compiler_native_gpu_executed':False,'execution_authorized':False,'candidate_accepted':False}
(O/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(O/'README.md').write_text('D066 prospective scripts pass independent review. Final seal, exact source/schema, fixed one-run lifecycle and retained compact count parser are bound. No timing or optimization acceptance is inferred. No compiler/native/GPU execution was performed; root execution remains separate.\n',encoding='utf-8')
mm={'id':'D066-script-review','verdict':report['verdict'],'artifact_sha256':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in ['report.json','README.md','review.py']}}
(O/'manifest.json').write_text(json.dumps(mm,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checks':len(checks),'pins':len(pins),'report_sha256':mm['artifact_sha256']['report.json'],'manifest_sha256':hashlib.sha256((O/'manifest.json').read_bytes()).hexdigest()}))
