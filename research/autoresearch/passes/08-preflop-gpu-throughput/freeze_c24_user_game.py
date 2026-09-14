"""Preserve the stopped game through the save API; never stop/reload/rebuild it."""
import hashlib,json,shutil,time,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[3];APP=Path('T:/Dev/GTOpen')
def api(path,body=None):
    data=None if body is None else json.dumps(body).encode()
    req=urllib.request.Request('http://127.0.0.1:56708/api/'+path,data=data,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=180) as f:return json.load(f)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
receipt=P/'raw/c24-user-fixture.json';assert not receipt.exists()
session=api('preflop/session');status=api('preflop/status');post=api('status');reports=api('reports/status')
assert session['state']==status['state']=='stopped' and session['iteration']==53 and session['nodes']==5704840
assert post['state']!='running' and not reports['running']
root_before=api('preflop/node',{'path':[]})
folder=ROOT/'target/c24-user-fixture';folder.mkdir(exist_ok=False)
name='research-c24-'+time.strftime('%Y%m%d-%H%M%S')
print('Saving stopped preflop game through the normal API',flush=True)
assert api('preflop/save',{'name':name})['ok']
source=APP/'saves/preflop'/f'{name}.gtop';assert source.is_file()
target=folder/'iteration53.gtop';shutil.copyfile(source,target)
checksum=sha(target);assert sha(source)==checksum
assert api('preflop/session')==session and api('preflop/node',{'path':[]})==root_before
assert api('status')==post and api('reports/status')==reports
result=dict(verified=True,name=name,source=str(source),frozen=str(target),sha256=checksum,bytes=target.stat().st_size,
    session=session,status=status,native_budget_mb=23911,expected_batch=4,
    user_state_unchanged=True,scope='Immutable research input; production session remains stopped at its original state.')
receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
(folder/'manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['verified','name','bytes','sha256','user_state_unchanged']}),flush=True)
