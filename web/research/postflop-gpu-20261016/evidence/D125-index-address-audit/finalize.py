"""Finish publication/commit after the completed read-only audit's missing import."""
from pathlib import Path
import json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
H=R/'runs/D125-index-address-audit';P=old.read(H/'protocol.json');q=old.read(H/'report.json')
old.custody();assert not (R/'gpu-run.lock').exists()
for p,h in P['input_sha256'].items():old.pin(p,h)
assert q['status']=='pass_original_tag_decode_semantics_with_byte_offset_masks'and all(q['effective_gates'].values())
assert q['compiler_native_GPU_solver_or_timing_executions']==0 and q['compiled_source_PTX_and_resource_rows_unchanged']
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';assert ledger.read_bytes().count(b'### D125 read-only widened index-mask address audit')==1
s=old.read(old.ar.STATUS);assert s['active_experiment']=='E077'and next(x for x in s['experiments']if x['id']=='D125')['status']=='measured'
old.save(H/'finalization-repair.json',{'at':old.now(),'original_script_sha256':old.sha(R/'runs/D125-index-address-audit.py'),'error':'NameError: subprocess not defined at final git commit only; all address/parser/algebra/resource checks, report/publication/status and ledger append had already completed.','repair':'Validate original frozen script/report/source/PTX/status/ledger, perform only pending ledger commit and publish this receipt. Do not rerun the audit, change any source/gate/report or execute a native process.','report_sha256':old.sha(H/'report.json'),'new_audit_or_compiler_resource_GPU_solver_timing_executions':0})
for p,key in [(H/'finalization-repair.json',H.name+'/finalization-repair.json'),(Path(__file__),H.name+'/finalize.py')]:
 dst=old.ar.DASHBOARD/'evidence'/key;assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
subprocess.run(['git','commit','--only','-m','research: verify widened index decode from immutable PTX addresses','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
old.custody()
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/report.json',timeout=15)as response:assert response.read()==(H/'report.json').read_bytes()
print(json.dumps({'status':q['status'],'checks':q['checks'],'effective_gates':all(q['effective_gates'].values()),'new_native_executions':0,'address_counts':{a:{'sources':len(x['sources']),'sinks':len(x['address_sinks']),'mask_sites':len(x['mask_witnesses'])}for a,x in q['address_analyses'].items()},'source_and_original_resource_report_unchanged':True,'all_owned_native_handles_terminal':True}),flush=True)
