import sys,json,shutil,subprocess,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();H=R/'runs/E080-reboot-recovery-20261019';assert H.is_dir()
m=old.read(C/'protected-main.json');main=Path(m['root']);exe=Path(m['live_path']);old.pin(exe,m['live_sha256'])
inventory=lambda:[{'path':str(p.relative_to(main/'saves')),'bytes':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns}for p in sorted((main/'saves').rglob('*'))if p.is_file()]
before=old.read(H/'saves-before.json');assert inventory()==before
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.custody();old.child(['powershell.exe','-NoProfile','-File',str(H/'restart-r2.ps1')],H,'restart-r2',old.env(),90)
 old.custody();after=inventory();assert after==before
 snap=old.ar.live_status();old.ar.refuse_active(snap)
 old.save(H/'live-after.json',snap);old.save(H/'saves-after.json',after)
 ui=old.read(R/'runs/E080-live-deployment/UI-after.json')
 for path,expected in ui.items():
  with urllib.request.urlopen(old.ar.LIVE+path,timeout=20)as z:assert z.status==expected['status']and z.read().decode('utf-8')==expected['body']
 native=json.loads((H/'native-after.json').read_text(encoding='utf-8-sig'))
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=20)
 assert gpu['returncode']==0 and'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee'in gpu['stdout']
 old.save(H/'report.json',{'at':old.now(),'status':'pass_verified_reboot_recovery','native':native,'saved_file_inventory_unchanged':True,'saved_files':len(before),'served_root_and_preflop_JS_exact':True,'accepted_source_main_live_PTX_custody_pass':True,'source_or_binary_replaced':False,'solver_performance_samples':0,'GPU_identity_after_reboot':gpu,'scope':'Restored exact previously qualified E080 app after verified OS reboot. No active process was stopped. Last verified sessions were empty; saved files remain available and no arbitrary save was loaded. Previous performance measurements remain historical observations; no new gain or cold-cache claim.'})
pub=[]
for p in H.iterdir():
 if not p.is_file()or p.suffix not in ['.json','.ps1','.log']:continue
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
 pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);s['deployment']['live_pid']=native['pid'];s['deployment']['last_recovered_at']=old.now()
 s['deployment']['summary']='Exact qualified E080 server restored after the Windows reboot. Saved-file inventory and served UI bytes are unchanged. Research continues on port 43735.'
 s['evidence'].append({'label':'Verified server recovery after reboot','url':'evidence/'+H.name+'/report.json'})
 s.update(updated_at=old.now(),state='running',goal_status='active',stage='Resume CFV row-width analysis after reboot recovery',activity='The Windows reboot stopped the app. The exact accepted E080 executable is serving the app and tracker again; no code or saved files changed. Resume the new CFV dependency analysis.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.save(H/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'intended_background_app_server_live':native['pid'],'restart_helper_terminal':True})
print(json.dumps({'status':'restored','pid':native['pid'],'saved_files_preserved':len(before),'new_performance_samples':0}),flush=True)
