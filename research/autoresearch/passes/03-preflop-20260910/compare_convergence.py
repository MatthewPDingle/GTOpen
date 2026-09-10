"""Compare frozen checkpoint trajectories without changing stopping targets."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL = json.loads((HERE/'convergence-protocol.json').read_text(encoding='utf-8'))

def read(run_id):
    path = HERE/'raw'/f'{run_id}.log'
    if not path.exists():
        return {'status': 'not_started', 'checkpoints': [], 'result': None, 'error': None}
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.startswith('CONVERGENCE '):
            continue
        try:
            rows.append(json.loads(line[len('CONVERGENCE '):]))
        except json.JSONDecodeError:
            continue  # A live writer can have an unfinished final line.
    result = next((r for r in reversed(rows) if r.get('phase') == 'result'), None)
    error = next((r for r in reversed(rows) if r.get('phase') == 'error'), None)
    return {'status': result['status'] if result else 'error' if error else 'running_or_interrupted',
            'result': result, 'error': error,
            'last_iteration': next((r['iteration'] for r in reversed(rows) if r.get('phase') == 'iterate'), None),
            'checkpoints': [r for r in rows if r.get('phase') == 'checkpoint']}

def compare():
    out = []
    exact_fields = ['iteration', 'done', 'gaps', 'evs', 'live_seats', 'learning_gap_bb',
                    'target_gap_bb', 'target_reached']
    for fixture in ['modeled', 'eight']:
        names = [f'convergence-{fixture}-{v}-a' for v in ['original', 'compatible']]
        original, candidate = [read(n) for n in names]
        left = {r['done']: r for r in original['checkpoints']}
        right = {r['done']: r for r in candidate['checkpoints']}
        points = []
        for done in sorted(left.keys() & right.keys()):
            a, b = left[done], right[done]
            mismatched = [k for k in exact_fields if a[k] != b[k]]
            points.append({'done': done, 'learning_gap_bb': a['learning_gap_bb'],
                           'exact': not mismatched, 'mismatched_fields': mismatched,
                           'original_ms': a['iterations_ms_total']+a['checks_ms_total']+a['syncs_ms_total'],
                           'candidate_ms': b['iterations_ms_total']+b['checks_ms_total']+b['syncs_ms_total']})
        row = {'fixture': fixture, 'target_gap_bb': PROTOCOL['runs'][names[0]]['target_gap_bb'],
               'original': original, 'candidate': candidate, 'matched_checkpoints': points}
        if original['result'] and candidate['result']:
            a, b = original['result'], candidate['result']
            fields = ['start_iteration', 'done', 'iteration', 'budget_mb', 'target_gap_bb', 'learning_gap_bb',
                      'check_every', 'gaps', 'evs', 'live_seats', 'arena_fnv1a64', 'converged', 'status', 'roundtrip_verified']
            row['final_mismatches'] = [k for k in fields if a[k] != b[k]]
            expected = list(range(a['check_every'], a['done']+1, a['check_every']))
            if a['done'] and a['done'] % a['check_every']:
                expected.append(a['done'])
            if [p['done'] for p in original['checkpoints']] != expected or [p['done'] for p in candidate['checkpoints']] != expected:
                row['final_mismatches'].append('complete_checkpoint_sequence')
            row['exact_trajectory_and_final_state'] = not row['final_mismatches'] and all(p['exact'] for p in points)
            row['trajectory_reduction_percent'] = 100*(1-b['trajectory_ms']/a['trajectory_ms'])
            row['interpretation'] = ('Time to the same fixed accuracy target' if a['converged'] and b['converged']
                                      else 'Fixed-iteration trajectory only; accuracy target was not reached by both')
        out.append(row)
    (HERE/'convergence-comparisons.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    for row in out:
        print(json.dumps({'fixture':row['fixture'], 'original_status':row['original']['status'],
                          'original_iteration':row['original'].get('last_iteration'),
                          'candidate_status':row['candidate']['status'],
                          'candidate_iteration':row['candidate'].get('last_iteration'),
                          'matched_checkpoints':len(row['matched_checkpoints']),
                          'all_matched_exact':all(p['exact'] for p in row['matched_checkpoints']) if row['matched_checkpoints'] else None,
                          'final_exact':row.get('exact_trajectory_and_final_state')}))
    return out

if __name__ == '__main__':
    results = compare()
    if any(r.get('final_mismatches') or any(not p['exact'] for p in r['matched_checkpoints']) for r in results):
        raise SystemExit('Convergence parity mismatch; retain evidence for investigation.')
