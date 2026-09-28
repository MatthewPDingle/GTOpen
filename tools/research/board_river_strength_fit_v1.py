"""Same fitting objective with controlled redundant river inputs."""
import time
import numpy as np
from board_river_strength_features_v1 import extras, fresh_network, digest
from board_later_fit_holdout_train_v1 import Evaluation
from sampled_visible_features_bulk_v1 import features
from sampled_visible_initialization_v1 import fresh_visible_network
from sampled_visible_gradient_graph_fit_v1 import gradient_tensor
from weighted_visible_objective_v1 import PreparedWeightedObjective
from weighted_training_graph_fit_v2 import capture_stream
from board_later_error_audit_math_v1 import row_totals, totals

POT_LABELS=('under 10 bb','10-50 bb','50-100 bb','100-200 bb','200+ bb')


class RiverObjective(PreparedWeightedObjective):
    def __init__(self,data,device,*,dtype,guard,pack,arm):
        import torch
        assert digest(data['active'])==pack['active_sha256'] and digest(data['arity'])==pack['arity_sha256']
        super().__init__(data,device,dtype=dtype,guard=guard)
        self.x=torch.cat((self.x,torch.as_tensor(extras(pack,arm),dtype=dtype,device=device)),dim=1)
        assert self.x.shape==(len(data['active']),307)


def contrast_metrics(predicted,raw,scale,pack):
    mask=pack['eligible'];weights=raw['weights'].astype(np.float64)
    target=raw['values'][:,1]-raw['values'][:,0]
    estimate=scale*(predicted[:,1]-predicted[:,0]);error=weights*(target-estimate)**2
    energy=weights*target**2;pot=pack['public'][:,0]
    def summary(selected):
        mass=float(weights[selected].sum());numerator=float(error[selected].sum());zero=float(energy[selected].sum())
        return dict(rows=int(selected.sum()),source_weight=mass,squared_error_bb2=numerator,target_energy_bb2=zero,
            mse_bb2=numerator/mass if mass else None,error_relative_to_zero=numerator/zero if zero else None)
    bins=np.searchsorted([10,50,100,200],pot,side='right')
    return dict(all=summary(mask),under_50bb=summary(mask&(pot<50)),
        pots=[dict(label=name,**summary(mask&(bins==i))) for i,name in enumerate(POT_LABELS)])


class RiverEvaluation(Evaluation):
    def __init__(self,raw,scale,guard,pack,arm):
        import torch
        assert digest(raw['active'])==pack['active_sha256'] and digest(raw['arity'])==pack['arity_sha256']
        super().__init__(raw,scale,guard);self.raw=raw;self.pack=pack
        if arm!='original':self.x=torch.cat((self.x,torch.as_tensor(extras(pack,arm),device='cuda')),dim=1)
    def score(self,model,guard):
        import torch
        predicted=[]
        with torch.no_grad():
            for start in range(0,len(self.x),8192):
                guard();predicted.append(model(self.x[start:start+8192]).cpu().numpy().astype(np.float64))
        predicted=np.concatenate(predicted)
        rows=row_totals(predicted,self.raw['values'],self.raw['arity'],self.raw['weights'],self.scale)
        masks=[('all',np.ones(len(self.x),dtype=bool)),('postflop',self.phase>0)]
        masks += [(name,self.phase==i) for i,name in enumerate(('preflop','flop','turn','river'))]
        metrics={}
        for name,mask in masks:
            value=totals(rows,mask);metrics[name]=dict(rows=value['rows'],source_weight=value['source_weight'],
                legal_target_mass=value['legal_target_mass'],normalized_loss=value['normalized_loss'],
                raw_scale_loss=value['normalized_loss']*self.scale**2,
                normalized_zero_loss=value['target_energy']/value['legal_target_mass'])
        return dict(metrics=metrics,contrast=contrast_metrics(predicted,self.raw,self.scale,self.pack))


