import shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
H=ROOT/'runs/D273-spot-construction-scout';p=H/'report.json';q=h.read(p)
assert q['local_revisions']==21 and q['retained_game_sources']==55 and q['unique_game_source_hashes']==9 and not q['literal_parallel_tree_river_hits_for_review']
assert q['new_source_compiler_CUDA_context_kernel_solver_or_timing_samples']==0 and not q['source_candidate_created']
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';prefix=ledger.read_bytes();assert b'\n## D273 distinct construction source scout'not in prefix;assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).strip()
entry=f'''

## D273 distinct construction source scout - no prototype admitted

After closing E115 at0.192324921678%/river guard, bounded read-only local21game/tree revisions and55retainedSpot sourcefiles/9unique hashes find no matching parallel tree/river join/spawn literals. Scope includes local refs and retained X/S source only, not exhaustive semantic/remote novelty proof. Actual Spot::new_impl serially builds tree fromconfig/board/handcounts/budget/strictness then river strengths fromboard/mask/hands; neither reads the other output and suit group setup followsboth. This is earlier CPU Spot construction, not GPUplan sub-stage or CUDA context work.

Plan/context/module/NVRTC overlap lead explicitly declined as closed E079/D109 family: E079 had2.9718558844%aggregate gain but34.3185952486%river regression3of3, no thread/helper/eligibility/placement/scope retry. No conservative-budget, owner-worker or threshold variant admitted. E115 row ordering also remains closed. No new compiler/native/CUDA context/kernel/solve/speed or sourcecandidate inD273.

Naive tree/river join would speculate expensive river evaluation on invalid tree/node-budget failures; old?returns before river work. Limiting optimization to max_nodes=None would miss normal limited API path and is not enough. Existing river evaluator already uses globalRayon, so contention/worker/FPU/peak/error cleanup/responsiveness andactual limited API behavior require design/measurement. Cancellation alone would not erase CPUwork already performed before a late budget failure; do not claim it proves no tradeoff. Fresh source-matched tree/river observations and a prospective effort budget are needed before any fixed source form. Historical D044/D110/D183 timings remain excluded, no old headroom/saving/whole-solve inference. Full original exactness/ordinary/complete1%/strictfixture/fresh16/broad/material/holdout/fresh-original/cumulative/app gates unchanged.

Source audit `{p}` HTTPbyteverified, all ownedhelpers terminal, source/main/live/protected2PTX unchanged, locks absent. E080/GPU/compressed/16/defaultaffinity bestlive, no newgain adopted,lastprimaryB362/nextB363. AllnewbulkX,Sarchive readonly,noT. Priorledgerprefix byteexact,goalactive.
'''
ledger.write_bytes(prefix+entry.encode());assert ledger.read_bytes()[:len(prefix)]==prefix;h.custody();subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
assert subprocess.check_output(['git','diff','--cached','--name-only'],cwd=h.REPO,text=True).splitlines()==['research/postflop-gpu-20261016/experiments.md'];subprocess.run(['git','-c','gc.auto=0','commit','-m','research: audit distinct Spot construction opportunity'],cwd=h.REPO,check=True)
h.save(H/'publication.json',{'at':h.now(),'local_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip(),'report_sha256':h.sha(p),'source_candidate_created':False,'new_compilers_GPU_or_speed_samples':0,'all_owned_helpers_terminal':True,'goal_active':True})
h.custody();print('D273 source/history audit preserved; no implementation or speed claim.',flush=True)
