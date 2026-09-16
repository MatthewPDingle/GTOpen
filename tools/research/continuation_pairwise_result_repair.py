"""N25 output-only repair: preserve frozen numerical code and native JSON bools."""
import hashlib
import json
from pathlib import Path
import numpy as np
import continuation_pairwise_values as experiment


def native_bools(value):
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, dict):
        return {key: native_bools(item) for key, item in value.items()}
    if isinstance(value, list):
        return [native_bools(item) for item in value]
    return value


def run():
    source = Path(experiment.__file__)
    frozen = experiment.study.read(experiment.OUT/'protocol-freeze.json')
    key = str(source.relative_to(experiment.study.ROOT)).replace('\\', '/')
    expected = frozen['inputs'][key]
    assert experiment.study.pilot.sha(source) == expected
    assert not (experiment.OUT/'candidate.json').exists(), 'This recovery expects no candidate was written'
    assert not (experiment.OUT/'training-screen.json').exists(), 'Already recovered; inspect before rerunning'
    original_freeze = experiment.study.freeze
    experiment.study.freeze = lambda path, value: original_freeze(path, native_bools(value))
    experiment.run()
    assert experiment.study.pilot.sha(source) == expected
    experiment.study.night.dump(experiment.OUT/'output-repair.json', dict(
        cause='numpy.bool_ eligibility flag was not JSON serializable; first process exited 1 after all four training folds, before writing results or any candidate.',
        repair='Convert only numpy boolean scalars to native booleans at the output boundary; rerun exact deterministic frozen calculation. No numerical code, labels, model grid or gates changed.',
        original_source_sha256=expected,
        adapter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        result_sha256=experiment.study.pilot.sha(experiment.OUT/'training-screen.json'),
        production_enabled=False))


if __name__ == '__main__':
    assert native_bools({'eligible': np.bool_(False), 'score': 1.25}) == {'eligible': False, 'score': 1.25}
    assert json.dumps(native_bools([np.bool_(True)])) == '[true]'
    run()
