"""Require the complete repaired hybrid workflow before the next fixed trial."""
import json
from sampled_physical_root_evaluation_v1 import ROOT, sha


def completed_hybrid_paths(out):
    paths = []

    def read(name):
        path = out / name
        value = json.loads(path.read_text())
        paths.append(path)
        return value

    def verify(inputs):
        for path, expected in inputs.items():
            assert sha(path) == expected, path

    prefix = 'sampled-physical-hybrid-repair-v1'
    registration = read(prefix + '-registration.json')
    status = read(prefix + '-status.json')
    assert status['state'] == 'complete' and status['error'] is None
    assert status['registration_sha256'] == sha(out / (prefix + '-registration.json'))
    assert [r['stage'] for r in status['completed_stages']] == [s[0] for s in registration['stages']]
    assert len(status['completed_stages']) == 6
    for record in status['completed_stages']:
        assert record['exit_code'] == 0
        assert sha(record['log']) == record['log_sha256']
    verify(registration['inputs'])

    prefix = 'sampled-physical-hybrid-evaluation-v2'
    registration = read(prefix + '-registration.json')
    status = read(prefix + '-status.json')
    review = read(prefix + '-independent-review.json')
    result_path = out / (prefix + '-result.json')
    paths.append(result_path)
    assert status['state'] == 'complete' and status.get('error') is None
    assert review['passed']
    assert review['registration_sha256'] == sha(out / (prefix + '-registration.json'))
    assert review['result_sha256'] == sha(result_path)
    assert review['terminal_status_sha256'] == sha(out / (prefix + '-status.json'))
    assert review['training_deals_replayed'] == 8192 and review['evaluation_deals_replayed'] == 16384
    assert review['reviewer_sha256'] == sha(ROOT / 'tools/research/hu_sampled_physical_hybrid_evaluation_review_20260923.py')
    verify(registration['inputs'])

    prefix = 'sampled-physical-hybrid-btn-jam-diagnosis-v1'
    review = read(prefix + '-independent-review.json')
    assert review['passed'] and review['paired_differences_reconstructed'] == 16384
    assert review['reviewer_sha256'] == sha(ROOT / 'tools/research/hu_sampled_physical_hybrid_btn_jam_review_20260923.py')
    verify(review['inputs'])
    paths.extend(map(type(out), review['inputs']))
    paths.append(out / 'sampled-physical-hybrid-comparison-v1-result.json')
    assert paths[-1].is_file()
    return list(dict.fromkeys(paths))
