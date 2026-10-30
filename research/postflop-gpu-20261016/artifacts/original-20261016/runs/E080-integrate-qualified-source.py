"""Integrate only the exact two qualified files; preserve all earlier epochs."""
from pathlib import Path
import json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');A0=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(A0));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
Q=R/'comparisons/E080-final-qualification-r3';q=old.read(Q/'report.json');assert q['status']=='pass_ready_for_exact_source_integration'and q['checks_passed']==23 and all(x['passed']for x in q['checks'])
for p,h in q['evidence_sha256'].items():old.pin(p,h)
for label in['build-unit','responsiveness']:v=old.read(R/'runs/E080-server-manager'/(label+'.exit.json'));assert v['returncode']==0 and v['error']is v['cleanup']is None
S=old.read(R/'runs/E080-source/manifest.json');newbase=old.BASE|S['candidate_owned_sha256'];assert q['source_sha256']==newbase
I=R/'runs/E080-source-integration';A=R/'runs/accepted-E080';MAIN=Path(r'X:\Dev\GTOpen');assert not I.exists()and not A.exists();I.mkdir();roots={'research':old.REPO,'main':MAIN};heads_before={};state={}
for name,root in roots.items():
    heads_before[name]=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip();state[name]=subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no'],cwd=root,text=True)
    for n in S['owned']:
        old.pin(root/n,old.BASE[n]);assert not subprocess.check_output(['git','diff','--cached','--name-only','--',n],cwd=root,text=True).strip();assert not subprocess.check_output(['git','diff','--name-only','--',n],cwd=root,text=True).strip()
old.save(I/'pre-integration.json',{'at':old.now(),'qualification_sha256':old.sha(Q/'report.json'),'integrator_sha256':old.sha(__file__),'heads_before':heads_before,'tracked_worktree_status':state,'only_intended_files':list(S['owned']),'candidate_source_sha256':newbase,'live_deployed':False})
with old.ar.exclusive_lock(R/'gpu-run.lock'):
    old.custody();old.ar.refuse_active(old.ar.live_status())
    for name,root in roots.items():
        for n,x in S['owned'].items():
            old.pin(root/n,old.BASE[n]);old.pin(x['candidate'],S['candidate_owned_sha256'][n]);shutil.copyfile(root/n,I/(name+'-'+Path(n).name+'.before'));shutil.copyfile(x['candidate'],root/n);old.pin(root/n,S['candidate_owned_sha256'][n])
        cmd=['git','-c','core.whitespace=cr-at-eol','diff','--check','--',*S['owned']];result=subprocess.run(cmd,cwd=root,text=True,capture_output=True);assert result.returncode==0,(name,result.stdout,result.stderr)
        cmd=['git','-c','core.autocrlf=false','commit','--only','-m','perf: overlap postflop zero validation with GPU setup','--',*S['owned']];result=subprocess.run(cmd,cwd=root,text=True,capture_output=True);old.save(I/(name+'-commit.json'),{'at':old.now(),'command':cmd,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr});assert result.returncode==0,(name,result.stdout,result.stderr)
    heads={name:subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()for name,root in roots.items()};assert old.ar.source_identity()['source_sha256']==newbase
    for name,root in roots.items():
        changed=subprocess.check_output(['git','diff','--name-only',heads_before[name],heads[name]],cwd=root,text=True).splitlines();assert set(changed)==set(S['owned']);assert subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no'],cwd=root,text=True)==state[name]
    A.mkdir();old.save(A/'baseline.json',{'at':old.now(),'candidate':'E080','source_sha256':newbase,'primary_binary':str(R/'binaries/E080-postflop_autoresearch.exe'),'primary_manifest':str(R/'binaries/E080-postflop_autoresearch.manifest.json'),'qualification_pre_sha256':old.sha(Q/'report.json')})
    protected=old.read(A0/'protected-main.json');protected['git_head']=heads['main'];protected['source_sha256'].update(S['candidate_owned_sha256']);old.save(A/'protected-main.json',protected);shutil.copyfile(A0/'preexisting-target-artifacts.json',A/'preexisting-target-artifacts.json')
    helper=(A0/'common_e051_live.py').read_text().replace('Accepted E051 source epoch after the explicitly recorded live deployment.','Accepted E080 source epoch; E051 executable remains live until separate maintenance.').replace("ROOT/'runs/accepted-E051'));import common_e051 as previous","ROOT/'runs/accepted-E051-live-20261018'));import common_e051_live as previous")
    assert 'import common_e051_live as previous'in helper;(A/'common_e080.py').write_text(helper,encoding='utf-8',newline='\n');sys.path.insert(0,str(A));import common_e080 as current;current.custody()
    integration={'at':old.now(),'status':'exact_qualified_host_source_integrated','heads_before':heads_before,'heads_after':heads,'source_sha256':newbase,'only_production_files_changed':list(S['owned']),'qualification_sha256':old.sha(Q/'report.json'),'server_binary_sha256':old.sha(R/'binaries/E080-gto-server.exe'),'live_deployed':False,'new_custody_epoch':str(A),'old_epochs_preserved':True,'no_native_or_performance_reruns':True};old.save(I/'report.json',integration)
    accepted=dict(q);accepted.update(at=old.now(),status='accepted_source_integrated',source_integrated=True,live_deployed=False,new_epoch=str(A),heads=heads,integration_sha256=old.sha(I/'report.json'));old.save(Q/'accepted.json',accepted)
