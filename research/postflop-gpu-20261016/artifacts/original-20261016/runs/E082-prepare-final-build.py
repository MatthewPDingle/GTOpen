"""Freeze fresh full builds after all declared direct GPU pairs passed."""
from pathlib import Path
import ast,json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018';sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
S=R/'runs/E082-source';D=R/'runs/E082-kernel-control';root=R/'comparisons/E082-kernel-control-root-check';q=old.read(root/'report.json');assert q['status']=='pass_scoped_full_prefix_consumer_raw_equivalence'and q['whole_physical_outputs_bitwise_equal']and q['all21_input_buffers_identical']and q['kernel_launches']==3640
for name in['direct','raw-replay']:
    x=old.read(R/'runs/E082-direct-manager'/(name+'.exit.json'));assert x['returncode']==0 and x['error']is x['cleanup']is None
H=R/'runs/E082-build-plan';assert not H.exists();H.mkdir();source=old.read(S/'manifest.json')
code=(R/'runs/E080-build-plan/build.py').read_text().replace('E080','E082').replace('e080','e082').replace('two-file build','one-file build').replace("HERE.parent/'accepted-E051-live-20261018'","HERE.parent/'accepted-E080-live-20261018'").replace('import common_e051_live as old','import common_e080_live as old');ast.parse(code);assert 'import common_e080_live as old'in code;(H/'build.py').write_text(code,encoding='utf-8',newline='\n')
owned={}
for n,v in source['owned'].items():
    old.pin(v['base'],old.BASE[n]);old.pin(v['candidate'],source['candidate_owned_sha256'][n]);owned[n]={'base':v['base'],'base_sha256':old.BASE[n],'candidate':v['candidate'],'candidate_sha256':source['candidate_owned_sha256'][n]}
assert set(owned)=={'crates/solver/src/gpu/kernels.cu'}
P=old.read(R/'runs/E080-build-plan/build-protocol.json');P.update(id='E082-final-build',at=old.now(),accepted_source_sha256=old.BASE,protected_main=str(C/'protected-main.json'),owned=owned,CUDA_source_unchanged=False,native_before_builds_terminal=True)
for key in list(P):
    if key.startswith('component_'):del P[key]
for phase in P['phases']:
    phase['target']=str(R/('build-e082-final-'+phase['id']));phase['outputs']={k:v.replace('E080','E082')for k,v in phase['outputs'].items()};assert not Path(phase['target']).exists()
P.update(source_scope=source['scope']+' Resource screen passed with unchanged38registers/local0/static1040/worst dynamic22600/maxthreads1024/residency. All1820 direct GPU pairs across five widths and full actual inputs/guards passed. Fresh feature and primary builds must restore E080 CUDA after each phase. Ordinary solver units remain86with4ignored. No full-solve or material qualification yet.',direct_pairs=1820,direct_launches=3640,expected_ordinary_units=86,ignored_ordinary_units=4)
paths=[Path(__file__),H/'build.py',R/'runs/D133-prepare-prefix-consumers.py',R/'runs/E082-prepare-direct.py',*[p for folder in[S,D,R/'runs/E082-resource',R/'runs/D133-readonly-prefix-consumers']for p in folder.iterdir()if p.is_file()and p.suffix in['.json','.py','.rs','.cu','.patch','.ptx']],root/'report.json',D/'execution/complete.json',C/'common_e080_live.py',C/'protected-main.json',C/'preexisting-target-artifacts.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md'];P['input_sha256']={str(p):old.sha(p)for p in paths};old.save(H/'build-protocol.json',P)
pub=[]
for folder in[D,R/'runs/E082-direct-manager',root,H]:
    for p in folder.rglob('*'):
        if not p.is_file()or p.suffix not in['.json','.jsonl','.py','.rs','.cu','.log','.patch']or'__pycache__'in p.parts or p.name=='raw-results.jsonl':continue
        key=folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert dst.read_bytes()==p.read_bytes()
        else:shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:assert response.read()==p.read_bytes()
        pub.append(key)
old.save(H/'pre-build-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'build-protocol.json'),'HTTP_verified_artifacts':pub,'raw194MB_remains_on_S_with_sha256':q['raw_sha256'],'integrated_compiler_or_solver_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    st=old.read(old.ar.STATUS);e=next(x for x in st['experiments']if x['id']=='E082');e.update(stage='Fresh full solver builds',correctness='direct_controls_pass',reason='All1820 direct GPU pairs passed, including417280nonfinite output words, complete output/guard images and all21actual inputs. Independent reader passed105571checks. Compile fresh full feature and primary binaries next; speed remains unknown.');e['evidence'].extend([{'label':'Full raw GPU control replay','url':'evidence/'+root.name+'/report.json'},{'label':'Fresh integrated build protocol','url':'evidence/'+H.name+'/build-protocol.json'}]);st.update(updated_at=old.now(),stage='Building E082 complete-solve trial',activity='Raw showdown controls passed. Build the exact single CUDA change in two isolated targets, restoring accepted E080 after each build. Fixed complete-solve timing and quality gates come next.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(old.sha(H/'build-protocol.json'),flush=True)
