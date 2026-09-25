"""Preserved-visit replay and exhaustive one-deal intervention control, no fitting."""
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from hu_paired_continuation_support_20260925 import guard_for, launch

PREFIX = 'later-action-trace-control-v1'
STORE = Path('T:/GTOpen-research')/PREFIX
TRACE = ROOT/'target/release/examples/hu_sampled_action_trace_v1.exe'
UPDATE = ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe'
FULL = ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
ITERATIONS = (1, 26, 78)


def worker(reg):
    guard = guard_for(reg, gpu=False); guard(); started = time.monotonic()
    store = Path(reg['store']); store.mkdir(exist_ok=False)
    context = OUT/'bb-context-candidate.json'
    result = read(reg['trials'][1]['result']); rows = []
    def invoke(exe, args):
        guard()
        p = subprocess.run([str(exe), *map(str,args)], capture_output=True, text=True,
            timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        assert p.returncode == 0, p.stderr[-3000:]
        guard()
    def check_targets(trace, policies):
        worst = 0.; count = 0
        node_maps = [{n['query']: n for n in d['nodes']} for d in trace['traces']]
        assert all(len(m) == len(d['nodes']) for m,d in zip(node_maps,trace['traces']))
        for target in trace['conditional_targets']:
            i, did, qi, actor = [target[k] for k in ('record','deal','query','updater')]
            record = trace['sampled_records'][i]; n = record[2]
            assert record[:3] == [qi, actor, n] and n > 0
            node = node_maps[did][qi]; assert node['actor'] == actor and node['n'] == n
            p = np.array(policies['policies'][qi]['probabilities'])
            q = np.array(node['action_values'])[:, actor]
            expected = float(p@q)
            adv = np.zeros(4); adv[:n] = q[:n]-expected
            worst = max(worst, abs(expected-node['values'][actor]),
                float(np.max(abs(adv-np.array(target['advantages'])))), abs(float(p@adv)))
            count += 1
        assert count == sum(r[2] > 0 for r in trace['sampled_records'])
        assert worst < 1e-10
        return count, worst
    for iteration in reg['iterations']:
        source = Path(result['store'])/f'iteration-{iteration:04d}'
        metric = read(source/'metrics.json'); fixture = source/'batch-00'
        folder = store/f'iteration-{iteration:04d}'; folder.mkdir()
        trace_path = folder/'trace.json'
        invoke(TRACE, [context, fixture/'batch.json', fixture/'policies.json', trace_path])
        trace = read(trace_path); old = read(fixture/'updates.json')
        assert trace['sampled_roots'] == old['roots']
        assert trace['sampled_records'] == old['records']
        assert trace['context_source'] == context.read_text()
        assert trace['batch_source'] == (fixture/'batch.json').read_text()
        full = read(fixture/'integrated-native.json')
        assert full['profiles'][0]['name'] == 'baseline'
        error = max(abs(a-b) for d,e in zip(trace['traces'],full['profiles'][0]['deals'])
                    for a,b in zip(d['values'],e['values']))
        assert len(trace['traces']) == len(full['profiles'][0]['deals']) == 64 and error < 1e-10
        count, centered_error = check_targets(trace, read(fixture/'policies.json'))
        rows.append(dict(iteration=iteration, records=len(old['records']), targets=count,
            sampled_values_identical=True, maximum_root_error=error,
            maximum_target_error=centered_error, trace_sha256=sha(trace_path)))
        print(json.dumps(rows[-1]), flush=True)

    # One physical deal; every node/action is checked, not just a few selected cells.
    source = Path(result['store'])/'iteration-0001/batch-00'
    folder = store/'exhaustive-uniform'; folder.mkdir()
    old = read(source/'batch.json')
    bp = folder/'batch.json'
    save(bp, dict(old, batch_id=PREFIX+'-uniform', deals=old['deals'][:1], allin_counts=old['allin_counts'][:1]))
    qp = folder/'queries.json'; invoke(UPDATE, ['queries', context, bp, '-', qp])
    queries = read(qp)
    policy_rows = [dict(hi=o['hi'], lo=o['lo'], actor=o['actor'], n=o['n'],
        probabilities=[1/o['n'] if a<o['n'] else 0. for a in range(4)]) for o in queries['observations']]
    pp = folder/'policies.json'
    policy = dict(format=3, terminal_estimator='conditional-preflop-allin-v1',
        context_source=context.read_text(), batch_source=bp.read_text(), policies=policy_rows)
    save(pp, policy)
    tp = folder/'trace.json'; invoke(TRACE, [context,bp,pp,tp]); trace = read(tp)
    up = folder/'updates.json'; invoke(UPDATE, ['verify',context,bp,pp,up]); updates = read(up)
    assert trace['sampled_roots'] == updates['roots'] and trace['sampled_records'] == updates['records']
    count, centered_error = check_targets(trace, policy)
    nodes = trace['traces'][0]['nodes']; baseline = np.array(trace['traces'][0]['values'])
    assert len(nodes) == len(policy_rows) and {n['query'] for n in nodes} == set(range(len(policy_rows)))
    interventions = [(node, a) for node in nodes for a in range(node['n'])]
    worst_delta = 0.; worst_conditional = 0.; audits = []
    for start in range(0,len(interventions),31):
        part = interventions[start:start+31]
        profiles = [dict(name='baseline',policies=policy_rows)]
        for j,(node, action) in enumerate(part):
            changed = list(policy_rows); qi=node['query']
            changed[qi] = dict(changed[qi],probabilities=np.eye(4)[action].tolist())
            profiles.append(dict(name=f'force-{start+j}',policies=changed))
        ip = folder/f'intervention-{start:05d}-profiles.json'
        op = folder/f'intervention-{start:05d}-values.json'
        save(ip,dict(format=1,context_source=context.read_text(),batch_source=bp.read_text(),profiles=profiles))
        invoke(FULL,[context,bp,ip,op]); native=read(op)
        assert np.max(abs(np.array(native['profiles'][0]['deals'][0]['values'])-baseline)) < 1e-10
        assert native['maximum_forward_cashflow_error'] < 1e-10
        assert native['maximum_conservation_error'] < 1e-10
        assert len(native['profiles']) == len(part)+1
        for j,((node,action), profile) in enumerate(zip(part,native['profiles'][1:])):
            assert profile['name'] == f'force-{start+j}' and node['reach'] > 0
            difference=np.array(profile['deals'][0]['values'])-baseline
            predicted=node['reach']*(np.array(node['action_values'][action])-np.array(node['values']))
            err=float(np.max(abs(difference-predicted)))
            worst_delta=max(worst_delta,err); worst_conditional=max(worst_conditional,err/node['reach'])
        audits.append(dict(start=start,count=len(part),profiles_sha256=sha(ip),native_sha256=sha(op)))
        # Only this freshly created, owned redundant transport is released.
        assert ip.resolve().parent == folder.resolve() and ip.name == f'intervention-{start:05d}-profiles.json'
        ip.unlink()
    assert worst_delta < 1e-10 and worst_conditional < 1e-7
    summary=dict(nodes=len(nodes),actions=len(interventions),maximum_delta_error=worst_delta,
        maximum_conditional_error=worst_conditional,maximum_target_error=centered_error,
        targets=count,interventions=audits,minimum_reach=min(n['reach'] for n in nodes))
    save(folder/'summary.json',summary)
    for path,digest in reg['inputs'].items(): guard(); assert sha(path)==digest,path
    artifacts={str(p):sha(p) for p in store.rglob('*') if p.is_file()}
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        fixtures=rows,exhaustive_uniform=summary,artifacts=artifacts,seconds=time.monotonic()-started,
        accuracy_qualified=False,production_modified=False,training_started=False,
        scope='Trace implementation and preserved-sampling checks only. No initial exact-target replacement or poker-strength claim.'))


