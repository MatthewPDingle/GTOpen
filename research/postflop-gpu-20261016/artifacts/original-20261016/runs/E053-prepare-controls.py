"""Replay resources, exhaustively check chunk ownership, freeze raw fusion controls."""
import importlib.util,json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();R=ROOT/'runs/E053-resource';P=old.read(R/'protocol.json');r=old.read(R/'report.json');assert r['status']=='pass_resource_feasibility_only' and all(r['gates'].values())
for p,h in P['input_sha256'].items():old.pin(p,h)
spec=importlib.util.spec_from_file_location('resource_entry_parser',ROOT/'runs/E052-resource/execute.py')
# Use the exact standalone entry parser source without executing a resource runner.
text=(ROOT/'runs/E052-resource/execute.py').read_text();a=text.index('def entries(');b=text.index('\nwith old.ar.exclusive_lock',a);scope={};exec(text[a:b],scope);entries=scope['entries']
checks=[]
def ck(label,v):checks.append({'label':label,'passed':bool(v)});assert v,label
raw=[json.loads(x.split('E053_RESOURCE ',1)[1]) for x in (R/'execution/probe.stdout.log').read_text().splitlines() if 'E053_RESOURCE ' in x];ck('raw markers exact',raw==r['raw_markers'] and len(raw)==22)
instruction_sites={}
for arch in ['compute_120','compute_75']:
 before,after=[entries(R/'execution'/(arm+'-'+arch+'.ptx')) for arm in ['baseline','candidate']];ck(arch+' nine entries',set(before)==set(after)==set(P['expected_entries']))
 for name in before:ck(arch+' body '+name,before[name]!=after[name] if name=='up_show' else before[name]==after[name])
 sig=lambda s:re.findall(r'\.param\s+\.(u[0-9]+)((?:\s+\.ptr\s+\.align\s+[0-9]+)?)\s+up_show_param_([0-9]+)',s.split('{',1)[0]);ck(arch+' same27parameter ABI',sig(before['up_show'])==sig(after['up_show']) and len(sig(after['up_show']))==27)
 instruction_sites[arch]={arm:{'shared_load_sites':len(re.findall(r'\bld\.shared(?:\.[a-z0-9]+)*\s',table['up_show'])),'shared_store_sites':len(re.findall(r'\bst\.shared(?:\.[a-z0-9]+)*\s',table['up_show'])),'barrier_sites':table['up_show'].count('bar.sync')} for arm,table in [('baseline',before),('candidate',after)]}
for shape,detail in r['details'].items():
 b,c=detail['baseline'],detail['candidate'];nh,m=P['shape_dimensions'][shape];ck(shape+' raw rows',b in raw and c in raw);ck(shape+' resources unchanged',(b['registers'],b['local_bytes_per_thread'],b['static_shared_bytes'])==(c['registers'],c['local_bytes_per_thread'],c['static_shared_bytes'])==(38,0,1040));ck(shape+' exact dynamic reservation',b['dynamic_shared_bytes']==c['dynamic_shared_bytes']==4*nh+16*m);ck(shape+' maxthreads/limits',b['max_threads']==c['max_threads']==1024 and b['fits_default_limits'] and c['fits_default_limits']);ck(shape+' occupancy no loss',len(c['occupancy_by_threads'])==3 and all(t==u and n>=m for (t,m),(u,n) in zip(b['occupancy_by_threads'],c['occupancy_by_threads'])))
for name in ['rustc','probe']:
 e=old.read(R/'execution'/(name+'.exit.json'));ck(name+' terminal0',e['returncode']==0 and e['error'] is None and e['cleanup'] is None)
shapes=nonempty=0
for m in range(1327):
 for block in range(1,257):
  chunk=(m+block-1)//block;end=0
  for thread in range(block):
   lo=thread*chunk;hi=min(lo+chunk,m)
   if lo<hi:assert lo==end and hi<=m;end=hi;nonempty+=1
  assert end==m;shapes+=1
