"""Root raw trace/clock/state replay and scoped hotspot publication."""
import ctypes,datetime,json,math,statistics,struct,sys,urllib.request
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();P=old.read(H/'cohort-plan.json');q=old.read(H/'cohort-report.json');E=H/'cohort-execution';done=old.read(E/'complete.json');assert done['all_children_terminal'] and done['report_sha256']==old.sha(H/'cohort-report.json');assert q['status']=='pass_scoped_activity_diagnostic'
for p,h in P['input_sha256'].items():old.pin(p,h)
checks=[]
def ck(label,v):checks.append({'label':label,'passed':bool(v)});assert v,label
def near(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-8)
def union(rows):
 total=0;right=None
 for a,b in sorted((r[6],r[7]) for r in rows):
  if right is None or a>=right:total+=b-a;right=b
  elif b>right:total+=b-right;right=b
 return total
ref=old.historical.exact_raw('E020C1');anchor=ref[0][0];trajectory=[c for c in ref[1] if c['fixture_id']=='rainbow'];reports={};last=None;rawpin={};families=defaultdict(list);counts_reference=None;trace_details={}
for identity in P['order']:
 d=ROOT/'runs'/identity;r=old.read(d/'report.json');log=d/'stdout.log';old.pin(log,r['stdout_sha256']);text=log.read_text();values=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_RESULT ' in x];ck(identity+' raw/report',values==r['results'] and len(values)==1)
 ck(identity+' full state/settings/stops exact',{k:v for k,v in values[0].items() if k not in old.historical.EXCLUDED}==anchor)
 stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_STAGE ' in x];cs=[{k:c[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for c in stages if c.get('stage')=='convergence_check'];ck(identity+' ten checkpoints exact',cs==trajectory and len(cs)==10)
 receipt=old.read(E/(identity+'.exit.json'));start=datetime.datetime.fromisoformat(receipt['started_at']);end=datetime.datetime.fromisoformat(receipt['finished_at']);ck(identity+' serial terminal0',receipt['returncode']==0 and receipt['error'] is None and receipt['cleanup'] is None and start<=end and (last is None or last<=start));last=end
 ck(identity+' accepted sources unchanged',r['provenance']['source_sha256']==old.BASE);reports[identity]=r
 for p in [d/'report.json',log,E/(identity+'.exit.json'),E/(identity+'.outer-wall.json')]:rawpin[str(p)]=old.sha(p)
 if identity.startswith('D085T'):
  directory=E/'traces'/identity;data=(directory/'trace.bin').read_bytes();ck(identity+' fixed trace framing',data[:16]==b'D085-TRACE-v1\0\0\0' and (len(data)-16)%176==0);rows=list(struct.Struct('<6I4Q10I80s').iter_unpack(data[16:]));meta=[json.loads(x) for x in (directory/'collector.jsonl').read_text().splitlines()];ck(identity+' complete clean collector',len(meta)==2 and meta[0]['event']=='start' and meta[1]['event']=='complete' and all(meta[-1][k]==0 for k in ['errors','dropped','invalid_timestamps','outstanding_buffers']) and meta[-1]['records']==len(rows))
  ck(identity+' all valid device0times',all(row[1]==0 and row[6]>0 and row[7]>=row[6] for row in rows));ks=[row for row in rows if row[0] in [3,10]];ck(identity+' kernel totals',len(ks)==meta[-1]['kernels']==26230)
  names=lambda row:row[20].split(b'\0',1)[0].decode();count=dict(Counter(names(row) for row in ks))
  if counts_reference is None:counts_reference=count
  ck(identity+' identical invocation counts',count==counts_reference==q['traces'][identity]['kernel_family_counts'])
  groups=defaultdict(lambda:Counter());attributes=defaultdict(set);top=defaultdict(int)
  for row in ks:
   name=names(row);attributes[name].add((row[14],row[15],row[16],row[17],row[18],row[19]));top[(row[10],row[9],name,row[11])]+=row[7]-row[6]
   if row[10] or row[9]:assert row[10]>0 and row[9]>0;groups[row[10]][row[9]]+=1
  repeated=[]
  for nodes in groups.values():assert len(set(nodes.values()))==1;repeated.append(next(iter(nodes.values())))
  ck(identity+' known full graph replay counts',sorted(repeated)==[9,199,199])
  total=sum(row[7]-row[6] for row in ks);ck(identity+' union/sum replay',near(total/1e6,q['traces'][identity]['summed_kernel_ms']) and near(union(ks)/1e6,q['traces'][identity]['kernel_union_ms']))
  for name,n in count.items():
   duration=sum(row[7]-row[6] for row in ks if names(row)==name);item=q['traces'][identity]['families'][name];ck(identity+' '+name+' raw family sum',near(duration/1e6,item['summed_ms']) and near(100*duration/total,item['share_of_summed_kernel_time_pct']) and n==item['count']);families[name].append({'summed_ms':duration/1e6,'share_pct':100*duration/total})
  trace_details[identity]={'kernels':len(ks),'attributes_observed':{k:[list(x) for x in sorted(v)] for k,v in attributes.items()},'top_graph_nodes_by_summed_duration':[{'graph':g,'node':n,'kernel':name,'grid_x':grid,'summed_ms':value/1e6} for (g,n,name,grid),value in sorted(top.items(),key=lambda x:x[1],reverse=True)[:12]],'traced_kernel_union_ms':union(ks)/1e6,'traced_kernel_sum_ms':total/1e6}
  rawpin[str(directory/'trace.bin')]=old.sha(directory/'trace.bin');rawpin[str(directory/'collector.jsonl')]=old.sha(directory/'collector.jsonl')
