"""Prepare an unexecuted primary controller while isolated builds run."""
from pathlib import Path
import re
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');src=R/'runs/E072-freeze-run-publish.py';dest=R/'runs/E073-freeze-run-publish.py';assert not dest.exists()
s=src.read_text(encoding='utf-8').replace('E072','E073').replace('e072','e073').replace('V072','V073')
s=s.replace('E073-source','E073-source-host-r2').replace('E073-direct-fold','E073-kernel-control-r3').replace('pass_scoped_full_fold_raw_equivalence','pass_scoped_full_show_raw_equivalence')
s=s.replace('360','364').replace('720','728').replace('B232','B235').replace('B233','B236').replace('B234','B237').replace('D117-fold-PTX-audit','D119-boundary-load-audit')
scope='Only privateGPUriver lower/upper boundary buffers narrowu32to u16, preserving complete logical values and original float body/order. Public CPUplan and all other GPUbuffers/launch/graph/save/quality unchanged. Added checked host packing4temporary allocations/4synchronizations inside complete clocks. Prebuild host accounting completion makes planned/observed continuation bytes exact, with CUDA/upload code unchanged from364direct pairs/728launches. Original resource pointer-decoder failure and D119cvta-only correction retained; same criterion/resources/PTX, no hardware rerun. Complete clocks include all NVRTC/JIT/setup/readback. No complete-solve/broad/material/holdout/cumulative result yet.'
s,n=re.subn(r"source_scope='[^']+'",'source_scope='+repr(scope),s,count=1);assert n==1
s=s.replace('Direct fold numerical','Direct showdown numerical').replace('cache-width/synchronization/source-scope variants','width/packing/helper/source-scope variants')
s=s.replace('research: screen fold index scratch staging','research: screen private river boundary storage')
s=s.replace('### E073 fold index staging complete-solve screen','### E073 private river boundary complete-solve screen')
start=s.index('D116source-address and D117static-count audit already recorded.');end=s.index('\n\nTwo fresh isolated builds;',start)
s=s[:start]+'''D118source/legal-domain proof and D119cvta-only decoder correction retained. CandidateCUDA{P['candidate_owned_sha256']['crates/solver/src/gpu/kernels.cu']} unchanged from the sole resource probe and364direct GPUcase pairs/728launches. All full output/input/guard bytes exact, including physical32bit/16bit boundary images; public CPUplan and19other inputs unchanged. The original parser/resource and pre-native runner failures remain preserved. No resource/NVRTC rerun, completed-case repetition or source/width/packing variant. Shared/dynamic/local reservations and queried occupancy/register38unchanged. Three-file final source completes exact continuation planned/observed payload accounting before first integrated build; CUDA/upload code unchanged. Added checked packing4temporary allocations/4explicit synchronizations remain inside clocks. No launch/graph/quality/save change.'''+s[end:]
s=s.replace('D117corrects the static count proxy','D119corrects omitted cvta propagation')
assert not any(x in s for x in ['D116source','D117','V072','B232','B233','B234','full_fold','E073-direct-fold','runs/E073-source/'])
compile(s,str(dest),'exec')
with dest.open('x',encoding='utf-8',newline='\n')as f:f.write(s)
print('E073 primary controller syntax checked; not executed or sealed. Fixed V073-unit then B235/E073R1,E073R2/B236,B237/E073R3.',flush=True)
