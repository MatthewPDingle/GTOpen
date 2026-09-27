"""Fixed BB subtree decomposition: exact preflop terms plus board contributions.

The board term is importance weighted under a uniform five-card public runout
proposal (sorted flop, ordered turn/river). No board-specific renormalization.
"""
import math
import numpy as np
from board_fixed_policy_values_v1 import evaluate


def validate_context(context):
    # This is deliberately scoped to the registered subtree, not a generic
    # preflop adapter. Refuse any action-layout or terminal-economics change.
    expected = {0:([1,2,3,12],0),3:([4,5,6,9],1),6:([7,8],0),9:([10,11],0),12:([13,14],1)}
    for i,(children,actor) in expected.items():
        if context['nodes'][i]['children'] != children or context['nodes'][i]['actor'] != actor:
            raise ValueError('Unsupported preflop topology')
    for i, values in ((1,[-1.,1.5]),(4,[2.5,-2.]),(7,[-6.,6.5]),(10,[-6.,6.5]),(13,[2.5,-2.])):
        if context['nodes'][i]['leaf']['utilities'] != values:
            raise ValueError('Unsupported fold economics')
    for i in (11,14):
        if context['nodes'][i]['leaf']['type'] != 'showdown': raise ValueError('All-in endpoint required')
    if any(context['nodes'][11][k] != context['nodes'][14][k] for k in ('invested','pot','leaf')):
        raise ValueError('All-in payouts must agree at both depths')


def exact_terms(matrix, preflop):
    mass = matrix.bb_mass
    if np.any(mass <= 0): raise ValueError('Every BB class must have positive entry mass')
    p3,p6,p9,p12 = [preflop[i] for i in (3,6,9,12)]
    for p,n in ((p3,4),(p6,2),(p9,2),(p12,2)):
        if p.shape != (169,n) or not np.isfinite(p).all() or np.any(p<0) or np.max(abs(p.sum(1)-1))>1e-12:
            raise ValueError('Class-constant normalized preflop policies required')
    out = np.zeros((169,4));out[:,0] = matrix.bb_fold
    out[:,2] = (matrix.mass @ (2.5*p3[:,0]) - 6*p6[:,0]*(matrix.mass @ p3[:,2])
                - 6*p9[:,0]*(matrix.mass @ p3[:,3]) + p9[:,1]*(matrix.bb @ p3[:,3])) / mass
    out[:,3] = (matrix.mass @ (matrix.bb_win*p12[:,0]) + matrix.bb @ p12[:,1]) / mass
    return out


def board_terms(tree, policies, preflop, weights, classes, total_pair_mass, class_mass):
    classes = [np.asarray(c,dtype=int) for c in classes]
    weights = [np.asarray(w,dtype=float) for w in weights]
    if total_pair_mass <= 0 or not np.isfinite(total_pair_mass): raise ValueError('Original joint mass required')
    class_mass = np.asarray(class_mass,dtype=float)
    if class_mass.shape != (169,) or np.any(class_mass<=0) or abs(class_mass.sum()-1)>1e-12:
        raise ValueError('Original normalized entry class mass required')
    if any(c.shape != w.shape or np.any(c<0) or np.any(c>=169) for c,w in zip(classes,weights)):
        raise ValueError('One native class per private holding required')
    branches = {b['branch']:(b,p) for b,p in zip(tree['branches'],policies)}
    if set(branches) != {2,5,8}: raise ValueError('Every postflop branch required')
    by_hand = np.zeros((len(weights[0]),4))
    by_hand[:,1] = evaluate(tree,*branches[2],weights)[0]
    p3 = preflop[3][classes[1]];p6 = preflop[6][classes[0]]
    by_hand[:,2] = evaluate(tree,*branches[5],[weights[0],weights[1]*p3[:,1]])[0]
    by_hand[:,2] += p6[:,1]*evaluate(tree,*branches[8],[weights[0],weights[1]*p3[:,2]])[0]
    # P(board | compatible private pair) / uniform q(board). Factor 20 from
    # turn/river ordering cancels, but the original class denominator remains.
    ratio = math.comb(52,5) / math.comb(48,5)
    result = np.column_stack([np.bincount(classes[0],weights=weights[0]*by_hand[:,a],minlength=169)
                              for a in range(4)])
    result *= ratio / total_pair_mass / class_mass[:,None]
    return result
