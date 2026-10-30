"""One fixed scalar-control build/run; preserve outputs on numerical rejection."""
import json,os,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
 for n,h in P['input_sha256'].items():old.pin(n,h)
 old.custody()
verify();E=H/'execution';assert not E.exists()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3;E.mkdir()
 env=old.env();env['E060_SCALAR_DIR']=str(E/'raw')
 old.child(P['rustc_command'],E,'rustc',env,180);verify()
 old.save(E/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(H/'probe.exe'),'compiler_terminal':True,'kernel_launches':0})
 old.child([str(H/'probe.exe')],E,'probe',env,180);verify()
 report=old.read(E/'raw/report.json');assert report['mismatches']==0
 assert (E/'raw/inputs.bin').read_bytes()==(E/'raw/inputs-after.bin').read_bytes()
 old.save(E/'complete.json',{'at':old.now(),'raw_report_sha256':old.sha(E/'raw/report.json'),'all_owned_children_terminal':True,'all_scalar_bits_exact':True,'no_performance_measurement':True})
 print(json.dumps(report),flush=True)
