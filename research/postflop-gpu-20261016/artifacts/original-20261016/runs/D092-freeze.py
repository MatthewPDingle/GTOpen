"""Seal and publish the CPU-only control package before compilation."""
import json, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();H=ROOT/'runs/D092-action-arity-order'
assert not (H/'protocol.json').exists() and not (ROOT/'gpu-run.lock').exists()
assert not (H/'build').exists() and not (H/'execution').exists()
old.ar.refuse_active(old.ar.live_status())
deps=ROOT/'build-e051-final-primary/release/deps'
cmd=['rustc','--edition=2021',str(H/'probe.rs'),'--crate-name','d092_probe','-C','opt-level=3','-C','lto=thin','-C','codegen-units=1']
for name in ['solver','serde','serde_json','rayon']:
    paths=list(deps.glob(f'lib{name}-*.rlib'));assert len(paths)==1,(name,paths)
    cmd+=['--extern',f'{name}={paths[0]}']
cmd+=['-L','dependency='+str(deps),'-o',str(H/'build/probe.exe')]
prior=old.read(ROOT/'runs/D090-wide-OR/protocol.json')['input_sha256']
inputs={p:h for p,h in prior.items() if Path(p).parent==deps}
for p in H.iterdir():
    if p.is_file():inputs[str(p)]=old.sha(p)
for p in [Path(__file__),ROOT/'runs/D092-prepare.py',ROOT/'runs/E005.patch',ROOT/'runs/E014-source/plan.rs',ROOT/'runs/accepted-E051/common_e051.py',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']:
    inputs[str(p)]=old.sha(p)
P={'id':'D092-action-arity-order','at':old.now(),'status':'FROZEN_PRE_COMPILE_NATIVE','cases':list(range(12)),'command':cmd,'input_sha256':inputs,'source_sha256':old.BASE,'candidate_plan_sha256':old.sha(H/'candidate-plan.rs'),'accepted_plan_sha256':old.sha(H/'accepted-plan.rs'),'compiler_version':subprocess.check_output(['rustc','--version','--verbose'],text=True),'disk_free_bytes':shutil.disk_usage(ROOT).free,'maximum_additional_disk_reservation_bytes':32*1024**3,'required_remaining_reserve_bytes':50*1024**3,'production_source_activated':False,'gpu_executions':0,'full_cycle_performance_measured':False,'acceptance_rule':'CPU-only exact metadata/ownership admission. Timings diagnostic. No solver source adoption. Any later full candidate must pass the current 1% no-tradeoffs qualification policy.'}
assert P['disk_free_bytes']>=82*1024**3
old.save(H/'protocol.json',P)
published=[]
for p in sorted(H.iterdir()):
    if not p.is_file():continue
    rel='evidence/D092-action-arity-order/'+p.name;dest=old.ar.DASHBOARD/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert dest.read_bytes()==p.read_bytes()
    else:shutil.copyfile(p,dest)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+rel,timeout=10) as response:
        assert response.read()==p.read_bytes()
    published.append({'file':str(p),'url':rel,'sha256':old.sha(p)})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);assert s['research_policy']['minimum_aggregate_gain_pct']==1
    assert not any(r['id']=='D092' for r in s['experiments'])
    s.update(updated_at=old.now(),state='running',stage='CPU controls for action-node ordering',active_experiment='D092',activity='The 1% no-tradeoffs policy is active. D092 will compare all GPU-plan fields and prove same-level address independence before any GPU candidate. No gain claimed.')
    s['experiments'].append({'id':'D092','at':old.now(),'title':'Group existing action work lists by arity','kind':'diagnostic','status':'running','scope':'CPU metadata and ownership only','fixture':'Three primary configurations; iso off/on, compact/full arenas','stage':'Frozen before CPU compilation and native execution','correctness':'pending','reason':'Ordering-only decomposition of prior direct-kernel composites; unchanged CUDA, dispatch, spans, child order and buffers. CPU controls first; no complete-cycle gain or adoption.','evidence':[{'label':'Frozen 12-case CPU control protocol','url':'evidence/D092-action-arity-order/protocol.json'},{'label':'Source/history and dependency review','url':'evidence/D092-action-arity-order/proposal.json'},{'label':'Exact intended source change','url':'evidence/D092-action-arity-order/candidate.patch'}]})
    old.ar.atomic_json(old.ar.STATUS,s)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'published':published,'http_bytes_verified':True,'native_executions':0})
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'http_verified_artifacts':len(published),'cases':12,'fields':53,'source_activated':False}),flush=True)
