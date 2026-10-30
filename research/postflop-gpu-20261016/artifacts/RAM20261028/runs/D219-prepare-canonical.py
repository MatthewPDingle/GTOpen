import ast,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists()
assert h.read(ROOT/'runs/D217-nullable-lock-direct/report.json')['cases']==8397 and h.read(ROOT/'runs/D217-nullable-lock-direct/execution/complete.json')['all_owned_compilers_native_readers_terminal'];assert h.read(ROOT/'runs/D218-lock-map-boundaries/report.json')['actual_state_pairs']==80 and h.read(ROOT/'runs/D218-lock-map-boundaries/execution/complete.json')['all_owned_compiler_native_children_terminal']
parent=ROOT/'runs/D178-canonical-cache-control';S=ROOT/'runs/E106-source-r2';R=ROOT/'runs/E106-resource-host';H=ROOT/'runs/D219-nullable-lock-canonical';H.mkdir(exist_ok=False);old=(parent/'baseline/mod.rs').read_bytes().decode('utf-8');shim=old[old.index('pub mod plan {'):old.index('\nmod arena;')];suffix=old[old.index('\nimpl GpuSolver {\n    pub fn d166_snapshot'):];proof={}
for arm in ['baseline','candidate']:
 d=H/arm;d.mkdir();prod=(S/('baseline-mod.rs' if arm=='baseline' else 'candidate-mod.rs')).read_bytes().decode('utf-8');src=prod.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1);a=src.index('        static PTX:');b=src.index('            .clone()?;',a)+len('            .clone()?;');compileblock=src[a:b];binding='        assert_eq!(arch,"compute_120");\n        println!("D219_BIND '+arm+'");\n        let ptx=cudarc::nvrtc::Ptx::from_src(include_str!("../'+arm+'.ptx"));';src=src[:a]+binding+src[b:];assert src.replace(binding,compileblock,1).replace(shim,'pub mod plan;',1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);',1)==prod
 if arm=='candidate':
  needle='        if value.1 {';assert src.count(needle)==1;src=src.replace(needle,'        crate::d219_arg_bind(value.1);\n'+needle,1)
  observer='''
impl GpuSolver{pub fn d219_check(&self,s:&Solver,stage:&str){assert_eq!(self.locks_absent,s.locks.is_empty());assert_eq!(std::mem::size_of::<Self>(),4448);println!("D219_FLAG {}",serde_json::json!({"stage":stage,"absent":self.locks_absent,"CPU_lock_count":s.locks.len(),"wrapper_bytes":std::mem::size_of::<Self>()}));}}
'''
 else:observer='\nimpl GpuSolver{pub fn d219_check(&self,_s:&Solver,_stage:&str){assert_eq!(std::mem::size_of::<Self>(),4448);}}\n'
 (d/'mod.rs').write_bytes((src+suffix+observer).encode('utf-8'));shutil.copyfile(parent/'baseline/arena.rs',d/'arena.rs');h.pin(d/'arena.rs',h.sha(h.REPO/'crates/solver/src/gpu/arena.rs'));shutil.copyfile(S/(arm+'.cu'),d/'kernels.cu');p=R/'baseline-compute_120.ptx' if arm=='baseline' else R/'execution/candidate-compute_120.ptx';shutil.copyfile(p,H/(arm+'.ptx'));proof[arm]={'production_source_sha256':h.sha(S/('baseline-mod.rs' if arm=='baseline' else 'candidate-mod.rs')),'exact_reverse_after_only_old_plan_sealed_PTX_and_readonly_markers':True,'adapted_host_sha256':h.sha(d/'mod.rs')}
 code=(parent/(arm+'-probe.rs')).read_bytes().decode('utf-8').replace('D178','D219')
 for needle,var,solver in [('        let mut gpu = GpuSolver::new(&host).expect("benchmark requires CUDA");','gpu','host'),('    let mut g=GpuSolver::new(&s).unwrap();','g','s')]:
  assert code.count(needle)==1;code=code.replace(needle,needle+var+'.d219_check(&'+solver+',"constructor");',1)
 needle='    let info=g.d166_snapshot(&out.join(format!("{name}-{stage}.gpu.bin")));';assert code.count(needle)==1;code=code.replace(needle,'    g.d219_check(s,stage);\n'+needle,1)
 code+='\nfn d219_arg_bind(absent:bool){println!("D219_ARG {}",json!({"absent":absent,"null_word":if absent{Some(0u64)}else{None},"original_slice_delegate":!absent}));}\n';(H/(arm+'-probe.rs')).write_text(code,encoding='utf-8',newline='\n')
