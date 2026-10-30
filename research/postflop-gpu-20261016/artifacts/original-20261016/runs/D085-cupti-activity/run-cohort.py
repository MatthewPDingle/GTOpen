import json,os,struct,sys,time
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'cohort-plan.json',sys.argv[1]);P=old.read(H/'cohort-plan.json');E=H/'cohort-execution';schema=struct.Struct('<6I4Q10I80s')
def verify():
 old.pin(H/'cohort-plan.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
def exact(report,log):
 raw=log.read_text();rows=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in raw.splitlines() if 'AUTORESEARCH_RESULT ' in x];assert rows==report['results'] and len(rows)==1 and rows[0]['fixture_id']=='rainbow' and rows[0]['iteration']==200 and rows[0]['target_met']
 stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in raw.splitlines() if 'AUTORESEARCH_STAGE ' in x];checks=[{k:r[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for r in stages if r.get('stage')=='convergence_check'];assert [r['iteration'] for r in checks]==list(range(20,201,20))
 return ({k:v for k,v in rows[0].items() if k not in old.historical.EXCLUDED},checks)
def union_ns(rows):
 end=None;total=0
 for a,b in sorted((r['start'],r['end']) for r in rows):
  if end is None or a>=end:total+=b-a;end=b
  elif b>end:total+=b-end;end=b
 return total
verify();assert not (ROOT/'gpu-run.lock').exists() and not E.exists();E.mkdir();(E/'traces').mkdir();reference=old.historical.exact_raw('E020C1');anchor=(reference[0][0],[r for r in reference[1] if r['fixture_id']=='rainbow']);records={};traces={};family_counts=None;wrapper_ms={}
try:
 for identity in P['order']:
  verify();old.ar.refuse_active(old.ar.live_status());arm='trace' if identity.startswith('D085T') else 'baseline';binary=P['binaries'][arm];env=old.env();env.pop('D085_TRACE_FILE',None);env.pop('D085_META_FILE',None);assert not env.get('CUDA_INJECTION64_PATH') and not env.get('CUDA_INJECTION32_PATH')
  if arm=='trace':
   directory=E/'traces'/identity;directory.mkdir();env['PATH']=os.pathsep.join(P['private_dll_dirs'])+os.pathsep+env['PATH'];env['D085_TRACE_FILE']=str(directory/'trace.bin');env['D085_META_FILE']=str(directory/'collector.jsonl')
  old.save(E/(identity+'.environment.json'),{'at':old.now(),'arm':arm,'private_dll_dirs':P['private_dll_dirs'] if arm=='trace' else [],'trace_file':env.get('D085_TRACE_FILE'),'meta_file':env.get('D085_META_FILE'),'fixture':'rainbow','storage':'compressed','postscore_profile':'0'})
  cmd=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',identity,'--title','D085 '+identity,'--kind','diagnostic','--binary',binary['path'],'--build-manifest',binary['manifest'],'--test','postflop_complete_cycle','--fixture','rainbow'];started=time.monotonic();old.child(cmd,E,identity,env,1200);wrapper_ms[identity]=(time.monotonic()-started)*1000;old.save(E/(identity+'.outer-wall.json'),{'elapsed_ms':wrapper_ms[identity],'scope':'Entire ar runner child, including its preflight/evidence work; distinct from native/complete-cycle clocks.'});verify()
  report=old.read(ROOT/'runs'/identity/'report.json');log=ROOT/'runs'/identity/'stdout.log';old.pin(log,report['stdout_sha256']);assert report['status']=='measured' and report['returncode']==0 and report['binary_sha256']==binary['sha256'] and report['binary_build_manifest']['sha256']==binary['manifest_sha256'];assert exact(report,log)==anchor;records[identity]=report
  if arm=='trace':
   data=(directory/'trace.bin').read_bytes();assert data[:16]==b'D085-TRACE-v1\0\0\0' and (len(data)-16)%176==0;rows=[]
   for v in schema.iter_unpack(data[16:]):
    row=dict(zip(['kind','device','context','stream','correlation','detail','start','end','bytes','graph_node','graph','gx','gy','gz','bx','by','bz','regs','static_shared','dynamic_shared','name'],v));row['name']=row['name'].split(b'\0',1)[0].decode();assert row['device']==0 and row['start']>0 and row['end']>=row['start'];rows.append(row)
   meta=[json.loads(x) for x in (directory/'collector.jsonl').read_text().splitlines()];assert [x['event'] for x in meta]==['start','complete'];complete=meta[-1];assert all(complete[k]==0 for k in ['errors','dropped','invalid_timestamps','outstanding_buffers']) and complete['records']==len(rows)
   kernels=[r for r in rows if r['kind'] in [3,10]];assert len(kernels)==complete['kernels']
   expected={'copy_root','down_action','down_chance','up_fold','up_show','up_chance','up_action','copy_span','up_action_eval'};assert {r['name'] for r in kernels}<=expected
   counts=dict(Counter(r['name'] for r in kernels))
   if family_counts is None:family_counts=counts
   assert counts==family_counts
   groups=defaultdict(lambda:defaultdict(list))
   for r in kernels:
    if r['graph'] or r['graph_node']:assert r['graph']>0 and r['graph_node']>0;groups[r['graph']][r['graph_node']].append(r)
   repeats=[];group_report=[]
   for graph,nodes in groups.items():
    values={len(v) for v in nodes.values()};assert len(values)==1;repeat=values.pop();repeats.append(repeat);group_report.append({'graph_id':graph,'kernel_nodes':len(nodes),'repeats_each_node':repeat,'families':dict(Counter(v[0]['name'] for v in nodes.values()))})
   assert sorted(repeats)==P['expected_graph_kernel_node_repeat_counts']
   summed=sum(r['end']-r['start'] for r in kernels);families={name:{'count':counts[name],'summed_ms':sum(r['end']-r['start'] for r in kernels if r['name']==name)/1e6,'share_of_summed_kernel_time_pct':sum(r['end']-r['start'] for r in kernels if r['name']==name)/summed*100} for name in counts}
   traces[identity]={'records':len(rows),'collector':complete,'kernel_family_counts':counts,'families':families,'graph_groups':group_report,'summed_kernel_ms':summed/1e6,'kernel_union_ms':union_ns(kernels)/1e6,'all_device_activity_union_ms':union_ns(rows)/1e6,'device_activity_span_ms':(max(r['end'] for r in rows)-min(r['start'] for r in rows))/1e6,'raw_trace_sha256':old.sha(directory/'trace.bin'),'metadata_sha256':old.sha(directory/'collector.jsonl'),'scope':'Traced activity only; family sums may overlap and are not uninstrumented wall-time attribution or removable speed headroom.'};old.save(directory/'parsed.json',traces[identity])
  print('D085 completed',identity,flush=True)
 changes=[]
 for pair in P['pairs']:
  b,t=records[pair['baseline']],records[pair['trace']];full=(t['results'][0]['full_cycle_ms']/b['results'][0]['full_cycle_ms']-1)*100;wall=(t['process_wall_ms']/b['process_wall_ms']-1)*100;outer=(wrapper_ms[pair['trace']]/wrapper_ms[pair['baseline']]-1)*100;changes.append({'baseline_id':pair['baseline'],'trace_id':pair['trace'],'baseline_cycle_ms':b['results'][0]['full_cycle_ms'],'trace_cycle_ms':t['results'][0]['full_cycle_ms'],'cycle_change_pct':full,'baseline_process_ms':b['process_wall_ms'],'trace_process_ms':t['process_wall_ms'],'process_change_pct':wall,'baseline_runner_wall_ms':wrapper_ms[pair['baseline']],'trace_runner_wall_ms':wrapper_ms[pair['trace']],'runner_wall_change_pct':outer,'usefulness_pass':abs(full)<=10 and abs(wall)<=10 and abs(outer)<=10})
 passed=all(x['usefulness_pass'] for x in changes);old.save(H/'cohort-report.json',{'at':old.now(),'status':'pass_scoped_activity_diagnostic' if passed else 'diagnostic_observer_perturbation_exceeds_gate','protocol_sha256':sys.argv[1],'pairs':changes,'traces':traces,'all6full_results_60checkpoints_exact':True,'all_expected_graph_repeats_verified':True,'all_kernel_family_counts_repeatable':True,'no_drops_or_collector_errors':True,'observer_usefulness_pass':passed,'excluded_samples':[],'extension_runs':0,'historical_timing_samples_used':0,'optimization_accepted':False,'accepted_source':'E051','scope':P['scope'],'limits':'No confidence or native per-family bias bound; summed kernel intervals are not complete-cycle wall time. This diagnostic does not establish a speedup.'});old.save(E/'complete.json',{'at':old.now(),'all_children_terminal':True,'order':P['order'],'report_sha256':old.sha(H/'cohort-report.json'),'accepted_source_unchanged':True});print(json.dumps({'status':'cohort_terminal','observer_pass':passed,'changes':changes,'report_sha256':old.sha(H/'cohort-report.json')}),flush=True)
except BaseException as exc:
 old.save(E/'failure.json',{'at':old.now(),'error':repr(exc),'completed_ids':list(records),'optimization_accepted':False});raise
