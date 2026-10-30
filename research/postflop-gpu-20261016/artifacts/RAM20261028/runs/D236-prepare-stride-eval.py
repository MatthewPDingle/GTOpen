import ast,copy,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists();h.read(ROOT/'runs/E109-direct-batch/report.json')
U=ROOT/'runs/D233-stride-up-action';H=ROOT/'runs/D236-stride-eval';H.mkdir(exist_ok=False);cases=[]
for mode in [0,1]:
 for c in h.read(U/'corpus.json')['cases']:
  r=copy.deepcopy(c);r.update(id=len(cases),evaluation_mode=mode);r['descriptor']+=[mode];cases.append(r)
assert len(cases)==1638;h.save(H/'corpus.json',{'cases':cases,'scope':'All original819 up-action shapes and value profiles in each BR and average evaluation mode. No null lock pointers, no filtering.'})
for name in ['baseline.ptx','candidate.ptx','discounts.rs']:shutil.copyfile(U/name,H/name)
source=(U/'probe.rs').read_bytes().decode('utf-8');changes=[]
def replace(old,new):
 global source
 assert source.count(old)==1,(old,source.count(old));source=source.replace(old,new,1);changes.append({'old':old,'new':new})
replace('struct Case {nh:','struct Case {evaluation_mode:i32,nh:')
a=source.index(' let mut cases=Vec::new();');b=source.index(' let case_count=cases.len();',a);old=source[a:b]
loader=''' let declared:serde_json::Value=serde_json::from_str(include_str!("corpus.json")).unwrap();
 let cases:Vec<Case>=declared["cases"].as_array().unwrap().iter().map(|c|{let n=|k:&str|c[k].as_u64().unwrap();Case{evaluation_mode:n("evaluation_mode") as i32,nh:n("hands") as usize,na:n("actions") as usize,block:n("threads") as u32,p:n("p") as i32,role:n("role") as u32,algo:n("algorithm") as u32,t:n("iteration") as u32,mode:n("value_mode") as u32,count:n("count") as i32}}).collect();assert_eq!(cases.len(),1638);
'''
replace(old,loader);replace('let Case{nh,na,block,p,role,algo,t,mode,count}=*c;','let Case{evaluation_mode,nh,na,block,p,role,algo,t,mode,count}=*c;')
replace('loff as u32]);','loff as u32,evaluation_mode as u32]);')
replace('let bf=bm.load_function("up_action").unwrap();let cf=cm.load_function("up_action").unwrap();','let bf=bm.load_function("up_action_eval").unwrap();let cf=cm.load_function("up_action_eval").unwrap();')
old='unsafe{stream.launch_builder(f).arg(&dn).arg(&start).arg(&count).arg(&p).arg(&dp).arg(&da).arg(&doff).arg(&dcs).arg(&dc).arg(&mut dr).arg(&mut ds).arg(&drs).arg(&drp).arg(&dl).arg(&dls).arg(&dslot).arg(&mut dv).arg(&dd).arg(&nharg).arg(&maxarg).launch(LaunchConfig{grid_dim:(3,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();}'
new='unsafe{stream.launch_builder(f).arg(&dn).arg(&start).arg(&count).arg(&p).arg(&evaluation_mode).arg(&dp).arg(&da).arg(&doff).arg(&dcs).arg(&dc).arg(&ds).arg(&dl).arg(&dls).arg(&dslot).arg(&mut dv).arg(&nharg).arg(&maxarg).launch(LaunchConfig{grid_dim:(3,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();}'
replace(old,new);replace('role==0 && i>=off','false && i>=off');replace('"stage":"case","id":index,','"stage":"case","id":index,"evaluation_mode":evaluation_mode,')
source=source.replace('D233','D236');(H/'probe.rs').write_bytes(source.encode('utf-8'))
audit=(U/'audit.py').read_bytes().decode('utf-8').replace('D233-stride-up-action-root-check','D236-stride-eval-root-check').replace('D233','D236').replace('kind==2 or role==0','kind==2').replace('len(cases)==819','len(cases)==1638').replace("summary['kernel_launches']==1638","summary['kernel_launches']==3276").replace("'cases':819,'kernel_launches':1638","'cases':1638,'kernel_launches':3276").replace('pass_scoped_up_action_raw_equivalence','pass_scoped_up_action_eval_raw_equivalence')
needle="for case,marker in zip(cases,markers[:-1]):";assert audit.count(needle)==1;audit=audit.replace(needle,"req({m:sum(c['evaluation_mode']==m for c in cases) for m in [0,1]}=={0:819,1:819},'both full evaluation mode corpora')\n"+needle+"\n req(marker['evaluation_mode']==case['evaluation_mode'],'actual mode identity')",1)
ast.parse(audit);(H/'audit.py').write_bytes(audit.encode('utf-8'))
h.save(H/'source-review.json',{'at':h.now(),'cases':1638,'kernel_launches':3276,'full_original_shape_value_profile_modes':True,'changes':changes,'non_null_original_17argument_eval_ABI_both_arms':True,'seed_generators_float_code_immutable_images_and_disjoint_guards_preserved':True,'scope':'All original819 retained shapes repeated forBR andaverage. Evaluation only updates owned CFV row; regret/strategy/otherarrays must be entirely unmodified. Complete independent retained raw reader, no speed samples.'})
cmd=[x.replace(str(U),str(H))for x in h.read(U/'protocol.json')['rustc_command']]
files=[Path(__file__),ROOT/'runs/D236-execute-stride-eval.py',U/'protocol.json',U/'probe.rs',U/'audit.py',U/'corpus.json',ROOT/'runs/E109-source/manifest.json',ROOT/'runs/E109-direct-batch/report.json',ROOT/'epoch/common.py']+[p for p in H.iterdir()if p.is_file()]+[p for p in(ROOT/'reference/accepted-e080-deps').iterdir()if p.is_file()]
h.save(H/'protocol.json',{'id':'D236','at':h.now(),'status':'FROZEN_PRE_COMPILER_NATIVE','rustc_command':cmd,'cases':1638,'kernel_launches':3276,'required_free_bytes':66*1024**3,'raw_reservation_bytes':12*1024**3,'raw_output':str(H/'output'),'input_sha256':{str(p):h.sha(p)for p in files},'failure':'Genuine numeric/ABI/input/guard failure closesE109 without source/helper/width/mode/subset/flag/quality/sample rescue. Completed native cases never repeat for mechanical observer repair.'})
for name in ['protocol.json','source-review.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
print(h.sha(H/'protocol.json'),flush=True)
