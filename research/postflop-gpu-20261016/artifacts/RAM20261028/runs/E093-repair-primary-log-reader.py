import sys,json,ast,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists()
P=h.read(ROOT/'runs/E093-primary-plan/protocol.json')
for path,digest in P['input_sha256'].items():h.pin(path,digest)
O=ROOT/'runs/E093-primary-execution';unit=ROOT/'runs/V093-unit';u=h.read(unit/'report.json');text=(unit/'stdout.log').read_text(encoding='utf-8')
assert h.read(O/'V093-unit.exit.json')['returncode']==0 and u['returncode']==0 and 'test result: ok. 86 passed; 0 failed; 4 ignored;' in text
assert text.count('gpu: postflop NVRTC13.0 runtime compiler')==1 and 'optional postflop NVRTC13 declined:' not in text
assert not(unit/'stderr.log').exists() and not(O/'complete.json').exists()
assert all(not(ROOT/'runs'/row['id']).exists() for row in P['sequence'] if not row['unit'])
H=ROOT/'runs/E093-primary-adapter-repair';H.mkdir(exist_ok=False)
source=ROOT/'runs/E093-primary-native.py';code=source.read_text(encoding='utf-8')
code=code.replace("H=ROOT/'runs/E093-primary-plan';assert len(sys.argv)==2;", "H=ROOT/'runs/E093-primary-plan';assert len(sys.argv)==3;",1)
needle="O=ROOT/'runs/E093-primary-execution'"
code=code.replace(needle,needle+"\nREPAIR=ROOT/'runs/E093-primary-adapter-repair/protocol.json';h.pin(REPAIR,sys.argv[2]);RP=h.read(REPAIR)\nfor path,digest in RP['input_sha256'].items():h.pin(path,digest)",1)
needle="verify();assert not(ROOT/'gpu-run.lock').exists();O.mkdir(exist_ok=False)"
code=code.replace(needle,"verify();assert not(ROOT/'gpu-run.lock').exists();assert O.is_dir() and not(O/'complete.json').exists()",1)
needle="h.save(O/'runtime-environment.json',{'at':h.now(),'GTOPEN_POSTFLOP_NVRTC13_DIR':P['runtime_directory'],'same_value_for_both_arms':True,'scope':'Onlythiscontrolleranditschildren;notpersistentuser/global/PATHsetting'})"
assert code.count(needle)==1;code=code.replace(needle,"assert h.read(O/'runtime-environment.json')['GTOPEN_POSTFLOP_NVRTC13_DIR']==P['runtime_directory']",1)
needle="  h.child(cmd,O,record['id'],1200);verify();r=h.read(ROOT/'runs'/record['id']/'report.json')"
replacement="  if record['unit']:\n   assert record['id']=='V093-unit';h.pin(ROOT/'runs/V093-unit/report.json',RP['completed_unit_report_sha256']);h.pin(ROOT/'runs/V093-unit/stdout.log',RP['completed_unit_stdout_sha256'])\n  else:h.child(cmd,O,record['id'],1200)\n  verify();r=h.read(ROOT/'runs'/record['id']/'report.json')"
assert code.count(needle)==1;code=code.replace(needle,replacement,1)
needle="stderr=(ROOT/'runs'/record['id']/'stderr.log').read_text(encoding='utf-8')";assert code.count(needle)==1;code=code.replace(needle,"stderr=(ROOT/'runs'/record['id']/'stdout.log').read_text(encoding='utf-8')",1)
needle="'protocol_sha256':sys.argv[1],'sequence':";assert code.count(needle)==1;code=code.replace(needle,"'protocol_sha256':sys.argv[1],'original_controller_failed_after_completed_units':True,'mechanical_adapter_repair_protocol_sha256':sys.argv[2],'actual_controller_sha256':h.sha(__file__),'completed_unit_reused_without_repeat':True,'sequence':",1)
script=ROOT/'runs/E093-primary-native-r2.py';assert not script.exists();ast.parse(code);script.write_bytes(code.encode())
review={'at':h.now(),'status':'mechanical_post_unit_pre_first_timing_log_locator_repair','original_controller_exit':1,'error':'FileNotFoundError reading V093-unit/stderr.log. Frozen runner explicitly uses stderr=subprocess.STDOUT andwrites combinedstdout.log.','original_script_sha256':h.sha(source),'original_primary_protocol_sha256':h.sha(ROOT/'runs/E093-primary-plan/protocol.json'),'original_completed_unit_exit':0,'original_unit_tests_passed':86,'original_unit_tests_ignored':4,'unit_actual13backend_marker_count':1,'completed_unit_reused_not_repeated':True,'original_controller_failure_preserved':True,'initial_speed_samples_before_repair':0,'changes':'Readonly mergedstdout asactualbackendlog;reuse verifiedexistingunitreport/receipt;continue same6originaltrialIDs/order/source/quality/flags/environment/1%/fixturegates. Newexecutionadapter separatelypinned;originalscript/protocol unchanged. No numerical/resource/timingfailure rescued,no nativeunit/compile rerun,no extra/pooled/excluded trial.','actual_repaired_script_sha256':h.sha(script)}
h.save(H/'review.json',review)
inputs=[Path(__file__),source,script,ROOT/'runs/E093-primary-plan/protocol.json',unit/'report.json',unit/'stdout.log',O/'V093-unit.exit.json',O/'V093-unit.invocation.json',O/'runtime-environment.json',H/'review.json',h.REPO/'tools/postflop_autoresearch.py']
h.save(H/'protocol.json',{'id':'E093-primary-adapter-repair','at':h.now(),'status':'FROZEN_PRE_FIRST_PRIMARY_TIMING','original_primary_protocol_sha256':h.sha(ROOT/'runs/E093-primary-plan/protocol.json'),'completed_unit_report_sha256':h.sha(unit/'report.json'),'completed_unit_stdout_sha256':h.sha(unit/'stdout.log'),'input_sha256':{str(path):h.sha(path) for path in inputs},'scope':'Mechanicalcontrolreader repair only;all6originalspeedmeasurements andgates/inputsunchanged. Originalcontrollerexit1preserved,actualunit0reused. No completedscientific/timingobservation repeatedorregraded.'})
for name in ['review.json','protocol.json']:
    path=H/name;key=H.name+'/'+name;dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(path,dest)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==path.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='E093');item.update(stage='86units passed;merged-log adapter repaired beforefirsttiming',reason='Unitnative0/86pass/4ignoredandactual13backend confirmed. Originalcontrollerlogpatherror preserved;separatefrozenreaderrepairusesmergedstdout andreusescompletedunit. Same6trialIDs/order andall1%/strictfixture/sciencegates unchanged.')
    item.setdefault('evidence',[]).append({'label':'Pre-timing log-reader repair','url':'evidence/E093-primary-adapter-repair/review.json'});status.update(updated_at=h.now(),active_experiment='E093',stage='E093 frozen6trial runtime speed screen',activity='86units pass;readerpathfixedbeforefirsttiming,no unitrepeat. Sameoriginalpairs/gates;no speedclaim.');h.ar.atomic_json(h.ar.STATUS,status)
h.custody();print(h.sha(H/'protocol.json'),flush=True)
