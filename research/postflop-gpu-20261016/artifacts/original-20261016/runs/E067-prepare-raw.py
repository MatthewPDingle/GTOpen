"""Freeze the complete1196case exact down_action matrix before any numerical launch."""
import ast,codecs,json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();old.ar.refuse_active(old.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
RES=ROOT/'runs/E067-resource';S=ROOT/'runs/E067-source';R=ROOT/'comparisons/E067-resource-mechanism-root-check';resource=old.read(RES/'report.json');root=old.read(R/'report.json')
assert all(resource['gates'].values()) and root['status']=='pass_actual_target_feasibility_abi_source_and_per_arity_mechanism' and root['actual_target_all_frozen_cfg_gates_pass']
old.pin(R/'pre-numerical-scope-amendment.json',root['scope_amendment_sha256'])
P0=old.read(RES/'protocol.json')
for p,h in P0['input_sha256'].items():old.pin(p,h)
H=ROOT/'runs/E067-kernel-control';assert not H.exists();H.mkdir()
for v in ['baseline','candidate']:(H/(v+'.ptx')).write_bytes((RES/'execution'/(v+'-compute_120.ptx')).read_bytes())
probe=(ROOT/'runs/E067-raw-probe.rs').read_text();magics=re.findall(r'b"(E067[^"\n]+)"',probe);assert len(magics)==5 and all(len(codecs.decode(x,'unicode_escape').encode('latin1'))==16 for x in magics)
expected_args=['dn','start','count','dp','da','doff','dcs','dc','drs0','drs1','dg0','dg1','dl','dls','mut dr0','mut dr1','n0','n1'];assert re.findall(r'\.arg\(&([^)]*)\)',probe)==expected_args
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
cases=[]
def add(nh0,nh1,na,threads,actor,locked,mode,count,group):
 i=len(cases);cases.append({'id':i,'nh0':nh0,'nh1':nh1,'actions':na,'threads':threads,'actor':actor,'locked':locked,'value_mode':mode,'count':count,'sigma_offset':7 if ((i//4)+actor)&1 else 0,'group':group})
dims=[(1,3),(31,32),(32,33),(33,31),(63,64),(64,65),(65,63),(127,128),(128,129),(129,127),(255,256),(256,257),(257,255),(511,512),(512,513),(513,511),(1023,1024),(1024,1326),(1326,1023),(0,0),(0,7),(7,0),(257,319),(258,320),(233,280)]
for a,b in dims:
 for na in [1,2,3,4,5,8,9,16,17]:
  for actor in [0,1]:
   for locked in [0,1]:add(a,b,na,128,actor,locked,0,1,'canonical_dims_menus')
for na in [2,3,4,9,17]:
 for block in [1,32,64,256]:
  for actor in [0,1]:
   for locked in [0,1]:add(129,257,na,block,actor,locked,0,1,'supplementary_threads')
for na in [1,2,3,4,8,9,17]:
 for mode in range(1,7):
  for actor in [0,1]:
   for locked in [0,1]:add(129,257,na,128,actor,locked,mode,1,'value_stress')
for na in [1,2,3,4,9,17]:
 for actor in [0,1]:
  for locked in [0,1]:add(129,257,na,128,actor,locked,0,0,'zero_count')
for na in [1,2,3,4,9,17]:
 for actor in [-1,2]:
  for locked in [0,1]:add(7,33,na,128,actor,locked,0,1,'noncanonical_actor_selection')
assert len(cases)==1196 and len({tuple(c[k] for k in ['nh0','nh1','actions','threads','actor','locked','value_mode','count','sigma_offset']) for c in cases})==1196
estimated=0
for c in cases:
 na=c['actions'];nn=na+9;a,b=c['nh0'],c['nh1'];h=a if c['actor']==0 else b;loff=c['sigma_offset'];immutable=5+9*nn+(na+4)+(13+na*a+17)+(13+na*b+17)+(loff+na*h+17);mutable=(10+2*na)*(max(a,1)+max(b,1))+34;estimated+=4*(3*immutable+3*mutable)+1000
assert estimated<2*1024**3
old.save(H/'corpus.json',{'id':'E067-down-action-raw-corpus','at':old.now(),'status':'FROZEN_PRE_FIRST_NUMERICAL_LAUNCH','case_count':1196,'kernel_launches':2392,'cases':cases,'groups':{'canonical_dims_menus':900,'supplementary_threads':80,'value_stress':168,'zero_count':24,'noncanonical_actor_selection':24},'value_modes':{'0':'mixed finite','1':'signedzero','2':'threshold-small finite','3':'NaN/Inf stress','4':'finite overflow','5':'subnormal/tiny','6':'adjacent float thresholds'},'raw_schema':'Each file16Bmagic, percaseu32id then lengthu64/u32word vectors. inputs:descriptor12,immutable12vectors(nodes,player,na,u64offhalves,childstart,children,rsrc0,rsrc1,regrets0bits,regrets1bits,i64lockhalves,sigmabits),2reachseeds. Eacharmoutputs2full reachvectors; eacharmactualpostinputs12immutablevectors. All littleendian; rawwords no fingerprints.','coverage':'Both actor orientations, different hand counts and source/child maps, nonzero node/start/data/child/sigma offsets, locked/unlocked,1..17action generic/specialized paths, zero/tails/full1326hands, count0, surplusCTAs and1/32/64/128/256threads. Each rawcase one actual node; integrated solver covers mixed multi-node graph behavior later.','limits':'Finite declared cases, no spansabove2^32orphysicalotherGPUorCPUreferencefloatparity claim; noncanonicalactor stress checks source else-select semantics, not supported gameplay.'})
runner=(ROOT/'runs/E067-raw-execute.py').read_text();ast.parse(runner);(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
P=old.read(RES/'protocol.json');P.update(id='E067-kernel-control',at=old.now(),status='FROZEN_PRE_FIRST_APPLICATION_KERNEL',cases=1196,kernel_launches=2392,raw_peak_reservation_bytes=2*1024**3,estimated_raw_bytes_upper_with_record_headers=estimated,source_manifest_sha256=old.sha(S/'manifest.json'),resource_report_sha256=old.sha(RES/'report.json'),mechanism_root_report_sha256=old.sha(R/'report.json'),scope_amendment_sha256=old.sha(R/'pre-numerical-scope-amendment.json'),candidate_accepted=False,performance_measured=False)
P['rustc_command']=[x.replace(str(RES),str(H)) for x in P['rustc_command']];P.pop('fixed_gates',None);P.pop('additional_required_gate',None)
P['scope']='Actualcompute120paired original/new full outputs and actualimmutableinputs/guards; only declared1196cases/2392launches, no variants or extra cases after any failure. Source/FPstatement/ABI/launch contracts unchanged; no speed score. Target-scope amendment replaces overbroadsm75branchfulbaseline prerequisite before any numerical execution; originalfailure preserved.'
paths=[*H.iterdir(),Path(__file__),ROOT/'runs/E067-raw-probe.rs',ROOT/'runs/E067-raw-execute.py',ROOT/'runs/E067-ptx-mechanism.py',ROOT/'runs/E067-pre-numerical-preparation-failure.json',*S.iterdir(),RES/'protocol.json',RES/'report.json',R/'report.json',R/'original-extra-gate-failure.json',R/'pre-numerical-scope-amendment.json',ROOT/'runs/D108-resource-feasibility-audit/docket.json',ROOT/'runs/D108-resource-feasibility-audit/commit.json',old.REPO/'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py']
P['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()}|{p:h for p,h in P0['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']};old.save(H/'execution-plan.json',P)
published={}
for p in H.iterdir():
 if not p.is_file():continue
 key='evidence/'+H.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as x:assert x.read()==p.read_bytes()
 published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'new_application_kernel_launches':0,'raw_reservation_bytes':2*1024**3})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E067');e.update(stage='Fixed1196paired full raw down_action controls',reason='Fresh actualGPU mechanism and feasibility passed, resource risks disclosed. Target-scope amendment preservedbeforefirstnumericalexecution.1196fixed cases test full2reachoutputs,12actualimmutablebuffers/guards; no historicaldata or timing score.');e['evidence'].append({'label':'Frozen first full raw numerical protocol','url':'evidence/'+H.name+'/execution-plan.json'});st.update(updated_at=old.now(),stage='E067 full raw GPU numerical matrix',activity='Both actors, distinct maps/dimensions, locked/unlocked,1..17actions,zero/tail/full1326hands,signedzero/threshold/nonfinite/subnormal,5threadwidths,count0. Exactoriginalform; no tuning.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'execution_plan_sha256':old.sha(H/'execution-plan.json'),'cases':1196,'kernel_launches':2392,'estimated_raw_bytes':estimated}),flush=True)