def curve(data,seed,checkpoints,callback,guard,pack,arm,*,chunk_size=4096,captured=True):
    import torch
    assert sorted(set(checkpoints))==list(checkpoints) and min(checkpoints)>0
    started=time.monotonic();guard();model=fresh_network(seed).cuda()
    prepared=RiverObjective(data,'cuda',dtype=torch.float32,guard=guard,pack=pack,arm=arm)
    optimizer=torch.optim.Adam(model.parameters(),lr=.003)
    if captured:
        stream=capture_stream(torch);stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            for _ in range(2):model.zero_grad(set_to_none=True);gradient_tensor(prepared,model,chunk_size)
        torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize();guard()
        graph=torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph,stream=stream):
            for p in model.parameters():p.grad.zero_()
            total=gradient_tensor(prepared,model,chunk_size)
        torch.cuda.synchronize()
    setup=time.monotonic()-started;fit_started=time.monotonic();callbacks=0.
    for step in range(1,max(checkpoints)+1):
        guard()
        if captured:graph.replay()
        else:
            model.zero_grad(set_to_none=True);total=prepared.objective(model,chunk_size,guard,backward=True)
        if not np.isfinite(float(total)):raise ValueError('Nonfinite training loss')
        optimizer.step()
        if step in checkpoints:
            with torch.no_grad():loss=prepared.objective(model,chunk_size,guard)+data['variance']
            assert all(bool(torch.isfinite(p).all()) for p in model.parameters())
            record=dict(step=step,normalized_training_loss=loss,raw_training_loss=loss*data['scale']**2,
                elapsed_fit_seconds=time.monotonic()-fit_started-callbacks)
            before=time.monotonic();callback(model,record);callbacks+=time.monotonic()-before
    return dict(setup_seconds=setup,fit_seconds=time.monotonic()-fit_started-callbacks,
        callback_seconds=callbacks,peak_allocated_bytes=torch.cuda.max_memory_allocated(),
        peak_reserved_bytes=torch.cuda.max_memory_reserved())


