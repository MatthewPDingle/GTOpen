"""Fixed-data fitting curves using the qualified ordered CUDA gradient."""
import time
import numpy as np
from sampled_visible_initialization_v1 import fresh_visible_network
from sampled_visible_features_bulk_v1 import features
from sampled_visible_gradient_graph_fit_v1 import gradient_tensor
from weighted_visible_objective_v1 import PreparedWeightedObjective
from weighted_training_graph_fit_v2 import capture_stream


def configure():
    import torch
    torch.set_num_threads(1)
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False


class Evaluation:
    """Direct raw-row loss, including variation hidden by grouped target means."""
    def __init__(self,raw,scale,guard):
        import torch
        guard()
        self.x=torch.as_tensor(features([dict(active_features=a.tolist()) for a in raw['active']]),device='cuda')
        self.targets=raw['values'].astype(np.float64)/scale
        self.weights=raw['weights'].astype(np.float64)
        self.arity=raw['arity'];self.phase=raw['active'][:,15].astype(int)-135
        self.scale=scale
        self.legal=np.arange(4)[None,:]<self.arity[:,None]
        assert set(self.phase)<=set(range(4))

    def __call__(self,model,guard):
        import torch
        prediction=[]
        with torch.no_grad():
            for start in range(0,len(self.x),8192):
                guard();prediction.append(model(self.x[start:start+8192]).cpu().numpy().astype(np.float64))
        prediction=np.concatenate(prediction)
        assert np.isfinite(prediction).all()
        numerator=((prediction-self.targets)**2*self.legal*self.weights[:,None]).sum(axis=1)
        zero=(self.targets**2*self.legal*self.weights[:,None]).sum(axis=1)
        denominator=self.weights*self.arity
        output={}
        for name,mask in [('all',np.ones(len(self.x),dtype=bool)),('postflop',self.phase>0)]+[
                (name,self.phase==i) for i,name in enumerate(('preflop','flop','turn','river'))]:
            if not np.any(mask):continue
            den=float(denominator[mask].sum());loss=float(numerator[mask].sum()/den)
            output[name]=dict(rows=int(mask.sum()),source_weight=float(self.weights[mask].sum()),
                legal_target_mass=den,normalized_loss=loss,raw_scale_loss=loss*self.scale**2,
                normalized_zero_loss=float(zero[mask].sum()/den))
        return output


def curve(data,seed,checkpoints,callback,guard,*,chunk_size=4096,captured=True):
    import torch
    assert sorted(set(checkpoints))==list(checkpoints) and min(checkpoints)>0
    started=time.monotonic();guard()
    model=fresh_visible_network(seed).cuda()
    prepared=PreparedWeightedObjective(data,'cuda',dtype=torch.float32,guard=guard)
    optimizer=torch.optim.Adam(model.parameters(),lr=.003)
    if captured:
        stream=capture_stream(torch);stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            for _ in range(2):
                model.zero_grad(set_to_none=True);gradient_tensor(prepared,model,chunk_size)
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
            model.zero_grad(set_to_none=True)
            total=prepared.objective(model,chunk_size,guard,backward=True)
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


def control(data,seed,guard):
    """Real-feature multichunk control: captured curve vs ordinary ordered fit."""
    import torch
    fixture={k:v for k,v in data.items()}
    for key in ('active','arity','masses','targets','counts'):fixture[key]=data[key][:257].copy()
    fixture['denominator']=float(np.dot(fixture['masses'],fixture['arity']))
    fixture['variance']=0.;fixture['examples']=257
    snapshots=[];records=[]
    def callback(model,record):
        snapshots.append({k:v.detach().cpu().clone() for k,v in model.state_dict().items()})
        records.append(record)
    curve(fixture,seed,(16,32,64),callback,guard,chunk_size=128)
    captured=snapshots;snapshots=[];captured_records=records;records=[]
    curve(fixture,seed,(16,32,64),callback,guard,chunk_size=128,captured=False)
    difference=max(float((a[k]-b[k]).abs().max()) for a,b in zip(captured,snapshots) for k in a)
    loss_difference=max(abs(a['normalized_training_loss']-b['normalized_training_loss'])
        for a,b in zip(captured_records,records))
    assert difference<1e-5 and loss_difference<1e-5,(difference,loss_difference)
    # Independent CPU/GPU first-gradient check using the same weighted objective.
    gradients=[];losses=[]
    for device in ('cpu','cuda'):
        model=fresh_visible_network(seed).to(device)
        prepared=PreparedWeightedObjective(fixture,device,dtype=torch.float32,guard=guard)
        model.zero_grad(set_to_none=True)
        losses.append(prepared.objective(model,128,guard,backward=True))
        gradients.append([p.grad.detach().cpu().clone() for p in model.parameters()])
    gradient_difference=max(float((a-b).abs().max()) for a,b in zip(*gradients))
    assert gradient_difference<1e-5 and abs(losses[0]-losses[1])<1e-5
    # Exercise raw-row and street-specific scoring without using holdout data.
    raw=dict(active=fixture['active'],arity=fixture['arity'],
        values=fixture['targets']*fixture['scale'],weights=fixture['masses'])
    evaluation=Evaluation(raw,fixture['scale'],guard)
    scored=evaluation(model,guard)
    cpu=fresh_visible_network(seed)
    with torch.no_grad():
        predicted=cpu(torch.from_numpy(features([dict(active_features=a.tolist()) for a in raw['active']]))).numpy().astype(float)
    legal=np.arange(4)[None,:]<raw['arity'][:,None]
    direct=float(((predicted-fixture['targets'])**2*legal*raw['weights'][:,None]).sum()/fixture['denominator'])
    evaluation_difference=abs(direct-scored['all']['normalized_loss'])
    phase_rows=[value for key,value in scored.items() if key in ('preflop','flop','turn','river')]
    phase_total=sum(v['normalized_loss']*v['legal_target_mass'] for v in phase_rows)/sum(v['legal_target_mass'] for v in phase_rows)
    assert evaluation_difference<1e-5 and abs(phase_total-scored['all']['normalized_loss'])<1e-12
    return dict(passed=True,real_visible_inputs=257,steps=64,checkpoints=[16,32,64],chunk_size=128,
        maximum_curve_parameter_difference=difference,maximum_curve_loss_difference=loss_difference,
        maximum_cpu_gpu_gradient_difference=gradient_difference,cpu_gpu_loss_difference=abs(losses[0]-losses[1]),
        direct_evaluation_cpu_gpu_difference=evaluation_difference,street_weighted_loss_identity=True)
