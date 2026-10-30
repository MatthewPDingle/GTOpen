"""Complete exact continuation accounting before the first integrated build."""
from pathlib import Path
import difflib,json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists()
S=R/'runs/E073-source';T=R/'runs/E073-source-host-r2';assert not T.exists();T.mkdir();m=old.read(S/'manifest.json')
done=old.read(R/'runs/E073-kernel-control-r3/complete.json');assert done['status']=='pass_scoped_full_show_raw_equivalence'and done['cases']==364
for p in S.iterdir():
 if p.is_file()and p.suffix in ['.cu','.rs']:shutil.copyfile(p,T/p.name)
p=T/'candidate-continuation_capacity.rs';b=p.read_bytes();t=b.decode();before='+bytes(&p.riv_cnt[q])+bytes(&p.riv_sorted_idx[q])+bytes(&p.riv_lower[q])+bytes(&p.riv_upper[q])';after='+bytes(&p.riv_cnt[q])+bytes(&p.riv_sorted_idx[q])\n            +(p.riv_lower[q].len() as u64+p.riv_upper[q].len() as u64)*2';assert t.count(before)==1;t=t.replace(before,after,1);p.write_text(t,encoding='utf-8',newline='');assert t.replace(after,before,1)==b.decode()
owned=m['candidate_owned_sha256'];m.update(at=old.now(),source_stage='Host accounting complete before first integrated build; CUDA/upload code byte-identical to exact direct controls',candidate_owned_sha256={n:old.sha(T/('candidate-'+Path(n).name))for n in owned},candidate_files={n:str(T/('candidate-'+Path(n).name))for n in owned},prior_source_manifest_sha256=old.sha(S/'manifest.json'));old.save(T/'manifest.json',m)
assert old.sha(T/'candidate.cu')==old.sha(S/'candidate.cu')and old.sha(T/'candidate-mod.rs')==old.sha(S/'candidate-mod.rs')
patch=''.join(''.join(difflib.unified_diff((T/('baseline-'+Path(n).name)).read_text(encoding='utf-8').splitlines(True),(T/('candidate-'+Path(n).name)).read_text(encoding='utf-8').splitlines(True),fromfile='E051/'+n,tofile='E073/'+n))for n in owned);(T/'candidate.patch').write_text(patch,encoding='utf-8',newline='')
old.save(T/'source-review.json',{'id':'E073-host-accounting','at':old.now(),'status':'pass_prebuild_accounting_completion','prior_manifest_sha256':old.sha(S/'manifest.json'),'final_manifest_sha256':old.sha(T/'manifest.json'),'reason':'continuation_storage.rs:223requires planned base GPUmetadata equal observed actual payload, not a conservative CPU-vector estimate. Initial staged candidate narrowed observed bytes only. Complete the planner bytes to2for these private buffers before first integrated build. Public GpuPlan vectors and ordinary conservative game budget remain unchanged.','candidate_CUDA_unchanged':True,'candidate_upload_unchanged':True,'direct_control_report_sha256':old.sha(R/'runs/E073-kernel-control-r3/report.json'),'only_delta_from_prior_stage':'metadata()accounts riv_lower/riv_upper lengths at2bytes each, matching already-updated observed_metadata(). No CUDA, upload, data, graph, numeric, quality or primary GPUfeature executable code changed.','original_incomplete_stage_preserved':True,'no_numeric_or_performance_failure_to_rescue':True,'compilers_or_solver_executions_before_completion':0,'full_feature_capacity_control_still_required':True,'candidate_accepted':False})
pub=[]
for p in T.iterdir():
 if p.is_file():
  key=T.name+'/'+p.name;dest=old.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(p,dest)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
  pub.append({'url':'evidence/'+key,'sha256':old.sha(p)})
old.save(T/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub})
old.custody();print(json.dumps({'status':'host_accounting_completed_prebuild','CUDA_and_upload_code_unchanged':True,'candidate_owned_sha256':m['candidate_owned_sha256']}),flush=True)
