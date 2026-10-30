"""Reuse the complete fixed action matrix for the conditional-read candidate."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
source=(ROOT/'runs/E054-prepare-control.py').read_text(encoding='utf-8').replace('E054','E055').replace("'781440'","'a76b41'")
start=source.index("old.save(H/'source-review.json',");end=source.index("p=old.read(prior/'protocol.json')",start)
replacement='''old.save(H/'source-review.json',{'id':'E055-raw-control-source-review','at':old.now(),'root_review_only':True,'resource_root_sha256':old.sha(O/'report.json'),'source_review_sha256':old.sha(ROOT/'runs/E055-source/source-review.json'),'cases':819,'launches':1638,'changed_path_cases':264,'scope':'Same819case matrix, complete actual output/input/guard words and disjoint owned device addresses. Bothactors, own/locked/opponent, arities1-17,hands0-1326,alternateblocks,algorithms/iterations,signedzero/subnormal/quietNaN/infinity/finiteoverflow/count0. No dropped cases.','discount_buffer_contract':'Exact3float device buffer initialized before eachlaunch; actual immutable device words captured and compared to original production-derived discounts. Supported ordinary/continuation stream dependencies prevent concurrent writes during launch. Own-unlocked arithmetic reads same3values; locked/opponent paths use none. Invalid/trapping custom buffers are outside supported kernel-call contract.','production_proof':'Only placement of3readonly discount loads changes. Resource and conservative PTX reachability gate passes: opponent/locked read0words, each declaredarity unlocked reads3words. Same arithmetic/reduction/store order, host/ABI/graphs/allocations/quality. Existing raw parent/child row and learning/CFV allocation disjointness checks retained unchanged, although this transform does not move a CFVstore.','caller_source_sha256':{n:old.sha(old.REPO/n) for n in caller_paths},'limits':'Finite direct raw matrix and root source/PTX review only. No external independent audit or universal malformed-input guarantee. Full solver, broader/F32/lifetime/capacity/saves/holdout/cumulative/performance qualification remains required.'})
'''
source=source[:start]+replacement+source[end:]
source=source.replace('Production and every direct-case parent CFV row disjoint from child inputs.','ConditionalPTX gate skips discount reads on unused roles; immutable3float caller buffer retained.')
path=ROOT/'runs/E055-prepare-control-derived.py';path.write_text(source,encoding='utf-8',newline='\n')
print('E055 full raw matrix preparation derived, resource report unchanged.',flush=True)
