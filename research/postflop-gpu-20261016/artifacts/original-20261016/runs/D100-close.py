"""Replay the cache preference occupancy rejection and preserve unused trace controls."""
import json,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D100-show-cache-configuration';E=H/'execution';P=old.read(H/'protocol-r2.json');q=old.read(H/'report.json');resource=q['resource'];checks=0
def require(v,label):
 global checks
 assert v,label;checks+=1
for p,h in P['input_sha256'].items():old.pin(p,h);checks+=1
require(q['status']=='rejected_resource_prerequisite' and q['kernel_launches']==0,'resource-only outcome')
require(q['protocol_sha256']==old.sha(H/'protocol-r2.json'),'frozen protocol')
for home,label in [(H/'build','collector'),(H/'build','rustc'),(E,'probe')]:
 r=old.read(home/(label+'.exit.json'));require(r['returncode']==0 and r['error'] is r['cleanup'] is None,'all native/compiler children terminal')
markers=[json.loads(x.split('D100_EXACT ',1)[1]) for x in (E/'probe.stdout.log').read_text().splitlines() if x.startswith('D100_EXACT ')]
require([x['stage'] for x in markers]==['corpus_validated','device','resource_gate','resource_rejected'],'no raw case stage reached')
require(markers[2]==resource and markers[3]['kernel_launches']==0,'raw resource report agreement')
require(resource['baseline_attributes']==resource['candidate_attributes']==[38,0,1040,1024,48112],'unchanged compiled attributes')
require((H/'baseline.cu').read_bytes()==(H/'candidate.cu').read_bytes(),'identical full CUDA source')
require((E/'baseline.ptx').read_bytes()==(E/'candidate.ptx').read_bytes(),'identical generated PTX')
for name in ['trace.bin','trace-meta.jsonl','raw-results.jsonl']:require(not (E/name).exists(),'no collector or raw kernel stage started')
g=old.read(H/'corpus.json')['geometries'];expected=[(i,t,f) for i in range(36) for t in [64,128,256] for f in [0,1]]
rows=resource['occupancy'];require([(r['geometry'],r['threads'],r['flag']) for r in rows]==expected,'all fixed resource queries')
failed=[]
for row in rows:
 require(row['dynamic_shared_bytes']==g[row['geometry']]['dynamic_shared_bytes'],'same requested shared shape')
 require(row['baseline_blocks']>0 and row['candidate_blocks']>0,'both legal launch shapes')
 require(row['candidate_blocks']<row['baseline_blocks'],'strict occupancy loss')
 failed.append(row)
