import sys,json,shutil,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import common as h
h.custody();assert not(h.ROOT/'gpu-run.lock').exists()
assert shutil.disk_usage(h.ROOT).free>=66*1024**3
A=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
REF=h.ROOT/'reference';REF.mkdir(exist_ok=False);copies=[]
for rel in ['runs/E090-source','runs/D141-cfv-width']:
 source=A/rel;dest=REF/source.name;dest.mkdir()
 for p in sorted(source.rglob('*')):
  if not p.is_file():continue
  q=dest/p.relative_to(source);assert q.resolve().is_relative_to(h.ROOT.resolve());q.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(p,q);digest=h.sha(p);h.pin(q,digest)
  copies.append({'original':str(p),'local':str(q),'sha256':digest,'bytes':q.stat().st_size})
depdir=REF/'accepted-e080-deps';depdir.mkdir()
manifest=h.read(h.ROOT/'binaries/E080-postflop_autoresearch.manifest.json')
for path,digest in manifest['dependency_artifact_sha256'].items():
 p=Path(path);h.pin(p,digest);q=depdir/p.name
 if q.exists():h.pin(q,digest);continue
 shutil.copyfile(p,q);h.pin(q,digest);copies.append({'original':str(p),'local':str(q),'sha256':digest,'bytes':q.stat().st_size})
original=h.read(REF/'E090-source/manifest.json');owned={}
for rel,paths in original['owned'].items():
 b=REF/'E090-source'/Path(paths['base']).name;c=REF/'E090-source'/Path(paths['candidate']).name
 h.pin(b,h.custody()[rel]);h.pin(c,original['candidate_owned_sha256'][rel])
 owned[rel]={'base':str(b),'candidate':str(c)}
report={'at':h.now(),'status':'pass_exact_reference_localization','physical_output_drive':'X:','source_archive_read_only':str(A),'copied_bytes':sum(x['bytes']for x in copies),'copies':copies,'owned_candidate_sources':owned,'candidate_owned_sha256':original['candidate_owned_sha256'],'source_activated':False,'GPU_executions':0,'new_performance_samples':0,'scope':'Checksum-verified copies of the existing two-statement E090 source, D141 CPU graph/address proof and accepted E080 library dependencies. Original frozen manifests and their historical path text remain byte-exact; this mapping explicitly binds their new physical X locations. Old archive is preserved. No benchmark input or candidate source values changed.'}
h.save(REF/'localization.json',report)
key='RAM20261028-baseline/next-trial-localization.json';dst=h.ar.DASHBOARD/'evidence'/key;assert not dst.exists();shutil.copyfile(REF/'localization.json',dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==(REF/'localization.json').read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E090')
 x.update(stage='GPU controls localized on X',reason='The two-statement per-traverser CFV stride candidate and its 12-layout integer proof are copied and checksum verified on X. The fresh E080 hardware baseline is complete. Real GPU correctness and speed remain unproven.',measurement_epoch_id='RAM20261028')
 x['evidence'].append({'label':'Verified X reference mapping','url':'evidence/'+key})
 s.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E090',stage='Preparing E090 GPU controls on X',activity='Fresh current-RAM E080 baseline is 10.4564 s, with all 86 tests and five scored exact-state measurements passing. Next test the unchanged per-traverser CFV stride candidate using verified references on X. Prior timing gains remain historical.')
 h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(json.dumps({'status':report['status'],'copied_bytes':report['copied_bytes'],'files':len(copies),'new_GPU_runs':0}),flush=True)
