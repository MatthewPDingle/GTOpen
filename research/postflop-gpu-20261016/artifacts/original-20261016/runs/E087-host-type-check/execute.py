import json,re,sys
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
 old.custody();old.pin(H/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
verify();O=H/'execution';O.mkdir(exist_ok=False);assert not(H/'probe.exe').exists()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status())
 old.child(P['rustc_command'],O,'rustc',old.env(),600);verify()
 old.child([str(H/'probe.exe'),'--nocapture','--test-threads=1'],O,'units',old.env(),300);verify()
 raw=(O/'units.stdout.log').read_text()
 assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('7','0','0','0','0')]
 old.save(O/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'binary_sha256':old.sha(H/'probe.exe'),'unit_tests_passed':7,'new_bounded_units':2,'GPU_contexts':0,'GPU_kernels':0,'performance_measurement':False,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True})
 print('7 CPU arena units pass; actual bounded methods type-check',flush=True)
