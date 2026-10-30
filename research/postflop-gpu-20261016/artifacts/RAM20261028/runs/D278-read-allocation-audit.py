import collections,json,re,statistics,struct,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D278-allocation-activity-audit';P=h.read(H/'protocol.json');assert len(sys.argv)==2;h.pin(H/'protocol.json',sys.argv[1])
for p,d in P['input_sha256'].items():h.pin(p,d)
h.custody();checks=0;schema=struct.Struct('<6I4Q10I80s');assert schema.size==176
def req(v):
    global checks
    assert v;checks+=1
names={int(n):name for name,n in re.findall(r'CUPTI_DRIVER_TRACE_CBID_(\w+)\s*=\s*(\d+)',(ROOT/'runs/D212-current-RAM-activity/private/cupti_driver_cbid.h').read_text(encoding='utf-8'))};req(len(names)>500)
def union(rows):
    end=None;total=0
    for a,b in sorted((r['start'],r['end'])for r in rows):
        if end is None or a>=end:total+=b-a;end=b
        elif b>end:total+=b-end;end=b
    return total
def describe(rows):
    apis=[r for r in rows if r['kind']==4];grouped=collections.defaultdict(list)
    for r in apis:grouped[names.get(r['detail'],'UNKNOWN_CBID_'+str(r['detail']))].append(r)
    summary={name:{'count':len(rs),'summed_wall_ms':sum(r['end']-r['start']for r in rs)/1e6,'union_wall_ms':union(rs)/1e6,'max_single_wall_ms':max(r['end']-r['start']for r in rs)/1e6,'return_value_counts':dict(collections.Counter(str(r['graph'])for r in rs)),'process_ids':sorted(set(r['context']for r in rs)),'thread_count':len(set(r['stream']for r in rs))}for name,rs in grouped.items()}
    copies=[r for r in rows if r['kind']==1];sets=[r for r in rows if r['kind']==2];kernels=[r for r in rows if r['kind']in[3,10]]
    kinds={str(k):{'count':len([r for r in rows if r['kind']==k]),'summed_wall_ms':sum(r['end']-r['start']for r in rows if r['kind']==k)/1e6,'union_wall_ms':union([r for r in rows if r['kind']==k])/1e6}for k in sorted(set(r['kind']for r in rows))}
    req(sum(x['count']for x in summary.values())==len(apis));req(sum(x['count']for x in kinds.values())==len(rows))
    return{'record_count':len(rows),'record_kinds':kinds,'all_API_records':len(apis),'all_API_union_wall_ms':union(apis)/1e6,'all_API_summed_wall_ms':sum(r['end']-r['start']for r in apis)/1e6,'APIs':summary,'copies_by_direction':{str(d):{'count':sum(r['detail']==d for r in copies),'bytes':sum(r['bytes']for r in copies if r['detail']==d)}for d in sorted(set(r['detail']for r in copies))},'memset_count':len(sets),'memset_bytes':sum(r['bytes']for r in sets),'kernels':len(kernels)}
