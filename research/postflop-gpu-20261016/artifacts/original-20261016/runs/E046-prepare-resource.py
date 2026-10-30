"""One off-tree packed chance-record CUDA candidate and no-launch resource gate."""
import difflib,json,re,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
SOURCE=ROOT/'runs/E046-design';SOURCE.mkdir();rel='crates/solver/src/gpu/kernels.cu'
raw=(ar.REPO/rel).read_bytes();base=raw.decode('utf-8');nl='\r\n' if '\r\n' in base else '\n'
start=base.index('extern "C" __global__ void up_chance(');end=base.index('// Up sweep, action nodes:',start)
before=base[start:end];after=before
header='    const u32* __restrict__ cc_card, const u32* __restrict__ cc_child,'+nl+'    const u32* __restrict__ cc_perm,'
assert after.count(header)==1;after=after.replace(header,'    const u32* __restrict__ cc_records,')
needle='            u64 cm = 1ull << cc_card[t];';assert after.count(needle)==1
after=after.replace(needle,'            u64 record = 3ull * t;'+nl+'            u64 cm = 1ull << cc_records[record];')
assert after.count('cc_perm[t]')==after.count('cc_child[t]')==1
after=after.replace('cc_perm[t]','cc_records[record + 2]').replace('cc_child[t]','cc_records[record + 1]')
candidate=base[:start]+after+base[end:]
reverse=after.replace('    const u32* __restrict__ cc_records,',header).replace('            u64 record = 3ull * t;'+nl,'').replace('cc_records[record]','cc_card[t]').replace('cc_records[record + 1]','cc_child[t]').replace('cc_records[record + 2]','cc_perm[t]')
assert reverse==before
(SOURCE/'baseline.cu').write_bytes(raw);(SOURCE/'candidate.cu').write_bytes(candidate.encode('utf-8'))
(SOURCE/'candidate.patch').write_text(''.join(difflib.unified_diff(base.splitlines(keepends=True),candidate.splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel)),encoding='utf-8')
paths=subprocess.check_output(['rg','--files','-g','*.cu',str(ROOT/'runs')],text=True).splitlines()
historical={p:old.sha(p) for p in paths if not Path(p).is_relative_to(SOURCE)}
assert old.sha(SOURCE/'candidate.cu') not in historical.values()
history=subprocess.run(['git','log','--all','--format=%H %s','-G','cc_records|cc_info|interleav.*chance','--','crates/solver/src/gpu'],cwd=ar.REPO,capture_output=True,text=True)
assert history.returncode==0
AUDIT=ROOT/'runs/D076-chance-record-source'
old.save(AUDIT/'bounded-staging-addendum.json',{'at':old.now(),'status':'go_one_fixed_no_launch_resource_probe','root_review_only':True,'earlier_scout_sha256':old.sha(AUDIT/'report.json'),'constructor_design':'Keep all original public CPU GpuPlan arrays. Replace three private device arrays by one flat u32 allocation of checked3*N words. Reuse existing pinned h_staging memory for interleaved triplets, with natural capacity floor(len/3), one ordered copy then unconditional drain before any reuse/return; original stack3word fallback if staging<3. No new host heap/pinned/device payload. Constructor copy behavior changes and needs whole-cycle/resource controls.','lifetime_rules':['No full f32 borrow overlaps the selected u32 staging borrow. f32 allocation alignment suffices for u32 and every bit pattern is valid; same4byte sizes verified.','Reserve checked3*N and use64-bit3*t CUDA indexing. Preserve exact record order and all float operations.','Always perform completion wait even if copy submission reports an error, before propagating either error. Host source cannot be overwritten/freed while queued.','Packing is constructor-only after arena uploads. Full/strategy readback later reuses staging as before. No new Drop guard/solver synchronization cadence.'],'device_payload':'Same12*N bytes, one allocation instead of three; observed_metadata feature accounting must count flat records and preserve original capacity vector indices/totals. CPU GpuPlan retained bytes/fields unchanged.','novelty':{'preserved_cuda_files_checked':len(historical),'preserved_cuda_sha256':historical,'new_candidate_unique':True,'local_all_ref_history_command':history.args,'local_all_ref_history_stdout':history.stdout,'text_search':'Earlier rg of preserved patch/readme/review files found no cc_info/cc_records/interleaved chance-record match. No whole remote-history claim.'},'limits':'Host helper not implemented; no compiler or native/probe/kernel/solver run yet. No resource or speed guarantee.'})
old.save(SOURCE/'manifest.json',{'id':'E046-cuda-source','at':old.now(),'accepted_cuda_sha256':old.sha(SOURCE/'baseline.cu'),'candidate_cuda_sha256':old.sha(SOURCE/'candidate.cu'),'candidate_patch_sha256':old.sha(SOURCE/'candidate.patch'),'exact_reversal':True,'only_changed_entry':'up_chance','old_parameter_count':15,'new_parameter_count':13,'float_expression_order_unchanged_by_source':True,'constructor_cost_design_sha256':old.sha(AUDIT/'bounded-staging-addendum.json'),'source_activated':False})
HERE=ROOT/'runs/E046-resource';HERE.mkdir()
for n in ['baseline.cu','candidate.cu']:(HERE/n).write_bytes((SOURCE/n).read_bytes())
prior=ROOT/'runs/E043-resource-r2'
probe=(prior/'probe.rs').read_text(encoding='utf-8').replace('E043','E046').replace('down_action','up_chance');(HERE/'probe.rs').write_text(probe,encoding='utf-8')
execute=(prior/'execute.py').read_text(encoding='utf-8').replace('E043','E046').replace('down_action','up_chance')
execute=execute.replace('import hashlib,json,shutil,subprocess,sys,time','import hashlib,json,re,shutil,subprocess,sys,time')
needle=" report={'id':'E046-resource'"
assert execute.count(needle)==1
insertion=""" old_abi=re.findall(r'\\.param\\s+\\.([a-z][0-9]+)\\s+up_chance_param_[0-9]+',be['up_chance'].split('{',1)[0])
 new_abi=re.findall(r'\\.param\\s+\\.([a-z][0-9]+)\\s+up_chance_param_[0-9]+',ce['up_chance'].split('{',1)[0])
 gates['baseline_abi_exact']=old_abi==['u64','u32','u32']+['u64']*10+['u32','u32']
 gates['candidate_abi_exact']=new_abi==['u64','u32','u32']+['u64']*8+['u32','u32']
"""
execute=execute.replace(needle,insertion+needle)
execute=execute.replace("'raw_markers':markers,","'raw_markers':markers,'abi':{'baseline':old_abi,'candidate':new_abi},")
(HERE/'execute.py').write_text(execute,encoding='utf-8')
p=old.read(prior/'protocol.json');p.update(id='E046-resource',at=old.now(),source_manifest_sha256=old.sha(SOURCE/'manifest.json'))
p['rustc_command']=[x.replace('E043-resource-r2','E046-resource') for x in p['rustc_command']]
deps={path:h for path,h in p['input_sha256'].items() if '/build/' in path.replace('\\','/')}
refs=[HERE/'baseline.cu',HERE/'candidate.cu',HERE/'probe.rs',HERE/'execute.py',SOURCE/'manifest.json',AUDIT/'report.json',AUDIT/'bounded-staging-addendum.json',ar.REPO/'tools/postflop_autoresearch.py',ROOT/'runs/small-gain-confirmation-plan/common.py']
p['input_sha256']=deps|{str(x):old.sha(x) for x in refs}
p['resource_gates']=['Only up_chance changes; all other8 entry bodies exact.','Original15-parameter and new13-parameter PTX ABI types exact.','No increased registers/local/staticshared, lower max supported threads, reduced64/128/256 theoretical occupancy or default-limit failure.','No kernel/solver execution or timing. No layout-width sweep after outcome.']
old.save(HERE/'protocol.json',p)
published={}
for directory in [SOURCE,HERE,AUDIT]:
 for src in directory.iterdir():
  if not src.is_file():continue
  key=directory.name+'/'+src.name;dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);b=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==b
  else:dst.write_bytes(b)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==b
  published[key]=old.sha(src)
