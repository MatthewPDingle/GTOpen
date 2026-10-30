"""Assess the one fixed evaluation envelope diagnostic; no timing-based extension or acceptance."""
import collections, hashlib, json, math, re, statistics, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
HERE=Path(__file__).resolve().parent
OUT=ROOT/'comparisons/D057-evaluation-envelope-diagnostic'
artifacts={};checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(condition,label):
    if not condition:raise AssertionError(label)
    checks.append(label)
def artifact(path,expected=None):
    path=Path(path);actual=sha(path)
    if expected is not None:need(actual==expected,'pin '+str(path))
    artifacts[str(path)]=actual
    return actual
def read(path,expected=None):artifact(path,expected);return json.loads(Path(path).read_text(encoding='utf-8'))
def markers(text,prefix):return [json.loads(line.split(prefix,1)[1]) for line in text.splitlines() if prefix in line]
def write(name,value):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as f:
        f.write(value if isinstance(value,str) else json.dumps(value,indent=2,allow_nan=False)+'\n')
def finite(value):return isinstance(value,(float,int)) and not isinstance(value,bool) and math.isfinite(value) and value>=0
def stats(values):return {'samples':values,'median':statistics.median(values),'min':min(values),'max':max(values)}

def assess():
    need(len(sys.argv)==2,'root authorization SHA argument')
    auth=read(HERE/'authorization.json',sys.argv[1])
    need(auth['candidate']=='D057' and all(auth[k] is True for k in ['E020_accepted','E020_server_qualification_pass','independent_source_review_pass','independent_script_review_pass']),'registered source/script prerequisites')
    seal=read(HERE/'scripts-manifest.json',auth['evidence_sha256'][str(HERE/'scripts-manifest.json')])
    need(seal['status']=='FROZEN_PROSPECTIVE_NOT_EXECUTED','prospective seal')
    for path,h in auth['evidence_sha256'].items():artifact(path,h)
    for path,h in seal['script_sha256'].items():artifact(HERE/path,h)
    for path,h in seal['reference_sha256'].items():artifact(path,h)
    protocol=read(HERE/'protocol.json','PENDING_PROTOCOL_SHA256')
    source=read(HERE/'source/source-manifest.json')
    for name,h in source['artifact_sha256'].items():artifact(HERE/'source'/name,h)
    report=read(ROOT/'runs/D057R1/report.json')
    raw_path=ROOT/'runs/D057R1/stdout.log';artifact(raw_path,report['stdout_sha256'])
    raw=raw_path.read_text(encoding='utf-8')
    records=markers(raw,protocol['marker']);write('parsed-records.json',records)
    build_exit=read(ROOT/'runs/D057-build/exit.json')
    execution=read(ROOT/'runs/D057-execution/invocation.json')
    execution_exit=read(ROOT/'runs/D057-execution/exit.json')
    execution_complete=read(ROOT/'runs/D057-execution/complete.json')
    for name in ['stdout.log','stderr.log']:artifact(ROOT/'runs/D057-execution'/name)
    need(build_exit['returncode']==execution_exit['returncode']==report['returncode']==0,'build and native terminal success')
    need(execution_exit['error'] is None and execution_exit['cleanup'] is None,'no interrupted native process')
    need(report['id']=='D057R1' and report['kind']=='diagnostic' and report['fixture']=='two-tone' and report['status']=='measured' and report['test_pass_count']==1 and report['accepted'] is False,'exact one diagnostic and no acceptance')
    need(execution_complete['actual_run']=='D057R1' and execution_complete['native_test_pass'] and execution_complete['performance_acceptance'] is False,'fixed invocation terminal record')
    need(execution['actual_run']=='D057R1' and execution['logical_dashboard_row']=='D057' and execution['performance_acceptance'] is False,'fixed logical/run identity')
    need(execution['authorization_sha256']==sys.argv[1] and execution['protocol_sha256']==sha(HERE/'protocol.json') and execution['script_sha256']==sha(HERE/'run.py'),'execution sealed inputs')
    need(build_exit['at']<=execution['at']<=report['process_started_at']<=report['finished_at']<=execution_exit['at'],'build before run chronology')
    manifest_path=ROOT/'binaries/D057-solver.manifest.json'
    manifest=read(manifest_path,execution['build_manifest_sha256'])
    need(report['binary_build_manifest']['path']==str(manifest_path) and report['binary_build_manifest']['sha256']==sha(manifest_path) and report['binary_build_manifest']['data']==manifest,'runner embedded manifest identity')
    binary=ROOT/'binaries/D057-solver.exe'
    artifact(binary,manifest['binary_sha256'])
    need(manifest['binary_sha256']==execution['binary_sha256']==report['binary_sha256'],'binary build/run identity')
    need(manifest['candidate']=='D057' and manifest['test_only_append_verified'] and manifest['source_matches_prebuild'],'test-only source scope verified')
    need(manifest['primary_protocol_sha256']==sha(HERE/'protocol.json') and manifest['build_script_sha256']==sha(HERE/'build.py') and manifest['probe_authorization_sha256']==sys.argv[1] and manifest['probe_evidence_sha256']==auth['evidence_sha256'],'build sealed inputs')
    for key,hkey in [('build_log','build_log_sha256'),('build_stderr_log','build_stderr_sha256'),('patch','patch_sha256')]:artifact(manifest[key],manifest[hkey])
    need(manifest['patch_sha256']==sha(HERE/'source/candidate.patch'),'complete archived patch includes new helper')
    before=read(ROOT/'runs/D057-build/source-before.json')
    need(before['source_sha256']==manifest['source_sha256']==execution['source_sha256']==report['provenance']['source_sha256'] and len(before['source_sha256'])==163,'163 build/run source identities exact')
    for name,h in before['source_sha256'].items():artifact(REPO/name,h)
    for value in manifest['source_copies'].values():artifact(value['path'],value['sha256'])
    need(report['command']==[str(binary),protocol['test_filter'],'--nocapture','--test-threads=1','--ignored'],'exact ignored diagnostic invocation')
    need(re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('1','0','0','0','88')],'one executed test and88 filtered')
    need(not any(s in raw for s in ['D057_CLEANUP_ERROR','D057_SOLVER_CLEANUP_ERROR','panicked at','D057 invalid diagnostic']),'no native cleanup/panic error')
    need(not (ROOT/'runs/D057-execution/stderr.log').read_text(encoding='utf-8').strip(),'no orchestration stderr error')
    for key,value in [('RAYON_NUM_THREADS','16'),('POSTFLOP_AUTORESEARCH_PROFILE','0'),('POSTFLOP_AUTORESEARCH_STORAGE','compressed'),('POSTFLOP_AUTORESEARCH_FIXTURE','two-tone')]:need(report['environment'][key]==value,'fixed env '+key)
    for snapshot in ['live_status_before','live_status_at_launch']:
        snap=report[snapshot];need(not snap['/api/status']['gpu'] and not snap['/api/preflop/status']['gpu'] and not snap['/api/reports/status']['running'],'live idle '+snapshot)
    raise NotImplementedError('Draft only: awaiting frozen actual D057 marker schema; no execution authorized')

OUT.mkdir(exist_ok=False)
try:
    result=assess()
except BaseException as error:
    write('report.json',{'id':'D057','status':'invalid','diagnostic_only':True,'error':repr(error),'checks_passed':checks,'artifact_sha256':artifacts,'candidate_accepted':False,'deployment_changed':False,'extension_allowed':False})
    raise
result.update(created_at=datetime.now(timezone.utc).isoformat(),checks_passed=checks,artifact_sha256=artifacts)
write('report.json',result)
write('assessor.py',Path(__file__).read_text(encoding='utf-8'))
write('manifest.json',{'id':'D057-evaluation-envelope-diagnostic','files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file()},'diagnostic_only':True,'candidate_accepted':False})
print(json.dumps({'status':result['status'],'report_sha256':sha(OUT/'report.json'),'performance_accepted':False}))
