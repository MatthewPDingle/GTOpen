"""Repair only stale summary counts from actual819 markers/raw inventory, no new native run."""
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
P=old.read(HERE/'protocol.json');EX=HERE/'execution';old.custody();assert not (old.ROOT/'gpu-run.lock').exists()
for p,h in P['input_sha256'].items():old.pin(p,h)
for label in ['rustc','probe']:
 e=old.read(EX/(label+'.exit.json'));assert e['returncode']==0 and e['error'] is None and e['cleanup'] is None
raw=(EX/'probe.stdout.log').read_text(encoding='utf-8');markers=[json.loads(x.split('E047_UNIT ',1)[1]) for x in raw.splitlines() if 'E047_UNIT ' in x];cases=old.read(HERE/'corpus.json')['cases']
assert len(markers)==820 and len(cases)==819
for c,m in zip(cases,markers[:-1]):
 assert m['stage']=='case' and all(m[k]==c[k] for k in ['id','hands','actions','threads','p','role','algorithm','iteration','value_mode','count','discount_bits'])
 assert m['all_raw_exact'] and m['guards_exact']
end=markers[-1];assert end['stage']=='complete' and end['cases']==717 and end['kernel_launches']==1434
assert end['all_raw_exact'] and end['all_inputs_and_guards_exact'] and end['raw_device_inputs_retained_both_arms']
assert (EX/'probe.stderr.log').read_bytes()==b''
source=(HERE/'probe.rs').read_text(encoding='utf-8');assert 'assert_eq!(cases.len(),819)' in source
assert '"stage":"complete","cases":717,"kernel_launches":1434' in source
assert source.count('.launch(')==1 and '[("baseline",&bf),("candidate",&cf)]' in source
old.save(EX/'wrapper-failure.json',{'at':old.now(),'status':'failed_stale_summary_count_observer','wrapper_returncode':1,'native_rustc_returncode':0,'native_probe_returncode':0,'error':'Final summary hard-coded717cases/1434launches despite819 successful per-case markers and fixed819-loop assertion.','execute_script_sha256':old.sha(HERE/'execute.py'),'probe_source_sha256':old.sha(HERE/'probe.rs'),'raw_marker_summary':end,'changed_fields_only':['cases','kernel_launches'],'new_native_runs':0,'required_before_timing':'Root decoder must verify full819-case inputs and both full GPU outputs/immutable images, exact EOF and recomputed inventories. No numerical mismatch observed.'})
validated=end|{'cases':len(cases),'kernel_launches':2*len(cases)}
rawdir=Path(P['raw_output']);files={str(p):old.sha(p) for p in rawdir.iterdir()};assert len(files)==5 and sum(p.stat().st_size for p in rawdir.iterdir())<2*1024**3
old.save(EX/'complete-r2.json',{'at':old.now(),'status':'native_pass_with_stale_summary_header','protocol_sha256':old.sha(HERE/'protocol.json'),'source_review_sha256':old.sha(HERE/'source-review.json'),'binary_sha256':old.sha(HERE/'probe.exe'),'native_raw_marker_summary':end,'validated_summary':validated,'actual_case_marker_count':819,'raw_file_sha256':files,'stdout_sha256':old.sha(EX/'probe.stdout.log'),'reporting_failure_sha256':old.sha(EX/'wrapper-failure.json'),'all_children_terminal':True,'accepted162_unchanged':True,'main_live_ptx_unchanged':True,'new_native_runs':0,'performance_measured':False,'candidate_accepted':False})
s=(HERE/'audit.py').read_text(encoding='utf-8').replace("execution/complete.json","execution/complete-r2.json").replace("comparisons/E047-kernel-control'","comparisons/E047-kernel-control-r2'").replace("C['raw_marker_summary']","C['validated_summary']")
s=s.replace("'id':'E047-kernel-control'","'id':'E047-kernel-control-r2'").replace("'root_cross_check_only':True","'root_cross_check_only':True,'reporting_failure_sha256':old.sha(HERE/'execution/wrapper-failure.json'),'new_native_runs':0")
s=s.replace("old.sha(HERE/'audit.py')","old.sha(HERE/'audit-r2.py')")
assert not (HERE/'audit-r2.py').exists();(HERE/'audit-r2.py').write_text(s,encoding='utf-8');print(old.sha(HERE/'audit-r2.py'))
