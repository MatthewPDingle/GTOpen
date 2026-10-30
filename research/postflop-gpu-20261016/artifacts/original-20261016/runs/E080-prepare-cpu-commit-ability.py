"""Freeze independent CPU-only explicit commitment calibration."""
from pathlib import Path
import ast,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());H=R/'runs/E080-cpu-commit-ability';assert not(H/'protocol.json').exists()
for n in['probe.py','execute.py']:ast.parse((H/n).read_text(encoding='utf-8'))
prior=R/'runs/E080-memory-observer-ability';oldq=old.read(prior/'report.json');assert not oldq['all_checks_pass']and old.read(prior/'calibration-closure.json')['overall_observer_form']=='closed_after_failed_combined_private_commit_control'
states=[{'stage':'baseline','bytes':0}]
for name,mb in[('alloc128',128),('alloc256',256),('alloc128_repeat',128)]:states.extend([{'stage':name,'bytes':mb*1024*1024},{'stage':name+'_free','bytes':0}])
paths=[Path(__file__),H/'probe.py',H/'execute.py',prior/'win_observer.py',prior/'report.json',prior/'calibration-closure.json',*[prior/'execution'/n for n in['baseline.json','CPU128.json','CPU_free.json']],C/'common_e051_live.py',C/'protected-main.json']
P={'id':'E080-independent-CPU-commit-ability','at':old.now(),'status':'FROZEN_PRE_NATIVE','input_sha256':{str(p):old.sha(p)for p in paths},'states':states,'samples_per_state':40,'interval_ms':50,'plateau_samples':20,'tolerance_bytes':4*1024*1024,'scope':'One CPU-only process with explicit VirtualAlloc reserve/commit, touch every byte, and VirtualFree release across128/256/repeated128MiB. Prove total private/RSS delta and return to baseline without CUDA or unrelated driver commitment. Same sample timing and4MiB tolerance as original calibration, with more than one payload size and repeat release. No solver workload, primary score, cost measurement, threshold relaxation or original failure reclassification.','original_combined_form_closed':True,'next':'If APIs calibrate, any actual solver profile must still include all CUDA/driver process commitment. GPU software accounting has separate fixed allocation/release evidence; original combined private-payload expectation remains failed. Freeze actual full-solve resource gates before any new solver observations.','candidate_accepted':False}
old.save(H/'protocol.json',P)
for p in[Path(__file__),*[p for p in H.iterdir()if p.is_file()]]:
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
old.save(H/'pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_byte_verified':True,'native_observations':0})
M=R/'runs/E080-cpu-commit-manager';assert not M.exists();M.mkdir();print('CPU commitment calibration protocol',old.sha(H/'protocol.json'),flush=True);old.child([sys.executable,'-B',str(H/'execute.py'),old.sha(H/'protocol.json')],M,'ability',old.env(),180);old.custody();print('CPU commitment calibration terminal.',flush=True)
