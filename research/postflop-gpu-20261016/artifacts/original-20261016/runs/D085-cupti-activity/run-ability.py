import json,os,struct,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'ability-plan.json',sys.argv[1]);P=old.read(H/'ability-plan.json');E=Path(P['output_dir'])
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();assert not E.exists();E.mkdir();fault=None
try:
 with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
  old.ar.refuse_active(old.ar.live_status());env=old.env();assert not env.get('CUDA_INJECTION64_PATH') and not env.get('CUDA_INJECTION32_PATH')
  env['PATH']=os.pathsep.join(P['private_dll_dirs'])+os.pathsep+env['PATH'];env['D085_TRACE_FILE']=str(E/'trace.bin');env['D085_META_FILE']=str(E/'collector.jsonl')
  old.save(E/'environment.json',{'at':old.now(),'private_dll_dirs':P['private_dll_dirs'],'D085_TRACE_FILE':env['D085_TRACE_FILE'],'D085_META_FILE':env['D085_META_FILE'],'no_injection_or_global_change':True})
  old.child([P['binary']],E,'native',env,60);old.custody()
 raw=(E/'native.stdout.log').read_text();markers=[json.loads(x.split('D085_ABILITY ',1)[1]) for x in raw.splitlines() if 'D085_ABILITY ' in x];assert len(markers)==1 and markers[0]['expected_kernels']==13 and markers[0]['all257words_equal13'] and markers[0]['guards_exact']
 meta=[json.loads(x) for x in (E/'collector.jsonl').read_text().splitlines()];assert [x['event'] for x in meta]==['start','complete'];last=meta[-1]
 assert all(last[k]==0 for k in ['dropped','errors','invalid_timestamps','outstanding_buffers']) and last['kernels']==13
 schema=struct.Struct('<6I4Q10I80s');assert schema.size==176;data=(E/'trace.bin').read_bytes();assert data[:16]==b'D085-TRACE-v1\0\0\0' and (len(data)-16)%schema.size==0;rows=[]
 for values in schema.iter_unpack(data[16:]):
  r=dict(zip(['kind','device','context','stream','correlation','detail','start','end','bytes','graph_node','graph','gx','gy','gz','bx','by','bz','regs','static_shared','dynamic_shared','name'],values));r['name']=r['name'].split(b'\0',1)[0].decode();rows.append(r);assert r['device']==0 and r['start']>0 and r['end']>=r['start']
 assert len(rows)==last['records'];kernels=[r for r in rows if r['kind'] in [3,10]];assert len(kernels)==13 and all(r['name']=='d085_tick' for r in kernels)
 eager=[r for r in kernels if r['graph']==0 and r['graph_node']==0];graph=[r for r in kernels if r['graph']>0 and r['graph_node']>0];assert len(eager)==1 and len(graph)==12 and len({r['graph'] for r in graph})==1 and len({r['graph_node'] for r in graph})==3
 assert all(sum(r['graph_node']==node for r in graph)==4 for node in {r['graph_node'] for r in graph})
 assert all((r['gx'],r['gy'],r['gz'],r['bx'],r['by'],r['bz'])==(3,1,1,128,1,1) for r in kernels)
 ordered=sorted(kernels,key=lambda r:r['start']);assert all(a['end']<=b['start'] for a,b in zip(ordered,ordered[1:]));assert len({(r['start'],r['end'],r['correlation'],r['graph_node']) for r in kernels})==13
 report={'at':old.now(),'status':'pass_activity_graph_feasibility','native_exactness':markers[0],'collector':last,'raw_records':rows,'all13kernels_and12graph_executions_verified':True,'privilege_or_global_change':False,'performance_measured':False,'accepted_source':'E051','source_production_unchanged':True,'protocol_sha256':sys.argv[1],'artifact_sha256':{str(p):old.sha(p) for p in E.iterdir() if p.is_file()}}
 old.save(H/'ability-report.json',report);print(json.dumps({'status':report['status'],'kernel_records':13,'graph_records':12,'total_records':len(rows),'report_sha256':old.sha(H/'ability-report.json')}),flush=True)
except BaseException as exc:
 fault=repr(exc);old.save(E/'failure.json',{'at':old.now(),'error':fault,'no_performance_claim':True});raise
