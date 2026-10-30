"""Physical fixed-policy EV transport/control; not a new poker strength test."""
import copy
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from hu_sampled_neural_residual_diagnostic_20260922 import ROOT, OUT, sha, save
from sampled_batch_protocol_v2 import policy_document
from sampled_evaluation_intervals_v1 import Plan, PairedEvaluation
from loopback_research_validation import idle

PREFIX = 'sampled-profile-evaluation-v1'


def main():
    assert idle() and psutil.virtual_memory().available >= 20_000_000_000
    prior_path = OUT / 'sampled-physical-bank-bridge-v1-result.json'
    prior = json.loads(prior_path.read_text()); assert prior['passed']
    for name, digest in prior['artifacts'].items(): assert sha(ROOT/name)==digest, name
    query_path = OUT / 'sampled-physical-bank-bridge-v1-queries.json'
    bank_path = OUT / 'sampled-physical-bank-bridge-v1-policies.json'
    queries = json.loads(query_path.read_text()); bank = json.loads(bank_path.read_text())
    context = OUT / 'bb-context-candidate.json'
    batch = ROOT / 'target/research-sampled/sampled-physical-checkpoint-v1/initial-2/batch.json'
    assert context.read_text()==queries['context_source'] and batch.read_text()==queries['batch_source']
    bounds_path = OUT / 'sampled-evaluation-v1-poker-bounds.json'
    bounds = json.loads(bounds_path.read_text())
    exe = ROOT / 'target/release/examples/hu_sampled_profile_evaluation.exe'
    paths = [Path(__file__), prior_path, query_path, bank_path, context, batch, bounds_path, exe]
    paths += [ROOT/'tools/research'/p for p in (
        'hu_sampled_neural_residual_diagnostic_20260922.py', 'sampled_batch_protocol_v2.py',
        'sampled_evaluation_intervals_v1.py', 'loopback_research_validation.py')]
    paths += [ROOT/'crates/solver/examples'/p for p in ('hu_sampled_profile_evaluation.rs',
        'research_sampled/state.rs','research_sampled/poker_reference_v1.rs',
        'research_sampled/observation_v1.rs','research_sampled/batch_queries_v1.rs')]
    frozen = {p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    regpath = OUT/(PREFIX+'-registration.json')
    save(regpath, dict(inputs=frozen, maximum_seconds=180, no_gpu=True,
        checks='Reverse fixed-policy expectation versus independent forward actual-investment accounting, chip/rake conservation, root model-mixture equality, analytic root fold, paired differences, invalid transports.',
        profile_names=['average','model00','model01','model10','model11','root_fold','root_call_checks','root_jam_call','replace_player0','replace_player1'],
        tolerance=1e-10,
        scope='Implementation qualification using the already observed eight-deal checkpoint fixture and tiny unqualified models. No new held-out poker evaluation or best-response claim.',
        production_modified=False))
    started=time.monotonic()
    def guard():
        assert time.monotonic()-started<180 and idle() and psutil.virtual_memory().available>=20_000_000_000
    def run(path,destination,valid=True):
        guard()
        result=subprocess.run([str(exe),str(context),str(batch),str(path),str(destination)],
                              cwd=ROOT,capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
        if valid: assert result.returncode==0,result.stderr[-3000:]
        else: assert result.returncode!=0 and not destination.exists()
    obs=queries['observations']; owners=np.array([o['actor'] for o in obs])
    models=np.asarray(bank['models']); averaged=np.asarray(bank['average'])
    assert models.shape[0]==2
    profiles=[('average',averaged)]
    for p0 in (0,1):
        for p1 in (0,1): profiles.append((f'model{p0}{p1}',np.where(owners[:,None]==0,models[p0],models[p1])))
    root=next(i for i,o in enumerate(obs) if o['phase']==0 and int(o['hi'])==1)
    assert obs[root]['n']==4
    root_fold=averaged.copy(); root_call=averaged.copy(); root_jam=averaged.copy()
    for i,o in enumerate(obs):
        if o['phase']==0 and int(o['hi'])==1:
            root_fold[i]=[1.,0,0,0]; root_call[i]=[0,1.,0,0]; root_jam[i]=[0,0,0,1.]
        if o['phase']>0:
            root_call[i]=[1.,0,0,0]  # check at every reached non-facing node
        if o['phase']==0 and int(o['hi'])==13:
            assert o['n']==2; root_jam[i]=[0,1.,0,0]
    profiles += [('root_fold',root_fold),('root_call_checks',root_call),('root_jam_call',root_jam)]
    for player in (0,1):
        profiles.append((f'replace_player{player}',np.where(owners[:,None]==player,models[1],averaged)))
    document=dict(format=1,context_source=queries['context_source'],batch_source=queries['batch_source'],
                  profiles=[dict(name=name,policies=policy_document(queries,p)['policies']) for name,p in profiles])
    transport=OUT/(PREFIX+'-policies.json'); save(transport,document)
    native_path=OUT/(PREFIX+'-native-result.json'); run(transport,native_path)
    native=json.loads(native_path.read_text())
    values={r['name']:np.array([d['values'] for d in r['deals']]) for r in native['profiles']}
    assert len(values)==10 and all(v.shape==(8,2) for v in values.values())
    weights=bank['weights_by_player']; mixed=np.zeros((8,2))
    for p0 in (0,1):
        for p1 in (0,1): mixed += weights[0][p0]/sum(weights[0])*weights[1][p1]/sum(weights[1])*values[f'model{p0}{p1}']
    mixture_error=float(np.abs(mixed-values['average']).max()); assert mixture_error<1e-10
    assert np.max(np.abs(values['root_fold']-[-1.,1.5]))<1e-12
    for name,policy_values in values.items():
        for player in (0,1):
            assert np.all(policy_values[:,player]>=bounds['utility_bounds'][player][0]-1e-10)
            assert np.all(policy_values[:,player]<=bounds['utility_bounds'][player][1]+1e-10)
    byname={p['name']:p for p in native['profiles']}
    assert all(abs(d['expected_rake']-.225)<1e-12 for d in byname['root_call_checks']['deals'])
    assert all(abs(d['expected_rake']-2.)<1e-12 for d in byname['root_jam_call']['deals'])
    plan=Plan(-398.5,398.5,('replace_player0','replace_player1'),(8,))
    paired=[]
    for player in (0,1):
        name=f'replace_player{player}'; differences=values[name][:,player]-values['average'][:,player]
        acc=PairedEvaluation(plan,name)
        for x in differences: acc.add_difference(float(x))
        interval=acc.interval(); assert abs(interval['mean']-float(differences.mean()))<1e-12
        paired.append(dict(name=name,deal_differences=differences.tolist(),interval_plumbing_only=interval))
    assert np.array_equal(values['average']-values['average'],np.zeros((8,2)))
    # Reuse one disposable path for deliberate invalid inputs; preserve results,
    # not entire duplicated policies, for each mutation.
    work=ROOT/'target/research-sampled'/PREFIX; work.mkdir(exist_ok=False)
    rejected=[]
    for variant in range(6):
        bad=copy.deepcopy(document)
        if variant==0: bad['context_source']+=' '
        elif variant==1: bad['batch_source']+=' '
        elif variant==2: bad['profiles'][1]['name']='average'
        elif variant==3: bad['profiles'][0]['policies'][0]['actor']=1-bad['profiles'][0]['policies'][0]['actor']
        elif variant==4: bad['profiles'][0]['policies'][0]['probabilities']=[.5,.5,.5,.5]
        else: bad['profiles'][0]['policies'].pop()
        path=work/f'bad{variant}.json'; save(path,bad); run(path,work/f'bad{variant}-result.json',False);rejected.append(variant)
    for name,digest in frozen.items(): assert sha(ROOT/name)==digest,name
    result=dict(passed=True,inputs_verified=len(frozen),registration_sha256=sha(regpath),
        physical_deals=8,profiles=10,maximum_root_model_mixture_ev_error=mixture_error,
        maximum_forward_cashflow_error=native['maximum_forward_cashflow_error'],
        maximum_conservation_error=native['maximum_conservation_error'],
        analytic_root_fold_verified=True,passive_and_allin_rake_verified=True,
        invalid_transports_rejected=len(rejected),paired_plumbing=paired,seconds=time.monotonic()-started,
        artifacts={p.relative_to(ROOT).as_posix():sha(p) for p in (transport,native_path)},
        warning='The eight previously inspected fixture deals are not an independent poker evaluation. Intervals only exercise the integration. A tested deviation is not an upper bound on exploitability.',
        physical_poker_convergence_qualified=False,production_modified=False)
    save(OUT/(PREFIX+'-result.json'),result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('artifacts','paired_plumbing')}))


if __name__=='__main__':main()