def control(data,seed,guard,catalog):
    import torch
    from board_river_strength_features_v1 import geometry,prepare_features,enumerate_cards
    phase=data['active'][:,15].astype(int)-135;eligible,_=geometry(data['active'],data['arity'],catalog)
    selections=[]
    for mask,count in [(phase==0,65),(phase==1,64),(phase==2,64),((phase==3)&~eligible,32),(eligible,32)]:
        choices=np.flatnonzero(mask);assert len(choices)>=count
        selections.extend(choices[np.linspace(0,len(choices)-1,count,dtype=int)].tolist())
    chosen=np.asarray(sorted(selections));assert len(chosen)==len(np.unique(chosen))==257
    fixture=dict(data)
    for key in ('active','arity','masses','targets','counts'):fixture[key]=data[key][chosen].copy()
    fixture.update(denominator=float(np.dot(fixture['masses'],fixture['arity'])),variance=0.,examples=257)
    packs,metadata=prepare_features({'train':fixture},catalog,guard,threads=16);pack=packs['train']
    assert int(pack['eligible'].sum())==32 and np.all(pack['extra'][~pack['eligible']]==0)
    visible=features([dict(active_features=a.tolist()) for a in fixture['active']])
    old=fresh_visible_network(seed).double();fresh=fresh_network(seed).double();initial={}
    for arm in ('geometry','strength'):
        with torch.no_grad():
            a=old(torch.as_tensor(visible,dtype=torch.float64))
            b=fresh(torch.as_tensor(np.column_stack((visible,extras(pack,arm))),dtype=torch.float64))
        initial[arm]=float((a-b).abs().max());assert initial[arm]<1e-12
    # Explicit hand calculation checks feature fractions and source-vs-target isolation.
    mask=pack['eligible'];p,c,r,total=pack['public'][mask].T
    value=pack['extra'][mask];equity=(value[:,3].astype(float)+1)/2
    assert np.max(np.abs(value[:,4]-(equity*(p+c-r)-c)/total))<1e-7
    assert np.array_equal(extras(pack,'geometry')[:,:3],extras(pack,'strength')[:,:3])
    assert np.all(extras(pack,'geometry')[:,3]==0)
    # Qualified fixture from the previous independent scalar controls.
    counts,_=enumerate_cards(np.array([[48,44,40,36,32,1,6],[1,6,32,36,40,44,48]],dtype=np.uint8),guard,16)
    assert np.array_equal(counts,[[990,0,0],[0,990,0]])
    results={}
    for arm in ('geometry','strength'):
        snapshots=[];records=[]
        def callback(model,record):
            snapshots.append({k:v.detach().cpu().clone() for k,v in model.state_dict().items()});records.append(record)
        curve(fixture,seed,(16,32,64),callback,guard,pack,arm,chunk_size=128)
        captured=snapshots;captured_records=records;snapshots=[];records=[]
        curve(fixture,seed,(16,32,64),callback,guard,pack,arm,chunk_size=128,captured=False)
        parameter_error=max(float((a[k]-b[k]).abs().max()) for a,b in zip(captured,snapshots) for k in a)
        loss_error=max(abs(a['normalized_training_loss']-b['normalized_training_loss']) for a,b in zip(captured_records,records))
        assert parameter_error<1e-5 and loss_error<1e-5
        gradients=[];losses=[]
        for device in ('cpu','cuda'):
            model=fresh_network(seed).to(device)
            objective=RiverObjective(fixture,device,dtype=torch.float32,guard=guard,pack=pack,arm=arm)
            model.zero_grad(set_to_none=True);losses.append(objective.objective(model,128,guard,backward=True))
            gradients.append([p.grad.detach().cpu().clone() for p in model.parameters()])
        gradient_error=max(float((a-b).abs().max()) for a,b in zip(*gradients))
        assert gradient_error<1e-5 and abs(losses[0]-losses[1])<1e-5
        assert float(gradients[0][0][:,302:].abs().max())>0
        raw=dict(active=fixture['active'],arity=fixture['arity'],values=fixture['targets']*fixture['scale'],weights=fixture['masses'])
        evaluation=RiverEvaluation(raw,fixture['scale'],guard,pack,arm);scored=evaluation.score(model,guard)
        with torch.no_grad():prediction=fresh_network(seed)(torch.from_numpy(np.column_stack((visible,extras(pack,arm))))).numpy().astype(float)
        cpu_contrast=contrast_metrics(prediction,raw,fixture['scale'],pack)
        contrast_error=abs(cpu_contrast['all']['mse_bb2']-scored['contrast']['all']['mse_bb2'])
        assert contrast_error<1e-3
        # Independent direct one-contrast arithmetic; never divide by arity.
        delta=raw['values'][mask,1]-raw['values'][mask,0]
        estimate=fixture['scale']*(prediction[mask,1]-prediction[mask,0]);w=raw['weights'][mask]
        assert abs(float(np.dot(w,(delta-estimate)**2)/w.sum())-cpu_contrast['all']['mse_bb2'])<1e-9
        results[arm]=dict(maximum_curve_parameter_difference=parameter_error,maximum_curve_loss_difference=loss_error,
            maximum_cpu_gpu_gradient_difference=gradient_error,cpu_gpu_loss_difference=abs(losses[0]-losses[1]),
            contrast_cpu_gpu_difference_bb2=contrast_error,new_columns_receive_gradient=True)
    return dict(passed=True,real_training_rows=257,eligible_river_rows=32,phase_rows=[65,64,64,64],
        initial_function_difference=initial,arms=results,feature_preparation=metadata,exact_fixture_counts=True,
        same_geometry_columns=True,zero_outside_eligible=True,one_contrast_denominator=True,
        heldout_loss_scored=False,final_test_features_created=False)
