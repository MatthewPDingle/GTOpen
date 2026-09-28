"""Read-only training diagnosis; does not inspect held-out evaluation data."""
import sys
from pathlib import Path
sys.path.insert(0, 'T:/Dev/GTOpen/tools/research')
import json
from river_matched_pilot_review_v2 import compare_model_parts, read, sha, OUT
from preflop_allin_matrix_v1 import AllinMatrix

store = Path('S:/GTOpen-research/weighted-complete-river-training-pilot-v1')
registration_path = OUT/'river-matched-training-pilot-v1-registration.json'
registration = read(registration_path)
source = OUT/'bb-context-candidate.json'
matrix_path = OUT/'preflop-allin-matrix-control-v1-matrix.json'
matrix = AllinMatrix(read(matrix_path), source.read_text())
models = []
identities = {str(registration_path): sha(registration_path)}
costs = {}
for arm in ('A-baseline', 'A-river'):
    folder = store/arm
    progress = read(folder/'progress.json')
    assert progress['completed'] == 80
    cp = folder/'objects'/progress['checkpoint']['file']
    assert sha(cp) == progress['checkpoint']['sha256']
    doc = read(cp)
    by_generation = {}
    for generation in (78, 79, 80):
        ref = doc['next_model'] if generation == 80 else doc['played_bank'][generation]
        path = folder/'objects'/ref['file']
        assert sha(path) == ref['sha256']
        by_generation[generation] = read(path)
        identities[str(path)] = ref['sha256']
    costs[arm] = []
    for update in progress['updates']:
        path = folder/update['metrics']
        assert sha(path) == update['sha256']
        metric = read(path)
        costs[arm].append(dict(iteration=metric['iteration'], seconds=metric['seconds'],
            pipeline_wall=metric['timings']['pipeline_wall'], fit=metric['timings']['fit'],
            gpu_wait_seconds=update['competing_gpu_wait_seconds']))
        identities[str(path)] = update['sha256']
    models.append(by_generation)
comparisons = [compare_model_parts(models[0][generation], models[1][generation],
    registration['arms']['A-baseline']['config'], source, matrix) for generation in (78, 79, 80)]
assert comparisons[0]['models_identical']
assert comparisons[1]['root_regret_max_difference'] == 0
assert comparisons[1]['exact_btn_regret_max_difference'] == 0
assert comparisons[2]['exact_btn_regret_max_difference'] == 0
print(json.dumps(dict(passed=True, source='Completed seed A training only',
    generations=comparisons, costs=costs, identities=identities,
    held_out_evaluation_inspected=False, accuracy_claim=False,
    interpretation='Generation 80 is not in the played-policy bank. Training movement is not evidence of improved range quality.')))
