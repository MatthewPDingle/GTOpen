import sys,json,shutil,subprocess,urllib.request
from pathlib import Path
EPOCH=Path(__file__).resolve().parent;ROOT=EPOCH.parent
ARCHIVE=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(ARCHIVE/'runs/accepted-E080-live-20261018'));import common_e080_live as old
old.custody();assert not(ARCHIVE/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert ROOT.drive.upper()=='X:'and shutil.disk_usage(ROOT).free>=66*1024**3
assert not(EPOCH/'baseline-protocol.json').exists()
for name in ['binaries','runs','comparisons']:(ROOT/name).mkdir(exist_ok=False)
C=ARCHIVE/'runs/accepted-E080-live-20261018'
for source,target in [(C/'baseline.json','accepted-source.json'),(C/'protected-main.json','protected-main.json'),(C/'preexisting-target-artifacts.json','preexisting-target-artifacts.json')]:
 shutil.copyfile(source,EPOCH/target);assert old.sha(source)==old.sha(EPOCH/target)
for stem in ['E080-solver','E080-postflop_autoresearch']:
 source=ARCHIVE/'binaries'/(stem+'.exe');m=old.read(source.with_suffix('.manifest.json'));old.pin(source,m['binary_sha256']);assert m['source_sha256']==old.BASE
 for p in [source,source.with_suffix('.manifest.json')]:
  dest=ROOT/'binaries'/p.name;shutil.copyfile(p,dest);assert old.sha(p)==old.sha(dest)
old.save(EPOCH/'exact-anchor.json',json.loads(json.dumps(old.historical.exact_raw('E020C1'))))
old.save(EPOCH/'anchor-provenance.json',{'id':'E020C1','excluded_fields':sorted(old.historical.EXCLUDED),'results':3,'checkpoints':23,'copied_expected_values_exact':True,'historical_timing_used':False,'reference_report_sha256':old.sha(ARCHIVE/'runs/E020C1/report.json'),'reference_log_sha256':old.sha(ARCHIVE/'runs/E020C1/stdout.log')})
ps="""@{memory=@(Get-CimInstance Win32_PhysicalMemory | Select-Object DeviceLocator,Capacity,Speed,ConfiguredClockSpeed,Manufacturer,PartNumber);cpu=@(Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed);os=@(Get-CimInstance Win32_OperatingSystem | Select-Object LastBootUpTime,TotalVisibleMemorySize,Version,BuildNumber);output_volume=@(Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='X:'" | Select-Object DeviceID,VolumeName,VolumeSerialNumber,FileSystem,Size,FreeSpace)} | ConvertTo-Json -Depth 5"""
hardware=json.loads(subprocess.check_output(['powershell.exe','-NoProfile','-Command',ps],text=True,encoding='utf-8-sig',creationflags=subprocess.CREATE_NO_WINDOW))
hardware.update(at=old.now(),gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader']),user_reported_RAM_timings_changed=True,active_RAM_latency_timings='Not exposed by standard Windows inventory; no inference from DIMM part number.',CPU_threads_used=16,configuration='Exact accepted E080 executable, GPU, compressed CPU storage',storage='New outputs on physical X. Prior archive on S is read-only; no T dependency in new runtime.',current_rustc=old.ar.read_command(['rustc','-Vv']))
assert hardware['gpu']['returncode']==0 and'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee'in hardware['gpu']['stdout']
old.save(EPOCH/'hardware.json',hardware);old.save(EPOCH/'status-before.json',old.read(old.ar.STATUS))
index=old.ar.DASHBOARD/'index.html';before=index.read_bytes();(EPOCH/'dashboard-before.html').write_bytes(before)
text=before.decode();needle='    <div id="fetch-alert"'
banner='    <section class="panel wide" id="hardware-epoch-banner"><div class="panel-body"><div class="label">New RAM measurement epoch · 28 October 2026</div><p>The headline results below belong to the earlier RAM settings. A fresh E080 baseline is being collected on X; the tracker will publish its measurements separately.</p></div></section>\n'
assert text.count(needle)==1;text=text.replace(needle,banner+needle,1)
nl=b'\r\n'if b'\r\n'in before else b'\n';index.write_bytes(text.replace('\r\n','\n').encode().replace(b'\n',nl))
sequence=[{'id':'RAM20261028-V01','title':'New RAM epoch: accepted E080 correctness tests','kind':'validation','binary':'E080-solver','unit':True,'scored':False},{'id':'RAM20261028-W01','title':'New RAM epoch: prespecified E080 warm-up','kind':'validation','binary':'E080-postflop_autoresearch','unit':False,'scored':False}]
sequence += [{'id':f'RAM20261028-B{i:02d}','title':f'New RAM epoch: accepted E080 baseline {i}/5','kind':'baseline','binary':'E080-postflop_autoresearch','unit':False,'scored':True}for i in range(1,6)]
s=old.read(old.ar.STATUS)
for x in sequence:assert not any(y['id']==x['id']for y in s['experiments'])
current={'status':'collecting','configuration':'E080','measurement_epoch_id':'RAM20261028','correctness':'pending','fixtures':[{**{k:f[k]for k in ['id','name','description']},'baseline':{},'best':{},'correctness':{'status':'pending','details':'Fresh baseline under changed RAM timings pending.'},'evidence':[]}for f in s['fixtures']]}
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS)
 s['measurement_epoch']={'id':'RAM20261028','label':'RAM settings changed · 28 October 2026','status':'collecting_baseline','summary':'Rebaseline the best accepted E080 configuration before evaluating further optimizations.','output_root':str(ROOT),'historical_archive':str(ARCHIVE),'prior_gains_historical_only':True}
 s['current_hardware_baseline']=current
 s['research_storage']={'current_output_root':str(ROOT),'physical_drive':'X:','historical_archive_read_only':str(ARCHIVE),'instruction_date':'2026-10-28','prior_T_reserve_not_used_for_new_work':True}
 s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='RAM20261028-baseline',stage='Fresh E080 baseline under changed RAM timings',activity='Run 86 ordinary tests, one prespecified warm-up and five complete three-fixture measurements on X. Keep all exactness checks and every observation. Earlier gains are historical.')
 old.ar.atomic_json(old.ar.STATUS,s)