ck('all339712 ownership shapes',shapes==339712)
RR=ROOT/'comparisons/E053-resource-root-check';RR.mkdir();old.save(RR/'report.json',{'at':old.now(),'status':'pass_resource_feasibility_only','checks':checks,'checks_passed':len(checks),'resource_report_sha256':old.sha(R/'report.json'),'registers_before_after':[38,38],'local_bytes_per_thread':0,'static_shared_bytes':1040,'dynamic_shared_unchanged':True,'instruction_sites_descriptive_only':instruction_sites,'chunk_ownership_shapes':shapes,'nonempty_chunks_checked':nonempty,'kernel_launches':0,'performance_measured':False,'root_cross_check_only':True,'candidate_accepted':False})
H=ROOT/'runs/E053-kernel-control';H.mkdir();parent=ROOT/'runs/E052-kernel-control'
for name in ['accepted-evaluator.rs']:(H/name).write_bytes((parent/name).read_bytes())
corpus=old.read(parent/'corpus.json');cases=corpus['cases'];gs=corpus['geometries'];assert len(cases)==328
pattern=[0x7fa00001,0xffa12345,0x7f800001,0xff800001,0,0x80000000,1,0x80000001]
for g in gs:
 base=next(c for c in cases if c['geometry']==g['id'] and c['count']==2);row=dict(base);row.update(id='E053-'+g['id']+'-stress_signaling_nan',profile='stress_signaling_nan',reach_o_bits=[pattern[(i*7+i//11)%len(pattern)] for i in range(len(base['reach_o_bits']))]);cases.append(row)
assert len(cases)==364 and len({c['id'] for c in cases})==364;old.save(H/'corpus.json',corpus)
for arm in ['baseline','candidate']:(H/(arm+'.cu')).write_bytes((ROOT/'runs/E053-source'/(arm+'.cu')).read_bytes())
probe=(parent/'probe-r2.rs').read_text().replace('E052','E053').replace('//! E053: exact128thread u32/u16shared-cache differential; no timing.','//! E053: exact128thread sorted-copy/prefix fusion differential; no timing.')
probe=probe.replace('width:u32,narrow:bool,active:','width:u32,active:').replace('shared_mem_bytes:(n(g,"dynamic_shared_bytes")-if narrow {4*n(g,"m_o")} else {0}) as u32','shared_mem_bytes:n(g,"dynamic_shared_bytes") as u32').replace('128,false,&active','128,&active').replace('128,true,&active','128,&active')
probe=probe.replace('n(g,"dynamic_shared_bytes")-4*n(g,"m_o")','g["dynamic_shared_bytes"]')
probe=probe.replace('assert_eq!(cs.len(),328)','assert_eq!(cs.len(),364)').replace('"comparison_pairs":328','"comparison_pairs":364')
active=sum(sum(bool(v) for v in g['output_active']) for c in cases for g in gs if g['id']==c['geometry'] and c['count']>0)
guards=sum(2*(len(g['output_initial'])-(sum(bool(v) for v in g['output_active']) if c['count']>0 else 0)) for c in cases for g in gs if g['id']==c['geometry'])
probe=re.sub(r'assert_eq!\(launches,656\);assert_eq!\(active_words,[0-9]+\);assert_eq!\(guard_checks,[0-9]+\);assert_eq!\(input_checks,13776\);',f'assert_eq!(launches,728);assert_eq!(active_words,{active});assert_eq!(guard_checks,{guards});assert_eq!(input_checks,15288);',probe)
assert 'narrow' not in probe and '128,false' not in probe and '128,true' not in probe
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
runner=(ROOT/'runs/E052-execute-controls.py').read_text().replace('E052','E053').replace('==331','==367').replace('==328','==364').replace('==656','==728');(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
cmd=list(P['rustc_command']);cmd[1]=str(H/'probe.rs');cmd[-1]=str(H/'probe.exe')
params={'id':'E053-kernel-control','at':old.now(),'status':'FROZEN_BEFORE_KERNEL_LAUNCH','cases':364,'kernel_launches':728,'geometries':36,'original328cases_unchanged':True,'added_fixed36signaling_nan_cases':True,'block_threads_each':128,'expected_active_words':active,'expected_guard_checks':guards,'expected_input_buffer_checks':15288,'same_shared_memory_reservation_each_arm':True,'full_actual_device_input_and_output_snapshots_retained':True,'resource_report_sha256':old.sha(R/'report.json'),'resource_root_sha256':old.sha(RR/'report.json'),'performance_measured':False,'candidate_accepted':False}
old.save(H/'protocol.json',params)
paths=[*H.iterdir(),RR/'report.json',R/'report.json',parent/'probe-r2.rs',parent/'corpus.json',ROOT/'runs/E053-source/manifest.json']
EP={'id':'E053-kernel-control-execution','at':old.now(),'status':'FROZEN_BEFORE_ANY_LAUNCH','rustc_command':cmd,'protocol_sha256':old.sha(H/'protocol.json'),'cases':364,'kernel_launches':728,'input_sha256':{str(p):old.sha(p) for p in paths if p.is_file()}|{p:h for p,h in P['input_sha256'].items() if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']},'candidate_accepted':False};old.save(H/'execution-plan.json',EP)
published={}
for directory in [RR,H]:
 for src in directory.iterdir():
  key=directory.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==src.read_bytes()
  published[key]=old.sha(src)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'artifact_sha256':published,'candidate_accepted':False})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E053');e.update(stage='Resource/ownership gates passed; raw GPU controls',reason='Regs38/local0/static1040/shared reservations/occupancy unchanged.339712integer shapes preserve unique ordered chunk ownership. Freeze364full raw comparisons, including signalingNaNs; no speed claim.');e['evidence'] +=[{'label':'E053 actual resource and ownership replay','url':'evidence/E053-resource-root-check/report.json'},{'label':'E053 fixed364case raw control','url':'evidence/E053-kernel-control/execution-plan.json'}];st.update(updated_at=old.now(),stage='E053 direct raw GPU controls',activity='Resource and339712shape ownership gates pass;364exact raw cases fixed before any kernel launch.');old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'resource_checks':len(checks),'ownership_shapes':shapes,'active_words':active,'guard_checks':guards,'execution_plan_sha256':old.sha(H/'execution-plan.json')}),flush=True)
