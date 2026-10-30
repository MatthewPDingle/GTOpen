"""Freeze E065's complete tree/capacity/error controls and fixed CPU admission screen."""
import ast,copy,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();old.ar.refuse_active(old.ar.live_status());assert not (ROOT/'gpu-run.lock').exists();assert shutil.disk_usage(ROOT).free>=66*1024**3
S=ROOT/'runs/E065-source';D=ROOT/'runs/D106-subtree-replication';H=ROOT/'runs/E065-tree-control';assert not H.exists();H.mkdir()
old.pin(S/'candidate-tree.rs','f01643acc261efc11df7e5e9cffbb3977e9e67a01ad8ba2211414af5be3437b4');old.pin(S/'baseline-tree.rs',old.BASE['crates/solver/src/tree.rs'])
for n in ['baseline-tree.rs','candidate-tree.rs']:(H/n).write_bytes((S/n).read_bytes())
design=old.read(D/'next-native-design.json');canonical=[];history=old.read(ROOT/'runs/D092-action-arity-order/report.json')
for i,entry in enumerate(design['canonical_inputs']):
 old.pin(entry['path'],entry['sha256']);spot=old.read(entry['path']);spot['tree']['carry_aggressor_through_checks']=False
 canonical.append({'id':i,'name':'canonical-'+str(i),'spot':spot,'expected_nodes':history['cases'][4*i]['nodes'],'strict':True,'cap':None})
empty={'bet':[],'raise':[],'donk':[]}
small={'starting_pot':10.0,'effective_stack':8.0,'rake_pct':0.05,'rake_cap':2.0,'oop':[copy.deepcopy(empty) for _ in range(3)],'ip':[copy.deepcopy(empty) for _ in range(3)],'allin_threshold':0.85,'add_allin':False,'max_raises':2,'carry_aggressor_through_checks':False}
controls=[]
def add(name,tree,board,hands=(7,11),strict=True,cap=100000):controls.append({'id':100+len(controls),'name':name,'tree':copy.deepcopy(tree),'board':board,'hands':list(hands),'strict':strict,'cap':cap})
add('empty-menus-flop',small,'Ks7h2d');add('empty-menus-turn',small,'Ks7h2d9c');add('empty-menus-river',small,'Ks7h2d9c3s')
for carry in [False,True]:
 t=copy.deepcopy(small);t['carry_aggressor_through_checks']=carry
 for player in ['oop','ip']:
  for st in t[player]:st.update(bet=[{'PotPct':33.0}],raise_=[{'PrevMult':2.0}]);st['raise']=st.pop('raise_')
 t['oop'][2]['donk']=[{'PotPct':50.0}];add('turn-initiative-'+str(carry),t,'Ks7h2d9c')
t=copy.deepcopy(small);t['effective_stack']=1.0;t['starting_pot']=20.0;t['add_allin']=True
for player in ['oop','ip']:
 for st in t[player]:st['bet']=['AllIn'];st['raise']=['AllIn']
add('flop-all-in-runouts',t,'AsKhQd')
t=copy.deepcopy(small);t['effective_stack']=1000.0;t['max_raises']=1;t['allin_threshold']=1.0
for player in ['oop','ip']:t[player][2]['bet']=[{'PotPct':float(x)} for x in range(10,111,10)]+['AllIn'];t[player][2]['raise']=[{'PrevMult':2.0}]
add('river-wide-menu',t,'AsKhQdJc2s',(1326,1081))
t=copy.deepcopy(small);t['oop'][1]['bet']=[{'PrevMult':2.5}];add('strict-bet-multiple-error',t,'Ks7h2d9c');add('lenient-bet-multiple-dropped',t,'Ks7h2d9c',strict=False)
t=copy.deepcopy(small);t['oop'][0]['bet']=[{'PrevMult':2.5}];add('unused-prior-street-size',t,'Ks7h2d9c3s')
t=copy.deepcopy(small)
for player in ['oop','ip']:
 for st in t[player]:st['bet']=[{'PotPct':33.33333333},{'PotPct':33.33333334},{'PotPct':33.3333333333}];st['raise']=[{'PrevMult':2.0},{'PrevMult':2.000000001}]
