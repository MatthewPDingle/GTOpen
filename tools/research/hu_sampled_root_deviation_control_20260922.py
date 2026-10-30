"""Root-action values and train/test-separated class-deviation plumbing."""
import copy
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from hu_sampled_neural_residual_diagnostic_20260922 import ROOT, OUT, sha, save
from loopback_research_validation import idle
from sampled_batch_protocol_v2 import policy_document
from sampled_root_deviation_v1 import learn, differences

PREFIX='sampled-root-deviation-v1'


def main():
    assert idle()
    prerequisite=OUT/'sampled-profile-evaluation-v1-result.json';prior=json.loads(prerequisite.read_text());assert prior['passed']
    for name,digest in prior['artifacts'].items():assert sha(ROOT/name)==digest,name
    query_path=OUT/'sampled-physical-bank-bridge-v1-queries.json'
    bank_path=OUT/'sampled-physical-bank-bridge-v1-policies.json'
    context=OUT/'bb-context-candidate.json';batch=ROOT/'target/research-sampled/sampled-physical-checkpoint-v1/initial-2/batch.json'
    exe=ROOT/'target/release/examples/hu_sampled_profile_evaluation.exe'
    paths=[Path(__file__),prerequisite,query_path,bank_path,context,batch,exe]
    paths += [ROOT/'tools/research'/n for n in ('sampled_root_deviation_v1.py','sampled_batch_protocol_v2.py',
        'hu_sampled_neural_residual_diagnostic_20260922.py','loopback_research_validation.py')]
    paths += [ROOT/'crates/solver/examples'/n for n in ('hu_sampled_profile_evaluation.rs',
        'research_sampled/state.rs','research_sampled/poker_reference_v1.rs',
        'research_sampled/observation_v1.rs','research_sampled/batch_queries_v1.rs')]
    frozen={p.relative_to(ROOT).as_posix():sha(p) for p in paths};regpath=OUT/(PREFIX+'-registration.json')
    save(regpath,dict(inputs=frozen,maximum_seconds=120,minimum_training_deals=1,
        selection='Training indices 0..3, evaluation indices 4..7 of the previously inspected eight-deal fixture. Separate synthetic checks cover response freezing and sparse fallback.',
        checks='Per-deal root-policy mixture identity for all four actions with frozen downstream play; disjoint sample-ID enforcement; class-only response selection; unchanged baseline fallback.',
        scope='Implementation control only. Neither the inspected fixture split nor synthetic values establish fresh held-out poker strength.',
        no_gpu=True,production_modified=False))
    started=time.monotonic();work=ROOT/'target/research-sampled'/PREFIX;work.mkdir(exist_ok=False)
    queries=json.loads(query_path.read_text());bank=json.loads(bank_path.read_text());obs=queries['observations']
    assert context.read_text()==queries['context_source'] and batch.read_text()==queries['batch_source']
    policy=np.asarray(bank['average']);profiles=[('baseline',policy)]
    roots=[i for i,o in enumerate(obs) if o['phase']==0 and int(o['hi'])==1]
    assert roots and all(obs[i]['n']==4 and obs[i]['actor']==0 for i in roots)
    for action in range(4):
        changed=policy.copy();changed[roots]=0.;changed[roots,action]=1.
        profiles.append((f'root_action_{action}',changed))
    transport=dict(format=1,context_source=queries['context_source'],batch_source=queries['batch_source'],
        profiles=[dict(name=name,policies=policy_document(queries,p)['policies']) for name,p in profiles])
    profile_path=work/'profiles.json';save(profile_path,transport);native_path=OUT/(PREFIX+'-native-result.json')
    run=subprocess.run([str(exe),str(context),str(batch),str(profile_path),str(native_path)],cwd=ROOT,
        timeout=60,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    assert run.returncode==0,run.stderr[-3000:]
    native=json.loads(native_path.read_text());values={p['name']:np.array([d['values'] for d in p['deals']]) for p in native['profiles']}
    actions=np.stack([values[f'root_action_{a}'][:,0] for a in range(4)],axis=1);baseline=values['baseline'][:,0]
    assert np.max(np.abs(actions[:,0]+1.))<1e-12
    deals=json.loads(batch.read_text())['deals'];classes=[];mixes=[]
    # Before any public card, suit canonicalization makes same-class private
    # observations identical. Extract the frozen baseline root policy by class.
    byclass={}
    def hand_class(cards):
        a,b=cards;lo,hi=sorted((a//4,b//4))
        return hi*13+lo if a%4==b%4 or hi==lo else lo*13+hi
    assert hand_class([48,44])==167 and hand_class([48,45])==155 and hand_class([48,49])==168
    for i in roots:
        lo=int(obs[i]['lo']);cards=[lo&63,(lo>>6)&63];c=hand_class(cards)
        if c in byclass:assert np.max(np.abs(byclass[c]-policy[i]))<1e-12
        byclass[c]=policy[i]
    for d in deals:
        c=hand_class(d[:2]);classes.append(c);mixes.append(byclass[c])
    mixture_error=float(np.max(np.abs((np.array(mixes)*actions).sum(axis=1)-baseline)));assert mixture_error<1e-10
    response=learn([f'fixture-{i}' for i in range(4)],classes[:4],actions[:4],baseline[:4],minimum_training_deals=1)
    test=differences(response,[f'fixture-{i}' for i in range(4,8)],classes[4:],actions[4:],baseline[4:])
    response_path=OUT/(PREFIX+'-response.json');save(response_path,response)
    # Known synthetic values prove frozen choices do not maximize test outcomes.
    toy=learn(['train0','train1','train2'],[1,1,2],[[0,4],[0,2],[9,0]],[0,0,0],minimum_training_deals=2)
    assert toy['actions'][1]==1 and toy['actions'][2]==-1
    toy_test=differences(toy,['test0','test1'],[1,2],[[10,-5],[20,0]],[1,3])
    assert np.array_equal(toy_test,[-6,0]) # Preserve an unfavorable held-out result.
    failures=0
    operations=[lambda:differences(toy,['train0'],[1],[[0,1]],[0]),
        lambda:learn(['x','x'],[1,1],[[0,1],[1,0]],[0,0],minimum_training_deals=1),
        lambda:learn(['x'],[169],[[0,1]],[0],minimum_training_deals=1),
        lambda:learn(['x'],[1],[[float('nan'),1]],[0],minimum_training_deals=1),
        lambda:learn(['x'],[1],[[0,1]],[0],minimum_training_deals=0),
        lambda:differences(toy,['x'],[1],[[0,1,2]],[0])]
    bad=copy.deepcopy(toy);bad['actions'][2]=0
    operations.append(lambda:differences(bad,['x'],[2],[[0,1]],[0]))
    for operation in operations:
        try:operation()
        except ValueError:failures+=1
        else:raise AssertionError('Invalid root-response input accepted')
    assert idle() and time.monotonic()-started<120
    for name,digest in frozen.items():assert sha(ROOT/name)==digest,name
    result=dict(passed=True,inputs_verified=len(frozen),registration_sha256=sha(regpath),
        per_deal_action_values=actions.tolist(),baseline_values=baseline.tolist(),own_hand_classes=classes,
        maximum_root_mixture_error=mixture_error,root_fold_value=-1.,
        fixture_evaluation_differences=test.tolist(),synthetic_frozen_response_differences=toy_test.tolist(),
        invalid_inputs_rejected=failures,seconds=time.monotonic()-started,
        artifacts={str(p):sha(p) for p in (profile_path,native_path,response_path)},
        warning='Only plumbing is tested. Sample IDs alone do not prove independent sampling. The future real evaluation must separately freeze policy/chance/menu identities and use fresh draws.',
        bounds_best_response_above=False,physical_poker_convergence_qualified=False,production_modified=False)
    save(OUT/(PREFIX+'-result.json'),result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('artifacts','per_deal_action_values','baseline_values','own_hand_classes')}))


if __name__=='__main__':main()
