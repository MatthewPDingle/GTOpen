"""CPU-only synthetic model/checkpoint transport and inference control."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import copy
import json
from pathlib import Path
import time
import numpy as np
import board_training_checkpoint_v1 as ck
import sampled_visible_hybrid_checkpoint_v1 as storage
from board_training_policy_v1 import probabilities, average
from board_root_accumulator_v1 import BoardRootRegrets, digest
from board_root_accumulator_control_v1 import fixture
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir, ARRAYS
from weighted_preflop_table_v1 import build, Table
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_physical_bank_v1 import histories
from sampled_physical_root_evaluation_v1 import hand_class
from board_fixed_policy_control_v1 import ROOT, OUT, read, save, sha
import weighted_training_checkpoint_v1 as legacy

PREFIX='board-training-checkpoint-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    began=time.monotonic()
    cp=OUT/'bb-context-candidate.json';mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    cat=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    qp=Path('S:/GTOpen-research/board-precision-repeat-v1/private-000/queries.json')
    assert not STORE.exists();STORE.mkdir()
    source=cp.read_text();matrix=AllinMatrix(read(mp),source);catalog=read(cat)
    root=BoardRootRegrets(context_sha256=storage.digest(source),matrix_sha256=sha(mp),
        entry_mass=matrix.bb_mass,physical_budget=512,boards_per_generation=4,board_seed=9280201)
    config=copy.deepcopy(read(OUT/'weighted-stratified-study-v1-registration.json')['arms'][0]['config'])
    config.update(policy_type=ck.POLICY_TYPE,board_root=root.config,reservoir_capacity=64)
    args=dict(context_source=source,catalog_source=cat.read_text(),matrix_sha256=sha(mp),
              entry_mass=matrix.btn_mass,root_config=root.config)
    ck.require_config(config)
    paths=[cp,mp,cat,qp,OUT/'weighted-stratified-study-v1-registration.json',
        *[ROOT/'tools/research'/name for name in ['board_training_checkpoint_v1.py',
          'board_training_policy_v1.py','board_training_checkpoint_control_v1.py',
          'board_root_accumulator_v1.py','board_root_accumulator_control_v1.py']]]
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs={str(p):sha(p) for p in paths},config=config,store=str(STORE),
        scope='Synthetic targets and synthetic network parameters on native observation fixtures. No training or native board estimates.',
        maximum_seconds=90,gpu_used=False,production_modified=False))
    exact=ExactBtnRegrets(storage.digest(source),matrix.btn_mass)
    initial=ck.write_model(STORE,0,storage.uniform_networks(),[1.,1.],[None,None],root,exact,**args)
    state=dict(completed_iterations=0,sampler=ClassStratifiedDeals(source,seed=config['sampler_seed']),
        action_rng=np.random.default_rng(config['action_seed']),
        reservoirs=[WeightedPhysicalReservoir(64,p,config['reservoir_seeds'][p],source) for p in (0,1)],
        played_bank=[],next_model=initial,root_regret_state=root,exact_btn_state=exact)
    refs=[ck.save_checkpoint(STORE,state,config,**args)]
    original_queries=read(qp);obs=original_queries['observations']
    assert original_queries['context_source']==source and any(o['own_history'] for o in obs)
    query=dict(context_source=source,observations=obs)
    # Deliberately conflicting table targets exercise override ordering.
    chosen=[]
    for player in (0,1):
        for phase in (0,1):
            chosen.extend([o for o in obs if o['actor']==player and int(o['phase']>0)==phase][:12])
    assert chosen and all(any(o['actor']==p and o['phase']>0 for o in chosen) for p in (0,1))
    models=[];maximum_error=0.;rejected=[]
    for generation in range(2):
        previous=state['next_model'];model=ck.model_document(STORE,previous,**args);models.append(model)
        roots=state['root_regret_state'];ex=state['exact_btn_state']
        root_p=roots.probabilities(np.full((169,4),.25));calls=ex.probabilities(np.full((169,2),.5))[:,1]
        x=matrix.evaluate(root_p,calls)
        ex.step(generation+1,calls,x['btn_jam_mass'],x['btn_fold_entries'],x['btn_call_entries'])
        plan,e,_,q,_=fixture(roots,generation)
        e.update(model_sha256=previous['sha256'],played_policy_sha256=digest(root_p.tolist()))
        for row in e['draws']:row['model_sha256']=previous['sha256']
        roots.step(plan,e,played_policy=root_p,exact_terms=q)
        state['sampler'].sample(512);state['action_rng'].integers(0,2**63,size=8)
        for o in chosen:
            values=[10. if a==1 else -3. for a in range(o['n'])]
            state['reservoirs'][o['actor']].add(o,values,generation+1,deal_weight=1.25)
        nets=storage.uniform_networks()
        for net in nets:net['b2']=[float(generation+1+a) for a in range(4)]
        current=ck.write_model(STORE,generation+1,nets,[1.,1.],
            [build(r,source) for r in state['reservoirs']],roots,ex,**args)
        state.update(completed_iterations=generation+1,played_bank=[*state['played_bank'],previous],next_model=current)
        refs.append(ck.save_checkpoint(STORE,state,config,**args))
        restored=ck.restore_checkpoint(STORE,refs[-1],config,**args)
        assert restored['sampler'].checkpoint()==state['sampler'].checkpoint()
        assert restored['root_regret_state'].plan()==roots.plan()
        assert restored['exact_btn_state'].document()==ex.document()
        assert restored['action_rng'].bit_generator.state==state['action_rng'].bit_generator.state
        for a,b in zip(restored['reservoirs'],state['reservoirs']):
            assert a.summary()==b.summary() and a.rng.bit_generator.state==b.rng.bit_generator.state
            assert all(np.array_equal(getattr(a,k),getattr(b,k)) for k in ARRAYS)
        current_model=ck.model_document(STORE,current,**args)
        actual,coverage=probabilities(query,current_model,device='cpu',**{k:v for k,v in args.items() if k!='context_source'})
        expected=np.zeros_like(actual)
        for i,o in enumerate(obs):
            row=np.arange(generation+1,generation+1+o['n'],dtype=float);expected[i,:o['n']]=row/row.sum()
        for t in current_model['preflop_tables']:expected,_=Table(t,source).apply(obs,expected)
        root_prob=roots.probabilities(np.full((169,4),.25));exact_prob=ex.probabilities(np.full((169,2),.5))
        jam_hi=json.loads(source)['nodes'][0]['children'][3]+1
        for i,o in enumerate(obs):
            lo=int(o['lo']);c=hand_class([lo&63,(lo>>6)&63])
            if int(o['hi'])==1:expected[i]=root_prob[c]
            elif int(o['hi'])==jam_hi and ex.reach[c]>0:expected[i]=[*exact_prob[c],0.,0.]
        error=float(np.max(abs(actual-expected)));maximum_error=max(maximum_error,error);assert error<1e-12
        assert coverage['board_root_rows']>0 and coverage['exact_btn_rows']>0
    # Current generation 2 is deliberately not part of the played average.
    weights=np.tile([1.,2.],(2,1));kw={k:v for k,v in args.items() if k!='context_source'}
    avg,reach=average(query,models,completed_iterations=2,weights_by_player=weights,guard=lambda:None,device='cpu',**kw)
    pp=[probabilities(query,m,device='cpu',**kw)[0] for m in models];history=histories(obs)
    scalar=np.zeros_like(avg);den=np.zeros(len(obs))
    for i,o in enumerate(obs):
        for g in range(2):
            w=float(g+1)
            for j,a in history[i]:w*=pp[g][j,a]
            den[i]+=w
            for a in range(o['n']):scalar[i,a]+=w*pp[g][i,a]
        if den[i]:scalar[i]/=den[i]
        else:scalar[i,:o['n']]=1./o['n']
    error=float(np.max(abs(avg-scalar)));assert error<1e-12 and np.max(abs(reach-den))<1e-12
    maximum_error=max(maximum_error,error)
    # Exercise all independent RNGs and reservoir replacement after recovery.
    resumed=ck.restore_checkpoint(STORE,refs[-1],config,**args)
    assert state['sampler'].sample(512)==resumed['sampler'].sample(512)
    assert np.array_equal(state['action_rng'].integers(0,2**63,32),resumed['action_rng'].integers(0,2**63,32))
    for i in range(256):
        o=chosen[i%len(chosen)]
        for st in (state,resumed):st['reservoirs'][o['actor']].add(o,[float(i+a) for a in range(o['n'])],3,deal_weight=.75)
    for a,b in zip(state['reservoirs'],resumed['reservoirs']):
        assert all(np.array_equal(getattr(a,k),getattr(b,k)) for k in ARRAYS)
        assert a.rng.bit_generator.state==b.rng.bit_generator.state
    def rejects(name,call):
        try:call()
        except (ValueError,KeyError,TypeError):rejected.append(name)
        else:raise AssertionError('Accepted '+name)
    final_model=ck.model_document(STORE,state['next_model'],**args)
    rejects('old model reader',lambda:legacy.validate_model(final_model,**{k:v for k,v in args.items() if k!='root_config'}))
    rejects('old checkpoint reader',lambda:legacy.restore_checkpoint(STORE,refs[-1],config,**{k:v for k,v in args.items() if k!='root_config'}))
    bad=copy.deepcopy(final_model);bad['generation']=1
    rejects('wrong generation',lambda:ck.validate_model(bad,**args))
    bad=copy.deepcopy(final_model);bad['board_root_state']['regret_sums'][0][0]+=1
    rejects('changed root',lambda:ck.validate_model(bad,**args))
    badconfig=copy.deepcopy(config);badconfig['board_root']['board_seed']+=1
    rejects('changed board seed',lambda:ck.restore_checkpoint(STORE,refs[-1],badconfig,**dict(args,root_config=badconfig['board_root'])))
    badstate=ck.restore_checkpoint(STORE,refs[-1],config,**args);badstate['played_bank'].append(badstate['next_model'])
    rejects('unplayed model in bank',lambda:ck.validate_state(STORE,badstate,config,**args))
    rejects('incomplete sampler boundary',lambda:ck.save_checkpoint(STORE,state,config,**args))
    # Unpublished interrupted work cannot alter the last immutable checkpoint.
    save(STORE/'interrupted-generation.json',dict(complete=False,generation=3))
    check=ck.restore_checkpoint(STORE,refs[-1],config,**args)
    assert check['completed_iterations']==2 and check['next_model']==state['next_model']
    for p,h in read(rp)['inputs'].items():assert sha(p)==h,p
    seconds=time.monotonic()-began;assert seconds<90
    result=dict(passed=True,registration_sha256=sha(rp),maximum_policy_or_average_error=maximum_error,
        observations=len(obs),checkpoints=refs,negative_checks=rejected,seconds=seconds,
        chance_reservoir_and_action_recovery=True,synthetic_targets=True,synthetic_networks=True,
        gpu_used=False,training_admitted=False,accuracy_qualified=False,production_modified=False)
    save(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result))


if __name__=='__main__':main()
