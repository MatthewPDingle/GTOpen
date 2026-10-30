import json, shutil, sys
from pathlib import Path
repo = Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0, str(repo / 'tools'))
import postflop_autoresearch as ar
review = ar.RESEARCH / 'comparisons/E020-independent-review'
pins = {
    'validation.json': 'ee2992d1066faeaf782f5276f7558521990f40a5cfbeece91cade970464fd438',
    'summary.md': '174e9859c23f4b7d6a869810593cb75a19bce876e9d4bb5d93208fad09178a66',
    'manifest.json': '764ddfd51fc33450f1d179a7933b5380397bd6faa1a6baafe007891d446bb5cc',
}
for name, expected in pins.items():
    source = review / name
    assert ar.sha256(source) == expected
    target = ar.DASHBOARD / 'evidence/E020-independent-review' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert ar.sha256(target) == expected
    else:
        shutil.copyfile(source, target)
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'), timeout=3):
    s = json.loads(ar.STATUS.read_text(encoding='utf-8'))
    for identity in ['E020', 'E020R1']:
        row = next(r for r in s['experiments'] if r['id'] == identity)
        row.update(updated_at=ar.now(), stage='Primary audit passed; broader qualification pending',
            reason='Provisional primary PASS: 10486.8499 to 10254.6581 ms, 2.2141% lower complete-solve time versus accepted E015. Independent audit confirms all 18 full non-timing results and 138 convergence records exact, and no fixture regression guard failure. Broader controls, prospective wide-range holdout and fresh original-baseline comparison remain required.',
            details='802 independent audit assertions passed. All six fixed timing runs retained. Full-range holdout was sealed and reviewed before primary execution. No acceptance, deployment, significance or all-workload claim; accepted cumulative improvement remains 9.62%.')
        for label, name in [('Independent primary audit', 'summary.md'), ('Independent audit details', 'validation.json')]:
            url = 'evidence/E020-independent-review/' + name
            if not any(e['url'] == url for e in row['evidence']):
                row['evidence'].append({'label': label, 'url': url})
    unit = next(r for r in s['experiments'] if r['id'] == 'V020-unit')
    unit.update(correctness='pass', reason='Independent audit confirms 84 passed, zero failed and four ignored; same test inventory as accepted E015.')
    s.update(updated_at=ar.now(), active_experiment=None, stage='Preparing E020 broader qualification',
        activity='E020 primary audit passed. Preparing identical full-range holdout evaluators and broader original-baseline correctness controls; no additional GPU timing until all binaries and execution plans are frozen and independently reviewed.')
    ar.atomic_json(ar.STATUS, s)
print('Published audited provisional E020 primary result; accepted headline unchanged.')