if __name__ == '__main__':
    if sys.argv[1:] == ['--worker']: worker(read(OUT/f'{PREFIX}-registration.json'))
    else:
        assert sys.argv[1:] == ['--run']
        source_result=read(OUT/'action-integrated-replication-v1-result.json')
        extras=[str(p) for p in (TRACE,UPDATE,FULL,OUT/'LATER-ACTION-INTEGRATION-PLAN.md',
            ROOT/'crates/solver/examples/hu_sampled_action_trace_v1.rs')]
        extras.extend(str(p) for p in (ROOT/'crates/solver/examples/research_sampled').glob('*.rs'))
        for iteration in ITERATIONS:
            folder=Path(source_result['store'])/f'iteration-{iteration:04d}'
            mp=folder/'metrics.json'; assert sha(mp)==source_result['steps'][iteration-1]['metrics_sha256']
            metric=read(mp); extras.append(str(mp))
            for name in ('batch','queries','policies','updates','integrated-native'):
                p=folder/'batch-00'/f'{name}.json'
                assert sha(p)==metric['subbatches'][0]['artifacts'][name]
                extras.append(str(p))
        launch(Path(__file__).resolve(),PREFIX,dict(extra_inputs=extras,store=str(STORE),
            iterations=list(ITERATIONS),scope='Diagnostic trace replay and exhaustive uniform single-deal forced-action checks.'),
            cap=256_000_000,seconds=1800)
