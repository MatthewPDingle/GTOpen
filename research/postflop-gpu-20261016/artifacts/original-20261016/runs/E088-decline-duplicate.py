import sys,shutil,subprocess,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists()
S=R/'runs/E088-source';H=R/'runs/E088-resource';D=R/'runs/D139-generic-cache';O=R/'runs/E088-duplicate-closure';O.mkdir(exist_ok=False)
assert not(H/'probe.exe').exists()and not(H/'execution').exists()
prior=R/'runs/E024-design/candidate/kernels.cu';assert 'bool small = NA != 0 && na <= 8;'in prior.read_text(encoding='utf-8')
checks=0
for na in range(1,256):
 for n in [0,2,3,4]:
  # Specialized instances admit only the matching constant action count.
  if n and n!=na:continue
  assert bool(n!=0)==bool(n!=0 and na<=8);checks+=1
reason='Declined before compiler/native: exact generic-cache-removal mechanism already tested asD046/E024 and rejected for complete-solve slowdown. NA!=0 is equivalent to the archived NA!=0&&na<=8 on all0/2/3/4instantiations. Frozen candidate/protocol retained, never activated or executed; no retest/rescue.'
old.save(O/'report.json',{'id':'E088','at':old.now(),'status':'declined_duplicate_before_execution','reason':reason,'source_review_correction':'Initial staged source-review omitted D046/E024 attribution; the generated history did contain both hits. Root inspection stopped execution. New/independent characterization is withdrawn.','predicate_domain_checks':checks,'historical_candidate_sha256':old.sha(prior),'E024_outcome':'-0.5027%complete-solve gain,rejected','candidate_manifest_sha256':old.sha(S/'manifest.json'),'frozen_unexecuted_protocol_sha256':old.sha(H/'protocol.json'),'compiler_invocations':0,'application_kernel_launches':0,'solve_samples':0,'accepted':'E080','source_main_live_PTX_custody_pass':True,'second_declined_lead':'Fold shuffle tail already tested/rejectedE019. No second candidate or compiler prepared.'})
pub=[]
for folder in [D,S,H,O]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key=folder.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E088')
 x.update(status='rejected',correctness='not_run',stage='Closed duplicate before compiler',reason=reason)
 x['evidence'].append({'label':'Duplicate guard and attribution correction','url':'evidence/E088-duplicate-closure/report.json'})
 x=next(x for x in s['experiments']if x['id']=='D139');x.update(reason='Audit identifies D046/E024 equivalent candidate and E019 fold shuffle; both declined before execution. Earlier new-form description corrected by closure.')
 s.update(updated_at=old.now(),active_experiment=None,stage='New mechanism source audit',activity='Generic-cache and fold-shuffle leads match closed experiments. No GPU re-runs. Investigating a distinct showdown serial-loop code-size hypothesis; E080 remains live.')
 old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';t=ledger.read_bytes();assert b'### D139 and E088 duplicate guard'not in t
entry='\n\n### D139 and E088 duplicate guard\n\nPrevious goal turn completed E087 raw GPU controls/full builds/fixed primary; rejected1.4873145842%aggregate gain for rainbow/river guards. Current source/history scout stagesE088 generic-cache predicate and freezes resource controls but inspects generated history before executing. History containsD046/E024 equivalent NA!=0&&na<=8 form. New NA!=0 equals it across actual0/2/3/4template instances;'+str(checks)+'CPU predicate-domain checks. Initial new-form characterization is explicitly corrected; priorE024complete-solve slowdown remains closed. E088declined before any compiler/applicationkernel/solve/sourceactivation. Frozen candidate/source/protocol and correction retained. Foldshuffle lead also matches rejectedE019; no secondcandidate. Source/main/live/protectedPTXcustody passes, no ownedchildren or lock. E08014.7414188354%measured cumulative gain,lastprimaryB289 unchanged;goalactive.\n'
nl=b'\r\n'if b'\r\n'in t else b'\n';ledger.write_bytes(t+entry.encode().replace(b'\n',nl))
subprocess.run(['git','commit','--only','-m','research: preserve duplicate guard and cache attribution','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
old.custody();print(reason,flush=True)