paths=[p for p in EPOCH.iterdir()if p.is_file()and p.name!='baseline-protocol.json']+list((ROOT/'binaries').iterdir())+[old.REPO/'tools/postflop_autoresearch.py',index]
P={'id':'RAM20261028-baseline','at':old.now(),'status':'FROZEN_PRE_FIRST_NEW_RAM_BENCHMARK','sequence':sequence,'scored_processes':5,'prespecified_unscored_warmup_processes':1,'unit_expected_pass':86,'unit_expected_ignored':4,'baseline_configuration':'Exact accepted E080 executable and source, unchanged GPU/compressed/Rayon16/quality/stopping/workloads','baseline_binary_sha256':old.sha(ROOT/'binaries/E080-postflop_autoresearch.exe'),'output_root':str(ROOT),'historical_archive_read_only':str(ARCHIVE),'required_free_bytes':66*1024**3,'conservative_peak_new_output_reservation_bytes':2*1024**3,'aggregation':'Unrounded sum of five-observation per-fixture complete-cycle medians. All five scored observations retained; warm-up prespecified and separate. No exclusions/extensions/rescue.','exactness':'Every complete non-timing result, fingerprint, EV/exploitability bits, stop and all23convergence checkpoints match unchanged E020C1 reference.','scope':'New RAM/machine epoch baseline, not an optimizer speedup or a controlled causal RAM-only comparison. The old14.7414% gain stays historical. Future improvements require new matched controls and unchanged1%/strictfixture/fresh16/broad/material/capacity/holdout/fresh-original qualification.','input_sha256':{str(p):old.sha(p)for p in paths}}
old.save(EPOCH/'baseline-protocol.json',P)
pub=[]
for p in [EPOCH/'baseline-protocol.json',EPOCH/'hardware.json',EPOCH/'anchor-provenance.json',*[EPOCH/n for n in ['common.py','runner.py','run-baseline.py','assess-baseline.py','prepare-baseline.py']]]:
 key='RAM20261028-baseline/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
 pub.append(key)
old.save(EPOCH/'pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(EPOCH/'baseline-protocol.json'),'HTTP_verified_artifacts':pub,'new_hardware_benchmark_samples':0})
old.custody();print(old.sha(EPOCH/'baseline-protocol.json'),flush=True)
