"""Preserve and review every outcome of the registered coherent-range diagnostic."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'
STUDY = OUT.parent/'symmetric-bridge-20260919'


def main():
    log = OUT/'coherent-range-diagnostic.log'
    status_path = OUT/'coherent-range-diagnostic-status.json'
    freeze_path = STUDY/'coherent-runtime-freeze.json'
    freeze = json.loads(freeze_path.read_text())
    for relative, digest in freeze['inputs'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == digest, relative
    rows = [json.loads(line[9:]) for line in log.read_text().splitlines() if line.startswith('COHERENT ')]
    assert len(rows) == 6 and {(r['mode'], r['board']) for r in rows} == {
        (mode, board) for mode in ['abrupt_pair', 'smooth_pair'] for board in ['KsQs2d', 'KsQs2s', 'KsQh2d']}
    for r in rows:
        passed = (r['same_state_cfv'] < .002 and r['immediate_root'] < .002 and
                  r['root_drift'] < .01 and r['avg_br_difference'] < .002 and
                  r['same_policy_quotient_difference'] < .0001)
        assert r['passed'] == passed
    status = json.loads(status_path.read_text())
    assert status['exit_code'] == (0 if all(r['passed'] for r in rows) else 101)
    files = [Path(__file__), log, status_path, freeze_path,
             ROOT/'crates/solver/src/cfr.rs', ROOT/'crates/solver/src/gpu/kernels.cu']
    result = dict(passed=all(r['passed'] for r in rows), passed_cases=sum(r['passed'] for r in rows),
                  total_cases=6, rows=rows, status=status, production_promotion_allowed=False,
                  inputs_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    with (STUDY/'coherent-range-review.json').open('x') as f:
        json.dump(result, f, indent=2, allow_nan=False)
    text = ['# Coherent-range diagnostic: failed qualification', '',
            f'{result["passed_cases"]}/6 cases passed. Original thresholds and the earlier independent-input stress failure remain unchanged. No production promotion.', '',
            '| Mode | Board | Same-state CFV / mass | Immediate root difference | Final root drift | Final average/BR value difference / mass | Same-policy quotient difference / mass | Passed |',
            '|---|---|---:|---:|---:|---:|---:|---|']
    for r in rows:
        text.append(f'| {r["mode"]} | {r["board"]} | {r["same_state_cfv"]:.8f} | {r["immediate_root"]:.8f} | {r["root_drift"]:.8f} | {r["avg_br_difference"]:.8f} | {r["same_policy_quotient_difference"]:.8f} | {r["passed"]} |')
    text += ['', 'Root differences are probability units, not bb. Value columns are bb divided by opposing reach mass. These are short, narrow diagnostics, not a full connected-game acceptance result.', '',
             'The smooth rainbow case passes and has identical independent GPU trajectories. The other smooth cases pass the immediate-update and same-policy evaluation checks but fail final independent-trajectory value agreement. This localizes a remaining issue to training trajectories rather than demonstrating an evaluation-only error; it does not prove that floating-point order is the sole cause.', '',
             'The abrupt rainbow case has identical independent GPU trajectories and final values, yet fails the CPU-versus-GPU immediate-average check. Source inspection identifies a relevant semantic difference: cfr.rs returns before updating averages when every opposing reach is zero, whereas kernels.cu updates average sums from the traverser reach even when the opposing reach is zero. The diagnostic deliberately includes whole-seat zero reaches. This is a concrete mismatch in the compared update rules, not evidence that every abrupt failure comes from suit compression. A focused zero-opponent update test should confirm its contribution before altering any implementation or test.', '',
             'That discrepancy does not explain the smooth two-tone and monotone final-value failures. Preserve all failures, align the intended zero-reach update contract in a separate experiment, and trace the remaining independent-trajectory differences. Do not relax the thresholds or treat the successful same-policy evaluator as qualification of the full training bridge.', '',
             'The test executable exited 101 after printing all six cases. The guard retained the failed status and verified its frozen inputs. The separate own-average transfer candidate uses full arenas and its own exact parity gates; these results neither qualify nor disqualify that different change.']
    (STUDY/'COHERENT-RANGE-REVIEW.md').write_text('\n'.join(text)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','passed_cases','total_cases','production_promotion_allowed']}))


if __name__ == '__main__':
    main()
