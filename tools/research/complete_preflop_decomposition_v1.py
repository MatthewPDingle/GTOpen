"""Checked fixed-context preflop reach; no postflop value prediction or sampling."""
import math
import numpy as np
from board_root_components_v1 import validate_context

DECISIONS=(0,3,6,9,12)
POSTFLOP=(2,5,8)
ALLIN=(11,14)
FOLDS=(1,4,7,10,13)


def tables(context,export,matrix):
    validate_context(context)
    if len(export['rows'])!=699:raise ValueError('Complete supported catalog required')
    probabilities=np.asarray(export['cuda_policy'],dtype=np.float64)
    if probabilities.shape!=(699,4):raise ValueError('Complete exported policies required')
    masses=(matrix.bb_mass,matrix.btn_mass); found=set(); result={}
    for node in DECISIONS:
        # Unsupported incoming BTN classes have exactly zero joint mass. A legal
        # placeholder is used only to permit dense arrays; it is never sampled.
        result[node]=np.zeros((169,4)); result[node][:,0]=1.
    for index,row in enumerate(export['rows']):
        node,cls,actor=row['node'],row['hand_class'],row['actor']
        if (node not in DECISIONS or type(cls) is not int or not 0<=cls<169 or row['index']!=index
                or context['nodes'][node]['actor']!=actor or masses[actor][cls]<=0 or (node,cls) in found):
            raise ValueError('Invalid, unsupported or duplicate exported row')
        result[node][cls]=probabilities[index];found.add((node,cls))
    expected={(n,h) for n in DECISIONS for h in range(169) if masses[context['nodes'][n]['actor']][h]>0}
    if found!=expected:raise ValueError('Missing supported policy rows')
    for node,p in result.items():validate_table(context,node,p)
    return result


def validate_table(context,node,p):
    arity=len(context['nodes'][node]['children'])
    if p.shape!=(169,4) or not np.isfinite(p).all() or np.any(p<0) or np.any(p[:,arity:]):
        raise ValueError('Finite legal policy required')
    if np.max(abs(p.sum(1)-1.))>1e-12:raise ValueError('Normalized policy required')


def reaches(context,policies):
    validate_context(context)
    if set(policies)!=set(DECISIONS):raise ValueError('All five preflop decisions required')
    if len(context['nodes'])!=15:raise ValueError('Fixed complete tree required')
    result={0:np.ones((169,169))}
    for node in DECISIONS:
        p=np.asarray(policies[node],dtype=np.float64);validate_table(context,node,p)
        if node not in result:raise ValueError('Decision missing its parent reach')
        actor=context['nodes'][node]['actor']
        for action,child in enumerate(context['nodes'][node]['children']):
            if child in result:raise ValueError('Non-tree topology')
            factor=p[:,action,None] if actor==0 else p[None,:,action]
            result[child]=result[node]*factor
    terminal=sum(result[i] for i in (*POSTFLOP,*ALLIN,*FOLDS))
    if len(result)!=15 or np.max(abs(terminal-1.))>1e-12:
        raise ValueError('Preflop terminal mass is not one')
    return result


def integrated_preflop(context,matrix,reach):
    """Exact matrix integration of class-constant paths; no matrix.evaluate scope expansion."""
    validate_context(context)
    entries=np.zeros((169,169,2))
    for node in FOLDS:
        entries+=matrix.mass[:,:,None]*reach[node][:,:,None]*np.asarray(context['nodes'][node]['leaf']['utilities'])
    for node in ALLIN:
        entries[:,:,0]+=reach[node]*matrix.bb
        entries[:,:,1]+=reach[node]*matrix.btn
    return np.asarray([math.fsum(entries[:,:,p].ravel()) for p in (0,1)])


def physical_preflop(context,reach,bb_class,btn_class,equity):
    """Independent terminal chip ledger at one physical pair, excluding postflop."""
    if not 0<=equity<=1:raise ValueError('Conditional all-in equity required')
    result=np.zeros(2)
    for i in FOLDS:
        n=context['nodes'][i]; winner=n['winner']
        payoff=np.asarray([-n['invested'][p]+(n['pot'] if p==winner else 0.) for p in (0,1)])
        if not np.array_equal(payoff,n['leaf']['utilities']):raise ValueError('Fold cashflow mismatch')
        result+=reach[i][bb_class,btn_class]*payoff
    for i in ALLIN:
        n=context['nodes'][i];rake=n['pot']*context['rake_fraction']
        if context['rake_cap']>0:rake=min(rake,context['rake_cap'])
        payoff=-np.asarray(n['invested'])+(n['pot']-rake)*np.asarray([equity,1.-equity])
        result+=reach[i][bb_class,btn_class]*payoff
    return result
