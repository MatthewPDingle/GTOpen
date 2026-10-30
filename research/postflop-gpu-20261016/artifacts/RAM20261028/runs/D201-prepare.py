import ast,json,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists();h.ar.refuse_active(h.ar.live_status())
topology=ROOT/'runs/D200-affinity-scope/report.json';T=h.read(topology);assert T['baseline_mask_hex']=='0xffffffff' and T['candidate_mask_hex']=='0x55555555' and T['workers_both_arms']==16
H=ROOT/'runs/D201-affinity-raw-controls';H.mkdir(exist_ok=False);parent=ROOT/'runs/D168-worker-raw-control';canonical=ROOT/'runs/D178-canonical-cache-control'
helper=ROOT/'runs/D201-affinity.py';shutil.copyfile(helper,H/'affinity.py')
binary=parent/'probe.exe';B=h.read(parent/'execution/binary.json');h.pin(binary,B['sha256']);assert B['one_binary_allconfigs'] and B['sealed12PTXembedded']
# A tiny, fixed CPU-only inheritance proof precedes any CUDA/native solver process.
test='''import ctypes as c,json,os
k=c.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.restype=c.c_void_p;k.GetProcessAffinityMask.argtypes=[c.c_void_p,c.POINTER(c.c_size_t),c.POINTER(c.c_size_t)];p,s=c.c_size_t(),c.c_size_t();assert k.GetProcessAffinityMask(k.GetCurrentProcess(),c.byref(p),c.byref(s));print(json.dumps({'pid':os.getpid(),'process_mask':p.value,'system_mask':s.value}),flush=True)
'''
(H/'inheritance-test.py').write_text(test,encoding='utf-8',newline='\n')
h.save(H/'adapter-protocol.json',{'id':'D201-adapter','at':h.now(),'status':'FROZEN_PRE_CPU_ONLY_INHERITANCE_CHILDREN','masks':[T['baseline_mask'],T['candidate_mask']],'source_sha256':{str(p):h.sha(p) for p in [Path(__file__),H/'affinity.py',H/'inheritance-test.py',topology]},'scope':'Exactly2Python CPU-onlychildren, initialparent/child masks andparent restoration. NoCUDA/context/compiler/native solver. No otherprocess/globalpriority/power/clock/affinitysetting. Any failure retained; no native solver before adapter passes.'})
import importlib.util
spec=importlib.util.spec_from_file_location('affinity',H/'affinity.py');affinity=importlib.util.module_from_spec(spec);spec.loader.exec_module(affinity)
witnesses=[]
for i,mask in enumerate([T['baseline_mask'],T['candidate_mask']]):
 with(H/f'adapter-{i}.stdout.log').open('xb') as stdout,(H/f'adapter-{i}.stderr.log').open('xb') as stderr:
  proc=affinity.spawn(mask,witnesses,[sys.executable,str(H/'inheritance-test.py')],stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
  proc.wait(timeout=30);assert proc.returncode==0
 actual=json.loads((H/f'adapter-{i}.stdout.log').read_text());assert actual=={'pid':proc.pid,'process_mask':mask,'system_mask':T['baseline_mask']}
h.save(H/'adapter-report.json',{'at':h.now(),'status':'pass_child_inheritance_and_parent_restoration','adapter_protocol_sha256':h.sha(H/'adapter-protocol.json'),'witnesses':witnesses,'parent_final':affinity.query(),'CUDA_or_native_solver_processes':0})
for name in ['sampler.py']:shutil.copyfile(parent/name,H/name)
bounded=(parent/'bounded_child.py').read_text();bounded=bounded.replace('import ctypes as c,importlib.util,subprocess,time,shutil','import ctypes as c,importlib.util,subprocess,time,shutil\nimport affinity',1)
bounded=bounded.replace('raw_root,output,workers):','raw_root,output,workers,mask):',1)
bounded=bounded.replace('terminal=None','terminal=None;affinity_witnesses=[];affinity_samples=[]',1)
old='proc=subprocess.Popen(command,cwd=h.REPO,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)';new='proc=affinity.spawn(mask,affinity_witnesses,command,cwd=h.REPO,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)';assert bounded.count(old)==1;bounded=bounded.replace(old,new,1)
old="try:info=s.process_memory(handle)";new="try:\n                    info=s.process_memory(handle);actual_affinity=affinity.query(handle);assert actual_affinity['process_mask']==mask;affinity_samples.append({'elapsed_ms':(stamp-clock)*1000,'actual':actual_affinity})";assert bounded.count(old)==1;bounded=bounded.replace(old,new,1)
old="'at':h.now(),'pid':proc.pid,'returncode':proc.returncode,'samples':rows";new="'at':h.now(),'pid':proc.pid,'returncode':proc.returncode,'affinity_spawn_witnesses':affinity_witnesses,'affinity_live_samples':affinity_samples,'expected_mask':mask,'parent_final_affinity':affinity.query(),'samples':rows";assert bounded.count(old)==1;bounded=bounded.replace(old,new,1)
ast.parse(bounded);(H/'bounded_child.py').write_text(bounded,encoding='utf-8',newline='\n')
audit=(canonical/'audit.py').read_text().replace('D178-canonical-cache-control','D201-affinity-raw-controls').replace("'id':'D178'","'id':'D201'").replace('pass_scoped_full_canonical_all_device_and_CPU_raw_lifecycle','pass_affinity_full_canonical_raw_lifecycle')
old="req([x for x in text.splitlines() if x.startswith('D178_BIND ')]==['D178_BIND '+arm]*P['expected_PTX_bindings_per_arm'],'actual sealed module bindings forinitial/resume')"
new="""req([x for x in text.splitlines() if x.startswith('D166_BIND ')]==['D166_BIND baseline']*6,'all original sealed acceptedE080 module bindings')
    pools=[json.loads(x.split('D168_POOL ',1)[1]) for x in text.splitlines() if x.startswith('D168_POOL ')]
    req(pools==[{'actual':16,'requested':16,'observation_after_entire_suite_and_lifecycle':True}],'actual16workers afterallsuite/lifecycle')"""
assert audit.count(old)==1;audit=audit.replace(old,new,1)
anchor="cpu=gpu=query=save=evs=0";assert audit.count(anchor)==1
inject="""for arm in P['sequence']:
    resource=h.read(H/'execution'/(arm+'.resource.json'));mask=P['masks'][arm]
    req(resource['expected_mask']==mask and len(resource['affinity_spawn_witnesses'])==1 and resource['affinity_live_samples'],'actual inherited and live affinity observations')
    w=resource['affinity_spawn_witnesses'][0];req(w['original_parent']==w['restored_parent_after_spawn']==resource['parent_final_affinity']=={'process_mask':P['masks']['baseline'],'system_mask':P['masks']['baseline']},'research controller affinity restored')
    req(w['selected_parent_before_spawn']['process_mask']==w['actual_child_at_spawn']['process_mask']==mask,'mask selected before child start')
    req(all(x['actual']['process_mask']==mask and x['actual']['system_mask']==P['masks']['baseline'] for x in resource['affinity_live_samples']),'all observed live child masks exact')
"""
audit=audit.replace(anchor,inject+'\n'+anchor,1)
audit=audit.replace("'scope':'Original three full same-quality","'scope':'One unchangedacceptedE080/prebuiltPTXnativebinary,16workersbotharms; onlychildprocessCPUaffinitymaskdiffers. All sampled masks and actualpost-suite pool checked,parent restored. Original three full same-quality",1)
ast.parse(audit);(H/'audit.py').write_text(audit,encoding='utf-8',newline='\n')
execute='''import sys,shutil,importlib.util,urllib.request,json
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O=H/'execution';O.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('bounded',H/'bounded_child.py');bounded=importlib.util.module_from_spec(spec);spec.loader.exec_module(bounded)
assert bounded.affinity.query()=={'process_mask':P['masks']['baseline'],'system_mask':P['masks']['baseline']}
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['limits']['required_free_bytes']
 for arm in P['sequence']:
  verify();h.ar.refuse_active(h.ar.live_status());out=H/(arm+'-output');out.mkdir(exist_ok=False)
  bounded.run([P['binary'],'--exact','d168_worker_controls','--ignored','--nocapture','--test-threads=1'],O,arm,h,P['limits'],H,out,16,P['masks'][arm]);verify()
 h.child([sys.executable,str(H/'audit.py')],O,'audit',1800);verify()
 D=ROOT/'comparisons/D201-affinity-raw-controls';h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(D/'report.json'),'source_main_live_PTX_unchanged':True,'performance_samples':0,'new_gain_accepted':False})
print('D201 raw affinity controls complete; all children terminal, no speed score.',flush=True)
'''
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
review=h.read(parent/'source-review.json');review.update(id='D201',at=h.now(),source='Same retained acceptedE080 D168 nativebinary/source andsealedPTXbotharms. No compiler/solver/kernel/source/graph/metadata/layout/math change. Original3fullcanonical fixtures andcontinued/locked/resumed lifecycle,allrawCPU/66GPUbuffers/fullphysicalCFV/query/save/futureEV unchanged.',CPU_affinity='Onlyresearchchild inherits explicitbaseline0xffffffff orcandidate0x55555555 before first nativeinstruction. Python controller temporarilychangesitsownmaskonlyaroundPopen andrestoresbeforechildobservation/wait; originalCodex/service/unrelatedprocesses untouched. ActualGetProcessAffinityMask initial/live observations retained. Botharms actualRayon16queriedonlyafterentiresuite/lifecycle.',novelty='D168/D169worker8/32forms stayclosed. This distinct16workerplacement changesavailableSMTsiblings, no worker-count/source/flag rescue. E050/E061cp.asyncfamily remainsclosed andwasnotrepeated.',expected_structural_costs='Exact samebinary wrapper/hostmetadata/CPU/GPUfieldtypes andsizes, no added resources orcapacity change expected. Changed scheduling can stillincrease CPU/lifetime/latency andallotherpathway risksremain; actualmaterial/broad/app gatesmandatory.',failure='Any realraw/science/pool/affinity/resourceguardfailurecloses exact16worker least-significant-bit-per-core mask. No alternatesibling/CCDsubset/threadcount/priority/source/flags/sample rescue. Alloriginal1%/strictfixture/fresh16/broad/material/capacity/holdout/cumulative/application gatesremain.',candidate_accepted=False)
h.save(H/'source-review.json',review)
old=h.read(canonical/'protocol.json');files=[Path(__file__),helper,topology,ROOT/'runs/D200-affinity-scope/protocol.json',parent/'protocol.json',parent/'source-review.json',parent/'execution/binary.json',binary,canonical/'audit.py',ROOT/'epoch/common.py',ROOT/'epoch/exact-anchor.json']+[p for p in H.rglob('*') if p.is_file()]
h.save(H/'protocol.json',{'id':'D201','at':h.now(),'status':'FROZEN_PRE_FULL_CANONICAL_AFFINITY_GPU_CONTROLS','binary':str(binary),'binary_sha256':h.sha(binary),'sequence':['baseline','candidate'],'masks':{a:T[a+'_mask'] for a in ['baseline','candidate']},'workers':16,'limits':old['limits'],'lifecycle_stages':old['lifecycle_stages'],'input_sha256':{str(p):h.sha(p) for p in files},'scope':'Exactly2fresh GPUprocesses sameacceptedE080nativebinary/sealedPTX, onefullretainedrawreader, zeroRust/Cargo/NVRTCcompilers. Fullcanonicalscience/quality/cadence/stops andallphysicalCPU/GPUstate mustexact; source/field/type/wrapperexception none. HonestprebuiltPTX clocksunscored. Onlyfixedchildaffinitymaskvaries, actualinherited/live mask+post-suiteRayon16 andcontrollerrestoration required. No live/main/globalsettings.256GiBraw+64headroom/32GiBprocess/64before32duringRAM guards retained. All speed/broad/material/adoption gatesremain.'})
evidence=[]
for folder,names in [(ROOT/'runs/D200-affinity-scope',['protocol.json','report.json']),(H,['protocol.json','source-review.json','adapter-report.json'])]:
 for name in names:
  p=folder/name;key=folder.name+'/'+name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  evidence.append({'label':folder.name+' '+name,'url':'evidence/'+key})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D200','title':'Physical core CPU placement scope','kind':'diagnostic','status':'measured','accepted':False,'measurement_epoch':'RAM20261028','stage':'Readonly16core/32logicaltopology verified','reason':'FixedoneSMTsiblingpercoremask0x55555555,all16coreskept; no setting/CUDA/solve in topologyquery. Distinct16workerplacement, D1698/32remainclosed.','evidence':evidence[:2]});s['experiments'].append({'id':'D201','title':'Physical core placement full canonical raw controls','kind':'diagnostic','status':'staged','accepted':False,'measurement_epoch':'RAM20261028','stage':'Frozen samebinary fullraw/lifecycle affinity controls','correctness':'pending_fullraw','reason':'Baselineall32logical versuscandidateoneperphysicalcore,16workersboth. SameacceptedE080binary,allCPU/device/fullCFV/query/save/futureEV,actualmask/pool andparentrestore. No speed claim.','evidence':evidence[2:]});s.update(updated_at=h.now(),active_experiment='D201',stage='CPU placement raw prerequisite',activity='Fixed16worker physical-core mask topology andtwoCPU-onlyinheritance tests passed. Fullcanonical/rawstate controls before original real-runtime speed clocks. E080/GPU/compressed/16 liveunchanged.');h.ar.atomic_json(h.ar.STATUS,s)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n### D200/D201 fixed physical-core CPU placement controls\n\nPreviousgoalturn progressed throughD195/D196rawengine andD197/D198fullcanonicalraw evidence;E102closedatwrappergate,no speed samples. Currentcustody/idle/absentlocks verified. Proposedcp.asyncshowstaging matchedclosedE050/E061;notrepeated.\n\nNew16worker placement distinctfromclosedD168/D1698/32worker counts: WindowsreadonlyGetLogicalProcessorInformationEx returns16symmetric2waySMTcores/group0,process/systemmask0xffffffff. Fixedleast-significantlogicalbitpercore yields0x55555555,all16physicalcoreskept. No alternative sibling/CCD/count/priority/power/OS/clock sweep. CPU-onlytwochildinheritanceproof verifies selectedmaskbeforestartupandcontrollerrestoration. OnlyresearchcontrollerbrieflysetsitsownmaskaroundPopen;live/Codex/unrelatedprocesses untouched. PrimaryWindowsdocslinkedinscopeprotocol.\n\nD201 freezes2freshprocesses ofsameoriginalacceptedE080/D168sealedPTXbinary,zeroRust/Cargo/NVRTCcompilers. Original3fullcanonicalfixtures/quality/cadence/stops andcontinued/locked/resumed wholeCPU/66GPU/fullphysicalCFV/query/save/futureEV equality;actualinherited/live masks andpost-suiteRayon16required. Heavyobserver/prebuiltPTX clocksunscored.256GiBraw+64headroom,32GiBprocesscap,64/32availableRAMguards retained. Scheduling/NVRTC/helper/otherpathway costs mayworsen;all1%strictfixture/fresh16/broad/material/capacity/holdout/cumulative/application gatesremain beforeadoption. Exactmask closesonfailurewithoutrescue.\n')
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);subprocess.run(['git','commit','-m','research: freeze physical core placement full raw controls'],cwd=h.REPO,check=True)
h.custody();print(h.sha(H/'protocol.json'),flush=True)
