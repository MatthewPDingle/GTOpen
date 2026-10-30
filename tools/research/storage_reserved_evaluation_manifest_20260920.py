"""Preserve the registered heldout sample while naming its actual evaluator."""
import json
from pathlib import Path
from storage_phase_run_20260920 import ROOT, OUT, read, sha
from storage_expansion_register_20260920 import signature, sample, TEST_SEED, FIXTURE, OLD


def main():
    registration = read(OUT/'expansion-registration-freeze.json')
    for p,digest in registration['inputs_sha256'].items():
        assert sha(ROOT/p) == digest,p
    source_path = OUT/'expansion-reserved-95.json'
    source = read(source_path)
    excluded = {signature(b['board']) for b in read(OLD)['boards']}
    for n in [128,112,96]:
        excluded.update(signature(b['board']) for b in read(OUT/f'expansion-train-{n}.json')['boards'])
    held = {signature(b['board']) for b in source['boards']}
    assert len(held) == len(source['boards']) == 95 and not held & excluded
    eligible = [(b,m) for b,m in read(FIXTURE)['canonical_flops'] if signature(b) not in excluded]
    assert len(eligible) == registration['eligible_orbits'] == 1302
    assert sum(m for b,m in eligible) == registration['eligible_physical_mass'] == 15320
    reproduced = sample(eligible,95,TEST_SEED)
    for key,value in reproduced.items():assert source[key] == value,key
    exe = ROOT/'target/release/examples/continuation_transfer_streamed.exe'
    assert sha(exe) == '1203c744b108bfe9d7ded463242c6b066a8a22df8e5fbcdb052cdf2bb3d7282f'
    evaluation = {**source,'future_card_policy':'plain_explicit',
                  'registered_source_panel_sha256':sha(source_path)}
    assert {k:v for k,v in evaluation.items() if k not in ['future_card_policy','registered_source_panel_sha256']} == {
        k:v for k,v in source.items() if k != 'future_card_policy'}
    destination = OUT/'expansion-reserved-95-evaluation-v1.json'
    with destination.open('x') as f:json.dump(evaluation,f,indent=2)
    review = dict(passed=True,metadata_only_adapter=True,all_boards_weights_and_selection_metadata_unchanged=True,
                  original_sample_reproduced=True,disjoint_from_all_training_candidates_and_old164=True,
                  eligible_physical_mass=15320,full_physical_mass=22100,
                  declared_future_card_policy='plain_explicit',actual_evaluator_sha256=sha(exe),
                  field_does_not_select_executable_behavior=True,reserved_strategy_results_read=False,
                  accuracy_claim=False,inputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in [
                      Path(__file__),source_path,destination,OUT/'expansion-registration-freeze.json',
                      ROOT/'crates/solver/examples/continuation_transfer_streamed.rs',
                      OUT/'STRATEGIC-EVALUATION-COMPATIBILITY.md']})
    with (OUT/'reserved-evaluation-manifest-v1-review.json').open('x') as f:json.dump(review,f,indent=2)
    print(json.dumps(review,indent=2))


if __name__ == '__main__':main()
