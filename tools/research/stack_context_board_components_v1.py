"""Derive BB root value terms from each context's actual preflop topology."""
import math
import numpy as np
from board_fixed_policy_values_v1 import evaluate


def routes(context):
    nodes=context['nodes']
    if context.get('schema')!='hu-context-v1' or context['positions']!=['BB','BTN']:
        raise ValueError('BB/BTN continuation context required')
    root=nodes[0]
    if (root['actor']!=0 or len(root['children'])!=4
            or [a['kind'] for a in root['actions']]!=['fold','call','raise','jam']):
        raise ValueError('BB fold/call/raise/jam root required')
    jam=nodes[root['children'][3]]
    if (jam['actor']!=1 or len(jam['children'])!=2
            or [a['kind'] for a in jam['actions']]!=['fold','call']):
        raise ValueError('Terminal BTN fold/call response required')
    called=nodes[jam['children'][1]]
    if called['leaf']['type']!='showdown' or nodes[jam['children'][0]]['leaf']['type']!='fold':
        raise ValueError('Original all-in reference endpoints required')
    seen={0};paths=[]
    def walk(index,action,path):
        if type(index) is not int or not 0<=index<len(nodes) or index in seen:
            raise ValueError('Acyclic unique preflop nodes required')
        seen.add(index);node=nodes[index];children=node['children']
        if children:
            if node['actor'] not in (0,1) or not 2<=len(children)<=4 or node['leaf'] is not None:
                raise ValueError('Supported native action menu required')
            for a,child in enumerate(children):walk(child,action,path+[(index,a)])
        else:
            kind=node['leaf']['type']
            if kind not in ('fold','showdown','postflop'):raise ValueError('Unknown native leaf')
            if kind=='fold':
                values=np.asarray(node['leaf']['utilities'],dtype=float)
                if values.shape!=(2,) or not np.isfinite(values).all():raise ValueError('Finite fold payoffs required')
            if kind=='showdown' and any(node[k]!=called[k] for k in ('pot','invested','leaf')):
                raise ValueError('All-in endpoints have different economics; a separate exact matrix is required')
            paths.append(dict(node=index,root_action=action,path=path,kind=kind))
    for action,child in enumerate(root['children']):walk(child,action,[])
    if len(seen)!=len(nodes) or nodes[root['children'][0]]['leaf']['type']!='fold':
        raise ValueError('Complete rooted preflop topology required')
    return paths


def path_reach(context,preflop,path):
    reach=[np.ones(169),np.ones(169)]
    for node,action in path:
        record=context['nodes'][node];p=np.asarray(preflop[node],dtype=float)
        if (p.shape!=(169,len(record['children'])) or not np.isfinite(p).all()
                or np.any(p<0) or np.max(abs(p.sum(1)-1))>1e-12):
            raise ValueError('Normalized class-constant preflop policies required')
        reach[record['actor']]*=p[:,action]
    return reach


def exact_terms(context,matrix,preflop):
    if np.any(matrix.bb_mass<=0):raise ValueError('Every root class requires incoming support')
    result=np.zeros((169,4))
    for route in routes(context):
        if route['kind']=='postflop':continue
        own,opponent=path_reach(context,preflop,route['path'])
        if route['kind']=='fold':
            value=(matrix.mass@opponent)*context['nodes'][route['node']]['leaf']['utilities'][0]
        else:value=matrix.bb@opponent
        result[:,route['root_action']]+=own*value/matrix.bb_mass
    if not np.isfinite(result).all():raise ValueError('Nonfinite exact preflop terms')
    return result


def board_terms(context,tree,policies,preflop,weights,classes,total_pair_mass,class_mass):
    classes=[np.asarray(c,dtype=int) for c in classes];weights=[np.asarray(w,dtype=float) for w in weights]
    class_mass=np.asarray(class_mass,dtype=float)
    if (len(classes)!=2 or len(weights)!=2 or not np.isfinite(total_pair_mass) or total_pair_mass<=0
            or class_mass.shape!=(169,) or not np.isfinite(class_mass).all()
            or np.any(class_mass<=0) or abs(class_mass.sum()-1)>1e-12):
        raise ValueError('Original pair and BB class masses required')
    if any(c.shape!=w.shape or np.any(c<0) or np.any(c>=169) or not np.isfinite(w).all() or np.any(w<0) for c,w in zip(classes,weights)):
        raise ValueError('Native hand classes and nonnegative entry weights required')
    paths=[r for r in routes(context) if r['kind']=='postflop']
    if len(tree['branches'])!=len(policies):raise ValueError('One policy map per native branch required')
    branches={b['branch']:(b,p) for b,p in zip(tree['branches'],policies)}
    if len(branches)!=len(tree['branches']) or set(branches)!={r['node'] for r in paths}:
        raise ValueError('Every actual postflop branch required exactly once')
    by_hand=np.zeros((len(weights[0]),4))
    for route in paths:
        own,opponent=path_reach(context,preflop,route['path'])
        value=evaluate(tree,*branches[route['node']],[weights[0],weights[1]*opponent[classes[1]]])[0]
        by_hand[:,route['root_action']]+=own[classes[0]]*value
    result=np.column_stack([np.bincount(classes[0],weights=weights[0]*by_hand[:,a],minlength=169) for a in range(4)])
    result*=math.comb(52,5)/math.comb(48,5)/total_pair_mass/class_mass[:,None]
    if not np.isfinite(result).all():raise ValueError('Nonfinite board terms')
    return result
