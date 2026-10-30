"""Recover only the independently audited prefix after an unexpected reboot."""
import json
import os
import shutil
from pathlib import Path
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read

OLD = 'root-retained-replication-v1'
PREFIX = 'root-retained-replication-prefix-v1'


def admit_resume(reg, source):
    old_path = OUT/f'{OLD}-registration.json'
    old = read(old_path)
    pp = OUT/f'{PREFIX}-result.json'
    rp = OUT/f'{PREFIX}-registration.json'
    audit_path = OUT/f'{PREFIX}-independent-review.json'
    reader_path = OUT/f'{PREFIX}-readback-registration.json'
    incident_path = OUT/'root-retained-replication-reboot-20260924.json'
    control_path = OUT/'root-retained-replication-resume-control-v1-result.json'
    prefix, audit, incident, control = map(read, (pp,audit_path,incident_path,control_path))
    assert old['config'] == reg['config']
    assert audit['passed'] and audit['completed_updates'] == 5 and not audit['terminal_complete']
    assert audit['source_registration_sha256'] == sha(rp)
    assert audit['source_result_sha256'] == sha(pp)
    assert audit['readback_registration_sha256'] == sha(reader_path)
    assert prefix['passed'] and not prefix['terminal'] and prefix['completed_iterations'] == 5
    assert incident['original_registration_sha256'] == sha(old_path)
    assert prefix['final_checkpoint'] == incident['checkpoint'] == control['checkpoint']
    assert control['passed'] and control['next_action_stream_verified']
    assert prefix['config'] == read(OUT/f'{OLD}-environment.json')
    assert incident['prior_runtime_charge_seconds'] == 2280
    assert incident['remaining_runtime_seconds'] + 2280 == old['maximum_seconds'] == 21600
    for evidence in (old['inputs'], read(reader_path)['inputs'], control['inputs']):
        for p,h in evidence.items():
            assert sha(ROOT/p) == h, p
        reg['inputs'].update(evidence)
    paths = [old_path,pp,rp,audit_path,reader_path,incident_path,control_path,
             Path(__file__),source,OUT/f'{OLD}-environment.json']
    reg['inputs'].update({str(p):sha(p) for p in paths})
    reg.update(maximum_seconds=19320,prior_runtime_charge_seconds=2280,
        original_registration=str(old_path),resume_checkpoint=prefix['final_checkpoint'],
        prefix_result=str(pp),prefix_steps=prefix['steps'],checkpoint_config=prefix['config'],
        changes='Same algorithm and random streams as the interrupted replication. Import the independently audited five-update prefix; redo incomplete update 6 from its preceding checkpoint.',
        stopping='Complete original 78 updates within the remaining 19320 seconds; 2280 seconds charged to the interrupted run. No score-based selection or automatic retry.',
        initialization='Restored generation 5, preserving the original fresh uniform generation 0 and entire played bank.')


def import_prefix(reg, destination):
    source = Path(read(reg['original_registration'])['store']).resolve()
    destination = Path(destination).resolve()
    assert source != destination and source.parent == destination.parent
    result = read(reg['prefix_result'])
    imported = {}
    for name,h in result['artifacts'].items():
        original = Path(name).resolve()
        relative = original.relative_to(source)
        target = destination/relative
        assert sha(original) == h and not target.exists()
        target.parent.mkdir(parents=True,exist_ok=True)
        with original.open('rb') as src, target.open('xb') as dst:
            shutil.copyfileobj(src,dst)
            dst.flush();os.fsync(dst.fileno())
        assert sha(target) == h
        imported[str(relative)] = h
    save(destination/'imported-prefix.json',dict(source=str(source),completed_iterations=5,
        original_registration_sha256=sha(reg['original_registration']),
        prefix_result_sha256=sha(reg['prefix_result']),files=imported))


def durable_iteration(folder, pointer):
    # Checkpoint objects already fsync at publication. Flush raw evidence and
    # its small pointer before publishing the next mutable progress indicator.
    for path in [*Path(folder).rglob('*'),Path(pointer)]:
        if path.is_file():
            with path.open('r+b') as stream:
                os.fsync(stream.fileno())
