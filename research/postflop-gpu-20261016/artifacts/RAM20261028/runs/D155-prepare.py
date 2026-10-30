import sys,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
import numpy as np
h.custody();h.ar.refuse_active(h.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
assert h.read(ROOT/'runs/D154-packet-integration-units/report.json')['status']=='pass_isolated_integration_unit_prerequisites'
assert shutil.disk_usage(ROOT).free>=162*1024**3
S=ROOT/'runs/E092-source';M=h.read(S/'manifest.json')
for p,digest in M['owned_source_sha256'].items():h.pin(p,digest)
for name,digest in M['candidate_source_sha256'].items():h.pin(S/'candidate'/name,digest)
H=ROOT/'runs/D155-packet-engine-control';H.mkdir(exist_ok=False)
parent=ROOT/'runs/E090-engine-control/reference/D134-observer-parent.rs';text=parent.read_text(encoding='utf-8')
shim=text[text.index('pub mod plan {'):text.index('\nmod arena;')]
validator=text[text.index('impl GpuSolver {\n    pub fn d134_validate'):].replace('d134_validate','d155_validate').replace('D134','D155')
invent=None
for arm in ['baseline','candidate']:
    d=H/arm;shutil.copytree(S/arm,d)
    prod=(d/'mod.rs').read_text(encoding='utf-8')
    start=prod.index('    /// Research-only counterpart');end=prod.index('    pub fn new(solver:')
    part=prod[start:end];attribute='    #[cfg(feature = "preflop-research")]\n';assert part.count(attribute)==2
    exposed=part.replace(attribute,'');adapted=prod[:start]+exposed+prod[end:]
    adapted=adapted.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1)
    reverse=adapted.replace(shim,'pub mod plan;',1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);',1).replace(exposed,part,1)
    assert reverse==prod
    body=prod[prod.index('pub struct GpuSolver {'):prod.index('\nfn checks_with_setup')]
    fields=[]
    for name,kind,size in re.findall(r'^\s*(\w+):\s*(CudaSlice<\w+>|\[CudaSlice<\w+>;\s*(\d+)\])',body,re.M):
        fields.extend((f'{name}[{i}]',f'&self.{name}[{i}]') for i in range(int(size))) if size else fields.append((name,'&self.'+name))
    assert len(fields)==66 and (invent is None or invent==fields);invent=fields
    obs=(ROOT/'runs/D150-observer-template.rs').read_text(encoding='utf-8').replace('D150','D155').replace('d150','d155')
    obs=obs.replace('// D155_ALL_DEVICE_FIELDS','\n        '.join(f'field!("{n}", {e});' for n,e in fields),1)
    obs=obs.replace('"wrapper_bytes": std::mem::size_of::<Self>()','"wrapper_bytes": std::mem::size_of::<Self>(), "packet_module_loaded": '+('self.packet_functions.is_some()' if arm=='candidate' else 'false'),1)
    extra=(ROOT/'runs/D155-candidate-control.rs').read_text(encoding='utf-8') if arm=='candidate' else ''
    (d/'mod.rs').write_bytes((adapted+'\n'+validator+'\n'+obs+'\n'+extra).encode())
main=(ROOT/'runs/D150-main.rs').read_text(encoding='utf-8').replace('D150','D155').replace('d150','d155').replace('clobbered','candidate')
for mut in ['','mut ']:
    main=main.replace('b: &'+mut+'observed::GpuSolver','b: &'+mut+'baseline::GpuSolver').replace('g: &'+mut+'observed::GpuSolver','g: &'+mut+'candidate::GpuSolver')