traces=[];raw_records=0
for trace in P['traces']:
    path=Path(trace['trace_path']);h.pin(path,trace['trace_sha256']);h.pin(trace['meta_path'],trace['meta_sha256']);raw=path.read_bytes();req(raw[:16]==b'D087-TRACE-v1\0\0\0'and(len(raw)-16)%176==0);rows=[]
    for values in schema.iter_unpack(raw[16:]):
        r=dict(zip(['kind','device','context','stream','correlation','detail','start','end','bytes','graph_node','graph','gx','gy','gz','bx','by','bz','regs','static_shared','dynamic_shared','name'],values));req(r['kind']in[1,2,3,4,10]and r['device']==0 and r['start']>0 and r['end']>=r['start']);rows.append(r)
    metadata=[json.loads(x)for x in Path(trace['meta_path']).read_text(encoding='utf-8').splitlines()];req([x['event']for x in metadata]==['start']+['phase']*18+['complete']);req([x['marker']for x in metadata[1:-1]]==list(range(1,19)));done=metadata[-1];req(all(done[k]==0 for k in['errors','dropped','invalid_timestamps','outstanding_buffers'])and done['records']==len(rows));req(done['driver_api_records']==sum(r['kind']==4 for r in rows));phases={x['marker']:x['timestamp_ns']for x in metadata[1:-1]};req(all(a<b for a,b in zip(list(phases.values()),list(phases.values())[1:])));buckets=[];assigned=set();crossings=[]
    for i,fixture in enumerate(P['fixtures']):
        for stage,(lo_index,hi_index)in P['phase_markers_per_fixture'].items():
            lo,hi=phases[i*6+lo_index],phases[i*6+hi_index];contained=[]
            for index,r in enumerate(rows):
                if lo<=r['start']and r['end']<=hi:
                    req(index not in assigned);assigned.add(index);contained.append(r)
                elif r['start']<hi and r['end']>lo:crossings.append({'fixture':fixture,'stage':stage,'record_index':index,'kind':r['kind'],'API':names.get(r['detail'])if r['kind']==4 else None,'start':r['start'],'end':r['end']})
            buckets.append({'fixture':fixture,'stage':stage,'phase_span_ms':(hi-lo)/1e6,**describe(contained)})
    outside=[r for i,r in enumerate(rows)if i not in assigned];req(sum(x['record_count']for x in buckets)+len(outside)==len(rows));whole=describe(rows);outside_summary=describe(outside);unknown=[name for name in whole['APIs']if name.startswith('UNKNOWN')]
    async_calls={name:data for name,data in whole['APIs'].items()if re.match(r'cuMemAlloc(FromPool)?Async',name)};sync_calls={name:data for name,data in whole['APIs'].items()if re.match(r'cuMemAlloc(_v\d+)?(_ptsz)?$',name)}
    req(all(all(key=='0'for key in v['return_value_counts'])for v in async_calls.values()));traces.append({'id':trace['id'],'whole_raw_sha256':trace['trace_sha256'],'raw_bytes':len(raw),'whole':whole,'phases':buckets,'outside_named_phases':outside_summary,'cross_phase_records_retained_in_outside_bucket':crossings,'unknown_driver_callback_names':unknown,'successful_stream_ordered_allocation_API_records':sum(x['count']for x in async_calls.values()),'synchronous_ordinary_allocation_API_records':sum(x['count']for x in sync_calls.values())});raw_records+=len(rows);print(trace['id'],'all',len(rows),'records accounted; async allocations',sum(x['count']for x in async_calls.values()),flush=True);h.custody()
medians=[]
for fixture in P['fixtures']:
    for stage in P['phase_markers_per_fixture']:
        phase_rows=[next(p for p in t['phases']if p['fixture']==fixture and p['stage']==stage)for t in traces];all_names=sorted({n for row in phase_rows for n in row['APIs']});api_medians={name:{'median_summed_wall_ms':statistics.median(row['APIs'].get(name,{'summed_wall_ms':0})['summed_wall_ms']for row in phase_rows),'counts':[row['APIs'].get(name,{'count':0})['count']for row in phase_rows]}for name in all_names};medians.append({'fixture':fixture,'stage':stage,'median_observer_span_ms':statistics.median(x['phase_span_ms']for x in phase_rows),'median_API_union_wall_ms':statistics.median(x['all_API_union_wall_ms']for x in phase_rows),'APIs':api_medians,'limits':'Per-family medians/sums and API waits are not additive or removable; no primary timing sample or full-cycle bound.'})
async_confirmed=all(t['successful_stream_ordered_allocation_API_records']>0 for t in traces);h.custody();h.save(H/'report.json',{'id':'D278','at':h.now(),'status':'pass_scoped_retained_allocation_API_activity_audit','protocol_sha256':sys.argv[1],'traces':traces,'phase_medians':medians,'reader_checks':checks,'raw_records_all_accounted':raw_records,'stream_ordered_allocation_observed_all3traces':async_confirmed,'new_optimizer_candidate_created':False,'new_compilers_native_GPU_CFR_solver_or_speed_samples':0,'scope_limits':P['scope']+' '+P['interpretation'],'next':'Do not propose enabling already observed stream-ordered allocation or ignored legacy eager-commit flag. Classify all actual initialization/API costs and semantic closed-family aliases before a distinct next source. No speed gain or source admission from this census.'});print(json.dumps({'status':'pass','raw_records':raw_records,'async_observed_all3':async_confirmed,'init_top_API_wall_sums':[{'fixture':row['fixture'],'top':sorted([(name,data['median_summed_wall_ms'])for name,data in row['APIs'].items()],key=lambda x:-x[1])[:8]}for row in medians if row['stage']=='init']}),flush=True)
