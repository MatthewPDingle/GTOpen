"""Repair a pre-compiler Python import collision; preserve original attempt."""
from pathlib import Path
import shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not(R/'gpu-run.lock').exists()
original=R/'runs/E051-server-final-plan';H=R/'runs/E051-server-final-plan-r2';H.mkdir()
failure=R/'runs/E051-server-final-manager/build-unit.exit.json';f=old.read(failure);assert f['returncode']==1 and f['error'] is None and f['cleanup'] is None
assert 'partially initialized module' in(failure.parent/'build-unit.stderr.log').read_text(encoding='utf-8')
for name in ['E051-server-final-build','V051-server-unit']:assert not(R/'runs'/name).exists()
P=old.read(original/'protocol.json');assert not Path(P['target']).exists()
for src,dest in [('common.py','server_common.py'),('build.py','build.py'),('smoke.py','smoke.py')]:
 code=(original/src).read_text(encoding='utf-8')
 if src!='common.py':
  assert 'import common as c' in code;code=code.replace('import common as c','import server_common as c')
 with(H/dest).open('x',encoding='utf-8',newline='\n')as out:out.write(code)
 compile(code,str(H/dest),'exec')
for name in ['unit-inventory.json','spot-request.json','solve-request.json']:shutil.copyfile(original/name,H/name)
repair={'at':old.now(),'original_protocol_sha256':old.sha(original/'protocol.json'),'original_manager_exit_sha256':old.sha(failure),'cause':'New helper module named common was importing common_e051, which in turn imports historical common. Python reused the partially initialized new module by its common name.','repair':'Rename only the new helper to server_common and update its two imports. Original code and failed native receipt preserved.','compiler_or_unit_or_solver_or_server_processes_started':0,'target_and_output_paths_still_absent':True,'source_inputs_and_build_test_smoke_gates_unchanged':True,'no_performance_samples':True}
old.save(H/'precompiler-import-repair.json',repair)
P.update(at=old.now(),status='FROZEN_PRE_COMPILATION_IMPORT_REPAIR',precompiler_repair=repair)
P['input_sha256']={k:v for k,v in P['input_sha256'].items() if Path(k).parent!=original}
P['input_sha256'].update({str(x):old.sha(x) for x in [Path(__file__),failure,failure.parent/'build-unit.stderr.log',*[H/n for n in ['server_common.py','build.py','smoke.py','unit-inventory.json','spot-request.json','solve-request.json','precompiler-import-repair.json']]]})
old.save(H/'protocol.json',P)
pub=[]
for src in H.iterdir():
 if not src.is_file():continue
 key=H.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(src,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
 pub.append({'url':'evidence/'+key,'sha256':old.sha(src)})
old.save(H/'pre-build-publication.json',{'at':old.now(),'files_http_byte_verified':pub,'protocol_sha256':old.sha(H/'protocol.json'),'native_build_or_unit_or_API_executions':0})
manager=R/'runs/E051-server-final-manager-r2';manager.mkdir();print('E051 server R2 protocol',old.sha(H/'protocol.json'),flush=True)
old.child([sys.executable,'-B',str(H/'build.py'),old.sha(H/'protocol.json')],manager,'build-unit',old.env(),4200)
print('E051 build/unit manager completed',flush=True)
