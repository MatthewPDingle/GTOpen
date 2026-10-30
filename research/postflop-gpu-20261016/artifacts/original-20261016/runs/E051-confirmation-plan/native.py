"""E051 fresh16pair complete-cycle confirmation; no adoption."""
import json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
ar=old.ar
read,sha,pin,save,now,child=old.read,old.sha,old.pin,old.save,old.now,old.child
assert len(sys.argv)==2;pin(HERE/'protocol.json',sys.argv[1]);P=read(HERE/'protocol.json')
ROOT=ar.RESEARCH;OUT=ROOT/'runs/E051-confirmation-execution';BASE=read(P['baseline']['path'])['source_sha256']
def verify():
 pin(HERE/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():pin(p,h)
 old.custody()
def binary(stem):
 path=ROOT/'binaries'/(stem+'.exe');mp=path.with_suffix('.manifest.json');m=read(mp)
 pin(path,m['binary_sha256']);assert m['build_protocol_sha256']==P['build_protocol_sha256']
 assert m['source_sha256']==BASE|P['candidate_owned_sha256']
 return {'path':str(path),'sha256':sha(path),'manifest':str(mp),'manifest_sha256':sha(mp),'data':m}
verify();assert not (ROOT/'gpu-run.lock').exists()
built=read(ROOT/'runs/E051-final-build/complete.json');assert built['all_compilers_terminal'] and built['build_protocol_sha256']==P['build_protocol_sha256']
for p,h in built['evidence_sha256'].items():pin(p,h)
control=read(P['gpu_control_report']['path']);assert control['status']=='pass_scoped_up_action_raw_equivalence' and control['cases']==819 and control['full_raw_files_equal']
assert not OUT.exists();OUT.mkdir()
status=read(ar.STATUS)
for identity in P['control_ids']+P['measurement_order']:
 assert not (ROOT/'runs'/identity).exists() and not any(e['id']==identity for e in status['experiments'])
save(OUT/'invocation.json',{'at':now(),'protocol_sha256':sys.argv[1],'build_complete_sha256':sha(ROOT/'runs/E051-final-build/complete.json'),'gpu_control_report_sha256':sha(Path(P['gpu_control_report']['path'])),'all_ids_previously_absent':True,'all_compilers_terminal':True})
def run_one(identity,b,ordinary=False):
 verify();pin(b['path'],b['sha256']);pin(b['manifest'],b['manifest_sha256'])
 command=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',identity,'--title','E051 '+identity,'--kind','validation' if ordinary else ('baseline' if identity.startswith('B') else 'candidate'),'--binary',b['path'],'--build-manifest',b['manifest'],'--test','*' if ordinary else 'postflop_complete_cycle']
 if ordinary:command.append('--not-ignored')
 e=old.env();e.pop('E051_KERNEL_CONTROL_DIR',None)
 child(command,OUT,identity,e,1200)
 verify();r=read(ROOT/'runs'/identity/'report.json');pin(ROOT/'runs'/identity/'stdout.log',r['stdout_sha256'])
 assert r['returncode']==0 and r['status']=='measured' and r['binary_sha256']==b['sha256']
 assert r['provenance']['source_sha256']==BASE and r['binary_build_manifest']['sha256']==b['manifest_sha256']
 assert r['binary_build_manifest']['binary_hash_verified'] and r['binary_build_manifest']['data']==b['data']
 print('Completed',identity,flush=True)
 return r,(ROOT/'runs'/identity/'stdout.log').read_text(encoding='utf-8')
assert P['control_ids']==[]
unit=read(ROOT/'runs/V051-unit/report.json');unitraw=ROOT/'runs/V051-unit/stdout.log';pin(unitraw,unit['stdout_sha256'])
assert unit['returncode']==0 and unit['status']=='measured'
assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',unitraw.read_text(encoding='utf-8'))==[('84','0','4','0','0')]
save(OUT/'controls-complete.json',{'at':now(),'previously_terminal_unit':'V051-unit','unit_report_sha256':sha(ROOT/'runs/V051-unit/report.json'),'gpu_control_report_sha256':sha(Path(P['gpu_control_report']['path'])),'no_control_reexecution':True,'all_passed':True})
baseline=P['baseline_binary'];baseline['data']=read(Path(baseline['manifest']));assert baseline['data']['source_sha256']==BASE
candidate=binary('E051-postflop_autoresearch');anchor=old.exact_raw('E020C1');environment=None;gpu=None
for identity in P['measurement_order']:
 r,_=run_one(identity,baseline if identity.startswith('B') else candidate)
 old.compare.validate_run(r,{});assert old.exact_raw(identity)==anchor
 if environment is None:environment=r['environment'];gpu=old.compare.gpu_identity(r)
 assert r['environment']==environment and old.compare.gpu_identity(r)==gpu
save(OUT/'complete.json',{'at':now(),'protocol_sha256':sys.argv[1],'measurement_order':P['measurement_order'],'all_samples_retained':True,'fixture_results':3*len(P['measurement_order']),'convergence_records':23*len(P['measurement_order']),'controls_complete_sha256':sha(OUT/'controls-complete.json'),'candidate_accepted':False})
print('E051 fresh16pair confirmation complete; assess before any adoption.',flush=True)