old.save(HERE/'pre-execution-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'kernel_launches':0,'solver_executions':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(ar.STATUS);assert not any(e['id']=='E046' for e in s['experiments'])
 s['experiments'].append({'id':'E046','at':old.now(),'title':'Interleaved chance metadata in existing staging','kind':'candidate','status':'preparing','correctness':'pending','stage':'Frozen no-launch compiler/resource gate','reason':'Three device arrays become one equal-payload triplet array. CPU plan unchanged; existing pinned staging design avoids a host packing allocation. Compilation/resources/numerical correctness and timing remain unproven.','evidence':[{'label':'E046 frozen resource protocol','url':'evidence/E046-resource/protocol.json'},{'label':'D076 bounded staging/lifetime design','url':'evidence/D076-chance-record-source/bounded-staging-addendum.json'}]})
 s.update(state='running',stage='E046 no-launch resource probe',activity='Check up-chance compiled resources and15-to13-argument ABI before any kernel or solver execution.',updated_at=ar.now());ar.atomic_json(ar.STATUS,s)
print(json.dumps({'protocol_sha256':old.sha(HERE/'protocol.json'),'source_manifest_sha256':old.sha(SOURCE/'manifest.json'),'candidate_sha256':old.sha(SOURCE/'candidate.cu'),'preserved_cuda_files':len(historical),'history_matches':history.stdout}),flush=True)
