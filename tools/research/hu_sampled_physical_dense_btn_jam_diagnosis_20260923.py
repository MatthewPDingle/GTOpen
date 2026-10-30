"""Post-hoc BTN-vs-jam diagnosis using the already audited dense evaluation.

No new training or policy edits. Independent five-card enumeration checks every
showdown against native fixed-policy values. All decisions use only hand class;
future cards enter payoffs, never the response selected on the training stream.
"""
from collections import Counter
from itertools import combinations
import hashlib
import json
import math
from pathlib import Path
import time
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-dense-btn-jam-diagnosis-v1'
SOURCE = 'sampled-physical-dense-evaluation-v1'
STORE = Path('S:/GTOpen-research')/PREFIX


def rank5(cards):
    ranks = sorted((c//4 for c in cards),reverse=True)
    groups = sorted(((n,r) for r,n in Counter(ranks).items()),reverse=True)
    flush = len({c%4 for c in cards}) == 1
    straight = (ranks[0] if len(groups)==5 and ranks[0]-ranks[-1]==4
                else 3 if ranks==[12,3,2,1,0] else -1)
    if flush and straight >= 0: return (8,straight)
    if groups[0][0] == 4: return (7,groups[0][1],groups[1][1])
    if [g[0] for g in groups] == [3,2]: return (6,groups[0][1],groups[1][1])
    if flush: return (5,*ranks)
    if straight >= 0: return (4,straight)
    if groups[0][0] == 3: return (3,groups[0][1],*sorted((r for n,r in groups[1:]),reverse=True))
    if [g[0] for g in groups[:2]] == [2,2]: return (2,*sorted((r for n,r in groups[:2]),reverse=True),groups[2][1])
    if groups[0][0] == 2: return (1,groups[0][1],*sorted((r for n,r in groups[1:]),reverse=True))
    return (0,*ranks)


def showdown(deal):
    assert len(deal)==len(set(deal))==9 and all(type(c) is int and 0<=c<52 for c in deal)
    best = [max(rank5(cards) for cards in combinations(deal[2*p:2*p+2]+deal[4:],5)) for p in (0,1)]
    return -1 if best[0]==best[1] else int(best[1]>best[0])


def name(c):
    a,b = divmod(c,13); ranks = '23456789TJQKA'
    return ranks[a]*2 if a==b else ranks[max(a,b)]+ranks[min(a,b)]+('s' if a>b else 'o')


def main():
    started = time.monotonic(); last = 0.
    def guard():
        nonlocal last
        now = time.monotonic()
        if now-last >= 2:
            assert now-started < 1200 and idle(), 'Diagnostic deadline or production activity'
            assert psutil.virtual_memory().available >= 20_000_000_000
            assert psutil.disk_usage(str(STORE.parent)).free >= 40_000_000_000
            last = now
    guard()
    paths = {s:OUT/f'{SOURCE}-{s}.json' for s in ('registration','result','independent-review','status')}
    documents = {s:json.loads(p.read_text()) for s,p in paths.items()}
    reg,result,review,status = [documents[s] for s in ('registration','result','independent-review','status')]
    assert review['passed'] and result['terminal'] and status['state']=='complete'
    assert review['result_sha256']==sha(paths['result']) and review['registration_sha256']==sha(paths['registration'])
    assert review['terminal_status_sha256']==sha(paths['status'])
    for p,h in reg['inputs'].items(): assert sha(p)==h,p
    context_path = Path(reg['context']); context = json.loads(context_path.read_text())
    root = context['nodes'][0]; jam_action = next(i for i,a in enumerate(root['actions']) if a['kind']=='jam')
    node_id = root['children'][jam_action]; node = context['nodes'][node_id]
    assert root['actor']==0 and node['actor']==1 and [a['kind'] for a in node['actions']]==['fold','call']
    assert sum(n['children'].count(node_id) for n in context['nodes'])==1
    folded,called = [context['nodes'][i] for i in node['children']]
    assert folded['leaf']['type']=='fold' and called['leaf']['type']=='showdown'
    assert called['invested']==[200.,200.] and context['dead_money']==.5
    pot = called['pot']; gross_rake = pot*context['rake_fraction']
    rake = min(gross_rake,context['rake_cap']) if context['rake_cap']>0 else gross_rake
    fold_value = folded['leaf']['utilities'][1]
    registration = dict(inputs={str(p):sha(p) for p in [Path(__file__),*paths.values(),context_path]},
        minimum_training_observations=16,source=SOURCE,target_node=node_id,
        selection='Per BTN class, maximize summed BB-jam-reach-weighted value on the existing response-training stream. Under 16 raw observations retains the original mix. Freeze before reading existing test batches.',
        scope='Post-hoc diagnosis on previously evaluated streams, not fresh confirmation. Alter only BTN response to the initial BB jam; all other policy rows fixed. Independent hand enumeration verifies native payoffs. No policy is deployed or fed into ongoing hybrid training.',
        production_modified=False)
    regpath = OUT/f'{PREFIX}-registration.json'; save(regpath,registration)
    assert not STORE.exists(); STORE.mkdir()
    stream_rows = {}; counts = [0]*169; weighted_call_advantage = [0.]*169
    class_probability = {}; source_hashes = {}; max_native_error = 0.; result_error = None
    try:
        for phase,total in [('train',8192),('test',16384)]:
            print(json.dumps(dict(phase=phase)),flush=True); rows = []
            for offset in range(0,total,16):
                guard(); folder = Path(reg['store'])/f'{SOURCE}-{phase}-{offset}'
                summary_path = folder/'summary.json'
                assert sha(summary_path)==result['batch_summary_hashes'][folder.name]
                summary = json.loads(summary_path.read_text()); contents = {}
                for artifact in ('batch.json','profiles.json','native.json'):
                    raw = (folder/artifact).read_bytes(); h = hashlib.sha256(raw).hexdigest()
                    assert h==summary['artifacts'][artifact]
                    source_hashes[str(folder/artifact)] = h; contents[artifact] = json.loads(raw)
                source_hashes[str(summary_path)] = sha(summary_path)
                native = {p['name']:p['deals'] for p in contents['native.json']['profiles']}
                baseline = contents['profiles.json']['profiles'][0]; assert baseline['name']=='baseline'
                call_by_class = {}
                for p in baseline['policies']:
                    if int(p['hi']) != node_id+1: continue
                    assert p['actor']==1 and p['n']==2
                    key = int(p['lo']); c = hand_class([key&63,(key>>6)&63]); prob = p['probabilities'][1]
                    assert p['probabilities'][2:]==[0.,0.] and 0<=prob<=1
                    if c in class_probability: assert abs(class_probability[c]-prob)<1e-12
                    class_probability[c] = prob; call_by_class[c] = prob
                for i,deal in enumerate(contents['batch.json']['deals']):
                    c = hand_class(deal[2:4]); probability = call_by_class[c]
                    winner = showdown(deal)
                    call_value = -called['invested'][1]+(pot-rake)*(0.5 if winner<0 else float(winner==1))
                    local_baseline = fold_value*(1-probability)+call_value*probability
                    native_local = native[f'action-{jam_action}'][i]['values'][1]
                    error = abs(local_baseline-native_local); assert error<1e-9
                    max_native_error = max(max_native_error,error)
                    reach = summary['root_probabilities'][i][jam_action]
                    row = dict(hand_class=c,jam_reach=reach,baseline_call_probability=probability,
                        call_value=call_value,fold_value=fold_value,baseline_local_value=local_baseline,
                        baseline_full_value=native['baseline'][i]['values'][1])
                    rows.append(row)
                    if phase=='train':
                        counts[c]+=1; weighted_call_advantage[c]+=reach*(call_value-fold_value)
            assert len(rows)==total; stream_rows[phase]=rows
            if phase=='train':
                response = dict(actions=[int(weighted_call_advantage[c]>0) if counts[c]>=16 else -1 for c in range(169)],
                    counts=counts,weighted_call_advantage=weighted_call_advantage,
                    tie_rule='fold',fallback='unchanged baseline')
                save(STORE/'response.json',response); response_hash = sha(STORE/'response.json')
        assert sha(STORE/'response.json')==response_hash
        test = stream_rows['test']; total_reach = math.fsum(r['jam_reach'] for r in test)
        class_rows = []; differences = []; applied = 0
        for r in test:
            choice = response['actions'][r['hand_class']]
            selected = r['baseline_local_value'] if choice<0 else (r['call_value'] if choice else r['fold_value'])
            differences.append(r['jam_reach']*(selected-r['baseline_local_value'])); applied+=int(choice>=0)
        for c in range(169):
            subset = [r for r in test if r['hand_class']==c]
            if not subset: continue
            weight = math.fsum(r['jam_reach'] for r in subset)
            class_rows.append(dict(hand=name(c),hand_class=c,test_deals=len(subset),training_deals=counts[c],
                baseline_call_probability=class_probability[c],train_selected_action=response['actions'][c],
                summed_jam_reach=weight,effective_weighted_test_deals=weight**2/math.fsum(r['jam_reach']**2 for r in subset),
                conditional_call_minus_fold=math.fsum(r['jam_reach']*(r['call_value']-r['fold_value']) for r in subset)/weight))
        save(STORE/'rows.json',stream_rows)
        document = dict(passed=True,registration_sha256=sha(regpath),source_artifacts=source_hashes,
            row_artifact=str(STORE/'rows.json'),rows_sha256=sha(STORE/'rows.json'),
            response_artifact=str(STORE/'response.json'),response_sha256=response_hash,
            training_deals=8192,test_deals=16384,independent_showdowns_verified=24576,
            maximum_native_value_error=max_native_error,mean_bb_jam_reach=total_reach/16384,
            conditional_btn_call_frequency=math.fsum(r['jam_reach']*r['baseline_call_probability'] for r in test)/total_reach,
            trained_response_gain_per_spot_entry_bb=math.fsum(differences)/16384,
            trained_response_gain_per_jam_reached_bb=math.fsum(differences)/total_reach,
            always_call_gain_per_spot_entry_bb=math.fsum(r['jam_reach']*(r['call_value']-r['baseline_local_value']) for r in test)/16384,
            always_fold_gain_per_spot_entry_bb=math.fsum(r['jam_reach']*(r['fold_value']-r['baseline_local_value']) for r in test)/16384,
            mean_baseline_btn_value_per_spot_entry_bb=math.fsum(r['baseline_full_value'] for r in test)/16384,
            fallback_test_deals=16384-applied,classes=class_rows,seconds=time.monotonic()-started,
            fresh_confirmation=False,production_modified=False,scope=registration['scope'])
        for p,h in registration['inputs'].items(): assert sha(p)==h,p
        guard(); save(OUT/f'{PREFIX}-result.json',document)
        print(json.dumps({k:v for k,v in document.items() if k not in ('source_artifacts','classes')}))
    except Exception as exc:
        result_error = str(exc); raise
    finally:
        save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if result_error else 'complete',error=result_error,
            seconds=time.monotonic()-started,production_modified=False))


if __name__=='__main__': main()
