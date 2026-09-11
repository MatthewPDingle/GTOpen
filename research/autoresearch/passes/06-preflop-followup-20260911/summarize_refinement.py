from run_experiment import HERE
import json

rows=[]
for name in ('refine-native100','refine-native-nested100','refine-sampled-nested100','refine-native-nested1000','refine-sampled-nested1000'):
    result=json.loads((HERE/'raw'/f'{name}-result.json').read_text())
    audit=json.loads((HERE/'raw'/f'{name}-local-v3.json').read_text())
    exits=[json.loads((HERE/'raw'/f'{name}{suffix}-exit.json').read_text()) for suffix in ('','-local')]
    if any(e['returncode'] or e['reason'] for e in exits):raise RuntimeError(name)
    refinement=result['refinement']
    if isinstance(refinement,dict):refinement=[refinement]
    rows.append(dict(name=name,seconds_including_load_global_check_save=result['elapsed_including_load_revalidation_save_seconds'],
        additional_independent_audit_wall_seconds=exits[1]['seconds'],
        local_learning_seconds=sum(r['seconds'] for r in refinement),global_gap_bb=sum(result['global_gaps']),
        independent_audit_global_gap_bb=sum(audit['independent_cpu']['candidate_gaps']),
        local_nodes=[dict(path=r['candidate_self']['path'],position=r['candidate_self'].get('position'),
            status=r['candidate_self']['status'],passes=r['candidate_self'].get('passes_local_tail_gate'),
            weighted_action_loss_bb=r['candidate_self'].get('weighted_action_loss_bb')) for r in audit['rows']]))
(HERE/'REFINEMENT-RESULTS.json').write_text(json.dumps(dict(scope='Selected conditional decisions only; additional refinement time is not included in GPU speedups; offline snapshots are not normal resumable sessions.',trials=rows),indent=2)+'\n',encoding='utf-8',newline='\n')
for r in rows:print(r['name'],r['seconds_including_load_global_check_save'],r['global_gap_bb'],sum(n['passes'] is True for n in r['local_nodes']))
