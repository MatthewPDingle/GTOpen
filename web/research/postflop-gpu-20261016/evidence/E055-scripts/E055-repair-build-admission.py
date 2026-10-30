"""Preserve a no-compiler admission failure and select genuinely fresh targets."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();H=ROOT/'runs/E055-build-plan';P=old.read(H/'build-protocol.json');O=ROOT/'runs/E055-final-build';assert O.exists() and not list(O.iterdir())
assert all('e054' in p['target'] for p in P['phases']) and all(not (ROOT/'binaries'/(n+'.exe')).exists() for p in P['phases'] for n in p['outputs'].values())
old.save(O/'prelaunch-failure.json',{'at':old.now(),'outer_exec_chunk_id':'251074','returncode':1,'failure':'Fresh-target guard found inherited lower-case e054target paths. No compiler/native work or source activation occurred; existing E054artifacts untouched.','original_protocol_sha256':old.sha(H/'build-protocol.json'),'original_targets':[p['target'] for p in P['phases']],'no_compiler_or_native_work':True,'source_main_live_ptx_unchanged':True})
s=(H/'build.py').read_text(encoding='utf-8').replace('build-protocol.json','build-protocol-r2.json').replace("runs/E055-final-build'","runs/E055-final-build-r2'").replace("HERE/'build.py'","HERE/'build-r2.py'")
(H/'build-r2.py').write_text(s,encoding='utf-8',newline='\n')
newP=dict(P);newP.update(id='E055-final-build-r2-admission',at=old.now(),original_protocol_sha256=old.sha(H/'build-protocol.json'),repair='Fresh lower-case e055targets and new final-build-r2evidence directory. Same source,flags,features,outputs and qualification. No compiler outcome or native timing preceded this repair.')
newP['phases']=[{**p,'target':p['target'].replace('e054','e055')} for p in P['phases']]
assert all(not Path(p['target']).exists() for p in newP['phases'])
newP['input_sha256']=dict(P['input_sha256'])|{str(p):old.sha(p) for p in [H/'build-r2.py',H/'build-protocol.json',O/'prelaunch-failure.json']};old.save(H/'build-protocol-r2.json',newP)
s=(ROOT/'runs/E055-freeze-primary.py').read_text(encoding='utf-8').replace('E055-final-build','E055-final-build-r2').replace('E055-build-plan/build-protocol.json','E055-build-plan/build-protocol-r2.json')
needle="text=(prior/name).read_text(encoding='utf-8').replace('E053','E055')";assert s.count(needle)==1
s=s.replace(needle,needle+".replace('E055-final-build','E055-final-build-r2')")
(ROOT/'runs/E055-freeze-primary-r2.py').write_text(s,encoding='utf-8',newline='\n')
for src in [H/'build-r2.py',H/'build-protocol-r2.json',O/'prelaunch-failure.json']:
 key=H.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;assert not dst.exists();dst.write_bytes(src.read_bytes());assert urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15).read()==src.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E055');e.update(stage='Fresh build paths repaired before compiler work',reason='819raw cases exact. Admission caught old e054target paths, preserving old outputs. R2uses fresh e055targets and evidence directory, same source/flags/features/gates.');e['evidence'].append({'label':'E055 preserved admission failure and fresh build protocol','url':'evidence/E055-build-plan/build-protocol-r2.json'});st.update(updated_at=old.now(),stage='E055 fresh integrated builds',activity='Compile exact conditional-read source into fresh targets; no E054output reuse, source/binary/timing change or extra sample.');old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'build_protocol_sha256':old.sha(H/'build-protocol-r2.json'),'targets':[p['target'] for p in newP['phases']]}),flush=True)
