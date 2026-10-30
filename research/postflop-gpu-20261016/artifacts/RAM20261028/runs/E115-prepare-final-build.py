"""Fresh ordinary source builds, gated on the unchanged full raw-state corpus."""
import ast,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
S=ROOT/'runs/E115-source-v2';M=h.read(S/'manifest.json');raw=ROOT/'comparisons/D272-metadata-canonical-v2/report.json';q=h.read(raw)
assert q['scientific_full_records_exact']==6 and q['canonical_checkpoints_exact']==46 and q['GPU_all69field_pairs']==12
assert q['all43_unmapped_device_buffers_including_entire_physical_CFV_literal_exact']and q['all66_device_buffers_exact_under_only_declared_metadata_identity']
assert h.read(ROOT/'runs/D272-metadata-canonical-v2/execution/complete.json')['all_owned_children_terminal']
engine=ROOT/'comparisons/D271-metadata-engine/report.json';e=h.read(engine);assert e['cases']==36 and e['phase_pairs']==752 and e['extra_lock_controls']['cases']==6
H=ROOT/'runs/E115-build-plan';H.mkdir(exist_ok=False)
parent=ROOT/'runs/E114-build.py';code=parent.read_text(encoding='utf-8').replace('E114','E115').replace('e114','e115')
needle=" and b'float acc0 = 0.f, acc1 = 0.f;' in data";assert code.count(needle)==1;code=code.replace(needle,'',1)
code=code.replace('fixed paired chance CUDA body','frozen metadata row projection and original CUDA')
ast.parse(code);script=ROOT/'runs/E115-build.py';assert not script.exists();script.write_bytes(code.encode())
phases=[{'id':'feature','features':'preflop-research','expected_features':['gpu','preflop-research'],'integration':False,'outputs':{'solver':'E115-feature-solver'},'target':str(ROOT/'build-e115-final-feature')},{'id':'primary','features':'gpu','expected_features':['gpu'],'integration':True,'outputs':{'solver':'E115-solver','postflop_autoresearch':'E115-postflop_autoresearch'},'target':str(ROOT/'build-e115-final-primary')}]
for p in phases:assert not Path(p['target']).exists()
for n,v in M['owned'].items():
    h.pin(v['candidate'],v['candidate_sha256'])
    if v['base']:h.pin(h.REPO/n,v['base_sha256'])
    else:assert not(h.REPO/n).exists()
files=[Path(__file__),parent,script,S/'manifest.json',S/'source-review.json',raw,ROOT/'runs/D272-metadata-canonical-v2/protocol.json',ROOT/'runs/D272-metadata-canonical-v2/source-review.json',ROOT/'runs/D272-metadata-canonical-v2/execution/complete.json',engine,ROOT/'runs/D271-metadata-engine/protocol.json',ROOT/'runs/D271-metadata-engine/source-review.json',ROOT/'runs/D270-actual-metadata-CPU/root-report-r2.json',ROOT/'runs/D269-host-layout/report.json',ROOT/'epoch/common.py',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json']+[Path(v[k])for v in M['owned'].values()for k in['base','candidate']if v[k]]
h.save(H/'protocol.json',{'id':'E115-final-build','at':h.now(),'status':'FROZEN_PRE_ORDINARY_INTEGRATED_CARGO_COMPILERS','owned':M['owned'],'accepted_source_sha256':M['accepted_source_sha256'],'candidate_owned_sha256':{n:v['candidate_sha256']for n,v in M['owned'].items()},'tracked_owned_paths':[n for n,v in M['owned'].items()if v['base']],'new_owned_paths':[n for n,v in M['owned'].items()if not v['base']],'phases':phases,'required_free_bytes':80*1024**3,'input_sha256':{str(p):h.sha(p)for p in files},'scope':'Two fresh offline/locked feature/primary Cargo builds of unchanged frozen E1155file host metadata form and identical original9entryCUDA. Actual runtimeNVRTC12.9/JIT, no sealed PTX or observers or diagnostic map/enum. Original4tracked research files/new metadata module restored after each compiler, all byte hashes/dependencies/executables recorded. Full CPU/engine/canonical state prerequisites pass under only declared23metadata identity inverse; all physical CFV/other43 buffers/CPU values literal exact. No source/field/helper/predicate/scope/flags/quality/sample rescue after genuine failure. No speed/adoption/no-tradeoff claim; original complete1%/strictfixture/fresh16/broad/material/holdout/cumulative/app gates remain.'})
p=H/'protocol.json';dst=h.ar.DASHBOARD/'evidence'/H.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+p.name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=h.read(h.ar.STATUS);item=next(x for x in s['experiments']if x['id']=='E115');item.update(stage='Fresh ordinary feature/primary source builds',correctness='CPU/42GPUcases/fullcanonical exact under declared metadata identity',reason='Full same-quality raw lifecycle passes. Fresh ordinary5file source builds include actual NVRTC/JIT, no observer/PTX shortcuts. Restore accepted research source after each compiler; all complete-solve/material gates remain.');item['evidence'].append({'label':'Frozen ordinary source build plan','url':'evidence/'+H.name+'/protocol.json'});s.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E115',stage=item['stage'],activity=item['reason']);h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(h.sha(H/'protocol.json'),flush=True)