for pair,declared in zip(P['pairs'],q['pairs']):
 b,t=reports[pair['baseline']],reports[pair['trace']];cycle=100*(t['results'][0]['full_cycle_ms']/b['results'][0]['full_cycle_ms']-1);process=100*(t['process_wall_ms']/b['process_wall_ms']-1);outer=100*(old.read(E/(pair['trace']+'.outer-wall.json'))['elapsed_ms']/old.read(E/(pair['baseline']+'.outer-wall.json'))['elapsed_ms']-1);ck(pair['trace']+' observer arithmetic',near(cycle,declared['cycle_change_pct']) and near(process,declared['process_change_pct']) and near(outer,declared['runner_wall_change_pct']));ck(pair['trace']+' all three clocks pass preset10%',abs(cycle)<=10 and abs(process)<=10 and abs(outer)<=10 and declared['usefulness_pass'])
summary=[{'kernel':name,'invocations_each_trace':counts_reference[name],'median_summed_ms':statistics.median(x['summed_ms'] for x in samples),'median_share_of_traced_kernel_time_pct':statistics.median(x['share_pct'] for x in samples),'share_range_pct':[min(x['share_pct'] for x in samples),max(x['share_pct'] for x in samples)]} for name,samples in families.items()];summary.sort(key=lambda row:row['median_summed_ms'],reverse=True)
assert summary[0]['kernel']=='up_action';R=ROOT/'comparisons/D085-activity-root-check';R.mkdir();report={'at':old.now(),'status':'pass_scoped_activity_diagnostic','checks':checks,'checks_passed':len(checks),'native_results_exact':6,'convergence_checkpoints_exact':60,'kernels_each_trace':26230,'all_graph_repetitions_and_counts_repeat':True,'collector_errors_drops_bad_times_outstanding_buffers':0,'parent_elevated':bool(ctypes.windll.shell32.IsUserAnAdmin()),'observer_cycle_changes_pct':[x['cycle_change_pct'] for x in q['pairs']],'observer_native_process_changes_pct':[x['process_change_pct'] for x in q['pairs']],'observer_outer_runner_changes_pct':[x['runner_wall_change_pct'] for x in q['pairs']],'families':summary,'trace_details':trace_details,'primary_cohort_report_sha256':old.sha(H/'cohort-report.json'),'preserved_raw_sha256':rawpin,'accepted_source':'E051','accepted_cumulative_gain_unchanged':12.4372274192464,'optimization_accepted':False,'root_external_independent_review':False,'limits':'Only rainbow/thisGPU/warm protocol. Low outer perturbation is a usefulness screen, not a per-family bias bound. Summed traced kernel durations may overlap; they are not full-cycle wall time, removable savings or an optimization gain. No source candidate admitted by this diagnostic alone.'};old.save(R/'report.json',report)
directories=[(H,H.name),(R,R.name)]+[(ROOT/'runs'/i,i) for i in P['order']];published={}
for directory,prefix in directories:
 for src in directory.rglob('*'):
  if not src.is_file() or 'vendor' in src.parts or src.suffix in ['.exe','.dll','.pdb','.obj','.lib','.exp'] or '__pycache__' in src.parts:continue
  key=prefix+'/'+src.relative_to(directory).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data,key
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(R/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published,'vendor_archives_remain_local_with_official_urls_and_checksums':True,'accepted_source_unchanged':True})
links=[{'label':label,'url':'evidence/'+key} for label,key in [('D085 validated activity hotspots and root replay','D085-activity-root-check/report.json'),('D085 six-run observer/state comparison','D085-cupti-activity/cohort-report.json'),('D085 collector source, explicit lifecycle','D085-cupti-activity/collector.cpp'),('D085 full raw trace1','D085-cupti-activity/cohort-execution/traces/D085T1/trace.bin')]]
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert s['accepted_complete_run']['candidate_id']=='E051';e=next(x for x in s['experiments'] if x['id']=='D085');e.update(status='measured',stage='Low-overhead activity profile validated',correctness='pass',accepted=False,reason='Non-elevated collector works; each trace26230kernels, full3graph repeats9/199/199,zero dropped/error/incomplete records. All6states/60checkpoints exact. Observer complete-cycle+0.4475/+0.6672/+1.1589%. Traced kernel time: action-up35.6%,showdown29.7%,action-down17.2%; these are diagnostic shares, not speedups.');e['evidence']+=links;s['evidence']+=links;s.update(updated_at=old.now(),stage='D085 profile validated; next action-update hypothesis',activity='New low-overhead GPU activity channel verified. Prioritize dominant action-update work after closed-evidence review. AcceptedE05112.437227%unchanged; no optimization adopted.',active_experiment=None);old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'status':'pass_scoped_activity_diagnostic','checks':len(checks),'top3':summary[:3],'http_verified_files':len(published),'report_sha256':old.sha(R/'report.json')}),flush=True)
