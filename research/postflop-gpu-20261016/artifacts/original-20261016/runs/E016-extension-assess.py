"""Apply the sealed finite-extension gates after every run completes."""
import json, shutil, subprocess, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
protocol_path=ar.RESEARCH/'runs/E016-extension/protocol.json'
protocol=json.loads(protocol_path.read_text(encoding='utf-8'))
assert ar.sha256(protocol_path)=='dc8eacf39025fa8330a7aca35a32f75403aa2de0db6e8967e26569c89fae38f2'
completed=json.loads((protocol_path.parent/'completed.json').read_text(encoding='utf-8'))
assert completed['runs_completed']==12 and completed['protocol_sha256']==ar.sha256(protocol_path)
reports={}
for name,key in [('E016-extension-new-six','new_pairs'),('E016-extension-pooled-nine','pooled_pairs')]:
    pairs=protocol[key]
    subprocess.run([sys.executable,'tools/postflop_compare.py','--id',name,'--candidate-id','E016',
      '--baseline-runs',*[p['baseline'] for p in pairs],'--candidate-runs',*[p['candidate'] for p in pairs],
      '--warm-cache-cohort'],cwd=repo,check=True)
    reports[name]=json.loads((ar.RESEARCH/'comparisons'/name/'report.json').read_text(encoding='utf-8'))
verdicts={name:{'aggregate_gate_met':r['performance']['aggregate_gate_met'],
  'fixture_guard_pass':not r['performance']['fixture_regression_guard']['failed'],
  'performance':r['performance']} for name,r in reports.items()}
passed=all(v['aggregate_gate_met'] and v['fixture_guard_pass'] for v in verdicts.values())
out=ar.RESEARCH/'comparisons/E016-extension-terminal';out.mkdir(exist_ok=False)
result={'created_at':ar.now(),'protocol':{'path':str(protocol_path),'sha256':ar.sha256(protocol_path)},
  'decision':'performance_pass_pending_independent_review' if passed else 'rejected',
  'accepted':False,'deployed':False,'cohorts':verdicts,
  'initial_failure_retained':True,'all_original_pairs_pooled':True,'diagnostic_D028_excluded':True,
  'further_extension_permitted':False,'statistical_significance_claim':False,
  'scope':'Adaptive engineering qualification amendment, explicitly triggered by the initial failure and D028 inconsistency. Both new-six and pooled-nine gates required.',
  'comparisons':[{'path':str(ar.RESEARCH/'comparisons'/name/'report.json'),'sha256':ar.sha256(ar.RESEARCH/'comparisons'/name/'report.json')} for name in reports]}
ar.atomic_json(out/'report.json',result)
dest=ar.DASHBOARD/'evidence/E016-extension-terminal/report.json';dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(out/'report.json',dest)
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    status=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    row=next(e for e in status['experiments'] if e['id']=='E016')
    row['correctness']='pass';row['status']='qualifying' if passed else 'rejected'
    row['reason']=('Both fixed extension cohorts passed the unchanged performance gates. Initial failed cohort remains preserved; independent review and final qualification pending.' if passed else 'Rejected: the bounded extension failed at least one required performance gate. All earlier failures remain preserved; no further extension is permitted.')
    row['evidence'].append({'label':'Finite extension terminal assessment','url':'evidence/E016-extension-terminal/report.json','detail':row['reason']})
    status.update(updated_at=ar.now(),active_experiment=None,stage='E016 extension terminal review' if passed else 'E016 rejected after finite extension',activity=row['reason']+' Accepted headline remains E015 9.62%.')
    ar.atomic_json(ar.STATUS,status)
print(json.dumps(result,indent=2))
