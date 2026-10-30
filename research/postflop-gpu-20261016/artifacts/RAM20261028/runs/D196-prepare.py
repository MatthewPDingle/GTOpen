import ast, difflib, json, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status())
direct=ROOT/'comparisons/D195-parent-chance-controls/report.json';Q=h.read(direct)
assert Q['cases']==8345 and Q['all_actual_immutable_outputs_guards_exact']
assert h.read(ROOT/'runs/D195-parent-chance-controls/execution/complete.json')['all_owned_compilers_native_readers_terminal']
parent=ROOT/'runs/D176-cache-engine-control';H=ROOT/'runs/D196-parent-chance-engine';H.mkdir(exist_ok=True);(H/'gpu').mkdir(exist_ok=True);assert not(H/'protocol.json').exists()
S=ROOT/'runs/E102-source';resource=ROOT/'runs/E102-resource';R=h.read(resource/'report.json')
mechanism=ROOT/'comparisons/E102-parent-load-mechanism/report.json';assert h.read(mechanism)['status'].startswith('pass')
for name in ['arena.rs','kernels.cu']:
 if (H/'gpu'/name).exists():h.pin(H/'gpu'/name,h.sha(parent/'gpu'/name))
 else:shutil.copyfile(parent/'gpu'/name,H/'gpu'/name)
base=(S/'baseline-mod.rs').read_text();cand=(S/'candidate-mod.rs').read_text()
observed=(parent/'gpu/mod.rs').read_text();shim=observed[observed.index('pub mod plan {'):observed.index('\nmod arena;')]
start=base.index('        static PTX:');end=base.index('            .clone()?;',start)+len('            .clone()?;');compile_block=base[start:end]
def adapt(source):
 source=source.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1).replace(compile_block,'        let ptx = crate::d196_ptx(arch);',1)
 for decl in ['pub fn research_continuation_sweep(', 'fn research_continuation_sweep_impl(']:
  old='    #[cfg(feature = "preflop-research")]\n    '+decl;assert source.count(old)==1;source=source.replace(old,'    '+decl,1)
 return source
ab=adapt(base);ac=adapt(cand);old_prefix=ab.replace('d196_ptx','d176_ptx');assert observed.startswith(old_prefix)
suffix=observed[len(old_prefix):]
# Only the two complete production chance blocks are dispatched by an immutable per-instance arm.
def chance_blocks(source):
 out=[];at=0
 while True:
  try:i=source.index('            let sp = self.chance_',at)
  except ValueError:break
  if source.startswith('            let sp = self.chance_node_spans[l];',i) or source.startswith('            let sp = self.chance_spans[l];',i):
   j=source.index('            if sp.count > 0 {',i);depth=1;k=j+len('            if sp.count > 0 {')
   while depth:
    if source[k]=='{':depth+=1
    elif source[k]=='}':depth-=1
    k+=1
   block=source[i:k]
   if '.launch_builder(&self.f_down_chance' in block:out.append(block)
   at=k
  else:at=i+1
 return out
bb=chance_blocks(ab);cb=chance_blocks(ac);assert len(bb)==len(cb)==2
dual=ab
for b,c in zip(bb,cb):
 assert dual.count(b)==1
 branch='            if self.d196_candidate {\n'+c+'\n            } else {\n'+b+'\n            }'
 dual=dual.replace(b,branch,1)
dual=dual.replace('    f_down_chance: CudaFunction,','    f_down_chance: CudaFunction,\n    f_down_chance_parent: CudaFunction,\n    d196_candidate: bool,',1)
dual=dual.replace('        let nh = plan.nh;','        let nh = plan.nh;\n        let d196_candidate = crate::d196_candidate();\n        crate::d196_note_binding(d196_candidate, &nh, &plan);',1)
dual=dual.replace('            f_down_chance: func("down_chance")?,','            f_down_chance: func("down_chance")?,\n            f_down_chance_parent: func(if d196_candidate { "down_chance_parent" } else { "down_chance" })?,\n            d196_candidate,',1)
# Exact textual projection of each immutable arm must recover the accepted/candidate adapted host.
for candidate,want in [(False,ab),(True,ac)]:
 projected=dual
 for b,c in zip(bb,cb):
  branch='            if self.d196_candidate {\n'+c+'\n            } else {\n'+b+'\n            }'
  assert projected.count(branch)==1;projected=projected.replace(branch,c if candidate else b,1)
 projected=projected.replace('    f_down_chance_parent: CudaFunction,\n    d196_candidate: bool,','    f_down_chance_parent: CudaFunction,' if candidate else '',1)
 if not candidate:projected=projected.replace('    f_down_chance: CudaFunction,\n\n','    f_down_chance: CudaFunction,\n',1)
 projected=projected.replace('        let d196_candidate = crate::d196_candidate();\n        crate::d196_note_binding(d196_candidate, &nh, &plan);\n','',1)
 projected=projected.replace('            f_down_chance_parent: func(if d196_candidate { "down_chance_parent" } else { "down_chance" })?,\n            d196_candidate,','            f_down_chance_parent: func("down_chance_parent")?,' if candidate else '',1)
 if not candidate:projected=projected.replace('            f_down_chance: func("down_chance")?,\n\n','            f_down_chance: func("down_chance")?,\n',1)
 assert projected==want,('source projection',candidate)
