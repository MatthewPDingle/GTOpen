"""One fixed full raw GPU fold comparison, then independent raw-word replay."""
from pathlib import Path
import json,shutil,sys
R=Path(__file__).resolve().parent.parent;H=R/'runs/E072-direct-fold';sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as c
assert len(sys.argv)==2;c.pin(H/'protocol.json',sys.argv[1]);P=c.read(H/'protocol.json')
def verify():
 c.pin(H/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():c.pin(p,h)
 c.custody()
verify();B=H/'build';E=H/'execution';assert not B.exists()and not E.exists()and not(H/'probe.exe').exists()
with c.ar.exclusive_lock(R/'gpu-run.lock'):
 c.ar.refuse_active(c.ar.live_status());assert shutil.disk_usage(R).free>=P['minimum_free_S_bytes'];B.mkdir();E.mkdir()
 c.child(P['command'],B,'rustc',c.env(),180);verify();c.save(B/'complete.json',{'at':c.now(),'compiler_terminal':True,'binary_sha256':c.sha(H/'probe.exe'),'application_kernel_launches':0})
 env=c.env();env['E072_FOLD_KERNEL_CONTROL_DIR']=P['raw_output_directory'];c.ar.refuse_active(c.ar.live_status());verify()
 c.child([str(H/'probe.exe')],E,'probe',env,300);verify()
 raw=(E/'probe.stdout.log').read_text(encoding='utf-8');markers=[json.loads(x.split('E072_FOLD_UNIT ',1)[1])for x in raw.splitlines()if x.startswith('E072_FOLD_UNIT ')];assert len(markers)==361 and markers[-1]['cases']==360 and markers[-1]['kernel_launches']==720 and markers[-1]['all_raw_exact']and markers[-1]['all_inputs_and_guards_exact']
 c.child([sys.executable,'-B',str(H/'audit_raw.py'),'up-fold',str(H),P['raw_output_directory'],str(H/'report.json')],E,'root-audit',c.env(),300);verify()
 q=c.read(H/'report.json');assert q['status']=='pass_scoped_full_raw_equivalence'and q['cases']==360 and q['kernel_launches']==720 and q['full_raw_files_equal']
 c.save(H/'complete.json',{'at':c.now(),'status':'pass_scoped_full_fold_raw_equivalence','protocol_sha256':sys.argv[1],'report_sha256':c.sha(H/'report.json'),'cases':360,'application_kernel_launches':720,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'source_activated':False,'solver_executions':0,'performance_measurements':0,'candidate_accepted':False});print({'direct_fold':'pass','cases':360,'launches':720,'checks':q['checks'],'solver_or_timing_runs':0},flush=True)
