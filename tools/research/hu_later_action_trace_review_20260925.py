"""Independent scalar readback of trace controls, including reconstructed transports."""
import hashlib
import json
import math
from pathlib import Path
import time

OUT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
PREFIX = 'later-action-trace-control-v1'


def read(path): return json.loads(Path(path).read_bytes())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value): return (json.dumps(value,separators=(',', ':'),allow_nan=False)+'\n').encode()


def main():
    started=time.monotonic(); rp=OUT/f'{PREFIX}-registration.json'; resultp=OUT/f'{PREFIX}-result.json'
    output=OUT/f'{PREFIX}-independent-review.json'; assert not output.exists()
    reg=read(rp); result=read(resultp)
    assert result['passed'] and result['registration_sha256']==sha(rp)
    for path,h in {**reg['inputs'],**result['artifacts']}.items(): assert sha(path)==h,path
    trial=read(reg['trials'][1]['result']); store=Path(reg['store'])
    counts=0; worst=0.; replayed=0
    fixtures=[(store/f'iteration-{it:04d}',Path(trial['store'])/f'iteration-{it:04d}/batch-00') for it in reg['iterations']]
    fixtures.append((store/'exhaustive-uniform',store/'exhaustive-uniform'))
    for target,source in fixtures:
        trace=read(target/'trace.json'); old=read(source/'updates.json'); policy=read(source/'policies.json')
        assert trace['sampled_records']==old['records'] and trace['sampled_roots']==old['roots']
        assert trace['context_source']==policy['context_source']
        assert trace['batch_source']==policy['batch_source']==(source/'batch.json').read_text()
        nodes=[]
        for did,d in enumerate(trace['traces']):
            assert d['deal_index']==did
            m={n['query']:n for n in d['nodes']}; assert len(m)==len(d['nodes']);nodes.append(m)
        assert len(nodes)==len(json.loads(trace['batch_source'])['deals'])
        positives=[i for i,r in enumerate(old['records']) if r[2]>0]
        assert [t['record'] for t in trace['conditional_targets']]==positives
        roots=[i for i,r in enumerate(old['records']) if policy['policies'][r[0]]['hi']=='1']
        assert len(roots)==len(old['roots'])==2*len(nodes) and roots[0]==0
        group=0
        for t in trace['conditional_targets']:
            i=t['record']
            while group+1<len(roots) and i>=roots[group+1]:group+=1
            did,actor=divmod(group,2)
            qi,updater,n,_=old['records'][i]
            assert t['deal']==did and t['updater']==updater==actor and t['query']==qi
            row=nodes[did][qi]; assert row['actor']==actor and row['n']==n
            probs=policy['policies'][qi]['probabilities']
            value=math.fsum(probs[a]*row['action_values'][a][actor] for a in range(n))
            worst=max(worst,abs(value-row['values'][actor]))
            for a in range(4):
                expected=row['action_values'][a][actor]-value if a<n else 0.
                worst=max(worst,abs(expected-t['advantages'][a]))
            counts+=1
        replayed+=len(old['records'])
        if target!=source:
            oldfull=read(source/'integrated-native.json')['profiles'][0]
            assert oldfull['name']=='baseline' and len(oldfull['deals'])==len(nodes)
            for d,e in zip(trace['traces'],oldfull['deals']):
                assert d['deal_index']==e['deal_index'] and d['values']==e['values']
    f=store/'exhaustive-uniform'; trace=read(f/'trace.json'); policy=read(f/'policies.json')
    nodes=trace['traces'][0]['nodes']; baseline=trace['traces'][0]['values']; summary=read(f/'summary.json')
    pairs=[(n,a) for n in nodes for a in range(n['n'])]
    checked=0; worst_conditional=0.; worst_delta=0.
    for audit in summary['interventions']:
        start=audit['start']; assert start==checked
        part=pairs[start:start+audit['count']]
        profiles=[dict(name='baseline',policies=policy['policies'])]
        for j,(node,a) in enumerate(part):
            changed=list(policy['policies']);qi=node['query']
            changed[qi]=dict(changed[qi],probabilities=[float(b==a) for b in range(4)])
            profiles.append(dict(name=f'force-{start+j}',policies=changed))
        transport=dict(format=1,context_source=policy['context_source'],batch_source=policy['batch_source'],profiles=profiles)
        assert hashlib.sha256(encoded(transport)).hexdigest()==audit['profiles_sha256']
        op=f/f'intervention-{start:05d}-values.json'; assert sha(op)==audit['native_sha256']
        native=read(op); assert native['maximum_forward_cashflow_error']<1e-10 and native['maximum_conservation_error']<1e-10
        assert len(native['profiles'])==len(part)+1 and native['profiles'][0]['deals'][0]['values']==baseline
        for j,((node,a),p) in enumerate(zip(part,native['profiles'][1:])):
            assert p['name']==f'force-{start+j}' and node['reach']>0
            for player in range(2):
                delta=p['deals'][0]['values'][player]-baseline[player]
                expected=node['reach']*(node['action_values'][a][player]-node['values'][player])
                err=abs(delta-expected);worst_delta=max(worst_delta,err)
                worst_conditional=max(worst_conditional,err/node['reach'])
        checked+=len(part)
    assert checked==len(pairs)==summary['actions'] and len(nodes)==summary['nodes']
    assert worst<1e-10 and worst_delta<1e-10 and worst_conditional<1e-7
    review=dict(passed=True,registration_sha256=sha(rp),result_sha256=sha(resultp),reader_sha256=sha(__file__),
        original_records_replayed=replayed,targets_reconstructed=counts,forced_actions_reconstructed=checked,
        maximum_target_error=worst,maximum_delta_error=worst_delta,maximum_conditional_error=worst_conditional,
        seconds=time.monotonic()-started,accuracy_qualified=False,
        scope='Independent scalar readback and exact reconstruction of released intervention transports. Does not rerun native poker traversal or prove improved training.')
    with output.open('xb') as stream: stream.write(encoded(review))
    print(json.dumps(review))


if __name__=='__main__': main()
