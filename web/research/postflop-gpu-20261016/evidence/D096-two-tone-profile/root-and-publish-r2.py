"""Root replay of retained API/device intervals and complete observer clocks."""
import ctypes,datetime,json,math,re,statistics,struct,sys,urllib.request
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
P=old.read(H/'cohort-plan.json');q=old.read(H/'cohort-report.json');E=H/'cohort-execution';done=old.read(E/'complete.json')
assert done['all_children_terminal'] and done['report_sha256']==old.sha(H/'cohort-report.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
checks=[]
def ck(label,v):checks.append({'label':label,'passed':bool(v)});assert v,label
def near(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-8)
def unite(spans):
 out=[]
 for a,b in sorted(spans):
  if not out or a>out[-1][1]:out.append([a,b])
  else:out[-1][1]=max(out[-1][1],b)
 return out
def ns(spans):return sum(b-a for a,b in unite(spans))
def clipped(rows,lo,hi):return [(max(r[6],lo),min(r[7],hi)) for r in rows if r[6]<hi and r[7]>lo]
names={int(n):name for name,n in re.findall(r'CUPTI_DRIVER_TRACE_CBID_(\w+)\s*=\s*(\d+)',Path(P['driver_cbid_header']).read_text())}
reference=old.historical.exact_raw('E020C1');anchor=reference[0][1];trajectory=[x for x in reference[1] if x['fixture_id']=='two-tone']
reports={};last=None;rawpins={};details={};functions=defaultdict(lambda:defaultdict(list));phase_totals=defaultdict(lambda:defaultdict(list));observer=[]
for identity in P['order']:
 d=ROOT/'runs'/identity;r=old.read(d/'report.json');log=d/'stdout.log';old.pin(log,r['stdout_sha256']);raw=log.read_text()
 values=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in raw.splitlines() if 'AUTORESEARCH_RESULT ' in x]
 ck(identity+' complete non-timing state',len(values)==1 and values==r['results'] and {k:v for k,v in values[0].items() if k not in old.historical.EXCLUDED}==anchor)
 stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in raw.splitlines() if 'AUTORESEARCH_STAGE ' in x]
 cs=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for x in stages if x.get('stage')=='convergence_check'];ck(identity+' exact ten checkpoints',cs==trajectory and len(cs)==10)
 receipt=old.read(E/(identity+'.exit.json'));a=datetime.datetime.fromisoformat(receipt['started_at']);b=datetime.datetime.fromisoformat(receipt['finished_at']);ck(identity+' serial terminal0',receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None and a<=b and (last is None or last<=a));last=b
 ck(identity+' accepted sources',r['provenance']['source_sha256']==old.BASE);reports[identity]=r
 for p in [d/'report.json',log,E/(identity+'.exit.json'),E/(identity+'.outer-wall.json')]:rawpins[str(p)]=old.sha(p)
 if not identity.startswith('D096T'):continue
 directory=E/'traces'/identity;data=(directory/'trace.bin').read_bytes();ck(identity+' raw framing',data[:16]==b'D087-TRACE-v1\0\0\0' and (len(data)-16)%176==0)
 rows=list(struct.Struct('<6I4Q10I80s').iter_unpack(data[16:]));meta=[json.loads(x) for x in (directory/'collector.jsonl').read_text().splitlines()];complete=meta[-1]
 ck(identity+' collector complete quality',len(meta)==8 and [x['event'] for x in meta]==['start']+['phase']*6+['complete'] and complete['records']==len(rows) and all(complete[k]==0 for k in ['errors','dropped','invalid_timestamps','outstanding_buffers']))
 ck(identity+' every row kind and times',all(r[0] in [1,2,3,4,10] and r[1]==0 and r[6]>0 and r[7]>=r[6] for r in rows))
 ks=[r for r in rows if r[0] in [3,10]];apis=[r for r in rows if r[0]==4];device=[r for r in rows if r[0]!=4]
 ck(identity+' kernel/API totals',len(ks)==complete['kernels']==P['expected_kernel_records'] and len(apis)==complete['driver_api_records'])
 ck(identity+' all API identity data',all(r[5] in names and r[2]>0 and r[3]>0 and r[4]>0 for r in apis))
 ai={r[4]:r for r in apis};ck(identity+' unique API correlations',len(ai)==len(apis))
 ck(identity+' all kernel joins',all(r[4] in ai and names[ai[r[4]][5]] in (['cuGraphLaunch','cuGraphLaunch_ptsz'] if r[10] else ['cuLaunchKernel','cuLaunchKernel_ptsz']) for r in ks))
 gs=[r for r in apis if names[r[5]] in ['cuGraphLaunch','cuGraphLaunch_ptsz']];ck(identity+' all407graph launches success',len(gs)==407 and all(r[10]==0 for r in gs))
 groups=defaultdict(Counter)
 for r in ks:
  if r[10]:groups[r[10]][r[9]]+=1
 ck(identity+' all graph-node repeats',sorted(next(iter(g.values())) for g in groups.values())==[9,199,199] and all(len(set(g.values()))==1 for g in groups.values()))
 counts=dict(Counter(r[20].split(b'\0',1)[0].decode() for r in ks));ck(identity+' full family counts',counts==q['traces'][identity]['kernel_family_counts'])
 stamps={x['marker']:x['timestamp_ns'] for x in meta[1:-1]};ck(identity+' sixordered phase markers',list(stamps)==list(range(1,7)) and all(stamps[i]<stamps[i+1] for i in range(1,6)))
 observed={}
 for label,m1,m2 in [('init',1,2),('solve',3,4),('readback',5,6)]:
  lo,hi=stamps[m1],stamps[m2];dev=clipped(device,lo,hi);api=clipped(apis,lo,hi);du,au,both=ns(dev),ns(api),ns(dev+api)
  fields={'span_ms':(hi-lo)/1e6,'device_union_ms':du/1e6,'api_union_ms':au/1e6,'api_device_overlap_ms':(du+au-both)/1e6,'device_uncovered_ms':((hi-lo)-du)/1e6,'uncovered_by_device_or_api_ms':((hi-lo)-both)/1e6}
  declared=q['traces'][identity]['phases'][label];ck(identity+' '+label+' interval replay',all(near(v,declared[k]) for k,v in fields.items()) and fields['uncovered_by_device_or_api_ms']>=-1e-9)
  selected=[r for r in apis if r[6]<hi and r[7]>lo];ck(identity+' '+label+' API counts',dict(Counter(names[r[5]] for r in selected))==declared['api_counts'])
  ck(identity+' '+label+' device kind counts',dict(Counter(str(r[0]) for r in device if r[6]<hi and r[7]>lo))==declared['device_kind_counts'])
  declared_functions={x['api']:x for x in declared['api_functions']};ck(identity+' '+label+' complete API names',set(declared_functions)=={names[r[5]] for r in selected})
  for name,f in declared_functions.items():
   selected_name=[r for r in selected if names[r[5]]==name];spans=clipped(selected_name,lo,hi);u=ns(spans);overlap=u+du-ns(spans+dev)
   ck(identity+' '+label+' '+name+' full durations',len(selected_name)==f['calls'] and near(sum(b-a for a,b in spans)/1e6,f['summed_ms']) and near(u/1e6,f['union_ms']) and near(overlap/1e6,f['device_overlap_ms']) and near((u-overlap)/1e6,f['api_union_without_device_activity_ms']) and sum(r[10]!=0 for r in selected_name)==f['nonzero_returns'])
   functions[label][name].append(f)
  for k,v in fields.items():phase_totals[label][k].append(v)
  observed[label]=fields
 details[identity]={'driver_API_records':len(apis),'kernel_records':len(ks),'phase_intervals':observed}
 for p in [directory/'trace.bin',directory/'collector.jsonl',directory/'parsed.json']:rawpins[str(p)]=old.sha(p)
