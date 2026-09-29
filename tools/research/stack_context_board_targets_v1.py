"""Complete fixed-board targets using the full shared-context current policy."""
import hashlib
import json
from pathlib import Path
import numpy as np
from stack_context_current_policy_v1 import CurrentPolicy
from stack_context_inputs_v1 import digest as source_sha
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_bank_v1 import histories
from storage_strategic_common_prior_20260920 import PAIRS,CLASSES
from sampled_physical_root_evaluation_v1 import hand_class
from stack_context_board_components_v1 import routes,exact_terms,board_terms
from board_training_targets_v1 import request,generation_evidence
from board_root_accumulator_v1 import digest


def preflop_policy(catalog,context,engine):
    if catalog['context_source']!=engine.context_source:raise ValueError('Physical catalog context mismatch')
    routes(context)
    rows=catalog['rows'];obs=[dict(row['observation']) for row in rows]
    indices={(row['node'],tuple(row['hand'])):i for i,row in enumerate(rows)};ancestors={}
    if len(indices)!=len(rows):raise ValueError('Duplicate physical catalog row')
    def walk(node,path):
        if not context['nodes'][node]['children']:return
        ancestors[node]=path
        for action,child in enumerate(context['nodes'][node]['children']):walk(child,path+[(node,action)])
    walk(0,[])
    physical={tuple(hand) for hand in PAIRS}
    if (set(row['node'] for row in rows)!=set(ancestors)
            or any({tuple(row['hand']) for row in rows if row['node']==node}!=physical for node in ancestors)):
        raise ValueError('Every decision requires all 1326 physical private holdings')
    for row,o in zip(rows,obs):
        if (o['actor']!=context['nodes'][row['node']]['actor'] or o['phase']!=0
                or o['hi']!=str(row['node']+1)
                or hand_class([(int(o['lo'])>>(6*j))&63 for j in range(2)])!=hand_class(row['hand'])):
            raise ValueError('Native catalog node or private class mismatch')
        o['own_history']=[[indices[(node,tuple(row['hand']))],action,len(context['nodes'][node]['children'])]
            for node,action in ancestors[row['node']] if context['nodes'][node]['actor']==o['actor']]
    histories(obs)
    p=engine.infer(engine.prepare(dict(context_source=catalog['context_source'],observations=obs)))
    native_classes={tuple(hand):int(c) for hand,c in zip(PAIRS,CLASSES)};by_class={};counts={};error=0.
    for row,probability in zip(rows,p):
        node=row['node'];c=native_classes[tuple(row['hand'])];arity=len(context['nodes'][node]['children'])
        if node not in by_class:by_class[node]=np.zeros((169,arity));counts[node]=np.zeros(169,dtype=int)
        if counts[node][c]:error=max(error,float(np.max(abs(by_class[node][c]-probability[:arity]))))
        else:by_class[node][c]=probability[:arity]
        counts[node][c]+=1
    if error>1e-12 or any(np.any(row==0) for row in counts.values()) or set(by_class)!=set(ancestors):
        raise ValueError('Incomplete physical preflop catalog or suit-dependent policy')
    return by_class,error


def policy_rows(tree,engine):
    result=[]
    for branch in tree['branches']:
        observations=[];spans=[]
        for i,node in enumerate(branch['nodes']):
            if node['kind']==0:
                spans.append((i,len(observations),len(node['observations'])))
                observations.extend(node['observations'])
        p=engine.score_rows(engine.context_source,observations)
        result.append({i:p[start:start+count,:len(branch['nodes'][i]['children'])] for i,start,count in spans})
    return result


def prepare(*,model_source,registry,context_sha256,resources,physical_catalog_source,matrix_source):
    source=registry.source(context_sha256);context=json.loads(source);routes(context)
    if context_sha256 not in registry.fit_contexts:raise ValueError('Board training targets require a fitting context')
    args=resources[context_sha256];matrix_sha=source_sha(matrix_source)
    matrix=AllinMatrix(json.loads(matrix_source),source)
    if matrix_sha!=args['matrix_sha256'] or not np.array_equal(matrix.btn_mass,np.asarray(args['entry_mass'])):
        raise ValueError('Exact matrix and current-policy entry population disagree')
    if not np.array_equal(matrix.bb_mass,np.asarray(args['root_config']['entry_mass'])):
        raise ValueError('Exact matrix and BB board-root population disagree')
    model=json.loads(model_source);engine=CurrentPolicy(model,registry,context_sha256=context_sha256,resources=resources)
    pre,error=preflop_policy(json.loads(physical_catalog_source),context,engine)
    sampler=PhysicalDeals(source,mode='full_deck',seed=0)
    recipe=dict(method='full-shared-context-fixed-board-current-policy-v1',model_sha256=source_sha(model_source),
        context_sha256=context_sha256,registry_sha256=registry.sha256,catalog_sha256=source_sha(args['catalog_source']),
        physical_catalog_sha256=source_sha(physical_catalog_source),matrix_sha256=matrix_sha,
        provider_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    return dict(model=model,engine=engine,context=context,pre=pre,sampler=sampler,class_mass=matrix.bb_mass,
                exact=exact_terms(context,matrix,pre),recipe=recipe,root_config=args['root_config'],maximum_preflop_suit_difference=error)


def draw_record(prepared,tree,*,tree_sha256,draw_index,board):
    req,ids=request(prepared,board)
    if tree.get('format')!=1 or tree['board']!=board or tree['hands']!=req['hands']:
        raise ValueError('Native tree has different board or incomplete physical support')
    post=policy_rows(tree,prepared['engine'])
    weights=[prepared['sampler'].weights[p,i] for p,i in enumerate(ids)]
    values=board_terms(prepared['context'],tree,post,prepared['pre'],weights,[CLASSES[i] for i in ids],prepared['sampler'].masses[0],prepared['class_mass'])
    return dict(draw_index=draw_index,board=board,model_sha256=prepared['recipe']['model_sha256'],
                tree_sha256=tree_sha256,policy_recipe_sha256=digest(prepared['recipe']),values=values.tolist(),values_sha256=digest(values.tolist()))
