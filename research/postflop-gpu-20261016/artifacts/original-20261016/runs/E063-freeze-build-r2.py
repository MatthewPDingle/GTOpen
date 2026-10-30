"""Freeze fresh build destinations after successful immutable raw root replay."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/E063-build-plan';R=ROOT/'comparisons/E063-kernel-control-root-check';K=ROOT/'runs/E063-kernel-control';RES=ROOT/'runs/E063-resource';S=ROOT/'runs/E063-source'
assert H.exists() and (H/'build.py').exists() and not (H/'build-protocol.json').exists() and not (ROOT/'runs/E063-final-build').exists()
q=old.read(R/'report.json');assert q['status']=='pass_scoped_show_raw_equivalence' and q['cases']==364 and q['resource_and_raw_ptx_byte_identical'] and q['packed_boundary_representation_independently_validated']
old.pin(K/'execution/raw-results.jsonl',q['raw_sha256']);assert old.read(K/'execution/probe.exit.json')['returncode']==0 and old.read(K/'execution/terminal.json')['returncode']==0
old.save(H/'preparation-failure.json',{'at':old.now(),'script_sha256':old.sha(ROOT/'runs/E063-freeze-build.py'),'error':'Prebuild target-absence check caught inherited lowercase e062 destination after otherwise successful raw root replay. No build or solver executed, no protocol frozen. Preserve root proof and source bytes; choose literal fresh E063destinations before compilation.','compilers_started':0,'solver_executions':0,'raw_root_report_sha256':old.sha(R/'report.json')})
B=old.read(ROOT/'runs/E062-build-plan/build-protocol.json')
B.update(id='E063-final-build',at=old.now(),status='FROZEN_PRE_INTEGRATED_BUILD',accepted_source_sha256=old.BASE,source_form='one_fixed_new_per_card_cutoff_precomputation',protected_main=str(ROOT/'runs/accepted-E051/protected-main.json'),owned={n:{'base':str(S/b),'base_sha256':old.sha(S/b),'candidate':str(S/c),'candidate_sha256':old.sha(S/c)} for n,b,c in [('crates/solver/src/gpu/kernels.cu','baseline.cu','candidate.cu'),('crates/solver/src/gpu/mod.rs','baseline-mod.rs','candidate-mod.rs')]})
B.pop('original_source_form',None)
for phase in B['phases']:
 assert 'build-e062-' in phase['target'];phase['target']=phase['target'].replace('build-e062-','build-e063-')
 phase['outputs']={k:v.replace('E062','E063') for k,v in phase['outputs'].items()}
 assert 'e062' not in phase['target'] and not Path(phase['target']).exists()
 for stem in phase['outputs'].values():assert stem.startswith('E063-') and not (ROOT/'binaries'/(stem+'.exe')).exists() and not (ROOT/'binaries'/(stem+'.manifest.json')).exists()
paths=[H/'build.py',H/'preparation-failure.json',*S.iterdir(),RES/'protocol.json',RES/'report.json',RES/'compiled-mechanism.json',K/'execution-plan.json',K/'report.json',K/'execution/complete.json',K/'execution/terminal.json',R/'report.json',Path(B['protected_main']),ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/D102-card-cutoffs-r3/report.json',ROOT/'runs/D102-card-cutoffs-r3/helper.rs',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',old.REPO/'tools/postflop_autoresearch.py',Path(__file__),ROOT/'runs/E063-freeze-build.py']
B['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()};old.save(H/'build-protocol.json',B)
published={}
for folder in [H,R,K,RES]:
 for p in folder.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.exe','.pdb','.bin']:continue
  key='evidence/'+folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  published[key]=old.sha(p)
old.save(H/'pre-build-publication.json',{'at':old.now(),'artifact_sha256':published,'http_bytes_verified':True,'solver_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E063');e.update(stage='Exact raw matrix passed; integrated builds',reason='364pairs/728launches:1,687,304output words,3,065,944actual inputs,1,292,824guards exact. Candidate boundary words independently checked by linear classification and root bisect reconstruction. Other19buffers exact across arms. Fresh two-source feature/primary builds next.');e['evidence'].extend([{'label':'Full raw root replay','url':'evidence/'+R.name+'/report.json'},{'label':'Fresh two-source build protocol','url':'evidence/'+H.name+'/build-protocol.json'}]);st.update(updated_at=old.now(),stage='E063 integrated feature and primary builds',activity='Complete direct numerical controls passed. Freeze fresh build destinations; accepted E051restored between phases. No speed claim.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'status':'build_plan_frozen','build_protocol_sha256':old.sha(H/'build-protocol.json'),'root_checks':q['checks'],'targets':[p['target'] for p in B['phases']],'published':len(published)}),flush=True)
