"""D109: bounded replay of existing accepted-source module/lifetime evidence."""
import sys,json,re,struct,math,tarfile,hashlib,shutil,urllib.request,subprocess
from pathlib import Path
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D109-module-lifetime-audit';H.mkdir()
repo=old.REPO; main=Path(r'X:\Dev\GTOpen')
core=Path(r'C:\Users\there\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\cudarc-0.19.7\src\driver\safe\core.rs')
crate=Path(r'C:\Users\there\.cargo\registry\cache\index.crates.io-1949cf8c6b5b557f\cudarc-0.19.7.crate')
inputs=[Path(__file__),repo/'Cargo.lock',core,crate,repo/'crates/solver/src/gpu/mod.rs',repo/'crates/server/src/main.rs',main/'crates/server/src/main.rs',repo/'crates/solver/tests/postflop_autoresearch.rs',ROOT/'runs/D041-initialization-source-audit/README.md',ROOT/'runs/D041-initialization-source-audit/observations.json',ROOT/'runs/D088-cohort/report-r2.json',ROOT/'runs/D088-source/mod.rs.patch']
cohorts=[('D087-cupti-driver-profile','cohort-plan.json'),('D096-two-tone-profile','cohort-plan-r2.json')]
for folder,plan in cohorts:
 d=ROOT/'runs'/folder;inputs += [d/plan,d/'cohort-report.json']
 p=old.read(d/plan);inputs.append(Path(p['driver_cbid_header']))
 for ident in old.read(d/'cohort-report.json')['traces']:
  inputs += [d/'cohort-execution/traces'/ident/f for f in ['trace.bin','collector.jsonl','parsed.json']]
  inputs.append(ROOT/'runs'/ident/'report.json')
old.save(H/'protocol.json',{'id':'D109','at':old.now(),'scope':'Replay six already-collected accepted E051 filtered init traces; source/dependency/lifetime audit only. No native execution or new timing samples.','input_sha256':{str(p):old.sha(p) for p in inputs},'accepted_source':old.BASE,'no_optimization':True,'no_new_sample_or_gain_claim':True})
checks=[]
def ck(label,v):
 checks.append({'label':label,'passed':bool(v)});assert v,label
lock=(repo/'Cargo.lock').read_text();block=lock[lock.index('name = "cudarc"'):].split('[[package]]',1)[0]
ck('pinned cudarc archive hash', 'version = "0.19.7"' in block and old.sha(crate)==re.search(r'checksum = "([a-f0-9]+)"',block).group(1))
with tarfile.open(crate,'r:gz') as t:ck('dependency source equals checksummed archive member',t.extractfile('cudarc-0.19.7/src/driver/safe/core.rs').read()==core.read_bytes())
ck('research and main server source identical',old.sha(repo/'crates/server/src/main.rs')==old.sha(main/'crates/server/src/main.rs'))
for p in [core,repo/'crates/solver/src/gpu/mod.rs',repo/'crates/server/src/main.rs',repo/'crates/solver/tests/postflop_autoresearch.rs']:
 target=H/('source/'+('cudarc-core.rs' if p==core else p.relative_to(repo).as_posix()));target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
def union(spans):
 merged=[]
 for a,b in sorted(spans):
  if not merged or a>merged[-1][1]:merged.append([a,b])
  else:merged[-1][1]=max(merged[-1][1],b)
 return sum(b-a for a,b in merged)
results={}
for folder,plan in cohorts:
 d=ROOT/'runs'/folder;p=old.read(d/plan);q=old.read(d/'cohort-report.json')
 ck(folder+' original protocol binding',q['protocol_sha256']==old.sha(d/plan))
 ck(folder+' observer accepted scoped',q['observer_usefulness_pass'] and q['excluded_samples']==[] and q['extension_runs']==0)
 names={int(n):s for s,n in re.findall(r'CUPTI_DRIVER_TRACE_CBID_(\w+)\s*=\s*(\d+)',Path(p['driver_cbid_header']).read_text())}
 for ident,declared in q['traces'].items():
  td=d/'cohort-execution/traces'/ident;data=(td/'trace.bin').read_bytes();meta=[json.loads(s) for s in (td/'collector.jsonl').read_text().splitlines()]
  ck(ident+' raw and metadata hashes',old.sha(td/'trace.bin')==declared['raw_trace_sha256'] and old.sha(td/'collector.jsonl')==declared['metadata_sha256'])
  ck(ident+' binary framing',data[:16]==b'D087-TRACE-v1\0\0\0' and (len(data)-16)%176==0)
  rows=list(struct.Struct('<6I4Q10I80s').iter_unpack(data[16:]));done=meta[-1]
  ck(ident+' collector quality',len(meta)==8 and done['event']=='complete' and done['records']==len(rows) and all(done[k]==0 for k in ['errors','dropped','invalid_timestamps','outstanding_buffers']))
  stamps={x['marker']:x['timestamp_ns'] for x in meta[1:-1]};ck(ident+' phase timestamps',stamps=={int(k):v for k,v in declared['phase_timestamps_ns'].items()})
  lo,hi=stamps[1],stamps[2];apis=[r for r in rows if r[0]==4 and r[6]<hi and r[7]>lo]
  api_names=[names[r[5]] for r in apis];focus={}
  ds={f['api']:f for f in declared['phases']['init']['api_functions']}
  for name,expected in [('cuDevicePrimaryCtxRetain',1),('cuModuleLoadData',1),('cuModuleGetFunction',8)]:
   selected=[r for r in apis if names[r[5]]==name];spans=[(max(lo,r[6]),min(hi,r[7])) for r in selected]
   ms=union(spans)/1e6;f=ds[name]
   ck(ident+' '+name+' replay',len(selected)==expected==f['calls'] and all(r[10]==0 for r in selected) and math.isclose(ms,f['union_ms'],abs_tol=1e-8) and math.isclose(sum(b-a for a,b in spans)/1e6,f['summed_ms'],abs_tol=1e-8))
   focus[name]={'calls':len(selected),'union_ms':ms}
  module=[r for r in apis if names[r[5]] in ['cuModuleLoadData','cuModuleGetFunction']]
  ck(ident+' no teardown within init bracket',not any('PrimaryCtxRelease' in n or n=='cuModuleUnload' for n in api_names))
  ck(ident+' accepted native source provenance',old.read(ROOT/'runs'/ident/'report.json')['provenance']['source_sha256']==old.BASE)
  results[ident]={'original_cohort':folder,'init_span_ms':(hi-lo)/1e6,'functions':focus,'module_and_lookup_union_ms':union([(max(lo,r[6]),min(hi,r[7])) for r in module])/1e6,'teardown_inside_init_bracket':False}
