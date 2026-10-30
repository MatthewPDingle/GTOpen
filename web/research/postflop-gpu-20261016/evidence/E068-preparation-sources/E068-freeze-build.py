"""Freeze fresh integrated builds after complete E068 raw equivalence."""
import ast,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();old.ar.refuse_active(old.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
S=ROOT/'runs/E068-source';RES=ROOT/'runs/E068-resource';K=ROOT/'runs/E068-kernel-control';R=ROOT/'comparisons/E068-kernel-control-root-check';C=old.read(R/'report.json');P=old.read(K/'protocol.json')
assert C['status']=='pass_scoped_up_chance_full_raw_equivalence' and C['cases']==1688 and C['kernel_launches']==3376 and C['all_full_outputs_inputs_guards_exact'] and C['checks']==3771697
for p,h in P['input_sha256'].items():old.pin(p,h)
for p,h in C['raw_file_sha256'].items():old.pin(p,h)
for label in ['rustc','probe']:
 x=old.read(K/'execution'/(label+'.exit.json'));assert x['returncode']==0 and x['error'] is x['cleanup'] is None
H=ROOT/'runs/E068-build-plan';assert not H.exists();H.mkdir();prior=ROOT/'runs/E067-build-plan'
code=(prior/'build.py').read_text().replace('E067','E068');ast.parse(code);(H/'build.py').write_text(code,encoding='utf-8',newline='\n')
B=old.read(prior/'build-protocol.json');B.update(id='E068-final-build',at=old.now(),status='FROZEN_PRE_INTEGRATED_BUILD',accepted_source_sha256=old.BASE,original_source_form='E059',owned={'crates/solver/src/gpu/kernels.cu':{'base':str(S/'baseline.cu'),'base_sha256':old.sha(S/'baseline.cu'),'candidate':str(S/'candidate.cu'),'candidate_sha256':old.sha(S/'candidate.cu')}})
B['phases']=[{**x,'target':x['target'].replace('e067','e068'),'outputs':{k:v.replace('E067','E068') for k,v in x['outputs'].items()}} for x in B['phases']]
for phase in B['phases']:assert not Path(phase['target']).exists()
paths=[H/'build.py',*S.iterdir(),RES/'protocol.json',RES/'report.json',RES/'blocker-branch-proof.json',K/'protocol.json',K/'execution/complete.json',K/'execution/terminal.json',R/'report.json',ROOT/'comparisons/E068-resource-root-check/report.json',ROOT/'runs/E068-raw-root-check.py',Path(B['protected_main']),ROOT/'runs/accepted-E051/common_e051.py',ROOT/'runs/D108-resource-feasibility-audit/report.json',ROOT/'runs/D108-resource-feasibility-audit/docket.json',ROOT/'runs/D108-resource-feasibility-audit/commit.json',ROOT/'runs/D097-chance-selection/protocol.json',ROOT/'runs/D097-chance-selection/report.json',old.REPO/'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',old.REPO/'tools/postflop_resource_feasibility.py',old.REPO/'tools/postflop_autoresearch.py',Path(__file__)]
B['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()};old.save(H/'build-protocol.json',B)
published={}
for folder in [H,R,K,RES,ROOT/'comparisons/E068-resource-root-check']:
 for p in folder.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.exe','.pdb','.bin']:continue
  key='evidence/'+folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  published[key]=old.sha(p)
old.save(H/'pre-build-publication.json',{'at':old.now(),'artifact_sha256':published,'http_bytes_verified':True,'integrated_solver_executions':0,'raw_binaries_kept_on_S_registered_full_sha256':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E068');e.update(stage='Full raw equivalence passed; fresh integrated builds',reason='1688pairs/3376launches;35,904,112fulloutputs/9,083,648actualinputs/34,875,264guards exact.3,771,697rootchecks,10,938,464extra/usedaddressesvalid;137,904canonical-cardrelations/126,840signedzero relations pass. No complete-solve speed observed yet.');e['evidence'].extend([{'label':'Full raw root replay and address/CPU relations','url':'evidence/'+R.name+'/report.json'},{'label':'Fresh integrated build protocol','url':'evidence/'+H.name+'/build-protocol.json'}]);st.update(updated_at=old.now(),stage='E068 fresh integrated solver builds',activity='Exact original blocked-accumulator form passes directGPU and separate raw replay. SameacceptedE051source restored betweenbuildphases; no adoption or speedclaim.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'build_protocol_sha256':old.sha(H/'build-protocol.json'),'root_checks':C['checks'],'published':len(published),'native_solver_executions':0}),flush=True)