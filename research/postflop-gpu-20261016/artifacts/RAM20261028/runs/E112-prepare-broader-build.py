"""Freeze matched, unchanged broader Cargo harnesses after fresh timing passes."""
import ast,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
assert shutil.disk_usage(ROOT).free>=160*1024**3
Q=ROOT/'comparisons/E112-fresh16-confirmation/report.json';A=ROOT/'comparisons/E112-fresh16-root-check/report.json';assert h.read(Q)['performance']['fresh_confirmation_pass']and h.read(A)['status']=='pass_timing_only'
assert h.read(ROOT/'runs/E112-confirmation-wrapper/complete.json')['all_owned_children_terminal']
H=ROOT/'runs/E112-broader-build-plan';H.mkdir(exist_ok=False);original=h.read(ROOT/'runs/E112-build-plan/protocol.json')
tests=['postflop_state_perf','postflop_action_menus','postflop_resume_state','gpu','preflop_gpu','continuation_paging','continuation_symmetry']
P={'id':'E112-broader-build','at':h.now(),'status':'FROZEN_PRE_COMPILER','accepted_source_sha256':original['accepted_source_sha256'],'candidate_owned_sha256':original['candidate_owned_sha256'],'owned':original['owned'],'tracked_owned_paths':original['tracked_owned_paths'],'new_owned_paths':original['new_owned_paths'],'required_free_bytes':160*1024**3,'tests':tests,'arms':{},'native_executions':0,'candidate_accepted':False,'scope':'Two matched fresh Cargo compilations of unchanged tracked state/menu/resume/postflopGPU/preflopGPU and experimental paging/symmetry harnesses plus stored-state unit harness. Compile only. Existing experimental changing-range symmetry gate remains failed and will be observed without altering thresholds; only paired parity can be assessed. No new primary samples, no quality/source/flag variants. Material costs/holdout/cumulative/temporary app remain required.'}
paths=[Path(__file__),ROOT/'runs/E112-broader-build.py',ROOT/'epoch/common.py',ROOT/'epoch/runner.py',Q,A,ROOT/'runs/E112-confirmation-checkpoint/report.json',ROOT/'runs/E112-build-plan/protocol.json',h.REPO/'crates/solver/src/lib.rs',h.REPO/'crates/solver/src/preflop/gpu/kernels.cu',h.REPO/'crates/solver/Cargo.toml',h.REPO/'research/preflop-evolution/symmetric-bridge-20260919/DIAGNOSTICS.md']
for n in tests:paths.append(h.REPO/'crates/solver/tests'/(n+'.rs'))
for d in P['owned'].values():paths.extend([Path(d['base']),Path(d['candidate'])])
for arm in ['baseline','candidate']:
 target=ROOT/('build-e112-broader-'+arm);outputs={n:'E112-broader-'+arm+'-'+n for n in ['solver']+tests};cmd=['cargo','test','--release','--locked','--offline','--target-dir',str(target),'-p','solver','--features','preflop-research','--lib']
 for n in tests:cmd+=['--test',n]
 cmd+=['--no-run','--message-format=json'];assert not target.exists()
 for stem in outputs.values():assert not(ROOT/'binaries'/(stem+'.exe')).exists()and not(ROOT/'binaries'/(stem+'.manifest.json')).exists()
 P['arms'][arm]={'command':cmd,'target':str(target),'outputs':outputs,'expected_features':['gpu','preflop-research'],'io_root':str(ROOT/'runs/E112-broader-scratch'/arm)}
P['input_sha256']={str(p):h.sha(p)for p in paths};h.save(H/'protocol.json',P)
for p in [H/'protocol.json',Path(__file__),ROOT/'runs/E112-broader-build.py']:
 key=H.name+'/'+p.name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as z:assert z.read()==p.read_bytes()
h.save(H/'publication.json',{'at':h.now(),'protocol_sha256':h.sha(H/'protocol.json'),'HTTP_byte_verified':True,'new_broader_native_executions':0})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E112');e.update(status='running',accepted=False,stage='Matched broader compatibility builds',reason='Fresh16 timing passed. Build unchanged matched state/menu/resume/GPU and experimental continuation controls. Material, holdout, cumulative and temporary app qualification remain. E080 remains live.');e['evidence'].append({'label':'Frozen broader build protocol','url':'evidence/'+H.name+'/protocol.json'});s.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E112',stage='Constant discounts: broader compatibility builds',activity=e['reason']);h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(h.sha(H/'protocol.json'),flush=True)
