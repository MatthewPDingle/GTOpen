"""One compiler/one GPU raw process; preserve first numerical failure without retry."""
from pathlib import Path
import json,shutil,subprocess,sys
H=Path(__file__).resolve().parent;R=H.parent.parent;sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
from replay import replay
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');E=H/'execution'
def verify():
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
def child(command,label,env,timeout):
 proc=None;error=None;cleanup=None;start=old.now()
 try:
  with(E/(label+'.stdout.log')).open('xb')as out,(E/(label+'.stderr.log')).open('xb')as err:
   old.save(E/(label+'.invocation.json'),{'at':start,'command':command,'cwd':str(E),'E078_KERNEL_CONTROL_DIR':env.get('E078_KERNEL_CONTROL_DIR')});proc=subprocess.Popen(command,cwd=E,env=env,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW);proc.wait(timeout=timeout)
 except BaseException as exc:error=repr(exc);cleanup=old.ar.cleanup_child(proc);raise
 finally:old.save(E/(label+'.exit.json'),{'started_at':start,'finished_at':old.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup})
 return proc.returncode
verify();assert not E.exists()and not(H/'probe.exe').exists()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3;E.mkdir();gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid']in gpu['stdout'];old.save(E/'before.json',{'at':old.now(),'GPU':gpu})
 rc=child(P['rustc_command'],'rustc',old.env(),300);verify();assert rc==0,'compiler failed; no native numerical process started';old.save(E/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(H/'probe.exe'),'native_processes':0})
 env=old.env();env['E078_KERNEL_CONTROL_DIR']=str(H/'evidence');rc=child([str(H/'probe.exe')],'probe',env,900);verify();corpus=old.read(H/'corpus.json');raw=replay(H/'evidence',corpus)
 markers=[json.loads(x.split('E078_UNIT ',1)[1])for x in(E/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if x.startswith('E078_UNIT ')];complete=[x for x in markers if x['stage']=='complete'];case_markers=[x for x in markers if x['stage']=='case'];assert [x['id']for x in case_markers]==list(range(len(case_markers)))
 assert all(x['all_raw_exact']and x['guards_exact']for x in case_markers)
 if rc==0:
  assert len(complete)==1 and len(case_markers)==complete[0]['cases']==1638 and complete[0]['kernel_launches']==4095 and raw['complete_frozen_corpus'];summary=complete[0];assert raw['output_words_both_arms']==summary['output_words_both_arms']and raw['actual_input_words_both_arms']==summary['immutable_words_both_arms']and raw['guard_words_both_arms']==summary['guard_words_both_arms']
 else:
  assert not complete and raw['first_output_differences']and raw['completed_case_count']==len(case_markers)+1,'nonzero native not an independently reproduced complete-case output mismatch';assert 'original/candidate case'in(E/'probe.stderr.log').read_text(encoding='utf-8',errors='replace');summary=None
 passed=rc==0 and raw['all_full_output_words_exact']and raw['all_finite_fold_oracle_words_exact'];status='pass_full_raw_fold_action_controls'if passed else'decline_exact_fold_action_numerical_form'
 report={'id':'E078-kernel-control','at':old.now(),'status':status,'protocol_sha256':sys.argv[1],'native_returncode':rc,'binary_sha256':old.sha(H/'probe.exe'),'raw_replay':raw,'native_complete_summary':summary,'raw_files':{p.name:{'bytes':p.stat().st_size,'sha256':old.sha(p)}for p in(H/'evidence').iterdir()if p.is_file()},'application_launches_maximum':4095,'all_owned_children_terminal':True,'compiled_once':True,'native_processes':1,'NVRTC_reruns':0,'source_activated':False,'solver_or_performance_measurements':0,'candidate_accepted':False,'accepted_main_live_PTX_custody_pass':True,'excluded_cases':[],'extension_runs':0,'limits':'Finite declared direct corpus, full actual physical input/output/guard bit comparisons, CPUfoldoracle only declaredfinite/signedzero/subnormal modes; not mathematical universal equivalence or integratedtree/state/continuation/F32/save/menu/material/complete-solve speed. Actualfullintegratedsource stillunactivated. Firstactual numerical mismatch closes exactform,nosource/helper/marker/arity/thread/placement/threshold or resampling rescue.'};old.save(H/'report.json',report);verify();old.save(E/'complete.json',{'at':old.now(),'report_sha256':old.sha(H/'report.json'),'all_owned_children_terminal':True,'status':status})
print(json.dumps({'status':status,'native_returncode':rc,'raw_cases':raw['completed_case_count'],'output_words':raw['output_words_both_arms'],'first_differences':raw['first_output_differences'][:3],'oracle_differences':raw['first_finite_fold_oracle_differences'][:3],'report_sha256':old.sha(H/'report.json')}),flush=True)
