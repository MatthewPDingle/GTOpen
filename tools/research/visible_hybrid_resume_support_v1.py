"""Explicit provenance and immutable prefix seeding for the authorized reboot resume."""
import json
import os
from pathlib import Path
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_visible_hybrid_checkpoint_v1 import read_object

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
OLD = 'sampled-visible-hybrid-trial-pilot-v1'
NEW = 'sampled-visible-hybrid-resume-pilot-v1'
TD = ROOT/'tools/research'


def verify_lineage(reg):
    original = json.loads(Path(reg['original_registration']).read_text())
    pause = json.loads(Path(reg['pause_record']).read_text())
    review = json.loads(Path(reg['prefix_review']).read_text())
    stopped = json.loads((OUT/f'{OLD}-status.json').read_text())
    latest = json.loads((Path(original['store'])/'latest.json').read_text())
    assert original['config'] == reg['config']
    assert pause['state'] == 'paused_by_user_for_reboot' and pause['checkpoint_restore_verified']
    assert pause['completed_iterations'] == latest['completed_iterations'] == review['completed_iterations'] == 48
    assert pause['checkpoint'] == latest['checkpoint'] == review['checkpoint'] == reg['resume_checkpoint']
    assert review['passed'] and not review['terminal_complete']
    assert review['source_registration_sha256'] == sha(reg['original_registration'])
    assert stopped['state'] == 'stopped' and stopped['exit_code'] == 15
    assert reg['prior_execution_seconds'] == stopped['execution_seconds']
    assert reg['maximum_seconds'] + reg['prior_execution_seconds'] == original['maximum_seconds'] == 10800
    assert latest['config'] == reg['checkpoint_config']
    for path, expected in {**original['inputs'], **reg['inputs']}.items():
        assert sha(ROOT/path) == expected, path
    return original, review


def register(source):
    original_path = OUT/f'{OLD}-registration.json'
    original = json.loads(original_path.read_text())
    source_store = Path(original['store'])
    latest = json.loads((source_store/'latest.json').read_text())
    prefix_review = OUT/f'{OLD}-prefix-0048-review.json'
    pause = OUT/'sampled-visible-hybrid-trial-reboot-pause-20260923.json'
    stopped = json.loads((OUT/f'{OLD}-status.json').read_text())
    control_path = OUT/'sampled-visible-hybrid-resume-control-v1-result.json'
    control = json.loads(control_path.read_text())
    assert control['passed'] and control['checkpoint'] == latest['checkpoint']
    for p,h in control['inputs'].items():
        assert sha(p) == h, p
    scripts = list(TD.glob('hu_visible_hybrid_resume_*_20260923.py'))
    paths = [source, Path(__file__), TD/'reboot_research_idle_v1.py',
        TD/'hu_visible_resume_prefix_audit_20260923.py', original_path, prefix_review,
        pause, source_store/'latest.json', OUT/f'{OLD}-status.json',
        OUT/'sampled-visible-hybrid-resume-prefix-audit-v1-registration.json',
        control_path, *scripts]
    inputs = dict(original['inputs'])
    inputs.update({str(p):sha(p) for p in paths})
    inputs.update(control['inputs'])
    reg = dict(original, inputs=inputs, store=str(Path('S:/GTOpen-research')/NEW),
        maximum_seconds=10800-stopped['execution_seconds'],
        original_registration=str(original_path), prefix_review=str(prefix_review),
        pause_record=str(pause), source_store=str(source_store),
        resume_checkpoint=latest['checkpoint'], checkpoint_config=latest['config'],
        prior_execution_seconds=stopped['execution_seconds'],
        candidate='User-authorized continuation of the original fixed 78-update trial after reboot; completed prefix 48 retained exactly; no checkpoint selection.',
        stopping='30 remaining updates, within the original cumulative three-hour training cap excluding reboot downtime and offline audits; no automatic retries.',
        resume_protocol='Separate store; hard-link only immutable complete-prefix files and referenced immutable objects. Never link latest.json or copy incomplete iteration 49. Original stopped status remains intact.')
    verify_lineage(reg)
    return reg


def seed_store(reg, destination):
    original, review = verify_lineage(reg)
    source = Path(original['store']).resolve(); destination = Path(destination).resolve()
    assert source != destination and source.parent == destination.parent
    assert not destination.exists()
    destination.mkdir(); (destination/'checkpoint-objects').mkdir()
    imported = {}

    def link(path, expected=None):
        path = path.resolve(); relative = path.relative_to(source)
        target = destination/relative
        assert not target.exists()
        if expected is not None:
            assert sha(path) == expected, path
        target.parent.mkdir(parents=True, exist_ok=True)
        os.link(path, target)
        assert os.path.samefile(path, target)
        imported[str(relative)] = expected or sha(path)

    references = {}
    for i in range(49):
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
            for name,h in batch['artifacts'].items():
                link(metric_path.parent/f'batch-{chunk:02d}'/name, h)
    for name,h in references.items():
        link(source/'checkpoint-objects'/name, h)
    save(destination/'imported-prefix.json',dict(source=str(source),completed_iterations=48,
        checkpoint=reg['resume_checkpoint'],immutable_files=imported))
    # An independent mutable pointer, never a hard link to the old run.
    save(destination/'latest.json',dict(completed_iterations=48,
        checkpoint=reg['resume_checkpoint'], config=reg['checkpoint_config']))
