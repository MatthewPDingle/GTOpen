"""Admit a bounded completion after the prospectively handled time-cap stop."""
import json
import os
from pathlib import Path
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_visible_hybrid_checkpoint_v1 import read_object
from visible_hybrid_resume_support_v1 import verify_lineage as verify_parent

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
OLD = 'sampled-visible-hybrid-resume-pilot-v1'
NEW = 'sampled-visible-hybrid-completion-pilot-v1'
TD = ROOT/'tools/research'


def verify_lineage(reg):
    parent = json.loads(Path(reg['parent_registration']).read_text())
    verify_parent(parent)
    stopped = json.loads((OUT/f'{OLD}-status.json').read_text())
    latest = json.loads((Path(parent['store'])/'latest.json').read_text())
    review = json.loads(Path(reg['prefix_review']).read_text())
    assert stopped['state'] == 'stopped' and stopped['error'] == 'Execution deadline'
    assert reg['config'] == parent['config'] and reg['config']['max_iterations'] == 78
    completed = latest['completed_iterations']
    assert 72 <= completed < 78 and completed == reg['completed_prefix'] == review['completed_iterations']
    assert review['passed'] and not review['terminal_complete']
    assert review['source_registration_sha256'] == sha(reg['parent_registration'])
    assert latest['checkpoint'] == reg['resume_checkpoint'] == review['checkpoint']
    assert latest['config'] == reg['checkpoint_config']
    assert reg['maximum_seconds'] == 1200
    assert reg['prior_execution_seconds'] == parent['prior_execution_seconds'] + stopped['execution_seconds']
    assert reg['original_training_cap_seconds'] == 10800 and reg['original_cap_passed'] is False
    for p, h in reg['inputs'].items():
        assert sha(ROOT/p) == h, p
    return parent, review


def register(source):
    parent_path = OUT/f'{OLD}-registration.json'
    parent = json.loads(parent_path.read_text())
    store = Path(parent['store']); latest = json.loads((store/'latest.json').read_text())
    completed = latest['completed_iterations']
    prefix_review = OUT/f'{OLD}-prefix-{completed:04d}-review.json'
    stopped_path = OUT/f'{OLD}-status.json'; stopped = json.loads(stopped_path.read_text())
    control_path = OUT/'sampled-visible-hybrid-completion-control-v1-result.json'
    control = json.loads(control_path.read_text())
    assert control['passed'] and control['checkpoint'] == latest['checkpoint']
    for p, h in control['inputs'].items():
        assert sha(p) == h, p
    paths = [source, Path(__file__), parent_path, prefix_review, stopped_path, store/'latest.json',
        OUT/f'{OLD}-resources.json', OUT/'sampled-visible-hybrid-resume-study-v1-status.json',
        OUT/'VISIBLE-HYBRID-TIME-CAP-CONTINGENCY.md', control_path,
        OUT/'sampled-visible-hybrid-completion-prefix-audit-v1-registration.json',
        TD/'reboot_research_idle_v1.py', TD/'visible_hybrid_resume_support_v1.py',
        *TD.glob('hu_visible_hybrid_completion_*_20260923.py')]
    inputs = dict(parent['inputs']); inputs.update(control['inputs'])
    inputs.update({str(p): sha(p) for p in paths})
    reg = dict(parent, inputs=inputs, store=str(Path('S:/GTOpen-research')/NEW),
        maximum_seconds=1200, parent_registration=str(parent_path), source_store=str(store),
        prefix_review=str(prefix_review), completed_prefix=completed,
        resume_checkpoint=latest['checkpoint'], checkpoint_config=latest['config'],
        prior_execution_seconds=parent['prior_execution_seconds']+stopped['execution_seconds'],
        original_training_cap_seconds=10800, original_cap_passed=False,
        candidate='Complete the originally fixed 78-update candidate after a preserved time-limit stop; no intermediate policy selection.',
        stopping='Only the remaining updates through 78, with 1200 extra controller seconds. No further automatic extension.',
        resume_protocol='Separate store of immutable complete prefix and checkpoint objects. Exclude interrupted next update. Original capped attempt remains incomplete.')
    verify_lineage(reg)
    return reg


def seed_store(reg, destination):
    parent, review = verify_lineage(reg)
    source = Path(parent['store']).resolve(); destination = Path(destination).resolve()
    assert source != destination and source.parent == destination.parent
    assert not destination.exists()
    destination.mkdir(); (destination/'checkpoint-objects').mkdir()
    imported = {}

    def link(path, expected=None):
        path = path.resolve(); relative = path.relative_to(source); target = destination/relative
        assert not target.exists()
        if expected is not None:
            assert sha(path) == expected, path
        target.parent.mkdir(parents=True, exist_ok=True)
        os.link(path, target)
        assert os.path.samefile(path, target)
        imported[str(relative)] = expected or sha(path)

    references = {}
    for i in range(reg['completed_prefix']+1):
        checkpoint_path = source/f'checkpoint-{i:04d}.json'
        ref = json.loads(checkpoint_path.read_text())
        document = json.loads(read_object(source/'checkpoint-objects', ref))
        assert document['completed_iterations'] == i
        link(checkpoint_path)
        for item in [ref, document['next_model'], *document['played_bank'], *document['reservoirs']]:
            references[item['file']] = item['sha256']
        if i == 0:
            continue
        metric_path = source/f'iteration-{i:04d}'/'metrics.json'
        assert review['steps'][i-1]['checkpoint'] == ref
        link(metric_path, review['steps'][i-1]['metrics_sha256'])
        metric = json.loads(metric_path.read_text())
        for chunk, batch in enumerate(metric['subbatches']):
            for name, h in batch['artifacts'].items():
                link(metric_path.parent/f'batch-{chunk:02d}'/name, h)
    for name, h in references.items():
        link(source/'checkpoint-objects'/name, h)
    save(destination/'imported-prefix.json', dict(source=str(source), completed_iterations=reg['completed_prefix'],
        checkpoint=reg['resume_checkpoint'], immutable_files=imported))
    save(destination/'latest.json', dict(completed_iterations=reg['completed_prefix'],
        checkpoint=reg['resume_checkpoint'], config=reg['checkpoint_config']))
