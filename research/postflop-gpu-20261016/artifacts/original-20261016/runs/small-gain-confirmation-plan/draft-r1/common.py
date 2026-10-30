"""Dedicated custody helpers reused by the fixed five-build/four-arm confirmation."""
import datetime, hashlib, json, os, re, signal, subprocess, sys, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(REPO/'tools'))
import postflop_autoresearch as ar
import postflop_compare as compare

def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return ar.sha256(Path(p))
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,v):
    p=Path(p); assert not p.exists(),p
    ar.atomic_json(p,v)
def pin(p,h): assert sha(p)==h,str(p)
P=read(HERE/'protocol.json')
S=read(HERE/'schedule.json')
BASE=read(P['accepted_manifest']['path'])['source_sha256']
SOURCE=Path(P['source_package']['path']).parent
BUILD=ROOT/P['build_output']
EXEC=ROOT/P['execution_output']

def verify(auth_hash):
    pin(HERE/'authorization.json',auth_hash)
    a=read(HERE/'authorization.json')
    assert a['id']==P['id'] and a['execute_fixed_package'] is True
    assert a['protocol_sha256']==sha(HERE/'protocol.json')
    pin(HERE/'scripts-manifest.json',a['scripts_manifest_sha256'])
    seal=read(HERE/'scripts-manifest.json')
    assert seal['status']=='FROZEN_PROSPECTIVE_NOT_EXECUTED'
    for n,h in seal['script_sha256'].items():pin(HERE/n,h)
    for n,h in seal['reference_sha256'].items():pin(n,h)
    pin(HERE/'schedule.json',P['schedule_sha256'])
    for key in ['source_package','accepted_manifest','source_review','root_preparation']:
        pin(P[key]['path'],P[key]['sha256'])
    sr=read(P['source_review']['path'])
    assert sr['independent_source_review_pass'] is True
    review=a['script_review'];pin(review['path'],review['sha256'])
    assert read(review['path'])['independent_script_review_pass'] is True
    for n,h in a['evidence_sha256'].items():pin(n,h)
    for n,h in read(P['source_package']['path'])['artifact_sha256'].items():pin(SOURCE/n,h)
    return a

def expected(c):
    return BASE|P['arms'][c]['candidate_owned_sha256']

def custody(c='E020'):
    current=ar.source_identity()['source_sha256']
    assert current==expected(c),(c,'research source drift')
    for n,p in P['preexisting_target_artifacts'].items():
        pin(REPO/n,p['sha256']);assert (REPO/n).stat().st_size==p['bytes']
    main=read(HERE/'protected-main.json');mp=Path(main['root'])
    for n,h in main['source_sha256'].items():pin(mp/n,h)
    for n in main['absent_research_paths']:assert not (mp/n).exists(),n
    pin(main['live_path'],main['live_sha256'])
    changed=subprocess.check_output(['git','diff','--name-only','HEAD','--','crates/solver'],cwd=REPO,text=True).splitlines()
    untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','crates/solver'],cwd=REPO,text=True).splitlines()
    assert set(changed)==set(P['arms'][c]['owned_sources'])
    assert set(untracked)==set(P['preexisting_target_artifacts'])
    return current

def env():
    e=os.environ.copy()
    e.pop('POSTFLOP_AUTORESEARCH_FIXTURE',None)
    e.update(POSTFLOP_AUTORESEARCH_PROFILE='0',POSTFLOP_AUTORESEARCH_STORAGE='compressed',RAYON_NUM_THREADS='16')
    e['PATH']=str(ar.NVRTC)+os.pathsep+e.get('PATH','')
    return e

def child(command,out,label,e,timeout):
    """Caller owns the build lock; ar owns the native-run lock. Never double-lock."""
    out=Path(out);started=now();proc=None;fault=None;cleanup=None
    save(out/(label+'.invocation.json'),{'at':started,'command':command})
    try:
        with (out/(label+'.stdout.log')).open('xb') as stdout,(out/(label+'.stderr.log')).open('xb') as stderr:
            proc=subprocess.Popen(command,cwd=REPO,env=e,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            proc.wait(timeout=timeout)
    except BaseException as error:
        fault=repr(error);cleanup=ar.cleanup_child(proc);raise
    finally:
        save(out/(label+'.exit.json'),{'started_at':started,'finished_at':now(),'command':command,'returncode':proc.returncode if proc else None,'error':fault,'cleanup':cleanup})
    assert proc.returncode==0,(label,(out/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-4000:])

def interrupted(signum,_frame):raise KeyboardInterrupt(f'received signal {signum}')
for sig in [signal.SIGTERM,getattr(signal,'SIGBREAK',None)]:
    if sig is not None:signal.signal(sig,interrupted)

def binaries():
    complete=read(BUILD/'complete.json')
    assert complete['build_order']==P['build_order'] and complete['all_compilers_terminal'] is True
    result={}
    for n,h in complete['evidence_sha256'].items():pin(n,h)
    for c in P['build_order']:
        for name in ['solver','postflop_autoresearch']:
            binary=ROOT/'binaries'/f'SG-{c}-{name}.exe';mp=binary.with_suffix('.manifest.json');m=read(mp)
            pin(binary,m['binary_sha256'])
            assert m['source_sha256']==expected(c)
            assert m['primary_protocol_sha256']==sha(HERE/'protocol.json')
            assert m['build_script_sha256']==sha(HERE/'build.py')
            assert m['cargo_artifact']['features']==['gpu'] and m['cargo_artifact']['fresh'] is False
            assert m['candidate_cuda_present'] is True
            result[(c,name)]={'path':str(binary),'sha256':sha(binary),'manifest':str(mp),'manifest_sha256':sha(mp)}
    return result

EXCLUDED={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
def exact_raw(identity):
    r=read(ROOT/'runs'/identity/'report.json')
    rawpath=ROOT/'runs'/identity/'stdout.log';pin(rawpath,r['stdout_sha256'])
    raw=rawpath.read_text(encoding='utf-8')
    results=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in raw.splitlines() if 'AUTORESEARCH_RESULT ' in x]
    assert results==r['results'] and [x['fixture_id'] for x in results]==P['expected_fixtures']
    assert all(x['iteration']==P['expected_stops'][x['fixture_id']] and x['target_met'] is True for x in results)
    stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in raw.splitlines() if 'AUTORESEARCH_STAGE ' in x]
    checks=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for x in stages if x.get('stage')=='convergence_check']
    assert len(checks)==23
    for f in P['expected_fixtures']:assert [x['iteration'] for x in checks if x['fixture_id']==f]==list(range(20,P['expected_stops'][f]+1,20))
    return ([{k:v for k,v in x.items() if k not in EXCLUDED} for x in results],checks)

def unit_check(c):
    identity=P['arms'][c]['unit_id'];r=read(ROOT/'runs'/identity/'report.json')
    pin(ROOT/'runs'/identity/'stdout.log',r['stdout_sha256'])
    assert r['returncode']==0 and r['status']=='measured'
    inv=P['arms'][c]['unit_inventory'];raw=(ROOT/'runs'/identity/'stdout.log').read_text(encoding='utf-8')
    assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[(str(inv['passed']),'0',str(inv['ignored']),'0','0')]
    for n in P['arms'][c]['focused_tests']:assert re.search(r'(?m)^test '+re.escape(n)+r' \.\.\. ',raw),n
    marker=P['arms'][c]['test_marker']
    if marker:
        records=[json.loads(x.split(marker['prefix'],1)[1]) for x in raw.splitlines() if marker['prefix'] in x]
        assert records==[marker['fields']]
    return r
