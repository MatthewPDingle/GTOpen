import json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/D185-paired-engine-controls';P=h.read(H/'reader-r2-protocol.json');O=H/'execution'
def verify():
 h.pin(H/'reader-r2-protocol.json',sys.argv[1]);h.custody()
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
 for p,size in h.read(H/'reader-r2-raw-extents.json').items():assert Path(p).stat().st_size==size
verify();assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'comparisons/D185-paired-engine-controls').exists()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());h.child([sys.executable,str(H/'audit-r2.py')],O,'audit-r2',1800);verify();report=ROOT/'comparisons/D185-paired-engine-controls/report.json';r=h.read(report);assert r['cases']==68 and r['phase_pairs']==1424 and r['exploitability_pairs']==612 and r['continuation_root_pairs']==64
 h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':h.sha(H/'protocol.json'),'reader_correction_protocol_sha256':sys.argv[1],'all_owned_compilers_native_readers_terminal':True,'original_engine_process_reused':True,'extra_native_runs':0,'original_reader_failure_preserved':True,'report_sha256':h.sha(report),'source_main_live_protected_PTX_unchanged':True,'performance_measurement':False})
p=ROOT/'comparisons/D185-paired-engine-controls/report.json';dst=h.ar.DASHBOARD/'evidence'/p.parent.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+p.parent.name+'/'+p.name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D185');item.update(status='measured',stage='68case full engine state comparisons passed',correctness='all_declared_raw_state_exact',reason='All68constructors/1424phasepairs/612EVpairs/64changingroots, all66fields/CPU/q/scales/save/query/resume checks passed. Original reader inventory locator fixed read-only; no native rerun.64 actual paired constructors proven.');item['evidence'].extend([{'label':'Full all-field engine report','url':'evidence/'+p.parent.name+'/report.json'},{'label':'Preserved reader failure and read-only correction','url':'evidence/'+H.name+'/reader-r2-protocol.json'}]);s.update(updated_at=h.now(),active_experiment='E099',stage='Full canonical original-workload state controls next',activity='Paired action direct and68case engine controls passed. No speed observation or gain yet; E080/16 unchanged.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({k:r[k] for k in ['status','cases','phase_pairs','constructor_pairs','exploitability_pairs','continuation_root_pairs','reader_checks']}),flush=True)
