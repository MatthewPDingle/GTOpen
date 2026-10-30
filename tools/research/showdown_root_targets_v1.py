"""Separately typed, research-only BB root target control; no policy input change."""
import hashlib
import json
import math
import copy
from action_integrated_root_targets_v1 import digest

METHOD='showdown-controlled-bb-root-targets-v1'
COEFFICIENT_METHOD='frozen-all-bank-showdown-root-coefficients-v1'


def derive(source,queries,policies,scores,coefficients):
    if source.get('method')!='action-integrated-bb-root-targets-v1' or source.get('format')!=1:
        raise ValueError('Original action-integrated root targets required')
    if source['queries_sha256']!=digest(queries) or source['policies_sha256']!=digest(policies):
        raise ValueError('Original target/query/policy binding required')
    if queries['context_source']!=policies['context_source'] or queries['batch_source']!=policies['batch_source']:
        raise ValueError('Context and physical batch must match')
    context=hashlib.sha256(queries['context_source'].encode()).hexdigest()
    if (coefficients.get('format')!=1 or coefficients.get('method')!=COEFFICIENT_METHOD
            or coefficients.get('context_sha256')!=context):
        raise ValueError('Explicit fixed coefficients for this context required')
    weights=coefficients['call_raise_coefficients']
    if len(weights)!=169 or any(len(r)!=2 or any(not math.isfinite(x) for x in r) for r in weights):
        raise ValueError('169 finite call/raise coefficient pairs required')
    batch=json.loads(queries['batch_source']);cards=batch['deals'];counts=batch['allin_counts']
    if scores.get('format')!=1 or json.loads(scores['input_source'])!={'format':1,'deals':cards}:
        raise ValueError('Showdown scores must bind the identical physical deals')
    outcomes=scores['twice_bb_share'];rows=source['bb_root_corrections']
    if not len(cards)==len(counts)==len(outcomes)==len(rows) or not cards:
        raise ValueError('One count, score and root target per physical deal required')
    corrected=[]
    for i,(deal,count,outcome,row) in enumerate(zip(cards,counts,outcomes,rows)):
        if (row['deal']!=i or type(outcome)!=int or outcome not in (0,1,2)
                or count['private_cards']!=deal[:4] or count['boards']!=1712304
                or any(type(count[k])!=int or count[k]<0 for k in ('wins','ties','losses','boards'))
                or sum(count[k] for k in ('wins','ties','losses'))!=count['boards']):
            raise ValueError('Checked complete-board counts and original deal ordering required')
        a,b=deal[:2];high,low=sorted((a//4,b//4),reverse=True)
        hand=high*14 if high==low else high*13+low if a%4==b%4 else low*13+high
        if row['hand_class']!=hand:raise ValueError('Native hand class does not match cards')
        q=row['query'];obs=queries['observations'][q]
        if obs['hi']!='1' or obs['actor']!=0 or obs['n']!=4:
            raise ValueError('BB initial four-action root only')
        probability=policies['policies'][q]['probabilities'];old=row['action_values']
        if (len(probability)!=4 or len(old)!=4 or any(not math.isfinite(z) for z in old)
                or any(not math.isfinite(z) or z<0 for z in probability) or abs(math.fsum(probability)-1)>1e-12):
            raise ValueError('Finite original values and normalized played policy required')
        old_mean=math.fsum(p*v for p,v in zip(probability,old))
        if abs(old_mean-row['derived_root_value'])>1e-9 or any(abs(v-old_mean-z)>1e-9 for v,z in zip(old,row['advantages'])):
            raise ValueError('Original played-policy centering must remain valid')
        mean=(count['wins']+.5*count['ties'])/count['boards'];x=.5*outcome-mean
        value=[old[0],old[1]-weights[hand][0]*x,old[2]-weights[hand][1]*x,old[3]]
        expected=math.fsum(p*v for p,v in zip(probability,value));adv=[v-expected for v in value]
        assert value[0]==old[0] and value[3]==old[3] and abs(math.fsum(p*z for p,z in zip(probability,adv)))<1e-9
        corrected.append(dict(row,action_values=value,derived_root_value=expected,advantages=adv,
                              original_action_values=old,centered_showdown_feature=x))
    result=copy.deepcopy(source)
    result.update(method=METHOD,identity=dict(source['identity'],root_estimator=METHOD,control_coefficients_sha256=digest(coefficients)),
        source_integrated_audit_sha256=digest(source),score_document_sha256=digest(scores),
        bb_root_corrections=corrected,
        scope='Root-only zero-mean showdown target correction with pre-frozen class coefficients. Fold and exact initial jam unchanged; not a new policy input or an exact call/raise value.')
    return result
