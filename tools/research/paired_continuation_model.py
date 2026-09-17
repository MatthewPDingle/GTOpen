"""Conservative, zero-sum residual fitted to connected postflop contexts."""
import numpy as np
import shallow_native_feedback as prior

native = prior.native
pilot = prior.pilot


def base(c):
    spr = c['case']['stack'] / c['case']['pot']
    if spr < 1:
        return native.hybrid(c)
    c = dict(c, base_x=c['x'].copy(), base_names=list(c['names']))
    return native.previous.prior.network.predict(c, prior.read(native.previous.prior.MODEL))


def features(c):
    return native.fit.features(c)


def predict(c, model):
    b = base(c)
    d = features(c) @ np.array(model['coefficients'])
    spr = c['case']['stack'] / c['case']['pot']
    # Shared scaling keeps both legal bounds and pair-weighted pot conservation.
    limits = np.where(d > 0, (1 + spr - b) / np.maximum(d, 1e-100),
                      (b + spr) / np.maximum(-d, 1e-100))
    s = max(0., min(1., float(limits.min())))
    v = b + s*d
    assert abs((v*c['mass']).sum()-1) < 1e-8
    assert v.min() >= -spr-1e-8 and v.max() <= 1+spr+1e-8
    return v


def pack(tree, cases, rows):
    v, info, reaches = native.tree_values(tree)
    terms, parent, den = prior.action.terminal_coefficients(tree, info)
    p = v[parent['children']]/den
    xdelta = np.zeros((169, 18))
    ref = {key: p[2]-p[1] for key in ['direct', 'corrected']}
    gains = np.zeros((2,169)); contexts = []
    for case in cases:
        c = native.fit.aggregate(case, rows[case['id']])
        c['base'] = base(c); c['features'] = features(c)
        assert abs(c['base'][0]*case['pot']-info[case['node']]['gross']).max() < 2e-5
        contexts.append(c)
        term = terms[case['node']]; action = term['action']-1
        sign = 1 if action == 1 else -1
        coef = term['coefficient']
        xdelta += sign*coef[:,None]*case['pot']*c['features'][0]
        for key in ref:
            ref[key] = ref[key] + sign*coef*(case['pot']*c[key][0]-info[case['node']]['gross'])
        gains[action] += coef*case['pot']*c['gain'][0]
    sigma = np.array(parent['sigma']).reshape(-1,169)
    qualified = (sigma[1] >= .0001) & (sigma[2] >= .0001) & (gains.max(axis=0) <= .025)
    counts, _ = pilot.matrices(); r = reaches[parent['id']]
    joint = counts*(r[1]/pilot.COMBOS)[:,None]*(r[0]/pilot.COMBOS)[None,:]
    mass = joint.sum(axis=1)/joint.sum()
    return dict(tree=tree, contexts=contexts, base_delta=p[2]-p[1], reference_delta=ref,
                action_x=xdelta, qualified=qualified, mass=mass, terms=terms, info=info,
                parent=parent, values=v, denominator=den, sigma=sigma, gains=gains)


def fit(packs, penalty, action_weight):
    xs=[]; ys=[]; ws=[]
    for p in packs:
        for c in p['contexts']:
            w=c['mass']*c['qualified']; w/=w.sum()
            xs.append(c['features'].reshape(-1,18))
            ys.append((c['corrected']-c['base']).ravel())
            ws.append(w.ravel()/len(p['contexts'])/len(packs))
        w=p['mass']*p['qualified']; w/=w.sum()
        # Five bb is a fixed reference scale, not a per-sample fitted divisor.
        xs.append(p['action_x']/5)
        ys.append((p['reference_delta']['corrected']-p['base_delta'])/5)
        ws.append(action_weight*w/len(packs))
    x=np.concatenate(xs); y=np.concatenate(ys); w=np.concatenate(ws)
    coef=np.linalg.solve(x.T@(w[:,None]*x)+penalty*np.eye(18),x.T@(w*y))
    return dict(coefficients=coef.tolist(), penalty=penalty, action_weight=action_weight,
                production_enabled=False)


def action_prediction(p, model):
    delta=p['base_delta'].copy()
    for c in p['contexts']:
        case=c['case']; term=p['terms'][case['node']]
        sign=1 if term['action']==2 else -1
        delta+=sign*term['coefficient']*case['pot']*(predict(c,model)[0]-c['base'][0])
    return delta


def score(p, model):
    pred=action_prediction(p,model); w=p['mass']*p['qualified']; w/=w.sum()
    action={key:float(w@abs(pred-truth)) for key,truth in p['reference_delta'].items()}
    baseline={key:float(w@abs(p['base_delta']-truth)) for key,truth in p['reference_delta'].items()}
    leaves=[]
    for c in p['contexts']:
        w=c['mass']*c['qualified']; w/=w.sum()
        leaves.append(dict(case=c['case']['id'],
            candidate={key:float((w*abs(predict(c,model)-c[key])).sum()) for key in ['direct','corrected']},
            baseline={key:float((w*abs(c['base']-c[key])).sum()) for key in ['direct','corrected']}))
    return dict(action_mae_bb=action, baseline_action_mae_bb=baseline, leaves=leaves,
                qualified_classes=int(p['qualified'].sum()),qualified_mass=float(p['mass']@p['qualified']))
