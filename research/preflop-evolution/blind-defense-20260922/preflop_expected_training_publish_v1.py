"""Exact reviewed publication of new sources and separate software evidence."""
import hashlib,json
from pathlib import Path
STAGE=Path(__file__).resolve().parent
TOOLS=Path(r'T:\Dev\GTOpen\tools\research')
OUT=TOOLS.parents[1]/'research/preflop-evolution/blind-defense-20260922'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources=['preflop_expected_training_checkpoint_v1.py','preflop_expected_training_fit_v1.py',
    'preflop_expected_training_control_fixture_v1.py','preflop_expected_training_checkpoint_check_v1.py',
    'preflop_expected_training_cuda_check_v1.py']
controls=['preflop-expected-training-checkpoint-control-v2-result.json','preflop-expected-training-cuda-control-v2-result.json']
for name in controls:
    value=json.loads((STAGE/name).read_bytes());assert value['passed'] and not value['scientific_attempt']
    for p,h in value['inputs'].items():assert sha(p)==h,(p,h)
pins={
 'stack-context-matched-evaluation-v5-result.json':'dd31ef7b49b75cd586d3d69769cb4d6fd8fc0cb4d81230330da7c7c59ab4ae96',
 'STACK-CONTEXT-FINDINGS-20261002.md':'7af730b47a02c837b1dbf3964ec66fa79276a3d815277dbdc78a20b74ab402de',
 'STACK-CONTEXT-AA-DIAGNOSIS-20261002.md':'e9789d5e5ceac94329f57fceda6e3871c0b75271a7062edbf9e727e4e71c6cb9',
 'STACK-CONTEXT-PREFLOP-EXPECTED-TARGETS-20261002.md':'fa4be0de7c91156e77344bdbe66dac84b0654b65bd456e6b9c5e923865018077',
 'STACK-CONTEXT-PREFLOP-CUMULATIVE-STATE-20261002.md':'01564493e0f89237add8c1d0ff5bdc50ccc322e1d4abf5b0440bae788a32ee37',
 'STACK-CONTEXT-PREFLOP-POLICY-INTEGRATION-20261002.md':'afa6072e4d9d04cb2d13486becabba0a19f4eae17db51c4f918598543e726cc5'}
for name,h in pins.items():assert sha(OUT/name)==h,name
copies={};snapshots={}
def copy_file(source,destination):
    raw=source.read_bytes()
    assert destination.resolve().parent in (TOOLS.resolve(),OUT.resolve())
    if destination.exists():assert destination.read_bytes()==raw,destination
    else:
        with destination.open('xb') as out:out.write(raw)
    copies[str(destination)]=dict(source=str(source),sha256=sha(source));return destination
preserved=json.loads((STAGE/'preflop-expected-training-initial-preservation-v1.json').read_bytes())
for original,ref in preserved['sources'].items():
    snapshot=Path(ref['snapshot']);assert sha(snapshot)==ref['sha256']
    destination=OUT/(Path(original).stem+'-initial-training-staging.py')
    copy_file(snapshot,destination);snapshots[original]=dict(path=str(destination),sha256=ref['sha256'])
    if Path(original).name not in sources:assert sha(TOOLS/Path(original).name)==ref['sha256'],original
for name in sources:
    copy_file(STAGE/name,TOOLS/name)
    copy_file(STAGE/name,OUT/(Path(name).stem+'-training-staging.py'))
for name in [*controls,'preflop-expected-training-checkpoint-control-v1-result.json',
    'preflop-expected-training-cuda-control-v1-result.json','preflop-expected-training-initial-preservation-v1.json',
    'preflop-expected-training-control-v1-environment-failure.txt',Path(__file__).name,
    'preflop_expected_training_preserve_initial_v1.py']:
    copy_file(STAGE/name,OUT/name)
receipt=dict(format=1,byte_copies=copies,initial_source_snapshots=snapshots,
    original_pins=pins,scientific_attempt=False,production_modified=False,push=False,deployment=False)
target=OUT/'preflop-expected-training-publication-v1.json'
with target.open('x',encoding='utf-8') as out:json.dump(receipt,out,indent=2,allow_nan=False)
print(json.dumps(dict(publication=str(target),copied_files=len(copies),sha256=sha(target))))
