"""One auditable full-policy crossed batch; caller owns sampling and admission.

Uses the existing native full-action evaluator. No forced root actions and no
new poker deals are generated here. Compatible with owned test-batch archives.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from sampled_physical_root_evaluation_v1 import sha, save
from crossed_complete_policy_comparison_v1 import crossed_profiles, differences, PROFILE_NAMES


def evaluate_batch(*, batch, folder, context_path, banks, cache, query_executable,
                   evaluation_executable, guard):
    if len(banks) != 4 or batch.get('format') != 2 or not 1 <= len(batch['deals']) <= 64:
        raise ValueError('Four frozen banks and a bounded visible-query batch required')
    if any(k.startswith('allin_') or k == 'terminal_estimator' for k in batch):
        raise ValueError('Hidden all-in labels cannot enter the query batch')
    guard(); folder=Path(folder); folder.mkdir(exist_ok=False)
    context_path=Path(context_path); context_source=context_path.read_text()
    context=json.loads(context_source)
    raw=folder/'query-batch.json'; labelled=folder/'conditional-batch.json'
    query_path=folder/'queries.json'; transport=folder/'profiles.json'; native_path=folder/'native.json'
    save(raw,batch); labels=cache.batch(batch); cache.check_batch(labels); save(labelled,labels)

    def invoke(executable, arguments):
        guard(); start=time.monotonic()
        result=subprocess.run([str(executable),*map(str,arguments)],capture_output=True,text=True,
            timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode: raise RuntimeError(result.stderr[-2000:])
        guard(); return time.monotonic()-start

    query_seconds=invoke(query_executable,['queries',context_path,raw,'-',query_path])
    query=json.loads(query_path.read_text())
    if query['context_source']!=context_source or query['batch_source']!=raw.read_text():
        raise ValueError('Native query identity mismatch')
    policies=[];coverage=[];timings=[]
    for bank in banks:
        guard();start=time.monotonic();p,support=bank.average(query,guard=guard)
        timings.append(time.monotonic()-start)
        p=np.asarray(p,dtype=np.float64); support=np.asarray(support,dtype=np.float64)
        if support.shape!=(len(query['observations']),) or not np.isfinite(support).all() or np.any(support<0):
            raise ValueError('Invalid own-action realization support')
        policies.append(p)
        coverage.append(dict(probabilities_sha256=hashlib.sha256(p.tobytes()).hexdigest(),
            support_sha256=hashlib.sha256(support.tobytes()).hexdigest(),
            zero_reach_rows=int(np.sum(support==0))))
    profiles=crossed_profiles(query,policies)
    save(transport,dict(format=1,context_source=context_source,batch_source=labelled.read_text(),profiles=profiles))
    native_seconds=invoke(evaluation_executable,[context_path,labelled,transport,native_path])
    native=json.loads(native_path.read_text())
    if (native['format']!=2 or native['terminal_estimator']!='conditional-preflop-allin-v1'
            or native['postflop_outcomes']!='sampled-board'
            or [p['name'] for p in native['profiles']]!=list(PROFILE_NAMES)):
        raise ValueError('Unexpected native evaluation protocol or profile order')
    for name in ('maximum_forward_cashflow_error','maximum_conservation_error'):
        if not 0<=native[name]<1e-10: raise ValueError('Native payoff identity failed')
    n=len(batch['deals'])
    if any(len(p['deals'])!=n for p in native['profiles']):
        raise ValueError('Profiles must share the complete batch')
    flat=np.asarray([[d['values'] for d in p['deals']] for p in native['profiles']],dtype=np.float64)
    if flat.shape!=(8,n,2) or not np.isfinite(flat).all():
        raise ValueError('Invalid paired player values')
    values=flat.transpose(1,0,2).reshape(n,2,4,2)
    stack=context['config']['stack'];dead=context['dead_money']
    if np.any(values < -stack) or np.any(values > stack+dead):
        raise ValueError('Payoff outside registered physical bounds')
    # This archive member records paired differences, not best-response residuals.
    residual_path=folder/'residuals.json'
    save(residual_path,dict(format=1,purpose='eight-paired-complete-policy-gains',
        values=differences(values).tolist(),bounds_best_response_above=False))
    summary=dict(format=1,purpose='crossed-complete-policy-effectiveness',deals=n,
        values=values.tolist(),profile_order=list(PROFILE_NAMES),coverage=coverage,
        query_seconds=query_seconds,averaging_seconds=timings,native_seconds=native_seconds,
        allin_cache_sha256=cache.sha256,
        maximum_forward_cashflow_error=native['maximum_forward_cashflow_error'],
        maximum_conservation_error=native['maximum_conservation_error'],
        artifacts={p.name:sha(p) for p in (raw,labelled,query_path,transport,native_path,residual_path)})
    save(folder/'summary.json',summary)
    return summary
