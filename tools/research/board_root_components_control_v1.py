"""Check forced call/raise board terms and exact preflop terms separately."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import json
import math
from pathlib import Path
import subprocess
import time
import numpy as np
from board_fixed_policy_control_v1 import ROOT,OUT,read,save,sha,policy_rows
from board_root_components_v1 import validate_context,exact_terms,board_terms
from weighted_training_policy_v1 import probabilities
from sampled_physical_bank_v1 import histories
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS,MASKS,CLASSES

PREFIX='board-root-components-control-v1'


def preflop_policy(catalog,context,model,args):
    rows=catalog['rows'];obs=[dict(x['observation']) for x in rows]
    indices={(x['node'],tuple(x['hand'])):i for i,x in enumerate(rows)}
    ancestors={}
    def walk(n,path):
        if not context['nodes'][n]['children']:return
        ancestors[n]=path
        for a,child in enumerate(context['nodes'][n]['children']):walk(child,path+[(n,a)])
    walk(0,[])
    for i,row in enumerate(rows):
        obs[i]['own_history']=[[indices[(n,tuple(row['hand']))],a,len(context['nodes'][n]['children'])]
            for n,a in ancestors[row['node']] if context['nodes'][n]['actor']==obs[i]['actor']]
    histories(obs)
    p,_=probabilities(dict(context_source=catalog['context_source'],observations=obs),model,device='cpu',**args)
    native_classes={tuple(h):int(c) for h,c in zip(PAIRS,CLASSES)}
    by_class={};counts={};error=0.
    for row,probability in zip(rows,p):
        n=row['node'];c=native_classes[tuple(row['hand'])];arity=len(context['nodes'][n]['children'])
        if n not in by_class:by_class[n]=np.zeros((169,arity));counts[n]=np.zeros(169,dtype=int)
        if counts[n][c]:error=max(error,float(np.max(abs(by_class[n][c]-probability[:arity]))))
        else:by_class[n][c]=probability[:arity]
        counts[n][c]+=1
    assert error<1e-12 and all(np.all(x>0) for x in counts.values())
    return by_class,error


def forward_variable(tree,post,pre,context,weights,classes,start):
    h0,h1=[np.asarray(x) for x in tree['hands']]
    compatible=(h0[:,None,0]!=h1[None,:,0])&(h0[:,None,0]!=h1[None,:,1])
    compatible&=(h0[:,None,1]!=h1[None,:,0])&(h0[:,None,1]!=h1[None,:,1])
    ranks=[np.asarray(x) for x in tree['ranks']]
    share=(ranks[0][:,None]>ranks[1][None,:]).astype(float)+.5*(ranks[0][:,None]==ranks[1][None,:])
    branches={b['branch']:(b,p) for b,p in zip(tree['branches'],post)}
    # Independent forward walk follows the context's actual child pointers.
    # Preflop fold/all-in terminals are intentionally omitted: separate exact
    # integration accounts for them under the original full private population.
    stack=[(start,None,compatible.astype(float))];values=np.zeros(compatible.shape)
    while stack:
        b,ni,reach=stack.pop()
        if ni is None:
            node=context['nodes'][b];kind=node['leaf']['type'] if node['leaf'] else None
            if kind=='postflop':stack.append((b,0,reach))
            elif kind is None:
                actor=node['actor'];p=pre[b][classes[actor]]
                for a,child in enumerate(node['children']):
                    stack.append((child,None,reach*(p[:,a,None] if actor==0 else p[None,:,a])))
            continue
        branch,policies=branches[b];node=branch['nodes'][ni]
        if node['kind']==0:
            p=policies[ni]
            for a,child in enumerate(node['children']):
                stack.append((b,child,reach*(p[:,a,None] if node['actor']==0 else p[None,:,a])))
        elif node['kind']==1:stack.append((b,node['children'][0],reach))
        else:
            invested=np.array(context['nodes'][b]['invested'])+np.array(node['put'])-branch['starting_pot']/2
            matched=min(invested);pot=2*matched+context['dead_money'];rake=pot*context['rake_fraction']
            if context['rake_cap']>0:rake=min(rake,context['rake_cap'])
            s=share if node['kind']==3 else float(node['actor']==1)
            values+=reach*(-matched+s*(pot-rake))
    return (values@weights[1])*weights[0]


def main():
    began=time.monotonic();prior_path=OUT/'board-full-support-control-v1-result.json';prior=read(prior_path)
    assert prior['passed']
    for path,digest in prior['inputs'].items():assert sha(path)==digest,path
    cp=OUT/'bb-context-candidate.json';source=cp.read_text();context=read(cp);validate_context(context)
    model_paths=[Path(p) for p in prior['inputs'] if '/objects/' in p.replace('\\','/')]
    assert len(model_paths)==1;model=read(model_paths[0])
    matrix_path=OUT/'preflop-allin-matrix-control-v1-matrix.json';matrix=AllinMatrix(read(matrix_path),source)
    cat_path=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    args=dict(catalog_source=cat_path.read_text(),matrix_sha256=sha(matrix_path),entry_mass=matrix.btn_mass)
    folder=Path('S:/GTOpen-research')/PREFIX;folder.mkdir(exist_ok=False)
    exe=ROOT/'target/release/examples/hu_preflop_visible_catalog_v1.exe'
    raw=subprocess.check_output([str(exe),str(cp)],creationflags=subprocess.CREATE_NO_WINDOW)
    physical_catalog=folder/'preflop-catalog.json';physical_catalog.write_bytes(raw)
    pre,policy_error=preflop_policy(json.loads(raw),context,model,args)
    exact=exact_terms(matrix,pre)
    # Scalar class-pair sum independently checks every exact action component.
    reference=np.zeros((169,4));reference[:,0]=-1.
    for b in range(169):
        for t in range(169):
            p3=pre[3][t];p6=pre[6][b];p9=pre[9][b];p12=pre[12][t]
            reference[b,2]+=matrix.mass[b,t]*(p3[0]*2.5+p3[2]*p6[0]*-6+p3[3]*p9[0]*-6)
            reference[b,2]+=matrix.bb[b,t]*p3[3]*p9[1]
            reference[b,3]+=matrix.mass[b,t]*p12[0]*2.5+matrix.bb[b,t]*p12[1]
        reference[b,2:]/=matrix.bb_mass[b]
    exact_error=float(np.max(abs(reference-exact)));assert exact_error<1e-10
    sampler=PhysicalDeals(source,mode='full_deck',seed=0)
    class_mass=np.bincount(CLASSES,weights=sampler.first[0],minlength=169)
    assert np.max(abs(class_mass-matrix.bb_mass))<1e-12
    tree=read('S:/GTOpen-research/board-full-support-control-v1/tree.json')
    indices={tuple(h):i for i,h in enumerate(PAIRS)}
    ids=[np.array([indices[tuple(h)] for h in hands]) for hands in tree['hands']]
    weights=[sampler.weights[p,i] for p,i in enumerate(ids)];classes=[CLASSES[i] for i in ids]
    post=policy_rows(tree,model,'saved-network')
    cases=[]
    # Known policies expose each branch and unreachable branch, in addition to
    # the saved policy. Changing only preflop probabilities needs no refit.
    variants={'saved':pre}
    for name,action,bbcall in [('btn-call',1,1),('btn-4bet-bb-call',2,1),('btn-4bet-bb-fold',2,0),('btn-fold',0,0),('btn-jam',3,1)]:
        q={n:p.copy() for n,p in pre.items()};q[3][:]=0;q[3][:,action]=1
        q[6][:]=0;q[6][:,bbcall]=1;variants[name]=q
    for name,q in variants.items():
        got=board_terms(tree,post,q,weights,classes,sampler.masses[0],class_mass)
        expected=np.zeros((169,4))
        for action,start in [(1,2),(2,3)]:
            physical=forward_variable(tree,post,q,context,weights,classes,start)
            numerator=np.bincount(classes[0],weights=physical,minlength=169)
            # Uniform q over C(52,3)*49*48 runouts; original conditional law
            # has C(48,3)*45*44 possibilities. This is the same ratio as C(n,5).
            factor=(math.comb(52,3)*49*48)/(math.comb(48,3)*45*44)
            expected[:,action]=numerator/sampler.masses[0]/class_mass*factor
        error=float(np.max(abs(got-expected)));assert error<1e-9
        assert np.all(got[:,[0,3]]==0)
        if name in ('btn-4bet-bb-fold','btn-fold','btn-jam'):assert np.all(got[:,2]==0)
        cases.append(dict(policy=name,board_component_max_error=error))
    inputs=dict(prior['inputs'])
    for p in (prior_path,Path(__file__),matrix_path,cat_path,physical_catalog,exe,
              ROOT/'crates/solver/examples/hu_preflop_visible_catalog_v1.rs',
              ROOT/'tools/research/board_root_components_v1.py',ROOT/'tools/research/weighted_training_policy_v1.py'):
        inputs[str(p)]=sha(p)
    result=dict(passed=True,cases=cases,exact_component_max_error=exact_error,
                preflop_suit_invariance_error=policy_error,preflop_physical_rows=len(json.loads(raw)['rows']),
                supported_holdings=[len(i) for i in ids],inputs=inputs,seconds=time.monotonic()-began,
                gpu_used=False,training_changed=False,production_modified=False,
                scope='One-board decomposition and exact class-pair terms; no fresh multi-board variance or playing-strength result.')
    save(OUT/f'{PREFIX}-result.json',result)
    print(json.dumps({k:result[k] for k in ('passed','cases','exact_component_max_error','preflop_suit_invariance_error','seconds')}))


if __name__=='__main__':main()
