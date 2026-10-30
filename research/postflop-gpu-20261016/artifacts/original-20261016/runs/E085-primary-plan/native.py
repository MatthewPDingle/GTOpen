"""E085 ordinary units then one fixed3-pair complete-cycle screen; no adoption."""
import json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'accepted-E080-live-20261018'));import common_e080_live as old
ar=old.ar
read,sha,pin,save,now,child=old.read,old.sha,old.pin,old.save,old.now,old.child
assert len(sys.argv)==2;pin(HERE/'protocol.json',sys.argv[1]);P=read(HERE/'protocol.json')
ROOT=ar.RESEARCH;OUT=ROOT/'runs/E085-native-execution';BASE=read(P['baseline']['path'])['source_sha256']
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
built=read(ROOT/'runs/E085-final-build/complete.json');assert built['all_compilers_terminal'] and built['build_protocol_sha256']==P['build_protocol_sha256']
for p,h in built['evidence_sha256'].items():pin(p,h)
control=read(P['direct_control_report']['path']);assert control['status']=='pass_scoped_up_action_raw_equivalence' and control['full_raw_files_equal'] and control['actual_device_inputs_retained_both_arms'] and control['all_parent_child_cfv_rows_disjoint'] and control['kernel_launches']==1638 and control['accepted162_main_live_ptx_unchanged']
assert not OUT.exists();OUT.mkdir()
status=read(ar.STATUS)
for identity in P['control_ids']+P['measurement_order']:
 assert not (ROOT/'runs'/identity).exists() and not any(e['id']==identity for e in status['experiments'])
save(OUT/'invocation.json',{'at':now(),'protocol_sha256':sys.argv[1],'build_complete_sha256':sha(ROOT/'runs/E085-final-build/complete.json'),'direct_control_report_sha256':sha(Path(P['direct_control_report']['path'])),'all_ids_previously_absent':True,'all_compilers_terminal':True})
def run_one(identity,b,ordinary=False):
 verify();pin(b['path'],b['sha256']);pin(b['manifest'],b['manifest_sha256'])
 command=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',identity,'--title','E085 '+identity,'--kind','validation' if ordinary else ('baseline' if identity.startswith('B') else 'candidate'),'--binary',b['path'],'--build-manifest',b['manifest'],'--test','*' if ordinary else 'postflop_complete_cycle']
 if ordinary:command.append('--not-ignored')
 e=old.env();e.pop('E085_PLAN_CONTROL_DIR',None)
 child(command,OUT,identity,e,1200)
 verify();r=read(ROOT/'runs'/identity/'report.json');pin(ROOT/'runs'/identity/'stdout.log',r['stdout_sha256'])
 assert r['returncode']==0 and r['status']=='measured' and r['binary_sha256']==b['sha256']
 assert r['provenance']['source_sha256']==BASE and r['binary_build_manifest']['sha256']==b['manifest_sha256']
 assert r['binary_build_manifest']['binary_hash_verified'] and r['binary_build_manifest']['data']==b['data']
 print('Completed',identity,flush=True)
 return r,(ROOT/'runs'/identity/'stdout.log').read_text(encoding='utf-8')
assert len(P['control_ids'])==1 and P['control_ids'][0]==P['ordinary_unit_id']
r,raw=run_one(P['control_ids'][0],binary('E085-solver'),True)
assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('86','0','4','0','0')]
save(OUT/'controls-complete.json',{'at':now(),'unit_id':P['control_ids'][0],'ordinary_units_passed':86,'ignored':4,'direct_control_report_sha256':sha(Path(P['direct_control_report']['path'])),'all_passed':True})
baseline=P['baseline_binary'];baseline['data']=read(Path(baseline['manifest']));assert baseline['data']['source_sha256']==BASE
candidate=binary('E085-postflop_autoresearch');anchor=old.historical.exact_raw('E020C1');environment=None;gpu=None
for identity in P['measurement_order']:
 r,_=run_one(identity,baseline if identity.startswith('B') else candidate)
 old.compare.validate_run(r,{});assert old.historical.exact_raw(identity)==anchor
 if environment is None:environment=r['environment'];gpu=old.compare.gpu_identity(r)
 assert r['environment']==environment and old.compare.gpu_identity(r)==gpu
save(OUT/'complete.json',{'at':now(),'protocol_sha256':sys.argv[1],'measurement_order':P['measurement_order'],'all_samples_retained':True,'fixture_results':18,'convergence_records':138,'controls_complete_sha256':sha(OUT/'controls-complete.json'),'candidate_accepted':False})
print('E085 fixed primary complete; assess before any confirmation.',flush=True)
