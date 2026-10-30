"""Freeze three-file E048 host integration after complete raw GPU control."""
import difflib,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
C=ROOT/'comparisons/E048-kernel-control/report.json';control=old.read(C)
assert control['status']=='pass_scoped_chance_raw_equivalence' and control['cases']==425 and control['kernel_launches']==850 and control['full_raw_files_equal']
D=ROOT/'runs/E048-final-source';D.mkdir();owned={}
def keep(rel,base,candidate):
 name=Path(rel).name;b=D/('base-'+name);c=D/('candidate-'+name);b.write_bytes(base);c.write_bytes(candidate)
 (D/(name+'.patch')).write_text(''.join(difflib.unified_diff(base.decode('utf-8').splitlines(keepends=True),candidate.decode('utf-8').splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel)),encoding='utf-8')
 owned[rel]={'base':str(b),'base_sha256':old.sha(b),'candidate':str(c),'candidate_sha256':old.sha(c)}
keep('crates/solver/src/gpu/kernels.cu',(ROOT/'runs/E048-design/baseline.cu').read_bytes(),(ROOT/'runs/E048-design/candidate.cu').read_bytes())
rel='crates/solver/src/gpu/mod.rs';base=(ar.REPO/rel).read_bytes();s=base.decode('utf-8');nl='\r\n' if '\r\n' in s else '\n'
field='    d_hand_mask: [CudaSlice<u64>; 2],'+nl;ctor='            d_hand_mask: [up64(&plan.hand_mask[0])?, up64(&plan.hand_mask[1])?],'+nl
assert s.count(field)==s.count(ctor)==1;s=s.replace(field,'').replace(ctor,'')
old_down='                        .arg(&self.d_hand_mask[0])'+nl+'                        .arg(&self.d_hand_mask[1])'
new_down=nl.join('                        .arg(&self.d_hand_'+card+'['+str(p)+'])' for p in [0,1] for card in ['c1','c2'])
assert s.count(old_down)==2;s=s.replace(old_down,new_down)
old_up='                        .arg(&self.d_hand_mask[p])';new_up='                        .arg(&self.d_hand_c1[p])'+nl+'                        .arg(&self.d_hand_c2[p])';assert s.count(old_up)==2;s=s.replace(old_up,new_up)
old_test='                        .arg(&gpu.d_hand_mask[0]).arg(&gpu.d_hand_mask[1])';new_test='                        .arg(&gpu.d_hand_c1[0]).arg(&gpu.d_hand_c2[0])'+nl+'                        .arg(&gpu.d_hand_c1[1]).arg(&gpu.d_hand_c2[1])';assert s.count(old_test)==1;s=s.replace(old_test,new_test)
assert 'd_hand_mask' not in s and 'plan.hand_mask' not in s
keep(rel,base,s.encode('utf-8'))
rel='crates/solver/src/gpu/continuation_capacity.rs';base=(ar.REPO/rel).read_bytes();s=base.decode('utf-8');assert s.count('bytes(&p.hand_mask[q])+')==s.count('d_hand_mask:u64,')==1;s=s.replace('bytes(&p.hand_mask[q])+','').replace('d_hand_mask:u64,','');keep(rel,base,s.encode('utf-8'))
for n,v in owned.items():assert old.sha(ar.REPO/n)==v['base_sha256']==old.BASE[n]
old.save(D/'manifest.json',{'id':'E048-final-source','at':old.now(),'accepted_source_sha256':old.BASE,'owned':owned,'raw_control_report_sha256':old.sha(C),'resource_report_sha256':old.sha(ROOT/'runs/E048-resource/report.json'),'domain_review_sha256':old.sha(ROOT/'runs/D078-card-membership-source/caller-and-domain-review.json'),'source_activated':False,'candidate_accepted':False})
old.save(D/'source-review.json',{'id':'E048-final-source-review','at':old.now(),'status':'pass_to_fresh_feature_primary_builds_and_fixed_screen','root_review_only':True,'scope':'kernels.cu changes only two membership predicates/interfaces. mod.rs updates all4 production caller sites and1 ordinary full-down reference, removes2 private mask buffers/uploads. continuation_capacity.rs removes the same payload from expected/observed GPU metadata; public CPU GpuPlan and component-vector schema unchanged.','caller_arg_order':{'down':'parents,childs,cards,start,count,rsrc0,rsrc1,c1_0,c2_0,c1_1,c2_1,reach0,reach1,nh0,nh1','up':'nodes,start,count,cc_start,cc_count,cc_card,cc_child,cc_perm,node_cdiv,c1_p,c2_p,hand_perm,cfv_slot,cfv,nh,nh_max'},'supported_domain':'Canonical two-card hands produced by Spot construction/load. Manually inconsistent public Rust HandInfo structs outside domain; supported callers verified.','numeric_control':{'cases':425,'kernel_launches':850,'raw_output_words_both_arms':18950844,'actual_immutable_words_both_arms':3951272,'guard_words_both_arms':13112256,'root_checks':2508695,'all_exact':True,'raw_files':3,'report_sha256':old.sha(C)},'resource_prerequisite':'Down registers30->28, up30unchanged; no shared/local allocation, same queried occupancy and correct changed ABI, other7 entries exact. This is not full module/resource or speed qualification.','expected_payload_change':'Device hand masks removed: minus8*(nh0+nh1)bytes and2allocations; existing card arrays retained, no new buffer, packing, stream, event, graph, launch or CPU plan field. Context/driver allocator/module costs remain empirical.','exactness':'All floating expressions/order, reduction order, discounts/storage/quality/check cadence and full readback unchanged. Existing ordinary test criteria unchanged; only its pointer arguments updated to the new private ABI.','ordinary_expected_passed':84,'ordinary_expected_ignored':4,'conditional_adoption_requirements':['Fresh16pair confirmation after qualifying fixed3pair screen','Broader originalGPU/F32/state/menu/resume/continuation plus actual capacity accounting','Fixed holdout and fresh-original cumulative comparison','No material resource/capacity/compatibility/behavior cost; validate actual removed-buffer accounting and lifetime/module effects'],'candidate_accepted':False})
HERE=ROOT/'runs/E048-build-plan';HERE.mkdir();prior=ROOT/'runs/E047-build-plan'
(HERE/'build.py').write_text((prior/'build.py').read_text(encoding='utf-8').replace('E047','E048'),encoding='utf-8')
p=old.read(prior/'build-protocol.json');p.update(id='E048-final-build',at=old.now(),owned=owned)
for phase in p['phases']:phase['target']=phase['target'].replace('e047','e048');phase['outputs']={k:v.replace('E047','E048') for k,v in phase['outputs'].items()}
refs=[HERE/'build.py',D/'manifest.json',D/'source-review.json',C,ROOT/'runs/E048-kernel-control/protocol.json',ROOT/'runs/E048-kernel-control/execution/complete.json',ROOT/'runs/E048-kernel-control/audit.py',ROOT/'runs/E048-resource/report.json',ROOT/'comparisons/E048-resource-root-check/report.json',Path(p['protected_main']),ROOT/'runs/small-gain-confirmation-plan/common.py',ar.REPO/'tools/postflop_autoresearch.py']
for v in owned.values():refs.extend([Path(v['base']),Path(v['candidate'])])
p['input_sha256']={str(x):old.sha(x) for x in refs};old.save(HERE/'build-protocol.json',p)
published={}
for directory in [D,HERE,ROOT/'runs/E048-kernel-control',C.parent]:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);raw=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==raw
  else:dst.write_bytes(raw)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==raw
  published[key]=old.sha(src)
old.save(HERE/'pre-compile-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'solver_executions':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(ar.STATUS);e=next(x for x in s['experiments'] if x['id']=='E048');e.update(correctness='pass',stage='Raw425-case control passed; fresh integrated builds next',reason='425cases/850launches exact; full18950844output words and all inputs/guards retained and decoded. Host bindings/capacity updated off-tree;2mask buffers removed. No full-solver speed result.');e['evidence'].extend([{'label':'E048 full raw GPU control','url':'evidence/E048-kernel-control/report.json'},{'label':'E048 integrated source review','url':'evidence/E048-final-source/source-review.json'}]);s.update(state='running',stage='E048 fresh integrated builds',activity='Build feature and primary binaries from frozen three-file candidate, restoring E020 after each.',updated_at=ar.now());ar.atomic_json(ar.STATUS,s)
print(json.dumps({'source_manifest_sha256':old.sha(D/'manifest.json'),'build_protocol_sha256':old.sha(HERE/'build-protocol.json'),'candidate_source_sha256':{n:v['candidate_sha256'] for n,v in owned.items()},'published_files':len(published)}),flush=True)
