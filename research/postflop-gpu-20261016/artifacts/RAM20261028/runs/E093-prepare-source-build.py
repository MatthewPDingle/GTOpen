import sys,json,shutil,ast,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
BASE=h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
proof=ROOT/'comparisons/D167-runtime-compiler-control/report.json';r=h.read(proof);assert r['status']=='pass_scoped_runtime_compiler_exact_PTX_and_fallbacks'
S=ROOT/'runs/E093-source';S.mkdir(exist_ok=False);(S/'base').mkdir();(S/'candidate').mkdir()
owned={};changed={};basefiles=['Cargo.lock','crates/solver/Cargo.toml','crates/solver/src/gpu/mod.rs'];reversals={}
for name in basefiles:
    original=(h.REPO/name).read_bytes();base=S/'base'/name;candidate=S/'candidate'/name;base.parent.mkdir(parents=True,exist_ok=True);candidate.parent.mkdir(parents=True,exist_ok=True);base.write_bytes(original)
    text=original.decode('utf-8');nl='\r\n' if '\r\n' in text else '\n';text=text.replace('\r\n','\n')
    if name=='Cargo.lock':
        needle='name = "solver"\nversion = "0.1.0"\ndependencies = [\n "cudarc",\n'
        replacement=needle+' "libloading",\n';assert text.count(needle)==1;text=text.replace(needle,replacement,1);reverse=text.replace(replacement,needle,1)
    elif name.endswith('Cargo.toml'):
        needle='mimalloc = "0.1"\n';replacement=needle+'libloading = { version = "0.9", optional = true }\n';assert text.count(needle)==1;text=text.replace(needle,replacement,1)
        a='gpu = ["dep:cudarc"]';b='gpu = ["dep:cudarc", "dep:libloading"]';assert text.count(a)==1;text=text.replace(a,b,1);reverse=text.replace(replacement,needle,1).replace(b,a,1)
    else:
        needle='mod arena;\n';replacement=needle+'#[cfg(all(target_os = "windows", target_pointer_width = "64"))]\nmod nvrtc13;\n';assert text.count(needle)==1;text=text.replace(needle,replacement,1)
        a='            .get_or_init(|| {\n';b=a+'                #[cfg(all(target_os = "windows", target_pointer_width = "64"))]\n                if let Some(ptx) = nvrtc13::try_compile(arch, include_str!("kernels.cu")) {\n                    return Ok(ptx);\n                }\n';assert text.count(a)==1;text=text.replace(a,b,1);reverse=text.replace(replacement,needle,1).replace(b,a,1)
    assert reverse.replace('\n',nl).encode()==original;candidate.write_bytes(text.replace('\n',nl).encode());changed[name]=h.sha(candidate);reversals[name]=True
    owned[name]={'base':str(base),'base_sha256':BASE[name],'candidate':str(candidate),'candidate_sha256':changed[name]}