report={'id':'D109','at':old.now(),'status':'module_cache_prototype_declined_no_demonstrated_complete_cycle_headroom','checks':checks,'traces':results,'source_findings':['PTX compilation already process-cached in OnceLock. Each GpuSolver loads module and acquires eight functions.','MEM_CTX is retained by vram_info_mb, not directly reused as a Rust Arc by constructor. Research and main server source match; gpu_budget queries VRAM before gpu_solve_loop constructor. No live-process profiling claim.','CudaModule and CudaFunction retain module/context ownership; CudaContext retains/releases primary context. Dependency archive checksum and source member verified.','Frozen benchmark constructs fresh solver per fixture, has no explicit VRAM query and stops timing before lexical-end teardown.','D088 nvrtc_module includes first PTX acquire/compilation but function acquisition occurs later in object initializer; its ~53ms is not repeated module cost.','D041 previously identified this cache/lifetime issue; D109 supplies accepted E051 raw API replay, not a novel optimizer.'],'decision':'Do not prototype module/context cache from these data. No demonstrated >=1% complete-solve gain; context retention may improve benchmark-only lifecycle and shift teardown. Any future lifecycle change requires separately frozen actual app/full-process and idle/active GPU capacity evidence.','limits':'Six historical, fresh-process filtered rainbow/two-tone traces only. API intervals are elapsed observations, can include waits, exclude teardown, and are not removable time. No ordinary three-fixture repeated-lifecycle bound, fresh timing, statistical inference, code optimization or speedup acceptance. No trace sums projected onto full-cycle gain.','optimization_accepted':False,'accepted_source_unchanged':True,'accepted_cumulative_gain_unchanged':12.4372274192464,'new_native_processes':0,'new_timing_samples':0,'external_independent_review':False,'protocol_sha256':old.sha(H/'protocol.json')}
old.save(H/'report.json',report)
old.save(H/'raw-artifact-registry.json',{str(p):{'sha256':old.sha(p),'bytes':p.stat().st_size} for p in inputs if p.suffix in ['.bin','.crate']})
readme='D109 — module/function lifetime audit\n\nSix preserved E051 CUPTI traces replay exactly. Combined module-load and eight function-lookup API unions range '+str(min(v['module_and_lookup_union_ms'] for v in results.values()))+' to '+str(max(v['module_and_lookup_union_ms'] for v in results.values()))+' ms per filtered initialization. First PTX compilation is already cached. Server source retains a primary context through its VRAM budget query before solver construction. These traces do not measure ordinary repeated full-suite/app lifecycle or teardown. No prototype, compiler, native process, new sample or gain accepted. Historical D041 warning remains applicable.\n'
(H/'README.txt').write_text(readme,encoding='utf-8')
old.custody();published={}
for src in H.rglob('*'):
 if not src.is_file():continue
 key=H.name+'/'+src.relative_to(H).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);raw=src.read_bytes()
 if dst.exists():assert dst.read_bytes()==raw
 else:dst.write_bytes(raw)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as r:assert r.read()==raw
 published[key]=old.sha(src)
old.save(H/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'files':published})
links=[{'label':'D109 accepted-source module/lifetime audit','url':'evidence/'+H.name+'/report.json'}]
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']=='D109' for x in s['experiments'])
 s['experiments'].append({'id':'D109','at':old.now(),'title':'Module and function lifetime audit','kind':'diagnostic','status':'measured','correctness':'pass','accepted':False,'stage':'Cache prototype declined','reason':'Six existing E051 traces replay; module+function acquisition ~1.5–2ms per filtered init. PTX already cached; server retains context. No demonstrated complete-cycle headroom or new performance samples.','evidence':links})
 s['evidence']+=links;s.update(updated_at=old.now(),state='running',active_experiment=None,stage='Inspect remaining measured solve work',activity='D109 closes duplicate cache lead without native work. Accepted E051 scoped gain unchanged; retain 1% complete-solve and no-tradeoff gates.');old.ar.atomic_json(old.ar.STATUS,s)
print(json.dumps({'status':report['status'],'checks':len(checks),'module_lookup_ms':{k:v['module_and_lookup_union_ms'] for k,v in results.items()},'published':len(published),'report_sha256':old.sha(H/'report.json')}),flush=True)