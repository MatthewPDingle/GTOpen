"""Explicit conditional-all-in batch evaluation for an injected visible-policy bank.

This is a new artifact format, not a silent replacement for sampled v1 output.
Equity labels are supplied only to native terminal evaluation; the policy bank
receives the original unlabelled, visible-observation query document.
"""
import json
from pathlib import Path
import subprocess

import numpy as np

from sampled_batch_protocol_v2 import policy_document
from sampled_physical_root_evaluation_v1 import ROOT,sha,save,hand_class

ESTIMATOR = 'conditional-preflop-allin-v1'


def batch_values(context_path,batch,folder,guard,bank,cache):
    """Return root choices and baseline payoffs without a sampled-payoff pass."""
    context_path=Path(context_path);folder=Path(folder)
    guard();folder.mkdir(exist_ok=False)
    raw_path=folder/'query-batch.json';save(raw_path,batch)
    labelled=cache.batch(batch);labelled_path=folder/'conditional-batch.json';save(labelled_path,labelled)
    query_path=folder/'queries.json';profile_path=folder/'profiles.json';native_path=folder/'native.json'
    def invoke(name,args):
        guard()
        run=subprocess.run([str(ROOT/'target/release/examples'/f'{name}.exe'),*map(str,args)],cwd=ROOT,
            capture_output=True,text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        if run.returncode:raise RuntimeError(run.stderr[-2000:])
        guard()
    invoke('hu_sampled_bank_bridge',['queries',context_path,raw_path,'-',query_path])
    queries=json.loads(query_path.read_text())
    assert queries['context_source']==context_path.read_text() and queries['batch_source']==raw_path.read_text()
    assert json.loads(queries['batch_source'])['format']==2
    policy,support=bank.average(queries,guard=guard)
    roots=[i for i,o in enumerate(queries['observations']) if o['phase']==0 and int(o['hi'])==1]
    assert roots and all(queries['observations'][i]['actor']==0 and queries['observations'][i]['n']==4 for i in roots)
    byclass={}
    for i in roots:
        lo=int(queries['observations'][i]['lo']);c=hand_class([lo&63,(lo>>6)&63])
        if c in byclass:assert np.max(np.abs(byclass[c]-policy[i]))<1e-12
        byclass[c]=policy[i]
    profiles=[dict(name='baseline',policies=policy_document(queries,policy)['policies'])]
    for a in range(4):
        changed=policy.copy();changed[roots]=0.;changed[roots,a]=1.
        profiles.append(dict(name=f'action-{a}',policies=policy_document(queries,changed)['policies']))
    # The profile evaluator intentionally uses its format-1 profile transport
    # with an exact format-3 batch source. No format-2 batch is relabelled in place.
    save(profile_path,dict(format=1,context_source=queries['context_source'],batch_source=labelled_path.read_text(),profiles=profiles))
    cache.check_batch(labelled)
    invoke('hu_sampled_profile_allin_evaluation_v1',[context_path,labelled_path,profile_path,native_path])
    native=json.loads(native_path.read_text())
    assert native['format']==2 and native['terminal_estimator']==ESTIMATOR
    assert native['postflop_outcomes']=='sampled-board'
    assert [p['name'] for p in native['profiles']]==[p['name'] for p in profiles]
    count=len(batch['deals']);assert all(len(p['deals'])==count for p in native['profiles'])
    values={p['name']:np.array([d['values'][0] for d in p['deals']]) for p in native['profiles']}
    actions=np.stack([values[f'action-{a}'] for a in range(4)],axis=1);baseline=values['baseline']
    classes=[hand_class(d[:2]) for d in batch['deals']];mixes=np.array([byclass[c] for c in classes])
    error=float(np.max(np.abs(np.sum(actions*mixes,axis=1)-baseline)))
    context=json.loads(queries['context_source']);stack=context['config']['stack'];dead=context['dead_money']
    assert error<1e-9 and np.max(np.abs(actions[:,0]+context['nodes'][0]['invested'][0]))<1e-12
    assert np.all(actions>=-stack-1e-10) and np.all(actions<=stack+dead+1e-10)
    summary=dict(format=2,terminal_estimator=ESTIMATOR,allin_cache_sha256=cache.sha256,
        policy_input='unlabelled visible queries',postflop_outcomes='sampled-board',
        classes=classes,action_values=actions.tolist(),baseline_values=baseline.tolist(),root_probabilities=mixes.tolist(),
        maximum_root_mixture_error=error,zero_own_reach_observations=int(np.count_nonzero(support==0)),
        maximum_forward_cashflow_error=native['maximum_forward_cashflow_error'],
        maximum_conservation_error=native['maximum_conservation_error'],
        artifacts={p.name:sha(p) for p in (raw_path,labelled_path,query_path,profile_path,native_path)})
    save(folder/'summary.json',summary)
    return summary
