"""Freeze copied-constructor component before any new compilation or native test."""
from pathlib import Path
import ast,difflib,json,re,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018';sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=80*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
H=R/'runs/D134-zero-init-fences';S=R/'runs/E083-source';assert H.exists()and not(H/'protocol.json').exists()and not S.exists();S.mkdir()
def function(text,needle):
    a=text.index(needle);left=text.index('{',a);j=left+1;depth=1
    while depth:
        if text[j]=='{':depth+=1
        elif text[j]=='}':depth-=1
        j+=1
    return a,j,text[a:j]
rel_a='crates/solver/src/gpu/arena.rs';rel_m='crates/solver/src/gpu/mod.rs';arena=(old.REPO/rel_a).read_bytes().decode();module=(old.REPO/rel_m).read_bytes().decode();an='\r\n'if'\r\n'in arena else'\n';mn='\r\n'if'\r\n'in module else'\n'
ac=arena;needle='self.upload_prechecked(stream, solver, p, which, staging, None)';assert ac.count(needle)==1;ac=ac.replace(needle,'self.upload_prechecked(stream, solver, p, which, staging, None, false)',1)
needle="staging: &mut [f32], check: Option<&ZeroCheck<'_>>,";assert ac.count(needle)==1;ac=ac.replace(needle,needle+an+'        defer_zero_sync: bool,',1)
needle='            let device = stream.alloc_zeros::<f32>(self.len).map_err(e)?;'+an+'            stream.synchronize().map_err(e)?;'+an+'            return Ok(device);';replacement='            let device = stream.alloc_zeros::<f32>(self.len).map_err(e)?;'+an+'            if !defer_zero_sync { stream.synchronize().map_err(e)?; }'+an+'            return Ok(device);';assert ac.count(needle)==1;ac=ac.replace(needle,replacement,1)
mc=module
for i in range(4):
    needle=f'zero_checks.as_ref().map(|checks| &checks[{i}]))?';repl=f'zero_checks.as_ref().map(|checks| &checks[{i}]), true)?';assert mc.count(needle)==1;mc=mc.replace(needle,repl,1)
