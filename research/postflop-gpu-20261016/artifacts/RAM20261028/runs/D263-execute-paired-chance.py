import json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/D263-paired-chance';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O.mkdir(exist_ok=False)
try:
 with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
  h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe'),str(H/'output')],O,'probe',1200);verify();files=list((H/'output').iterdir());assert len(files)==P['raw_file_count']and all(p.is_file()for p in files)and sum(p.stat().st_size for p in files)<=P['raw_reservation_bytes'];markers=[json.loads(x.split('D263_CONTROL ',1)[1])for x in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'D263_CONTROL 'in x];assert len(markers)==426 and markers[-1]['cases']==425 and markers[-1]['kernel_launches']==850;assert all(x['id']==i and x['descriptor']==h.read(H/'corpus.json')['cases'][i]['descriptor']for i,x in enumerate(markers[:-1]));h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'raw_marker_summary':markers[-1],'raw_file_sha256':{str(p):h.sha(p)for p in files},'all_owned_native_children_terminal':True,'solver_or_speed_samples':0});h.child(P['audit_command'],O,'audit',600);verify();report=Path(P['report']);q=h.read(report);assert q['status']=='pass_scoped_chance_raw_equivalence';h.save(O/'reader-complete.json',{'at':h.now(),'report_sha256':h.sha(report),'all_owned_children_terminal':True,'source_activated':False,'solver_or_speed_samples':0})
except BaseException as exc:
 h.save(O/'failure.json',{'at':h.now(),'error':repr(exc),'original_logs_and_partial_raw_preserved':True,'no_retry_or_new_cases_authorized':True,'source_activated':False});raise
p=report;dst=h.ar.DASHBOARD/'evidence'/p.parent.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+p.parent.name+'/'+p.name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E114');e.update(stage='All425direct chance cases passed; full solver proof pending',correctness='425directpairs exact; full solver proof pending',reason='All850directkernels match completeoutputs,actualimmutableimages andguards,including nonfinite/tails/permutations andall1326canonicalhands/everydealtcard. Source/binaries remainfixed andoff-tree. Need engine/canonical raw exactness before any ordinary complete-solve timing.');e['evidence'].append({'label':'Full direct raw numerical comparison','url':'evidence/'+p.parent.name+'/'+p.name});s.update(updated_at=h.now(),active_experiment='E114',stage=e['stage'],activity=e['reason']+' E080 remains live; no gain claimed.');h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(json.dumps({k:q[k]for k in['status','checks','cases','kernel_launches','output_words_both_arms','actual_immutable_words_both_arms','guard_words_both_arms']}),flush=True)
