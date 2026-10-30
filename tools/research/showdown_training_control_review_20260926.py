"""Read-only scalar reconstruction of the showdown integration control.

Does not call the target adapter, accumulator update, or training runner.
"""
import hashlib
import json
import math
from pathlib import Path
import time
import numpy as np
from showdown_control_reference_v1 import score

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'showdown-training-integration-control-v1'


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    started = time.monotonic(); result_path = OUT/f'{PREFIX}-result.json'
    result = read(result_path); reg_path = OUT/f'{PREFIX}-registration.json'; reg = read(reg_path)
    assert result['passed'] and read(OUT/f'{PREFIX}-status.json')['state'] == 'complete'
    assert result['registration_sha256'] == sha(reg_path)
    for path,h in reg['inputs'].items(): assert sha(path)==h,path
    for path,h in result['artifacts'].items(): assert sha(path)==h,path
    store = Path(result['store']); coefficients = read(OUT/'showdown-root-control-coefficients-v1.json')
    assert digest(coefficients) == result['config']['control_coefficients_sha256']
    counts = [0]*169; regrets = [[0.]*4 for _ in range(169)]
    max_error = 0.; max_mean_error = 0.; rows = 0
    for iteration in (1,2):
        part = store/f'iteration-{iteration:04d}'/'batch-00'
        batch = read(part/'batch.json'); queries = read(part/'queries.json'); policies = read(part/'policies.json')
        original = read(part/'integrated-targets.json'); corrected = read(part/'showdown-targets.json')
        assert corrected['identity']['control_coefficients_sha256'] == digest(coefficients)
        assert corrected['source_integrated_audit_sha256'] == digest(original)
        assert corrected['queries_sha256'] == digest(queries) and corrected['policies_sha256'] == digest(policies)
        assert len(original['bb_root_corrections']) == len(corrected['bb_root_corrections']) == len(batch['deals']) == 64
        for i,(old,new) in enumerate(zip(original['bb_root_corrections'],corrected['bb_root_corrections'])):
            cards = batch['deals'][i]; record = batch['allin_counts'][i]
            assert record['private_cards'] == cards[:4]
            assert record['wins']+record['ties']+record['losses'] == record['boards'] == 1712304
            hi,lo = sorted([cards[0]//4,cards[1]//4],reverse=True)
            hand = hi*14 if hi==lo else hi*13+lo if cards[0]%4==cards[1]%4 else lo*13+hi
            assert old['hand_class'] == new['hand_class'] == hand and old['deal'] == new['deal'] == i
            q = old['query']; assert queries['observations'][q]['hi'] == '1'
            p = policies['policies'][q]['probabilities']; assert len(p)==4 and abs(sum(p)-1)<1e-12
            feature = score(cards)/2 - (record['wins']+record['ties']/2)/record['boards']
            beta = [0.,*coefficients['call_raise_coefficients'][hand],0.]
            values = [v-b*feature for v,b in zip(old['action_values'],beta)]
            mean = math.fsum(prob*v for prob,v in zip(p,values))
            advantages = [v-mean for v in values]
            max_error = max(max_error,max(abs(a-b) for a,b in zip(values,new['action_values'])),
                            max(abs(a-b) for a,b in zip(advantages,new['advantages'])))
            assert values[0] == old['action_values'][0] and values[3] == old['action_values'][3]
            # Conditional expectation of correction (including recentering) is zero.
            masses = [record[k]/record['boards'] for k in ('losses','ties','wins')]
            feature_mean = math.fsum(m*(o/2-(record['wins']+record['ties']/2)/record['boards']) for o,m in enumerate(masses))
            expected_adv_correction = [(math.fsum(prob*b for prob,b in zip(p,beta))-b)*feature_mean for b in beta]
            max_mean_error = max(max_mean_error,max(abs(v) for v in expected_adv_correction))
            counts[hand] += 1
            for action in range(4): regrets[hand][action] += advantages[action]
            rows += 1
        ref = result['steps'][iteration-1]['next_model']; path = store/'objects'/ref['file']
        assert sha(path) == ref['sha256']; model = read(path)
        assert model['format'] == 8 and model['generation'] == iteration
        state = model['integrated_root']['state']
        assert state['coefficients_sha256'] == digest(coefficients)
        assert state['completed_updates'] == iteration and state['sample_counts'] == counts
        max_error = max(max_error,float(np.max(abs(np.array(regrets)-np.array(state['regret_sums'])))))
    assert rows == 128 and max_error < 1e-10 and max_mean_error < 1e-10
    # Replayed artifacts must match originals, not only the reported checkpoint.
    for p in (store/'iteration-0002'/'batch-00').iterdir():
        if p.is_file(): assert sha(p) == sha(store/'replay-0002'/'batch-00'/p.name),p
    replay = read(store/'replay-0002'/'metrics.json')
    assert replay['checkpoint'] == result['final_checkpoint']
    output = dict(passed=True,source_result_sha256=sha(result_path),registration_sha256=sha(reg_path),
        reviewer_sha256=sha(__file__),rows=rows,maximum_scalar_error=max_error,
        maximum_expected_advantage_correction=max_mean_error,root_counts_and_sums_reconstructed=True,
        replay_subbatch_artifacts_identical=True,seconds=time.monotonic()-started,
        production_modified=False,accuracy_qualified=False,
        scope='Independent scalar target, zero-mean correction, cumulative root state and replay-artifact checks; not strength validation.')
    path = OUT/f'{PREFIX}-independent-review.json'
    with path.open('x') as f: json.dump(output,f,indent=2,allow_nan=False)
    print(json.dumps(output))


if __name__=='__main__': main()
