"""D110 root replay and publication; preserve observer failure without timing rescue."""
import array,datetime,json,math,statistics,struct,sys,urllib.request
from pathlib import Path
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();H=ROOT/'runs/D110-plan-stage-profile';P=old.read(H/'protocol.json');N=old.read(H/'native-report.json');E=H/'execution';A=ROOT/'runs/D092-action-arity-order';AR=old.read(A/'report.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
assert old.read(H/'build/rustc.exit.json')['returncode']==0 and N['protocol_sha256']==old.sha(H/'protocol.json') and N['all_owned_children_terminal']
checks=0;words_total=0;raw_bytes=0;last=None;results=[]
def ck(v,label):
 global checks
 assert v,label;checks+=1

def vec(f,skip=False):
 n=struct.unpack('<Q',f.read(8))[0];ck(n<=100000000,'bounded words')
 if skip:f.seek(n*8,1);return
 a=array.array('Q');a.fromfile(f,n);ck(len(a)==n,'full vector');return a
for identity,v in enumerate(N['cases']):
 label=f'case-{identity:02d}';r=old.read(E/(label+'.exit.json'));ck(r['returncode']==0 and r['error'] is r['cleanup'] is None,'terminal0')
 a=datetime.datetime.fromisoformat(r['started_at']);b=datetime.datetime.fromisoformat(r['finished_at']);ck(a<=b and (last is None or last<=a),'serial');last=b
 native=[json.loads(s.split('D110 ',1)[1]) for s in (E/(label+'.stdout.log')).read_text().splitlines() if s.startswith('D110 ')];ck(len(native)==1 and native[0]=={k:v[k] for k in native[0]},'native observed report')
 path=E/(label+'.bin');old.pin(path,v['raw_sha256']);prior=A/'execution'/(label+'.bin');old.pin(prior,AR['cases'][identity]['raw_sha256']);count=0
 with path.open('rb') as f,prior.open('rb') as g:
  ck(f.read(16)==b'D110-PLAN-RAW1\0\0' and g.read(16)==b'D092-PLAN-RAW1\0\0','framing')
  ck(struct.unpack('<II',f.read(8))==struct.unpack('<II',g.read(8))==(identity,53),'case schema')
  sa,sb=struct.unpack('<QQ',f.read(16));ga,gb=struct.unpack('<QQ',g.read(16));ck(sa==sb==ga==gb and sa>0,'struct size')
  for field in range(53):
   ck(struct.unpack('<I',f.read(4))[0]==struct.unpack('<I',g.read(4))[0]==field,'field id')
   ca,cb,wa,wb=[vec(f) for _ in range(4)];oc=vec(g);vec(g,True);ow=vec(g);vec(g,True)
   ck(ca==cb==oc,'all capacities exact archived accepted');ck(wa==wb==ow,'all words exact archived accepted');count+=len(wa)
  for _ in range(2):ck(vec(f)==vec(g),'actual tree data exact')
  ck(f.read(1)==g.read(1)==b'','full endpoints')
 ck(count==v['baseline_words'],'word inventory');words_total+=count;raw_bytes+=path.stat().st_size
 bs=v['baseline_samples_ms'];ps=v['profile_samples_ms'];st=v['stage_spans_ms'];ck(len(bs)==len(ps)==len(st)==3,'fixed samples')
 ck(v['pair_orders']==['BC','CB','BC'] and v['warmup_pairs']==1 and v['measured_pairs']==3,'fixed sampling')
 ck(all(math.isfinite(x) and x>=0 for x in bs+ps+[x for row in st for x in row]),'finite times')
 bm,pm=statistics.median(bs),statistics.median(ps);passed=abs(pm-bm)<=max(0.1*bm,0.05)
 ck(bm==v['baseline_plan_ms'] and pm==v['profile_plan_ms'] and passed==v['observer_pass'],'observer rule replay')
 ck(all(len(row)==8 and math.isclose(sum(row),pm_sample,rel_tol=1e-12,abs_tol=1e-8) for row,pm_sample in zip(st,ps)),'disjoint stage partition')
 results.append({'case':identity,'baseline_median_ms':bm,'profile_median_ms':pm,'observer_pass':passed,'raw_sha256':old.sha(path),'raw_bytes':path.stat().st_size,'all53field_values_capacities_exact':True,'descriptive_stage_medians_ms':{name:statistics.median(row[j] for row in st) for j,name in enumerate(P['stage_names'])}})
ck(len(results)==12,'all12cases');passed=all(r['observer_pass'] for r in results);ck((N['status']=='pass_scoped_plan_diagnostic')==passed,'overall frozen diagnostic rule')
R=ROOT/'comparisons/D110-plan-stage-root-check';R.mkdir()
report={'id':'D110','at':old.now(),'status':'observer_gate_failed_diagnostic_only' if not passed else 'pass_scoped_CPU_plan_profile','checks':checks,'protocol_sha256':old.sha(H/'protocol.json'),'native_report_sha256':old.sha(H/'native-report.json'),'cases':results,'encoded_baseline_words_compared':words_total,'raw_bytes':raw_bytes,'failed_observer_cases':[r['case'] for r in results if not r['observer_pass']],'all12cases53fields_capacities_exact':True,'all_raw_accepted_fields_match_D092':True,'external_independent_review':False,'optimization_accepted':False,'gain_inferred':False,'new_native_processes':12,'new_GPU_execution':0,'accepted_source_unchanged':True,'accepted_cumulative_gain_unchanged':12.4372274192464,'decision':'Close frozen diagnostic without rerun/exclusions/extension or timing-based optimizer inference. Preserve all descriptive stages and raw controls. No source optimized or activated.','limits':'Warmed CPU-only component with held Spot and separate result destruction/raw encoding; one observer failed. Results are not reliable full-cycle cost attribution, app lifecycle, cold construction, whole-solver correctness, capacity, no-material-cost or performance evidence.'}
old.save(R/'report.json',report);old.save(H/'checkpoint.json',{'at':old.now(),'goal_active':True,'all_owned_children_terminal':True,'accepted':'E051','last_primary_baseline':'B222','next':'Source-level independent CPU plan dependency/ownership audit against frozen E051, bounded all-ref/history search first. Do not use failed D110 stage times to select or quantify savings; no repeat/finer/coarser marker/observer rescue. Any genuinely distinct candidate needs prospective source/exactness/component/whole-solve/material gates. No prior rejected kernel/cache/source form reopened.'})
old.custody();published={}
def put(src,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
 if dst.exists():assert dst.read_bytes()==data,key
 else:dst.write_bytes(data)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as r:assert r.read()==data,key
 published[key]=old.sha(src)
for src in H.rglob('*'):
 if src.is_file() and src.suffix not in ['.bin','.exe','.pdb','.obj'] and '__pycache__' not in src.parts:put(src,H.name+'/'+src.relative_to(H).as_posix())
for src in [R/'report.json',ROOT/'runs/D109-audit.py',ROOT/'runs/D110-prepare.py',ROOT/'runs/D110-execute.py',Path(__file__)]:put(src,('D109-preparation/' if src.name.startswith('D109') else 'D110-preparation/')+src.name)
old.save(H/'raw-registry.json',{str(E/f'case-{r["case"]:02d}.bin'):{'sha256':r['raw_sha256'],'bytes':r['raw_bytes']} for r in results});put(H/'raw-registry.json',H.name+'/raw-registry.json')
old.save(H/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'sha256':published,'all_raw_bytes_preserved_physically_S':True})
link={'label':'D110 full raw and observer replay','url':'evidence/D110-preparation/report.json'}
# report name is unique within this intentionally scoped publication folder.
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(e for e in s['experiments'] if e['id']=='D110');e.update(status='rejected' if not passed else 'measured',correctness='pass',accepted=False,stage='Observer gate failed; diagnostic closed' if not passed else 'Scoped CPU profile measured',reason='Full12x53planfields/capacities exact against archived accepted raw data; one fixed observer case failed. All observations preserved; no timing attribution/optimizer inference/retry or speedup accepted.');e['evidence'].append(link);s['evidence'].append(link);s.update(updated_at=old.now(),state='running',active_experiment=None,stage='Source dependency audit of accepted GPU-plan construction',activity='D109 cache declined; D110 observer failure preserved with full raw exact controls. No new gain; qualified E051 cumulative remains12.44%.');old.ar.atomic_json(old.ar.STATUS,s)
print(json.dumps({'status':report['status'],'checks':checks,'words_compared':words_total,'raw_bytes':raw_bytes,'failed_observer_cases':report['failed_observer_cases'],'http_files':len(published),'report_sha256':old.sha(R/'report.json')}),flush=True)