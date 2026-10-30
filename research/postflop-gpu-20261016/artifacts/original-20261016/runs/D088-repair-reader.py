"""Correct combined-log parsing and resume the remaining five fixed processes."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D088-cohort';P=old.read(H/'protocol.json');E=H/'execution';f=old.read(E/'failure.json')
assert f['completed_ids']==['D088B1'] and 'FileNotFoundError' in f['error']
assert P['order'][0]=='D088B1' and all(not (ROOT/'runs'/i).exists() for i in P['order'][1:])
r=old.read(ROOT/'runs/D088B1/report.json');receipt=old.read(E/'D088B1.exit.json');assert r['status']=='measured' and r['returncode']==receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None
old.pin(ROOT/'runs/D088B1/stdout.log',r['stdout_sha256']);assert r['binary_sha256']==P['binaries']['baseline']['sha256']
s=(H/'native.py').read_text(encoding='utf-8')
s=s.replace("H/'protocol.json'","H/'protocol-r2.json'").replace("E=H/'execution'","E=H/'execution-r2'")
s=s.replace("(ROOT/'runs'/identity/'stderr.log')","(ROOT/'runs'/identity/'stdout.log')")
s=s.replace("'stderr_sha256':","'marker_log_sha256':").replace("H/'report.json'","H/'report-r2.json'")
needle="  started=time.monotonic();old.child(command,E,identity,env,1200);outer[identity]=(time.monotonic()-started)*1000;old.save(E/(identity+'.outer-wall.json'),{'elapsed_ms':outer[identity]});verify()"
assert s.count(needle)==1
replacement='''  if identity=='D088B1':
   prior=H/'execution'
   for suffix in ['.invocation.json','.exit.json','.outer-wall.json']:
    src=prior/(identity+suffix);dst=E/(identity+suffix);assert not dst.exists();dst.write_bytes(src.read_bytes());assert old.sha(src)==old.sha(dst)
   outer[identity]=old.read(E/(identity+'.outer-wall.json'))['elapsed_ms']
   old.save(E/'carried-baseline.json',{'at':old.now(),'identity':identity,'native_reexecution':False,'original_execution':str(prior),'original_failure_sha256':old.sha(prior/'failure.json'),'report_sha256':old.sha(ROOT/'runs'/identity/'report.json'),'full_raw_log_sha256':old.sha(ROOT/'runs'/identity/'stdout.log'),'reason':'Successful first fixed baseline retained. Reader-only log destination repair; no native outcome excluded/repeated or new sample added.'})
  else:
   started=time.monotonic();old.child(command,E,identity,env,1200);outer[identity]=(time.monotonic()-started)*1000;old.save(E/(identity+'.outer-wall.json'),{'elapsed_ms':outer[identity]})
  verify()'''
s=s.replace(needle,replacement)
assert 'stderr.log' not in s
(H/'native-r2.py').write_text(s,encoding='utf-8',newline='\n')
s=(H/'root-and-publish.py').read_text(encoding='utf-8').replace("H/'protocol.json'","H/'protocol-r2.json'").replace("H/'report.json'","H/'report-r2.json'").replace("E=H/'execution'","E=H/'execution-r2'").replace("stderr=d/'stderr.log'","stderr=d/'stdout.log'").replace("declared['stderr_sha256']","declared['marker_log_sha256']")
assert 'stderr.log' not in s
(H/'root-and-publish-r2.py').write_text(s,encoding='utf-8',newline='\n')
newP=dict(P);newP.update(id='D088-constructor-cohort-r2-reader',at=old.now(),original_protocol_sha256=old.sha(H/'protocol.json'),reader_repair='Read markers from combined stdout/stderr saved by ar. Carry exact successful D088B1 and its native/runner receipts; execute only remaining5original IDs. Same source,binaries,workload,observer gates and cohort.')
paths=[H/'native-r2.py',H/'root-and-publish-r2.py',H/'protocol.json',E/'failure.json',ROOT/'runs/D088B1/report.json',ROOT/'runs/D088B1/stdout.log',E/'D088B1.invocation.json',E/'D088B1.exit.json',E/'D088B1.outer-wall.json',old.REPO/'tools/postflop_autoresearch.py']
newP['input_sha256']=dict(P['input_sha256'])|{str(p):old.sha(p) for p in paths};old.save(H/'protocol-r2.json',newP)
published={}
for src in [H/'native-r2.py',H/'root-and-publish-r2.py',H/'protocol-r2.json',E/'failure.json']:
 key=H.name+'/'+src.relative_to(H).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes());assert urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15).read()==src.read_bytes();published[key]=old.sha(src)
old.save(H/'reader-repair-publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published,'native_reexecution':False})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='D088');e.update(stage='Reader repaired; retain baseline and finish5original runs',reason='First fixed baseline succeeded and is retained unchanged. Reader expected a separate stderr file, while ar combines native stdout/stderr. No source/binary/workload/gate change or extra sample.');e['evidence'].append({'label':'D088 combined-log reader repair and fixed-cohort continuation','url':'evidence/D088-cohort/protocol-r2.json'});st.update(updated_at=old.now(),stage='D088 fixed cohort continuation',activity='Carry successful D088B1 unchanged; run only original remaining5processes with combined-log parsing.');old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol-r2.json'),'first_baseline_retained':True,'remaining_processes':5}),flush=True)
