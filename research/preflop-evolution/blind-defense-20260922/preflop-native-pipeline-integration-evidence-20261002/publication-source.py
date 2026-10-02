"""Publish exact qualified native pipeline sources and compact retained evidence."""
import hashlib
import json
from pathlib import Path

STAGE=Path(__file__).resolve().parent
ROOT=Path(r'T:\Dev\GTOpen'); TOOLS=ROOT/'tools/research'
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
DEST=OUT/'preflop-native-pipeline-integration-evidence-20261002'
PROFILE=Path(r'S:\GTOpen-research\preflop-expected-native-cycle-profile-v1')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_bytes())
def write(path,raw):
    path=Path(path)
    if not path.resolve().is_relative_to(ROOT.resolve()): raise ValueError('Publication escaped GTOpen')
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=raw: raise ValueError('Preserve differing destination: '+str(path))
    else:
        with path.open('xb') as stream: stream.write(raw)


sources=['preflop_expected_native_execution_v1.py','preflop_expected_native_execution_check_v1.py',
 'preflop_expected_board_workers_v1.py','preflop_expected_board_workers_check_v1.py',
 'preflop_expected_river_workers_v1.py','preflop_expected_river_transport_v1.py',
 'preflop_expected_river_workers_source_check_v1.py',
 'preflop_expected_training_pipeline_v1.py','preflop_expected_training_pipeline_check_v2.py',
 'preflop_expected_pipeline_board_admission_check_v1.py','preflop_expected_worker_cancellation_v1.py',
 'preflop_expected_board_cancellation_check_v1.py','preflop_expected_river_cancellation_check_v1.py',
 'preflop_expected_native_cycle_profile_v1.py','preflop_expected_profile_resource_check_v1.py',
 'preflop_expected_profile_storage_options_analysis_v1.py']

evidence=[(PROFILE/name,'native-profile/'+name) for name in
 ('registration.json','attempt.json','result.json','released.json','cycle-0001/metrics.json')]
for folder in ('preflop-expected-native-execution-control-v1','preflop-expected-pipeline-control-v2-362',
 'preflop-expected-pipeline-control-v2-387','preflop-expected-pipeline-cancellation-control-v3-362',
 'preflop-expected-pipeline-cancellation-control-v3-387','preflop-expected-pipeline-board-admission-control-v1',
 'preflop-expected-board-cancellation-control-v1','preflop-expected-profile-resource-control-v1'):
    evidence.append((STAGE/folder/'result.json','controls/'+folder+'.json'))
for name in ('preflop-expected-river-cancellation-control-v1-result.json',
 'preflop-expected-native-cycle-profile-v1-inventory.json','preflop-expected-profile-resource-analysis-v1.json',
 'preflop-expected-profile-storage-options-analysis-v1.json','preflop-expected-profile-resource-planning-v1.txt',
 'preflop-expected-board-pre-cancellation-source-archive-v1.json','preflop-expected-river-pre-cancellation-source-archive-v1.json',
 'preflop-expected-board-workers-source-control-v1-result.txt','preflop-expected-board-workers-cancellation-regression-v1-result.txt'):
    evidence.append((STAGE/name,'controls/'+name))
for folder in ('preflop-expected-native-cycle-independent-readback-v1','preflop-expected-native-cycle-independent-readback-v2'):
    for p in sorted((STAGE/folder).iterdir()):
        if p.is_file(): evidence.append((p,'independent/'+folder+'/'+p.name))
for p in sorted(STAGE.glob('*pre-cancellation-snapshot.py')):
    evidence.append((p,'source-snapshots/'+p.name))
evidence.append((STAGE/'preflop_expected_training_pipeline_check_v1.py','source-snapshots/failed-coordinator-summary-control-v1.py'))
evidence.append((STAGE/'preflop_expected_preserve_pipeline_snapshot_v1.py','source-snapshots/preserve_pipeline_snapshot_v1.py'))

registration=read(PROFILE/'registration.json'); result=read(PROFILE/'result.json')
audit=read(STAGE/'preflop-expected-native-cycle-independent-readback-v2/result.json')
assert result['passed'] and audit['passed'] and result['completed_cycles']==1 and not result['scientific_accuracy_qualified']
assert not (PROFILE/'failure.json').exists() and (PROFILE/'released.json').exists()
assert result['registration_sha256']==sha(PROFILE/'registration.json')
assert result['attempt_sha256']==sha(PROFILE/'attempt.json') and result['metrics_sha256']==sha(PROFILE/'cycle-0001/metrics.json')
for p,h in registration['config']['source_identities'].items(): assert sha(p)==h,p
for p,_ in evidence:
    assert p.is_file(),p
for name in sources: assert (STAGE/name).is_file(),name
if DEST.exists(): raise ValueError('Preserve existing publication receipt directory')

copied=[]; inputs={}
for name in sources:
    p=STAGE/name; target=TOOLS/name; inputs[str(p)]=sha(p)
    write(target,p.read_bytes()); assert sha(target)==inputs[str(p)]
    copied.append(dict(path=str(target),sha256=sha(target)))
for p,suffix in evidence:
    inputs[str(p)]=sha(p); target=DEST/suffix
    write(target,p.read_bytes()); assert sha(target)==inputs[str(p)]
    copied.append(dict(path=str(target),sha256=sha(target)))
note=STAGE/'STACK-CONTEXT-NATIVE-PIPELINE-20261002.md'; inputs[str(note)]=sha(note)
target=OUT/note.name; write(target,note.read_bytes()); copied.append(dict(path=str(target),sha256=sha(target)))
publication_source=DEST/'publication-source.py'; write(publication_source,Path(__file__).read_bytes())
copied.append(dict(path=str(publication_source),sha256=sha(publication_source)))
manifest=dict(format=1,qualified_scope='Exact source publication, synthetic controls and one audited native20bb software/resource cycle',
 scientific_accuracy_qualified=False,production_modified=False,github_pushed=False,
 inputs=inputs,outputs=copied,native_registration_sha256=sha(PROFILE/'registration.json'),
 independent_readback_sha256=sha(STAGE/'preflop-expected-native-cycle-independent-readback-v2/result.json'))
receipt=DEST/'publication.json'; write(receipt,(json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n').encode())
paths=[str(Path(r['path']).relative_to(ROOT)).replace('\\','/') for r in copied]+[str(receipt.relative_to(ROOT)).replace('\\','/')]
path_file=DEST/'git-paths.json'; write(path_file,(json.dumps(paths+[str(path_file.relative_to(ROOT)).replace('\\','/')])+'\n').encode())
print(json.dumps(dict(published=True,sources=len(sources),evidence=len(evidence),outputs=len(copied),
 receipt=str(receipt),sha256=sha(receipt),git_paths=str(path_file))))
