"""Strict acceptance gate for frozen native comparator reports."""
import datetime as dt
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
for run_id in sys.argv[1:]:
    d=json.loads((HERE/'raw'/f'{run_id}.log').read_text(encoding='utf-8'))
    assert d['headers_identical_after_point_lock_order_canonicalization'], run_id
    assert d['all_compared_values_finite'], run_id
    assert d['invalid_effective_entries']==0 and d['invalid_reach_classes']==0, run_id
    stats=[*d['raw_arenas'].values(),d['effective_average_strategy'],d['raw_arena_normalized_strategy']]
    for s in stats:
        assert s['entries']==s['bit_equal']==s['finite_pairs'], (run_id,s)
        assert s['max_abs']==0 and s['max_ulp']==0, (run_id,s)
    result=dict(event='full_native_exact_assertion',id=run_id,utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                iteration=d['iteration'],payoff_model=d['payoff_model'],
                raw_arena_entries=sum(s['entries'] for s in d['raw_arenas'].values()),
                effective_policy_entries=d['effective_average_strategy']['entries'],passed=True)
    with (HERE/'events.jsonl').open('a',encoding='utf-8') as out: out.write(json.dumps(result)+'\n')
    print(json.dumps(result))
