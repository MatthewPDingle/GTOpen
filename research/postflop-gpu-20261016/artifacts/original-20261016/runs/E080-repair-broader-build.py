"""Freeze an observer-only repair, reusing all five terminal compiler outputs."""
from pathlib import Path
import ast,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());H=R/'runs/E080-broader-build-plan';P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
receipt=old.read(R/'runs/E080-broader-build-manager/build.exit.json');assert receipt['returncode']==1 and receipt['error']is receipt['cleanup']is None
assert not Path(P['feature']['target']).exists();assert not(H/'protocol-r2.json').exists();ast.parse((H/'build-r2.py').read_text(encoding='utf-8'))
completed={};extra=[Path(__file__),H/'build-r2.py',H/'protocol.json',old.REPO/'crates/solver/src/preflop/kernels.cu']
for row in P['arms']['baseline']['standalone'][:5]:
    d=R/'runs/E080-broader-build'/('baseline-'+row['test_target']);e=old.read(d/'rustc.exit.json');assert e['returncode']==0 and e['error']is e['cleanup']is None and old.read(d/'rustc.invocation.json')['command']==row['command'];binary=Path(row['binary'])
    completed['baseline-'+row['test_target']]={'binary_sha256':old.sha(binary),'receipt':str(d/'rustc.exit.json'),'invocation':str(d/'rustc.invocation.json'),'stdout':str(d/'rustc.stdout.log'),'stderr':str(d/'rustc.stderr.log')};extra.extend([binary,*[p for p in d.iterdir()if p.is_file()]])
    if binary.with_suffix('.manifest.json').exists():extra.append(binary.with_suffix('.manifest.json'))
extra.extend(p for p in(R/'runs/E080-broader-build-manager').iterdir()if p.is_file())
P.update(id='E080-broader-build-r2',at=old.now(),repair_scope='Observer-only: preflop_gpu dead-strips unreferenced postflop code, so require its actual preflop CUDA source. All other harnesses retain the postflop source assertion. Reuse all five successful compiler outputs and prior four immutable manifests. No source, fixture, flags, correctness or timing changes; zero native solver observations so far.',original_protocol_sha256=old.sha(H/'protocol.json'),completed_compilers=completed)
P['input_sha256']=P['input_sha256']|{str(p):old.sha(p)for p in extra};old.save(H/'protocol-r2.json',P)
for p in[Path(__file__),H/'build-r2.py',H/'protocol-r2.json']:
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
old.save(H/'r2-pre-build-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol-r2.json'),'HTTP_byte_verified':True,'compiled_outputs_reused':5,'native_solver_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E080');e.update(stage='Broader builds; target-specific observer repaired',reason='Five baseline compilers succeeded. The original verifier wrongly required postflop CUDA text in the standalone preflop binary, where the linker omits unused postflop code. Preserve the failure and reuse all five binaries. Check preflop CUDA for that target; keep the original postflop check elsewhere. No solver observations or candidate-source changes.');e['evidence'].append({'label':'Observer repair and reused compiler evidence','url':'evidence/E080-broader-build-plan/protocol-r2.json'});s.update(updated_at=old.now(),stage='E080 broader build observer repair',activity='Reuse all completed compiler outputs and continue the remaining unchanged builds. No native solver tests have run; accepted and live E051 are unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
M=R/'runs/E080-broader-build-manager-r2';assert not M.exists();M.mkdir();print('E080 broader build r2 protocol',old.sha(H/'protocol-r2.json'),flush=True);old.child([sys.executable,'-B',str(H/'build-r2.py'),old.sha(H/'protocol-r2.json')],M,'build',old.env(),3900);old.custody();print('E080 broader builds terminal.',flush=True)
