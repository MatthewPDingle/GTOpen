"""Keep self-policy diagnostics distinct from comparisons to reference play."""
import json
from pathlib import Path
from run_local_v2 import CASES

HERE = Path(__file__).resolve().parent


def classify(nodes):
    # Forced play is not a learning-policy convergence test. Unreachable or
    # missing nodes cannot silently turn an incomplete audit into a pass.
    failures = sum(n.get('passes_local_tail_gate') is False for n in nodes)
    forced = sum(n.get('forced_or_frozen') is True for n in nodes)
    tested = [n for n in nodes if n.get('forced_or_frozen') is not True]
    complete = bool(tested) and all(n.get('status') == 'evaluated' and
                                  isinstance(n.get('passes_local_tail_gate'), bool)
                                  for n in tested)
    status = 'fail' if failures else ('pass' if complete else 'incomplete')
    return dict(status=status, failed_nodes=failures, forced_nodes=forced,
                requested_nodes=len(nodes), learning_nodes=len(tested))


def summarize():
    records = []
    for name, reference in CASES:
        record = dict(name=name, reference=reference, status='not_run')
        output = HERE / 'raw' / f'{name}-local-v2.json'
        exit_path = HERE / 'raw' / f'{name}-local-v2-exit.json'
        if not exit_path.exists():
            if output.exists():
                record['status'] = 'completion_not_verified'
            records.append(record)
            continue
        result = json.loads(exit_path.read_text())
        record['seconds'] = result['seconds']
        if result.get('returncode') != 0 or result.get('reason') or not output.exists():
            record.update(status='audit_failed', reason=result.get('reason'),
                          returncode=result.get('returncode'))
            records.append(record)
            continue
        audit = json.loads(output.read_text())
        rows = audit.get('rows', [])
        record['status'] = 'completed' if rows else 'incomplete'
        for label in ['candidate', 'candidate_self', 'reference_self']:
            record[label] = classify([row.get(label, {}) for row in rows])
        record['nodes'] = []
        for row in rows:
            node = dict(path=row.get('candidate', {}).get('path'),
                        position=row.get('candidate', {}).get('position'))
            for label in ['candidate', 'candidate_self', 'reference_self']:
                source = row.get(label, {})
                node[label] = {key: source.get(key) for key in [
                    'status', 'forced_or_frozen', 'passes_local_tail_gate',
                    'weighted_action_loss_bb', 'joint_reach_independent_model',
                    'worst_relevant_probability_on_strongly_inferior_actions']}
            record['nodes'].append(node)
        records.append(record)
    return dict(scope='Selected-path one-step diagnostics only; no full-subgame or production qualification.',
                trials=records)


if __name__ == '__main__':
    result = summarize()
    (HERE / 'local-v2-summary.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
