import sys,shutil,ast,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
assert h.read(ROOT/'comparisons/D163-action-compiler-controls/report.json')['cases']==2349
assert h.read(ROOT/'comparisons/D164-showdown-compiler-control/report.json')['inventory']['comparison_pairs']==1820
prior=ROOT/'runs/D150-CFV-liveness';H=ROOT/'runs/D165-compiler-engine-control';H.mkdir(exist_ok=False);(H/'gpu').mkdir()
for name in ['arena.rs','kernels.cu']:shutil.copyfile(prior/'gpu'/name,H/'gpu'/name)
for arm in ['baseline','candidate']:shutil.copyfile(ROOT/'runs/D162-private-dependency-repair/execution'/(arm+'.ptx'),H/(arm+'.ptx'))
production=(h.REPO/'crates/solver/src/gpu/mod.rs').read_text(encoding='utf-8');parent=(prior/'gpu/mod.rs').read_text(encoding='utf-8')
start=parent.index('        static PTX:');end=parent.index('            .clone()?;',start)+len('            .clone()?;');original=parent[start:end]
assert original in production and parent.count(original)==1
replacement='        let ptx = crate::d165_ptx(arch);';adapted=parent[:start]+replacement+parent[end:]
assert adapted.replace(replacement,original,1)==parent
(H/'gpu/mod.rs').write_bytes(adapted.encode());(H/'original-compilation-block.txt').write_bytes(original.encode())
src=(prior/'probe.rs').read_text(encoding='utf-8')
needle='let mut b = observed::GpuSolver::new(&a).unwrap(); let mut g = observed::GpuSolver::new(&c).unwrap();'
assert src.count(needle)==2;src=src.replace(needle,'let mut b = d165_new(0,&a); let mut g = d165_new(1,&c);')
binding='''
static D165_ARM:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(2);
static D165_BINDS:[std::sync::atomic::AtomicUsize;2]=[std::sync::atomic::AtomicUsize::new(0),std::sync::atomic::AtomicUsize::new(0)];
fn d165_ptx(arch:&str)->cudarc::nvrtc::Ptx{
 assert_eq!(arch,"compute_120");let arm=D165_ARM.load(std::sync::atomic::Ordering::SeqCst);assert!(arm<2);
 let call=D165_BINDS[arm].fetch_add(1,std::sync::atomic::Ordering::SeqCst)+1;
 println!("D165_PTX_BIND {}",serde_json::json!({"arm":arm,"call":call,"architecture":arch}));std::io::stdout().flush().unwrap();
 cudarc::nvrtc::Ptx::from_src(if arm==0{include_str!("baseline.ptx")}else{include_str!("candidate.ptx")})
}
fn d165_new(arm:usize,solver:&Solver)->observed::GpuSolver{
 assert!(arm<2);D165_ARM.store(arm,std::sync::atomic::Ordering::SeqCst);
 let result=observed::GpuSolver::new(solver).unwrap();assert_eq!(D165_ARM.load(std::sync::atomic::Ordering::SeqCst),arm);result
}
'''
src+=binding
needle='    assert_eq!(phase_pairs, 752); assert_eq!(epoch, 752); assert_eq!(root_pairs, 32);'
assert src.count(needle)==1;src=src.replace(needle,needle+'\n    assert_eq!(D165_BINDS[0].load(std::sync::atomic::Ordering::SeqCst),72);assert_eq!(D165_BINDS[1].load(std::sync::atomic::Ordering::SeqCst),72);',1)
(H/'probe.rs').write_bytes(src.encode())
audit=(prior/'audit.py').read_text(encoding='utf-8').replace("D = ROOT/'comparisons/D150-CFV-liveness'","D = ROOT/'comparisons/D165-compiler-engine-control'",1).replace("'id':'D150'","'id':'D165'",1).replace('pass_scoped_actual_CFV_clobber_liveness','pass_scoped_compiler_engine_raw_lifecycle_equivalence',1)
audit=audit.replace('Actual paged/stored continuation wrappers, large capacity, packing arithmetic, resource/loading and speed remain unproven.','The two instances use sealed12.9/13PTX;all9kernels run in ordinary,graph,eval,lock/save/resume/plain-continuation workflows. Actual paged/stored wrappers,canonical large cases,all generic menus,private runtime compiler integration,capacity/material and speed remain unproven.')
(H/'audit.py').write_bytes(audit.encode());ast.parse(audit)
execute=(prior/'execute.py').read_text(encoding='utf-8').replace('comparisons/D150-CFV-liveness/report.json','comparisons/D165-compiler-engine-control/report.json').replace('D150 finite CFV clobber controls and raw reader passed.','D165 sealed compiler engine controls and raw reader passed.')
(H/'execute.py').write_bytes(execute.encode());ast.parse(execute)
review=h.read(prior/'source-review.json');review.update(at=h.now(),id='D165',parent_source_sha256=h.sha(prior/'gpu/mod.rs'),exact_reverse_compiler_adapter_to_parent=True,production_numerical_work_and_main_kernel_unchanged=True,compiler_outputs_differ=True,scope='Same existing36case/752phase/324EV/32changing-range-root matrix and entire input/range/phase/seed corpus. Only test module binding chooses sealed12.9vs13PTX for each constructor. Single serialized main sets atomic before synchronous constructor;source-bound144binding markers must be72perarm. All returned instance functions/graphs retain own module;globalselector not consulted in numericalwork. Zero-validation setup threads joined before next selector set. No production cache/loader/host math/launch/quality or source transform. Inherited full66field validator,CFV-only poison,raw readers and all finite engine workflows remain. No NVRTC/compiler performance score. Any actual numerical mismatch closes13form without source/corpus/shape/source/version/flags/sample rescue.')
h.save(H/'source-review.json',review)
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for name,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
cmd+=['-o',str(H/'probe.exe')]
files=[Path(__file__),prior/'probe.rs',prior/'gpu/mod.rs',prior/'gpu/arena.rs',prior/'audit.py',prior/'execute.py',prior/'source-review.json',ROOT/'comparisons/D163-action-compiler-controls/report.json',ROOT/'comparisons/D164-showdown-compiler-control/report.json']+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
h.save(H/'protocol.json',{'id':'D165','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_ENGINE_CONTROLS','rustc_command':cmd,'cases':36,'phase_pairs':752,'constructor_pairs':36,'expected_PTX_bindings':{'0':72,'1':72},'exploitability_pairs':324,'continuation_root_pairs':32,'raw_reservation_bytes':96*1024**3,'required_free_bytes':162*1024**3,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'Same finite existing36case native/retained full raw control matrix,now sealed12.9vs13PTX. One Rust compiler,one GPUengine process,one whole-word reader. Native math/corpus/stages exact;only explicit constructor module selection. No NVRTC repeat/new runtime integration,performance score,production activation or shape/corpus/source/version/flag/sample rescue after numericalfailure.'})
# Publish frozen prerequisites and tracker before execution; no native child started here.
import urllib.request
for name in ['protocol.json','source-review.json']:
    path=H/name;dest=h.ar.DASHBOARD/'evidence'/H.name/name;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(path,dest)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20) as response:assert response.read()==path.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);assert not any(x['id']=='D165' for x in status['experiments'])
    status['experiments'].append({'id':'D165','title':'CUDA13 complete-engine raw lifecycle controls','kind':'diagnostic','status':'staged','accepted':False,'correctness':'not_executed','measurement_epoch':'RAM20261028','stage':'Frozen36case engine matrix;all66device fields and CPU/save/query state','reason':'Same original DCFR/CFR+,F32/compressed,iso/noiso,cold/warm,locks,graph/eager/replay,save/resume and32plain changing-range continuation roots. Both sealedPTX in serialized sameengine instances. No runtime integration or speed result.','evidence':[{'label':'Frozen full engine protocol','url':'evidence/D165-compiler-engine-control/protocol.json'},{'label':'Exact module-binding adapter and inherited validators','url':'evidence/D165-compiler-engine-control/source-review.json'}]})
    status.update(updated_at=h.now(),active_experiment='D165',stage='CUDA13 complete-engine controls',activity='Action2349cases and showdown1820pairs exact. Full engine raw lifecycle matrix prepared next;no runtime compiler candidate or speed qualification yet. E08010.4564s remains live.')
    h.ar.atomic_json(h.ar.STATUS,status)
h.custody();print(h.sha(H/'protocol.json'),flush=True)
