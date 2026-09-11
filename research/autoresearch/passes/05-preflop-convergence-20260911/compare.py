"""Compare only completed, matching-input full-gap trials; preserve missing runs."""
import json, math, statistics
from pathlib import Path
from summarize import HERE

trials=json.loads((HERE/'summary.json').read_text())['trials']
for row in trials:
    name=row['name']
    protocol=HERE/'raw'/(name+'-protocol.json')
    row['protocol']=json.loads(protocol.read_text()) if protocol.exists() else None

comparisons=[]
for candidate in trials:
    # Tiny fixtures are correctness controls; cold NVRTC setup dominates timing.
    if candidate['schedule'] in ('native',) or candidate['target']!=.005 or candidate['nodes']<10_000:continue
    cp=candidate['protocol']
    matches=[]
    for baseline in trials:
        bp=baseline['protocol']
        if baseline['schedule']!='native' or baseline['target']!=candidate['target'] or not bp or not cp:continue
        if not all(cp.get(key)==bp.get(key) for key in ['input_sha256','cache_sha256','fit_sha256','exe_sha256']):continue
        if baseline['two_global_passes']:matches.append(baseline)
    qualifies=candidate['two_global_passes'] and bool(matches)
    ratio=(statistics.median(x['to_last_check_seconds'] for x in matches)/candidate['to_last_check_seconds']) if qualifies else None
    comparisons.append({'candidate':candidate['name'],'baseline_trials':[x['name'] for x in matches],
        'matched_full_gap_speedup':ratio,'candidate_seconds':candidate['to_last_check_seconds'],
        'candidate_complete_seconds':candidate['complete_seconds'],'candidate_gap':candidate['gap'],
        'local_status':candidate['local_status'],
        'claim_scope':'Time to two consecutive full-model global-gap checks only; not qualified local convergence.' if qualifies else 'No completed matching comparison yet.'})

expected=['eight-s128-a','eight-native-a','eight-s64-a','eight-s128-b','modeled-native-a','modeled-s128-a']
done={x['name'] for x in trials}
result={'comparisons':comparisons,'unfinished_registered_large_trials':[n for n in expected if n not in done],
        'production_qualification':'not established','all_reported_ratios_finite':all(c['matched_full_gap_speedup'] is None or math.isfinite(c['matched_full_gap_speedup']) for c in comparisons)}
(HERE/'comparison.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