cum=old.read(R/'comparisons/E080-remaining-native/cumulative.json');links=[{'label':'E080 final qualification and preserved failure scope','url':'evidence/'+Q.name+'/accepted.json'},{'label':'E080 application responsiveness','url':'evidence/E080-server-controls/responsiveness-report.json'},{'label':'E080 source integration','url':'evidence/'+I.name+'/report.json'}]
published=[]
for folder in[Q,I,A,R/'runs/E080-server-controls',R/'runs/E080-server-manager',R/'runs/E080-qualification-manager',R/'comparisons/E080-final-qualification',R/'comparisons/E080-final-qualification-r2']:
    for p in folder.rglob('*'):
        if not p.is_file()or p.suffix not in['.py','.json','.log']or'__pycache__'in p.parts:continue
        key=folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(exist_ok=True,parents=True)
        if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
        else:shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=30)as response:assert response.read()==p.read_bytes()
        published.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);s.setdefault('accepted_complete_run_history',[]).append(s['accepted_complete_run']);s['accepted_complete_run']={'status':'validated','scope':'complete_run','candidate_id':'E080','baseline_ms':cum['baseline_full_cycle_ms'],'best_ms':cum['candidate_full_cycle_ms'],'observed_gain_pct':cum['observed_gain_pct'],'correctness':'pass','measured_at':cum['at'],'method':q['scope']};s['baseline'].update(id='B272 / B273 / B274',measured_at=cum['at'],full_cycle_definition=q['scope']);s['validation']={'status':'pass','candidate_id':'E080','summary':'E080 passed the registered primary, fresh16, exactness, capacity, CPU/memory, graph/resource, holdout and application checks. All16 confirmation pairs improved. 86 solver and20 server tests passed. Existing experimental symmetry trajectories remain failed identically in both versions and are not cleared.'};s['evidence'].extend(links)
    for fixture in s['fixtures']:
        f=next(x for x in cum['fixtures']if x['fixture_id']==fixture['id']);fixture['baseline'].update(full_cycle_ms=f['baseline']['full_cycle_ms']['median_ms'],solve_ms=f['baseline']['solve_ms']['median_ms']);fixture['best'].update(status='accepted',candidate_id='E080',full_cycle_ms=f['candidate']['full_cycle_ms']['median_ms'],solve_ms=f['candidate']['solve_ms']['median_ms'],median_regression_pct=-f['observed_gain_pct'],guard_passed=True);fixture['evidence'].extend(links[:2])
    e=next(x for x in s['experiments']if x['id']=='E080');e.update(status='accepted',accepted=True,stage='Qualified source integrated; deploying server next',correctness='pass',reason='Fresh16 confirms 1.7148% incremental improvement; fresh original cumulative is14.7414%. All registered material and production compatibility checks passed. Known experimental symmetry and original combined observer calibration remain failed. Exact two host files committed; E051 is still live until maintenance completes.');e['evidence'].extend(links);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E080',stage='Deploying qualified E080 server',activity='Exact E080 source is integrated. Registered cumulative benchmark gain is14.74%; E051 remains the live executable until the separately guarded routine restart. No accuracy, storage or kernel changes.');old.ar.atomic_json(old.ar.STATUS,s)
old.save(I/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':published,'source_custody_pass':True,'live_still_E051':True,'no_push':True});current.custody();print(json.dumps({'status':'accepted_source_integrated','heads':heads,'cumulative_gain_pct':cum['observed_gain_pct'],'live_deployed':False,'HTTP_files':len(published)}),flush=True)
