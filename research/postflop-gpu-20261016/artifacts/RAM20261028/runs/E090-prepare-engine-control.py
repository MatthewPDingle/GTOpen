import sys,json,shutil,ast,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'epoch';sys.path.insert(0,str(E));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status())
assert h.read(h.ar.STATUS)['current_hardware_baseline']['correctness']=='pass'
assert shutil.disk_usage(ROOT).free>=74*1024**3
H=ROOT/'runs/E090-engine-control';H.mkdir(exist_ok=False)
A=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
reference=H/'reference';reference.mkdir()
for source,name in [(A/'runs/D134-zero-init-fences-r2/baseline/mod.rs','D134-observer-parent.rs'),(A/'runs/E087-transfer-control/probe.rs','E087-capture-parent.rs')]:
 q=reference/name;shutil.copyfile(source,q);h.pin(q,h.sha(source))
source=reference/'D134-observer-parent.rs';t=source.read_text(encoding='utf-8')
shim=t[t.index('pub mod plan {'):t.index('\nmod arena;')]
validator=t[t.index('impl GpuSolver {\n    pub fn d134_validate'):].replace('d134_validate','e090_validate').replace('D134','E090')
capture=(reference/'E087-capture-parent.rs').read_text(encoding='utf-8')
helpers=capture[capture.index('pub trait Word'):capture.index('fn emit(')]
cpu=capture[capture.index('fn host_field'):capture.index('fn device_frame')].replace('E087','E090')
prefix='''#![allow(dead_code,unused_imports,unused_mut)]
pub use solver::*;
use solver::store::{Store,Storage};
use cudarc::driver::{CudaContext,CudaSlice,CudaStream,DeviceRepr};
use serde_json::{json,Value};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::{Path,PathBuf},sync::Arc};
#[path="baseline/mod.rs"]mod baseline;
#[path="candidate/mod.rs"]mod candidate;
'''
(H/'probe.rs').write_bytes((prefix+helpers+cpu+(ROOT/'runs/E090-engine-main.rs').read_text(encoding='utf-8')).encode())
local=h.read(ROOT/'reference/localization.json');owned=local['owned_candidate_sources'];rel='crates/solver/src/gpu/mod.rs'
for arm,key in [('baseline','base'),('candidate','candidate')]:
 d=H/arm;d.mkdir()
 p=Path(owned[rel][key]);h.pin(p,h.custody()[rel]if key=='base'else local['candidate_owned_sha256'][rel])
 production=p.read_text(encoding='utf-8')
 assert production.count('pub mod plan;')==1 and production.count('plan.use_full_action_arenas(&solver.spot);')==1
 adapted=production.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1)
 assert adapted.replace(shim,'pub mod plan;',1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);',1)==production
 observer=(ROOT/'runs/E090-engine-observer.rs').read_text(encoding='utf-8')
 assert observer.count('E090_STRIDE')==1
 observer=observer.replace('E090_STRIDE','old_width'if arm=='baseline'else'logical')
 (d/'mod.rs').write_bytes((adapted+'\n'+validator+'\n'+observer).encode())
 for name in ['arena.rs','kernels.cu']:shutil.copyfile(h.REPO/'crates/solver/src/gpu'/name,d/name)
src=h.read(ROOT/'reference/E090-source/manifest.json')
h.save(H/'source-review.json',{'at':h.now(),'production_source_reverse_exact_after_public_plan_adapter':True,'candidate_source_sha256':src['candidate_owned_sha256'],'unchanged_kernel_sha256':h.sha(h.REPO/'crates/solver/src/gpu/kernels.cu'),'adapter':'Copied accepted exact private full-arena helper through public GpuPlan fields, in both standalone copies. Prefix reverses to original production text. Append full66-buffer constructor validator and read-only whole-state/CFV guard observers; only private force-sweep control poisons CFV and sets original discounts. No production source activation.','matrix':'32 cases:compressed/F32 x DCFR/CFR+ x both asymmetric range orientations x isooff/on x fresh/warmCPU. Rakeoff/on tied to fresh/warm dimension explicitly. Each arm:fullconstructor,both poisoned eager player sweeps,two graph iterations,eager/captured eval,query,strategy/full CPU sync,freeze lock/unlock graph recapture,save/load/warm GPU resume.','raw_contract':'Every full learning/reach/discount/weight/lock array and logical CFV row bitwise equal. Every complete physical CFV image retained. Under isolated poisoned sweep, every nonowned/padding word remains exact and every logical word replaces seed. Physical layouts may differ and are not claimed byte-identical. Constructor all66actual device fields compare to original CPU references; whole CPU/query/save images compare in full.','scope':'Finite declared matrix and actual arrays; no performance, physical peak, large capacity, actual paging or universal NaN proof. Kernel arithmetic/compiled source unchanged. Whole-solve and later broad/material qualification still required.'})
for name in ['audit.py','execute.py']:
 q=ROOT/'runs'/('E090-engine-'+name);assert q.exists(),q
 shutil.copyfile(q,H/name)
deps=ROOT/'reference/accepted-e080-deps'
cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for crate,filename in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',crate+'='+str(deps/filename)]
cmd+=['-o',str(H/'probe.exe')]
files=[p for p in H.rglob('*')if p.is_file()]+[Path(__file__),ROOT/'runs/E090-engine-observer.rs',ROOT/'runs/E090-engine-main.rs',ROOT/'reference/localization.json',ROOT/'reference/D141-cfv-width/report.json',E/'common.py',E/'accepted-source.json',E/'protected-main.json',ROOT/'comparisons/RAM20261028-baseline/report.json']+list(deps.iterdir())+list((ROOT/'reference/E090-source').iterdir())
h.save(H/'protocol.json',{'id':'E090-engine-control','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_GPU_CONTROLS','measurement_epoch':'RAM20261028','rustc_command':cmd,'input_sha256':{str(p):h.sha(p)for p in files if p.is_file()},'cases':32,'GPU_snapshot_pairs':288,'constructor_pairs':32,'exploitability_pairs':128,'standard_training_iterations':320,'extra_single_player_sweeps':128,'raw_reservation_bytes':8*1024**3,'required_free_bytes':74*1024**3,'scope':'One Rust compiler and one GPU control process, then independent retained-raw reader. All output on X, old source inputs copied and checksum bound on X. No shader/source/width/case/gate variants or GPU extensions after actual failure; reader-only bookkeeping may replay unchanged retained observations. No performance samples or production source activation.','candidate_accepted':False})
pub=[]
for p in [H/'protocol.json',H/'source-review.json']:
 key='E090-engine-control/'+p.name;dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(p,dest)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
 pub.append(key)
h.save(H/'publication.json',{'at':h.now(),'HTTP_verified_artifacts':pub,'GPU_control_executions':0,'protocol_sha256':h.sha(H/'protocol.json')})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E090')
 x.update(status='running',stage='Real GPU engine state and scratch guards',reason='Frozen 32-case engine comparison: full learning/reach state, translated logical CFV rows, untouched physical guards, eager/graphs/evaluation/locks/save/resume. No speed result.')
 x['evidence'].append({'label':'Frozen full engine controls on X','url':'evidence/E090-engine-control/protocol.json'})
 s.update(updated_at=h.now(),state='running',active_experiment='E090',stage='E090 real GPU engine controls',activity='Compare the unchanged two-statement CFV stride candidate with accepted E080 across 32 fixed cases. Fresh RAM baseline is 10.4564 s. Accuracy and speed of E090 remain unproven.')
 h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(h.sha(H/'protocol.json'),flush=True)
