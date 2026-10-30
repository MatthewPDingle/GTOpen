import ast,copy,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status());R=ROOT/'runs/E099-resource';rr=h.read(R/'report.json');assert rr['status']=='pass_compiled_prerequisites' and all(rr['gates'].values());G=ROOT/'runs/E099-direct-controls';G.mkdir(exist_ok=False)
for p,digest in h.read(R/'protocol.json')['input_sha256'].items():h.pin(p,digest)
up_parent=ROOT/'runs/D177-up-action';down_parent=ROOT/'runs/D163-down-action';up=G/'up';down=G/'down';up.mkdir();down.mkdir();old_up=h.read(up_parent/'corpus.json')['cases'];uc=copy.deepcopy(old_up);discounts={}
for c in old_up:
 ckey=(c['algorithm'],c['iteration']);discounts.setdefault(ckey,c['discount_bits']);assert discounts[ckey]==c['discount_bits']
for c in uc:c['layout']=0;c['paired_active_expected']=False
def add_up(nh,na,block,p,role,algo,t,mode,count=1,layout=1):
 off=13 if layout in [0,3] else 14;loff=5 if layout in [0,4] else 6;stride=nh+(5 if layout in [0,2,5] else 4);ident=len(uc);uc.append({'id':ident,'hands':nh,'actions':na,'threads':block,'p':p,'role':role,'algorithm':algo,'iteration':t,'value_mode':mode,'count':count,'discount_bits':discounts[algo,t],'layout':layout,'descriptor':[nh,na,block,p,role,algo,t,mode,count,stride,1,2,off,loff],'paired_active_expected':bool(count and nh and na==2 and (nh|stride)%2==0 and off%2==0 and(role!=1 or loff%2==0))})