add('duplicate-rounded-sizes',t,'Ks7h2d9c')
t=copy.deepcopy(small);t['carry_aggressor_through_checks']=None;add('public-builder-absent-carry-flag',t,'Ks7h2d9c')
t=copy.deepcopy(small);t['starting_pot']=-1.0;add('negative-pot-error',t,'Ks7h2d9c');add('invalid-board-length',small,'Ks7h')
t=copy.deepcopy(small);t['effective_stack']=10000.0;t['allin_threshold']=1.0;t['oop'][2]['bet']=[{'PotPct':float(x)} for x in range(1,301)];add('too-many-actions-error',t,'Ks7h2d9c3s')
old.save(H/'corpus.json',{'canonical':canonical,'controls':controls,'budget_controls':'For each canonical reference N, compare exact results/errors for caps0,1,N-1,N,N+1after timing. No additional timed samples.'})
probe=r'''#![allow(dead_code)]
#[path="baseline-tree.rs"] mod baseline;
#[path="candidate-tree.rs"] mod candidate;
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},time::Instant};
use serde_json::{Value,json};
trait View {fn meta(&self)->[u64;11];fn node(&self,i:usize)->[u64;12];fn children(&self)->&[u32];fn action(&self,i:usize)->[u64;2];fn config(&self)->Vec<u8>;}
macro_rules! view {($m:ident)=>{impl View for $m::Tree {
 fn meta(&self)->[u64;11]{[self.nodes.len() as u64,self.children.len() as u64,self.actions.len() as u64,self.root_street as u64,self.data_size[0],self.data_size[1],self.nodes.capacity() as u64,self.children.capacity() as u64,self.actions.capacity() as u64,std::mem::size_of::<$m::Node>() as u64,std::mem::size_of::<$m::Action>() as u64]}
 fn node(&self,i:usize)->[u64;12]{let n=&self.nodes[i];[n.kind as u64,n.player as u64,n.street as u64,n.num_children as u64,n.children_start as u64,n.actions_start as u64,n.data_offset,n.put[0].to_bits(),n.put[1].to_bits(),n.t_win.to_bits(),n.t_lose.to_bits(),n.t_tie.to_bits()]}
 fn children(&self)->&[u32]{&self.children}
 fn action(&self,i:usize)->[u64;2]{match self.actions[i]{$m::Action::Fold=>[0,0],$m::Action::Check=>[1,0],$m::Action::Call(v)=>[2,v.to_bits()],$m::Action::Bet(v)=>[3,v.to_bits()],$m::Action::Raise(v)=>[4,v.to_bits()]}}
 fn config(&self)->Vec<u8>{serde_json::to_vec(&self.config).unwrap()}
}};}
view!(baseline);view!(candidate);
fn hash<T:View>(t:&T)->String {let mut h=0xcbf29ce484222325u64;let mut word=|x:u64|{for b in x.to_le_bytes(){h=(h^b as u64).wrapping_mul(0x100000001b3);}};let m=t.meta();for x in m{word(x);}for i in 0..m[0] as usize{for x in t.node(i){word(x);}}for &c in t.children(){word(c as u64);}for i in 0..m[2] as usize{for x in t.action(i){word(x);}}for b in t.config(){word(b as u64);}format!("{h:016x}")}
fn emit(v:Value){let mut o=std::io::stdout().lock();writeln!(o,"E065_TREE {v}").unwrap();o.flush().unwrap();}
fn write_u64(f:&mut BufWriter<File>,v:u64){f.write_all(&v.to_le_bytes()).unwrap();}
fn raw<A:View,B:View>(id:u32,name:&str,a:&A,b:&B)->u64 {let m=a.meta();assert_eq!(m,b.meta(),"metadata/capacity {name}");let ac=a.config();assert_eq!(ac,b.config(),"config {name}");let file=OpenOptions::new().write(true).create_new(true).open(format!("tree-{name}.bin")).unwrap();let mut f=BufWriter::with_capacity(1024*1024,file);f.write_all(b"D106-TREE-RAW1\0\0").unwrap();f.write_all(&id.to_le_bytes()).unwrap();f.write_all(&1u32.to_le_bytes()).unwrap();for t in [m,b.meta()]{for x in t{write_u64(&mut f,x);}}for c in [ac.as_slice(),ac.as_slice()]{write_u64(&mut f,c.len() as u64);f.write_all(c).unwrap();}let mut checks=11+ac.len() as u64;
 for i in 0..m[0] as usize{let aw=a.node(i);let bw=b.node(i);assert_eq!(aw,bw,"node {name} {i}");for row in [aw,bw]{for x in row{write_u64(&mut f,x);}}checks+=12;}
 assert_eq!(a.children(),b.children(),"children {name}");for (&x,&y) in a.children().iter().zip(b.children()){f.write_all(&x.to_le_bytes()).unwrap();f.write_all(&y.to_le_bytes()).unwrap();checks+=1;}
 for i in 0..m[2] as usize{let x=a.action(i);let y=b.action(i);assert_eq!(x,y,"action {name} {i}");for row in [x,y]{for w in row{write_u64(&mut f,w);}}checks+=2;}
 f.flush().unwrap();f.get_ref().sync_all().unwrap();checks}
fn inputs(case:&Value)->(Value,Vec<u8>,[usize;2]) {if let Some(spot)=case.get("spot") {let board=solver::cards::parse_cards(spot["board"].as_str().unwrap()).unwrap();let mask=board.iter().fold(0u64,|a,&c|a|(1u64<<c));let hands=std::array::from_fn(|p|{let range=solver::range::Range::parse(spot[if p==0{"range_oop"}else{"range_ip"}].as_str().unwrap()).unwrap();(0..solver::cards::NUM_COMBOS).filter(|&i|{let(c,d)=solver::cards::combo_from_index(i);range.weights[i]>0.0&&mask&((1u64<<c)|(1u64<<d))==0}).count()});(spot["tree"].clone(),board,hands)}else{(case["tree"].clone(),solver::cards::parse_cards(case["board"].as_str().unwrap()).unwrap(),[case["hands"][0].as_u64().unwrap() as usize,case["hands"][1].as_u64().unwrap() as usize])}}
fn build_a(v:&Value,board:&[u8],hands:[usize;2],cap:Option<usize>,strict:bool)->Result<baseline::Tree,String>{let cfg=serde_json::from_value(v.clone()).unwrap();baseline::TreeBuilder::build_with_options(&cfg,board,hands,cap,if strict{baseline::Strictness::Strict}else{baseline::Strictness::LenientLoad})}
fn build_b(v:&Value,board:&[u8],hands:[usize;2],cap:Option<usize>,strict:bool)->Result<candidate::Tree,String>{let cfg=serde_json::from_value(v.clone()).unwrap();candidate::TreeBuilder::build_with_options(&cfg,board,hands,cap,if strict{candidate::Strictness::Strict}else{candidate::Strictness::LenientLoad})}
fn compare_case(case:&Value,label:&str,cap:Option<usize>)->Value {let(v,board,hands)=inputs(case);let strict=case["strict"].as_bool().unwrap();let a=build_a(&v,&board,hands,cap,strict);let b=build_b(&v,&board,hands,cap,strict);match(a,b){(Ok(a),Ok(b))=>{let checks=raw(case["id"].as_u64().unwrap() as u32,label,&a,&b);json!({"label":label,"status":"exact_tree","raw_file":format!("tree-{label}.bin"),"checks":checks,"metadata":a.meta(),"fingerprint":hash(&a),"cap":cap,"hands":hands})},(Err(a),Err(b))=>{assert_eq!(a,b,"error {label}");json!({"label":label,"status":"exact_error","error":a,"cap":cap})},_=>panic!("success/error mismatch {label}")}}
fn median(v:&[f64])->f64{let mut x=v.to_vec();x.sort_by(f64::total_cmp);x[x.len()/2]}
fn main(){let args:Vec<String>=std::env::args().collect();assert_eq!(args.len(),3);let corpus:Value=serde_json::from_str(include_str!("corpus.json")).unwrap();if args[1]=="canonical" {let id:usize=args[2].parse().unwrap();let case=&corpus["canonical"][id];let(v,board,hands)=inputs(case);let mut reference=None;let mut asamples=Vec::new();let mut bsamples=Vec::new();let mut afinal=None;let mut bfinal=None;
 // Two unscored warmup pairs, then exactly nine alternating measured pairs.
 for first in [false,true]{for arm in [first,!first]{if arm{drop(build_b(&v,&board,hands,None,true).unwrap());}else{drop(build_a(&v,&board,hands,None,true).unwrap());}}}
 for pair in 0..9 {let candidate_first=pair%2==1;for arm in [candidate_first,!candidate_first]{if arm{let t=Instant::now();let tree=build_b(&v,&board,hands,None,true).unwrap();let ms=t.elapsed().as_secs_f64()*1000.0;std::hint::black_box(&tree);let fp=hash(&tree);assert_eq!(reference.as_ref().unwrap(),&fp);bsamples.push(ms);if pair==8{bfinal=Some(tree);}else{drop(tree);}}else{let t=Instant::now();let tree=build_a(&v,&board,hands,None,true).unwrap();let ms=t.elapsed().as_secs_f64()*1000.0;std::hint::black_box(&tree);assert_eq!(tree.nodes.len() as u64,case["expected_nodes"].as_u64().unwrap());let fp=hash(&tree);if let Some(r)=&reference{assert_eq!(r,&fp);}else{reference=Some(fp);}asamples.push(ms);if pair==8{afinal=Some(tree);}else{drop(tree);}}}}
 let a=afinal.unwrap();let b=bfinal.unwrap();let checks=raw(id as u32,&format!("canonical-{id}"),&a,&b);let meta=a.meta();let baseline_ms=median(&asamples);let candidate_ms=median(&bsamples);let slower=asamples.iter().zip(&bsamples).filter(|(a,b)|b>a).count();emit(json!({"stage":"canonical","id":id,"status":"pass_exact_tree_and_capacity","hands":hands,"metadata":meta,"checks":checks,"raw_file":format!("tree-canonical-{id}.bin"),"baseline_samples_ms":asamples,"candidate_samples_ms":bsamples,"baseline_median_ms":baseline_ms,"candidate_median_ms":candidate_ms,"saving_ms":baseline_ms-candidate_ms,"slower_pairs":slower,"positive_median_slowdown":candidate_ms>baseline_ms,"fingerprint":reference,"gpu_executions":0,"full_cycle_performance_measured":false}));drop(a);drop(b);
 // Fixed post-timing node-budget controls; each successful result has full raw data.
 for (j,cap) in [0usize,1,meta[0] as usize-1,meta[0] as usize,meta[0] as usize+1].into_iter().enumerate(){let label=format!("canonical-{id}-budget-{j}");emit(json!({"stage":"control","result":compare_case(case,&label,Some(cap))}));}
 }else{assert_eq!(args[1],"controls");assert_eq!(args[2],"all");for case in corpus["controls"].as_array().unwrap(){let label=case["name"].as_str().unwrap();let cap=case["cap"].as_u64().map(|x|x as usize);emit(json!({"stage":"control","result":compare_case(case,label,cap)}));}}
 emit(json!({"stage":"complete","all_exact":true,"gpu_executions":0,"full_cycle_performance_measured":false,"candidate_accepted":false}));}
'''
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
execute=r'''import json,os,shutil,subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
OUT=H/'execution'
def child(cmd,label,timeout):
 proc=None;fault=None;cleanup=None;start=old.now();clock=time.monotonic();old.save(OUT/(label+'.invocation.json'),{'at':start,'command':cmd,'cwd':str(OUT)})
 try:
  with (OUT/(label+'.stdout.log')).open('xb') as out,(OUT/(label+'.stderr.log')).open('xb') as err:
   proc=subprocess.Popen(cmd,cwd=OUT,env=old.env(),stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
   while True:
    try:proc.wait(timeout=10);break
    except subprocess.TimeoutExpired:
     elapsed=time.monotonic()-clock
     if elapsed>=timeout:raise TimeoutError(label)
     print(label,'running',int(elapsed),'seconds; child',proc.pid,flush=True)
 except BaseException as e:fault=repr(e);cleanup=old.ar.cleanup_child(proc);raise
 finally:old.save(OUT/(label+'.exit.json'),{'started_at':start,'finished_at':old.now(),'returncode':proc.returncode if proc else None,'error':fault,'cleanup':cleanup})
 assert proc.returncode==0,(label,(OUT/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-4000:])
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=66*1024**3;assert not OUT.exists();OUT.mkdir()
 child(P['rustc_command'],'rustc',180);old.custody();old.save(OUT/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(H/'probe.exe'),'native_executions':0})
 canonical=[];controls=[]
 for label,args in [('canonical-0',['canonical','0']),('canonical-1',['canonical','1']),('canonical-2',['canonical','2']),('controls',['controls','all'])]:
  child([str(H/'probe.exe'),*args],label,600);old.custody()
  markers=[json.loads(x.split('E065_TREE ',1)[1]) for x in (OUT/(label+'.stdout.log')).read_text(encoding='utf-8').splitlines() if x.startswith('E065_TREE ')];assert markers[-1]['stage']=='complete' and markers[-1]['all_exact']
  canonical.extend(m for m in markers if m['stage']=='canonical');controls.extend(m['result'] for m in markers if m['stage']=='control')
 assert len(canonical)==3 and [c['id'] for c in canonical]==[0,1,2] and len(controls)==15+P['extra_control_cases']
 raw_records=[]
 for row in canonical+controls:
  if 'raw_file' in row:
   f=OUT/row['raw_file'];assert f.is_file();raw_records.append({'path':str(f),'sha256':old.sha(f),'bytes':f.stat().st_size,'label':row.get('label','canonical-'+str(row.get('id'))),'checks':row['checks'],'metadata':row['metadata'],'hands':row['hands']})
 saving=sum(c['saving_ms'] for c in canonical);guards=[{'id':c['id'],'positive_median_slowdown':c['positive_median_slowdown'],'slower_pairs':c['slower_pairs'],'failed':c['positive_median_slowdown'] and c['slower_pairs']>=5} for c in canonical];passed=saving>=P['minimum_component_saving_ms'] and not any(g['failed'] for g in guards)
 report={'id':'E065-tree-control','at':old.now(),'status':'advance_to_integrated_qualification' if passed else 'rejected_component_admission','protocol_sha256':sys.argv[1],'canonical':canonical,'controls':controls,'raw_files':raw_records,'sum_component_median_saving_ms':saving,'required_component_saving_ms':P['minimum_component_saving_ms'],'component_guards':guards,'all_tree_fields_capacities_errors_exact':True,'measured_pairs_per_canonical':9,'warmup_pairs_per_canonical':2,'historical_timing_samples_scored':0,'exclusions':[],'extension_samples':0,'binary_sha256':old.sha(H/'probe.exe'),'all_owned_children_terminal':True,'source_activated':False,'gpu_executions':0,'full_cycle_performance_measured':False,'candidate_accepted':False,'limits':'TreeBuilder-only component admission, historical full-cycle number is a frozen reference, not a combined score. Each measured tree fingerprint/capacity matches; final full typed paired trees and every successful control retained. Raw root replay still required. No whole Spot/CPUStore/GPU/quality/process/peak/speedup qualification yet.'};old.save(H/'report.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ['canonical','controls','raw_files']},indent=2),flush=True)
'''
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
deps=ROOT/'build-e051-final-primary/release/deps';solver=deps/'libsolver-e2d3113d740308c1.rlib';serde=deps/'libserde-47b4d5f55b04d3b5.rlib';sj=deps/'libserde_json-83a0670a02a34a4d.rlib'
cmd=['rustc','--edition=2021',str(H/'probe.rs'),'--crate-name','e065_tree_probe','-C','opt-level=3','-C','lto=thin','-C','codegen-units=1','--extern','solver='+str(solver),'--extern','serde='+str(serde),'--extern','serde_json='+str(sj),'-L','dependency='+str(deps),'-o',str(H/'probe.exe')]
paths=[*H.iterdir(),*S.iterdir(),D/'next-native-design.json',D/'source-audit.json',D/'ledger-source-audit-snapshot.md',ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/D092-action-arity-order/report.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',Path(__file__)]+list(deps.glob('*.rlib'))+list(deps.glob('*.dll.lib'))
P={'id':'E065-tree-control','at':old.now(),'status':'FROZEN_PRE_COMPILER_AND_CPU_NATIVE','rustc_command':cmd,'input_sha256':{str(p):old.sha(p) for p in paths if p.is_file()},'extra_control_cases':len(controls),'source_sha256':old.read(S/'manifest.json')['candidate_owned_sha256'],'minimum_component_saving_ms':design['CPU_proxy_minimum_saving_ms'],'historical_reference_ms':design['CPU_proxy_reference_ms'],'sampling':'Fixed2warmup pairs+9alternatingBC/CBpairs in3canonical CPUprocesses, then fixed budget controls; one extra fixed control process. All retained. No extensions/exclusions/variants. All fingerprints/full raw validation outside component clock.','admission_rule':design['advance_rule'],'conditional_real_qualification':design['conditional_real_qualification'],'reserve_bytes':50*1024**3,'maximum_additional_disk_reservation_bytes':8*1024**3,'disk_free_bytes':shutil.disk_usage(ROOT).free,'source_activated':False,'GPU_executions':0,'full_cycle_performance_measured':False,'previous_goal_turn_classification':'progress: counter API busy outcome closed, address resource failure closed, distinct tree source staged.'}
old.save(H/'protocol.json',P)
published={}
for p in H.iterdir():
 if not p.is_file():continue
 key='evidence/'+H.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'artifact_sha256':published,'http_bytes_verified':True,'native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E065');assert e['status']=='preparing';e.update(status='running',stage='Frozen CPU full-tree/capacity/error and component screen',reason='Original/candidate source fixed.3canonical cases x9paired CPUtree builds, all typed final fields/capacities and fixed budget/legacy/menu/error controls. Require>=107.808471mscomponent saving proxy before real solve qualification; no full-cycle gain claim.');e['evidence'].append({'label':'Frozen CPU tree control protocol','url':'evidence/E065-tree-control/protocol.json'});st.update(updated_at=old.now(),state='running',active_experiment='E065',stage='E065 CPU tree controls and fixed component screen',activity='Full typed tree layouts, all3Vec capacities, budgets and legacy/error cases, plus9fixed pairs percanonical. CPUcomponent only; no GPU/whole-cycle gain accepted.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'status':'CPU_controls_frozen','protocol_sha256':old.sha(H/'protocol.json'),'canonical_cases':3,'extra_controls':len(controls),'native_executions':0}),flush=True)
