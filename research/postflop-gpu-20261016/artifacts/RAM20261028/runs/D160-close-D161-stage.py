import sys,json,shutil,subprocess,statistics,urllib.request,zipfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D160-arena-lifecycle';P=h.read(H/'protocol.json');R=h.read(ROOT/'comparisons/D160-arena-lifecycle/report.json')
for path,digest in P['input_sha256'].items():h.pin(path,digest)
assert h.read(H/'execution/complete.json')['all_owned_children_terminal']
N=ROOT/'runs/D160-outcome-checkpoint';N.mkdir(exist_ok=False)
def floor_sum(n,m,a,b):
    total=0
    while True:
        if a>=m:total+=(n-1)*n*(a//m)//2;a%=m
        if b>=m:total+=n*(b//m);b%=m
        y=a*n+b
        if y<m:return total
        n=y//m;b=y%m;m,a=a,m
def modsum(n,m,b):return 17*n*(n-1)//2+b*n-m*floor_sum(n,m,17,b)
checks=0;rows={};resources={}
for item in P['sequence']:
    ident=item['id'];assert h.read(H/'execution'/(ident+'.exit.json'))['returncode']==0
    raw=(H/'execution'/(ident+'.stdout.log')).read_text(encoding='utf-8')
    rows[ident]=[json.loads(x.split('D160_ARENA ',1)[1]) for x in raw.splitlines() if x.startswith('D160_ARENA ')]
    assert rows[ident]==R['all_native_component_rows'][ident]
    for row in rows[ident]:
        lengths=[row['q_entries'][0],row['q_entries'][1]]*2
        for ri,sums in enumerate(row['checksums'],1):
            for ai,pair in enumerate(sums):
                assert pair[0]==modsum(lengths[ai],65536,ri*13+ai*2*19)
                n=row['scale_entries'];assert pair[1]==0x3f000000*n+modsum(n,8388608,ri*13+(ai*2+1)*19)
                checks+=2
        assert row['VM_allocations']==row['VM_releases']==(4 if item['arm']=='candidate' and row['fixture']!='river' else 0)
    resource=h.read(H/'execution'/(ident+'.resource.json'));resources[ident]=resource;t=resource['terminal_process_times']
    assert t['CPU_ms']==(t['kernel_100ns']+t['user_100ns'])/10000
    assert t['lifetime_ms']==(t['exit_FILETIME']-t['creation_FILETIME'])/10000
bm=cm=0;guards=[]
for index,f in enumerate(P['fixture_order']):
    b=[rows['B'+str(i)][index]['complete_ns']/1e6 for i in [1,2,3]];c=[rows['C'+str(i)][index]['complete_ns']/1e6 for i in [1,2,3]]
    bm+=statistics.median(b);cm+=statistics.median(c);guards.append(statistics.median(c)>statistics.median(b) and sum(v>u for u,v in zip(b,c))>=2)
assert bm-cm==R['component_saving_ms'] and all(guards) and bm-cm<P['minimum_component_saving_ms']
assert R['status']=='declined_component_lifecycle_or_resources'
h.save(N/'report.json',{'at':h.now(),'status':'pass_retained_component_replay','D160_remains_declined':True,'native_processes':6,'fixture_component_records':18,'independent_closed_form_checksums':checks,'all_VM_allocations_released':True,'component_difference_ms':bm-cm,'all_three_strict_fixture_guards_failed':True,'original_terminal_process_times_recomputed':True,'report_sha256':h.sha(ROOT/'comparisons/D160-arena-lifecycle/report.json'),'scope':'Retained integer-sum oracle recomputed independently by Euclidean floor-sum from every length/round/arena index,not just B/C checksum agreement. Full every-element zero and pattern assertions are source-bound successful native checks; full raw component arrays were not persisted. No rerun or relabel. No GPU/solver or speed qualification.'})
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';old=ledger.read_bytes();marker='### D160 large numeric allocation lifecycle declined; D161 toolchain scout'
assert marker.encode() not in old
entry=f'''

{marker}

D160 fixed CPU-only allocation lifecycle protocol {h.sha(H/'protocol.json')} compares actual accepted ArenaBuf/mimalloc against ordinary Win32 VirtualAlloc only for >=64MiB q arrays. Scale/small/river allocations keep original constructor; no new production code. D107already proved zeroed allocation/no separate memset; D138VirtualAlloc was sampler validation only. Current exact canonical CPU lengths/order feed full scale-positive-zero checks/q OR, two dense16thread pattern writes with serial every-element bit validation, then full freeing. All phases included; no apparent allocation-only win. No large pages,MEM_RESET,prefetch,zero-scan omission,privilege/global setting or closed ownership/transport variant.

One compiler,six fixed B1/C1/C2/B2/B3/C3 fresh processes terminal0.18fixture records exact,all24actual VM allocations/releases match. Independent retained replay verifies288expected q/scale sums using closed-form modular sums and original terminal CPU/lifetime arithmetic. Full individual-word validation is bound native assertions;raw component arrays were not persisted. Sum fixture lifecycle medians2030.8548ms baseline versus2132.567ms candidate,difference {bm-cm}ms (slower),below prospectively fixed104.564109ms effort proxy. All3strict fixture slowdown guards fail. Whole-process lifetime median+1.859118048732178% fails<=1% limit;CPU+0.20703933747412417% passes;reported memory peaks slightly lower. This is a component/resource rejection,not a full-solve measurement. Close backend form without threshold,touch/schedule,fixture,source or sample rescue. No E093 created or gain adopted.

Next D161 is a distinct postflop compiler-version scout. Existing CUDA uses process-local main-source PTX compilation with actual device arch and default math flags. Bounded history has no CUDA13/NVRTC13 compiler-upgrade trial; the no-effect extra-device-vectorization option stays closed. Pinned NVIDIA-owned NVRTC13.0.88 Windows wheel will be fetched/checksummed into isolated X research storage only. No global toolchain/driver/PATH replacement,preflop compiler change or production activation. Exact target-only source/flags and same compilation-in-clock policy required. Primary NVIDIA13.0.1 docs support Windows NVRTC and CUDA13 family R580+ compatibility,but current610.88 PTX load must still be proven; documentation establishes no speed/accuracy gain.

Before any new compiler execution freeze explicit DLL/header/API/version identities,original12.9 control,source-target inventories,math flags,ABI/caller-default/resource feasibility and emitted-code mechanism criteria. Existing12.9fallback for other targets remains exact. If code genuinely changes,full raw exact arithmetic/engine/lifecycle controls precede fresh unchanged complete-cycle>=1%/strict fixture/fresh16/broad/material/holdout/fresh-original qualification. No blanket alternate-version or source/flag tuning after failed frozen form. Package retrieval is preparation,not compiler or optimizer acceptance.

All artifacts on X,archive read-only,no T access. E080 current-RAM10.4564109s baseline unchanged;historical14.7414% remains separate. Accepted162/main/live/protectedPTX custody passes,all owned native children terminal,locks absent. No push or server replacement;goal active.
'''
nl=b'\r\n' if b'\r\n' in old else b'\n';ledger.write_bytes(old+entry.encode().replace(b'\n',nl))
subprocess.run(['git','-c','gc.auto=0','commit','--only','-m','research: reject inclusive arena backend and stage compiler-version scout','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
D=ROOT/'runs/D161-toolchain-scout';D.mkdir(exist_ok=False);shutil.copyfile(ledger,D/'history-at-freeze.txt')
api='https://pypi.org/pypi/nvidia-cuda-nvrtc/13.0.88/json'
metadata=urllib.request.urlopen(api,timeout=30).read();(D/'pypi-13.0.88.json').write_bytes(metadata);data=json.loads(metadata)
files=[x for x in data['urls'] if x['filename'].endswith('win_amd64.whl')];assert len(files)==1
file=files[0];assert file['size']==76807835 and file['digests']['sha256']=='6bcd4e7f8e205cbe644f5a98f2f799bef9556fefc89dd786e79a16312ce49872'
assert file['url'].startswith('https://files.pythonhosted.org/') and data['info']['name']=='nvidia-cuda-nvrtc' and data['info']['version']=='13.0.88'
assert shutil.disk_usage(ROOT).free>=8*1024**3
h.save(D/'retrieval-protocol.json',{'at':h.now(),'status':'FROZEN_PRE_WHEEL_RETRIEVAL','source':api,'metadata_sha256':h.sha(D/'pypi-13.0.88.json'),'wheel_filename':file['filename'],'wheel_URL':file['url'],'wheel_bytes':file['size'],'wheel_sha256':file['digests']['sha256'],'output_root':str(D),'extract_only':['nvidia/cuda_nvrtc/bin/nvrtc64_130_0.dll','nvidia/cuda_nvrtc/bin/nvrtc-builtins64_130.dll','nvidia/cuda_nvrtc/include/nvrtc.h'],'scope':'Download/extract official pinned artifacts only. No pip install,global setting,driver/compiler replacement,DLL load,native compile,GPU context/kernel or solver execution. Read package metadata/license as data,never instructions.'})
wheel=D/file['filename'];started=time.monotonic();last=started;received=0
with urllib.request.urlopen(file['url'],timeout=30) as response,wheel.open('xb') as out:
    while True:
        chunk=response.read(1024*1024)
        if not chunk:break
        out.write(chunk);received+=len(chunk)
        if time.monotonic()-last>=20:print('D161 package retrieval',received,'bytes',flush=True);last=time.monotonic()
assert wheel.stat().st_size==file['size'];h.pin(wheel,file['digests']['sha256'])
extracted={}
with zipfile.ZipFile(wheel) as archive:
    expected=h.read(D/'retrieval-protocol.json')['extract_only']
    for name in expected:
        assert name in archive.namelist(),name
        dest=D/'toolchain'/name;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();dest.write_bytes(archive.read(name));extracted[str(dest)]={'bytes':dest.stat().st_size,'sha256':h.sha(dest)}
baseline=h.ar.NVRTC
h.save(D/'toolchain-files.json',{'at':h.now(),'wheel_sha256':h.sha(wheel),'candidate_files':extracted,'baseline_DLLs':{str(p):{'bytes':p.stat().st_size,'sha256':h.sha(p)} for p in baseline.glob('*.dll')},'compile_options_source':str(Path(r'C:\Users\there\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\cudarc-0.19.7\src\nvrtc\safe.rs')),'new_DLL_loads_or_compiler_runs':0})
h.save(D/'scope-review.json',{'id':'D161','at':h.now(),'status':'official_toolchain_artifacts_staged_compiler_protocol_next','candidate_version':'13.0.88','candidate_wheel_sha256':h.sha(wheel),'history_sha256':h.sha(D/'history-at-freeze.txt'),'accepted_CUDA_sha256':h.sha(h.REPO/'crates/solver/src/gpu/kernels.cu'),'accepted_host_compilation_source_sha256':h.sha(h.REPO/'crates/solver/src/gpu/mod.rs'),'scope':'Same exact accepted main CUDA source,no new compiler flags,arithmetic,precision,launches or global/preflop toolchain change. Candidate private13runtime compilation only oncc12.0; other targets retain exact original12.9 compiler. Need actual baseline version/API and compile options before a frozen no-kernel mechanism/resource probe. Runtime compilation/DLL/JIT/load costs remain inside qualification clock.','primary_sources':['https://pypi.org/project/nvidia-cuda-nvrtc/13.0.88/','https://docs.nvidia.com/cuda/archive/13.0.1/nvrtc/index.html','https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html'],'obligations':['Verify exact native ABI/nvrtcVersion and Create/Compile/log/PTX/Destroy lifecycle;load only private absolute DLLs with scoped dependency directory. No alias renaming or global PATH replacement.','Source-bound literal default CompileOptions only gpu-architecture plus existing kernel name,default math preserved;validate control PTX matches retained accepted PTX before attributing candidate changes.','Freeze kernel/parameter inventories,actual supported launch shape/default stack/heap/shared/local/max-thread gates and emitted-code mechanism before compilation. Whole PTX version/header difference alone is not a useful codegen mechanism. No kernel launch before resources/caller/ABI pass.','If compiler passes,use full signed-zero/nonfinite/locks/arbitrarymenu/disjointarena/rawdevice/CPU EV/stop/save/resume/continuation controls,both algorithms,F32/compressed,and original reference;never infer exactness from compilation.','Only then fresh complete-cycle screen plus independent fresh16,broad/capacity/material/holdout/fresh-original gates. Resource warnings alone follow D108policy,but actual hard failures close the form.','No new optimizer/E093,application activation,source flag rescue or performance gain at preparation stage.'],'new_compiler_runs':0,'GPU_or_solver_runs':0,'all_new_output_X':True})
pub=[]
for folder,names in [(N,['report.json']),(D,['retrieval-protocol.json','toolchain-files.json','scope-review.json'])]:
    for name in names:
        path=folder/name;key=folder.name+'/'+name;dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert dest.read_bytes()==path.read_bytes()
        else:shutil.copyfile(path,dest)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==path.read_bytes()
        pub.append(key)
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D160')
    item.setdefault('evidence',[]).append({'label':'Independent retained arithmetic replay','url':'evidence/D160-outcome-checkpoint/report.json'})
    status['experiments'].append({'id':'D161','title':'Postflop NVRTC13 compiler-version scout','kind':'diagnostic','status':'staged','accepted':False,'correctness':'not_executed','measurement_epoch':'RAM20261028','stage':'Pinned isolated official toolchain;freeze actual API/resource protocol next','reason':'NVIDIA13.0.88 Windows wheel checksum-verified on X;two DLLs/header extracted privately. No install,global/preflop compiler change,DLL load,compiler or GPU run. Same accepted CUDA source/default math/clock scope required. All numerical/full-cycle/material qualification remains.','evidence':[{'label':'Toolchain/source obligations','url':'evidence/D161-toolchain-scout/scope-review.json'},{'label':'Exact private package/DLL identities','url':'evidence/D161-toolchain-scout/toolchain-files.json'}]})
    status.update(updated_at=h.now(),active_experiment='D161',stage='Compiler-version scout',activity='Current-RAM E080 baseline10.4564s remains best. E092 rejected process-lifetime regression;D159flag no code change;D160inclusive allocation lifecycle slower. Isolated NVIDIA13 toolchain prepared for source-bound compiler/resource controls;no new gain claimed.')
    h.ar.atomic_json(h.ar.STATUS,status)
h.custody();assert not (ROOT/'gpu-run.lock').exists() and not (ROOT/'epoch-sequence.lock').exists()
h.save(N/'terminal-checkpoint.json',{'at':h.now(),'research_git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip(),'D160_closed':True,'D161_prepared_no_native_run':True,'HTTP_verified_artifacts':pub,'current_E080_baseline_ms':10456.4109,'all_owned_research_children_terminal':True,'research_locks_absent':True,'accepted_main_live_PTX_custody_pass':True,'all_new_outputs_X':True,'X_free_bytes':shutil.disk_usage(ROOT).free,'new_gain_accepted':False,'goal_status':'active'})
print(json.dumps({'D160':'declined_and_replayed','independent_checksums':checks,'D161':'private_pinned_toolchain_staged','package_bytes':received,'HTTP_artifacts':len(pub),'all_children_terminal':True}),flush=True)