(H/'gpu/mod.rs').write_text(dual+suffix,encoding='utf-8',newline='\n')
probe=(parent/'probe.rs').read_text().replace('D176_','D196_').replace('d176_','d196_')
probe+='''
fn d196_candidate()->bool{D196_ARM.load(std::sync::atomic::Ordering::SeqCst)==1}
fn d196_note_binding(candidate:bool,nh:&[usize;2],plan:&solver::gpu::plan::GpuPlan){let arm=D196_ARM.load(std::sync::atomic::Ordering::SeqCst);assert!(arm<2);assert_eq!(candidate,arm==1);println!("D196_PARENT_BIND {}",json!({"arm":arm,"hands":nh,"candidate":candidate,"down_name":if candidate{"down_chance_parent"}else{"down_chance"},"parents":plan.chance_node_spans.iter().map(|s|s.count as usize).sum::<usize>(),"edges":plan.chance_spans.iter().map(|s|s.count as usize).sum::<usize>()}));std::io::stdout().flush().unwrap();}
'''
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
for arm in ['baseline','candidate']:
 p=resource/'execution'/(arm+'-compute_120.ptx');h.pin(p,R['ptx_sha256'][arm+'-compute_120']);shutil.copyfile(p,H/(arm+'.ptx'))
audit=(parent/'audit.py').read_text().replace('D176-cache-engine-control','D196-parent-chance-engine').replace("'id':'D176'","'id':'D196'").replace('pass_scoped_cache_hint_engine_raw_lifecycle_equivalence','pass_scoped_parent_chance_engine_raw_lifecycle_equivalence').replace('sealedoriginal/cachehintPTX','sealedoriginal/parentfanoutPTX')
anchor='h.custody()\nD = ';assert audit.count(anchor)==1
audit=audit.replace(anchor,'''logs=(H/'execution/probe.stdout.log').read_text();binds=[__import__('json').loads(x.split('D196_PARENT_BIND ',1)[1]) for x in logs.splitlines() if 'D196_PARENT_BIND ' in x];ptx=[__import__('json').loads(x.split('D196_PTX_BIND ',1)[1]) for x in logs.splitlines() if 'D196_PTX_BIND ' in x]
req(len(binds)==len(ptx)==144,'all constructor/PTX binding markers')
req(sum(x['arm']==0 for x in binds)==sum(x['arm']==1 for x in binds)==72,'per-arm constructor count')
for x in binds:
    want=x['arm']==1;req(x['candidate']==want and x['down_name']==('down_chance_parent' if want else 'down_chance'),'literal per-instance kernel binding')
req(sum(x['candidate'] and x['parents']>0 for x in binds)==68,'actual candidate chance-bearing constructor count')
req(sum(x['candidate'] and x['parents']==0 for x in binds)==4,'river no-chance constructor count')
'''+'\n'+anchor,1)
ast.parse(audit);(H/'audit.py').write_text(audit,encoding='utf-8',newline='\n')
execute=(parent/'execute.py').read_text().replace('D176-cache-engine-control','D196-parent-chance-engine').replace('D176 sealed cache-hint engine controls and raw reader passed.','D196 parent chance engine controls and raw reader passed.')
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
review=h.read(parent/'source-review.json');review.update(id='D196',at=h.now(),source='Original36case D176 matrix and complete observer suffix retained. Adapted accepted E080 and E102 production host source are merged only by immutable per-instance arm. Constructor loads literal candidate new entry only for candidate; baseline has unused alias of original entry. Exact textual per-arm projection recovers production host after original public-plan/PTX adapters. No allocation/array/quality changes.',source_projection_exact=True,source_baseline_sha256=h.sha(S/'baseline-mod.rs'),source_candidate_sha256=h.sha(S/'candidate-mod.rs'),raw_contract='All66 constructor arrays to CPU oracle, every65 nonCFV device array and allCPU state/query/save/resume exact; every physical CFV poison seed checked and logical current-player CFV exact after regeneration. No speed samples. Canonical whole physical CFV still required.',closure='Any genuine numeric/control failure closes E102 exact parent fanout without grouping/width/guard/field/caller/helper/flag/source/sample rescue. Only pre-native mechanical adapters and retained-data reader repairs may be separately frozen without repeating native observations.',candidate_accepted=False)
h.save(H/'source-review.json',review)
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for name,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
cmd+=['-o',str(H/'probe.exe')]
files=[Path(__file__),ROOT/'epoch/common.py',direct,ROOT/'runs/D195-parent-chance-controls/protocol.json',ROOT/'runs/D195-parent-chance-controls/execution/complete.json',mechanism,resource/'protocol.json',resource/'report.json',S/'manifest.json',S/'source-review.json',S/'baseline-mod.rs',S/'candidate-mod.rs',parent/'protocol.json',parent/'source-review.json',parent/'gpu/mod.rs',parent/'probe.rs',parent/'execute.py',parent/'audit.py']+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
h.save(H/'protocol.json',{'id':'D196','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_ENGINE_RAW_PROCESS','rustc_command':cmd,'cases':36,'phase_pairs':752,'constructor_pairs':36,'expected_PTX_bindings':{'0':72,'1':72},'actual_chance_bearing_candidate_constructors':68,'exploitability_pairs':324,'continuation_root_pairs':32,'raw_reservation_bytes':128*1024**3,'required_free_bytes':194*1024**3,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'One fresh Rust compiler, one paired engine process, one complete raw reader. Original36 fixtures/order/stages and all raw/poison/CPU contracts retained. Both actual production candidate downward callers selected per immutable instance, legacy_down untouched. No NVRTC/source activation/speed/adoption. Any genuine failure closes exact form, no rescue. All later 1% complete/strict fixture/fresh16/broad/material/capacity/holdout/cumulative/application gates unchanged.'})
published=[]
for folder,names in [(direct.parent,['report.json']),(ROOT/'runs/D195-parent-chance-controls',['protocol.json']),(ROOT/'runs/D195-parent-chance-controls/execution',['complete.json']),(H,['protocol.json','source-review.json'])]:
 for name in names:
  p=folder/name;key=folder.relative_to(ROOT).as_posix()+'/'+name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  published.append({'label':folder.name+' '+name,'url':'evidence/'+key})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D195');item.update(status='measured',correctness='pass_full_raw_direct',stage='All8345paired GPU cases exact',reason='All425 original cases retained plus7920 prospective parent-fanout cases. Whole output/input/guards and independent bitcopy oracle exact, including signedzero/subnormal/Inf/qNaN/sNaN;16690launches, no solver timing.');item.setdefault('evidence',[]).extend(published[:3])
 s['experiments'].append({'id':'D196','title':'Parent chance complete engine state controls','kind':'diagnostic','status':'staged','accepted':False,'measurement_epoch':'RAM20261028','correctness':'pending_engine_raw_state','stage':'Frozen36case engine raw/lifecycle matrix','reason':'Both production downward callers,144actual constructor bindings,all66arrays/CPU/poison/graph/locks/save/resume/changingroots. No speed claim.','evidence':published[3:]});s.update(updated_at=h.now(),active_experiment='D196',stage='Parent chance full engine state prerequisite',activity='All8345 direct GPU pairs exact. Next36engine cases with full device/CPU state,graph,locks,save/resume andchanging root ranges. E080/GPU/compressed/16 remains live; no new gain.');h.ar.atomic_json(h.ar.STATUS,s)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n### D195 complete direct controls; D196 engine prerequisite\n\nE102 direct parent-fanout controls passed all8345pairs/16690launches: original425 cases preserve every original input/seed/baseline output word, plus7920 fixed Cartesian parent/hand/block/active/float/orbit cases. Full outputs/immutable inputs/guards and independent copy/mask oracle exact across signedzero/subnormal/Inf/qNaN/sNaN. Report7f731b8ec2058b126e4d8d9b574c8d64c8e0153dd4a6759e7a59c1fd5ede0c8d; all compiler/native/readers terminal. No GPU solve/speed claim.\n\nD196 freezes original36 full engine cases,752phases,324EVpairs,32changing-root continuation sweeps. Exact per-arm host source projection to E080/E102 after prior public-plan and sealed-PTX adapters, immutable per-instance arm, actual constructor entry markers. All prior full raw/CFV poison/CPU/query/save/resume/graph/lock controls retained. Canonical physical buffers and ordinary real runtime compiler timing still required; all rejection/adoption gates unchanged.\n')
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);subprocess.run(['git','commit','-m','research: retain complete parent chance controls and freeze engine checks'],cwd=h.REPO,check=True)
print(h.sha(H/'protocol.json'),flush=True)
