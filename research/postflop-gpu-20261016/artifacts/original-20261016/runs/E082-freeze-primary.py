"""Seal exactly three same-quality complete-solve pairs against accepted E080."""
from pathlib import Path
import ast,json,re,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018';sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
build=R/'runs/E082-final-build/complete.json';done=old.read(build);assert done['all_compilers_terminal']and done['native_executions']==0
for p,h in done['evidence_sha256'].items():old.pin(p,h)
x=old.read(R/'runs/E082-build-manager/build.exit.json');assert x['returncode']==0 and x['error']is x['cleanup']is None
direct=R/'comparisons/E082-kernel-control-root-check/report.json';control=old.read(direct);assert control['status']=='pass_scoped_full_prefix_consumer_raw_equivalence'and control['whole_physical_outputs_bitwise_equal']and control['all21_input_buffers_identical']and control['kernel_launches']==3640
S=R/'runs/E082-source';source=old.read(S/'manifest.json');H=R/'runs/E082-primary-plan';assert not H.exists();H.mkdir()
for name in['native.py','assess.py','root-check.py','run.py']:
    code=(R/'runs/E080-primary-plan'/name).read_text().replace('E080','E082').replace('e080','e082').replace('exact two-source scope','exact one-source scope').replace("accepted-E051-live-20261018","accepted-E080-live-20261018").replace('import common_e051_live as old','import common_e080_live as old')
    if name in['native.py','assess.py']:
        predicate="assert control['status']=='pass_scoped_full_prefix_consumer_raw_equivalence' and control['whole_physical_outputs_bitwise_equal'] and control['all21_input_buffers_identical'] and control['kernel_launches']==3640 and control['source_main_live_PTX_custody_pass']"
        code,n=re.subn(r"assert control\['admit_one_integrated_trial'\][^\n]+",predicate,code);assert n==1
    ast.parse(code);(H/name).write_text(code,encoding='utf-8',newline='\n')
P=old.read(R/'runs/E080-primary-plan/protocol.json');base=C/'baseline.json';bexe=R/'binaries/E080-postflop_autoresearch.exe';bmp=bexe.with_suffix('.manifest.json');bm=old.read(bmp);old.pin(bexe,bm['binary_sha256']);assert bm['source_sha256']==old.BASE
P.update(id='E082-primary',at=old.now(),baseline={'path':str(base),'sha256':old.sha(base)},baseline_binary={'path':str(bexe),'sha256':old.sha(bexe),'manifest':str(bmp),'manifest_sha256':old.sha(bmp)},candidate_owned_sha256=source['candidate_owned_sha256'],build_protocol_sha256=old.sha(R/'runs/E082-build-plan/build-protocol.json'),ordinary_unit_id='V082-unit',control_ids=['V082-unit'],pairs=[{'baseline':'B275','candidate':'E082R1'},{'baseline':'B276','candidate':'E082R2'},{'baseline':'B277','candidate':'E082R3'}],measurement_order=['B275','E082R1','E082R2','B276','B277','E082R3'],direct_control_report={'path':str(direct),'sha256':old.sha(direct)},source_scope=source['scope']+' All1820 raw GPU case pairs passed with identical physical outputs and all21actual input images. Source/ABI/other8kernels unchanged, resources equal. Complete clocks still include tree/CPU allocation, all GPU initialization/NVRTC/JIT, fixed-quality solve/checks/full readback; no isolated timings pooled. Initial screen alone cannot qualify adoption.')
paths=[Path(__file__),build,direct,R/'runs/E082-resource/protocol.json',R/'runs/E082-resource/report.json',R/'runs/E082-kernel-control/protocol.json',R/'runs/E082-kernel-control/execution/complete.json',R/'runs/E082-build-plan/build-protocol.json',*[p for p in S.iterdir()if p.is_file()],base,bexe,bmp,C/'common_e080_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[H/n for n in['native.py','assess.py','root-check.py','run.py']]]
for stem in['E082-feature-solver','E082-solver','E082-postflop_autoresearch']:
    exe=R/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=old.read(mp);old.pin(exe,m['binary_sha256']);assert m['source_sha256']==old.BASE|P['candidate_owned_sha256'];paths.extend([exe,mp])
st=old.read(old.ar.STATUS)
for identity in P['control_ids']+P['measurement_order']:assert not(R/'runs'/identity).exists()and not any(x['id']==identity for x in st['experiments'])
for identity in['E082-native-execution','E082-primary-wrapper','E082-primary-manager']:assert not(R/'runs'/identity).exists()
for identity in['E082-three-pair-comparison','E082-root-crosscheck']:assert not(R/'comparisons'/identity).exists()
P['input_sha256']={str(p):old.sha(p)for p in paths};old.save(H/'protocol.json',P)
pub=[]
for p in H.iterdir():
    if not p.is_file():continue
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
    pub.append(key)
old.save(H/'pre-timing-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_verified_artifacts':pub,'native_primary_or_ordinary_unit_executions':0,'all_compilers_terminal':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    st=old.read(old.ar.STATUS);e=next(x for x in st['experiments']if x['id']=='E082');e.update(stage='86 ordinary tests and three full-solve pairs',reason='Fresh builds are terminal and E080 source is restored. Run86ordinary tests, then exactly B275/E082R1, E082R2/B276, B277/E082R3. Same unrounded1%cutoff and strict fixture guards; no additional samples or adoption from this initial screen.');e['evidence'].append({'label':'Frozen complete-solve screen','url':'evidence/E082-primary-plan/protocol.json'});st.update(updated_at=old.now(),stage='E082 complete-solve comparison',activity='Run the fixed complete-solve screen after direct accuracy and resource checks passed. All setup, quality checks and full readback remain included. E080 remains deployed at14.74% cumulative gain.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(old.sha(H/'protocol.json'),flush=True)
