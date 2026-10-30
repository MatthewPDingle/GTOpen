"""Serialized unit screen followed by three fixed E015/E017 alternating pairs."""
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
run('V017-unit','E017-solver','validation','E017 GPU solver unit tests','*',True)
run('V017-capacity','E017-continuation-tests','validation','E017 mixed/uniform continuation capacity accuracy',
  'gpu::continuation_capacity::tests::optional_down_list_matches_observed_metadata_for_mixed_and_uniform_plans',True)
for identity,candidate in [('B053',False),('E017',True),('E017R2',True),('B054',False),('B055',False),('E017R3',True)]:
    run(identity,'E017-postflop_autoresearch' if candidate else 'E015-postflop_autoresearch','candidate' if candidate else 'baseline',
      'E017 filtered downward action work' if candidate else 'Accepted E015 paired-reuse reference')
print('E017 unit screen and all three primary pairs complete.',flush=True)