for pair,declared in zip(P['pairs'],q['pairs']):
 b,t=reports[pair['baseline']],reports[pair['trace']];changes=[100*(t['results'][0]['full_cycle_ms']/b['results'][0]['full_cycle_ms']-1),100*(t['process_wall_ms']/b['process_wall_ms']-1),100*(old.read(E/(pair['trace']+'.outer-wall.json'))['elapsed_ms']/old.read(E/(pair['baseline']+'.outer-wall.json'))['elapsed_ms']-1)]
 ck(pair['trace']+' three raw observer clocks',all(near(x,declared[k]) for x,k in zip(changes,['cycle_change_pct','process_change_pct','runner_wall_change_pct'])))
 passed=all(abs(v)<=10 for v in changes);ck(pair['trace']+' preset usefulness decision',passed==declared['usefulness_pass']);observer.append(passed)
passed=all(observer);ck('complete observer decision',passed==q['observer_usefulness_pass'] and q['status']==('pass_scoped_activity_diagnostic' if passed else 'diagnostic_observer_perturbation_exceeds_gate'))
ck('no excluded pooled or extended samples',q['excluded_samples']==[] and q['extension_runs']==0 and q['historical_timing_samples_used']==0)
median_phases={label:{k:statistics.median(v) for k,v in fields.items()} for label,fields in phase_totals.items()}
median_apis={}
for label,apis in functions.items():
 median_apis[label]=sorted([{'api':name,'traces_observed':len(records),'median_calls':statistics.median(x['calls'] for x in records),'median_union_ms':statistics.median(x['union_ms'] for x in records),'median_device_overlap_ms':statistics.median(x['device_overlap_ms'] for x in records),'median_API_without_device_ms':statistics.median(x['api_union_without_device_activity_ms'] for x in records)} for name,records in apis.items()],key=lambda x:x['median_union_ms'],reverse=True)