new='crates/solver/src/gpu/nvrtc13.rs';target=S/'candidate'/new;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'runs/D167-runtime-compiler-control/nvrtc13.rs',target);assert not(h.REPO/new).exists();changed[new]=h.sha(target)
owned[new]={'base':None,'base_sha256':None,'candidate':str(target),'candidate_sha256':changed[new]}
parsed=tomllib.loads((S/'candidate/crates/solver/Cargo.toml').read_text(encoding='utf-8'));assert parsed['features']['gpu']==['dep:cudarc','dep:libloading']
lock=tomllib.loads((S/'candidate/Cargo.lock').read_text(encoding='utf-8'));solver=next(x for x in lock['package'] if x['name']=='solver');assert 'libloading' in solver['dependencies'];assert next(x for x in lock['package'] if x['name']=='libloading')['version']=='0.9.0'
h.save(S/'source-review.json',{'at':h.now(),'id':'E093','status':'isolated_source_frozen_not_activated','design_sha256':h.sha(ROOT/'runs/D167-runtime-compiler-contract/design-review.json'),'runtime_component_report_sha256':h.sha(proof),'exact_tracked_source_reversal':reversals,'new_module_sha256_matches_actual_tested_wrapper':h.sha(target)==r['new_runtime_module_sha256'],'scope':'Exactly3existingfiles+1newprivate module. Addoptionalalreadylocked libloading0.9 dependency/edge,gpu-only Windows64module and optionalchoice insideoriginalPTXOnceLockclosure. CUDA source/arena/plan/tree/precision/launches/budget/graph/readback/quality/preflop source unchanged. No publicsolverfield. Same arch/cacheclone,lifetime;allunavailable/unsupported/error declines fallthroughoriginal compiler. Allnewloader/program/close/JIT costs stayinside GPUinit,wholeprocess/resourcegates later.','preflop_and_other_targets':'No preflop source/compiler/PATH change. Windows64 compute120 driver>=13000 privateoptional path only;otherplatforms/arch/missingprivate ornewcompilererror retain original existing call. Newdependencyoptional tiedgpu,already presenttransitively. Integrationruntime/backend/units/broadfallback controls remainrequired.','real_costs':'AdditionaloptionalWindows vendorpackage ~186MB DLL/header artifacts on disk;package notinstalledmain. Newfilesystem/path/driverAPIchecks,DLLload/pathverification/CString/PTXcopy/compile/destruction code mustbe measured,notassumedfree. Component observed no residual13DLLloaded aftersuccess/error;notuniversalpeak/capacity proof.','qualification':'No sourceactivation orspeed sampleyet. Twofresh offline/locked featureandprimarybuilds,restoreallacceptedfiles/removeonlyournewfile aftereach. Thennewordinaryunits/actualbackend/engine checks andfixed>=1%/strictfixture initial3pairs,fresh16,broad/material/capacity/holdout/freshoriginal/serverqualification. No source/flags/version/shape/sample rescue afteractualfailure.'})
h.save(S/'manifest.json',{'id':'E093','at':h.now(),'accepted_source_sha256':BASE,'candidate_owned_sha256':changed,'owned':owned,'new_owned_paths':[new],'tracked_owned_paths':basefiles,'owned_artifact_sha256':{str(p):h.sha(p) for p in S.rglob('*') if p.is_file()},'candidate_accepted':False})
H=ROOT/'runs/E093-build-plan';H.mkdir(exist_ok=False);script=ROOT/'runs/E093-build.py';assert not script.exists();shutil.copyfile(ROOT/'runs/E093-build-template.py',script);ast.parse(script.read_text(encoding='utf-8'))
phases=h.read(ROOT/'runs/E091-build-plan/protocol.json')['phases']
for phase in phases:
    phase['target']=str(ROOT/('build-e093-final-'+phase['id']));phase['outputs']={k:v.replace('E091','E093') for k,v in phase['outputs'].items()}
files=[Path(__file__),ROOT/'runs/E093-build-template.py',script,S/'manifest.json',S/'source-review.json',proof,ROOT/'comparisons/D166-canonical-compiler-control/report.json',ROOT/'runs/D167-runtime-compiler-contract/design-review.json',ROOT/'epoch/common.py',h.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']+[p for p in S.rglob('*') if p.is_file()]
h.save(H/'protocol.json',{'id':'E093-final-build','at':h.now(),'status':'FROZEN_PRE_INTEGRATED_CARGO_COMPILERS','accepted_source_sha256':BASE,'candidate_owned_sha256':changed,'owned':owned,'new_owned_paths':[new],'tracked_owned_paths':basefiles,'phases':phases,'required_free_bytes':80*1024**3,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'Onefrozen optionalpostflopruntime13wrapper insideoriginalcache. Twofresh feature/primary offline lockedCargo builds,restore3tracked files andremoveonlyverifiednewmodule aftereach. No tests/native solves/timing,globalinstall/server/preflop activation oradoption.'})
# Publish concrete source and build protocol before activation.
import urllib.request
for folder,names in [(S,['manifest.json','source-review.json']),(H,['protocol.json'])]:
    for name in names:
        p=folder/name;dest=h.ar.DASHBOARD/'evidence'/folder.name/name;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(p,dest)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);assert not any(x['id']=='E093' for x in status['experiments'])
    status['experiments'].append({'id':'E093','title':'Optional postflop runtime CUDA13 compiler','kind':'optimization','status':'staged','accepted':False,'correctness':'runtime_component_and_sealed_PTX_controls_pass_integration_pending','measurement_epoch':'RAM20261028','stage':'Frozenisolated source;freshfeature/primary builds next','reason':'Originallarge canonical allCPU/66GPUrawstate exact andactualruntimewrapper emitssealedPTX. OptionalWindows64/compute120/driver13privatepath,originalcompilerfallback,unchangedPTXcache/math/launches. Allreal loader/compile/closecosts inbenchmark. No speed result orappinstall/adoption.','evidence':[{'label':'Exact isolated source contract','url':'evidence/E093-source/source-review.json'},{'label':'Frozen fresh builds','url':'evidence/E093-build-plan/protocol.json'}]})
    status.update(updated_at=h.now(),active_experiment='E093',stage='Fresh integrated runtime compiler builds',activity='Fullraw canonicalandactual runtimeAPI controls passed. Buildoptionalpostflop-only13compiler withcostsinsiderealclocks,restoreacceptedsourceaftereach. No speedupaccepted;E080live.')
    h.ar.atomic_json(h.ar.STATUS,status)
h.custody();print(h.sha(H/'protocol.json'),flush=True)
