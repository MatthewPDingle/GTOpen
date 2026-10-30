"""Shared immutable qualification support. Importing does not execute work."""
import json, math, os, re, shutil, signal, subprocess, sys, time
from pathlib import Path
from types import SimpleNamespace
REPO = Path(r'X:\Dev\GTOpen-gpu-research-20261016')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / 'tools'))
import postflop_autoresearch as ar
import postflop_compare as cmp
import postflop_validate_controls as vc
ROOT = ar.RESEARCH
TIMING = {'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
SUMMARY = re.compile(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;')

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.write('\n')

def check_record(record):
    assert set(record) == {'path','sha256'}, record
    path = Path(record['path'])
    assert ar.sha256(path) == record['sha256'], str(path)
    return read(path)

def initialize(auth_sha):
    global AUTH, PROTOCOL, SOURCES, PINS
    ap = HERE / 'authorization.json'
    assert ar.sha256(ap) == auth_sha
    AUTH = read(ap)
    assert AUTH['candidate'] == 'E020'
    for flag in ('primary_independent_pass','source_review_pass','qualification_script_review_pass'):
        assert AUTH[flag] is True, flag
    prepared = HERE / 'prepared-manifest.json'
    assert ar.sha256(prepared) == AUTH['prepared_manifest_sha256']
    for name, sha in read(prepared)['artifact_sha256'].items():
        assert ar.sha256(HERE / name) == sha, name
    for path, sha in AUTH['evidence_sha256'].items():
        assert ar.sha256(Path(path)) == sha, path
    assert AUTH['evidence_sha256'], 'Pin independent reviews'
    PROTOCOL = read(HERE/'protocol.json')
    SOURCES = read(HERE/'primary-source.json')
    PINS = read(HERE/'input-pins.json')
    for path,sha in PINS.items():
        assert ar.sha256(Path(path)) == sha, path
    primary = read(ROOT/'comparisons/E020-three-pair-comparison/report.json')
    assert primary['decision'] == 'qualifying' and not cmp.rejection_reasons(primary['performance'])
    unit=read(ROOT/'runs/V020-unit/report.json')
    raw=(ROOT/'runs/V020-unit/stdout.log').read_text(encoding='utf-8')
    assert unit['status']=='measured' and unit['returncode']==0
    assert SUMMARY.findall(raw)==[('84','0','4','0','0')]
    verify_source()
    def interrupted(signum, frame):
        raise InterruptedError(f'Signal {signum}')
    for name in ('SIGTERM','SIGBREAK'):
        if hasattr(signal,name): signal.signal(getattr(signal,name),interrupted)
    return PROTOCOL

def verify_source():
    assert ar.source_identity()['source_sha256'] == SOURCES, 'Checkout differs from frozen E020 primary source'
    for key in ('baseline-complete','E020-postflop_autoresearch','E020-solver'):
        for suffix in ('.exe','.manifest.json'):
            p=ROOT/'binaries'/(key+suffix)
            assert ar.sha256(p)==PINS[str(p)], str(p)

def disk_check():
    q=PROTOCOL['resource_policy']
    assert shutil.disk_usage(ROOT).free >= q['disk_reserve_bytes']+q['output_reservation_bytes']

def require_unused(ids):
    status=read(ar.STATUS)
    assert len(ids)==len(set(ids))
    for identity in ids:
        assert not (ROOT/'runs'/identity).exists(), identity
        assert not any(row.get('id')==identity for row in status['experiments']), identity

def binary_pair(name):
    bp=ROOT/'binaries'/(name+'.exe'); mp=bp.with_suffix('.manifest.json'); m=read(mp)
    assert ar.sha256(bp)==m['binary_sha256'], name
    if name.startswith('E020-'):
        assert m['source_sha256']==SOURCES, name
    else:
        assert name=='baseline-complete'
        assert ar.sha256(mp)==PINS[str(mp)] and ar.sha256(bp)==PINS[str(bp)]
    return bp,mp,{'binary_sha256':ar.sha256(bp),'manifest_sha256':ar.sha256(mp)}

def verify_binary_pins(pins):
    for name, pin in pins.items():assert binary_pair(name)[2]==pin, name

def build_ready(sha):
    path=HERE/'all-builds-ready.json';assert ar.sha256(path)==sha
    ready=read(path)
    assert ready['all_required_builds_terminal'] is True and ready['all_builds_terminal'] is True and ready['holdout_builds_terminal'] is True
    complete=check_record(ready['broader_build_complete'])
    assert Path(ready['broader_build_complete']['path'])==ROOT/'runs/E020-qualification-build/complete.json'
    assert complete['status']=='pass' and complete['source_sha256']==SOURCES
    verify_binary_pins(complete['binary_pins'])
    assert len(complete['binary_pins'])==7
    artifacts=ready['artifacts']
    required={name+'.exe' for name in complete['binary_pins']}|{'E015-holdout.exe','E020-holdout.exe','E015-resource.exe'}
    assert {Path(k).name for k in artifacts if k.endswith('.exe')}==required
    for path,expected in artifacts.items():assert ar.sha256(Path(path))==expected,path
    for path in artifacts:
        if path.endswith('.exe'):
            manifest=Path(path).with_suffix('.manifest.json')
            assert str(manifest) in artifacts and read(manifest)['binary_sha256']==artifacts[path]
    assert ready['holdout_build_source_review_pass'] is True
    assert not (ROOT/'gpu-run.lock').exists(), 'A build/GPU owner remains active'
    return ready,complete

def process(command, out, env, timeout):
    """Caller must retain gpu-run.lock until this returns/raises and cleanup finishes."""
    out=Path(out); out.mkdir(exist_ok=False)
    save(out/'invocation.json',{'at':ar.now(),'command':command,'cwd':str(REPO),
          'CARGO_TARGET_DIR':env.get('CARGO_TARGET_DIR'),'RAYON_NUM_THREADS':env.get('RAYON_NUM_THREADS')})
    proc=None;error=None;cleanup=None;start=time.monotonic()
    try:
        with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
            proc=subprocess.Popen(command,cwd=REPO,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            while True:
                try:
                    result=proc.wait(timeout=min(10,max(.1,timeout-(time.monotonic()-start))))
                    break
                except subprocess.TimeoutExpired:
                    if time.monotonic()-start>=timeout:raise TimeoutError(f'Command exceeded {timeout}s')
                    try: print('Still running:',command[:5],flush=True)
                    except Exception: pass
        assert result==0, str(out/'stderr.log')
        return out/'stdout.log',out/'stderr.log'
    except BaseException as exc:
        error=repr(exc);cleanup=ar.cleanup_child(proc);raise
    finally:
        save(out/'exit.json',{'at':ar.now(),'returncode':None if proc is None else proc.returncode,'error':error,'cleanup':cleanup})

def native(row, pins):
    verify_source();verify_binary_pins(pins)
    bp,mp,_=binary_pair(row['binary'])
    env_before={key:os.environ.get(key) for key in ('RAYON_NUM_THREADS','POSTFLOP_AUTORESEARCH_STORAGE','POSTFLOP_AUTORESEARCH_PROFILE','POSTFLOP_AUTORESEARCH_FIXTURE','GTO_SSD_STUDY_DIR')}
    os.environ.update(RAYON_NUM_THREADS='16',POSTFLOP_AUTORESEARCH_STORAGE=row['storage'],POSTFLOP_AUTORESEARCH_PROFILE='0')
    os.environ.pop('POSTFLOP_AUTORESEARCH_FIXTURE',None)
    if row['id']=='V020-continuation-stored':os.environ['GTO_SSD_STUDY_DIR']=PROTOCOL['stored_directory']
    else:os.environ.pop('GTO_SSD_STUDY_DIR',None)
    try:
        with ar.exclusive_lock(ROOT/'gpu-run.lock'):
            disk_check();ar.refuse_active(ar.live_status());require_unused([row['id']]);verify_source();verify_binary_pins(pins)
            d=ROOT/'runs'/row['id'];d.mkdir(exist_ok=False)
            args=SimpleNamespace(id=row['id'],title='E020 broader qualification',kind=row.get('kind','validation'),binary=bp,build_manifest=mp,test=row['test'],not_ignored=row['ordinary'],fixture=None)
            # Reuse the unchanged runner in-process so it owns/cleans its native child while our lock is held.
            assert ar.run(args,d)==0,row['id']
            verify_source();verify_binary_pins(pins)
    finally:
        for key,value in env_before.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value
    return verify_run(row)

def verify_run(row):
    d=ROOT/'runs'/row['id']; report=read(d/'report.json');raw=(d/'stdout.log').read_text(encoding='utf-8')
    assert report['id']==row['id'] and report['status']=='measured' and report['returncode']==0
    assert report['test_pass_count']==row['passes']
    bp,mp,pin=binary_pair(row['binary']);bm=report['binary_build_manifest']
    assert report['binary_sha256']==pin['binary_sha256'] and bm['sha256']==pin['manifest_sha256']
    assert bm['binary_hash_verified'] is True and bm['data']==read(mp)
    assert Path(report['command'][0])==bp
    expected=[] if row['test']=='*' else [row['test']]
    expected+=['--nocapture','--test-threads=1']+([] if row['ordinary'] else ['--ignored'])
    assert report['command'][1:]==expected
    assert ar.sha256(d/'stdout.log')==report['stdout_sha256']
    summaries=SUMMARY.findall(raw);assert len(summaries)==1
    passed,failed,ignored,measured,filtered=map(int,summaries[0])
    assert (passed,failed,ignored,measured)==(row['passes'],0,0,0)
    if row['test']=='*' or not row['ordinary']:assert filtered==0
    if row['test']!='*':assert re.search(r'^test '+re.escape(row['test'])+r' \.\.\.',raw,re.M)
    env=report['environment'];assert env['RAYON_NUM_THREADS']=='16' and env['POSTFLOP_AUTORESEARCH_STORAGE']==row['storage'] and env['POSTFLOP_AUTORESEARCH_PROFILE']=='0' and env['POSTFLOP_AUTORESEARCH_FIXTURE'] is None
    return report,raw

def results_exact(report, raw, storage):
    results=[json.loads(line.split('AUTORESEARCH_RESULT ',1)[1]) for line in raw.splitlines() if 'AUTORESEARCH_RESULT ' in line]
    assert results==report['results'] and [r['fixture_id'] for r in results]==list(cmp.FIXTURES)
    hashes=cmp.source_hashes(report['binary_build_manifest']['data'])
    for f in cmp.EVALUATOR_FILES:assert hashes[f]==SOURCES[f]==report['provenance']['benchmark_sha256'][f]
    for r in results:
        assert r['storage']==storage and r['target_met'] is True and r['target_pct']==.3 and r['check_every']==20 and r['max_iterations']==400
        assert math.isfinite(r['exploit_chips']) and math.isfinite(r['exploit_pct_pot'])
    return [{k:v for k,v in r.items() if k not in TIMING} for r in results]

def evidence(identity):
    d=ROOT/'runs'/identity
    return {str(f):ar.sha256(f) for f in (d/'report.json',d/'stdout.log')}