for nh in [0,2,30,32,34,64,66,126,128,130,256,258,320,512,1024,1326]:
 for block in [1,32,64,128,256]:
  for role in range(3):
   for p in range(2):
    for algo in range(2):
     for mode in range(5):add_up(nh,2,block,p,role,algo,[1,20,200][(nh//2)%3],mode)
for na in [1,3,4,5,8,9,16,17]:
 for nh in [2,258]:
  for role in range(3):
   for p in range(2):
    for algo in range(2):
     for mode in range(5):add_up(nh,na,128,p,role,algo,200,mode)
for layout in [2,3,4,5]:
 for nh0 in [2,258]:
  for role in range(3):
   for p in range(2):
    for algo in range(2):
     for mode in range(5):add_up(257 if layout==5 else nh0,2,128,p,role,algo,20,mode,layout=layout)
for role in range(3):add_up(2,2,128,0,role,0,20,0,count=0)
assert len(uc)==7062 and [dict((k,v) for k,v in c.items() if k not in ['layout','paired_active_expected']) for c in uc[:819]]==old_up
h.save(up/'corpus.json',{'legacy_cases':819,'cases':uc,'scope':'Original819cases preserved as firstrecords, then fixed pair-eligible fullaxis/generic/individual alignmentfallback/count0 corpus. No old corpus changed.'})
source=(up_parent/'probe.rs').read_text();changes=[('struct Case {nh:', 'struct Case {layout:u32,nh:'),('cases.push(Case{','cases.push(Case{layout:0,'),('let Case{nh,na,block,p,role,algo,t,mode,count}=*c;','let Case{layout,nh,na,block,p,role,algo,t,mode,count}=*c;'),('let max=nh+5;let parent=2usize;let off=13usize;let cs=2usize;let loff=5usize;','let max=nh+if [0,2,5].contains(&layout){5}else{4};let parent=2usize;let off=if [0,3].contains(&layout){13usize}else{14usize};let cs=2usize;let loff=if [0,4].contains(&layout){5usize}else{6usize};'),('let cf=cm.load_function("up_action").unwrap();','let cf=cm.load_function("up_action_pair2").unwrap();'),('E085_UNIT','E099_UP')]
for old,new in changes:assert old in source,old;source=source.replace(old,new)
needle=' assert_eq!(cases.len(),819);';assert source.count(needle)==1
append='''
 let declared:serde_json::Value=serde_json::from_str(include_str!("corpus.json")).unwrap();let declared=declared["cases"].as_array().unwrap();
 for c in declared.iter().skip(819){let n=|k:&str|c[k].as_u64().unwrap();cases.push(Case{layout:n("layout") as u32,nh:n("hands") as usize,na:n("actions") as usize,block:n("threads") as u32,p:n("p") as i32,role:n("role") as u32,algo:n("algorithm") as u32,t:n("iteration") as u32,mode:n("value_mode") as u32,count:n("count") as i32});}
 assert_eq!(cases.len(),7062);
''';source=source.replace(needle,needle+append,1)
old='regions":disjoint_regions(&stream,[&dr,&ds,&dv])';new='regions":disjoint_regions(&stream,[&dr,&ds,&dv]),"paired_float_regions":paired_regions(&stream,&[("regrets",&dr),("strategy",&ds),("CFV",&dv),("own_reach",&drp),("lock_sigma",&dls)])';assert source.count(old)==1;source=source.replace(old,new,1)
old='"count":count,"discount_bits":fb(&disc)';new='"count":count,"layout":layout,"paired_active_expected":declared[index]["paired_active_expected"],"discount_bits":fb(&disc)';assert source.count(old)==1;source=source.replace(old,new,1)
helper='''
fn paired_regions(s:&Arc<CudaStream>,buffers:&[(&str,&CudaSlice<f32>)])->Vec<serde_json::Value>{let v:Vec<_>=buffers.iter().map(|(name,b)|{let(p,_guard)=b.device_ptr(s);assert_eq!(p%8,0);(*name,p,b.len() as u64*4)}).collect();for i in 0..v.len(){for j in i+1..v.len(){assert!(v[i].1+v[i].2<=v[j].1||v[j].1+v[j].2<=v[i].1);}}v.into_iter().map(|(name,p,n)|serde_json::json!({"name":name,"address":p,"bytes":n})).collect()}
''';source+=helper;(up/'probe.rs').write_text(source,encoding='utf-8',newline='\n');shutil.copyfile(up_parent/'discounts.rs',up/'discounts.rs')
dc=copy.deepcopy(h.read(down_parent/'corpus.json'));old_dc=copy.deepcopy(dc)
for c in dc:c.update(layout=0,reuse_zero=False)
def add_down(nh,na,block,actor,locked,rm,pm,count=1,layout=1,reuse=False):dc.append({'nh':nh,'na':na,'block':block,'actor':actor,'lock_mode':locked,'regret_mode':rm,'reach_mode':pm,'count':count,'layout':layout,'reuse_zero':reuse})
for nh in [0,2,30,32,34,64,66,126,128,130,256,258,320,512,1024,1326]:
 for actor in range(2):
  for locked in [0,1]:
   for rm in range(7):
    for pm in range(5):add_down(nh,2,128,actor,locked,rm,pm)
for block in [1,32,64,256]:
 for nh in [2,34,258,1326]:
  for actor in range(2):
   for locked in range(4):
    for rm in [0,4,5,6]:
     for pm in [0,3,4]:add_down(nh,2,block,actor,locked,rm,pm)
for na in [1,3,4,5,8,9,16,17]:
 for nh in [2,258]:
  for actor in range(2):
   for locked in range(4):
    for rm in [0,4]:
     for pm in [0,4]:add_down(nh,na,128,actor,locked,rm,pm)
for actor in range(2):
 for locked in range(4):
  for nh in [0,2,258]:add_down(nh,2,128,actor,locked,0,0,count=0)
for nh in [2,258]:
 for actor in range(2):
  for locked in range(4):
   for rm in [0,4,5]:
    for pm in [0,3,4]:
     for block in [1,128,256]:add_down(nh,2,block,actor,locked,rm,pm,reuse=True)
for layout in [2,3,4]:
 for nh0 in [2,258]:
  for actor in range(2):
   for locked in range(4):
    for rm in [0,4]:
     for pm in [0,4]:add_down(257 if layout==4 else nh0,2,128,actor,locked,rm,pm,layout=layout)
assert len(dc)==6466 and [{k:v for k,v in c.items() if k not in ['layout','reuse_zero']} for c in dc[:1530]]==old_dc
h.save(down/'corpus.json',dc);source=(down_parent/'probe.rs').read_text();old='let other=if nh==0{5}else{nh+5};let nhs=if actor==0{[nh,other]}else{[other,nh]};let nn=na+9;let parent=2;let off=13;let cs=2;let loff=7;';new='let layout=get("layout");let reuse=c["reuse_zero"].as_bool().unwrap();let other=if layout==0{if nh==0{5}else{nh+5}}else if layout==4{nh+5}else{nh+6};let mut nhs=if actor==0{[nh,other]}else{[other,nh]};if reuse{nhs[1]=0;}let active_nh=nhs[actor];let nn=na+9;let parent=2;let off=if layout==0||layout==2{13}else{14};let cs=2;let loff=if layout==0||layout==3{7}else{8};';assert source.count(old)==1;source=source.replace(old,new,1)
for old,new in [('let cf=cm.load_function("down_action").unwrap();','let cf=cm.load_function("down_action_pair2").unwrap();'),('CudaStream,LaunchConfig','CudaStream,DevicePtr,LaunchConfig'),('p==actor&&nh>0&&i/nh>=5&&i/nh<5+na','p==actor&&active_nh>0&&i/active_nh>=5&&i/active_nh<5+na'),('E091_RAW','E099_DOWN')]:assert old in source,old;source=source.replace(old,new)
old='let mut expected=None;';new='let mut expected=None;let mut device_regions=Vec::new();';assert source.count(old)==1;source=source.replace(old,new,1)
old='let nh0=nhs[0]as i32;let nh1=nhs[1]as i32;';new=old+'device_regions.push(serde_json::json!({"arm":label,"paired_float_regions":paired_regions(&s,&[("regrets0",&dr0),("regrets1",&dr1),("lock_sigma",&dls),("reach0",&d0),("reach1",&d1)])}));';assert source.count(old)==1;source=source.replace(old,new,1)
old='"case":c,"all_raw_outputs_and_inputs_exact"';new='"case":c,"device_regions":device_regions,"all_raw_outputs_and_inputs_exact"';assert source.count(old)==1;source=source.replace(old,new,1);source+=helper;(down/'probe.rs').write_text(source,encoding='utf-8',newline='\n')
units={};deps=ROOT/'reference/accepted-e080-deps'
for name,folder,parent_dir,legacy,marker in [('up',up,up_parent,819,'E099_UP'),('down',down,down_parent,1530,'E099_DOWN')]:
 for arm in ['baseline','candidate']:
  p=R/'execution'/(arm+'-compute_120.ptx');h.pin(p,rr['PTX_sha256'][arm+'-compute_120']);shutil.copyfile(p,folder/(arm+'.ptx'))
 cmd=['rustc',str(folder/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
 for lib,file in [('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:cmd+=['--extern',lib+'='+str(deps/file)]
 cmd+=['-o',str(folder/'probe.exe')];oldoutput=Path(h.read(up_parent/'protocol.json')['raw_output']) if name=='up' else down_parent/'output';units[name]={'folder':str(folder),'rustc_command':cmd,'legacy_cases':legacy,'expected_cases':len(uc) if name=='up' else len(dc),'marker':marker,'legacy_raw':{n:{'path':str(oldoutput/n),'bytes':(oldoutput/n).stat().st_size,'sha256':h.sha(oldoutput/n)} for n in ['inputs.bin','baseline.bin','baseline-inputs.bin']}}
files=[Path(__file__),ROOT/'runs/E099-direct-execute.py',ROOT/'runs/E099-direct-audit.py',ROOT/'epoch/common.py',R/'protocol.json',R/'report.json',ROOT/'runs/E099-source/manifest.json',ROOT/'runs/E099-source/source-review.json',up_parent/'probe.rs',up_parent/'corpus.json',down_parent/'probe.rs',down_parent/'corpus.json']+[p for p in G.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
for script in ['E099-direct-execute.py','E099-direct-audit.py']:ast.parse((ROOT/'runs'/script).read_text())
h.save(G/'protocol.json',{'id':'E099-direct-controls','at':h.now(),'status':'FROZEN_PRE_BOTH_COMPILERS_AND_GPU_RAW_PROCESSES','units':units,'native_sequence':['up','down'],'required_free_bytes':32*1024**3,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'TwofreshRustcompilers,twofixedGPUrawprocesses,onefullstreamreader. Retain original819up/1530down cases and exactlegacy rawprefixes. Append fixedeven/aligned/oddguard/nonfinite/algorithm/lock/width/count0/reuse0 controls. ExactresourcePTX only; noNVRTC/newsource/sample/numericperformance/adoption. Stoponfirstgenuinenumericfailure; preservepartialfilesandclosepairedformwithoutrescue. Multinode/fullengine/fullcanonical/ordinary/broad/material/samequalityspeed gatesremain pending evenifthisdirectgatepasses.','candidate_accepted':False})
for name in ['protocol.json']:
 p=G/name;dst=h.ar.DASHBOARD/'evidence'/G.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+G.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='E099');item.update(stage='Frozen full-word direct numerical comparisons',correctness='compiled36gates_pass_raw_pending',reason='Original9entries exact; pairedloads emitted. Down registers40to48/occupancy12to10, up62to64/occupancy8same. No new local/shared/maxthread loss. Now7062up+6466down pairs, originalcases retained plus aligned/nonfinite/fallback/reuse0; no speedclaim.');item['evidence'].append({'label':'Frozen full-word numerical matrix','url':'evidence/'+G.name+'/protocol.json'});s.update(updated_at=h.now(),stage='Paired action direct raw GPU equivalence',activity='Compile-only gate passed with disclosed register/occupancy warning. Fixed direct raw word/input/guard controls next. E080/16 and source remain unchanged.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(G/'protocol.json'),flush=True)