R=ROOT/'comparisons/D096-two-tone-root-check';R.mkdir()
report={'at':old.now(),'status':'pass_scoped_driver_phase_diagnostic' if passed else 'observer_gate_failed_diagnostic_only','checks':checks,'checks_passed':len(checks),'native_results_exact':6,'convergence_checkpoints_exact':60,'all_kernel_driver_correlations_verified':True,'all_graph_replays_and_phase_intervals_verified':True,'parent_elevated':bool(ctypes.windll.shell32.IsUserAnAdmin()),'observer_usefulness_pass':passed,'observer_cycle_changes_pct':[x['cycle_change_pct'] for x in q['pairs']],'observer_process_changes_pct':[x['process_change_pct'] for x in q['pairs']],'observer_runner_changes_pct':[x['runner_wall_change_pct'] for x in q['pairs']],'median_phase_intervals':median_phases,'median_API_functions':median_apis,'trace_details':details,'preserved_raw_sha256':rawpins,'cohort_report_sha256':old.sha(H/'cohort-report.json'),'accepted_source':'E051','accepted_cumulative_gain_unchanged':12.4372274192464,'optimization_accepted':False,'root_external_independent_review':False,'limits':'Only fixed two-tone/thisGPU. Observer usefulness is not unbiased phase/API attribution or a per-function bias bound. APIs may wait for device work and overlap kernel/memory intervals; summed/median intervals are not removable time or additive complete-cycle gains. Time outside phase brackets is excluded. No optimizer admitted by diagnostic alone.'}
old.save(R/'report.json',report);old.custody()
published={}
for directory,prefix in [(H,H.name),(R,R.name)]+[(ROOT/'runs'/i,i) for i in P['order']]:
 for src in directory.rglob('*'):
  if not src.is_file() or src.suffix in ['.exe','.dll','.pdb','.obj','.lib','.exp'] or '__pycache__' in src.parts:continue
  key=prefix+'/'+src.relative_to(directory).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data,key
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(R/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published,'SDK_archives_remain_local':True,'accepted_source_unchanged':True})
links=[{'label':'D096 root API/phase/raw clock replay','url':'evidence/'+R.name+'/report.json'},{'label':'D096 complete matched observer results','url':'evidence/'+H.name+'/cohort-report.json'},{'label':'Retained D087 API correlation control','url':'evidence/'+H.name+'/ability-report.json'}]
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='D096');e.update(status='measured' if passed else 'rejected',stage='Driver API/phase profile validated' if passed else 'Observer perturbation exceeds fixed gate',correctness='pass',accepted=False,reason='All6states/60checks exact;26230kernels and407graph launches pertrace correlate with DriverAPI; sixphase brackets and full raw intervals replay. '+('All3observer clock changes pass10%in everypair.' if passed else 'Observer gate failed; no native-overhead or optimization inference.'));e['evidence'] +=links;st['evidence'] +=links;st.update(updated_at=old.now(),state='running',stage='D096 measured; inspect two-tone phase/API evidence',activity='AcceptedE051 remains12.437227%cumulative. Interpret host/device overlaps and closed evidence before selecting next optimizer.',active_experiment=None);old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'status':report['status'],'checks':len(checks),'median_phase_intervals':median_phases,'top_API_each_phase':{k:v[:5] for k,v in median_apis.items()},'http_verified_files':len(published),'report_sha256':old.sha(R/'report.json')}),flush=True)