a,b,ctor=function(mc,'    pub fn new_with_budget(');needle='        Ok(GpuSolver {';assert ctor.count(needle)==1;newctor=ctor.replace(needle,'        let gpu = GpuSolver {',1);end=newctor.rfind('        })');assert end>0;newctor=newctor[:end]+'        };'+mn+'        gpu.stream.synchronize().map_err(e)?;'+mn+'        Ok(gpu)'+newctor[end+10:];mc=mc[:a]+newctor+mc[b:]
# Independently reconstruct the baseline; no unrelated production hunk.
ar=ac.replace(replacement,needle if False else '            let device = stream.alloc_zeros::<f32>(self.len).map_err(e)?;'+an+'            stream.synchronize().map_err(e)?;'+an+'            return Ok(device);',1).replace(an+'        defer_zero_sync: bool,','',1).replace('self.upload_prechecked(stream, solver, p, which, staging, None, false)','self.upload_prechecked(stream, solver, p, which, staging, None)',1);assert ar==arena
mr=mc
for i in range(4):mr=mr.replace(f'zero_checks.as_ref().map(|checks| &checks[{i}]), true)?',f'zero_checks.as_ref().map(|checks| &checks[{i}]))?',1)
mr=mr.replace('        let gpu = GpuSolver {','        Ok(GpuSolver {',1).replace('        };'+mn+'        gpu.stream.synchronize().map_err(e)?;'+mn+'        Ok(gpu)','        })',1);assert mr==module
for name,text in[('baseline-arena.rs',arena),('candidate-arena.rs',ac),('baseline-mod.rs',module),('candidate-mod.rs',mc)]:(S/name).write_bytes(text.encode())
owned={rel_a:{'base':str(S/'baseline-arena.rs'),'candidate':str(S/'candidate-arena.rs')},rel_m:{'base':str(S/'baseline-mod.rs'),'candidate':str(S/'candidate-mod.rs')}}
scope='Only four proven-positive-zero action-arena uploads in GpuSolver construction defer their per-arena stream waits. All allocations and every zero fill remain; add one final initialization stream wait before returning the fully owned GpuSolver. Ordinary ArenaLayout::upload keeps defer=false, and every F32/nonzero/staging upload keeps its original wait. No new buffers, graph/capture/launch, CPU helper/thread, kernel/math/precision, skipped predicate/initialization, layout, payload, save or quality changes. E080 full zero predicates and borrowed-token guards remain unchanged.'
old.save(S/'manifest.json',{'id':'E083','at':old.now(),'owned':owned,'candidate_owned_sha256':{n:old.sha(v['candidate'])for n,v in owned.items()},'scope':scope,'source_activated':False,'candidate_accepted':False})
old.save(S/'source-review.json',{'at':old.now(),'scope':scope,'production_source_reverse_exact':True,'zero_eligibility_predicates_unchanged':True,'normal_upload_for_other_callers_retains_original_sync':True,'final_constructor_fence':'All allocations/copies/zeroing queued on the original one stream; final synchronize occurs before return and before original local host inputs drop. Deferred asynchronous errors still surface before returning this constructor. No forced driver/allocation failure injection or universal error-text equivalence claim.','references':['https://docs.nvidia.com/cuda/cuda-driver-api/cuda_driver_api/group__CUDA__MALLOC__ASYNC.html','https://docs.nvidia.com/cuda/cuda-driver-api/cuda_driver_api/group__CUDA__STREAM.html'],'counterevidence':'Pageable copies may themselves serialize pending work; batching may save little. Added final wait also applies to already-synchronous warm/F32 constructor paths. Small-case and actual material/compatibility guards remain mandatory. Closed GPU quantization/readback overlap, zero-scan omission/provenance and context/plan worker forms are not reused.','component_limits':'Copied exact constructor with only public accepted-GpuPlan import adapter and post-timing device-validation methods. Component clock is full GPU initialization plus required readiness, not complete solve. Shader kernels never launch in component tests. Same source fields and every device byte checked after the clock.'})
for name,bt,ct in[('arena.patch',arena,ac),('mod.patch',module,mc)]:(S/name).write_text(''.join(difflib.unified_diff(bt.splitlines(True),ct.splitlines(True),fromfile='accepted/'+name,tofile='E083/'+name)),encoding='utf-8',newline='')
history=[]
for cmd in[['git','log','--all','--oneline','-G','deferred|batch.*sync|initial.*fence|zero.*synchroniz','--','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/arena.rs'],['rg','-n','-i','zero.{0,60}synch|synch.{0,60}zero|batch.{0,30}(initial|upload|alloc)|defer.{0,30}(sync|fence)','research/postflop-gpu-20261016/experiments.md']]:
    p=subprocess.run(cmd,cwd=old.REPO,text=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);assert p.returncode in[0,1];history.append({'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
old.save(H/'history.json',{'at':old.now(),'bounded_history':history,'limits':'No matching implemented initialization-fence batching found in bounded local GPU source/ledger history. Unrelated zero/scan source references remain counterevidence and closed.'})
cuda=(old.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();_,_,lock_fn=function(module,'fn build_lock_table(')
fold_start=module.index('        let mut fold_card_off');fold_end=module.index('        Ok(GpuSolver {',fold_start);fold=module[fold_start:fold_end]
struct_start=module.index('pub struct GpuSolver {');struct_end=module.index('fn checks_with_setup',struct_start);fields=re.findall(r'^    (d_\w+): (CudaSlice<(\w+)>|\[CudaSlice<(\w+)>; 2\]),',module[struct_start:struct_end],re.M);assert len(fields)>40
_,_,base_ctor=function(module,'    pub fn new_with_budget(');meta=[]
for name,ty,t1,t2 in fields:
    if name in['d_regrets','d_strat','d_reach','d_cfv','d_disc','d_eval_roots']:continue
    match=re.search(r'^            '+name+r': (.+?)(?=^            \w+:|^        \}\))',base_ctor,re.M|re.S);assert match,name;rhs=match[1].strip().rstrip(',');exprs=re.findall(r'up(?:32|i32|64|f)\(&([^)]*)\)',rhs)
    if name=='d_lock_off':exprs=['lock_off']
    if name=='d_lock_sigma':exprs=['lock_sigma']
    expected=2 if t2 else 1;assert len(exprs)==expected,(name,rhs,exprs)
    for i,expr in enumerate(exprs):meta.append((name+('['+str(i)+']'if t2 else''),expr))
assert len(meta)==57,len(meta)
observer=r'''
impl GpuSolver {
    pub fn d134_validate(&self, solver: &Solver, path: &std::path::Path, fresh_zero: bool) -> serde_json::Value {
        assert_eq!(self._ctx.name().unwrap(), "NVIDIA GeForce RTX 5090");
        assert_eq!(self._ctx.compute_capability().unwrap(), (12,0));
        let mut plan=GpuPlan::build(&solver.spot,solver.use_isomorphism);
        let full_needed=plan.staging_bytes()+(solver.spot.tree.data_size[0]+solver.spot.tree.data_size[1])*8+512*1024*1024;
        if solver.storage==crate::store::Storage::F32 && full_needed<=u64::MAX {plan.use_full_action_arenas(&solver.spot);}
        let(lock_off,lock_sigma)=build_lock_table(solver);
// D134_FOLD
        let mut out=std::io::BufWriter::new(std::fs::OpenOptions::new().create_new(true).write(true).open(path).unwrap());
        use std::io::Write;out.write_all(b"D134-FRAME-v1\0\0\0").unwrap();
        let mut records=Vec::new();
// D134_META
        for seat in 0..2 {for which in 0..2 {
            let d=if which==0{&self.d_regrets[seat]}else{&self.d_strat[seat]};
            assert_eq!(d.len(),plan.arena_elements[seat]);let name=format!("arena-{seat}-{which}");
            if fresh_zero {records.push(crate::capture_zero(&self.stream,&name,d,&mut out));}
            else {let expected=crate::expected_arena(solver,&plan,seat,which);records.push(crate::capture(&self.stream,&name,d,&expected,&mut out));}
        }}
        records.push(crate::capture_zero(&self.stream,"reach0",&self.d_reach[0],&mut out));
        records.push(crate::capture_zero(&self.stream,"reach1",&self.d_reach[1],&mut out));
        records.push(crate::capture_zero(&self.stream,"cfv",&self.d_cfv,&mut out));
        records.push(crate::capture_zero(&self.stream,"disc",&self.d_disc,&mut out));
        records.push(crate::capture_zero(&self.stream,"eval_roots",&self.d_eval_roots,&mut out));
        assert_eq!(records.len(),66);out.flush().unwrap();out.get_ref().sync_all().unwrap();
        serde_json::json!({"fields":records.len(),"metadata_fields":57,"all_complete_images_exact":true,"records":records,"kernel_launches":0})
    }
}
'''
observer=observer.replace('// D134_FOLD',fold).replace('// D134_META','\n'.join('        records.push(crate::capture(&self.stream,"'+name+'",&self.'+name+',&'+expr+',&mut out));'for name,expr in meta))
for arm,mt,at in[('baseline',module,arena),('candidate',mc,ac)]:
    folder=H/arm;folder.mkdir();(folder/'kernels.cu').write_bytes(cuda);(folder/'arena.rs').write_bytes(at.encode());assert mt.count('pub mod plan;')==1;mt=mt.replace('pub mod plan;','pub mod plan { pub use solver::gpu::plan::*; }',1);(folder/'mod.rs').write_text(mt+observer,encoding='utf-8',newline='\n')
# Reuse the already calibrated Win64 observation ABI, outside the timing window.
res=(R/'runs/E080-resource-controls/evaluator.rs').read_text();left=res.index('#[repr(C)] #[derive(Default)] struct ResourceFileTime');right=res.index('const TARGET_PCT_POT',left);bridge=res[left:right]
probe=(H/'probe-template.rs').read_text().replace('// D134_OS_BRIDGE',bridge);(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n');shutil.copyfile(old.REPO/'bench_spot.json',H/'bench_spot.json');tiny=old.read(old.REPO/'bench_spot.json');tiny.update(board='Ks7h2dQhTc',range_oop='AA,KK,QQ,AKs',range_ip='AA,QQ,JJ,AQs');tiny['tree'].update(starting_pot=20.,effective_stack=100.,max_raises=2,rake_pct=0.,rake_cap=0.)
old.save(H/'tiny.json',tiny)
M=old.read(R/'binaries/E080-postflop_autoresearch.manifest.json');deps=M['dependency_artifact_sha256'];libs={}
for name in['solver','cudarc','serde_json','rayon']:
    values=[p for p in deps if Path(p).suffix=='.rlib'and Path(p).name.startswith('lib'+name+'-')];assert len(values)==1;libs[name]=values[0]
for p,h in deps.items():old.pin(p,h)
command=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(Path(libs['solver']).parent)]
for name,path in libs.items():command+=['--extern',name+'='+path]
command+=['-o',str(H/'probe.exe')]
for p in H.glob('*.py'):ast.parse(p.read_text())
files=[Path(__file__),*[p for p in H.rglob('*')if p.is_file()],*[p for p in S.iterdir()if p.is_file()],C/'common_e080_live.py',C/'protected-main.json',R/'binaries/E080-postflop_autoresearch.manifest.json',R/'runs/E080-graph-controls/protocol.json',R/'runs/E080-graph-controls/report.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
P={'id':'D134-zero-init-fence-component','at':old.now(),'status':'FROZEN_PRE_COMPILER_AND_NATIVE','rustc_command':command,'input_sha256':deps|{str(p):old.sha(p)for p in files},'order':[{'id':'B1','arm':'baseline'},{'id':'C1','arm':'candidate'},{'id':'C2','arm':'candidate'},{'id':'B2','arm':'baseline'},{'id':'B3','arm':'baseline'},{'id':'C3','arm':'candidate'}],'pairs':[{'baseline':'B1','candidate':'C1'},{'baseline':'B2','candidate':'C2'},{'baseline':'B3','candidate':'C3'}],'workloads':['rainbow','two-tone','river'],'minimum_saving_ms':94.215979,'budget_origin':'1% of frozen accepted E080 cumulative9421.5979ms used only as prospective component-admission constant; historical timing samples never pooled.','gates':'One compiler, one untimed ability process (fresh/warm compressed/F32, exact frames and budget refusal) then six fresh processes BC/CB/BC each all3canonical cases. Sum fixture-median GPU-initialization saving >=94.215979ms; both large fixtures positive median and>=2/3improving pairs; each fixture all-thread CPU median<=baseline*1.02+15.625ms. All66full actual device fields exact to fresh CPU references, full positive-zero words ORchecked, every baseline/candidate frame byteexact. No extra samples/exclusions/extensions or source, eligibility, helper, scope, fence, placement or caller variants after failure.','frame_encoding':'57metadata arrays saved as complete expected+actual u32images. Nine fresh-zero fields are read back in full and every word ORchecked==0, then losslessly represented as positive-zero runs with complete lengths. Warm ability stores retain full explicit expected/actual float bits. No sampled zero checks or fingerprints substitute for these full checks.','scope':'Copied actual GPU constructors/private ArenaLayout, with only accepted public-GpuPlan import adapter and identical post-timing validation additions. Same kernels and current E080 CPU-plan library. Component clock covers GpuSolver::new plus required readiness, excludes tree/CPU solver allocation, validation/readbacks/destruction. No app kernels or full solves; no complete-cycle gain/material/universal claim. Production source never activated. Actual allocator failure not forced.','output_reservation_bytes':8*1024**3,'minimum_free_S_bytes':80*1024**3,'candidate_accepted':False};old.save(H/'protocol.json',P)
pub=[]
for folder in[S,H]:
    for p in folder.rglob('*'):
        if not p.is_file():continue
        key=folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:assert response.read()==p.read_bytes()
        pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    st=old.read(old.ar.STATUS);assert not any(x['id']in['D134','E083']for x in st['experiments']);st['experiments'].extend([{'id':'D134','at':old.now(),'title':'Batch proven-zero initialization waits','status':'running','correctness':'pending','accepted':False,'stage':'Source-matched initialization component','reason':'Keep all zero fills and allocations, then wait once before returning the constructed solver. Test copied real constructors and all66device fields before considering an integrated trial. No solve speed result.','evidence':[{'label':'Frozen component and admission budget','url':'evidence/D134-zero-init-fences/protocol.json'},{'label':'Source and stream-order review','url':'evidence/E083-source/source-review.json'}]},{'id':'E083','at':old.now(),'title':'Batch constructor zero-arena waits','status':'planned','correctness':'pending','accepted':False,'reason':'Proposed exact two-file change awaits D134component admission; no production activation or full-solve sample.','evidence':[{'label':'Frozen candidate source scope','url':'evidence/E083-source/manifest.json'}]}]);st.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='D134',stage='D134 initialization fence component',activity='Testing whether batching proven-zero arena waits saves enough initialization time to justify a full trial. All allocations, zero fills and final readiness remain; actual device contents are checked after timing. E080 remains deployed at14.74% registered gain.');old.ar.atomic_json(old.ar.STATUS,st)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_verified_artifacts':pub,'compiler_or_native_executions':0});old.custody();print(old.sha(H/'protocol.json'),flush=True)
