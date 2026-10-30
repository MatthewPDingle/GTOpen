from pathlib import Path
import json,shutil,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
 old.custody();old.pin(H/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
verify();O=H/'execution';assert not O.exists()and not(H/'probe.exe').exists()and not(H/'output').exists();O.mkdir()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=74*1024**3
 old.child(P['rustc_command'],O,'rustc',old.env(),600);verify()
 old.save(O/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(H/'probe.exe'),'compiler_terminal':True,'native_executions':0})
 old.child([str(H/'probe.exe'),str(H/'output')],O,'model',old.env(),1000);verify()
 markers=[json.loads(l.split('D138_MODEL ',1)[1])for l in(O/'model.stdout.log').read_text().splitlines()if'D138_MODEL 'in l]
 assert len(markers)==14 and all(m['stage']=='layout_complete'for m in markers[:12])and markers[-2]['stage']=='codecs_complete'and markers[-1]['stage']=='complete'
 assert markers[-1]['layouts']==12 and markers[-1]['codec_cases']==216 and markers[-1]['invalid_controls_rejected']==6
 assert markers[-1]['CUDA_contexts']==markers[-1]['GPU_kernels']==markers[-1]['solver_iterations']==0 and markers[-1]['performance_measurement']is False
 paths=list((H/'output').iterdir());assert {p.name for p in paths}=={'nodes.bin','groups.bin','codecs.bin','metadata.json'}
 size=sum(p.stat().st_size for p in paths);assert size<=P['maximum_output_bytes']
 old.save(O/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'all_owned_children_terminal':True,'raw_file_sha256':{str(p):old.sha(p)for p in paths},'raw_bytes':size,'summary':markers[-1],'source_main_live_PTX_custody_pass':True,'production_source_activated':False,'performance_measurement':False})
 verify();print(json.dumps({'raw_bytes':size,'summary':markers[-1]}),flush=True)
