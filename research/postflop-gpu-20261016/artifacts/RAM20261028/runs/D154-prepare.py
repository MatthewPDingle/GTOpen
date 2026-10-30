import sys,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
S=ROOT/'runs/E092-source';M=h.read(S/'manifest.json')
for p,d in M['owned_source_sha256'].items():h.pin(p,d)
for name,d in M['candidate_source_sha256'].items():h.pin(S/'candidate'/name,d)
H=ROOT/'runs/D154-packet-integration-units';H.mkdir(exist_ok=False)
gpu=H/'gpu';shutil.copytree(S/'candidate',gpu)
parent=ROOT/'runs/E090-engine-control/reference/D134-observer-parent.rs';text=parent.read_text(encoding='utf-8');shim=text[text.index('pub mod plan {'):text.index('\nmod arena;')]
source=(gpu/'mod.rs').read_text(encoding='utf-8')
adapted=source.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1)
assert adapted.replace(shim,'pub mod plan;',1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);',1)==source
(gpu/'mod.rs').write_bytes(adapted.encode())
unit=ROOT/'runs/D154-unit-tests.rs';q=gpu/'packet_readback.rs';original=q.read_text(encoding='utf-8');q.write_bytes((original+'\n'+unit.read_text(encoding='utf-8')).encode())
(H/'probe.rs').write_bytes(b'#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]\npub use solver::*;\n#[path="gpu/mod.rs"]mod observed;\n')
shutil.copyfile(ROOT/'runs/D154-execute.py',H/'execute.py')
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','--test','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for crate,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',crate+'='+str(deps/file)]
cmd+=['-o',str(H/'probe.exe')]
count=sum((gpu/name).read_text(encoding='utf-8').count('#[test]') for name in ['mod.rs','arena.rs','packet_readback.rs'])
files=[Path(__file__),ROOT/'runs/D154-execute.py',unit,parent,S/'manifest.json',S/'source-review.json',ROOT/'epoch/common.py',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json']+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
compile((ROOT/'runs/D154-execute.py').read_text(encoding='utf-8'),'D154-execute.py','exec')
h.save(H/'protocol.json',{'id':'D154','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_UNITS','rustc_command':cmd,'expected_test_count':count,'required_free_bytes':66*1024**3,'candidate_manifest_sha256':h.sha(S/'manifest.json'),'input_sha256':{str(p):h.sha(p) for p in files},'scope':'One Rust compiler and one serial unit/GPU test process for original candidate GPU/arena tests plus three unsafe-layout/scatter/pinned guard controls appended only under cfgtest. Exact standalone private-plan shim reverses to candidate text; production source remains frozen. No source/numerical/threshold/gate rescue after actual failure. Mechanical pre-native adapters or retained-reader bookkeeping preserve originals. No complete-cycle timing or candidate acceptance.'})
h.custody();print(h.sha(H/'protocol.json'),flush=True)
