"""Publish re-raise coverage, without changing any fitted probabilities.

The editor's after-entry grid is a conditional response, not a cold defense
range. Keep sample coverage and the mixture of entry/depth/price auditable.
Only aggregate counts are published; sessions and hands remain local.
"""
import collections
import importlib.util
import json
from pathlib import Path

spec=importlib.util.spec_from_file_location('response_audit',Path(__file__).with_name('responses.py'))
resp=importlib.util.module_from_spec(spec);spec.loader.exec_module(resp)


def summarize(sessions):
    result={}
    for bucket in ['cold_reraise','reraise']:
        cs=resp.opening.arrays(resp.subset(sessions,bucket))
        result[bucket]=[dict(players=n,role=r,decisions=int(c.sum()),
            observed_classes=int((c.sum(1)>0).sum()),zero_observation_classes=int((c.sum(1)==0).sum()),
            actions=dict(zip(['fold','call','raise'],map(int,c.sum(0))))) for (n,r),c in sorted(cs.items())]
    contexts=collections.defaultdict(collections.Counter)
    for s in sessions:
        for key,value in s['counts'].items():
            if key.startswith('reraise_context/'):
                key,action=key.split('|');contexts[key][action]+=value
    if not contexts:raise ValueError('Re-run analyze.py for re-raise context counters')
    result['contexts']=[dict(context=k.split('/')[1:],actions=dict(v)) for k,v in sorted(contexts.items())]
    assert sum(sum(v.values()) for v in contexts.values()) == sum(r['decisions'] for b in ['reraise','cold_reraise'] for r in result[b])
    result['interpretation']='Conditional frequencies. After-entry responses pool prior calls/raises, raise depths and prices. Zero-observation hand classes are inferred from other contexts, not directly measured.'
    result['price_definition']='Incremental call / (pot before acting + incremental call), before rake: low <=15%, medium <=30%, high >30%. Coverage audit only; not model inputs.'
    return result


def publish(source,out):
    source=json.loads(Path(source).read_text(encoding='utf-8'))
    out=Path(out);report=json.loads((out/'NL10.json').read_text(encoding='utf-8'))
    assert source['audit']==report['audit']
    evidence=summarize(source['sessions']);report['reraise_coverage']=evidence
    model=report['model'];notes=model['stats']['dataset']['response_notes']
    for bucket in ['cold_reraise','reraise']:
        for r in evidence[bucket]:
            notes[f"{bucket}_{r['players']}_{r['role']}"]=(f"Direct coverage: {r['decisions']:,} decisions across {r['observed_classes']}/169 hand classes at this table size and position. "
                + (f"{r['zero_observation_classes']} classes have no direct observations; their probabilities are pooled estimates." if r['zero_observation_classes'] else 'All classes are represented, but sparse cells still borrow pooled estimates.'))
    for name,value in [('NL10.json',report),('models.json',[model])]:
        (out/name).write_text(json.dumps(value,indent=1,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    publish(a.input,a.out)