for name in ['bench_spot.json','bounded_child.py','sampler.py']:shutil.copyfile(parent/name,H/name)
audit=(parent/'audit.py').read_text(encoding='utf-8').replace('D178-canonical-cache-control','D219-nullable-lock-canonical').replace('D178_BIND','D219_BIND').replace("'id':'D178'","'id':'D219'")
needle="    conv=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']}";assert audit.count(needle)==1
inject='''    flags=[json.loads(x.split('D219_FLAG ',1)[1]) for x in text.splitlines() if x.startswith('D219_FLAG ')]
    binds=[json.loads(x.split('D219_ARG ',1)[1]) for x in text.splitlines() if x.startswith('D219_ARG ')]
    if arm=='candidate':
        req(len(flags)==18 and sum(x['stage']=='constructor' for x in flags)==6,'all candidate constructor and4stage flag checks')
        req(all(x['absent']==(x['CPU_lock_count']==0) and x['wrapper_bytes']==4448 for x in flags),'actual host predicate and exact original layout')
        req(sum(x['absent'] for x in flags)==9 and sum(not x['absent'] for x in flags)==9,'all initial-unlocked and locked/resumed predicate states')
        req(binds and any(x['absent'] for x in binds) and any(not x['absent'] for x in binds),'both actual argument branches execute')
        req(all((x['null_word']==0 and not x['original_slice_delegate']) if x['absent'] else (x['null_word'] is None and x['original_slice_delegate']) for x in binds),'staticzero or originalslice binding')
    else:req(not flags and not binds,'original host uses original pointer binding')
'''
audit=audit.replace(needle,inject+needle,1).replace("'scope':'Original three full", "'candidate_predicate_checks':18,'actual_null_and_nonnull_arguments_seen':True,'both_wrapper_bytes':4448,'scope':'Original three full",1);ast.parse(audit);(H/'audit.py').write_text(audit,encoding='utf-8',newline='\n')
execute=(parent/'execute.py').read_text(encoding='utf-8').replace('D178-canonical-cache-control','D219-nullable-lock-canonical').replace('D178','D219').replace('CFV cache-hint','Nullable-lock').replace('CFV cache hint','Nullable-lock');ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
review=h.read(parent/'source-review.json');review.update(id='D219',at=h.now(),source='Exact E080/E106r2 full host prefixes, old public-plan/fullarena adapters, sealed resourcePTX, unchanged D166 full66buffer/rawCPU/lifecycle observers and additional read-only argument/lockmap markers. Both actual wrappers4448, all original metadata equality retained without field exceptions.',source_reversal_proof=proof,scope='Original3 full compressed workloads, same .3%pot/check20/cap400/stops200/200/60. All12CPU+12entire69field GPUstate pairs,6queries/3saves/9futureEVs. Locks persist through saves/load; actual18predicate checks and both null/non-null argument branches required. All original process/RAM/disk/raw bounds unchanged. PrebuiltPTX/giantobserver clocks unscored; no speed claim.',failure='Any genuine numeric/physicalstate/lifecycle/binding/capacity failure closes exactE106 without source/helper/field/predicate/threshold/entry/flags/quality/sample rescue. Mechanical observer/reader errors retained separately without completed native cases repeated. All future ordinary/fresh16/broad/lockedcost/material/holdout/cumulative/application gates remain.');h.save(H/'source-review.json',review)
deps=ROOT/'reference/accepted-e080-deps';commands={}
for arm in ['baseline','candidate']:
 cmd=['rustc',str(H/(arm+'-probe.rs')),'--edition=2021','--test','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
 for name,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
 commands[arm]=cmd+['-o',str(H/(arm+'.exe'))]
oldP=h.read(parent/'protocol.json');paths=[Path(__file__),parent/'protocol.json',parent/'source-review.json',parent/'audit.py',parent/'execute.py',S/'manifest.json',S/'source-review.json',R/'report.json',ROOT/'runs/E106-engine-checkpoint/report.json',ROOT/'runs/D217-nullable-lock-direct/protocol.json',ROOT/'runs/D217-nullable-lock-direct/report.json',ROOT/'runs/D217-nullable-lock-direct/execution/complete.json',ROOT/'runs/D218-lock-map-boundaries/report.json',ROOT/'runs/D218-lock-map-boundaries/execution/complete.json',h.REPO/'crates/solver/src/save.rs',ROOT/'epoch/common.py',ROOT/'epoch/exact-anchor.json']+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
h.save(H/'protocol.json',{**{k:v for k,v in oldP.items() if k not in ['id','at','status','rustc_commands','input_sha256']},'id':'D219','at':h.now(),'status':'FROZEN_PRE_COMPILERS_AND_FULL_CANONICAL_NATIVE','rustc_commands':commands,'input_sha256':{str(p):h.sha(p) for p in paths},'scope':review['scope'],'failure':review['failure']})
evidence=[]
for folder,names in [(H,['protocol.json','source-review.json']),(ROOT/'runs/D217-nullable-lock-direct',['report.json']),(ROOT/'runs/D218-lock-map-boundaries',['report.json'])]:
 for name in names:
  p=folder/name;dst=h.ar.DASHBOARD/'evidence'/folder.name/name;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
  evidence.append({'label':folder.name+' '+name,'url':'evidence/'+folder.name+'/'+name})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D219','title':'Nullable lock original full canonical raw lifecycle','kind':'diagnostic','status':'staged','accepted':False,'measurement_epoch':'RAM20261028','stage':'Original200/200/60full-state workloads frozen','reason':'All CPU stores and66actual device buffers, entire physicalCFV,query/save/resume/futureEV plus lock-map predicate/binding checks. Same original quality and resource guards; no speed score.','evidence':evidence[:2]});item=next(x for x in s['experiments'] if x['id']=='E106');item.update(stage='Direct and predicate boundaries passed; full canonical state frozen');item.setdefault('evidence',[]).extend(evidence);s.update(updated_at=h.now(),active_experiment='D219',stage='No-lock full canonical state prerequisite',activity='8397direct pairs/16794launches and80host table/predicate states passed. Next fullsize original workloads and whole physical buffers/lifecycle before fresh ordinary NVRTC speed builds. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(H/'protocol.json'),flush=True)
