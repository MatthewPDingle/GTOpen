"""Seal the application smoke only after terminal build and unit validation."""
from pathlib import Path
import shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
H=R/'runs/E051-server-final-plan-r2';built=old.read(R/'runs/E051-server-final-build/report.json');assert built['status']=='pass' and built['all_compilers_and_unit_children_terminal']
manager=old.read(R/'runs/E051-server-final-manager-r2/build-unit.exit.json');assert manager['returncode']==0 and manager['error'] is None and manager['cleanup'] is None
unit=R/'runs/V051-server-unit/report.json';u=old.read(unit);assert u['test_pass_count']==20 and u['ignored']==1 and u['all_owned_children_terminal']
original=H/'smoke.py';script=H/'smoke-r2.py';code=original.read_text(encoding='utf-8')
assert code.count("c.LIVE['executable']")==1 and code.count("c.LIVE['sha256']")==1
code=code.replace("c.LIVE['executable']","c.LIVE['path']").replace("c.LIVE['sha256']","c.P['live_sha256']")
needle="c.initialize('smoke',sys.argv[1])";assert code.count(needle)==1
code=code.replace(needle,needle+"\n    for path,h in c.AUTH['input_sha256'].items():c.old.pin(path,h)")
compile(code,str(script),'exec')
with script.open('x',encoding='utf-8',newline='\n')as out:out.write(code)
binary=R/'binaries/E051-gto-server.exe';manifest=binary.with_suffix('.manifest.json');m=old.read(manifest);old.pin(binary,m['binary_sha256'])
assert m['source_sha256']==old.read(H/'protocol.json')['source_sha256']
repair={'at':old.now(),'status':'prospective_guard_schema_alignment_no_server_started','original_smoke_sha256':old.sha(original),'changes':['Guard live path uses the frozen live_identity.path field instead of the historical executable alias.','Guard old binary hash uses the frozen protocol.live_sha256 field instead of a historical live alias.','Verify every new smoke protocol input before any server launch.'],'unchanged':'Original tiny river spot,100iterations,API requests,finite/value/strategy checks,port43736 ownership,cleanup and unchanged live source/process/state checks.','server_launches_before_alignment':0,'performance_samples':0}
old.save(H/'smoke-guard-schema-alignment.json',repair)
inputs=[Path(__file__),script,H/'smoke-guard-schema-alignment.json',H/'protocol.json',R/'runs/E051-server-final-build/report.json',R/'runs/E051-server-final-manager-r2/build-unit.exit.json',unit,unit.parent/'stdout.log',binary,manifest]
P={'id':'E051-isolated-application-smoke','at':old.now(),'candidate':'E051','status':'FROZEN_PRE_SERVER_LAUNCH','acceptance':old.read(H/'protocol.json')['acceptance'],'server_binary_sha256':old.sha(binary),'server_manifest_sha256':old.sha(manifest),'server_unit_report':{'path':str(unit),'sha256':old.sha(unit)},'input_sha256':{str(p):old.sha(p)for p in inputs},'port':43736,'scope':'Isolated API correctness smoke; no measured speed claim, live mutation or deployment.'}
old.save(H/'smoke-protocol.json',P)
pub=[]
for src in [script,H/'smoke-guard-schema-alignment.json',H/'smoke-protocol.json']:
 key=H.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;assert not dst.exists();shutil.copyfile(src,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==src.read_bytes()
 pub.append({'url':'evidence/'+key,'sha256':old.sha(src)})
old.save(H/'pre-smoke-publication.json',{'at':old.now(),'files_http_byte_verified':pub,'server_launches':0,'protocol_sha256':old.sha(H/'smoke-protocol.json')})
O=R/'runs/E051-server-final-smoke-manager';O.mkdir()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);s.update(updated_at=old.now(),state='running',goal_status='active',stage='E051 isolated GPU API smoke',activity='Fresh E051 server and test binaries compiled;20server unit tests passed, one ignored. Launching one owned43736 server for the frozen100iteration tiny river solve. Live43735 remains idle and unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
old.child([sys.executable,'-B',str(script),old.sha(H/'smoke-protocol.json')],O,'smoke',old.env(),300)
report=old.read(R/'runs/E051-server-final-smoke/result.json');assert report['passed'] and report['owned_process_stopped'] and report['test_port_released'] and report['live_api_unchanged']
old.custody();print({'E051_server_smoke':'passed','GPU_iterations':report['final_status']['iteration'],'GPU':report['final_status']['gpu'],'live_unchanged':True},flush=True)
