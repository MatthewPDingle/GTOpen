"""Assess the prospectively fixed cohort once; no acceptance or reruns."""
import json, shutil, subprocess, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
import postflop_compare as comp
out=ar.RESEARCH/'runs/E018-primary-assessment';out.mkdir(exist_ok=False)
source=ar.RESEARCH/'runs/E018-build/candidate.patch'
design=ar.RESEARCH/'runs/E018-design-r2/candidate.patch'
assert ar.sha256(source)==ar.sha256(design)
alias=ar.RESEARCH/'runs/E018R1.patch';assert not alias.exists();shutil.copyfile(source,alias)
ar.atomic_json(out/'comparison-adapter.json',{'at':ar.now(),'logical_candidate':'E018','measured_candidate':'E018R1',
 'source_patch':str(source),'design_patch':str(design),'alias_patch':str(alias),'all_patch_sha256':ar.sha256(source),
 'reason':'The comparison helper requires an actual measured run and adjacent frozen patch. E018 is reserved for the logical dashboard row.',
 'timing_exclusions':[]})
baseline=['B056','B057','B058'];candidate=['E018R1','E018R2','E018R3']
frozen=json.loads((ar.RESEARCH/'baseline-manifest.json').read_text(encoding='utf-8-sig'))
result=comp.summarize([comp.load_run(x)[0] for x in baseline],[comp.load_run(x)[0] for x in candidate],comp.source_hashes(frozen))
failures=comp.rejection_reasons(result['performance'])
command=[sys.executable,'tools/postflop_compare.py','--id','E018-three-pair-comparison','--candidate-id','E018R1',
 '--baseline-runs',*baseline,'--candidate-runs',*candidate,'--warm-cache-cohort']
if failures:command.append('--reject')
with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
    run=subprocess.run(command,cwd=repo,stdout=stdout,stderr=stderr)
ar.atomic_json(out/'invocation.json',{'at':ar.now(),'command':command,'returncode':run.returncode})
assert run.returncode==0,(out/'stderr.log').read_text(encoding='utf-8',errors='replace')
report=json.loads((ar.RESEARCH/'comparisons/E018-three-pair-comparison/report.json').read_text(encoding='utf-8'))
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    status=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    logical=next(e for e in status['experiments'] if e['id']=='E018')
    measured=next(e for e in status['experiments'] if e['id']=='E018R1')
    for key in ('status','correctness','reason','qualification_summary'):logical[key]=measured[key]
    unit=json.loads((ar.RESEARCH/'runs/V018-unit/report.json').read_text(encoding='utf-8'))
    logical['details']=f"{unit['test_pass_count']} unit tests and the mapped-child continuation capacity test passed; independent primary audit pending. Broader original-kernel controls are required before acceptance."
    for e in measured.get('evidence',[]):
        if not any(x['url']==e['url'] for x in logical['evidence']):logical['evidence'].append(e)
    status.update(updated_at=ar.now(),stage='E018 primary screen '+report['decision'],
      activity='Fixed primary cohort complete. Independent review is checking all results. Retained accepted gain remains E015 9.62%.',active_experiment='E018')
    ar.atomic_json(ar.STATUS,status)
print(json.dumps({'decision':report['decision'],'performance':report['performance']},indent=2))
