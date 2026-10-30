"""Prespecified diagnosis of the original/E015/E016 river discrepancy; no acceptance."""
import json, os, subprocess, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
out=ar.RESEARCH/'runs/D028-three-arm'
out.mkdir(exist_ok=False)
arms={'original':('baseline-complete','f2b93f5088f8395baaac9b47e7cdb89cfc92e7e33d9af50702b0ee8485e6ee6f'),
      'E015':('E015-postflop_autoresearch','37e09be0b3d2ec66db6b49e13e09aa468a487218bd0215306f025bf7ca226eda'),
      'E016':('E016-postflop_autoresearch','bab2bf04b107dba790a875efd611831e73dc47e5f6faa13e6351f88202dc2bcf')}
order=[('original',1),('E015',1),('E016',1),('E015',2),('E016',2),('original',2),('E016',3),('original',3),('E015',3)]
for arm,(name,expected) in arms.items():
    assert ar.sha256(ar.RESEARCH/'binaries'/(name+'.exe'))==expected
protocol={'id':'D028','created_before_runs':ar.now(),
          'purpose':'Locate whether the fresh original-baseline river regression is specific to E016 or shared with retained E015 under the current run history.',
          'scope':'Diagnostic only. Does not replace, exclude or reclassify any prior timing cohort; no candidate acceptance from this script.',
          'trigger':'E016 primary passed +4.1126% versus E015; fresh original-baseline cohort failed river regression guard in all three pairs, primarily in constructor initialization.',
          'arms':arms,'order':[{'arm':a,'repetition':n,'id':f'D028-{a}-{n}'} for a,n in order],
          'fixed_inputs':'Same frozen complete-cycle evaluator, workload, native binaries, full fixture order, compressed storage, 16 CPU threads and unprofiled environment.',
          'interpretation_rules':['Retain all nine runs and all 27 fixture records. Compare full-cycle and component distributions across all arms.',
             'Report original/E015 and original/E016 differences separately from E015/E016; do not infer a unique cause from timing location.',
             'If the regression occurs before graph construction in solve, do not attribute it to graph capture without further evidence.',
             'A favorable diagnostic does not erase the failed cumulative cohort or by itself establish stable cumulative performance.'],
          'source_hash':ar.sha256(repo/'crates/solver/src/gpu/mod.rs')}
ar.atomic_json(out/'protocol.json',protocol)
for arm,number in order:
    name=arms[arm][0];identity=f'D028-{arm}-{number}'
    env=os.environ.copy()
    for key in ('POSTFLOP_AUTORESEARCH_PROFILE','POSTFLOP_AUTORESEARCH_FIXTURE','POSTFLOP_AUTORESEARCH_STORAGE'):env.pop(key,None)
    subprocess.run([sys.executable,'tools/postflop_autoresearch.py','--id',identity,'--title',f'D028 three-arm river diagnosis: {arm}',
      '--kind','diagnostic','--binary',str(ar.RESEARCH/'binaries'/(name+'.exe')),
      '--build-manifest',str(ar.RESEARCH/'binaries'/(name+'.manifest.json')),'--test','postflop_complete_cycle'],cwd=repo,env=env,check=True)
ar.atomic_json(out/'completed.json',{'finished_at':ar.now(),'completed_runs':9,'scope':'All runs retained for diagnostic review; acceptance remains on hold'})
print('D028 all nine diagnostic runs completed.',flush=True)
