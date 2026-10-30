import ast,json,shutil,sys,urllib.request,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists();h.ar.refuse_active(h.ar.live_status())
R=ROOT/'runs/D204-cooperative-resource';Q=h.read(R/'report.json');assert Q['status']=='pass_compiled_cooperative_primitive_resources' and all(Q['gates'].values()) and h.read(R/'execution/complete.json')['all_owned_children_terminal']
assert Q['resources']['resident_blocks_per_SM']==12 and Q['resources']['SM_count']==170 and Q['resources']['max_cooperative_grid_blocks']==2040
H=ROOT/'runs/D205-cooperative-grid-controls';H.mkdir(exist_ok=False)
for source,name in [('D205-grid-controls.rs','probe.rs'),('D205-audit.py','audit.py')]:shutil.copyfile(ROOT/'runs'/source,H/name)
p=R/'execution/primitive-compute_120.ptx';h.pin(p,Q['PTX_sha256']['compute_120']);shutil.copyfile(p,H/'primitive.ptx')
execute='''import sys,json,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O=H/'execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',600);verify();assert(H/'primitive.ptx').read_bytes() in(H/'probe.exe').read_bytes();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe'),'sealed_primitive_PTX_embedded':True})
 h.child([str(H/'probe.exe'),str(H/'output')],O,'probe',600);verify()
 markers=[json.loads(x.split('D205_CONTROL ',1)[1]) for x in (O/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'D205_CONTROL ' in x];assert len(markers)==257 and markers[-1]['stage']=='complete' and markers[-1]['cases']==256 and markers[-1]['kernel_launches']==768;assert [x['id'] for x in markers[:-1]]==list(range(256));assert(H/'output/raw.bin').stat().st_size<=P['raw_reservation_bytes']
 h.child([sys.executable,str(H/'audit.py')],O,'audit',1200);verify()
 report=ROOT/'comparisons/D205-cooperative-grid-controls/report.json';h.save(O/'complete.json',{'at':h.now(),'all_owned_compilers_native_readers_terminal':True,'report_sha256':h.sha(report),'application_primitive_launches':768,'solver_or_speed_samples':0,'source_main_live_protected_PTX_unchanged':True,'new_gain_accepted':False})
print('D205 whole primitive raw/capture/replay controls complete; no solver/speed result.',flush=True)
'''
ast.parse(execute);ast.parse((H/'audit.py').read_text());(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for name,file in [('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
cmd+=['-o',str(H/'probe.exe')]
files=[Path(__file__),ROOT/'runs/D205-grid-controls.rs',ROOT/'runs/D205-audit.py',ROOT/'epoch/common.py',R/'protocol.json',R/'report.json',R/'execution/complete.json',ROOT/'runs/D202-cooperative-scope/report.json']+[p for p in H.iterdir() if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
h.save(H/'protocol.json',{'id':'D205','at':h.now(),'status':'FROZEN_PRE_PRIMITIVE_RAW_COMPILER_AND_KERNEL_PROCESS','rustc_command':cmd,'required_free_bytes':66*1024**3,'raw_reservation_bytes':2*1024**3,'descriptor_order':'gridthenlengththenphasethenmode','grids':[1,2,170,2040],'active_lengths':'[0,1,127,128,129,513,1326,grid*128+1], retainduplicate129forgrid1 asdistinctlengthindex','phase_counts':[0,1,2,17],'modes':['purebitcopy','xorphasecounter'],'fixed_threads':128,'cases':256,'kernel_launches':768,'graph_captures':256,'graph_replays_per_case':2,'prefix_words':17,'tail_words':19,'native_cases_may_not_be_filtered':True,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'OneRustcompiler,oneprimitiveGPUprocess,oneindependentfullrawreader. NoNVRTC/newshadercompile orCFRsolver/sourceactivation/timing. Existingsealedactual120PTX unchanged;allinputs/recurrences/empty/tail/fullresidentgrids and256actualcooperativegraphattributes/stages before/after2replayschecked. Everyfullstate/scratch/guardword retained,alladdresspairsdisjoint. BothCPU/RustandseparatePythonarrayoracles. RawbitpatternsincludeNaN/signedzero etc butnoFPoperation,notfloatingsemanticsproof. No ad-hoc barriers orunsupportedoversubscribedgrid; actual12residentblocks/SM*170SM=2040boundfixedbeforelaunch.','failure':'Any genuineprimitivebit/guard/liveness/graph/cooperativeattribute failureclosesexactform;no shape/width/phase/barrier/flag/sample/source rescue. Mechanical Rustadapter orreader-onlyerrors separatelypreservedandrepairablewithoutrepeatingcompletednativecases. No wholetraversal/optimizer/performanceadmission from pass. All future originalCFRraw/material/resource/capacity/complete1%strictfixture/fresh16/broad/holdout/applicationgatesremain.'})
evidence=[]
for folder,names in [(R,['report.json']),(R/'execution',['complete.json']),(H,['protocol.json'])]:
 for name in names:
  p=folder/name;key=folder.relative_to(ROOT).as_posix()+'/'+name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  evidence.append({'label':folder.name+' '+name,'url':'evidence/'+key})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D204');item.update(status='measured',stage='Both120/75compile,module andactualresourcespassed',reason='Primitive26regs/local0/shared0/defaultstackunchanged,maxthreads1024. Actual128-threadresidency12blocks/SM*170SM=2040maxgrid. Zero applicationkernels sofar; no solver/speed claim.');item.setdefault('evidence',[]).extend(evidence[:2]);s['experiments'].append({'id':'D205','title':'Cooperative grid barrier whole-buffer and graph controls','kind':'diagnostic','status':'staged','accepted':False,'measurement_epoch':'RAM20261028','stage':'Frozen256case eager/capture/tworeplay rawmatrix','correctness':'pending_all_primitive_raw','reason':'Same sealedPTX;grids1/2/170/2040,zero/tail/fullresident extents,0/1/2/17phases,copy/xor. Actualcooperativegraphattribute andeverybuffer/guard checked; noCFR/speed proof.','evidence':evidence[2:]});s.update(updated_at=h.now(),active_experiment='D205',stage='Resident grid primitive raw and graph prerequisite',activity='OfficialCUDAgridprimitive compiles/loads withinfixedresources. Next256GPUcases/768requestedcompletedlaunches withfullraw/graph/cooperative/guard controls. E080/16/defaultaffinity unchanged;no speedgain.');h.ar.atomic_json(h.ar.STATUS,s)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n### D204 primitive resources pass; D205 full raw/graph controls frozen\n\nOneRustcompiler/oneNVRTC12.9module-onlyhelperterminal0;actual120andcompat75compilewithtwofrozenprivatevendorinclude roots,one6argumentgridprimitive. Actual12026regs/local0/shared0/defaultstack1024unchanged,maxthreads1024,128-threadresidency12blocks/SM*170SM=2040. No applicationkernels/CFR/speed samples.\n\nD205 freezesoneRustcompiler/oneGPUprimitiveprocess/onefullrawreader,zeroNVRTC/newshader/sourceactivation.256fixedcases: grids1/2/170/2040;lengths0/1/127/128/129/513/1326/grid*128+1 retainingduplicates;phases0/1/2/17;copy/xor. OriginalsealedPTX,128threads,eachcaseeagerthennewbuffergraphcapture/tworeplays,768kernel executionsplanned. Actualgraphnodecooperativeattribute1andonekernel required. Everyactualstate/scratchwordand17prefix/19tailguards retained;addressrangesdisjoint;RustandindependentPythonoracles. Pureintegertransportofexceptionalfloatbitsnotfloatingarithmetic/CFRproof.2GiBrawreserve+64GiBheadroom. Any genuineraw/guard/liveness/graphfailureclosesformwithoutshape/barrier/flags/sample rescue. Passonlypermitsfurtherwholetraversaldesign,alloriginalraw/material/complete1%/strictfixture/fresh16/broad/capacity/holdout/applicationgatesremain.\n')
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);subprocess.run(['git','commit','-m','research: pass cooperative primitive resources and freeze raw graph controls'],cwd=h.REPO,check=True)
print(h.sha(H/'protocol.json'),flush=True)
