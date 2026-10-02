"""CPU synthetic complete-cycle/restart and independent dense-loss controls."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import argparse
import copy
import json
import math
from pathlib import Path
import tempfile
import time
import traceback
import numpy as np
import preflop_expected_training_control_fixture_v1 as f
cp,fit=f.cp,f.fit
import preflop_expected_policy_v1 as policy
import stack_context_policy_v1 as base
import stack_context_relative_policy_v1 as relative

def independent_objective(registry,local,resources,config,actor):
    prepared=fit.prepare(registry,local,resources,player=actor,
        context_weights=config['context_weights'],preflop_fraction=config['preflop_fraction'])
    rows={tuple(key):i for i,key in enumerate(prepared['keys'])}; count=0
    expected=np.zeros_like(prepared['targets']); weights=np.zeros_like(prepared['weights']); variance=0.
    from storage_strategic_common_prior_20260920 import PAIRS,CLASSES
    classes={tuple(h):int(c) for h,c in zip(PAIRS,CLASSES)}
    for key in registry.fit_contexts:
        s=local[key]['preflop_state']; source=json.loads(resources[key]['physical_catalog_source']); index={}
        for row in source['rows']: index.setdefault((row['node'],classes[tuple(row['hand'])]),row['observation'])
        legal_mass=math.fsum(float(s.mass[actor][c])*s.specs[n]['arity'] for n in s.nodes
            if s.specs[n]['actor']==actor for c in range(169) if s.mass[actor][c]>0 and s.supported_generations[n][c]>0)
        for n in s.nodes:
            if s.specs[n]['actor']!=actor: continue
            for c in range(169):
                if not(s.mass[actor][c]>0 and s.supported_generations[n][c]>0):continue
                o=index[n,c]; row=rows[key,o['hi'],o['lo']]
                for a in range(s.specs[n]['arity']):
                    expected[row,a]=float(s.regrets[n][c,a])/float(s.config['generation_scale'])/float(s.mass[actor][c])/s.steps/float(s.context['config']['stack'])
                    weights[row,a]=config['context_weights'][key]*config['preflop_fraction']*float(s.mass[actor][c])/legal_mass
                    count+=1
        r=local[key]['reservoirs'][actor]; groups={}
        for j in range(r.size):groups.setdefault((str(int(r.keys[j,0])),str(int(r.keys[j,1]))),[]).append(j)
        denominator=math.fsum(float(r.deal_weights[j])*int(r.arity[j]) for j in range(r.size))
        for (hi,lo),ids in groups.items():
            row=rows[key,hi,lo]; total=math.fsum(float(r.deal_weights[j]) for j in ids)
            for a in range(int(r.arity[ids[0]])):
                y=math.fsum(float(r.deal_weights[j])*float(r.values[j,a]) for j in ids)/total/float(s.context['config']['stack'])
                expected[row,a]=y
                weights[row,a]=config['context_weights'][key]*(1-config['preflop_fraction'])*total/denominator
                variance+=config['context_weights'][key]*(1-config['preflop_fraction'])/denominator*math.fsum(
                    float(r.deal_weights[j])*(float(r.values[j,a])/float(s.context['config']['stack'])-y)**2 for j in ids)
    maximum=max(float(np.max(abs(expected-prepared['targets']))),float(np.max(abs(weights-prepared['weights']))))
    assert maximum<1e-12 and abs(float(weights.sum())-1)<1e-12
    assert abs(variance-prepared['within_observation_variance'])<1e-12
    for summary in prepared['contexts']:
        ids=[i for i,k in enumerate(prepared['keys']) if k[0]==summary['context_sha256']]
        pre=[i for i in ids if int(prepared['keys'][i][1])<1<<63]; post=[i for i in ids if i not in pre]
        w=config['context_weights'][summary['context_sha256']]
        assert abs(float(prepared['weights'][pre].sum())-w*config['preflop_fraction'])<1e-12
        assert abs(float(prepared['weights'][post].sum())-w*(1-config['preflop_fraction']))<1e-12
    import torch
    torch.set_num_threads(1)
    model=fit.fresh_network(477,registry.manifest['representation']['input_width']).double()
    obj=fit.PreparedExpectedObjective(prepared,'cpu',dtype=torch.float64,guard=lambda:None)
    with torch.no_grad(): prediction=model(obj.x).numpy()
    scalar=math.fsum(float(weights[i,a])*(float(prediction[i,a])-float(expected[i,a]))**2
                     for i in range(len(weights)) for a in range(4))
    got=obj.objective(model,127,lambda:None)
    assert abs(got-scalar)<1e-12 and obj.identity==prepared['objective_sha256']
    model.zero_grad();obj.objective(model,127,lambda:None,backward=True)
    actual=[p.grad.detach().clone() for p in model.parameters()]
    model.zero_grad();((model(obj.x)-obj.target).square()*obj.weight).sum().backward()
    error=max(float((a-p.grad).abs().max()) for a,p in zip(actual,model.parameters()))
    assert error<1e-12
    return dict(actor=actor,rows=len(rows),independent_legal_preflop_targets=count,maximum_target_weight_error=maximum,
        independent_loss_error=abs(got-scalar),chunked_gradient_error=error)

def main(output):
    began=time.monotonic(); cases=[]; rejected=[]
    for width,cycles in ((362,3),(387,1)):
        with tempfile.TemporaryDirectory(prefix=f'expected-cycle-{width}-',dir=output.parent) as directory:
            registry,resources,config,state=f.fixture(width,directory=directory)
            first=cp.save_checkpoint(directory,state,config,registry,resources)
            restored=cp.restore_checkpoint(directory,first,config,registry,resources)
            f.same_local(state['contexts'],restored['contexts']); assert state['played_bank']==[]
            objective_cases=[]
            for g in range(cycles):
                staged=f.stage(directory,state,registry,resources); repeated=f.stage(directory,restored,registry,resources)
                f.same_local(staged['contexts'],repeated['contexts']);assert staged['board_targets']==repeated['board_targets']
                networks=(base if width==362 else relative).uniform_networks()
                for actor,n in enumerate(networks):n['b2']=[.01*(g+1)*(actor+1),.02,.03,.04]
                receipts=f.receipts(staged,state,registry,resources,config,networks)
                if g==0:objective_cases=[independent_objective(registry,staged['contexts'],resources,config,a) for a in (0,1)]
                if width==362 and g==0:
                    previous_identity={k:cp.local_fit_identity(v) for k,v in state['contexts'].items()}
                    def refuse(label,operation):
                        try:operation()
                        except (ValueError,KeyError,TypeError,IndexError):pass
                        else:raise AssertionError('Accepted invalid '+label)
                        assert {k:cp.local_fit_identity(v) for k,v in state['contexts'].items()}==previous_identity
                        f.same_local(state['contexts'],cp.restore_checkpoint(directory,first,config,registry,resources)['contexts'])
                        rejected.append(label)
                    key=registry.fit_contexts[0]
                    def complete(s=staged,rs=receipts,c=config):
                        return cp.complete_cycle(directory,state,s,c,registry,resources,networks=networks,fit_receipts=rs)
                    mutations=[
                        ('missing-context',lambda s:s['contexts'].pop(key)),
                        ('mixed-collection-model',lambda s:s['collected_against'].update({key:'0'*64})),
                        ('missing-board',lambda s:s['board_targets'][key]['evidence']['draws'].pop()),
                        ('altered-plan',lambda s:s['board_targets'][key]['plan'].update(generation=2)),
                        ('partial-context-update',lambda s:s['contexts'][key].update(preflop_state=copy.deepcopy(state['contexts'][key]['preflop_state']))),
                        ('sampler-not-completed',lambda s:s['contexts'][key].update(sampler=copy.deepcopy(state['contexts'][key]['sampler']))),
                        ('wrong-post-iteration',lambda s:s['contexts'][key]['reservoirs'][0].iterations.__setitem__(0,2)),
                        ('preflop-row-in-post-reservoir',lambda s:s['contexts'][key]['reservoirs'][0].keys.__setitem__((0,0),1)),
                        ('altered-post-target',lambda s:s['contexts'][key]['reservoirs'][0].values.__setitem__((0,0),9)),
                        ('wrong-source-weight',lambda s:s['contexts'][key]['reservoirs'][0].deal_weights.__setitem__(0,4))]
                    for label,mutate in mutations:
                        bad=copy.deepcopy(staged);mutate(bad);refuse(label,lambda bad=bad:complete(s=bad))
                    for label,mutate in [
                        ('missing-second-fit',lambda r:r.pop()),
                        ('wrong-fit-targets',lambda r:r[1]['local_fit_identities'].update({key:'0'*64})),
                        ('wrong-objective',lambda r:r[0].update(objective_sha256='0'*64)),
                        ('wrong-actor',lambda r:r[1].update(player=0)),
                        ('wrong-fit-generation',lambda r:r[0].update(generation=2)),
                        ('wrong-shared-model',lambda r:r[0].update(collected_against='0'*64)),
                        ('wrong-network',lambda r:r[0].update(network_sha256='0'*64)),
                        ('changed-objective-mixture',lambda r:r[0].update(preflop_fraction=.5)),
                        ('changed-optimizer',lambda r:r[0].update(optimizer={})),
                        ('changed-execution-mode',lambda r:r[0].update(execution_mode='study'))]:
                        bad=copy.deepcopy(receipts);mutate(bad);refuse(label,lambda bad=bad:complete(rs=bad))
                    bad=copy.deepcopy(config);bad['contexts'][key]['sampler_seed']+=1
                    refuse('changed-initial-RNG-seed',lambda:cp.restore_checkpoint(directory,first,bad,registry,resources))
                    bad=copy.deepcopy(resources);bad[key]['physical_catalog_source']+=' '
                    refuse('changed-dense-catalog',lambda:fit.prepare(registry,staged['contexts'],bad,player=0,
                        context_weights=config['context_weights'],preflop_fraction=config['preflop_fraction']))
                    for stage in ('before-model-publication','before-checkpoint-publication'):
                        class InjectedFailure(Exception):pass
                        def inject(s,stage=stage):
                            if s==stage:raise InjectedFailure(s)
                        try:cp.complete_cycle(directory,state,staged,config,registry,resources,
                            networks=networks,fit_receipts=receipts,on_stage=inject)
                        except InjectedFailure:pass
                        else:raise AssertionError('Missing publication failure injection')
                        assert state['completed_cycles']==0 and state['played_bank']==[]
                        f.same_local(state['contexts'],cp.restore_checkpoint(directory,first,config,registry,resources)['contexts'])
                        rejected.append('publication-interruption-'+stage)
                state,reference=cp.complete_cycle(directory,state,staged,config,registry,resources,
                                                networks=networks,fit_receipts=receipts)
                restored=cp.restore_checkpoint(directory,reference,config,registry,resources)
                assert state['played_bank']==restored['played_bank'] and len(state['played_bank'])==g+1
                f.same_local(state['contexts'],restored['contexts'])
                assert all(s['preflop_state'].steps==g+1 for s in restored['contexts'].values())
                assert all(r.seen==19*(g+1) and r.size==7 for s in restored['contexts'].values() for r in s['reservoirs'])
                print(json.dumps(dict(input_width=width,completed_cycles=g+1,fitted_stacks=5)),flush=True)
            future=f.stage(directory,state,registry,resources); replay=f.stage(directory,restored,registry,resources)
            f.same_local(future['contexts'],replay['contexts']);assert future['board_targets']==replay['board_targets']
            models=[policy.read_model(directory,ref,registry,resources) for ref in restored['played_bank']]
            assert [m['generation'] for m in models]==list(range(cycles))
            assert policy.read_model(directory,restored['next_model'],registry,resources)['generation']==cycles
            cases.append(dict(input_width=width,completed_cycles=cycles,fit_depths=[20,40,100,200,400],heldout_depths=[60,150],
                restart_next_cycle_bit_identical=True,retention_overflow_exercised=True,
                played_bank_excludes_final_unplayed_model=True,objectives=objective_cases))
    result=dict(passed=True,seconds=time.monotonic()-began,cases=cases,refused_cases=rejected,inputs=f.inputs(),
        synthetic_only=True,scientific_attempt=False,native_invocations=0,gpu_used=False,
        accuracy_qualified=False,actual_training_worker_qualified=False,production_modified=False)
    with output.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2,allow_nan=False)
    print(json.dumps({k:v for k,v in result.items() if k!='inputs'},indent=2),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--result',type=Path,required=True);args=parser.parse_args()
    try:main(args.result)
    except BaseException:
        with args.result.with_name(args.result.stem+'-failure.txt').open('x',encoding='utf-8') as out:out.write(traceback.format_exc())
        raise