main=main.replace('b = observed::GpuSolver::new','b = baseline::GpuSolver::new').replace('g = observed::GpuSolver::new','g = candidate::GpuSolver::new')
assert 'observed::' not in main
old='"AA,KK,QQ,JJ,TT,99,AKs,AQs,JTs,87s,AKo"'
new='"AA,KK,QQ,JJ,TT,99,88,77,66,55,44,33,22,AKs,AQs,AJs,ATs,A9s,A8s,A7s,A6s,A5s,A4s,A3s,A2s,AKo,AQo,AJo,ATo,KQs,KJs,KTs,QJs,QTs,JTs"'
assert main.count(old)==1;main=main.replace(old,new,1)
old='"AA,QQ,TT,77,55,AQs,KQs,QJs,98s,AQo"'
new='"AA,QQ,JJ,TT,99,88,77,66,55,44,33,22,AQs,AJs,ATs,A9s,A8s,A7s,A6s,A5s,A4s,A3s,A2s,KQs,KJs,KTs,K9s,QJs,QTs,Q9s,JTs,J9s,T9s,98s,AQo,AJo,KQo"'
assert main.count(old)==1;main=main.replace(old,new,1)
old='    assert_eq!(bi, gi);'
new='''    let mut normalized = gi.clone(); normalized["wrapper_bytes"] = bi["wrapper_bytes"].clone(); normalized["packet_module_loaded"] = bi["packet_module_loaded"].clone();
    assert_eq!(bi, normalized, "all geometry and graph presence");'''
assert main.count(old)==1;main=main.replace(old,new,1)
main=main.replace('"info": bi, "all65other_device_arrays_exact"','"baseline_info": bi, "candidate_info": gi, "all65other_device_arrays_exact"',1)
needle='records: &mut Vec<Value>) {\n    poison(g, out, id, stage, 1, epoch, witnesses);\n    b.sync_to_cpu(a).unwrap(); g.sync_to_cpu(c).unwrap();'
fixed='records: &mut Vec<Value>, readbacks: &mut Vec<Value>) {\n    poison(g, out, id, stage, 1, epoch, witnesses);\n    b.sync_to_cpu(a).unwrap(); readback(g,c,out,id,stage,false,readbacks);'
assert main.count(needle)==1;main=main.replace(needle,fixed,1)
main=main.replace('let mut witnesses = Vec::new();','''b.sync_strategy(&mut a).unwrap();g.d155_default_sync(&mut c,true);cpu_pair(&a,&c,&out,id,"default-strategy");
        b.sync_to_cpu(&mut a).unwrap();g.d155_default_sync(&mut c,false);cpu_pair(&a,&c,&out,id,"default-full");
        let mut readbacks=Vec::new();
        let mut witnesses = Vec::new();''',1)
main=main.replace('g.sync_strategy(&mut c).unwrap();','readback(&mut g,&mut c,&out,id,"strategy-sync",true,&mut readbacks);',1)
assert main.count('g.sync_to_cpu(&mut c).unwrap();')==2
main=main.replace('g.sync_to_cpu(&mut c).unwrap();','readback(&mut g,&mut c,&out,id,"prelock-full",false,&mut readbacks);',1)
main=main.replace('g.sync_to_cpu(&mut c).unwrap();','readback(&mut g,&mut c,&out,id,"continuation-final",false,&mut readbacks);',1)
lines=main.splitlines(True);changed=0
for i,line in enumerate(lines):
    if line.lstrip().startswith('full_sync(&mut b,'):
        assert '&mut records);' in line;lines[i]=line.replace('&mut records);','&mut records,&mut readbacks);');changed+=1
