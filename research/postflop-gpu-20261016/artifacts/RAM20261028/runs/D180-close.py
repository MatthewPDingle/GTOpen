import json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();D=ROOT/'runs/D180-independent-action-warp-scope'
old=Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs/E081-source')
r=h.read(Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs/E081-resource/report.json'))
assert r['status']=='rejected_compiled_prerequisite' and not r['gates']['max_threads_not_reduced']
report={'id':'D180','at':h.now(),'status':'declined_semantic_duplicate_of_closed_E081','source_scope_sha256':h.sha(D/'scope-review.json'),'historical_source_sha256':{str(old/n):h.sha(old/n) for n in ['kernels.cu.patch','mod.rs.patch','candidate.cu','candidate-mod.rs']},'historical_resource_report_sha256':h.sha(Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs/E081-resource/report.json')),'classification':'Exact original E081 already mapped four independent 32-thread logical action nodes into a physical 128-thread block with ceil(count/4) host geometry and unchanged ordered arithmetic. Actual E081 max-thread loss 1024->896 and occupancy 8->7 closed this family. A private entry, helper template, small-span fallback or eligibility threshold changes source scope/shape but does not establish a distinct mechanism. Therefore no such rescue is admitted. E007 separately changed launch bounds and later failed a river guard; no launch-bound revival.','source_or_compiler_or_kernel_or_new_timing_runs':0,'new_gain_accepted':False}
h.save(D/'history-classification.json',report)
for name in ['scope-review.json','history-classification.json']:
 p=D/name;dst=h.ar.DASHBOARD/'evidence'/D.name/name;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes()
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+D.name+'/'+name,timeout=20) as resp:assert resp.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D180');item.update(status='declined',stage='Closed history alias; no candidate',reason=report['classification']);item['evidence'].append({'label':'Exact E081 source and resource attribution','url':'evidence/'+D.name+'/history-classification.json'});s.update(updated_at=h.now(),stage='Searching distinct ordered card-correction work',activity='D180declined as E081 alias before new source/compiler/native. E096 rejection preserved. E080/16/currentRAMbaseline unchanged; no new gain adopted.');h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(json.dumps({'D180':'declined_duplicate_E081','new_native':0}))
