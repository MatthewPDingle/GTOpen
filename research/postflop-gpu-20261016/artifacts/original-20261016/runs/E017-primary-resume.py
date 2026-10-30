"""Continue the unchanged cohort after a pre-launch dashboard-ID collision."""
import json, subprocess, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
out=ar.RESEARCH/'runs/E017-primary-id-recovery';out.mkdir(exist_ok=False)
manifest=json.loads((ar.RESEARCH/'binaries/E017-postflop_autoresearch.manifest.json').read_text(encoding='utf-8'))
assert ar.source_identity()['source_sha256']==manifest['source_sha256']
assert not (ar.RESEARCH/'runs/E017').exists()
previous={}
for identity in ('V017-unit','V017-capacity','B053'):
    p=ar.RESEARCH/'runs'/identity/'report.json';r=json.loads(p.read_text(encoding='utf-8'))
    assert r['status']=='measured' and r['returncode']==0
    previous[identity]={'report_sha256':ar.sha256(p),'stdout_sha256':ar.sha256(p.with_name('stdout.log'))}
order=[('E017R1',True),('E017R2',True),('B054',False),('B055',False),('E017R3',True)]
for identity,_ in order:assert not (ar.RESEARCH/'runs'/identity).exists()
ar.atomic_json(out/'protocol.json',{'at':ar.now(),'reason':'Root reserved E017 dashboard row for source work. Runner refused its duplicate ID before creating the run directory or launching the candidate. Parent script exited1.',
 'failed_original_script':str(ar.RESEARCH/'runs/E017-primary.py'),'failed_original_script_sha256':ar.sha256(ar.RESEARCH/'runs/E017-primary.py'),
 'refusal':'Refused: Experiment ID already appears in dashboard: E017',
 'completed_unchanged_inputs':previous,'first_candidate_renamed':'E017R1','remaining_order':[x[0] for x in order],
 'pairs':[{'baseline':'B053','candidate':'E017R1'},{'baseline':'B054','candidate':'E017R2'},{'baseline':'B055','candidate':'E017R3'}],
 'timing_exclusions':[],'input_or_binary_change':False,'limits':'First pair has an operational pause after its baseline. Retain it and disclose chronology; no score was consulted to choose a replacement and no timing is discarded.'})
for identity,candidate in order:
    name='E017-postflop_autoresearch' if candidate else 'E015-postflop_autoresearch'
    subprocess.run([sys.executable,'tools/postflop_autoresearch.py','--id',identity,'--title','E017 filtered downward action work' if candidate else 'Accepted E015 paired-reuse reference',
      '--kind','candidate' if candidate else 'baseline','--binary',str(ar.RESEARCH/'binaries'/(name+'.exe')),
      '--build-manifest',str(ar.RESEARCH/'binaries'/(name+'.manifest.json')),'--test','postflop_complete_cycle'],cwd=repo,check=True)
ar.atomic_json(out/'completed.json',{'at':ar.now(),'additional_runs':5,'original_baseline_retained':'B053','accepted':False})
print('E017 primary cohort complete; original baseline retained.',flush=True)
