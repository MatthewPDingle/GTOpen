import json,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists();h.ar.refuse_active(h.ar.live_status())
H=ROOT/'runs/D199-existing-max-scout';H.mkdir(exist_ok=False)
source=ROOT/'runs/E102-source/baseline-kernels.cu';ptx=ROOT/'runs/E102-resource/execution/baseline-compute_120.ptx'
h.pin(source,'a926bf0bc818a2ba808c862b59a552dfb7ade453ca18f347b4307784e47d9647');h.pin(ptx,'4457a101f35369c5d1d9893409e4bc8a9dc027fc4234e325b72c621f73017c12')
text=ptx.read_text();entries={}
pattern=r'\bmax\.f32\s+[^;]*,\s*0f00000000\s*;'
assert len(re.findall(pattern,'max.f32 %f2, %f1, 0f00000000;'))==1
assert not re.findall(pattern,'max.f32 %f2, %f1, 0f3f800000;')
assert not re.findall(pattern,'setp.gt.f32 %p1, %f1, 0f00000000;')
for m in re.finditer(r'\.visible\s+\.entry\s+(\w+)\(',text):
 start=text.index('{',m.end());depth=1;at=start+1
 while depth:
  if text[at]=='{':depth+=1
  elif text[at]=='}':depth-=1
  at+=1
 body=text[start:at];entries[m.group(1)]={'positive_zero_max_f32_sites':len(re.findall(pattern,body)),'positive_zero_setp_gt_f32_sites':len(re.findall(r'\bsetp\.gt\.f32\s+[^;]*,\s*0f00000000\s*;',body))}
assert len(entries)==9 and [entries[n]['positive_zero_max_f32_sites'] for n in ['down_action','up_action','up_action_eval']]==[23,23,38]
closure=ROOT/'runs/E102-terminal-checkpoint/report.json';assert h.read(closure)['all_owned_compilers_native_readers_terminal']
h.save(H/'report.json',{'id':'D199','at':h.now(),'status':'declined_existing_compiled_mechanism_before_candidate','proposal':'Spell positive-regret clamp using fmaxf instead of original positive ternary.','observation':'Accepted baseline actual compute120PTX already contains84positivezero max.f32 sites across originaldown_action/up_action/up_action_eval. Merely spelling the same max operation has no demonstrated absent compiled mechanism; do not admit a candidate or search alternative syntax/flags here.','entry_inventory':entries,'source_positive_r_ternary_occurrences':source.read_text().count('r > 0.f ? r : 0.f'),'setp_caution':'Remaining16up_action zero comparisons include original sign-dependent discount selection; not counted as missing clamp max or removed by this proposal. No blanket equivalence or instruction-removal claim.','new_source_variants':0,'new_compilers':0,'new_CUDA_queries_or_kernels':0,'new_solve_or_speed_samples':0,'new_gain_accepted':False,'limits':'Read-only PTX/source scout, not finalSASS/dynamic instruction timing, all-float mathematical proof or a speed bound. No candidate compiled or measured.','inputs':{str(p):h.sha(p) for p in [Path(__file__),source,ptx,closure]}})
p=H/'report.json';key=H.name+'/'+p.name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D199','title':'Positive-regret max compiled-mechanism scout','kind':'diagnostic','status':'rejected','accepted':False,'measurement_epoch':'RAM20261028','stage':'No candidate admitted: max already compiled','reason':'Original accepted action PTX already has84positivezero max.f32 sites. No source/compiler/CUDA/solve/timing trial; no gain claim. E102 wrapper failure retained.','evidence':[{'label':'Read-only compiled scout','url':'evidence/'+key}]});s.update(updated_at=h.now(),active_experiment='D199',stage='Independent source research; accepted configuration unchanged',activity='E102 raw numerical states exact but frozen wrapper gate failed; no speed measured. D199 avoids redundant max-clamp source trial because accepted PTX already emits it. E080/GPU/compressed/16 remains live, no new gain.');h.ar.atomic_json(h.ar.STATUS,s)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20) as response:assert response.read()==h.ar.STATUS.read_bytes()
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n### D199 positive-regret clamp compiled scout\n\nRead-only original accepted source and sealedcompute120PTX4457a101f35369c5d1d9893409e4bc8a9dc027fc4234e325b72c621f73017c12 show23/23/38positivezero max.f32 sites in down_action/up_action/up_action_eval,84total. Decline fmaxf spelling-only candidate before any source/compiler/CUDA/solve/timing trial: no demonstrated missing max mechanism. Remaining16up_action sign comparisons include unchanged discount selection and are not presumed removable. Parserpositive/negative instruction fixtures pass; no finalSASS/dynamic/speed/equivalence claim. CurrentE080/GPU/compressed/16 stays live; E102 originalwrapper failure remainsclosed, no newgain.\n')
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);subprocess.run(['git','commit','-m','research: decline redundant positive regret clamp source trial'],cwd=h.REPO,check=True)
h.custody();print(json.dumps({'D199':'declined_existing_compiled_max','original_max_sites':84,'new_compiler_CUDA_solver_runs':0,'source_main_live_PTX_unchanged':True}),flush=True)