assert changed==3;main=''.join(lines)
main=main.replace('"constructor": bc,','"constructor": bc, "readbacks": readbacks, "default_public_fallbacks_silent": true,',1)
main=main.replace('"packing_implementation_created": false','"packing_implementation_created": true',1)
readback='''fn readback(g:&mut candidate::GpuSolver, c:&mut Solver,out:&Path,id:usize,stage:&str,strategy:bool,proofs:&mut Vec<Value>) {
    let before=out.join(format!("pinned-{id:02}-{stage}-before.u32"));let after=out.join(format!("pinned-{id:02}-{stage}-after.u32"));
    let proof=g.d155_forced_sync(c,strategy,&before,&after);proofs.push(json!({"stage":stage,"proof":proof}));
}
'''
capture=(ROOT/'runs/E090-engine-control/probe.rs').read_text(encoding='utf-8');helpers=capture[capture.index('pub trait Word'):capture.index('fn emit(')].replace('E090','D155')
prefix='''#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
use solver::store::{Store,Storage};
use cudarc::driver::{CudaContext,CudaSlice,CudaStream,DeviceRepr};
use serde_json::{json,Value};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::{Path,PathBuf},sync::Arc};
#[path="baseline/mod.rs"]mod baseline;
#[path="candidate/mod.rs"]mod candidate;
'''
(H/'probe.rs').write_bytes((prefix+helpers+readback+main).encode())
for name in ['audit','execute']:shutil.copyfile(ROOT/'runs'/f'D155-{name}.py',H/(name+'.py'))
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for crate,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',crate+'='+str(deps/file)]
cmd+=['-o',str(H/'probe.exe')]
h.save(H/'source-review.json',{'at':h.now(),'id':'D155','original_and_candidate_source_reverse_exact_after_plan_cfg_adapters':True,'device_field_inventory':[x[0] for x in invent],'candidate_manifest_sha256':h.sha(S/'manifest.json'),'matrix':'32 turn cases use broader asymmetric ranges to ensure current scratch/staging can exercise the exact internal path without changing candidate capacity. Four prior small flop/river cases retained. Both storages/algorithms/iso/fresh-warm dimensions unchanged; actual settings restored after load.','forced_controls':'Public calls keep fixed16MiB admission. Appended private observer calls exactly same try_packet_sync with min_bytes0, while retaining all capacity/format/bounds/architecture checks. Expected activation from fixture format/current lengths must match; no admission-width or production source change. Original public small/f32 fallback calls run before force and require no module retained.','raw_contract':'All66 constructor buffers, all65 other actual device arrays/host scalars, every CPU q/scale/query/save/resume word and subsequent logical CFV regeneration exact. Full physical CFV retained; arbitrary scratch differences only at readback. Full pinned before/after images retained; every word beyond checked65544word prefix remains exact on handled paths.','scope':'Finite direct engine controls and forced activation. No large primary workload, actual peak/capacity, driver errors or timing qualification.'})
npnative=list(Path(np.__file__).parent.rglob('*multiarray_umath*.pyd'));assert len(npnative)==1
files=[Path(__file__),ROOT/'runs/D155-candidate-control.rs',ROOT/'runs/D155-audit.py',ROOT/'runs/D155-execute.py',ROOT/'runs/D150-main.rs',ROOT/'runs/D150-observer-template.rs',parent,ROOT/'runs/E090-engine-control/probe.rs',S/'manifest.json',S/'source-review.json',ROOT/'runs/D154-packet-integration-units/report.json',ROOT/'epoch/common.py',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',Path(np.__file__)]+npnative+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
for n in ['audit','execute']:compile((H/(n+'.py')).read_text(encoding='utf-8'),n,'exec')
h.save(H/'protocol.json',{'id':'D155','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_ENGINE_CONTROLS','rustc_command':cmd,'cases':36,'clobbers':752,'phase_pairs':752,'constructor_pairs':36,'exploitability_pairs':324,'continuation_root_pairs':32,'forced_readbacks':188,'ordinary_public_decline_calls':72,'required_free_bytes':162*1024**3,'raw_reservation_bytes':96*1024**3,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'One Rust compiler, one fixed36case GPU engine process, then independent retained-word reader. Candidate production source/threshold/capacity/shader is frozen E092. Broader turn control ranges fixed before native work to exercise exact private path; four small extras and F32/original public declines preserved. No source/shape/case/gate/sample rescue after actual failure. Pre-native adapter or reader bookkeeping preserves all originals. No performance measurement or acceptance.'})
h.custody();print(h.sha(H/'protocol.json'),flush=True)
