"""Freeze ordinary activity and compiled-resource equivalence; no speed scoring."""
from pathlib import Path
import ast,json,sys,urllib.request,shutil
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert not(H/'protocol.json').exists()
D=R/'runs/D087-cupti-driver-profile';base=old.read(D/'diagnostic-build/postflop-trace.manifest.json')
assert base['source_sha256']==old.BASE
P0=old.read(D/'cohort-plan.json');M=old.read(R/'binaries/E080-postflop_autoresearch.manifest.json');S=old.read(R/'runs/E080-source/manifest.json')
assert M['source_sha256']==old.BASE|S['candidate_owned_sha256']
deps=M['dependency_artifact_sha256'];libs={}
for name in ['solver','cudarc','serde_json']:
    x=[p for p in deps if Path(p).suffix=='.rlib'and Path(p).name.startswith('lib'+name+'-')];assert len(x)==1;libs[name]=x[0]
for p,h in deps.items():old.pin(p,h)
commands=[]
for label,source,test in [('candidate-trace',D/'evaluator.rs',True),('compiled-resources',H/'resources.rs',False)]:
    cmd=['rustc','--edition=2021']+(['--test','--cfg','feature="gpu"']if test else[])+[str(source),'--crate-name','e080_'+label.replace('-','_'),'-C','opt-level=3','-C','lto=thin','-C','codegen-units=1']
    for n,p in libs.items():cmd+=['--extern',n+'='+p]
    cmd+=['-L','dependency='+str(Path(libs['solver']).parent),'-L','native='+str(D/'build'),'-o',str(H/'build'/(label+'.exe'))]
    commands.append({'id':label,'command':cmd,'path':str(H/'build'/(label+'.exe'))})
cuda=old.REPO/'crates/solver/src/gpu/kernels.cu'
assert cuda.read_bytes()==(R/'runs/E051-resource/candidate.cu').read_bytes()
for name in ['accepted.cu','candidate.cu']:
    assert not(H/name).exists();shutil.copyfile(cuda,H/name)
paths=[p for p in H.iterdir()if p.is_file()]+[D/'evaluator.rs',D/'collector.cpp',D/'diagnostic-build/postflop-trace.exe',D/'diagnostic-build/postflop-trace.manifest.json',D/'build/D087Collector.dll',D/'build/D087Collector.lib',Path(P0['driver_cbid_header']),R/'binaries/E080-postflop_autoresearch.manifest.json',R/'runs/E080-source/manifest.json',R/'runs/E080-resource-controls/report.json',R/'runs/E080-resource-controls/root-report.json',R/'runs/E020C1/stdout.log',R/'runs/E051-resource/candidate.cu',R/'runs/E051-resource/report.json']
for p in H.glob('*.py'):ast.parse(p.read_text())
P={'id':'E080-graph-and-compiled-resource-controls','at':old.now(),'status':'FROZEN_PRE_COMPILER_AND_NATIVE','commands':commands,'input_sha256':{str(p):old.sha(p)for p in paths}|deps,'baseline_binary':str(D/'diagnostic-build/postflop-trace.exe'),'source_sha256':{'baseline':old.BASE,'candidate':M['source_sha256']},'private_dll_dirs':P0['private_dll_dirs'],'driver_cbid_header':P0['driver_cbid_header'],'order':['baseline','candidate'],'quality':'Exactly one fresh ordinary CUPTI activity process per arm, largest registered rainbow compressed fixture, same D087 lifetime-safe evaluator; full non-timing state and ten checkpoints exact E020C1, stop200. No errors/drops/bad timestamps/outstanding buffers. Every kernel joins its launch API. All graph-node descriptor multisets, per-node repeats, kernel register/static/dynamic shared/launch geometry counts and driver API call/return counts exactly equal after ignoring process-specific graph/context/stream/correlation IDs. Expected graph repeats9/199/199 and407successful graph launches. No timing score or causal headroom inference.','compiled_resources':'One private probe compiles identical accepted/E080 CUDA bytes with the original default CompileOptions and actual compute_120, loads all nine functions, queries registers/local/static-shared/maxthreads and occupancy64/128/256. Both complete PTX bytes and all resources equal. Cross-check actual launched trace register/static-shared fields against driver attributes. Private PTX outputs stay in this new folder. Protected historical PTX untouched.','policy':'Fixed two trace processes, one compiler/resource probe process. No exclusions, extensions, hardware counters, source/thread/threshold/helper/flag variants or retries after actual failure. This is count/resource equivalence only, not a timing observation or observer overhead claim. Original experimental symmetry and combined calibration gates remain failed. Candidate not adopted.','candidate_accepted':False}
old.save(H/'protocol.json',P)
for p in H.iterdir():
    if not p.is_file():continue
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);s.update(updated_at=old.now(),stage='E080 compiled resources and graph audit',activity='Compare actual ordinary GPU activity, graph replays and compiled function resources for the unchanged E080 candidate. No new performance score; E051 remains live.');old.ar.atomic_json(old.ar.STATUS,s)
print(old.sha(H/'protocol.json'),flush=True)