require(len(failed)==216 and not resource['passed'],'frozen occupancy gate rejects')
R=ROOT/'comparisons/D100-cache-resource-root-check';R.mkdir()
report={'id':'D100','at':old.now(),'status':'pass_resource_rejection','checks':checks,'protocol_sha256':old.sha(H/'protocol-r2.json'),'native_report_sha256':old.sha(H/'report.json'),'source_sha256':old.sha(H/'baseline.cu'),'identical_ptx_sha256':old.sha(E/'baseline.ptx'),'compiled_attributes':resource['baseline_attributes'],'attribute_order':resource['attribute_order'],'fixed_queries':216,'strictly_lower_occupancy_queries':216,'zero_capacity_queries':0,'resource_rows':rows,'example128':next(x for x in rows if x['geometry']==0 and x['threads']==128 and x['flag']==0),'no_trace_or_raw_kernel_execution':True,'all_compilers_and_native_terminal':True,'source_activated':False,'application_kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'limits':'Driver theoretical maximum active CTAs per SM, not achieved runtime occupancy, speed, cache hit rates, actual per-launch configuration fields or GPU workload capacity. Raw/kernel/CUPTI checks were prepared but deliberately never started after resource rejection. Root replay is not independent external review.'}
old.save(R/'report.json',report)
old.save(H/'checkpoint.json',{'at':old.now(),'previous_goal_turn_classification':'progress: D098actual code capture and E060timed/accuracy/resource rejection','current_goal_turn':'D099all12x53field/capacity full raw CPU controls, fixed component rejection; D100one identical-code cache hint rejected from216real driver occupancy queries','goal_active':True,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'last_primary_baseline':'B188','owned_sessions_terminal':[98886,35744,87971],'all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True,'D100_raw_kernel_or_trace_runs':0,'next':'A useful next audit is the inventory of prior resource-only rejections: distinguish true allocated-register/shared/occupancy costs from nominal-only count changes, using current calibrated D094model. First read the frozen policy scope; do not rewrite prior decisions or retry any timed/failed-numerical hypothesis. Identify all never-timed source forms systematically, not selectively. Any future eligibility supplement must be explicit and prospective before new native/timing qualification, preserve original history, keep1%and all exactness/material/fresh16/holdout gates, and justify why a corrected allocation assessment warrants it. Do not claim or perform a reopened experiment from this checkpoint alone. Alternatively find a distinct untested GPU mechanism with actual full-cycle relevance. Do not sweep D100cache preference/carveout/kernel variants or D099scratch allocation variants.','live_deployment':'Prior automatic approval block remains; do not retry or ask duplicate permission.'})
published={}
def put(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes()
 else:dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
for p in H.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.exe','.dll','.pdb','.obj','.lib','.exp']:put(p,H.name+'/'+p.relative_to(H).as_posix())
for p in [Path(__file__),ROOT/'runs/D100-prepare.py',ROOT/'runs/D100-freeze-execution.py']:put(p,'D100-preparation-sources/'+p.name)
put(R/'report.json',R.name+'/report.json')
old.save(H/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published,'no_numerical_or_speed_claim':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='D100')
 e.update(status='rejected',correctness='pending',accepted=False,stage='Closed: all216resource combinations lose occupancy',reason='Identical CUDA/PTX,38registers/0local/1040static shared/max1024threads unchanged. L1preference reduces driver theoretical active CTAs in all216shape/thread/cache-override queries. Smallest128threadcase12->3. Stop before raw kernels/CUPTI/solver/timing; no measured slowdown or speedup.')
 e['evidence'].extend([{'label':'Frozen resource/actual-configuration admission','url':'evidence/'+H.name+'/protocol-r2.json'},{'label':'Raw compiled attributes and driver occupancy','url':'evidence/'+H.name+'/report.json'},{'label':'Resource/root rejection replay','url':'evidence/'+R.name+'/report.json'},{'label':'Preserved checkpoint','url':'evidence/'+H.name+'/checkpoint.json'}])
 st.update(state='running',active_experiment=None,updated_at=old.now(),stage='Next GPU hotspot/eligibility evidence audit',activity='D099component and D100occupancy paths closed without integration. No new speed gain accepted. E051qualified cumulative12.437227% remains;1%and no-material-tradeoff policy unchanged.');old.ar.atomic_json(old.ar.STATUS,st)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();require(b'### D100 per-function' not in raw,'new ledger entry')
note=f'''

### D100 per-function showdown cache preference -- occupancy rejection

One owned off-tree diagnostic applies CU_FUNC_CACHE_PREFER_L1only to a second up_show function; baseline default remains. Full CUDA source and generated PTX are byte-identical to acceptedE051. Official CUDA12.9driver docs say preference may be overridden/ignored and switching preferences may add device synchronization; B200SM10cache capacities are not assumed for this RTX5090SM12. Scoped ledger search found no previous per-function cache configuration candidate. No context/global setting, counters, injection, live attach or source activation.

Original preparation1e86b0d88b10bf71f684ebe9d63f5e31ca8867c6d84e1cfe4dcb11324c981a18is preserved. Before any compiler/native output, SDK review normalized unavailable CUPTIcache fields: cacheConfignot updated when explicit carveout is requested, and requested percent only valid with its flag. Collector R2/protocol64a06735dd3525f435617afe85295c50c25369cba8e68c44585fddbae9bdf24dretains identical hint/geometry/gates. Original collector source retained. One C++DLL build, one Rust build and one resource native process in handle87971all terminal0. Private field collector/raw364pair controls were compiled but remain unexecuted.

Before kernel launch, compare actual compiled attrs and36geometries x64/128/256threads x default/disable-caching-override occupancy flags. Registers38/38,local0/0,static shared1040/1040,maxthreads1024/1024,maxdynamic48112/48112 unchanged. **All216queries have lower theoretical active CTAs per SM under L1preference**, none zero. Smallest dynamic68byte shape at128threads:12to3for both flags; dynamic5208example12to1. Resource gate therefore rejects before raw numerical tests or activity collection. No trace/meta/raw-result file exists, no application kernel launch or solver/timing run. Theoretical scheduler occupancy loss is not measured runtime occupancy or a demonstrated speed regression.

Root{report['checks']}checks SHA{old.sha(R/'report.json')}; native report89ac5e5921c7a568e4c66aeb10c2e1d58f6a4298c51a43459ef69dbba7ed684a. No alternate preference/carveout/kernel scope sweep, integrated source, primary/fresh16/broad/material/holdout/cumulative or adoption. All{len(published)}source/report/log/PTX artifacts HTTP-byte verified; root replay is not independent external review. Accepted162/main157/live/protectedPTX and acceptedE051cumulative12.4372274192%unchanged, lastprimaryB188. Goal active.
'''
nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+note.encode('utf-8').replace(b'\n',nl));old.custody()
print(json.dumps({'status':'resource_rejection_published','root_checks':report['checks'],'lower_occupancy_combinations':216,'application_kernel_launches':0,'published':len(published),'accepted_source':'E051','goal_active':True}),flush=True)
