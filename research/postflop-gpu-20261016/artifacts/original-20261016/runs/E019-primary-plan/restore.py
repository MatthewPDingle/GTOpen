import json, shutil, sys
from pathlib import Path
repo = Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0, str(repo / 'tools'))
import postflop_autoresearch as ar
base=ar.RESEARCH
owned='crates/solver/src/gpu/kernels.cu'
assert not (base / 'gpu-run.lock').exists()
assert (base / 'runs/E019-primary-execution/complete.json').is_file()
assessment=json.loads((base / 'comparisons/E019-three-pair-comparison/report.json').read_text(encoding='utf-8'))
assert assessment['decision']=='rejected' and not assessment['accepted']
manifest_path=base / 'binaries/E019-postflop_autoresearch.manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
before=ar.source_identity()
assert before['source_sha256']==manifest['source_sha256']
candidate_sha='9eff0e598c69bafcf4dc8a04ad116bd25482b06bd9bde34c143d45688ab5505a'
accepted_sha='8fe86cb859124592f9df13821f4a300450045620e6947e99466e4228b78c20d0'
for p in [repo/owned,base/'runs/E019-source/candidate.cu',base/'runs/E019-build/candidate.cu',base/'runs/D036-fold-shuffle-probe-r3/candidate.cu']:
    assert ar.sha256(p)==candidate_sha,str(p)
restore_source=base/'runs/E019-source/accepted.cu'
assert ar.sha256(restore_source)==accepted_sha
assert ar.sha256(ar.APP/owned)==accepted_sha
for name in ['E019-solver','E019-postflop_autoresearch']:
    m=json.loads((base/'binaries'/f'{name}.manifest.json').read_text(encoding='utf-8'))
    assert ar.sha256(base/'binaries'/f'{name}.exe')==m['binary_sha256']
assert ar.sha256(base/'runs/E019-build/candidate.patch')==ar.sha256(base/'runs/E019R1.patch')
shutil.copyfile(restore_source,repo/owned)
after=ar.source_identity()
accepted=json.loads((base/'binaries/E015-postflop_autoresearch.manifest.json').read_text(encoding='utf-8'))
assert after['source_sha256']==accepted['source_sha256']
record=base/'runs/E019-cleanup-restored-E015.json'
assert not record.exists()
ar.atomic_json(record,{'at':ar.now(),'candidate':'E019','decision':'rejected','changed_paths':[owned],
    'candidate_source_sha256':candidate_sha,'restored_source_sha256':accepted_sha,
    'all_accepted_source_entries_match':True,'source_entry_count':len(after['source_sha256']),
    'before_source_identity':before,'after_source_identity':after,
    'candidate_manifest_sha256':ar.sha256(manifest_path),'comparison_sha256':ar.sha256(base/'comparisons/E019-three-pair-comparison/report.json'),
    'candidate_source_binaries_and_measurements_preserved':True,'main_and_live_mutated':False})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    s=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    row=next(r for r in s['experiments'] if r['id']=='E019')
    row.update(updated_at=ar.now(),details='Rejected:0.7172% observed aggregate improvement below2% gate. All18 compressed non-timing screens exact;84 unit tests passed. All162 accepted E015 source identities restored. Independent terminal audit pending; broader qualification not run after failed primary screen.')
    s.update(updated_at=ar.now(),active_experiment=None,stage='E019 rejected; accepted source restored',activity='Fold reduction candidate did not meet the2% complete-solve gain threshold. Raw evidence preserved; independent audit in progress. Next source hypothesis under review; accepted E015 remains9.62%.')
    ar.atomic_json(ar.STATUS,s)
print('Restored all',len(after['source_sha256']),'accepted source entries. Cleanup SHA256:',ar.sha256(record))
