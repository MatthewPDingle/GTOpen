import sys,json,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;P=h.read(H/'repair-r3-protocol.json')
def verify():
 h.pin(H/'repair-r3-protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O=H/'execution-r3';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',600);verify();assert(H/'primitive.ptx').read_bytes() in(H/'probe-r3.exe').read_bytes();h.save(O/'binary.json',{'sha256':h.sha(H/'probe-r3.exe'),'sealed_primitive_PTX_embedded':True})
 h.child([str(H/'probe-r3.exe'),str(H/'output-r3')],O,'probe',600);verify()
 markers=[json.loads(x.split('D205_CONTROL ',1)[1]) for x in (O/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'D205_CONTROL ' in x];assert len(markers)==257 and markers[-1]['stage']=='complete' and markers[-1]['cases']==256 and markers[-1]['kernel_launches']==768;assert [x['id'] for x in markers[:-1]]==list(range(256));assert(H/'output-r3/raw.bin').stat().st_size<=P['raw_reservation_bytes']
 h.child([sys.executable,str(H/'audit-r3.py')],O,'audit',1200);verify()
 report=ROOT/'comparisons/D205-cooperative-grid-controls/report.json';h.save(O/'complete.json',{'at':h.now(),'all_owned_compilers_native_readers_terminal':True,'report_sha256':h.sha(report),'application_primitive_launches':768,'solver_or_speed_samples':0,'source_main_live_protected_PTX_unchanged':True,'new_gain_accepted':False})
print('D205 whole primitive raw/capture/replay controls complete; no solver/speed result.',flush=True)
