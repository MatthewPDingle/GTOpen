import json,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
H=ROOT/'runs/E120-primary-checkpoint';R=h.read(H/'report.json');pub=h.read(H/'publication.json')
for row in R['child_receipts']:
 h.pin(row['path'],row['sha256']);r=h.read(row['path']);assert r['returncode']==row['returncode']and r['error']is r['cleanup']is None
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip();assert head==pub['local_commit'];assert not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=h.REPO,text=True).strip();assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
for path,url in [(h.ar.STATUS,'status.json'),(h.ar.DASHBOARD/'index.html','index.html'),(H/'report.json','evidence/E120-primary-checkpoint/report.json'),(ROOT/'comparisons/E120-three-pair-comparison/report.json','evidence/E120-three-pair-comparison/report.json')]:
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/'+url,timeout=20)as z:assert z.read()==path.read_bytes()
pidcheck=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter 'ProcessId = 26528' | Select-Object ProcessId,ExecutablePath | ConvertTo-Json -Compress"],text=True);process=json.loads(pidcheck);assert process['ExecutablePath'].lower()==str(Path(r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe')).lower()
h.save(H/'terminal-audit.json',{'at':h.now(),'status':'E120_ALL_OWNED_WORK_TERMINAL_QUALIFICATION_PENDING'if R['performance']['primary_timing_pass']else'E120_CLOSED_ALL_OWNED_WORK_TERMINAL','all_child_receipts_terminal_and_explained':len(R['child_receipts']),'locks_absent':True,'source_main_live_protected_PTX_exact':True,'HTTP_status_index_checkpoint_result_exact':True,'server_idle':True,'live_pid':26528,'local_ledger_commit':head,'research_tracked_diff_clean':True,'observed_primary_gain_pct':R['performance']['observed_gain_pct'],'new_adopted_gain':False,'goal_active':True,'last_primary_baseline':'B371','next_unused_primary_baseline':'B372','X_free_bytes':shutil.disk_usage(ROOT).free,'all_new_bulk_X_S_readonly_no_T':True})
print(json.dumps(h.read(H/'terminal-audit.json'),indent=2),flush=True)
