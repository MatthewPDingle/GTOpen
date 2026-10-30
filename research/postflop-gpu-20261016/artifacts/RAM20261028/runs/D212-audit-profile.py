import collections,json,re,statistics,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D212-current-RAM-activity';P=h.read(H/'protocol.json');schema=struct.Struct('<6I4Q10I80s');assert schema.size==176
for p,d in P['input_sha256'].items():h.pin(p,d)
checks=0
def req(v,label):
 global checks
 assert v,label;checks+=1
def union(rows):
 end=None;total=0
 for a,b in sorted((x['start'],x['end']) for x in rows):
  if end is None or a>=end:total+=b-a;end=b
  elif b>end:total+=b-end;end=b
 return total
def clip(rows,lo,hi):return [dict(x,start=max(x['start'],lo),end=min(x['end'],hi)) for x in rows if x['start']<hi and x['end']>lo]
names={int(n):name for name,n in re.findall(r'CUPTI_DRIVER_TRACE_CBID_(\w+)\s*=\s*(\d+)',(H/'private/cupti_driver_cbid.h').read_text(encoding='utf-8'))};req(len(names)>500,'exact SDK driver API names')
reports={};traces={};counts=None;rawpins={};receipts={}
for row in P['sequence']:
 ident=row['id'];D=ROOT/'runs'/ident;r=h.read(D/'report.json');receipt=h.read(D/'exit.json');reports[ident]=r;receipts[ident]=receipt;req(receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None,'native terminal');req(h.exact(ident)==h.read(ROOT/'epoch/exact-anchor.json'),'entire original science and23checkpoints');h.pin(D/'stdout.log',r['stdout_sha256'])
 if row['arm']!='trace':continue
 data=(D/'trace.bin').read_bytes();req(data[:16]==b'D087-TRACE-v1\0\0\0' and (len(data)-16)%176==0,'whole raw trace schema');req(len(data)<=P['raw_reservation_bytes']//3,'raw reservation');rows=[]
 for v in schema.iter_unpack(data[16:]):
  x=dict(zip(['kind','device','context','stream','correlation','detail','start','end','bytes','graph_node','graph','gx','gy','gz','bx','by','bz','regs','static_shared','dynamic_shared','name'],v));x['name']=x['name'].split(b'\0',1)[0].decode();req(x['device']==0 and x['start']>0 and x['end']>=x['start'],'valid raw timestamps/device');rows.append(x)
 meta=[json.loads(x) for x in (D/'collector.jsonl').read_text(encoding='utf-8').splitlines()];req([x['event'] for x in meta]==['start']+['phase']*18+['complete'],'entire collector lifetime');req([x['marker'] for x in meta[1:-1]]==list(range(1,19)),'all original fixture phase markers');phases={x['marker']:x['timestamp_ns'] for x in meta[1:-1]};req(all(a<b for a,b in zip(phases.values(),list(phases.values())[1:])),'ordered phase timestamps');complete=meta[-1];req(all(complete[k]==0 for k in ['errors','dropped','invalid_timestamps','outstanding_buffers']) and complete['records']==len(rows),'complete successful trace no drops');req(meta[0]['explicit_lifetime'] and not meta[0]['hardware_counters'],'no counters')
 kernels=[x for x in rows if x['kind'] in [3,10]];apis=[x for x in rows if x['kind']==4];req(len(kernels)==complete['kernels'] and len(apis)==complete['driver_api_records'],'all recorded kernel/API counts');req(set(x['name'] for x in kernels)<=set(h.read(ROOT/'runs/E105-resource/protocol.json')['original_entries']),'original kernel family only')
 req(all(x['detail'] in names and x['context']>0 and x['stream']>0 and x['correlation']>0 for x in apis),'actual successful API correlation domains');by_id={x['correlation']:x for x in apis};req(len(by_id)==len(apis),'unique API correlations')
 for x in kernels:
  req(x['correlation'] in by_id,'kernel/API correlation');a=by_id[x['correlation']];req(a['graph']==0 and names[a['detail']] in (['cuGraphLaunch','cuGraphLaunch_ptsz'] if x['graph'] else ['cuLaunchKernel','cuLaunchKernel_ptsz']),'successful original launch/replay API')
 per_fixture={}
 for i,f in enumerate(['rainbow','two-tone','river']):
  lo,hi=phases[i*6+3],phases[i*6+4];ks=[x for x in kernels if lo<=x['start'] and x['end']<=hi];req(ks and all(x['end']>=lo and x['start']<=hi for x in ks),'solve kernel containment');req(all(x['start']>=lo and x['end']<=hi for x in kernels if x['start']<hi and x['end']>lo),'no partial solve kernel clipping')
  groups=collections.defaultdict(lambda:collections.defaultdict(list))
  for x in ks:
   if x['graph'] or x['graph_node']:req(x['graph']>0 and x['graph_node']>0,'actual graph identities');groups[x['graph']][x['graph_node']].append(x)
  repeats=[]
  for graph,nodes in groups.items():
   q={len(v) for v in nodes.values()};req(len(q)==1,'each graph node repeats identically');repeats.append(q.pop())
  req(sorted(repeats)==P['expected_graph_repeats_per_fixture'][f],'all original graph repeats');launches=[a for a in apis if lo<=a['start'] and a['end']<=hi and names[a['detail']] in ['cuGraphLaunch','cuGraphLaunch_ptsz']];req(len(launches)==sum(P['expected_graph_repeats_per_fixture'][f]),'all original graph launch calls')
  family_counts=dict(collections.Counter(x['name'] for x in ks));families={n:{'count':family_counts[n],'summed_ms':sum(x['end']-x['start'] for x in ks if x['name']==n)/1e6,'union_ms':union([x for x in ks if x['name']==n])/1e6} for n in family_counts};req('up_action_eval' in families,'actual evaluation entry recorded');per_fixture[f]={'kernel_family_counts':family_counts,'families':families,'kernel_union_ms':union(ks)/1e6,'summed_kernel_ms':sum(x['end']-x['start'] for x in ks)/1e6,'graph_repeats':sorted(repeats),'graph_launch_API_calls':len(launches),'solve_span_ms':(hi-lo)/1e6}
 cc={f:x['kernel_family_counts'] for f,x in per_fixture.items()}
 if counts is None:counts=cc
 req(counts==cc,'every actual family count repeatable across3traces');traces[ident]={'fixtures':per_fixture,'collector':complete,'whole_raw_trace_sha256':h.sha(D/'trace.bin'),'metadata_sha256':h.sha(D/'collector.jsonl'),'all_original_kernel_API_correlations_exact':True};rawpins[str(D/'trace.bin')]=h.sha(D/'trace.bin');rawpins[str(D/'collector.jsonl')]=h.sha(D/'collector.jsonl');print('D212 raw trace complete',ident,flush=True)
pairs=[]
for pair in P['pairs']:
 b,t=reports[pair['baseline']],reports[pair['trace']];bs=sum(x['full_cycle_ms'] for x in b['results']);ts=sum(x['full_cycle_ms'] for x in t['results']);diff={'suite':100*(ts/bs-1),'native_lifetime':100*(receipts[pair['trace']]['terminal_process_times']['lifetime_ms']/receipts[pair['baseline']]['terminal_process_times']['lifetime_ms']-1),'parent_wall':100*(receipts[pair['trace']]['parent_wall_ms']/receipts[pair['baseline']]['parent_wall_ms']-1)}
 for f in ['rainbow','two-tone','river']:diff[f]=100*(next(x['full_cycle_ms'] for x in t['results'] if x['fixture_id']==f)/next(x['full_cycle_ms'] for x in b['results'] if x['fixture_id']==f)-1)
 pairs.append(pair|{'observer_change_pct':diff,'usefulness_pass':all(abs(v)<=10 for v in diff.values())})
useful=all(x['usefulness_pass'] for x in pairs);baseline=sum(statistics.median(next(x['full_cycle_ms'] for x in reports[p['baseline']]['results'] if x['fixture_id']==f) for p in P['pairs']) for f in ['rainbow','two-tone','river']);family_medians={n:{f:statistics.median(traces[p['trace']]['fixtures'][f]['families'].get(n,{'summed_ms':0})['summed_ms'] for p in P['pairs']) for f in ['rainbow','two-tone','river']} for n in sorted({n for tr in traces.values() for x in tr['fixtures'].values() for n in x['families']})};target=sum(family_medians['up_action_eval'].values());budget=baseline*.01
h.custody();h.save(H/'report.json',{'id':'D212','at':h.now(),'status':'pass_scoped_current_RAM_activity_diagnostic' if useful else 'diagnostic_observer_usefulness_failed','protocol_sha256':h.sha(H/'protocol.json'),'pairs':pairs,'traces':traces,'family_fixture_median_summed_ms':family_medians,'observer_usefulness_pass':useful,'all18full_scientific_records_and138checkpoints_exact':True,'all_original_graph_repeats_and_API_correlations_exact':True,'all_family_counts_repeatable':True,'no_collector_errors_drops_invalid_timestamps_or_outstanding_buffers':True,'E105_target_budget':{'passed':useful and target>=budget,'current_control_sum_fixture_median_ms':baseline,'planning_one_percent_ms':budget,'target_sum_fixture_median_activity_ms':target,'target_fraction_of_control_pct':100*target/baseline,'historical_timings_scored':0,'scope':'Current observer durations versus fresh control medians are a budgeting proxy. They are not a proven removable saving, complete wall-time attribution, unbiased per-family bound or universal upper limit.'},'reader_checks':checks,'raw_sha256':rawpins,'excluded_samples':[],'extension_runs':0,'performance_qualification_samples':0,'candidate_accepted':False,'source_activated':False,'all_native_processes_terminal':True,'limits':'Finite current3fixture activity with original collector and exact E080. Baseline/trace original quality/cadence/cap/physics match. Observer +/-10% usefulness is coarse and cannot establish per-family bias, significance, causal attribution or actual optimization gain. D104 hardware counters remain closed; no counter APIs called. All source/main/live/PTX unchanged.'})
print(json.dumps({'observer_usefulness_pass':useful,'E105_target_ms':target,'budget_ms':budget,'reader_checks':checks}),flush=True)
