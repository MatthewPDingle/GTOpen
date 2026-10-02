"""Verify passed component evidence, preserve original science, save local analysis."""
import hashlib
import json
from pathlib import Path
import re

STAGE = Path(__file__).parent
REPO = Path(r'T:\Dev\GTOpen')
OUT = REPO/'research/preflop-evolution/blind-defense-20260922'

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path, raw):
    if path.exists():
        if path.read_bytes() != raw: raise ValueError('Conflicting evidence: '+str(path))
    else:
        with path.open('xb') as stream: stream.write(raw)
    return sha(path)

def main():
    checked = {}
    for name in ('preflop-expected-native-targets-publication-v1.json', 'preflop-expected-policy-publication-v1.json'):
        path = OUT/name; receipt = json.loads(path.read_bytes()); assert receipt['passed']
        for field in ('inputs', 'outputs'):
            for source, identity in receipt[field].items():
                assert sha(source) == identity, source
                checked[source] = identity
        checked[str(path)] = sha(path)
    results = {}
    for name in ('preflop-expected-native-targets-check-v3-result.json',
                 'preflop-expected-policy-check-v1-result.json',
                 'preflop-expected-policy-cuda-check-v1-result.json'):
        path = OUT/name; value = json.loads(path.read_bytes())
        assert value['passed'] and not value['scientific_attempt'] and not value['accuracy_qualified']
        assert not value['production_modified']
        for source, identity in value['inputs'].items():
            assert sha(source) == identity, source
            checked[source] = identity
        checked[str(path)] = sha(path); results[name] = value
    original = {'stack-context-matched-evaluation-v5-result.json': 'dd31ef7b49b75cd586d3d69769cb4d6fd8fc0cb4d81230330da7c7c59ab4ae96',
        'STACK-CONTEXT-FINDINGS-20261002.md': '7af730b47a02c837b1dbf3964ec66fa79276a3d815277dbdc78a20b74ab402de',
        'STACK-CONTEXT-AA-DIAGNOSIS-20261002.md': 'e9789d5e5ceac94329f57fceda6e3871c0b75271a7062edbf9e727e4e71c6cb9',
        'STACK-CONTEXT-PREFLOP-EXPECTED-TARGETS-20261002.md': 'fa4be0de7c91156e77344bdbe66dac84b0654b65bd456e6b9c5e923865018077',
        'STACK-CONTEXT-PREFLOP-CUMULATIVE-STATE-20261002.md': '01564493e0f89237add8c1d0ff5bdc50ccc322e1d4abf5b0440bae788a32ee37'}
    for name, identity in original.items():
        path = OUT/name; assert sha(path) == identity, name
        checked[str(path)] = identity
    native = results['preflop-expected-native-targets-check-v3-result.json']
    policy = results['preflop-expected-policy-check-v1-result.json']
    cuda = results['preflop-expected-policy-cuda-check-v1-result.json']
    assert len(native['refused_cases']) == 20 and len(policy['refused_cases']) == 15
    assert {(r['input_width'], r['stack']) for r in cuda['cases']} == {(362, 20), (362, 200), (387, 20), (387, 200)}
    assert max(r['preflop_maximum_error'] for r in cuda['cases']) == 0
    assert max(r['postflop_maximum_error'] for r in cuda['cases']) == 0
    document = '''# Connecting complete preflop learning state to played policies

The new cumulative preflop state now has a typed played-policy format and a native-target adapter with passed software checks. Every fitted preflop decision uses the cumulative state, including later responses after a raise. The new format refuses the old sparse retained tables and separate legacy root/BTN overrides. This addresses the policy-routing part of the diagnosed AA problem; it does **not** show that real AA ranges or overall poker accuracy have improved.

Shared postflop network calculations retain the existing visible-input and public-price checks. A context held out from fitting has no local cumulative state and uses the shared network. That behavior is explicit; no nearest-stack table is silently substituted. Model averaging weights each played strategy by the hand's own earlier actions, and excludes the final unplayed model using the completed-cycle boundary supplied by the checkpoint caller. A complete on-disk training checkpoint is still required before that boundary can be authenticated in a real run.

The target adapter retains all 1,081 board-legal holdings per actor, including zero-entry-weight hands. It verifies ordered hand rows, visible board prefixes, actor, action menu and public history before scoring. Each board contribution is bound to the raw tree bytes, frozen model and parent cumulative state. Native executable/context/request authentication is still the worker caller's responsibility; a tree hash alone does not prove the correct native process produced it.

## What passed

| Control | Coverage | Result |
| --- | --- | --- |
| Published native transport | 20bb and 200bb; complete 1,081-hand domains | Exact target transport agreement, unchanged postflop policy, exact update/restoration; 20 invalid cases refused |
| Typed model | 5,304 physical preflop rows at 20bb and 6,630 at 200bb | Every fitted row uses cumulative state; held-out 60bb uses network only; 15 invalid cases refused |
| Typed target producer | 20bb preserved native topology expanded to the complete private domain | All-node values match the previously checked transport exactly; postflop probabilities unchanged |
| Played-policy averaging and storage | Two synthetic generations at both fitted depths | Independent row-by-row own-history average matches; content-addressed model round-trip exact |
| CPU/CUDA parity | 362- and 387-input models at 20bb/200bb; native flop, turn and river rows | Zero observed prediction differences for all four cases |

The GPU control used nonuniform synthetic network weights and synthetic cumulative updates. It ran on the RTX 3090 with TF32 disabled, allocating about 34 MiB of CUDA tensors at peak. The CPU and CUDA controls ran independently in parallel after publication. Their durations were small software-control measurements, **not throughput benchmarks or evidence of faster learning**.

The original native controls exported only two test holdings per actor. Their topology, cashflows and visible-prefix rows are preserved. The expanded trees use synthetic strengths; they are not independent validations of the full native poker payoff oracle. Earlier expected-component tests independently checked the reduction mathematics, but these integration controls do not establish real range accuracy.

An earlier control stopped during setup because it supplied an unsupported `chance` constructor argument. Its exact source and failure are retained separately. The corrected control changed that setup call; the transport provider remained unchanged. The additional typed policy and typed target adapter are separately versioned. No original scientific source, result or improvement gate was changed.

## What remains

Next is the actual worker and complete training-cycle integration: authenticate native exports, collect every fitting context against the same frozen played model, publish cumulative states and both fitted networks together, and restore all sampling/reservoir state at a completed boundary. Then measure representative CPU/GPU/RAM/storage use and register a stability comparison with an explicit board-sampling budget before starting it.

These components are prepared for the existing heads-up BB-versus-BTN continuation family. They do not yet solve stack-specific opening ranges, add five-bets, establish multiway accuracy or demonstrate agreement with GTO Wizard. The original comparison failed its improvement criterion and remains unchanged. No scientific training run was started, no production behavior changed, and nothing was deployed on port 56708.

Evidence: [typed policy](../../../tools/research/preflop_expected_policy_v1.py), [typed target adapter](../../../tools/research/preflop_expected_native_targets_v2.py), [CPU control](preflop-expected-policy-check-v1-result.json), [CUDA control](preflop-expected-policy-cuda-check-v1-result.json), [transport control](preflop-expected-native-targets-check-v3-result.json), [review receipt](preflop-expected-policy-review-v1.json), and [AA diagnosis](STACK-CONTEXT-AA-DIAGNOSIS-20261002.md).
'''
    for link in re.findall(r'\]\(([^)]+)\)', document):
        if link == 'preflop-expected-policy-review-v1.json': continue
        assert (OUT/link).resolve().is_file(), link
    doc_path = OUT/'STACK-CONTEXT-PREFLOP-POLICY-INTEGRATION-20261002.md'
    doc_sha = put(doc_path, document.encode('utf-8'))
    source_path = OUT/Path(__file__).name
    source_sha = put(source_path, Path(__file__).read_bytes())
    receipt = dict(passed=True, checked_inputs=checked,
        outputs={str(doc_path):doc_sha, str(source_path):source_sha},
        original_comparison_preserved=True, typed_policy_and_native_transport_software_qualified=True,
        native_execution_authentication_and_cycle_checkpoint_qualified=False,
        scientific_attempt=False, accuracy_qualified=False, production_modified=False,
        prose_review='Coverage and limits checked against saved controls; real range accuracy remains unproven.')
    receipt_path = OUT/'preflop-expected-policy-review-v1.json'
    receipt_sha = put(receipt_path, json.dumps(receipt, indent=2, allow_nan=False).encode())
    journal = OUT/'RIVER-CONTINUATION-RUNNING.md'
    marker = '## 2026-10-02 Adelaide - typed cumulative policy and native transport controls pass'
    assert marker not in journal.read_text(encoding='utf-8')
    entry = f'''\n\n{marker}

The previous goal turn completed the live native software-control handle and answered the user's question about correct ranges; this yielded new terminal evidence rather than a status-only wait. This turn published the unchanged transport provider and preserved setup failure, qualified the published transport, then implemented a separate genuine all-node played-policy contract and typed target adapter. Every fitted preflop decision uses the cumulative state; legacy sparse/root/BTN overlays are refused. Held-out contexts use the shared network only. Shared postflop visible-input math is retained; own-history-weighted averaging and immutable model I/O are qualified by synthetic controls.

Published transport checks pass at20/200bb with all1081holdings/player,20refused invalid cases and exact transport/update/restoration. Published typed-model checks cover5304/6630physical preflop rows,15refusals, unchanged postflop probabilities and exact typed-target parity at20bb. Published CPU/CUDA checks pass for362/387inputs at20/200bb and all three postflop phases, with zero observed prediction differences. Nonuniform synthetic networks were used; RTX3090 peak CUDA tensors35314176bytes. Controls ran independently in parallel, CPU{policy['seconds']:.3f}s and GPU{cuda['seconds']:.3f}s; these are software-control timings, not a training/throughput benchmark. Tiny native exports are preserved and reused; expanded strengths remain synthetic, not a full independent poker-payoff validation.

Saved STACK-CONTEXT-PREFLOP-POLICY-INTEGRATION-20261002.md SHA{doc_sha} and review receipt SHA{receipt_sha}; all{len(checked)}source/evidence identities checked, original comparison/result/findings/AA/expected-component notes unchanged. All foreground software handles63441/70773/93431/80366/93353 completed successfully and are closed. No scientific run admitted or started; no production56708change, GitHub push/deployment, or broad completion claim.

Next: wire authenticated native workers and complete joint training cycles, including sampler/reservoir/RNG restoration and both network fits. The current component must replace later sparse preflop policy behavior in the actual runner, not merely exist as an unused overlay. Then measure representative resources and prospectively register a sufficiently sampled stability comparison. Original failed improvement gate, models/budgets/sources/failures remain preserved. Full preflop, stack-specific openings, five-bets, multiway and GTO Wizard accuracy remain outstanding. Goal active.
'''
    with journal.open('a', encoding='utf-8') as stream: stream.write(entry)
    for path, identity in checked.items(): assert sha(path) == identity, path
    assert sha(doc_path) == doc_sha and sha(receipt_path) == receipt_sha
    print(json.dumps(dict(passed=True, checked_inputs=len(checked), document_sha256=doc_sha, receipt_sha256=receipt_sha)))

if __name__ == '__main__': main()
