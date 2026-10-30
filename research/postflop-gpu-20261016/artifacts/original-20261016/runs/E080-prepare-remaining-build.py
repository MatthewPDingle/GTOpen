"""Freeze capacity and unchanged holdout candidate builds; reuse accepted baselines."""
from pathlib import Path
import ast,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
H=R/'runs/E080-remaining-build-plan';assert H.exists()and not(H/'protocol.json').exists();ast.parse((H/'build.py').read_text(encoding='utf-8'))
previous=old.read(R/'runs/E051-remaining-build-plan-r3/protocol.json');capacity=Path(previous['capacity_source']);holdout=Path(previous['holdout_source']);assert capacity.is_file()and holdout.is_file()
for src,dest in[(capacity,H/'capacity.rs'),(holdout,H/'evaluator.rs'),(holdout.parent/'fixture.json',H/'fixture.json')]:assert not dest.exists();shutil.copyfile(src,dest);assert src.read_bytes()==dest.read_bytes()
source=old.read(R/'runs/E080-source/manifest.json');rows=[];paths=[Path(__file__),H/'build.py',H/'capacity.rs',H/'evaluator.rs',H/'fixture.json',capacity,holdout,holdout.parent/'fixture.json',R/'runs/E080-broader-observation-closure/root-audit.json',R/'runs/E080-broader-observation-closure/desktop-feature-scope.json',R/'comparisons/E080-broader-observations/report.json',R/'comparisons/E080-broader-observations/known-symmetry-failure.json',R/'comparisons/E080-large-warm-controls/report.json',R/'comparisons/E080-fresh16-confirmation/report.json',R/'comparisons/E080-fresh16-root-check/report.json',R/'runs/E080-source/manifest.json',C/'common_e051_live.py',C/'protected-main.json']
for kind,stem,src in[('capacity','E080-broader-continuation_paging',H/'capacity.rs'),('holdout','E080-postflop_autoresearch',H/'evaluator.rs')]:
    mp=R/'binaries'/(stem+'.manifest.json');m=old.read(mp);assert m['source_sha256']==old.BASE|source['candidate_owned_sha256'];deps=m['dependency_artifact_sha256'];libs={}
    for name in['solver','serde_json','cudarc']:
        found=[p for p in deps if Path(p).suffix=='.rlib'and(Path(p).name.startswith('lib'+name+'-')or Path(p).name=='lib'+name+'.rlib')];assert len(found)==1,(name,found);libs[name]=found[0]
    for p,h in deps.items():old.pin(p,h)
    binary=R/'binaries'/('E080-'+kind+'-candidate.exe');cmd=['rustc','--edition=2021',str(src),'--crate-name','e080_'+kind+'_candidate','-C','opt-level=3','-C','lto=thin','-C','codegen-units=1']
    if kind=='holdout':cmd+=['--test','--cfg','feature="gpu"']
    for name,p in libs.items():cmd+=['--extern',name+'='+p]
    cmd+=['-L','dependency='+str(Path(libs['serde_json']).parent),'-o',str(binary)]
    rows.append({'id':kind,'source':str(src),'binary':str(binary),'command':cmd,'dependencies':deps,'solver_library_sha256':old.sha(libs['solver'])});paths.extend([mp,R/'binaries'/(stem+'.exe')])
baseline={}
for kind,stem in[('capacity','E051-capacity-candidate'),('holdout','E051-holdout-candidate')]:
    binary=R/'binaries'/(stem+'.exe');mp=binary.with_suffix('.manifest.json');m=old.read(mp);assert m['source_sha256']==old.BASE;old.pin(binary,m['binary_sha256']);baseline[kind]={'path':str(binary),'sha256':old.sha(binary),'manifest':str(mp),'manifest_sha256':old.sha(mp)};paths.extend([binary,mp])
P={'id':'E080-capacity-holdout-build','at':old.now(),'status':'FROZEN_PRE_COMPILER','candidate_owned_sha256':source['candidate_owned_sha256'],'compilers':rows,'accepted_baseline_binaries':baseline,'input_sha256':{str(p):old.sha(p)for p in paths},'source_activation':False,'native_before_all_compilers_terminal':False,'scope':'Two standalone candidate evaluators using exact existing sources, fixed fixture and frozen E080 libraries. Accepted E051 baseline evaluators reused after full hash/source verification. No new solver code, flags, scenario, stopping rules or performance samples. The known failed experimental research gate remains failed and visible; not cleared by these builds. Native capacity/holdout/cumulative protocol will be frozen separately.'}
for row in rows:P['input_sha256'].update(row['dependencies'])
old.save(H/'protocol.json',P)
for p in[Path(__file__),*[p for p in H.iterdir()if p.is_file()]]:
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
old.save(H/'pre-build-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_byte_verified':True,'compiler_or_native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E080');e.update(status='running',accepted=False,stage='Capacity and fixed holdout evaluator builds',reason='Build only the missing candidate capacity and fixed wide-turn evaluators against frozen libraries. Accepted baseline binaries are source/hash verified and reused. No new solver source, benchmark samples or research-equivalence clearance.');e['evidence'].append({'label':'Frozen capacity and holdout build protocol','url':'evidence/E080-remaining-build-plan/protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E080',stage='E080 capacity and holdout evaluator builds',activity='Compile the existing fixed evaluators without solver source activation. Keep all previous timing and known research failures intact. Accepted and live E051 remain unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
M=R/'runs/E080-remaining-build-manager';assert not M.exists();M.mkdir();print('E080 remaining build protocol',old.sha(H/'protocol.json'),flush=True);old.child([sys.executable,'-B',str(H/'build.py'),old.sha(H/'protocol.json')],M,'build',old.env(),1500);old.custody();print('E080 remaining builds terminal.',flush=True)
