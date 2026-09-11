"""Summarize completed trials without treating global-gap passes as local passes."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
rows=[]
for path in sorted((HERE/'raw').glob('*-result.json')):
    r=json.loads(path.read_text())
    if 'checks' not in r or not r['checks']:continue
    last=r['checks'][-1]
    row={'name':path.name.removesuffix('-result.json'),'schedule':r['schedule'],'samples':r['samples'],
         'seed':r['seed'],'nodes':r['nodes'],'iteration':r['iteration'],'target':r.get('target',.005),
         'two_global_passes':r['converged_twice'],'gap':last['gap'],'to_last_check_seconds':last['elapsed_seconds'],
         'complete_seconds':r['total_seconds'],'solve_seconds':last['solve_seconds'],'check_seconds':last['check_seconds'],
         'local_status':'not_evaluated','local_audit_seconds':None}
    local=HERE/'raw'/(row['name']+'-local.json')
    if local.exists():
        a=json.loads(local.read_text())
        checks=[x['candidate'].get('passes_local_tail_gate') for x in a['rows'] if x['candidate'].get('status')=='evaluated']
        row['local_status']='pass' if checks and all(x is True for x in checks) else 'fail_or_incomplete'
        row['local_rows']=[{'path':x['candidate']['path'],'position':x['candidate'].get('position'),
            'worst_bad_action_probability':x['candidate'].get('worst_relevant_probability_on_strongly_inferior_actions'),
            'weighted_action_loss_bb':x['candidate'].get('weighted_action_loss_bb'),
            'reference_self_pass':x['reference_self'].get('passes_local_tail_gate')} for x in a['rows']]
        independent=a.get('independent_cpu')
        if independent:
            row['max_cpu_gpu_gap_difference']=max(abs(x-y) for x,y in zip(independent['candidate_gaps'],last['gaps']))
        exit_path=HERE/'raw'/(row['name']+'-local-exit.json')
        if exit_path.exists():row['local_audit_seconds']=json.loads(exit_path.read_text())['seconds']
    row['passes_measured_gates']=row['two_global_passes'] and row['local_status']=='pass'
    row['production_qualification']='not_established_by_this_summary'
    rows.append(row)
(HERE/'summary.json').write_text(json.dumps({'scope':'Research feasibility only; global pass does not imply local convergence.','trials':rows},indent=2))
print(json.dumps([ {k:v for k,v in r.items() if k in ['name','iteration','gap','to_last_check_seconds','local_status','max_cpu_gpu_gap_difference']} for r in rows],indent=2))
