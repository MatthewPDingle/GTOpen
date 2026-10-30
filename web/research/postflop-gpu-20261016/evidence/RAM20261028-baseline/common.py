import datetime,hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EPOCH=ROOT/'epoch'
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(REPO/'tools'))
import postflop_autoresearch as ar
ar.RESEARCH=ROOT
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return ar.sha256(Path(p))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,v):
 p=Path(p);assert not p.exists(),p
 ar.atomic_json(p,v)
def pin(p,h):assert sha(p)==h,str(p)
def custody():
 base=read(EPOCH/'accepted-source.json')['source_sha256']
 assert ar.source_identity()['source_sha256']==base
 m=read(EPOCH/'protected-main.json');main=Path(m['root'])
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()==m['git_head']
 for n,h in m['source_sha256'].items():pin(main/n,h)
 pin(m['live_path'],m['live_sha256'])
 for n in m['absent_research_paths']:assert not(main/n).exists()
 assert not subprocess.check_output(['git','diff','--name-only','HEAD','--','crates/solver'],cwd=REPO,text=True).strip()
 targets=read(EPOCH/'preexisting-target-artifacts.json')
 for n,v in targets.items():pin(REPO/n,v['sha256']);assert(REPO/n).stat().st_size==v['bytes']
 assert set(subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','crates/solver'],cwd=REPO,text=True).splitlines())==set(targets)
 assert ROOT.drive.upper()=='X:'
 return base
def env():
 e=os.environ.copy();e.pop('POSTFLOP_AUTORESEARCH_FIXTURE',None)
 e.update(RAYON_NUM_THREADS='16',POSTFLOP_AUTORESEARCH_STORAGE='compressed',POSTFLOP_AUTORESEARCH_PROFILE='0',PYTHONIOENCODING='utf-8')
 e['PATH']=str(ar.NVRTC)+os.pathsep+e.get('PATH','')
 return e
def child(command,out,label,timeout=1200):
 out=Path(out);start=now();proc=None;error=None;cleanup=None;clock=time.monotonic()
 save(out/(label+'.invocation.json'),{'at':start,'command':command,'cwd':str(REPO)})
 print('Starting',label,flush=True)
 try:
  with(out/(label+'.stdout.log')).open('xb')as stdout,(out/(label+'.stderr.log')).open('xb')as stderr:
   proc=subprocess.Popen(command,cwd=REPO,env=env(),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
   announced=0
   while True:
    try:proc.wait(timeout=10);break
    except subprocess.TimeoutExpired:
     elapsed=time.monotonic()-clock
     if elapsed>timeout:raise TimeoutError(label)
     if elapsed-announced>=30:print(label,'running;',int(elapsed),'seconds; PID',proc.pid,flush=True);announced=elapsed
 except BaseException as e:error=repr(e);cleanup=ar.cleanup_child(proc);raise
 finally:save(out/(label+'.exit.json'),{'started_at':start,'finished_at':now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup})
 assert proc.returncode==0,(label,(out/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-3000:])
def exact(identity):
 r=read(ROOT/'runs'/identity/'report.json');p=ROOT/'runs'/identity/'stdout.log';pin(p,r['stdout_sha256']);raw=p.read_text(encoding='utf-8')
 results=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1])for x in raw.splitlines()if'AUTORESEARCH_RESULT 'in x]
 assert results==r['results']and[x['fixture_id']for x in results]==['rainbow','two-tone','river']
 stops={'rainbow':200,'two-tone':200,'river':60}
 assert all(x['iteration']==stops[x['fixture_id']]and x['target_met']is True for x in results)
 stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1])for x in raw.splitlines()if'AUTORESEARCH_STAGE 'in x]
 checks=[{k:x[k]for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']}for x in stages if x.get('stage')=='convergence_check']
 assert len(checks)==23
 for f in stops:assert[x['iteration']for x in checks if x['fixture_id']==f]==list(range(20,stops[f]+1,20))
 excluded={'build_ms','fingerprint_ms_excluded','full_cycle_ms','init_ms','readback_ms','solve_ms'}
 return [[{k:v for k,v in x.items()if k not in excluded}for x in results],checks]
