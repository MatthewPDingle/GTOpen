"""Actual board targets for the separately typed experimental training model.

No environment or GPU settings are changed here. CPU workers may limit their
own math threads. This module does not fit networks or publish checkpoints.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from board_training_policy_v1 import probabilities
from board_training_checkpoint_v1 import validate_model
from board_root_accumulator_v1 import TARGET, digest
from sampled_visible_features_bulk_v1 import features
from sampled_physical_bank_v1 import histories
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS, CLASSES
from preflop_allin_matrix_v1 import AllinMatrix
from board_root_components_v1 import validate_context, exact_terms, board_terms


def text_sha(source):return hashlib.sha256(source.encode()).hexdigest()


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



def policy_rows(tree, model, mode):
    result = []
    for branch in tree['branches']:
        obs = []; spans = []
        for i, node in enumerate(branch['nodes']):
            if node['kind'] == 0:
                spans.append((i, len(obs), len(node['observations'])))
                obs.extend(node['observations'])
        if mode == 'saved-network':
            x = features(obs).astype(np.float64); actors = np.array([o['actor'] for o in obs])
            scores = np.zeros((len(obs), 4))
            for player, net in enumerate(model['networks']):
                ids = np.flatnonzero(actors == player); y = x[ids]
                for layer, shape in enumerate(((64,302), (64,64), (4,64))):
                    w = np.asarray(net[f'w{layer}'], dtype=np.float32).astype(float).reshape(shape)
                    b = np.asarray(net[f'b{layer}'], dtype=np.float32).astype(float)
                    y = y @ w.T + b
                    if layer < 2: y = np.maximum(y, 0.)
                scores[ids] = y
            arity = np.array([o['n'] for o in obs]); legal = np.arange(4)[None, :] < arity[:, None]
            p = np.maximum(scores, 0.) * legal; z = p.sum(1); live = z > 0
            p[live] /= z[live, None]
            zero = np.flatnonzero(~live)
            p[zero, np.argmax(np.where(legal, scores, -np.inf), axis=1)[zero]] = 1.
        else:
            p = np.zeros((len(obs), 4))
            for i, o in enumerate(obs): p[i, :o['n']] = 1. / o['n']
        result.append({i: p[start:start+count, :len(branch['nodes'][i]['children'])]
                       for i, start, count in spans})
    return result



def prepare(*,model_source,context_source,catalog_source,physical_catalog_source,matrix_source,root_config):
    context=json.loads(context_source);validate_context(context)
    model=json.loads(model_source);matrix_sha=text_sha(matrix_source)
    matrix=AllinMatrix(json.loads(matrix_source),context_source)
    args=dict(catalog_source=catalog_source,matrix_sha256=matrix_sha,entry_mass=matrix.btn_mass,root_config=root_config)
    validate_model(model,context_source=context_source,**args)
    if not np.array_equal(np.asarray(root_config['entry_mass']),matrix.bb_mass):
        raise ValueError('Board-root entry population differs from exact original population')
    pre,error=preflop_policy(json.loads(physical_catalog_source),context,model,args)
    sampler=PhysicalDeals(context_source,mode='full_deck',seed=0)
    recipe=dict(method='typed-board-model-widened-f32-network-f64-inference-v1',
        model_sha256=text_sha(model_source),context_sha256=text_sha(context_source),
        catalog_sha256=text_sha(catalog_source),physical_catalog_sha256=text_sha(physical_catalog_source),
        matrix_sha256=matrix_sha,provider_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    return dict(model=model,context=context,pre=pre,sampler=sampler,class_mass=matrix.bb_mass,
        exact=exact_terms(matrix,pre),recipe=recipe,root_config=root_config,
        maximum_preflop_suit_difference=error)


def request(prepared,board):
    if (len(board)!=5 or any(type(c) is not int or not 0<=c<52 for c in board)
            or len(set(board))!=5 or board[:3]!=sorted(board[:3])):
        raise ValueError('Canonical flop and ordered turn/river required')
    legal=~np.isin(PAIRS,board).any(1)
    ids=[np.flatnonzero(legal&(prepared['sampler'].weights[p]>0)) for p in (0,1)]
    return dict(board=board,hands=[PAIRS[i].tolist() for i in ids]),ids


def draw_record(prepared,tree,*,tree_sha256,draw_index,board):
    req,ids=request(prepared,board)
    if tree.get('format')!=1 or tree['board']!=board or tree['hands']!=req['hands']:
        raise ValueError('Native tree has changed board or incomplete physical support')
    post=policy_rows(tree,prepared['model'],'saved-network')
    weights=[prepared['sampler'].weights[p,i] for p,i in enumerate(ids)]
    values=board_terms(tree,post,prepared['pre'],weights,[CLASSES[i] for i in ids],
        prepared['sampler'].masses[0],prepared['class_mass'])
    return dict(draw_index=draw_index,board=board,model_sha256=prepared['recipe']['model_sha256'],
        tree_sha256=tree_sha256,policy_recipe_sha256=digest(prepared['recipe']),
        values=values.tolist(),values_sha256=digest(values.tolist()))


def generation_evidence(state,prepared,plan,records):
    if (state.config!=prepared['root_config'] or plan!=state.plan()
            or prepared['model']['generation']!=state.steps):
        raise ValueError('Complete board generation must use its played model and own plan')
    return dict(format=1,method=TARGET,generation=state.steps,plan_sha256=digest(plan),
        context_sha256=prepared['recipe']['context_sha256'],matrix_sha256=prepared['recipe']['matrix_sha256'],
        played_policy_sha256=digest(prepared['pre'][0].tolist()),
        exact_terms_sha256=digest(prepared['exact'].tolist()),
        model_sha256=prepared['recipe']['model_sha256'],draws=records)
