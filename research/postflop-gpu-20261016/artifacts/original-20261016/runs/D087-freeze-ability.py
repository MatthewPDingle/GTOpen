"""Freeze the native driver/device correlation control before it runs."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D087-cupti-driver-profile';prior=ROOT/'runs/D085-cupti-activity';B=H/'build';C=old.read(B/'complete.json')
assert C['all_compilers_terminal'] and C['native_executions']==0
for p,h in C['artifact_sha256'].items():old.pin(p,h)
s=(prior/'run-ability.py').read_text(encoding='utf-8').replace('D085','D087').replace('d085','d087')
s=s.replace("import json,os,struct,sys","import json,os,re,struct,sys")
s=s.replace("assert [x['event'] for x in meta]==['start','complete'];last=meta[-1]","assert [x['event'] for x in meta]==['start','phase','phase','complete'] and [x['marker'] for x in meta if x['event']=='phase']==[1,6];assert meta[1]['timestamp_ns']<meta[2]['timestamp_ns'];last=meta[-1]")
needle=" report={'at':old.now(),'status':'pass_activity_graph_feasibility'"
assert s.count(needle)==1
extra=''' header=Path(P['driver_cbid_header']).read_text();names={int(n):name for name,n in re.findall(r'CUPTI_DRIVER_TRACE_CBID_(\\w+)\\s*=\\s*(\\d+)',header)};assert len(names)>500
 apis=[r for r in rows if r['kind']==4];assert len(apis)==last['driver_api_records'] and len(apis)>8
 assert all(r['detail'] in names and r['correlation']>0 and r['context']>0 and r['stream']>0 for r in apis)
 assert len({r['correlation'] for r in apis})==len(apis)
 graph_calls=[r for r in apis if names[r['detail']] in ['cuGraphLaunch','cuGraphLaunch_ptsz']]
 kernel_calls=[r for r in apis if names[r['detail']] in ['cuLaunchKernel','cuLaunchKernel_ptsz']]
 assert len(graph_calls)==4 and len(kernel_calls)==4 and all(r['graph']==0 for r in graph_calls+kernel_calls)
 by_id={r['correlation']:r for r in apis}
 for r in kernels:
  assert r['correlation'] in by_id
  assert names[by_id[r['correlation']]['detail']] in (['cuGraphLaunch','cuGraphLaunch_ptsz'] if r['graph'] else ['cuLaunchKernel','cuLaunchKernel_ptsz'])
 api_summary={name:sum(names[r['detail']]==name for r in apis) for name in {names[r['detail']] for r in apis}}
'''
s=s.replace(needle,extra+needle)
s=s.replace("'native_exactness':markers[0]","'driver_api_counts':api_summary,'graph_launch_API_records':4,'kernel_launch_API_records':4,'all_kernel_driver_correlations_verified':True,'phase_markers_verified':[1,6],'native_exactness':markers[0]")
(H/'run-ability.py').write_text(s,encoding='utf-8',newline='\n')
header=prior/'vendor/cuda_cupti/cuda_cupti-windows-x86_64-12.9.79-archive/include/cupti_driver_cbid.h'
paths=[H/'run-ability.py',H/'collector.cpp',H/'ability.rs',H/'proposal.json',H/'build-plan.json',B/'complete.json',B/'D087Collector.dll',B/'D087Collector.lib',B/'ability.exe',header]
P={'id':'D087-ability','at':old.now(),'status':'FROZEN_PRE_NATIVE','output_dir':str(H/'ability-execution'),'binary':str(B/'ability.exe'),'private_dll_dirs':C['private_dll_dirs'],'driver_cbid_header':str(header),'expected_kernels':13,'graph_nodes':3,'graph_replays':4,'expected_graph_launch_API_records':4,'expected_kernel_launch_API_records':4,'correlation_contract':'Every13actual kernel must join its own eager launch or graph replay API by exact CUPTIcorrelationId. All API correlation IDs unique and valid. Two phase markers ordered.','input_sha256':{str(p):old.sha(p) for p in paths},'optimization_accepted':False};old.save(H/'ability-plan.json',P)
published={}
for src in H.rglob('*'):
 if not src.is_file() or src.suffix in ['.exe','.dll','.pdb','.obj','.lib','.exp'] or '__pycache__' in src.parts:continue
 key=H.name+'/'+src.relative_to(H).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==src.read_bytes()
 published[key]=old.sha(src)
old.save(H/'pre-ability-publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='D087');e.update(stage='Compiled; native API correlation control next',reason='CUPTI Driver API observer compiled without solver changes. Verify exact13kernel data/guards and4graph/4kernel APIcalls before full diagnostic solves.');e['evidence'] +=[{'label':'D087 observed device-gap census','url':'evidence/'+H.name+'/gap-census.json'},{'label':'D087 diagnostic proposal and gates','url':'evidence/'+H.name+'/proposal.json'},{'label':'D087 frozen API correlation control','url':'evidence/'+H.name+'/ability-plan.json'}];st.update(updated_at=old.now(),stage='D087 native API feasibility',activity='Verify direct Driver API records join actual eager/graph kernels and phase timestamps, with no dropped/error/incomplete records.');old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'protocol_sha256':old.sha(H/'ability-plan.json'),'published':len(published)}),flush=True)
