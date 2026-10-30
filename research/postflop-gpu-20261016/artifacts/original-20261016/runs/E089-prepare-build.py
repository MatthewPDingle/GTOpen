import sys,ast,shutil,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=50*1024**3
S=R/'runs/E089-source';D=R/'runs/E089-kernel-control';Q=R/'comparisons/E089-kernel-control-root-check';RES=R/'runs/E089-resource'
q=old.read(Q/'report.json')
assert q['status']=='pass_scoped_full_serial_card_loop_raw_equivalence'and q['inventory']['comparison_pairs']==1820 and q['whole_physical_outputs_bitwise_equal']and q['all21_input_buffers_identical']
for p in [D/'execution/rustc.exit.json',D/'execution/probe.exit.json',R/'runs/E089-direct-audit/audit.exit.json']:
 x=old.read(p);assert x['returncode']==0 and x['error']is x['cleanup']is None
H=R/'runs/E089-build-plan';H.mkdir(exist_ok=False)
code=(R/'runs/E086-build-plan/build.py').read_text(encoding='utf-8').replace('E086','E089');ast.parse(code);(H/'build.py').write_bytes(code.encode())
P=old.read(R/'runs/E086-build-plan/build-protocol.json');source=old.read(S/'manifest.json')
owned={}
for n,v in source['owned'].items():
 old.pin(v['base'],old.BASE[n]);old.pin(v['candidate'],source['candidate_owned_sha256'][n])
 owned[n]={'base':v['base'],'base_sha256':old.BASE[n],'candidate':v['candidate'],'candidate_sha256':source['candidate_owned_sha256'][n]}
P.update(id='E089-final-build',at=old.now(),owned=owned,accepted_source_sha256=old.BASE,CUDA_source_unchanged=False,direct_pairs=1820,direct_launches=3640,expected_ordinary_units=86,source_scope=source['scope']+' Compiledbody smaller120/75; raw1820pairs/3640launches/full21actualinputs pass; no speed/materialqualification yet.')
for phase in P['phases']:
 phase['target']=str(R/('build-e089-final-'+phase['id']));phase['outputs']={k:v.replace('E086','E089')for k,v in phase['outputs'].items()};assert not Path(phase['target']).exists()
files=[Path(__file__),H/'build.py',Q/'report.json',D/'protocol.json',D/'execution/complete.json',RES/'protocol.json',RES/'report.json',C/'common_e080_live.py',C/'protected-main.json',C/'preexisting-target-artifacts.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
files += [p for folder in [S,D,RES]for p in folder.rglob('*')if p.is_file()and p.suffix in ['.json','.rs','.py','.cu','.patch','.log']]
P['input_sha256']={str(p):old.sha(p)for p in files};old.save(H/'build-protocol.json',P)
pub=[]
for folder in [D,Q,H,RES,R/'runs/E089-direct-audit']:
 for p in folder.rglob('*'):
  if not p.is_file()or p.suffix not in ['.json','.py','.rs','.cu','.patch','.log']:continue
  key=folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
old.save(H/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'raw_bulk_on_S_only':True,'protocol_sha256':old.sha(H/'build-protocol.json')})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E089');x.update(stage='Fresh integrated solver builds',correctness='raw_controls_pass',reason='All1820direct rawpairs/fullinputs/guards and105571readerchecks pass. Buildfeature/primary for86ordinaryunits andfixedcomplete-solvecomparison. Speedunproven.')
 x['evidence'] += [{'label':'Full raw GPU replay','url':'evidence/E089-kernel-control-root-check/report.json'},{'label':'Frozen integrated builds','url':'evidence/E089-build-plan/build-protocol.json'}]
 s.update(updated_at=old.now(),stage='E089 full builds before complete-solve timing',activity='DirectGPUoutputs/inputs/guards exact acrossfivewidths. Twofreshbuilds next;acceptedE080live,nonewspeedresult.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(old.sha(H/'build-protocol.json'),flush=True)
