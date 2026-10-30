"""Prepare fixed driver/phase cohort without changing the primary evaluator."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
H=ROOT/'runs/D087-cupti-driver-profile';prior=ROOT/'runs/D085-cupti-activity'
old.custody()
s=(prior/'run-cohort.py').read_text(encoding='utf-8').replace('D085','D087')
s=s.replace('import json,os,struct,sys,time','import json,os,re,struct,sys,time')
needle="   meta=[json.loads(x) for x in (directory/'collector.jsonl').read_text().splitlines()];assert [x['event'] for x in meta]==['start','complete'];complete=meta[-1];"
replacement="   meta=[json.loads(x) for x in (directory/'collector.jsonl').read_text().splitlines()];assert [x['event'] for x in meta]==['start']+['phase']*6+['complete'];assert [x['marker'] for x in meta[1:-1]]==list(range(1,7));assert all(a['timestamp_ns']<b['timestamp_ns'] for a,b in zip(meta[1:-2],meta[2:-1]));complete=meta[-1];"
assert s.count(needle)==1;s=s.replace(needle,replacement)
s=s.replace("'all_device_activity_union_ms':union_ns(rows)/1e6,'device_activity_span_ms':(max(r['end'] for r in rows)-min(r['start'] for r in rows))/1e6","'all_device_activity_union_ms':union_ns([r for r in rows if r['kind']!=4])/1e6,'device_activity_span_ms':(max(r['end'] for r in rows if r['kind']!=4)-min(r['start'] for r in rows if r['kind']!=4))/1e6")
needle=";old.save(directory/'parsed.json',traces[identity])"
assert s.count(needle)==1
extra='''
   names={int(n):name for name,n in re.findall(r'CUPTI_DRIVER_TRACE_CBID_(\\w+)\\s*=\\s*(\\d+)',Path(P['driver_cbid_header']).read_text())};assert len(names)>500
   apis=[r for r in rows if r['kind']==4];assert len(apis)==complete['driver_api_records'] and len(apis)>0
   assert all(r['detail'] in names and r['context']>0 and r['stream']>0 and r['correlation']>0 for r in apis)
   by_id={r['correlation']:r for r in apis};assert len(by_id)==len(apis)
   for r in kernels:
    assert r['correlation'] in by_id
    assert names[by_id[r['correlation']]['detail']] in (['cuGraphLaunch','cuGraphLaunch_ptsz'] if r['graph'] else ['cuLaunchKernel','cuLaunchKernel_ptsz'])
   graph_api=[r for r in apis if names[r['detail']] in ['cuGraphLaunch','cuGraphLaunch_ptsz']]
   assert len(graph_api)==sum(P['expected_graph_kernel_node_repeat_counts'])==407 and all(r['graph']==0 for r in graph_api)
   phases={r['marker']:r['timestamp_ns'] for r in meta[1:-1]};phase_reports={}
   def clipped(source,lo,hi):return [dict(r,start=max(r['start'],lo),end=min(r['end'],hi)) for r in source if r['start']<hi and r['end']>lo]
   device=[r for r in rows if r['kind']!=4]
   for label,a,b in [('init',1,2),('solve',3,4),('readback',5,6)]:
    lo,hi=phases[a],phases[b];d=clipped(device,lo,hi);api=clipped(apis,lo,hi);both=union_ns(d+api);du=union_ns(d);au=union_ns(api)
    fs=[]
    for name in {names[r['detail']] for r in api}:
     rs=[r for r in api if names[r['detail']]==name];u=union_ns(rs);overlap=union_ns(rs)+du-union_ns(rs+d)
     fs.append({'api':name,'calls':len(rs),'summed_ms':sum(r['end']-r['start'] for r in rs)/1e6,'union_ms':u/1e6,'device_overlap_ms':overlap/1e6,'api_union_without_device_activity_ms':(u-overlap)/1e6,'nonzero_returns':sum(r['graph']!=0 for r in rs)})
    fs.sort(key=lambda r:r['union_ms'],reverse=True)
    phase_reports[label]={'span_ms':(hi-lo)/1e6,'device_union_ms':du/1e6,'api_union_ms':au/1e6,'api_device_overlap_ms':(du+au-both)/1e6,'device_uncovered_ms':((hi-lo)-du)/1e6,'uncovered_by_device_or_api_ms':((hi-lo)-both)/1e6,'api_counts':dict(Counter(names[r['detail']] for r in api)),'device_kind_counts':dict(Counter(r['kind'] for r in d)),'api_functions':fs}
   traces[identity].update(driver_api_records=len(apis),all_kernel_APIcorrelations_exact=True,graph_launch_API_records=len(graph_api),phase_timestamps_ns=phases,phases=phase_reports,API_time_limit='API calls may wait on GPU execution. CPU/API and GPU times overlap; these intervals are not removable overhead or complete-cycle gains.')
   old.save(directory/'parsed.json',traces[identity])'''
s=s.replace(needle,extra)
s=s.replace("'all_kernel_family_counts_repeatable':True,","'all_kernel_family_counts_repeatable':True,'all_driver_API_kernel_correlations_exact':True,'all_phase_timestamps_valid':True,")
assert 'D085' not in s
(H/'run-cohort.py').write_text(s,encoding='utf-8',newline='\n')
s=(prior/'freeze-cohort.py').read_text(encoding='utf-8').replace('D085','D087').replace("H/'build-r3","H/'build")
header=prior/'vendor/cuda_cupti/cuda_cupti-windows-x86_64-12.9.79-archive/include/cupti_driver_cbid.h'
s=s.replace("'fixture':'rainbow','storage'","'driver_cbid_header':r'"+str(header)+"','fixture':'rainbow','storage'")
s=s.replace("H/'collector.cpp']","H/'collector.cpp',Path(r'"+str(header)+"'),H/'proposal.json',H/'gap-census.json',H/'diagnostic-draft-r1/failure.json']")
s=s.replace('all node repeats9,199,199; identical kernel-family invocation counts','all node repeats9,199,199;407successfulGraphLaunchAPIrecords and exact correlation join for everykernel; six strictlyordered phase timestamps; identical kernel-family invocation counts')
s=s.replace('to locate work inside captured graphs','to locate hostAPI/device overlap in init/solve/readback')
s=s.replace('D087 matched activity profiling','D087 matched API and phase profiling')
assert 'build-r3' not in s
(H/'freeze-cohort.py').write_text(s,encoding='utf-8',newline='\n')
print('D087 fixed cohort source prepared; no new native work launched.',flush=True)
