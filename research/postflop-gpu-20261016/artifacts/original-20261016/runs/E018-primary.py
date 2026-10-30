"""Serialized unit screen followed by three fixed E015/E018 alternating pairs."""
import json,subprocess,sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
def run(identity,name,kind,title,test='postflop_complete_cycle',ordinary=False):
    command=[sys.executable,'tools/postflop_autoresearch.py','--id',identity,'--title',title,'--kind',kind,
      '--binary',str(ar.RESEARCH/'binaries'/(name+'.exe')),'--build-manifest',str(ar.RESEARCH/'binaries'/(name+'.manifest.json')),'--test',test]
    if ordinary:command.append('--not-ignored')
    subprocess.run(command,cwd=repo,check=True)
    report=json.loads((ar.RESEARCH/'runs'/identity/'report.json').read_text(encoding='utf-8'))
    assert report['returncode']==0 and report['status']=='measured' and report['test_pass_count']>0,identity
run('V018-unit','E018-solver','validation','E018 GPU solver unit tests','*',True)
run('V018-capacity','E018-continuation-tests','validation','E018 child-value table continuation capacity accuracy',
  'gpu::continuation_capacity::tests::child_mapping_matches_observed_metadata_for_turn_and_river',True)
for identity,candidate in [('B056',False),('E018R1',True),('E018R2',True),('B057',False),('B058',False),('E018R3',True)]:
    run(identity,'E018-postflop_autoresearch' if candidate else 'E015-postflop_autoresearch','candidate' if candidate else 'baseline',
      'E018 precomputed child-value addresses' if candidate else 'Accepted E015 paired-reuse reference')
print('E018 unit screen and all three primary pairs complete.',flush=True)
