import json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;G=ROOT/'runs/E099-direct-controls';P=h.read(G/'protocol.json');O=G/'execution'
def verify():
 h.pin(G/'protocol.json',sys.argv[1]);h.custody()
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
verify();O.mkdir(exist_ok=False);phase='before';fault=None
try:
 with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
  h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
  for name,unit in P['units'].items():
   verify();H=Path(unit['folder']);assert not(H/'probe.exe').exists() and not(H/'output').exists();phase=name+'-compile';h.child(unit['rustc_command'],O,phase,600);verify();h.save(O/(name+'-binary.json'),{'at':h.now(),'sha256':h.sha(H/'probe.exe')})
  for name in P['native_sequence']:
   verify();h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];H=Path(P['units'][name]['folder']);phase=name+'-native';h.child([str(H/'probe.exe'),str(H/'output')],O,phase,1800);verify();markers=[json.loads(x.split(P['units'][name]['marker']+' ',1)[1]) for x in (O/(phase+'.stdout.log')).read_text().splitlines() if P['units'][name]['marker']+' ' in x];assert len(markers)==P['units'][name]['expected_cases']+1 and markers[-1]['stage']=='complete' and markers[-1]['cases']==P['units'][name]['expected_cases'];h.save(O/(name+'-complete.json'),{'at':h.now(),'last_marker':markers[-1],'all_owned_native_terminal':True,'raw_files':{str(p):{'bytes':p.stat().st_size} for p in(H/'output').glob('*.bin')}})
  phase='audit';h.child([sys.executable,str(ROOT/'runs/E099-direct-audit.py'),sys.argv[1]],O,phase,1800);verify();h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'report_sha256':h.sha(ROOT/'comparisons/E099-direct-controls/report.json'),'all_compilers_native_and_reader_terminal':True,'NVRTC_runs':0,'solver_or_speed_runs':0})
except BaseException as error:
 fault=repr(error);h.save(O/'failure.json',{'at':h.now(),'phase':phase,'error':fault,'source_main_live_PTX_unchanged':True,'no_automatic_native_retry':True,'scope':'Inspect retained stderr and partial raw output. Actual numerical mismatch closes paired form without rescue; compiler/harness/reader defects require separately preserved mechanical diagnosis, no score/data rewriting.'});raise
finally:h.custody()
p=ROOT/'comparisons/E099-direct-controls/report.json';dst=h.ar.DASHBOARD/'evidence'/p.parent.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+p.parent.name+'/'+p.name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='E099');item.update(stage='Direct full-word controls passed; engine/raw lifecycle next',correctness='compiled_and_direct_raw_pass_broader_pending',reason='13528pairs/27056launches fulloutput/immutableinput/guards exact, originallegacycases retained. Multi-node fullengine/fullcanonical andall speed/material/adoption gatesstillpending.');item['evidence'].append({'label':'Every direct word, original prefix and device-alignment witness','url':'evidence/'+p.parent.name+'/'+p.name});s.update(updated_at=h.now(),stage=item['stage'],activity='Paired-load direct controls passed. No performance result or adoption; E080/16 remains unchanged.');h.ar.atomic_json(h.ar.STATUS,s)
r=h.read(p);print(json.dumps({k:r[k] for k in ['status','cases','kernel_launches','output_words_both_arms','immutable_words_both_arms','guard_words_both_arms','checks']}),flush=True)
